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
        con.close(); return
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
