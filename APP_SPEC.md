# APP SPEC — "RajScore": an auto-updating accountability ledger for Indian political actors
*(Companion to REPORT.md. This file is the engineering blueprint; the research artefacts (`data/*.csv`) are its seed corpus.)*

## 1. What it does
Watches Indian politics continuously (news, Parliament, courts, PIB, ECI, commissions), auto-creates an ID for **every noun** it encounters — party, person, scheme, act, verdict, agency, panel — clusters events into **cases**, invents case-specific **parameters**, proposes **relative scores**, and publishes an always-current ledger: exactly the manual method used in REPORT.md, automated.

## 2. Core concepts

### 2.1 Entities (auto IDs for any noun)
```
entity_id:  {type}:{slug}          # e.g. person:rahul-gandhi, verdict:electoral-bonds-2024, scheme:upi
types:      party | person | scheme | act | verdict | agency | crisis | election | event
fields:     aliases[], first_seen, parent (event→case), current status (OPEN/CLOSED), wikidata_id (for resolution)
```
A resolver maps "RG", "राहुल गांधी", ex-Congress president → same ID. New nouns are auto-minted on first sighting; a merge-review queue handles duplicates.

### 2.2 Cases
An event cluster bound in time/geography with a primary actor set. Each case gets:
- `parameters[]` — 2–4, **proposed by the rubric engine, not from a fixed list** (your instruction). Proposal logic: map case type-class (war / welfare scheme / graft case / opposition stance / institutional act / crisis response) → candidate parameter sets → LLM rewrites to case-specific wording → human/auto accept.
- `param_scores[]` ∈ −5..+5, each with **evidence_links[]** and a **source_grade** (A/B/C per REPORT §1.4).
- `weight` ∈ {1,2,3}.
- `case_score = mean(param_scores) × weight`.

### 2.3 The evidence ledger (non-negotiable)
Nothing publishes without a link per parameter. Every link is archived (snapshot), graded, and cross-checked: **A-grade alone can publish; B needs two independent outlets; C stays OPEN and renders both readings.** Viral partisan claims are routed to a **claim-check** workflow with verdicts (TRUE/MOSTLY/HALF/MOSTLY/FALSE/UNVERIFIABLE) — see the UPI row in REPORT §5 for the template.

### 2.4 Relative scoring + safe rescaling (your "doubling" rule)
- Scores are ordinal-robust: any positive affine transform `x' = a·x + b (a>0)` preserves all rankings. The engine enforces this on every recalibration.
- When a new case "belongs between" two existing ones, the system triggers a **rescale proposal**: re-space the domain vector, run a **Kendall-τ check** (must equal 1.0 vs. pre-rescale order within the same domain), auto-commit if pass, else human review.
- Nightly job: cross-domain consistency audit (a +3 in Security should be defensible against a +3 in Economy; drift flagged).

### 2.5 Opposition mirror-test
For every "actor X opposed policy Y" record, the engine auto-queries: did X later adopt/extend Y in office? If yes → flip-flop row (extra scoring weight on the `consistency` axis). Seeded exemplars: Aadhaar, GST, MGNREGA, insurance FDI, nuclear deal.

## 3. Data model (matches the shipped CSVs)
```sql
entities(entity_id, type, name, aliases, wikidata_id, status)
cases(case_id, title, domain, period, weight, opened_at, status)
case_actors(case_id, entity_id, role)          -- role: ruling|opposition|person
param_scores(case_id, actor_id, param, score, justification, evidence_json, grade, updated_at)
timeline(event_id, date, actor_id, case_id, summary, source_url)
claim_checks(claim_id, text, verdict, actor_id, evidence_json)
rescale_log(run_id, domain, kendall_tau, diff_json)
```
`scores.csv` ↔ `param_scores` rows; `timeline.csv` ↔ `timeline` rows. The seeds load verbatim.

## 4. Pipeline (weekly cron + on-demand)
1. **Ingest:** PIB, PRS Legislative, Lok/Rajya Sabha records, SCI/High-Court feeds, CAG, ECI, RBI, WHO/WB datasets + wires (PTI/ANI) + outlets of record (Hindu/IE/TOI/HT/BS/Reuters/AP).
2. **Extract:** events + quotes → entity resolution → cluster into cases (time/geo/actor windows).
3. **Parameter proposal:** rubric engine → candidate params, domain, weight.
4. **Scoring draft:** LLM proposes −5..+5 per param, bound to evidence links (A/B graded; auto-C if single-sourced).
5. **Rescale check** (§2.4) → publish to review queue.
6. **Human gate (MVP):** analyst approves/rejects; every edit logged (auditability).
7. **Publish:** API + dashboards; weekly diff notes ("this week: case B41 moved −0.1 because JPC testimony X").
8. **Aged-well revisits:** time-triggered re-review (e.g., 'triple talaq FIR data, 12 months later'), updating the vindication ledger.

## 5. MVP stack (build path you can start with)
- **Backend:** FastAPI + Postgres(+pgvector) • **Jobs:** APScheduler/cron • **NLP/scoring:** any strong LLM with JSON-mode (schema-enforced) • **Front end:** Next.js dashboard (entity pages, case pages, heat tables, claim-check cards, rescale diffs) • **Hosting:** single VPS is enough.
- **Seed load:** `data/scores_computed.csv` + `data/timeline.csv` → day-one content = this report.
- **First vertical slice (2 weeks):** entities + timeline read API + static ledgers render. Week 3–4: ingest PIB+PRS+SCI; week 5: scoring drafts + rescale logs; week 6: claim-check UI.

## 6. Guardrails
- **No unsourced score, ever.** • **Both-sides rendering** for contested items. • **Party-agnostic grade counts** published monthly (proves the engine isn't over-reliant on one side's media ecology). • Adversarial test suite: seed claims known to be tricky ("Congress opposed UPI", "2G = ₹1.76L cr scam") must come out correctly nuanced before any release.

## 7. What still needs you
Next step (say the word): I scaffold the FastAPI+Next.js project in this repo, load the seed CSVs, wire the PIB/PRS/SCI ingesters, and stand up the weekly scoring job with the Kendall-τ rescale gate — then point a live preview at it.
