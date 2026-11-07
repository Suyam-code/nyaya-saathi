"""Nyaya Saathi - grounded AI legal helper for everyday problems in India.
Design: LLM only talks; facts come from kb/laws.json; guardrail checks every cited law against the KB.
Swap model with env vars:  LLM_PROVIDER=anthropic|openai  LLM_MODEL=...  LLM_API_KEY=...  LLM_BASE_URL=... (openai-compatible: Gemini, Groq, OpenRouter, ...)"""
import json, os, re, pathlib, time, requests

KB = json.load(open(pathlib.Path(__file__).parent / "kb" / "laws.json"))
ENTRIES = {e["id"]: e for e in KB["entries"]}

# ---------- 1. deterministic routing (code, not LLM) ----------
KEYWORDS = {
 "consumer": ["refund","product","order","delivery","amazon","flipkart","defect","warranty","service","overcharg","insurance","airline","faulty","repair","bought","purchase","seller","replacement","bill"],
 "tenancy": ["landlord","deposit","rent","tenant","flat","pg ","lease"],
 "employment": ["salary","wage","employer","fired","notice period","offer letter","full and final","unpaid","internship stipend"],
 "cheque": ["cheque","check bounce","dishonour","bounced"],
}
def route(text):
    t = text.lower()
    scores = {k: sum(w in t for w in ws) for k, ws in KEYWORDS.items()}
    topic = max(scores, key=scores.get) if max(scores.values()) else "general"
    escalate = any(re.search(r"\b" + re.escape(w) + r"\b", t) for w in KB["escalate_triggers"])
    return topic, escalate

def retrieve(topic):
    return [e for e in KB["entries"] if e["topic"] in (topic, "general")]

# ---------- 2. prompt ----------
MODES = {
 "advise": "Explain where the person stands and their options in plain, warm language. Then give 3 concrete next steps.",
 "notice": "Draft a legal notice / complaint letter using ONLY facts the user gave. Leave [PLACEHOLDERS] for anything missing. Add a one-line reminder to get a lawyer to review before sending.",
 "opponent": "Role-play the OTHER side (landlord / company / employer) so the user can practise. Stay in character for 1 short reply, then add a 'Coach note:' on how the user could respond better.",
}
SYSTEM = """You are Nyaya Saathi, a legal-information assistant for ordinary people in India. You are NOT a lawyer.
RULES
1. Reply in the language/script the user writes in (Hindi, Hinglish, Bengali, English...). Keep sentences short.
2. Legal statements may ONLY come from the VERIFIED FACTS block, and each one must carry its tag like [CPA-LIMIT]. Never cite any section, Act, case name or amount that is not in that block.
3. If the facts block does not cover something, say 'I am not sure about this - please check with a lawyer / DLSA (15100)'. Do not guess.
4. If the user asks a direct question that the VERIFIED FACTS answer, answer it first (with the tag), then ask at most 3 short questions for missing facts. If nothing can be answered yet, just ask at most 3 short questions. If the user asks for a section number or case law that is not in the facts, say 'I am not sure about this - please check with a lawyer / DLSA (15100)' and do not guess.
5. Include EVERY deadline and time limit from the facts that applies to the user's case, each with its tag. Never promise outcomes. No 'you will win'.
6. Return ONLY JSON: {"reply": str, "case_card": {"what_happened": str, "when": str, "amount": str, "proof_have": [str], "proof_missing": [str]}, "used": [kb ids], "needs_lawyer": bool}
7. If the latest message is small talk, thanks or off-topic, answer in 1-2 friendly lines and ask what legal problem they need help with. Do NOT repeat earlier advice.\nMODE: {mode}
VERIFIED FACTS:
{facts}"""

def build_system(topic, mode):
    facts = "\n".join(f"[{e['id']}] {e['title']}: {e['text']} (Source: {e['cite']})" for e in retrieve(topic))
    return SYSTEM.replace("{mode}", MODES[mode]).replace("{facts}", facts)

