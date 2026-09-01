"""RajScore — SQLite layer: schema + seeding from the research CSVs."""
import sqlite3, csv, os, re, hashlib, secrets, time, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "rajscore.db")

# --- Evidence grading heuristic (MVP of the trust dial) -------------------
GRADE_A = ["sci.gov.in", "main.sci.gov.in", "eci.gov.in", "cag.gov.in",
           "rbi.org.in", "who.int", "worldbank.org", "pib.gov.in",
           "static.pib.gov.in", "indiacode.nic.in", "sansad.in"]
GRADE_B = ["thehindu.com", "indianexpress.com", "timesofindia", "indiatoday",
           "hindustantimes", "business-standard", "ndtv.com", "livelaw.in",
           "scobserver.in", "reuters.com", "apnews.com", "aljazeera.com",
           "theprint.in", "thewire.in", "tribuneindia", "outlookindia",
           "rediff.com", "deccanchronicle", "frontline.thehindu",
           "economictimes", "livemint.com", "financialexpress", "scroll.in",
           "thefederal.com", "gulfnews.com", "dw.com", "cnn.com", "bbc.com",
           "qz.com", "governancenow.com", "caravanmagazine.in", "indiaspend.com",
           "boomlive.in", "en.wikipedia.org", "wsls.com", "prokerala.com",
           "etvbharat.com", "indiatvnews.com", "ptcnews.tv", "nagalandtribune",
           "newslaundry.com", "thesouthfirst.com", "theweek.in", "firstpost.com",
           "newindianexpress.com", "nationalheraldindia.com", "vajiramandravi.com",
           "manoramayearbook.in", "edunovations.com", "thehindubusinessline",
           "organiser.org", "ibtimes.co.in", "atlanticcouncil.org", "morganlewis.com",
           "spectrumbooks.in", "visionias.in", "padhai.ai", "believersias.com",
           "pwonlyias.com", "legalonus.com", "lawbhoomi.com", "tscld.com",
           "drishtijudiciary.com", "lawsho.com", "indiatimes.com", "grokipedia.com",
           "hindutvawatch.org", "isas.nus.edu.sg", "bajajfinserv.in", "caderaedu.com",
           "nriaffairs.com", "msmsw.co.in", "timesofindia.indiatimes.com"]

def grade_url(url: str) -> str:
    u = url.lower()
    for d in GRADE_A:
        if d in u: return "A"
    for d in GRADE_B:
        if d in u: return "B"
    return "C"

PROFILE_RULES = {"official": {"A"}, "balanced": {"A", "B"}, "open": {"A", "B", "C"}}
PROFILE_LABELS = {
    "official": "Court & official only (courts, commissions, CAG/ECI/RBI, WHO/WB)",
    "balanced": "Balanced — official + outlets of record (default)",
    "open": "Open — count everything, flag the weak stuff",
}

ACTOR_MAP = {
    "CONG":      ("party:inc", "ruling-era"),
    "BJP":       ("party:bjp", "ruling-era"),
    "CONG-OPP":  ("party:inc", "opposition"),
    "BJP-OPP":   ("party:bjp", "opposition"),
    "MODI":      ("person:narendra-modi", "person"),
    "RG":        ("person:rahul-gandhi", "person"),
}

ENTITIES = [
    ("party:inc", "party", "Indian National Congress", "INC|Congress|कांग्रेस",
     "India's oldest national party (founded 1885); governed ~55 of 79 years since 1947."),
    ("party:bjp", "party", "Bharatiya Janata Party", "BJP|बीजेपी|भाजपा",
     "Founded 1980 (roots: Jana Sangh); led Centre 1998–2004 and 2014–present."),
    ("person:narendra-modi", "person", "Narendra Modi", "Modi|PM Modi|नरेंद्र मोदी",
     "PM since May 2014; Gujarat CM 2001–14."),
    ("person:rahul-gandhi", "person", "Rahul Gandhi", "RG|Rahul Gandhi|राहुल गांधी",
     "Congress leader; MP since 2004; Leader of Opposition (Lok Sabha) since 2024."),
]

