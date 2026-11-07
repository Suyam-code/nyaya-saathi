# Nyaya Saathi — grounded AI legal helper (Kuku Problem 2)
Run: `pip install -r requirements.txt`, set `LLM_API_KEY` (+ `LLM_PROVIDER`, `LLM_MODEL`, `LLM_BASE_URL`), then:
- `streamlit run app.py`  (chat UI)  |  `python lawyer.py` (CLI)
- `python run_tests.py` (7 cases -> raw_outputs/)  |  `python run_tests.py --guardrail` (offline)
Add a law: append an entry to `kb/laws.json`. Nothing else changes.
