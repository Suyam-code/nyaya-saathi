"""python run_tests.py            -> runs all cases against the real model, writes raw_outputs/*.json (unedited)
   python run_tests.py --guardrail -> offline unit test of the guardrail with deliberately hallucinated replies (no API key)"""
import json, sys, pathlib, time
import lawyer
OUT = pathlib.Path(__file__).parent / "raw_outputs"; OUT.mkdir(exist_ok=True)
if "--guardrail" in sys.argv:
    bad = [{"reply":"Under Section 420 IPC you can file an FIR. See Sharma v. Gupta. Also the Consumer Safety Act, 2031 helps."},
           {"reply":"File on e-Daakhil within 2 years [CPA-LIMIT] under Consumer Protection Act, 2019, Section 69."},
           {"reply":"Per [FAKE-TAG] you can sue."}]
    res = [{"reply": b["reply"], "flags": lawyer.guardrail(b)} for b in bad]
    (OUT / "guardrail_unit_test.json").write_text(json.dumps(res, indent=2, ensure_ascii=False)); print(json.dumps(res, indent=2, ensure_ascii=False)); sys.exit()
for c in json.load(open(pathlib.Path(__file__).parent / "tests" / "cases.json")):
    f = OUT / f"{c['id']}.json"
    if f.exists() and "--force" not in sys.argv:
        print(c["id"], "already done, skipping"); continue
    r = lawyer.respond([{"role":"user","content":c["input"]}])
    text = json.dumps(r, ensure_ascii=False)
    r["_check"] = {"routed_ok": r["topic"] == c["topic"],
                   "must_hit": {m: (m.lower() in text.lower()) for m in c["must"]},
                   "must_not_hit": {m: (m.lower() in text.lower()) for m in c["must_not"]}}
    (OUT / f"{c['id']}.json").write_text(json.dumps(r, indent=2, ensure_ascii=False)); print(c["id"], r["_check"]); time.sleep(20)