CLAIMS_SEED = [
    ("Congress opposed the creation of UPI", "FALSE",
     "party:inc",
     "No party-level vote or institutional opposition to UPI exists. NPCI was incorporated in 2008 (UPA-era RBI-bank consortium); UPI piloted 11 Apr 2016 under the Modi govt. Isolated scepticism by individual Congress figures (Chidambaram on vendor usability, Tharoor on infrastructure) aged badly. Verdict detail in REPORT.md §5 row 3.",
     "https://newstodaynet.com/2026/08/26/bjp-targets-congress-over-upi-criticism;https://indianexpress.com/article/political-pulse/aadhaar-journey-bjp-digital-india-9095394/"),
    ("2G spectrum case was a Rs 1.76 lakh crore proven scam", "HALF TRUE",
     "party:inc",
     "CAG calculated a presumptive loss of Rs 1.76 lakh crore and the SC cancelled 122 licences as arbitrary (2012). BUT the special trial court acquitted all accused (21 Dec 2017, 'miserably failed'); CBI/ED appeals admitted in Delhi HC (2024), pending. Process failure proven; criminal loot not proven in court.",
     "https://en.wikipedia.org/wiki/2G_spectrum_case;https://timesofindia.indiatimes.com/india/2g-spectrum-verdict-no-proof-of-scam-says-court-a-scam-of-lies-says-congress/articleshow/62201212.cms"),
    ("BJP blocked GST during UPA, then implemented it", "TRUE",
     "party:bjp",
     "BJP-ruled states incl. Modi's Gujarat opposed the 2011 GST constitutional amendment (claims of Rs 14,000 cr loss); Congress-ruled states also dissented. BJP passed the 101st Amendment and launched GST on 1 Jul 2017. Modi admitted his doubts in the Lok Sabha (9 Aug 2016).",
     "https://www.governancenow.com/news/regular-story/-recalling-a-time-when-bjp-opposed-gst--"),
    ("Modi called MGNREGA a 'living monument of Congress failure' then ran record allocations", "TRUE",
     "person:narendra-modi",
     "LS speech Feb 2015 mocked MGNREGA; the same scheme got record usage/outlays during COVID-19 and is called a lifeline across analyses.",
     "https://www.ndtv.com/opinion/mnrega-once-reviled-by-pm-narendra-modi-saved-the-day-2370825;https://www.business-standard.com/india-news/once-called-a-failure-mgnregs-became-lifeline-during-covid-lockdown-124122701040_1.html"),
    ("PM Modi has held no solo unscripted press conference since 2014", "TRUE",
     "person:narendra-modi",
     "AP (Jun 2023): never held a solo presser as PM; pattern repeated across 2026 NZ/Australia trip per contemporaneous coverage. He does scripted interviews and Mann Ki Baat, not open questioning.",
     "https://apnews.com/article/biden-modi-press-conference-india-e9deb7a1115952f95e3683b156d4ed86;https://www.nriaffairs.com/modi-press-conference-mea-new-zealand-2026/"),
    ("Rahul Gandhi apologised in the Supreme Court in the Rafale 'chowkidar chor hai' matter", "TRUE",
     "person:rahul-gandhi",
     "He filed a written apology (2019) for attributing the slogan to the court; the SC had given the deal a clean chit (2018; review dismissed 2019).",
     "https://en.wikipedia.org/wiki/Rafale_deal_controversy"),
]

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS entities(
  id TEXT PRIMARY KEY, type TEXT, name TEXT, aliases TEXT, summary TEXT);
CREATE TABLE IF NOT EXISTS cases(
  id TEXT PRIMARY KEY, title TEXT, domain TEXT, period TEXT, weight INT,
  status TEXT DEFAULT 'SEEDED');
CREATE TABLE IF NOT EXISTS case_params(
  rowid INTEGER PRIMARY KEY AUTOINCREMENT,
  case_id TEXT, entity_id TEXT, role TEXT, param TEXT,
  seed_score REAL, justification TEXT, sources TEXT);
CREATE TABLE IF NOT EXISTS votes(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INT, case_id TEXT, entity_id TEXT, param TEXT,
  score REAL, evidence_url TEXT, created REAL,
  UNIQUE(user_id, case_id, param));
CREATE TABLE IF NOT EXISTS challenges(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT, object_id TEXT, note TEXT, evidence_url TEXT,
  user_id INT, created REAL, status TEXT DEFAULT 'OPEN');
