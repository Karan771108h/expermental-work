# RajScore v2 — Platform Specification (Crowd Edition)
### "Wikipedia + scoreboard" for Indian political accountability: run by people, rules editable, everything challengeable, credibility personal-tunable.

> **Update log:** v1 (AI-scoring engine) → **v2 (this file): the people do the judging.** AI only fetches, dedupes, translates and formats. The earlier research (`REPORT.md`, `data/*.csv`) becomes the **seed database** — every row in it is a user-editable, challengeable object on day one.

---

## 1. Why this shape

The v1 design assumed an engine that scores reality. Two problems with that in India:

1. **No panel can encode "credible" for everyone.** One citizen trusts only Supreme Court orders; another trusts field reporting; a third trusts first-person video. A single house score pretending to be "the truth" would be dismissed as biased — correctly.
2. **Coverage.** A research session — even a 108-case one — misses state-level and older cases (the user noted this: "you missed many things"; true — this research skipped e.g. state CMs' records, district-level incidents, most manifesto promise-tracking, 1977–96 Congress opposition conduct, nitrogen? coverage of regional parties like TMC/DMK/AAP/SP/TDP, and thousands of smaller cases). Only crowdsourcing scales.

So the platform's job is not to *decide* — it is to be the **operating system for judging**: it provides the grammar (IDs, cases, parameters, points, evidence), the process (challenge → vote → consensus → re-open), and views (scores, report cards, fact-checks) computed from whatever rules *you* chose.

## 2. The core grammar (what the app provides)

Six object types. Everything else is a view.

| Object | What users do with it |
|---|---|
| **Entity (auto ID)** | Create an ID for any noun: `party:BJP`, `person:kejriwal`, `scheme:upi`, `act:waqf-2025`, `verdict:electoral-bonds-2024`, `agency:eci`, `event:pahalgam-2025`, `promise:2cr-jobs-2018`. Aliases ("राहुल गांधी", "RG") get resolved to one ID. |
| **Case** | Any incident/policy/statement attached to 1+ entities: "demonetisation", "Chandigarh mayor ballots". Contains: period, actors, domain tags, sources. |
| **Parameter** | A scoring dimension *anyone may propose for a case* — e.g. `process fairness`, `stated-aim delivery`. No fixed global list; per-case as required. |
| **Score proposal** | A user's −5..+5 vote on a parameter **with mandatory evidence links**. A vote without a link is a comment, not a score. |
| **Evidence / Source** | A link/document with a **type** (court order / commission / CAG / official data / wire / newspaper / video / social post / affidavit) and a **grade given by the community of *your* trust-set**. |
| **Rule (rubric preset)** | A named scoring constitution: weights, allowed source types, parameter guidance. Two presets ship built-in — the "Ideal-Party Charter" (this project's rubric) and a "Development-only" preset — but **users make their own** and publish them. |

## 3. The credibility dial (the feature that makes it un-killable)

Each user sets their **Trust Profile**:
- ✅ Court orders & commission reports — always count
- ✅ CAG/RBI/ECI/WHO/World Bank datasets
- ❓ Mainstream media — count only if 2+ independent outlets
- ❌ Anonymous sources, party press releases (the accused grading itself), unsourced videos
- Source-level overrides: trust The Hindu courts desk, distrust channel X, etc.
- Verifier seats: optionally appoint "trusted graders" (retired judge, journalist YouTuber cluster…)

**Consequence:** the same case renders differently per trust profile — and the UI *shows the difference explicitly*: "Under Courts-only: BJP −13 on electoral bonds. Under All-media: −12.4. 2.1% of voters used Courts-only." Nothing pretends to be objective; everything shows its recipe.

## 4. Nothing is permanent — the challenge loop

Every object (entity merge, case datum, source grade, parameter, score, verdict) has a status machine:

```
PROPOSED → UNDER REVIEW → CONSENSUS (quorum + supermajority, e.g. 200 votes & 2:1) → STABLE (30d unchallenged)
     ↑__________ CHALLENGE (needs: 1 new evidence link OR 3 co-signers) __________↓
```

- A **challenge re-opens even "stable" items** — with new evidence mandatory (prevents endless reopening-by-spam).
- Disputes go to a **randomly-sampled, leaning-balanced jury** (see §6) that votes on evidence quality only ("Did the SC really say this?" checkable), not on politics.
- Full git-style history: no deletion, only supersession; every score carries its provenance trail ("voted 61–34 on 2026-09-14, jury #511, evidence links archived").

## 5. How a score exists (three layers, always separated)

1. **Raw votes** — the crowd's per-parameter submissions with evidence.
2. **Credibility-filtered view** — votes whose evidence passes *your* trust profile, weighted by voter reputation, collapsed by anti-brigading (§6).
3. **Final number you see** = your chosen rubric preset applied to your credibility-filtered view. Formula (default): case score = mean(param medians) × weight. Every preset is a two-line diff of this formula; users can fork presets like code.

## 6. Anti-manipulation (where all such platforms die; non-negotiable)

- **One-person-one-account:** phone-OTP + device attestation; optional Aadhaar/DigiLocker "verified citizen" badge (proof-of-personhood, identity never published).
- **Declared leaning, publicly:** every voter wears a self-declared badge (BJP-lean/Congress-lean/None/Other). Leanings are *inputs*, not secrets: aggregation shows per-lean lines; a case where BJP-leans and Cong-leans diverge wildly is flagged **POLARISED** and its score shows a band, not a point.
- **Quadratic-style dampening:** 1 person = 1 vote on whether something counts; reputation only widens your allowed score *deviation range*, never multiplies your ballot.
- **Brigade detection:** burst/coordination analytics (same-link posting waves, synchronized registrations, same-template text) freeze a case into jury mode automatically.
- **Random juries with mandatory diversity:** sampled across declared leanings, geography, account age; rotation and recusal on topics they scored before.
- **Bot/AI-text monitoring** on submissions; all votes public as data (anonymised IDs).

## 7. Everything else the platform becomes (the "what more")

1. **Fact-check vernacular** — every claim ("Congress opposed UPI", "2G = ₹1.76L cr scam") becomes a Claim object with verdict workflow; words like TRUE/HALF-TRUE/FALSE are crowdsoured but juries certify. The entity/evidence graph makes verdicts fast.
2. **Promise Register** — each manifesto point gets an ID and a status tracker (Delivered / Partial / Stalled / Broken / Open) voted annually. *Nobody in India maintains this at scale, forever.*
3. **Report cards** — auto-PDF per entity & window: "BJP 2024-25 Report Card", "Rahul Gandhi: 5-year ledger", "Karnataka state govt, any 12 months". Our REPORT.md is literally the template for the first generated document class.
4. **Topic dossiers** — query by tag: `federalism`, `farmers`, `press freedom`, `Kashmir` → timeline + scores + both-sides notes, printable.
5. **Election season mode** — constituency pages, candidate quick-ledgers, "what did this MP score" cards shareable to WhatsApp (the real Indian broadcast medium).
6. **Blind review mode** — rate a case with actor names masked; great for schools/researchers; kills halo effects.
7. **Aged-well revisited feed** — time-triggered reopeners: "farm laws: 5 years on — final score?", "370: statehood restored year?" keeps history honest.
8. **Embedding/API** — newsrooms and YouTubers embed live scoreboards (rate-limited API, attributed); journalists get a researchers' export tier.
9. **Multilingual first** — Hindi + top regional languages at parity with English; the jury layer requires at least one local-language reader per regional case.
10. **Civil-service exam/education pack** — "101 accountability cases" free module (viral distribution via coaching culture), driving the first 100k care-users.

## 8. Product surfaces

- **Entity page** — profile, trend line over years, top +/− cases, open challenges count.
- **Case page** — evidence well (per type), parameter table with live median + band, discussion, challenge button, history diff view.
- **Rule studio** — fork "Ideal-Party Charter", edit weights/source types, publish; others subscribe (your default feed respects your active rubric).
- **Dashboards** — party/topic/year composites; "most challenged this week", "new consensus reached".
- **Moderator console** — brigade alerts, jury queue, frozen topics.

## 9. Governance & neutrality (the reason people will trust it)

- Run as a **nonprofit trust** with a public charter (like an election-observer NGO); board must include declared members of at least 3 political leanings.
- **No political ads, ever.** Funding: grants + API/subscription of analytics by media/NGOs + voluntary donations; funding sources disclosed quarterly (practice what you score).
- **Source code, scoring engine, and aggregation logic public.** Secret moderation is the only thing closed.
- Legal posture (India): court-orders and CAG/RBI data usage is safe; defamation risk lives on user claims → mandatory evidence-link rule + quick-response legal cell; DPDP Act compliance for voter metadata.

## 10. Build plan

| Phase | Output |
|---|---|
| P0 (this repo, done) | Seed data: entities/cases from `data/*.csv`; REPORT.md as first "report card" |
| P1 (4–6 wks) | Read-only web app: entity/case pages, dataset browsing, search (FastAPI + Postgres + Next.js; live preview) |
| P2 (+6 wks) | Accounts + trust profiles + first alternate rubric presets; score rendering per profile |
| P3 (+8 wks) | Voting & challenge loops, juries, status machine, audit history |
| P4 (+6 wks) | Fact-check objects, promise register, report-card generator (PDF), Hindi UI |
| P5 | Anti-brigading hardening, pub API, embeddings, regional language packs, election mode |

## 11. Why it survives
- It takes **no editorial position** — the toughest group can't call it biased, they can only bring more evidence.
- The **challenge loop** means errors self-heal publicly; credibility grows like Wikipedia's.
- The **trust-profile dial** means opposite-lean users both see *their* receipt — and the divergence is itself published data (which becomes journalism).
