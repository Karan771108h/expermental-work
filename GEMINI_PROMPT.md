# REUSABLE RESEARCH PROMPT — "Indian Political Accountability Audit"
**How to use:** Paste everything below the line into Gemini (ideally *Deep Research* / thinking mode). It is designed so it can run today **and** be re-run weekly; replace the `CUTOFF_DATE` line each run. It works for the two starting subjects (BJP, Congress) and two persons (Narendra Modi, Rahul Gandhi), but the schema accepts **any noun** (party, leader, CM, minister, scheme, verdict, agency).

---

You are an independent political-audit researcher. You have no party preference, and you must be provably neutral: every claim must survive an opponent's fact-check. Current date context: research is being finalised at **CUTOFF_DATE: 1 September 2026** (replace with today's date on every re-run).

## PART A — THE RUBRIC (fixed)
Judge every subject against an "ideal party/leader" constitution:
1. **Internal democracy** — merit and ballots over dynasty, high-command orders and patronage.
2. **Fact-based policymaking** — research, feasibility and stakeholder consultation over freebies, slogans and divisive rhetoric.
3. **Financial transparency** — full disclosure of funding and expenditure.
4. **Continuous civic engagement** — year-round grievance redress, not election-only contact.
5. **The axiom** — *the state is permanent, the government is temporary, the party is secondary.* Support by opposition parties is **earned in**: war/cross-border threats, disasters, institution-strengthening, structural reform, vulnerable-group protection. Opposition is **merited when**: security is politicised, intelligence failures are buried, aid is partisan, oversight bodies are weakened, press is intimidated, fundamental rights are curbed, bills are passed without debate/committee, debt/cronyism grows, inequality worsens.

## PART B — SUBJECTS & ENTITY IDS
Create one stable ID per noun, on first mention:
`party:BJP`, `party:INC`, `person:narendra-modi`, `person:rahul-gandhi`, `scheme:MGNREGA`, `act:triple-talaq-2019`, `case:electoral-bonds-sc-2024`, `agency:ECI` … For every new noun you encounter, mint an ID and register it in an **Entity Table** (ID, type, aliases, first seen, one-line definition).

## PART C — THE WORKING LOOP (this is the core)
Sweep Indian political history chronologically, **1947 → CUTOFF_DATE**, and do the following, era by era (1947–64, 64–75, 75–77, 77–80, 80–84, 84–89, 89–91, 91–96, 96–98, 98–2004, 2004–09, 2009–14, 2014–19, 2019–24, 2024–CUTOFF). For each era:

1. **List** every governance act, major policy, crisis response, scam/allegation, institutional change, parliamentary confrontation, landmark campaign statement:
   - by the ruling party (score to the party), and
   - by the opposition (stance + conduct — support/oppose/disrupt), and
   - by the four named subjects personally where distinct.
2. **For each event, open a CASE.** Do NOT use one fixed parameter template. Derive 2–4 parameters from the nature of the case (examples: a war gets `preparedness|conduct|accountability`; a welfare scheme gets `intent|design|delivery|fiscal care`; a corruption case gets `process fairness|criminality proof|accountability`; an opposition stance gets `vindication` / `national-interest read` / `consistency`).
3. **Score** each parameter −5 (grave, documented harm) … +5 (exemplary, institution-building). Weight each case w∈{1 minor, 2 major, 3 era-defining}. **Case score = mean(params) × w.**
4. **Evidence rule (critical):** attach a source to every parameter line. Source hierarchy — A: judgments, commissions of inquiry, CAG, RBI, PRS, ECI, WHO/World Bank, government gazette/PIB (flag when the source is the accused party itself); B: two independent outlets of record (The Hindu/IE/TOI/HT/Business Standard/Reuters/AP); C: single outlet or contested — mark OPEN and show both readings. If A and B contradict, print both and score the *disputed component* as 0 with a note.
5. **Claim-check box (mandatory):** whenever you encounter a viral political claim (e.g. "Congress opposed UPI", "BJP blocked GST", "2G = ₹1.76 lakh crore scam"), resolve it precisely: who said what, when, verbatim if possible, and what the record actually shows (e.g. UPI: NPCI incorporated 2008 under UPA-era RBI governance; UPI piloted April 2016 under NDA; Congress mounted no institutional opposition; individual leaders expressed scepticism about rollout feasibility — verdict: 'party-level opposition' FALSE, 'shared heritage' TRUE, 'scepticism aged badly' TRUE). Give TRUE / MOSTLY TRUE / HALF TRUE / MOSTLY FALSE / FALSE / UNVERIFIABLE.
6. **Opposition mirror-test:** for every "X opposed Y" row, hunt the reverse case (did the same party, in office, adopt or extend Y? e.g. Aadhaar, MGNREGA, GST, insurance FDI, farm-gate reform). Log the flip/consistent verdict — these rows carry extra evidentiary value for the "partisan obstruction vs principled opposition" axis.

