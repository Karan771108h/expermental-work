# Ideal-Party Accountability Audit (Congress vs BJP, Modi vs Rahul) — 1947 → 1 Sep 2026

| File | What it is |
|---|---|
| **REPORT.md** | The full research report: methodology, master governance timeline with proof links, 108 scored cases (6 ledgers), domain comparison charts, support/oppose vindication ledger (370, triple talaq, UPI claim-check, GST, Aadhaar, MGNREGA, nuclear deal, farm laws, demonetisation, electoral bonds…), Modi-vs-Rahul person files, contested-facts double-check table, limitations |
| **GEMINI_PROMPT.md** | Copy-paste prompt that makes Gemini (Deep Research) regenerate and continuously extend this same audit |
| **APP_SPEC.md** | Blueprint for "RajScore" — the auto-updating score app (auto IDs for any noun, auto parameters per case, rescale-invariant relative scoring) |
| data/timeline.csv | Every dated milestone 1947→2026 with source links (machine-readable) |
| data/scores.csv | Every case: parameters, points (−5..+5), weight, justification, sources |
| data/scores_computed.csv | Same + computed case scores (totals: INC gov −43.75 · BJP gov −29.96 · INC opp +34.50 · BJP opp −6.00 · Modi −6.50 · Rahul +4.17) |
| report_template.md / tables/ | Build inputs used to render REPORT.md (kept for regeneration) |

Regenerate tables/totals after editing scores.csv: see the python one-liner used in-session (compute = mean(params)×weight per actor).
