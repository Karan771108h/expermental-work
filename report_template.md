# The Ideal‑Party Benchmark Report
### Congress vs BJP (1947 → September 2026) • Modi vs Rahul Gandhi • A case-by-case, relative-point audit against the ideal-party constitution
*Compiled 1 September 2026 • Research method: every claim linked to a primary or court-grade source, or two independent credible media; contested numbers shown from BOTH sides in §7. Data files: `data/timeline.csv`, `data/scores.csv`, `data/scores_computed.csv`.*

---

## 0. TL;DR — the headline numbers

| Actor | Governance ledger | Opposition ledger | **Composite** | Cases scored |
|---|---|---|---|---|
| **Congress** | **−43.75** (34 cases) | **+34.50** (15 cases) | **−9.25** | 49 |
| **BJP** | **−29.96** (45 cases) | **−6.00** (10 cases) | **−35.96** | 55 |
| **Narendra Modi (person)** | — | — | **−6.50** | 16 |
| **Rahul Gandhi (person)** | — | — | **+4.17** | 14 |

**Read the table correctly:**
- *Both* parties are negative overall. That is not a bug — the yardstick here is your "ideal party" (merit over dynasty, facts over freebies, institutions over individuals, country over seat-count). Measured against that bar across 79 years, neither comes out as ideal; this report shows **who is worse on which dimension, and who is better on which, with proof**.
- On **governance alone**, Congress (−43.75 over 34 cases) and BJP (−29.96 over 45 cases) are statistically close — both are dragged down by their biggest single-case catastrophes (Congress: Emergency −15, Babri prevention −15, 1987 Kashmir rigging −15, 1984 pogrom −14; BJP: Ayodhya movement −15, electoral bonds −13, demonetisation −12).
- The **decisive separator is opposition conduct**: Congress's 2014–26 opposition record (+34.50) contains a run of outcomes that aged well in the courts and the data (land ordinance, farm laws, demonetisation figures, Operation Sindoor solidarity), while BJP's 2004–14 opposition record (−6.00) is dominated by stances it reversed the moment it took office (nuclear deal, Aadhaar, GST, MGNREGA, insurance FDI).
- **Modi vs Rahul as individuals**: a tight band (−6.5 vs +4.17). Modi scores big on personal probity (no graft charge in 25 years of office) and delivery drive, and pays heavily for Manipur attention, Wave-2 conduct, demonetisation ownership and 12 years without a single open press conference. Rahul scores on the ordinance stand, Bharat Jodo Yatra, early COVID warning and forcing the caste-census U-turn, and pays for the "chowkidar chor hai" overreach, the dynasty factor and fact-discipline lapses.

> **What the scores are NOT:** they are not "the truth" about who is patriotic. They are the transparent output of *your rubric* applied to a documented record. Every parameter, point and weight is editable in `data/scores.csv`; re-run the totals and the conclusions update — that is exactly what the app (APP_SPEC.md) automates.

---

## 1. Method — how the points were given (and why they are fair)

### 1.1 The rubric (from your brief)
An ideal party: **internal democracy** (no dynasty/high-command), **fact-based policy** (no freebie bidding, no divisive rhetoric), **financial transparency** (funding disclosure), **continuous civic engagement**, and above all the axiom **"state permanent, government temporary, party secondary"** — support the ruling party in crises/cross-border threats, oppose it when it damages institutions, security, sound economics or parliamentary process.

### 1.2 Per-case parameters (your core instruction)
I deliberately did **not** fix one global list of parameters. Every case gets **2–4 parameters derived from what the case was actually about** (demonetisation gets `design evidence`, `economic cost`, `consultation`, `stated-aim delivery`; Operation Sindoor gets `deterrence`, `transparency`; an opposition stance gets `vindication` or `national-interest misread`). Each parameter is scored **−5 to +5**:

- **+5** exemplary, institution-building, vindicated by evidence
- **0** neutral/mixed
- **−5** grave violation of the rubric with documented harm