CREATE TABLE IF NOT EXISTS claims(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  text TEXT, verdict TEXT, actor_id TEXT, detail TEXT, evidence TEXT);
CREATE TABLE IF NOT EXISTS timeline(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  year TEXT, date TEXT, era TEXT, actor TEXT, event TEXT, category TEXT, proof TEXT);
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE, pw TEXT, leaning TEXT DEFAULT 'none',
  reputation REAL DEFAULT 1.0, created REAL);
CREATE TABLE IF NOT EXISTS sessions(
  token TEXT PRIMARY KEY, user_id INT, created REAL);
"""

def q(sql, args=(), one=False, commit=False):
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    cur = con.execute(sql, args)
    rows = cur.fetchall()
    if commit: con.commit()
    con.close()
    return (rows[0] if rows else None) if one else rows

def first_year(period: str) -> int:
    m = re.search(r"(18|19|20)\d{2}", period or "")
    return int(m.group(0)) if m else 0

def init_and_seed():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    if con.execute("SELECT count(*) c FROM case_params").fetchone()[0] > 0:
        con.close(); seed_fundamentals(); return
    con.executemany("INSERT INTO entities VALUES(?,?,?,?,?)", ENTITIES)
    con.executemany(
        "INSERT INTO claims(text,verdict,actor_id,detail,evidence) VALUES(?,?,?,?,?)",
        CLAIMS_SEED)
    with open(os.path.join(ROOT, "data", "scores.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["actor"] not in ACTOR_MAP: continue
            ent, role = ACTOR_MAP[r["actor"]]
            title = r["case"]
            cid = r["id"] + (":opp" if r["actor"].endswith("OPP") else "")
            con.execute(
                "INSERT OR REPLACE INTO cases(id,title,domain,period,weight,status) VALUES(?,?,?,?,?,'SEEDED')",
                (cid, title, r["domain"], r["period"], int(r["weight"])))
            params = r["params"].split("|")
            scores = r["param_scores"].split("|")
            for p, s in zip(params, scores):
                con.execute(
                    "INSERT INTO case_params(case_id,entity_id,role,param,seed_score,justification,sources) VALUES(?,?,?,?,?,?,?)",
                    (cid, ent, role, p.replace("_", " "), float(s), r["justification"], r["sources"]))
    with open(os.path.join(ROOT, "data", "timeline.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            con.execute(
                "INSERT INTO timeline(year,date,era,actor,event,category,proof) VALUES(?,?,?,?,?,?,?)",
                (r["year"], r["date"], r["era"], r["actor_in_office"], r["event"], r["category"], r["proof"]))
    con.commit(); con.close()
    seed_fundamentals()

def hash_pw(pw: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), b"rajscore-v2", 60000).hex()

def create_user(username, pw, leaning):
    if q("SELECT id FROM users WHERE username=?", (username,), one=True):
        return None
    cur = None
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO users(username,pw,leaning,created) VALUES(?,?,?,?)",
                (username, hash_pw(pw), leaning, time.time()))
    con.commit()
    uid = con.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()[0]
    con.close()
    return uid

def new_session(uid: int) -> str:
    tok = secrets.token_hex(16)
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO sessions VALUES(?,?,?)", (tok, uid, time.time()))
    con.commit(); con.close()
    return tok

def user_by_token(tok):
    if not tok: return None
    r = q("""SELECT u.id, u.username, u.leaning, u.reputation
             FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=?""",
          (tok,), one=True)
    return dict(r) if r else None

def best_grade(sources: str) -> str:
    g = "C"
    for u in (sources or "").split(";"):
        u = u.strip()
        if u.startswith("http"):
            gg = grade_url(u)
            if gg == "A": return "A"
            if gg == "B": g = "B"
    return g

def links(sources: str):
    return [s.strip() for s in (sources or "").split(";") if s.strip().startswith("http")]

def param_median(case_id, param, profile):
    """Median of seed + crowd votes whose best evidence passes the trust profile."""
    allowed = PROFILE_RULES.get(profile, {"A", "B"})
    vals = []
    row = q("""SELECT seed_score, sources FROM case_params
               WHERE case_id=? AND param=?""", (case_id, param), one=True)
    if row and best_grade(row["sources"]) in allowed:
        vals.append(float(row["seed_score"]))
    for v in q("SELECT score, evidence_url FROM votes WHERE case_id=? AND param=?",
               (case_id, param)):
        if grade_url(v["evidence_url"]) in allowed:
            vals.append(float(v["score"]))
    if not vals: return None, 0
    return round(statistics.median(vals), 2), len(vals)

def vote_count(case_id, param=None):
    if param:
        return q("SELECT count(*) c FROM votes WHERE case_id=? AND param=?",
                 (case_id, param), one=True)["c"]
    return q("SELECT count(*) c FROM votes WHERE case_id=?", (case_id,), one=True)["c"]

def case_status(case_id):
    c = q("SELECT status FROM cases WHERE id=?", (case_id,), one=True)
    base = c["status"] if c else "SEEDED"
    if base == "CHALLENGED": return "CHALLENGED"
    n = vote_count(case_id)
    if base == "SEEDED" and n == 0: return "SEEDED (seed corpus)"
    if n >= 5:
        # consensus: 66% of votes share the seed's sign
        seed = q("""SELECT avg(seed_score) m FROM case_params WHERE case_id=?""",
                 (case_id,), one=True)["m"] or 0
        sign = 1 if seed >= 0 else -1
        same = q("""SELECT count(*) c FROM votes WHERE case_id=? AND score*?>0""",
                 (case_id, sign), one=True)["c"]
        if same / n >= 0.66: return "CONSENSUS"
        return "CONTESTED"
    return "COMMUNITY REVIEW"

# ---------------------------------------------------------------------------
# FUNDAMENTALS LAYER (P2): atomic, irreplaceable building blocks on a 0-100
# severity/virtue scale. Parameters are COMPOSITIONS of fundamentals, so unlike
# things can never be scored equal just by flat labels.
# Positions are crowd-placed relative to anchors (placement votes -> mean).
# ---------------------------------------------------------------------------

# polarity: 'harm' (negative) or 'virtue' (positive). position on 0..100.
FUND_SEEDS = [
    ("rhetoric-slip",        "Rhetorical / factual slip",            "A statement that is wrong or exaggerated, no lasting damage", "harm", 3,  1, 5),
    ("opacity",              "Opacity / avoiding scrutiny",          "Not facing press, withholding data, evading accountability",  "harm", 6,  4, 10),
    ("promise-break",        "Broken major promise",                 "A campaign promise abandoned or delivered only as rhetoric",  "harm", 12, 8, 18),
    ("norm-erosion",         "Democratic norm erosion",              "Voice votes, skipping debate/committee, ignoring house rules","harm", 15, 10, 22),
    ("corruption-alleged",   "Corruption alleged, uninvestigated",   "Credible allegation kept away from independent probe",        "harm", 22, 12, 32),
    ("othering-speech",      "Communal / othering speech",           "Speech that divides citizens on identity lines",              "harm", 25, 15, 35),
    ("corruption-proven",    "Corruption proven (individual)",       "Court or audited proof of personal/party graft",              "harm", 35, 25, 50),
    ("corrupt-institutional","Institutional-scale scam (proven)",    "Systemic loot established by court/CAG/inquiry",              "harm", 50, 40, 65),
    ("power-misuse",         "State power misused vs opponents",     "Agencies/ordinances weaponised for politics",                 "harm", 55, 40, 70),
    ("institution-capture",  "Capture of an independent institution","Independence of ECI/CBI/courts/media structurally compromised","harm",60, 45, 75),
    ("life-single",          "Civilian life lost, small scale, policy-linked", "Deaths directly traceable to a decision/neglect, few in number","harm",62,50,75),
    ("life-hundreds",        "Deaths in the hundreds (policy-linked)","Mass casualties linked to a decision or dereliction",        "harm", 75, 60, 88),
    ("anti-national",        "Act against national integrity/security","Proven act materially harming the nation's security/unity", "harm", 88, 70, 100),
    ("life-thousands",       "Mass life loss (thousands+) under watch","Catastrophic, policy-linked loss of life",                  "harm", 92, 80, 100),
    ("constit-siege",        "Assault on the Constitution itself",   "Suspension/hollowing of constitutional order (Emergency-grade)","harm",100,90,100),
    ("admin-minor",          "Competent administration, small win",  "Routine duty done visibly well",                              "virtue", 5,  2, 8),
    ("service-reach",        "Delivery at scale (10M+ households)",  "Welfare/infrastructure reaching tens of millions on record",  "virtue", 30, 18, 45),
    ("unity-act",            "Uniting act in national crisis",       "Crossing party lines for the nation when it mattered",        "virtue", 35, 20, 50),
    ("crisis-lead",          "Steady leadership through crisis",     "Visible, calm, effective helmsmanship",                       "virtue", 40, 25, 60),
    ("infra-strategic",      "Strategic infrastructure delivered",   "Long-horizon national asset built to acceptable standard",    "virtue", 45, 30, 60),
    ("reform-structural",    "Structural reform, measured outcome",  "Reform whose effects are independently measurable",           "virtue", 55, 40, 70),
    ("life-saved-scale",     "Policy saving lives at lakh scale",    "Health/safety interventions with audited mortality gains",    "virtue", 80, 60, 95),
    ("institution-build",    "Institution with decades-long payoff", "Creating capacity that outlives the builder (IITs/ISRO-grade)","virtue",85, 70, 100),
]

_FUND_SCHEMA = """
CREATE TABLE IF NOT EXISTS fundamentals(
  slug TEXT PRIMARY KEY, name TEXT, definition TEXT, polarity TEXT,
  position REAL, range_lo REAL, range_hi REAL,
  status TEXT DEFAULT 'CONSENSUS', created_by INTEGER, created REAL);