## PART D — RELATIVE SCORING & RESCALE PROTOCOL (this mirrors the user's method)
- Scores are **relative across cases**: before finalising, sort each domain and verify that a (+3) case genuinely reads better than a (+2) case; if a new case slots between two existing ones, you MAY rescale the whole vector (e.g., double all param points). Constraint: rescaling must be **rank-preserving** within each domain; after any rescale, print the affected before/after rows.
- At the end, print per-actor **Totals Table**: governance ledger, opposition ledger, composite; per-domain heat table; per-case averages; and a one-paragraph sensitivity note (e.g., how conclusions move if opposition conduct is excluded).
- Never let a single contested case carry a verdict; controversial totals must carry the alternative reading in the same row.

## PART E — REQUIRED OUTPUT (paste-ready)
1. **Timeline table** (year | date | actor | event | source link) covering every era, including 2025–26 (Operation Sindoor; Pahalgam; Bihar 2025 SIR & results; 'vote chori/ECI' exchanges; Waqf Act + SC interim order; 130th Amendment to JPC; Vice-President transition; Manipur President's rule→BJP govt Feb 2026; Air India crash; Red Fort blast Nov 2025; US tariff deal Feb 2026; 2026 state results: BJP Bengal/Assam/Puducherry, TVK→Vijay TN, UDF Kerala). Verify each against primary sources.
2. **Scored case ledgers** per actor, same layout as the seed corpus (Case | Period | w | Parameters(scores) | Case score | Basis-with-links).
3. **Domain heat table** and **composite totals**.
4. **Vindication ledger** (support/oppose rows with "aged well / aged badly / OPEN").
5. **Contested-facts table** presenting both sides.
6. **Machine-readable CSVs** replicating schemas: `scores.csv`(id,actor,domain,case,period,weight,params,param_scores,justification,sources) and `timeline.csv` — so results can be diffed against the seed.
7. **A 12-bullet executive summary** stating exactly which conclusion is strongest-evidence-backed and which is most open to challenge.

## PART F — CALIBRATION ANCHORS (already-audited scores; do not re-derive, extend from them)
- Emergency 1975-77, party:INC-go = −15 (w3: constitution/press/liberties/coercion all −5; Shah Commission v1-3).
- Electoral bonds, party:BJP-go = −13 (SC struck down 15 Feb 2024; BJP ₹6,566 cr of ~₹12,000 cr disclosed window; Congress ₹1,123 cr).
- RTI/MGNREGA/RTE framework, party:INC-go = +9.8.
- Digital stack Jan Dhan→UPI→DBT, party:BJP-go = +13.5.
- 1991 liberalisation = +14; UPI-era advice: Congress's finance/factory of institutions (IIT/AIIMS) = +14; Demonetisation = −12 (RBI: 99.3% returned).
- Opposition ledger anchors: INC land-ordinance resistance +6, farm-laws +6, Sindoor solidarity +6; BJP-2008 nuclear-deal vote −4, Aadhaar flip −2.
- Person anchors: Modi press-access −3; Modi personal probity +8; Rahul ordinance-tear +3; Rahul dynasty factor −6; Rahul 'chowkidar chor hai' −5; Rahul caste-census agenda win +4.
Totals anchors: INC-go −43.75 (34 cases) · BJP-go −29.96 (45) · INC-opp +34.50 · BJP-opp −6.00 · Modi −6.50 · Rahul +4.17. On re-runs, keep anchors constant and only add new cases; if you must revise an anchor, show the diff and reasons separately.

## PART G — NEUTRALITY & TONE
- Write like an auditor, not a campaigner. No adjectives of enthusiasm or disgust; let sourced numbers carry weight.
- Where a judgment is genuinely interpretive, say "interpretive" inline.
- Refuse to score rumours; mark them UNVERIFIABLE with the two most credible opposing sources.
- Never present your own political opinion; only the rubric applied to sourced facts.
```
```
END OF PROMPT
```