**Case score = mean(parameter scores) × weight**, where weight w ∈ {1 minor, 2 major, 3 landmark-period-defining}.

### 1.3 Relative scaling (your "doubling the points" idea)
Scores are **ratio-preserved**: doubling every weight, or any uniform multiplier/divisor, changes every total by the same factor and **cannot change any ranking** (mathematically: multiplying all scores by c multiplies totals by c; order is invariant). This is why the system is safe to recalibrate — e.g., if a new case deserves to sit *between* two old cases, you can rescale freely. In the app this is handled by a Kendall-τ consistency check before any rescale is allowed to commit (see `APP_SPEC.md` §4.5).

### 1.4 Source grading
- **Grade A** — Supreme Court/High Court judgments, official commissions (Shah, Nanavati, Liberhan, Kargil Review), CAG reports, RBI annual reports, PRS Legislative data, ECI, WHO/World Bank datasets.
- **Grade B** — national media of record corroborated across outlets (The Hindu, Indian Express, TOI, Business Standard, India Today, Reuters, AP).
- **Grade C** — single credible outlet or contested reading. Contested items are never decided on C evidence; §7 shows both sides.

### 1.5 Honesty disclaimers (read these before quoting anyone)
1. **Window asymmetry.** Congress governed ~55 years (1947–77, 1980–89, 1991–96, 2004–14); BJP ~18 years (1998–2004, 2014–). Congress's full opposition ledger is only scored for 1999 and 2014–26 (its 1977–96 opposition episodes are not scorable from available public data), BJP's only for 2004–14. So *per-case averages* matter as much as totals.
2. **"Week-wise"** across 79 years ≈ 4,100 weeks; this report is **event-wise and era-wise** with exact dates (the data layer supports week-granularity — the app and the Gemini prompt extend it continuously).
3. **Judgments ≠ moral verdicts.** A judgment bounds conduct; it does not certify intent to rule well. Both are noted.
4. All things being read on **1 September 2026**; several matters (Waqf Act constitutionality, 130th Amendment JPC, National Herald ED appeal, SIR litigation, ONOE JPC) are **live** and are marked OPEN.

---

## 2. Master timeline of governance (1947 → 2026), with proof

*(Full machine-readable version: `data/timeline.csv` — same rows, CSV form for the app.)*

{{TIMELINE}}

---

## 3. The scored ledgers

### 3.1 Congress in government (34 cases · total −43.75)

**Where it built:** institutions (IITs/AIIMS/ISRO roots +14), 1971 (+12), 1991 liberalisation (+14), rights framework RTI/MGNREGA/RTE (+9.8), nuclear deal (+13.5), growth & poverty decade (+7), Panchayati Raj (+10).
**Where it broke the rubric:** Emergency (−15), Babri prevention failure (−15), 1987 Kashmir rigging (−15), 1984 pogrom (−14), 1962 (−14), dynasty culture (−10), Article 356 legacy (−8).

{{CONG}}

### 3.2 BJP in government + party conduct (45 cases · total −29.96)

**Where it built:** digital stack/UPI/DBT (+13.5), welfare last-mile (+8), Kargil (+12), Golden Quadrilateral/PMGSY (+9), GST (+4), IBC (+4), infra capex (+6).
**Where it broke the rubric:** Ayodhya movement (−15), electoral bonds (−13), demonetisation (−12), Gujarat 2002 (−10), institutional-pressure complex (−9), Kandahar tradeoff (−8).

{{BJP}}

### 3.3 Congress as Opposition (1999, 2014–26 · 15 cases · +34.50)

{{CONGOPP}}

### 3.4 BJP as Opposition (2004–14 · 10 cases · −6.00)

{{BJPOPP}}

### 3.5 Narendra Modi — the person (16 cases · −6.50)

{{MODI}}

### 3.6 Rahul Gandhi — the person (14 cases · +4.17)

{{RG}}

---

## 4. Comparison charts

### 4.1 Domain-by-domain (raw points)

{{DOMAINS}}

### 4.2 What the chart says, in plain words