CREATE TABLE IF NOT EXISTS fund_votes(
  id INTEGER PRIMARY KEY, slug TEXT, user_id INTEGER, position REAL,
  between_a TEXT, between_b TEXT, "when" TEXT, created REAL,
  UNIQUE(slug, user_id));
CREATE TABLE IF NOT EXISTS param_funds(
  case_id TEXT, param TEXT, slug TEXT, strength REAL,
  UNIQUE(case_id, param, slug));
"""

# illustrative compositions for seeded params (case_id, param, slug, strength)
PARAM_FUND_SEEDS = [
    ("C05", "rule of law suspension", "constit-siege", 1.0),
    ("C05", "rule of law suspension", "institution-capture", 0.8),
    ("B19", "execution shock", "life-hundreds", 0.6),
    ("B19", "execution shock", "corruption-alleged", 0.5),
    ("M10", "communication opacity", "opacity", 1.0),
]

def _migrate(con):
    """Idempotent additive migrations: 'when' (event date) columns everywhere."""
    for sql in ('ALTER TABLE votes ADD COLUMN "when" TEXT DEFAULT ""',
                'ALTER TABLE challenges ADD COLUMN "when" TEXT DEFAULT ""',
                'ALTER TABLE case_params ADD COLUMN creator INTEGER',
                'ALTER TABLE case_params ADD COLUMN created REAL',
                'ALTER TABLE fundamentals ADD COLUMN parent TEXT DEFAULT ""'):
        try: con.execute(sql)
        except sqlite3.OperationalError: pass

def seed_fundamentals():
    con = sqlite3.connect(DB)
    con.executescript(_FUND_SCHEMA)
    _migrate(con)
    if con.execute("SELECT COUNT(*) FROM fundamentals").fetchone()[0] == 0:
        con.executemany(
            "INSERT INTO fundamentals(slug,name,definition,polarity,position,range_lo,range_hi,status,created) VALUES(?,?,?,?,?,?,?,'CONSENSUS',0)",
            [tuple(r) for r in FUND_SEEDS])
    con.executemany(
        "INSERT OR IGNORE INTO param_funds(case_id,param,slug,strength) VALUES(?,?,?,?)", PARAM_FUND_SEEDS)
    # sub-fundamentals (protons/electrons) and modifiers (multipliers)
    con.executemany(
        "INSERT OR IGNORE INTO fundamentals(slug,name,definition,polarity,position,range_lo,range_hi,status,created,parent)"
        " VALUES(?,?,?,?,?,?,?,'CONSENSUS',0,?)",
        [(sl, n, d, pol, pos, lo, hi, par) for (sl, n, d, pol, pos, lo, hi, par) in SUB_FUND_SEEDS])
    con.executemany(
        "INSERT OR IGNORE INTO fundamentals(slug,name,definition,polarity,position,range_lo,range_hi,status,created,parent)"
        " VALUES(?,?,?,'modifier',?,?,?,'CONSENSUS',0,'')",
        [(sl, n, d, m, max(0.2, m-0.2), min(3.0, m+0.2)) for (sl, n, d, m) in MODIFIER_SEEDS])
    con.commit(); con.close()
    seed_case_events()

def fund_rows(): return q("SELECT * FROM fundamentals ORDER BY position")

def fund_vote_stats(slug):
    r = q("SELECT AVG(position) m, COUNT(*) c FROM fund_votes WHERE slug=?", (slug,), one=True)
    return (r["m"], r["c"])

def fund_consensus_refresh(slug):
    m, c = fund_vote_stats(slug)
    if c and c >= 5:
        con = sqlite3.connect(DB)
        con.execute("UPDATE fundamentals SET position=?, status='CONSENSUS' WHERE slug=?",
                    (round(m, 1), slug))
        con.commit(); con.close()

def param_funds(case_id, param):
    return q("SELECT pf.slug, pf.strength, f.name, f.polarity, f.position, f.range_lo, f.range_hi "
             "FROM param_funds pf JOIN fundamentals f ON f.slug=pf.slug "
             "WHERE pf.case_id=? AND pf.param=?", (case_id, param))

def compose_points(funds):
    """Fundamental-scale raw points of a composition: sum(position*strength), signed."""
    total = 0.0
    for f in funds:
        sign = -1 if f["polarity"] == "harm" else 1
        strength = f["strength"] if "strength" in [k for k in f.keys()] else 1.0
        total += sign * (f["position"] or 0) * strength
    return round(total, 1)

def composed_to_five(raw):
    """Map fundamental-scale points into the legacy -5..+5 pool (crowd-added params)."""
    return round(max(-5, min(5, raw / 20.0)), 2)

# ---------------------------------------------------------------------------
# P3: SUB-FUNDAMENTALS (protons/electrons) + MODIFIERS (universal multipliers)
# + CASE THREADS (per-case dated, actor-POV timelines, crowd-built)
# ---------------------------------------------------------------------------

# modifiers: universal multipliers. position column stores the multiplier (0.2..3.0).
MODIFIER_SEEDS = [
    ("venue-parliament",   "Said/done in Parliament",        "The floor of the House amplifies — words there are matters of record", 1.5),
    ("venue-press-conf",   "Said in a formal press conference","On-record, with press present",                                    1.2),
    ("venue-rally",        "Said at a public rally",          "Public but rhetorical setting",                                     1.0),
    ("venue-social-media", "Said on social media",            "Lowest venue weight — noise floor",                                 0.6),
    ("role-party-chief",   "By the party chief / sitting PM-CM","Leader's words carry the institution's weight",                   1.25),
    ("role-member",        "By a regular member/MP/MLA",      "Standard responsibility",                                           1.0),
    ("role-supporter",     "By a rank-and-file supporter",    "Lowest responsibility tier",                                        0.7),
    ("cons-none",          "No traced consequence",           "Words ended where they started",                                    1.0),
    ("cons-sentiment",     "Hurt public sentiment",           "Anger/hurt documented in reporting",                                1.2),
    ("cons-violence",      "Violence or riots followed",      "Blood on the trail — multiply accordingly",                         1.8),
    ("cons-law",           "Official/legal action followed",  "Arrests, bans, cases, dismissals followed",                         1.4),
    ("cons-correction",    "Voluntary correction/apology",    "Owns the error — de-amplifies",                                     0.8),
]

# sub-fundamentals: the protons/electrons. (slug, name, definition, polarity, position, lo, hi, parent)
SUB_FUND_SEEDS = [
    ("no-press-access",      "No press access",            "Avoiding unscripted press interaction",              "harm", 5,  3, 8,  "opacity"),
    ("data-withholding",     "Withholding official data",  "Suppressing reports/reports released late",          "harm", 8,  5, 12, "opacity"),
    ("rti-evasion",          "RTI / disclosure evasion",   "Blocking statutory disclosure routes",               "harm", 9,  6, 13, "opacity"),
    ("oded-assets",          "Disproportionate assets",    "Wealth beyond declared income, evidenced",           "harm", 38, 30, 48,"corruption-proven"),
    ("bribery-documented",   "Documented bribery",         "Bribes evidenced on record (tapes, FIR, judgement)", "harm", 40, 32, 52,"corruption-proven"),
    ("falsehood-lie",        "A lie (demonstrably false)", "Not exaggeration — false, and no correction offered","harm", 6,  3, 10, "rhetoric-slip"),
    ("exaggeration",         "Exaggeration/spin",          "A claim beyond what evidence supports",              "harm", 3,  1, 6,  "rhetoric-slip"),
    ("propaganda-machinery", "Propaganda machinery",       "Industrial-scale narrative machinery",               "harm", 28, 18, 40,"institution-capture"),
    ("minority-targeting",   "Minority targeting",         "Singling out a community for blame",                 "harm", 32, 22, 42,"othering-speech"),
    ("crisis-silence",       "Silence during crisis",      "Visible absence when response was owed",             "harm", 20, 12, 30,"norm-erosion"),
    ("debate-avoidance",     "Debate/committee avoidance", "Skipping scrutiny of bills",                         "harm", 16, 10, 24,"norm-erosion"),
    ("transparent-books",    "Transparent books",          "Accounts/funding open to audit",                     "virtue",25, 15, 35,"reform-structural"),
    ("credit-sharing",       "Credit-sharing",             "Publicly acknowledges others' work incl. opponents", "virtue",18, 10, 28,"unity-act"),
]

_CASE_EVENT_SCHEMA = """
CREATE TABLE IF NOT EXISTS case_events(
  id INTEGER PRIMARY KEY, case_id TEXT, ymd TEXT, actor TEXT, pov TEXT,
  text TEXT, evidence_url TEXT, added_by INTEGER, created REAL);
