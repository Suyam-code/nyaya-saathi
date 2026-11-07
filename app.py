import html, re
import streamlit as st
from lawyer import respond, ENTRIES

import base64, pathlib
_A = pathlib.Path(__file__).parent / "assets"
def _b64(n):
    try: return base64.b64encode((_A / n).read_bytes()).decode()
    except Exception: return ""
LOGO, LOGO_S = _b64("logo.png"), _b64("logo_small.png")
HERO_LOGO = f'<img class="logo" src="data:image/png;base64,{LOGO}">' if LOGO else '<div class="orb"></div>'
BRAND_LOGO = f'<img class="logo-s" src="data:image/png;base64,{LOGO_S}">' if LOGO_S else '<div class="orb-s"></div>'
AVATAR_BOT = str(_A / "logo_small.png") if LOGO_S else "⚖️"
try:
    from PIL import Image as _Img
    _ICON = _Img.open(_A / "logo_small.png")
except Exception:
    _ICON = "⚖️"

st.set_page_config(page_title="Nyaya Saathi", page_icon=_ICON, layout="wide", initial_sidebar_state="expanded")

TOPIC = {"consumer": ("🛒", "Consumer", "#3b82f6"), "tenancy": ("🏠", "Rental deposit", "#8b5cf6"),
         "employment": ("💼", "Unpaid salary", "#f97316"), "cheque": ("🧾", "Cheque bounce", "#14b8a6"),
         "general": ("⚖️", "General", "#64748b")}
MODES = {"advise": ("💡", "Understand my options", "Where do I stand?"),
         "notice": ("📝", "Draft my notice", "Ready-to-edit legal notice"),
         "opponent": ("🎭", "Practise vs other side", "Rehearse, get coached")}
CARDS = [("🏠", "My landlord is not returning my security deposit", "Mere landlord ne 40000 deposit nahi diya, agreement hai"),
         ("🛒", "A seller refuses to refund my defective product", "I bought a faulty laptop for Rs 24,000 in March 2026 and the seller refuses a refund"),
         ("💼", "My company has not paid my salary for 3 months", "Meri company ne 3 mahine ki salary nahi di, offer letter aur bank statement hai")]
TOPICS = [("🏠", "Rental deposit", CARDS[0][2]), ("🛒", "Refund / defective goods", CARDS[1][2]),
          ("💼", "Unpaid salary", CARDS[2][2]), ("🧾", "Cheque bounce", "My friend's cheque of Rs 1.5 lakh bounced 10 days ago, I have the bank memo")]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,.stApp,.stApp p,.stApp label,.stApp button,.stApp textarea,.stApp input,.stApp h1,.stApp h2,.stApp h3,.stApp h4{font-family:'Inter',sans-serif}