| Arena | Who is ahead | Why (one line) |
|---|---|---|
| Institution-building (original kind) | **Congress** | IITs/AIIMS/ISRO/Panchayati Raj/RTI era (+17 vs BJP +13.5) — but BJP owns the digital-stack class |
| Economy | **Congress** | 1991 reforms + 6.67% back-series average (+16 vs +2.25) — BJP's big wins (GST, IBC) are offset by demonetisation's −12 |
| Infrastructure | **BJP** | Quad/PMGSY base + capex acceleration (+15 vs +3) |
| Welfare delivery | **BJP** | Last-mile machines (Jan Dhan/Ujjwala/taps/toilets) (+11 vs +6) |
| Security & diplomacy | **BJP, narrowly** | Kargil + cross-LoC doctrine + Sindoor (+4.4 vs +3.3); both carry major failures (Congress 1962/IPKF; BJP Kandahar/Galwan optics/Pahalgam) |
| Democratic-institution hygiene | **Neither — Congress worse** | Emergency + Art 356 legacy (−37.25) vs BJP's ED/EC/data complexes (−24.17) — different decades, same instinct |
| Social cohesion | **Neither** | BJP −29.7 (Ayodhya movement, Gujarat 2002, CAA-NRC, Manipur) vs Congress −23.8 (1984, Shah Bano, Babri lock/unlock politics) |
| Corruption/accountability | **Both negative** | UPA's presumptive-loss era (−13) vs BJP's opaque funding architecture (−19) — nature differs (rent-seeking vs secrecy-by-design) |
| Opposition conduct | **Congress decisively** | +34.5 vs −6.0 — see §5 vindication ledger |
| Internal party democracy | **Slightly Congress** | BJP has cadre strength (−0.67 net on culture) vs Congress dynasty (−7) partially offset by the 2022 elected presidency |

### 4.3 The "who is less un-ideal, finally" index