"""

# Ayodhya/Ram Mandir example thread, matching the user's example.
CASE_EVENT_SEEDS = [
    ("1992-12-06", "party:bjp",        "crowd event", "Babri Masjid demolished at Ayodhya by kar sevaks amid a BJP-VHP mobilisation; Liberhan panel later finds 68 people culpable", "https://en.wikipedia.org/wiki/Demolition_of_the_Babri_Masjid"),
    ("2019-11-09", "institution:sci",   "ruled",       "Supreme Court 5-0: the 1949 idol placement and 1992 demolition were an 'egregious violation of the rule of law'; land to a trust for the temple, 5 acres allotted for a mosque", "https://www.sci.gov.in/supreme-court-judgements/"),
    ("2020-09-30", "institution:court", "ruled",       "Special CBI court acquits all 32 demolition accused citing lack of conclusive proof (appeal lives on)", "https://en.wikipedia.org/wiki/Demolition_of_the_Babri_Masjid#Trial"),
    ("2024-01-22", "person:narendra-modi", "did",      "Pran-pratishtha consecration of the Ram Mandir led by the PM in a state-level ceremony", "https://pib.gov.in/PressReleasePage.aspx?PRID=1999797"),
]

def seed_case_events():
    con = sqlite3.connect(DB)
    con.executescript(_CASE_EVENT_SCHEMA)
    # link thread to whichever case mentions Ayodhya/Babri
    row = con.execute("SELECT id FROM cases WHERE lower(title) LIKE '%ayodhya%' OR lower(title) LIKE '%babri%' LIMIT 1").fetchone()
    cid = row[0] if row else None
    if cid and con.execute("SELECT COUNT(*) FROM case_events").fetchone()[0] == 0:
        con.executemany(
            "INSERT INTO case_events(case_id,ymd,actor,pov,text,evidence_url,added_by,created) VALUES(?,?,?,?,?,?,0,0)",
            [(cid,) + s for s in CASE_EVENT_SEEDS])
    con.commit(); con.close()

def case_events(cid):
    return q("SELECT ce.*, u.username FROM case_events ce LEFT JOIN users u ON u.id=ce.added_by "
             "WHERE ce.case_id=? ORDER BY ce.ymd, ce.id", (cid,))

def fund_children(slug):
    return q("SELECT * FROM fundamentals WHERE parent=? ORDER BY position", (slug,))

def case_coverage(case_id):
    """Aspect-coverage meter: distinct fundamentals composed across this case's params,
    plus how many params are composed at all. More aspects = finer signal."""
    n_params = q("SELECT count(*) c FROM case_params WHERE case_id=?", (case_id,), one=True)["c"]
    composed = q("SELECT count(DISTINCT param) c FROM param_funds WHERE case_id=?", (case_id,), one=True)["c"]
    aspects = q("SELECT count(DISTINCT slug) c FROM param_funds WHERE case_id=?", (case_id,), one=True)["c"]
    if aspects <= 1: label, cls = "thin", "bad"
    elif aspects <= 4: label, cls = "moderate", "warn"
    else: label, cls = "rich", "ok"
    return aspects, composed, n_params, label, cls

def compose_with_modifiers(funds, modifiers):
    """raw = signed sum(fund positions * strengths) * product(modifier multipliers)."""
    base = compose_points(funds)
    mult = 1.0
    for m in modifiers:
        mult *= (m["position"] or 1.0)
    return round(base * mult, 1)

# ---------------------------------------------------------------------------
# P4: MASTER 0-300 LEDGER (anchored slider scale)
# One continuous scale: 0-100 harm (more bad -> closer 0), 100-200 neutral,
# 200-300 virtue (less good -> more good). Stored authoritative value remains
# the polarity-domain 0-100 position (compose math unchanged); master is the
# presentation + input layer. Consensus locks to the MEDIAN of placements.
# ---------------------------------------------------------------------------

def master_of(f):
    """Return the authoritative value on the master 0-300 ledger."""
    if f["polarity"] == "modifier":
        return 150.0
    return 100.0 - f["position"] if f["polarity"] == "harm" else 200.0 + f["position"]

def pos_from_master(f, m):
    """Inverse of master_of: master slider value -> polarity-domain position."""
    return round(100.0 - m, 1) if f["polarity"] == "harm" else round(m - 200.0, 1)

def master_bounds(f):
    """Allowed slider window on the master scale for a fundamental."""
    if f["polarity"] == "modifier": return (0.2, 3.0)
    if f["polarity"] == "harm":   return (100.0 - f["range_hi"], 100.0 - f["range_lo"])
    return (200.0 + f["range_lo"], 200.0 + f["range_hi"])

def band_word(m):
    if m < 50:  return "very bad"
    if m < 100: return "bad"
    if m < 140: return "neutral-bad"
    if m <= 160: return "neutral"
    if m <= 200: return "neutral-good"
    if m <= 250: return "good"
    return "very good"

# Reference anchors everyone understands (presentation layer, master coords)
MASTER_ANCHORS = [
    ("mass killing / communal massacre", 3),    ("an act against the nation", 14),
    ("murder", 5),                              ("institutional scam", 50),
    ("casteist/communal hate speech", 74),      ("traffic violation", 93),
    ("littering", 97),                          ("jury duty, done well", 215),
    ("temple/school donated by a stranger", 228), ("founding an institution (IIT-class)", 285),
]

def fund_consensus_refresh(slug):
    """Median-lock consensus: median of placements when n>=5, plus it must sit
    within the fundamental's declared band; the placement cloud stays visible."""
    vals = [r["p"] for r in q('SELECT position p FROM fund_votes WHERE slug=?', (slug,))]
    if len(vals) < 5: return
    f = q("SELECT * FROM fundamentals WHERE slug=?", (slug,), one=True)
    med = statistics.median(vals)
    if f["polarity"] != "modifier":
        med = max(min(med, f["range_hi"]), f["range_lo"])
    con = sqlite3.connect(DB)
    con.execute("UPDATE fundamentals SET position=?, status='CONSENSUS' WHERE slug=?",
                (round(med, 1), slug))
    con.commit(); con.close()

def fund_placement_cloud(slug):
    """All placement values (for the distribution dots)."""
    return [r["p"] for r in q('SELECT position p FROM fund_votes WHERE slug=?', (slug,))]