[data-testid="stIconMaterial"],.material-symbols-rounded,[class*="material-symbols"]{font-family:'Material Symbols Rounded','Material Icons'!important}
.stApp{background:#0a0a0f;color:#e5e7eb}
.stApp::before{content:"";position:fixed;top:-160px;right:-120px;width:620px;height:620px;pointer-events:none;z-index:0;
 background:radial-gradient(circle at 60% 40%,rgba(167,139,250,.38),rgba(124,58,237,.14) 38%,transparent 68%);filter:blur(24px)}
header[data-testid="stHeader"]{background:transparent}
#MainMenu,footer,[data-testid="stMainMenu"],[data-testid="stToolbarActions"],.stDeployButton{visibility:hidden}
[data-testid="stSidebarCollapsedControl"],[data-testid="stExpandSidebarButton"],[data-testid="stSidebarCollapseButton"]{visibility:visible!important;opacity:1!important;color:#c9ccd3!important}
[data-testid="stSidebarCollapsedControl"] button,[data-testid="stExpandSidebarButton"]{background:rgba(255,255,255,.08)!important;border-radius:10px!important}
.block-container{padding-top:2.2rem;max-width:1180px}
/* sidebar */
[data-testid="stSidebar"]{background:#0e0e13;border-right:1px solid rgba(255,255,255,.06)}
[data-testid="stSidebar"] .block-container{padding-top:1.2rem}
.brand{display:flex;align-items:center;gap:10px;font-weight:600;font-size:1.05rem;margin-bottom:12px}
.orb-s{width:26px;height:26px;border-radius:50%;background:radial-gradient(circle at 30% 30%,#ddd6fe,#8b5cf6 55%,#4c1d95);box-shadow:0 0 14px rgba(139,92,246,.6)}
.sec{font-size:.68rem;letter-spacing:.09em;text-transform:uppercase;opacity:.45;margin:16px 0 4px 4px;font-weight:600}
[data-testid="stSidebar"] .stButton>button{background:transparent;border:none;color:#c9ccd3;justify-content:flex-start;text-align:left;
 padding:.38rem .6rem;border-radius:8px;font-size:.86rem;font-weight:400;box-shadow:none;width:100%}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(255,255,255,.06);color:#fff}
.st-key-new button{background:#fff!important;color:#0a0a0f!important;font-weight:600!important;justify-content:center!important;border-radius:10px!important;padding:.55rem!important;margin-bottom:6px}
.st-key-new button:hover{background:#ede9fe!important}
[data-testid="stSidebar"] [data-testid="stRadio"] label{padding:6px 8px;border-radius:8px}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{background:rgba(255,255,255,.05)}
.aid{border:1px solid rgba(167,139,250,.35);background:linear-gradient(160deg,rgba(124,58,237,.16),rgba(124,58,237,.04));border-radius:12px;padding:12px 14px;font-size:.8rem;margin-top:14px}
.aid b{font-size:.86rem}.aid .num{display:inline-block;margin-top:6px;margin-right:6px;padding:3px 10px;border-radius:8px;background:rgba(255,255,255,.08);font-weight:600}
/* hero */
.hero{text-align:center;margin-top:6vh}
.orb{width:64px;height:64px;border-radius:50%;margin:0 auto 18px;background:radial-gradient(circle at 30% 28%,#e9e3ff,#8b5cf6 52%,#3b0764);box-shadow:0 0 38px rgba(139,92,246,.65),inset 0 0 12px rgba(255,255,255,.25);position:relative}
.orb::after{content:"";position:absolute;inset:-7px;border-radius:50%;border:1px solid rgba(196,181,253,.35)}
.welcome{opacity:.6;font-size:1rem;margin-bottom:6px;font-weight:400}
.headline{font-size:2.5rem;font-weight:400;letter-spacing:-.02em;color:#f4f4f7;margin-bottom:26px}
.headline b{font-weight:600;background:linear-gradient(90deg,#c4b5fd,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.main .stButton>button,[data-testid="stMain"] .stButton>button{background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.09);color:#d4d4d8;border-radius:14px;
 min-height:96px;padding:14px 16px;text-align:left;justify-content:flex-start;align-items:flex-start;font-size:.9rem;line-height:1.35;transition:all .15s}
[data-testid="stMain"] .stButton>button:hover{border-color:rgba(167,139,250,.7);background:rgba(167,139,250,.10);color:#fff;box-shadow:0 0 22px rgba(139,92,246,.22)}
/* chat */
[data-testid="stChatMessage"]{background:transparent;padding:.4rem 0}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]){background:rgba(255,255,255,.045);border-radius:14px;padding:.7rem 1rem}
[data-testid="stBottom"],[data-testid="stBottom"]>div{background:transparent!important}
[data-testid="stChatInput"]{background:#111117;border:1px solid rgba(167,139,250,.55);border-radius:18px;box-shadow:0 0 28px rgba(139,92,246,.28)}
[data-testid="stChatInput"]>div{background:transparent!important;border:none!important}
[data-testid="stChatInput"] textarea{background:transparent!important;color:#e5e7eb!important}
[data-testid="stChatInput"] button{background:linear-gradient(135deg,#8b5cf6,#6d28d9)!important;border-radius:10px;color:#fff!important}
/* panels, chips, callouts (dark) */
.pill{display:inline-block;padding:3px 11px;border-radius:999px;font-size:.76rem;font-weight:600;margin:2px 4px 2px 0;color:#fff}
.tag{display:inline-block;padding:1px 8px;border-radius:6px;font-size:.73rem;font-weight:700;background:rgba(139,92,246,.2);color:#c4b5fd;border:1px solid rgba(139,92,246,.45);margin:0 2px}
.card{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:14px 16px;margin-bottom:12px}
.lbl{font-size:.68rem;text-transform:uppercase;letter-spacing:.06em;opacity:.55;margin-top:9px}.val{font-size:.95rem;font-weight:600}
.chip{display:inline-block;padding:2px 10px;border-radius:8px;font-size:.78rem;margin:2px 4px 2px 0}
.have{background:rgba(34,197,94,.14);color:#86efac;border:1px solid rgba(34,197,94,.4)}.miss{background:rgba(245,158,11,.14);color:#fcd34d;border:1px solid rgba(245,158,11,.4)}
.ok{background:rgba(34,197,94,.12);color:#86efac;border:1px solid rgba(34,197,94,.35);border-radius:10px;padding:8px 12px;font-size:.82rem;font-weight:600;margin-bottom:10px}
.bad{background:rgba(239,68,68,.12);color:#fca5a5;border:1px solid rgba(239,68,68,.4);border-radius:10px;padding:8px 12px;font-size:.82rem;font-weight:600;margin-bottom:10px}
.callout-red{background:rgba(239,68,68,.10);color:#fecaca;border-left:4px solid #ef4444;border-radius:8px;padding:10px 14px;margin-top:10px;font-size:.9rem}
.callout-amber{background:rgba(245,158,11,.10);color:#fde68a;border-left:4px solid #f59e0b;border-radius:8px;padding:10px 14px;margin-top:10px;font-size:.9rem}
.hint{opacity:.6;font-size:.82rem}.h4{font-weight:600;font-size:.95rem;margin:2px 0 8px}
/* v2 fixes */
[data-testid="stMain"] .stButton>button{height:auto;min-height:112px;align-items:flex-start}
[data-testid="stMain"] .stButton>button>div{justify-content:flex-start!important;width:100%}
[data-testid="stMain"] .stButton>button p{white-space:normal!important;overflow:visible!important;text-overflow:clip!important;text-align:left!important;line-height:1.45}
[data-testid="stSidebar"] .stButton>button>div{justify-content:flex-start!important;width:100%}
[data-testid="stSidebar"] .stButton>button p{text-align:left!important;white-space:nowrap}
.st-key-new button>div{justify-content:center!important}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:.15rem}
[data-testid="stSidebar"] [data-testid="stRadio"] p{font-size:.88rem}
/* v3 subtle */
.stApp::before{background:radial-gradient(circle at 60% 40%,rgba(139,120,210,.20),rgba(100,80,180,.07) 40%,transparent 68%)}
.orb{background:radial-gradient(circle at 30% 28%,#cfc8ee,#7c6bc4 52%,#2e2358);box-shadow:0 0 22px rgba(124,107,196,.35),inset 0 0 10px rgba(255,255,255,.12)}
.orb::after{border-color:rgba(180,170,230,.2)}
.orb-s{background:radial-gradient(circle at 30% 30%,#cfc8ee,#7c6bc4 55%,#2e2358);box-shadow:0 0 8px rgba(124,107,196,.35)}
.headline{color:#dcdce4}
.headline b{background:linear-gradient(90deg,#a99fd8,#8f84c8);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.welcome{opacity:.5}
.st-key-new button{background:rgba(255,255,255,.09)!important;color:#e5e7eb!important;border:1px solid rgba(255,255,255,.12)!important}
.st-key-new button:hover{background:rgba(255,255,255,.15)!important}
[data-testid="stChatInput"]{border:1px solid rgba(139,120,210,.32);box-shadow:0 0 16px rgba(124,107,196,.10)}
[data-testid="stChatInput"] button{background:#5b4fa8!important}
[data-testid="stMain"] .stButton>button:hover{border-color:rgba(139,120,210,.45);background:rgba(139,120,210,.07);box-shadow:none}
.aid{border-color:rgba(139,120,210,.22);background:rgba(124,107,196,.07)}
.tag{background:rgba(139,120,210,.14);color:#b9b0e6;border-color:rgba(139,120,210,.3)}
.pill{filter:saturate(.7) brightness(.92)}
.have{color:#8fd0a6}.miss{color:#e3c37a}.ok{color:#8fd0a6}.bad{color:#e8a0a0}
.callout-red{color:#ecc0c0;background:rgba(239,68,68,.08)}.callout-amber{color:#e6d49a;background:rgba(245,158,11,.08)}
/* v5 fixes */
.block-container{padding-bottom:9rem!important}
.tag{white-space:nowrap}
[data-testid="stAppDeployButton"],.stAppDeployButton{display:none!important}
/* logo */
.logo{width:128px;height:128px;object-fit:contain;display:block;margin:0 auto 6px;filter:drop-shadow(0 0 16px rgba(139,120,210,.35))}
.logo-s{width:32px;height:32px;object-fit:contain}
/* v4 fixes */
[class*="st-key-ex"] button{height:auto!important;min-height:120px!important;align-items:flex-start!important;justify-content:flex-start!important;text-align:left!important;white-space:normal!important;padding:16px 18px!important}
[class*="st-key-ex"] button>div{justify-content:flex-start!important;width:100%!important;overflow:visible!important}
[class*="st-key-ex"] [data-testid="stMarkdownContainer"]{overflow:visible!important;white-space:normal!important;width:100%!important}
[class*="st-key-ex"] button p{white-space:normal!important;overflow:visible!important;text-overflow:clip!important;text-align:left!important;line-height:1.5!important;font-size:.95rem!important}
[class*="st-key-ex"] button:hover{border-color:rgba(139,120,210,.45)!important;background:rgba(139,120,210,.07)!important}
.brand{margin-bottom:16px}.sec{margin-bottom:8px!important}
.aid .fine{display:block;margin-top:10px;opacity:.5;font-size:.72rem}
</style>""", unsafe_allow_html=True)

ss = st.session_state
ss.setdefault("h", []); ss.setdefault("meta", []); ss.setdefault("card", None); ss.setdefault("pending", None); ss.setdefault("archive", [])

def pill(text, color): return f'<span class="pill" style="background:{color}">{html.escape(text)}</span>'

def fmt(text):
    t = html.escape(text.replace("\u00a0", " ")).replace('&quot;[', "[").replace(']&quot;', "]")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\[([A-Z0-9-]{3,})\]", lambda m: f'<span class="tag" title="{html.escape(ENTRIES[m.group(1)]["title"]) if m.group(1) in ENTRIES else "unverified"}">{m.group(1)}</span>', t)
    return t.replace("\n", "<br>")

def split_reply(text):
    esc = warn = ""
    if "🧑‍⚖️" in text: text, esc = text.split("🧑‍⚖️", 1)
    if "⚠️" in text: text, warn = text.split("⚠️", 1)
    return text.strip(), warn.strip(), esc.strip()

def render_reply(text):
    body, warn, esc = split_reply(text)
    st.markdown(fmt(body), unsafe_allow_html=True)
    if warn: st.markdown(f'<div class="callout-amber">⚠️ {fmt(warn)}</div>', unsafe_allow_html=True)
    if esc: st.markdown(f'<div class="callout-red">🧑‍⚖️ <b>Talk to a real lawyer</b><br>{fmt(esc)}</div>', unsafe_allow_html=True)

def new_case():
    if ss.h: ss.archive = ([{"title": ss.h[0]["content"][:34], "h": ss.h, "meta": ss.meta, "card": ss.card}] + ss.archive)[:5]
    ss.h, ss.meta, ss.card, ss.pending = [], [], None, None

# ---------------- sidebar ----------------
with st.sidebar:
    st.markdown(f'<div class="brand">{BRAND_LOGO}Nyaya Saathi</div>', unsafe_allow_html=True)
    if st.button("＋  New case", key="new", use_container_width=True): new_case(); st.rerun()
    st.markdown('<div class="sec">Mode</div>', unsafe_allow_html=True)
    mode = st.radio("mode", list(MODES), format_func=lambda m: f"{MODES[m][0]}  {MODES[m][1]}", captions=[MODES[m][2] for m in MODES], label_visibility="collapsed")
    st.markdown('<div class="sec">Topics</div>', unsafe_allow_html=True)
    for i, (ic, label, text) in enumerate(TOPICS):
        if st.button(f"{ic}  {label}", key=f"tp{i}", use_container_width=True): ss.pending = text; st.rerun()
    if ss.archive:
        st.markdown('<div class="sec">Recent cases</div>', unsafe_allow_html=True)
        for i, a in enumerate(ss.archive):
            if st.button(f"💬  {a['title']}", key=f"ar{i}", use_container_width=True):
                ss.h, ss.meta, ss.card = a["h"], a["meta"], a["card"]; st.rerun()
    st.markdown('<div class="aid"><b>Free legal aid</b><br>Eligible people can get a lawyer at no cost.<br>'
                '<span class="num">📞 15100</span><span class="num">🛒 1915</span><span class="fine">Legal information, not legal advice.</span></div>', unsafe_allow_html=True)

typed = st.chat_input("Ask anything or describe your legal problem...")   # top level = pinned to bottom of page
prompt = typed or ss.pending; ss.pending = None
if prompt:
    ss.h.append({"role": "user", "content": prompt})
    try:
        with st.spinner("Checking the facts file and thinking..."):
            out = respond(ss.h, mode)
        ss.h.append({"role": "assistant", "content": out["reply"]})
        if not out.get("small_talk"): ss.meta.append({"topic": out["topic"], "flags": out["guardrail_flags"], "used": out.get("used", []), "links": out["verify_links"]})
        if any(out.get("case_card", {}).values()): ss.card = out["case_card"]
    except Exception as e:
        ss.h.pop()
        st.error(f"Could not get an answer: {e}")
        st.caption("Check LLM_API_KEY / LLM_BASE_URL / LLM_MODEL in the terminal that started Streamlit, then try again.")

# ---------------- main ----------------
if not ss.h:
    st.markdown('<div class="hero">' + HERO_LOGO + '<div class="welcome">Welcome to Nyaya Saathi</div>'
                '<div class="headline">How can I help with your <b>legal problem</b>?</div></div>', unsafe_allow_html=True)
    _, mid, _ = st.columns([0.15, 3, 0.15])
    with mid:
        cols = st.columns(3, gap="medium")
        for i, (ic, label, text) in enumerate(CARDS):
            if cols[i].button(f"{ic}\n\n{label}", key=f"ex{i}", use_container_width=True): ss.pending = text; st.rerun()
        st.markdown('<p class="hint" style="text-align:center;margin-top:14px">Write in Hindi, Hinglish, Bengali or English · mention what happened, when, how much, and what proof you have</p>', unsafe_allow_html=True)
    chat_col, side_col = st.container(), None
else:
    chat_col, side_col = st.columns([1.7, 1], gap="large")

if side_col is not None:
    with side_col:
        c, m = ss.card, (ss.meta[-1] if ss.meta else None)
        st.markdown('<div class="h4">📋 Your case card</div>', unsafe_allow_html=True)
        if not c:
            st.markdown('<div class="card hint">Fills in as you describe what happened: facts, amount, proof you have and proof you still need.</div>', unsafe_allow_html=True)
        else:
            ic, name, col = TOPIC.get(m["topic"], TOPIC["general"]) if m else TOPIC["general"]
            rows = [("What happened", c.get("what_happened")), ("When", c.get("when")), ("Amount", c.get("amount"))]
            inner = "".join(f'<div class="lbl">{l}</div><div class="val">{html.escape(str(v)) if v else "—"}</div>' for l, v in rows)
            have = "".join(f'<span class="chip have">✓ {html.escape(str(x))}</span>' for x in c.get("proof_have", [])) or '<span class="hint">none yet</span>'
            miss = "".join(f'<span class="chip miss">＋ {html.escape(str(x))}</span>' for x in c.get("proof_missing", [])) or '<span class="hint">nothing missing</span>'
            st.markdown(f'<div class="card">{pill(f"{ic} {name}", col)}{inner}<div class="lbl">Proof you have</div>{have}<div class="lbl">Proof to collect</div>{miss}</div>', unsafe_allow_html=True)
        if m:
            if m["flags"]: st.markdown(f'<div class="bad">🚫 Unverified legal reference flagged: {html.escape(", ".join(m["flags"]))}</div>', unsafe_allow_html=True)
            else: st.markdown('<div class="ok">✅ Legal references checked against verified list</div>', unsafe_allow_html=True)
            if m["used"]:
                st.markdown('<div class="h4">📚 Sources used</div>', unsafe_allow_html=True)
                tbl = "".join(f'<tr><td style="vertical-align:top;padding:3px 8px 6px 0"><span class="tag">{i}</span></td><td style="font-size:.8rem">{html.escape(ENTRIES[i]["title"])}<br><span class="hint">{html.escape(ENTRIES[i]["cite"])}</span></td></tr>' for i in m["used"] if i in ENTRIES)
                st.markdown(f'<div class="card"><table style="width:100%;border-collapse:collapse">{tbl}</table></div>', unsafe_allow_html=True)
                links = {l.strip() for v in m["links"] for l in v.split(",")}
                st.markdown("Verify at: " + " · ".join(f"[{l.replace('https://','')}]({l})" for l in sorted(links)))

with chat_col:
    for msg in ss.h:
        with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else AVATAR_BOT):
            if msg["role"] == "user": st.write(msg["content"])
            else: render_reply(msg["content"])