- Governance-only: **BJP −30.0 vs Congress −43.75** (Congress carries the heaviest single violations; BJP's record is more recent and narrower).
- Opposition conduct: **Congress +34.5 vs BJP −6.0**.
- **Composite: Congress −9.25 · BJP −35.96.**
- Sensitivity: if you delete all opposition-ledger rows (some readers consider only governance as "work"), BJP (−29.96) edges Congress (−43.75). If you include opposition duty as the rubric demands (your watchdog clause is explicit), Congress closes the ledger far better. **Both readings are printed so no one can accuse this report of hiding either.**

---

## 5. The support/oppose ledger — who stood where, and how it aged

This is the section you specifically asked for (370, triple talaq, UPI, and the mirror cases where BJP obstructed Congress-era reforms, then adopted them).

| # | Issue | Government's move | Opposition's stand | Evidence since | How each side aged |
|---|---|---|---|---|---|
| 1 | **Article 370 (Aug 2019)** | BJP abrogated; J&K split into UTs amid detentions | Congress opposed manner & bifurcation, voted against Reorganisation Bill (some leaders — Scindia, Tewari — broke ranks) | SC upheld abrogation 5–0 (11 Dec 2023); elections held Sep–Oct 2024; statehood still un-restored by Sep 2026 (Omar Abdullah mulls joining SC case) | **BJP: substance durable, manner costly;** Congress: principled on process but read the nation wrong electorally |
| 2 | **Triple Talaq Bill (2019)** | BJP criminalised instant triple talaq (3-yr jail) | Congress: supported Shayara Bano verdict, opposed criminalisation, demanded select committee; voted against when refused (RS 99–84, 30 Jul 2019) | Law in force; FIR data mixed; women's groups split on jailing husbands | **BJP's principle aged well, its process (no committee) didn't.** Congress: procedurally right (your rubric's committee rule), optically punished |
| 3 | **UPI** | BJP govt scaled it (launched Apr 2016 by NPCI/RBI; now ~24,162 cr txns FY 2025-26, live in 11 countries) | **CLAIM-CHECK: "Congress opposed UPI" is FALSE as stated** — no party vote against it exists; what exists are individual scepticisms (Chidambaram on vendor usability; Tharoor on infrastructure), which aged badly. BJP's 2026 counter that NPCI was UPA-incorporated (2008) is factually true | UPI = world's largest real-time rail | **Shared heritage:** UPA laid rails, BJP built the station and ran the trains. Both sides' pure-credit claims fail |
| 4 | **GST** | BJP passed 101st Amendment, launched 1 Jul 2017; GST 2.0 two-slab reset 22 Sep 2025 | UPA proposed 2006-style GST; BJP-ruled states (Modi's Gujarat, MP) blocked 2011-13 (₹14,000 cr loss claim); Congress voted FOR in 2016 then called rollout 'Gabbar Singh Tax'; Congress claims 2.0 vindicates its old demand | Collections ~₹1.9L cr/mo; structure simplified only in 2025 | **Both flipped positions for electoral convenience;** concept: bipartisan; delivery: BJP; delay: BJP-era states + Congress-era state dissent — shared blame |
| 5 | **Aadhaar** | BJP passed Aadhaar Act 2016 as Money Bill; made it the spine of DBT | BJP (pre-2014): 'fraud', Modi's 'jadi booti' jibe, security-threat letters; Congress (post-2014): Jairam Ramesh challenged Money Bill route | SC (2018): Aadhaar valid, corporate linkage (s.57) struck, privacy limits imposed | **BJP's pre-2014 hostility aged terribly (it now owns Aadhaar);** Congress's court challenge partially vindicated |
| 6 | **MGNREGA** | UPA created (2005) | Modi in Lok Sabha (Feb 2015): "living monument of failure" | BJP ran record outlays; COVID lifeline (Azim Premji studies) | **BJP's rhetoric aged badly; UPA's scheme aged well** |
| 7 | **Nuclear deal (2008)** | UPA pushed; won trust vote 275–256 amid cash-for-votes scandal | BJP voted against | BJP in office (2014–) deepened the same architecture; Khan? In 2025, two joint sessions of nuclear cooperation continue | **BJP's vote aged badly** (pure anti-incumbency posture); UPA's vision aged well, its cash-for-votes stain did not |
| 8 | **Farm laws (2020)** | BJP passed via ordinances; RS voice vote, no division | Congress opposed from day 1, demanded JSM hearing | SC stayed (12 Jan 2021); repealed 1 Dec 2021 without debate, weeks before UP/Punjab polls | **Congress's opposition fully vindicated;** BJP's process (and exit) is a case study in your "bills without committee review" clause |
| 9 | **Demonetisation (2016)** | BJP's move | Congress (Rahul front and centre) opposed | RBI (Aug 2018): 99.3% of banned notes returned | **Congress's critique vindicated on stated aims** (recovery failed); BJP's later re-justifications (cashless share) partially true but post-hoc |
| 10 | **Land ordinance (2015)** | BJP ordinance diluting UPA's 2013 LARR consent clauses | Rahul's "suit-boot" campaign; Congress street + House resistance | Ordinance lapsed Aug 2015; govt let states customise | **Congress's constructive-opposition win** — textbook use of your "oppose when stakeholder consultation is skipped" row |
| 11 | **Electoral bonds (2018–24)** | BJP created anonymous-donor scheme via money bills | Congress opposed in Parliament; *also encashed ₹1,123 cr* | SC struck it down unanimously (15 Feb 2024, Art 19(1)(a)); SBI forced to link donors | ** BJP's scheme struck down; Congress's opposition genuine but purchase of ₹1,123 cr dilutes it. Winner: the Constitution (and ADR).** |
| 12 | **Women's reservation** | UPA passed it in RS 2010 (died in LS); BJP enacted it 2023 | Both supported in principle at different times; Congress voted YES 2023, asked for rollout + OBC quota | Activation deferred to post-census/delimitation (~2029) | **Shared credit, shared foot-dragging** — 13 years of cross-party dithering |
| 13 | **FDI multi-brand retail (2012)** | UPA notified 51% | BJP street-blocked; 2014 manifesto promised rollback | BJP retained status quo on multi-brand but eased single-brand/defence | **BJP flip-flop** (opposed for votes, kept for economics) |
| 14 | **Insurance FDI 49%** | UPA tried 2012 | BJP stalled | BJP passed the same 49% in 2015 | **BJP flip-flop** |
| 15 | **CAA (2019)** | BJP enacted religion-linked citizenship test | Congress opposed (Art 14) | SC cases pending 6+ years; rules notified only Mar 2024; Assam NRC (19 lakh excluded, many Hindu) repudiated by BJP itself | **BJP's NRC misfire self-owns the "deport all infiltrators" plank;** Congress's objection open in court — unresolved |
| 16 | **Caste census (2025)** | BJP Govt approved caste enumeration (30 Apr 2025), folded into Census 2027 (notified 4 Jun 2025) | Congress/Rahul demanded it publicly since 2021–2024; claimed credit | "Centre bowed to pressure" reads accurate; RSS chief met PM 29 Apr | **Rahul's clearest agenda-setting win; BJP U-turn documented on video** (Modi 2023-24 clips calling caste demands divisive) |
| 17 | **Operation Sindoor (May 2025)** | BJP executed 4-day campaign vs terror HQs/airbases; cessation at 1700h 10 May | Congress: full support, joined all-party delegations; later questioned aircraft losses & Trump-claim inside Parliament | CDS Chauhan (Aug 2025): "ceasefire decided between two DGMOs"; govt ack'd Kap?l losses rectified fast | **Both behaved per your crisis doctrine:** Congress = support + Parliamentary (not street) scrutiny; BJP = decisive force, less-than-full ceasefire transparency |
| 18 | **'Vote chori' / Bihar SIR (2025)** | ECI (independent; CEC appointed under 2023 law that dropped CJI) ran SIR; rolls 7.8 cr → 7.42 cr | Rahul: '1 lakh stolen votes' (Mahadevapura, 7 Aug); CEC Kumar's 7-day affidavit ultimatum (17 Aug); SC directed disclosure of deletions | Some Rahul examples rebutted (Subodh Kumar BLA case); ECI itself filed FIR in Aland deletion attempts; NDA then won 202/243 | **Both sides over-reached:** Rahul's headline number didn't survive scrutiny, ECI's conduct didn't fully reassure (its own FIR proves attempted abuse exists). OPEN |
| 19 | **National Herald (ED vs Sonia/Rahul)** | ED filed first PMLA charge sheet vs both Gandhis (9 Apr 2025; ~₹5,000 cr claim) | Congress: 'political vendetta' | Trial court REFUSED cognisance 16 Dec 2025 (probe founded on private complaint, no FIR); HC notice on ED appeal; hearing 12 Mar 2026 | **Courts, not either party, are deciding.** BJP's agency-driven pressure loses this round procedurally; nothing yet exonerates on merits. OPEN |
| 20 | **Shadow history both share** | UPA misused CBI ('caged parrot', SC 2013); Congress imposed Emergency | Jan Sangh/RSS leaders were Emergency prisoners (aged well for BJP's forebears) | ED/CBI opposition-skew data (95% since 2014, vs 54% in UPA decade) | **Instrument abuse is an Indian-governing-party disease, not a party trait** — this is your Financial-Transparency & Institutions clause failing under both |

---

## 6. The two men — Modi vs Rahul, beyond the party files

**Narendra Modi (−6.50, 16 cases).** Strengths that survive every audit: zero personal corruption charge in 25 years of executive office (+8, weight 2, because the probity bar in Indian public life is this rubric's Principle 3 applied to a person), delivery discipline, Mann Ki Baat's weekly civic voice, the Sindoor doctrine, and global projection. Liabilities the record can't wash: 12 years without one open, unscripted press conference (−3); owning demonetisation personally when RBI's own numbers voided its stated aim (−6); campaigning through Wave-2 (−6); 28 months of Manipur silence/distance (−6); the 2002 question the courts legally closed but history keeps open (−2 net after the judicial-outcome credit).

**Rahul Gandhi (+4.17, 14 cases).** The single most rubric-consistent act by either man is his: on 27 Sep 2013 he publicly destroyed his own Cabinet's ordinance protecting convicted legislators (+3) — precisely "party survival below institutional duty," even though it humiliated his own PM abroad. Add the early COVID warnings, a 4,080 km Bharat Jodo walk, the post-2019 resignation gesture, and that his caste-census demand literally became national policy in April 2025. Liabilities: he IS the dynasty exemption his rubric fails (+0 on this axis? no — −6); the Rafale campaign's overreach cost him an apology in the Supreme Court (−5); "vote chori" needed a filed affidavit it never got (−0.5); and a drumbeat of fact-slips keeps handing opponents clips.

**Net:** as *people measured against the ideal-leader clauses*, Rahul edges Modi on accountability-facing conduct, Modi dominates execution-facing conduct, and *both* fail the transparency-to-press clause for different reasons (Modi: no pressers; Rahul: no affidavits filed on his own mega-claims).

---

## 7. Contested facts — shown from both sides (the "double check" section)

| Contest | Side A | Side B | What this report did |
|---|---|---|---|
| 2G 'scam' | CAG: ₹1.76 lakh cr presumptive loss; SC cancelled licences as arbitrary (2012) | Trial court (2017): all acquitted, "scam… artfully arranged beyond recognition"; appeals pending in Delhi HC | Scored as **process failure (−3)** with **criminality_proof +2** — not as proven loot, not as innocence |
| COVID deaths | WHO: ~4.7 million excess (2020-21) | Govt: methodology "unsound", official toll ~4.8 lakh (2020-21) | Data-transparency parameter scored on what is not disputed: govt withheld all-cause mortality from WHO |
| UPA vs NDA GDP | NSC-style: UPA ~8.1% avg | MoSPI back-series: UPA 6.67%, NDA-1(4y) 7.35% | Both series printed; growth credit split |
| Rafale | SC clean chit 2018 (review dismissed 2019) | French probe; "chowkidar chor hai" apologised in SC | Rahul's campaign scored for overreach, not for raising oversight |
| Electoral rolls (2025) | Rahul: mass theft | ECI: "wrong analysis", affidavit challenge; own FIR in Aland | Both scored separately; neither absolved |
| Ahmedabad Air India crash | AAIB: both fuel switches cut, pilots deny | Families: 'vague' report; foreign press vs AAIB tells | Logged as crisis-transparency watch item, no points assigned (investigation live) |
| Farmers' protest deaths | ~700+ (protest unions) | Govt: no official count | Point flow only from what is documented (SC stay, repeal, zero-debate) |

---

## 8. If you had to fix ONE thing per party

- **Congress:** the dynasty clause is the largest single negative on its ledger (−10 culture, −6 Rahul's embodiment). The 2022 Kharge election (+3) was a start; an elected, term-limited AICC and ticket-by-ballot would do more for its score than any manifesto.
- **BJP:** opacity-by-design — electoral bonds (−13), ED/EC pressure (−9), press ecology (−4.7) — is a self-chosen wound. A funding-reform Act written with the struck-down-bonds judgment as its floor would net +8 or more overnight on its own rubric.

## 9. Files, and how to keep this alive

- `data/timeline.csv` — every dated event with a proof link (the app ingests this)
- `data/scores.csv` — every case, parameter, point, weight, justification, sources (editable)
- `data/scores_computed.csv` — adds the computed case score
- `GEMINI_PROMPT.md` — paste into Gemini (Deep Research) to regenerate/extend this continuously
- `APP_SPEC.md` — design for the auto-scoring app (auto entity IDs for any noun — party/person/scheme/verdict — auto parameters, relative scoring, rescale-invariant)

## 10. Limitations

Post-2014 items have denser digital records than 1947–96 items; weight distribution compensates but cannot erase the media-density bias. Scores are applied-judgment on sourced facts, and are designed to be challenged line-by-line — that is a feature: the CSV is the argument.
