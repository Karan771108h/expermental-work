# Ideal-Party Accountability Audit

## RajScore app (P1 build — running code)

Server-rendered FastAPI + SQLite in [`app/`](app/); the seed corpus (`data/scores.csv`, `data/timeline.csv`) is loaded on first boot.

```bash
pip install fastapi "uvicorn[standard]"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- `/` scoreboards under your personal **trust dial** (cookie `rs_trust`: `official|balanced|open` — `open` reproduces REPORT.md totals exactly; `balanced` hides wiki/tweet-grade seed rows by design)
- `/entities` + `/entity/<id>` — aliases, composites, sparkline, open challenges
- `/cases` + `/case/<id>` — per-parameter seed vs live median, A/B/C evidence grades, source links, **vote** and **challenge** forms (login-gated)
- `/auth` — signup with public **leaning badge** (pbkdf2-hashed passwords, session cookies)
- `/report/<id>?frm=2014&to=2026` — instant report cards · `/timeline` (proof-linked, filterable) · `/claims` (fact-check lang)
- JSON API (`/api/entities`, `/api/case/<id>`, `/api/totals?trust=…`, `/api/vote`, `/api/challenge`) — the Next.js front end per APP_SPEC.md P-phase consumes this layer unchanged.

Status machine: SEEDED → COMMUNITY REVIEW → **CONSENSUS** (≥5 votes, ≥⅔ sign agreement); any item re-openable forever via CHALLENGED + counter-evidence link (`cases.status` flips live).

### P2 layer — fundamentals (added after user review)

- **`/fundamentals`** — the bedrock idea: **atomic, irreplaceable building blocks** (*opacity ≈ 6, proving institutional scam ≈ 50, constitutional siege ≈ 100…*) plotted on a **0–100 severity spectrum**. Parameters are now **compositions of fundamentals** (e.g. a press-shy PM and a proven scam can never be equal by construction).
- **Crowd placement**: propose a new fundamental (name + one-line objective definition + polarity + suggested position + date); members submit placements, ≥5 placements lock the consensus position to the crowd mean. Everything re-challengeable forever.
- **Compose-a-parameter** on every case page: pick fundamentals + strengths → server computes fundamental-scale points → normalises to the −5..+5 pool. Compositions render as chips on the case.
- **Dates are mandatory everywhere** (votes, challenges, fundamental placements/proposals) → `/timeline` now has a **community activity layer** alongside the proof-linked master timeline.
- **First-run tutorial**: modal walkthrough on first visit + `/tour` page; replayable from the footer.

--- (Congress vs BJP, Modi vs Rahul) — 1947 → 1 Sep 2026

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

## App direction (v2, Sept 2026)
The app is designed as a **people-run** system, not an AI oracle: users mint entity IDs, propose case-specific parameters, score with mandatory evidence links, set personal source-trust profiles (e.g. "court orders only"), and everything — even old scored items — stays challengeable forever. Consensus = quorum + supermajority under a leaning-balanced jury; consensus items go "stable", never "final". See `APP_SPEC.md` (v2) for the full loop, anti-brigading, promise register, and yearly-report-card generator.