# ---------- 3. swappable model ----------
def _post(url, **kw):
    for i in range(5):
        r = requests.post(url, **kw)
        if r.status_code in (429, 503) and i < 4:
            wait = float(r.headers.get("retry-after", 0) or 0) or 15 * (i + 1)
            print(f"  [{r.status_code}] waiting {wait:.0f}s then retrying...")
            time.sleep(wait); continue
        if not r.ok: raise RuntimeError(f"{r.status_code}: {r.text[:400]}")
        return r

def call_llm(system, messages):
    prov = os.getenv("LLM_PROVIDER", "anthropic")
    key = os.environ["LLM_API_KEY"]
    model = os.getenv("LLM_MODEL", "claude-haiku-4-5" if prov == "anthropic" else "gpt-4o-mini")
    if prov == "anthropic":
        r = _post("https://api.anthropic.com/v1/messages", timeout=90,
            headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
            json={"model": model, "max_tokens": 1500, "system": system, "messages": messages})
        r.raise_for_status(); return r.json()["content"][0]["text"]
    base = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    r = _post(f"{base}/chat/completions", timeout=90, headers={"Authorization": f"Bearer {key}"},
        json={"model": model, "messages": [{"role": "system", "content": system}] + messages})
    r.raise_for_status(); return r.json()["choices"][0]["message"]["content"]

# ---------- 4. guardrail (code, not LLM) ----------
CITE_RE = re.compile(r"(?:Section|Sec\.?|S\.)\s*\d+[A-Za-z]*(?:\(\d+\))?|[A-Z][A-Za-z()]+(?: [A-Z][A-Za-z()]+)* (?:Act|Code|Sanhita)(?:,)? ?\d{4}|\bv\.?s?\.? [A-Z][a-z]+")
def guardrail(parsed):
    """Flag any statute/section/case-looking string not present in the KB, and any tag not in KB."""
    allowed = " ".join(e["cite"] + " " + e["text"] + " " + e["title"] for e in KB["entries"]).lower()
    flags = []
    for m in CITE_RE.findall(parsed["reply"]):
        if m.lower().replace(" ", "") not in allowed.replace(" ", ""):
            flags.append(m)
    for t in re.findall(r"\[([A-Z0-9-]+)\]", parsed["reply"]):
        if t not in ENTRIES: flags.append(f"unknown tag [{t}]")
    return flags

def parse(raw):
    m = re.search(r"\{.*\}", raw, re.S)
    try: return json.loads(m.group(0))
    except Exception: return {"reply": raw, "case_card": {}, "used": [], "needs_lawyer": True}

GREET = re.compile(r"^\s*(hi+|hello+|hey+|hii+|namaste|namaskar|hola|thanks?|thank you|ok(ay)?|नमस्ते|नमस्कार|নমস্কার|হ্যালো)\W*$", re.I)

def respond(history, mode="advise"):
    if GREET.match(history[-1]["content"]):   # greeting / thanks: no model call, no repeated advice
        return {"reply": "Namaste! 🙏 I am Nyaya Saathi. Tell me what happened in your own words (Hindi, Hinglish, Bengali or English): what the problem is, when it happened, how much money is involved, and what proof you have.",
                "case_card": {}, "used": [], "needs_lawyer": False, "topic": "general", "guardrail_flags": [], "verify_links": [], "small_talk": True}
    user_text = " ".join(m["content"] for m in history if m["role"] == "user")
    topic, escalate = route(user_text)
    out = parse(call_llm(build_system(topic, mode), history))
    flags = guardrail(out)
    if flags:   # fail closed: tell the user
        out["reply"] += "\n\n⚠️ Parts of this answer mention law I could not verify (" + ", ".join(flags) + "). Please ignore those and confirm with a lawyer."
        out["needs_lawyer"] = True
    if escalate or out.get("needs_lawyer"):
        out["reply"] += "\n\n🧑‍⚖️ " + KB["escalate_message"]
    out.update(topic=topic, guardrail_flags=flags, verify_links=[ENTRIES[i]["verify_at"] for i in out.get("used", []) if i in ENTRIES])
    return out

if __name__ == "__main__":
    print(json.dumps(respond([{"role": "user", "content": input("Your problem: ")}]), ensure_ascii=False, indent=2))
