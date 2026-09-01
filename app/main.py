"""RajScore v2 — crowd-run accountability platform (P1 build).
FastAPI + SQLite, server-rendered, JSON API exposed for the future Next.js front end.
Run:  PYTHONPATH=/home/user/.pydeps python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
import time, datetime, re
from fastapi import FastAPI, Request, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import render as R
from . import db

db.init_and_seed()
app = FastAPI(title="RajScore", version="0.1.0")
import os
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# ---------- helpers --------------------------------------------------------
def ctx(request: Request):
    tok = request.cookies.get("rs_session")
    user = db.user_by_token(tok) if tok else None
    profile = request.cookies.get("rs_trust", "balanced")
    if profile not in db.PROFILE_RULES: profile = "balanced"
    return user, profile

def today(): return datetime.date.today().strftime("%d %b %Y")

def entity_name(eid):
    e = db.q("SELECT name FROM entities WHERE id=?", (eid,), one=True)
    return e["name"] if e else eid

def case_median(case_id, weight, profile):
    vals = []
    rows = db.q("SELECT param FROM case_params WHERE case_id=? GROUP BY param", (case_id,))
    for r in rows:
        m, n = db.param_median(case_id, r["param"], profile)
        if m is not None: vals.append(m)
    if not vals: return None
    return round(sum(vals) / len(vals) * weight, 2)

def entity_totals(eid, profile):
    out = {}
    rows = db.q("SELECT DISTINCT case_id, role FROM case_params WHERE entity_id=?", (eid,))
    for r in rows:
        c = db.q("SELECT weight FROM cases WHERE id=?", (r["case_id"],), one=True)
        m = case_median(r["case_id"], c["weight"], profile)
        if m is None: continue
        out.setdefault(r["role"], 0.0)
        out[r["role"]] += m
    # also person rows live under role 'person'
    return out

def sparkline_svg(points, w=260, h=54):
    if not points: return ""
    xs = list(range(len(points)))
    mn, mx = min(points), max(points)
    rng = (mx - mn) or 1
    step = w / max(len(points) - 1, 1)
    coords = " ".join(f"{round(i*step,1)},{round(h - (v - mn)/rng * (h-8) - 4,1)}" for i, v in zip(xs, points))
    zy = h - (0 - mn)/rng * (h-8) - 4
    return (f'<svg class="spark" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<line x1="0" x2="{w}" y1="{zy}" y2="{zy}" stroke="#94a3b8" stroke-dasharray="3 3" stroke-width="1"/>'
            f'<polyline fill="none" stroke="#1e3a8a" stroke-width="2" points="{coords}"/></svg>')

# ---------- pages ----------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    user, profile = ctx(request)
    ents = db.q("SELECT * FROM entities")
    cards = []
    for e in ents:
        tot = entity_totals(e["id"], profile)
        total = sum(tot.values())
        role_txt = " · ".join(f"{k} {v:+.1f}" for k, v in tot.items()) or "no scored items yet"
        ncases = db.q("SELECT count(DISTINCT case_id) c FROM case_params WHERE entity_id=?", (e["id"],), one=True)["c"]
        cards.append(f"""<div class="card">
          <div class="etype">{R.esc(e['type'])}</div>
          <h2 style="margin:.15rem 0"><a href="/entity/{e['id']}">{R.esc(e['name'])}</a></h2>
          <div style="font-size:1.6rem;font-weight:800">{R.chip(total)}</div>
          <div class="muted">{R.esc(role_txt)}</div>
          <div class="muted">{ncases} cases · <a href="/report/{e['id']}">instant report card</a></div>
        </div>""")
    nc = db.q("SELECT count(*) c FROM cases", one=True)["c"]
    nv = db.q("SELECT count(*) c FROM votes", one=True)["c"]
    nu = db.q("SELECT count(*) c FROM users", one=True)["c"]
    nch = db.q("SELECT count(*) c FROM challenges WHERE status='OPEN'", one=True)["c"]
    top_pos = db.q("""SELECT c.id, c.title, c.weight FROM cases c ORDER BY c.weight DESC, c.id LIMIT 200""")
    ranked = [(case_median(c["id"], c["weight"], profile), c) for c in top_pos]
    scored = [x for x in ranked if x[0] is not None]
    best = sorted([x for x in scored if x[0] > 0], key=lambda x: -x[0])[:5]
    worst = sorted([x for x in scored if x[0] < 0], key=lambda x: x[0])[:5]
    def row(items):
        return "".join(f'<tr><td><a href="/case/{c["id"]}">{R.esc(c["title"])}</a></td><td class="num">{R.chip(m)}</td></tr>'
                       for m, c in items)
    body = f"""
    <div class="hero"><h1>Score power. With receipts.</h1>
      <p>Anyone can mint an ID for any actor, add an incident, propose parameters and vote — every number carries
      evidence links, and nothing is permanent: consensus is earned and can always be re-challenged with new evidence.</p>
      <p class="muted">Seeded with the Ideal-Party Audit: <b>{nc} cases</b>, 1947 → Sep 2026 ·
      <b>{nu}</b> registered voters · <b>{nv}</b> votes cast · <b>{nch}</b> open challenges</p>
      <p class="muted">📊 Totals currently reflect your <i>balanced</i> trust dial. Setting the dial to
      <a href="/rules/set?profile=open"><b>open</b></a> reproduces the published
      <a href="https://github.com/Karan771108h/expermental-work/blob/main/REPORT.md">report totals</a> exactly
      (balanced hides seed rows backed only by wiki/tweet-grade evidence — that is the dial doing its job).</p>
      <p><a class="btn" href="/cases">Browse cases</a> <a class="btn ghost" href="/fundamentals">⚖ The fundamentals scale</a>
      <a class="btn ghost" href="/rules">Set my trust dial</a> <a class="btn ghost" href="/auth">Join to vote</a></p>
      <p class="muted">New here? The platform runs on three moves — <b>read → vote → challenge</b> — and one bedrock:
      the <a href="/fundamentals">0–100 fundamentals scale</a>, where atomic building blocks (opacity ≈ 6,
      proven institutional scam ≈ 50, constitutional siege ≈ 100) are layered into every parameter, so unlike acts
      can never be scored equal. <a href="/tour">📖 Tutorial in 6 steps</a></p>
    </div>
    <h2>Composite scoreboards (under <i>your</i> trust dial)</h2>
    <div class="grid">{''.join(cards)}</div>
    <h2>Top positive cases</h2><table><tbody>{row(best)}</tbody></table>
    <h2>Top negative cases</h2><table><tbody>{row(worst)}</tbody></table>
    """
    return R.page("Score power, with receipts", body, user, profile, db.PROFILE_LABELS[profile])

@app.get("/entities", response_class=HTMLResponse)
def entities(request: Request):
    user, profile = ctx(request)
    rows = []
    for e in db.q("SELECT * FROM entities ORDER BY type, name"):
        ncases = db.q("SELECT count(DISTINCT case_id) c FROM case_params WHERE entity_id=?", (e["id"],), one=True)["c"]
        tot = sum(entity_totals(e["id"], profile).values())
        rows.append(f"""<tr><td class="etype">{R.esc(e['type'])}</td>
          <td><a href="/entity/{e['id']}"><b>{R.esc(e['name'])}</b></a><br><span class="muted">{R.esc(e['summary'])}</span></td>
          <td class="muted">{R.esc(e['aliases'])}</td><td class="num">{ncases}</td><td class="num">{R.chip(round(tot,1))}</td>
          <td><a href="/report/{e['id']}">report</a></td></tr>""")
    body = f"""<h1>Entities</h1><p class="muted">Mint a new entity (any noun — a party, a CM, a scheme, a verdict)
    by adding a case against it: <a href="/cases">case intake</a>. Aliases merge to one ID.</p>
    <table><thead><tr><th>Type</th><th>Entity</th><th>Aliases</th><th class="num">Cases</th><th class="num">Composite</th><th></th></tr></thead>
    <tbody>{''.join(rows)}</tbody></table>"""
    return R.page("Entities", body, user, profile, db.PROFILE_LABELS[profile])

@app.get("/entity/{eid}", response_class=HTMLResponse)
def entity(request: Request, eid: str):
    user, profile = ctx(request)
    e = db.q("SELECT * FROM entities WHERE id=?", (eid,), one=True)
    if not e: return HTMLResponse(R.page("Not found", "<div class='alert'>Unknown entity.</div>", user, profile, db.PROFILE_LABELS[profile]), 404)
    tots = entity_totals(eid, profile)
    # trend
    rows = db.q("SELECT case_id FROM case_params WHERE entity_id=? GROUP BY case_id", (eid,))
    pts = {}
    for r in rows:
        c = db.q("SELECT period, weight FROM cases WHERE id=?", (r["case_id"],), one=True)
        m = case_median(r["case_id"], c["weight"], profile)
        if m is None: continue
        y = db.first_year(c["period"])
        pts.setdefault(y, []).append(m)
    years = sorted(y for y in pts if y)
    series = [round(sum(pts[y])/len(pts[y]), 1) for y in years]
    spark = sparkline_svg(series)
    trend_labels = ", ".join(f"{y}: {v:+.1f}" for y, v in list(zip(years, series))[-12:])
    cases_by_role = {}
    for r in db.q("SELECT case_id, role FROM case_params WHERE entity_id=? GROUP BY case_id, role", (eid,)):
        cases_by_role.setdefault(r["role"], []).append(r["case_id"])
    blocks = []
    for role, ids in cases_by_role.items():
        lines = []
        for cid in ids:
            c = db.q("SELECT * FROM cases WHERE id=?", (cid,), one=True)
            m = case_median(cid, c["weight"], profile)
            st = db.case_status(cid)
            lines.append(f"""<tr><td><a href="/case/{cid}">{R.esc(c['title'])}</a><br>
              <span class="muted">{R.esc(c['period'])} · {R.esc(c['domain'])} · w{c['weight']}</span></td>
              <td class="num">{R.chip(m)}</td><td>{R.badge(st)}</td></tr>""")
        lines.sort(key=lambda s: s)  # stable; order keep csv order
        blocks.append(f"<h2>{R.esc(role)} ledger</h2><table><tbody>{''.join(lines)}</tbody></table>")
    chall = db.q("SELECT c.*, u.username FROM challenges c LEFT JOIN users u ON u.id=c.user_id WHERE object_id LIKE ? AND c.status='OPEN'",
                 (eid + "%",))
    ch_html = "".join(f'<div class="alert">⚔ <b>{R.esc(x["kind"])}:{R.esc(x["object_id"])}</b> — {R.esc(x["note"])} '
                      f'(<a href="{R.esc(x["evidence_url"])}" target="_blank">evidence</a>) by {R.esc(x["username"] or "?")}</div>' for x in chall) or ""
    body = f"""<div class="card"><div class="etype">{R.esc(e['type'])}</div>
      <h1>{R.esc(e['name'])}</h1><p class="muted">{R.esc(e['summary'])} · aliases: {R.esc(e['aliases'])}</p>
      <p><b>Composite: {R.chip(round(sum(tots.values()),1))}</b> &nbsp;
      {' · '.join(f"{k} {v:+.1f}" for k, v in tots.items())}</p>
      <p>{spark}</p><p class="muted">yearly mean (latest 12 pts): {R.esc(trend_labels)}</p>
      <p><a class="btn ghost" href="/report/{eid}">Generate report card</a></p></div>
      {ch_html}{''.join(blocks)}"""
    return R.page(e["name"], body, user, profile, db.PROFILE_LABELS[profile])

@app.get("/cases", response_class=HTMLResponse)
def cases(request: Request, domain: str = "", status: str = ""):
    user, profile = ctx(request)
    doms = sorted({r["domain"] for r in db.q("SELECT DISTINCT domain FROM cases")})
    sel = "".join(f'<option {"selected" if d==domain else ""}>{d}</option>' for d in doms)
    rows = []
    for c in db.q("SELECT * FROM cases ORDER BY CAST(SUBSTR(period,1,4) AS INT), id"):
        if domain and c["domain"] != domain: continue
        st = db.case_status(c["id"])
        if status == "open" and st not in ("COMMUNITY REVIEW", "CONTESTED", "CHALLENGED"): continue
        if status == "consensus" and st != "CONSENSUS": continue
        m = case_median(c["id"], c["weight"], profile)
        actors = db.q("SELECT DISTINCT entity_id FROM case_params WHERE case_id=?", (c["id"],))
        actor_tags = " ".join(f'<a class="tag" href="/entity/{a["entity_id"]}">{entity_name(a["entity_id"])}</a>' for a in actors)
        rows.append(f"""<tr><td><a href="/case/{c['id']}"><b>{R.esc(c['title'])}</b></a><br>
          <span class="muted">{R.esc(c['period'])}</span></td>
          <td><span class="tag">{R.esc(c['domain'])}</span>{actor_tags}</td>
          <td class="num">w{c['weight']}</td><td class="num">{R.chip(m)}</td><td>{R.badge(st)}</td></tr>""")
    body = f"""<h1>Case intake & ledger</h1>
    <form class="inline filters" method="get"><label>Domain <select name="domain"><option value="">all</option>{sel}</select></label>
    <label>Status <select name="status"><option value="">all</option>
      <option value="open" {'selected' if status=='open' else ''}>needs review / challenged</option>
      <option value="consensus" {'selected' if status=='consensus' else ''}>consensus reached</option></select></label>
    <button class="btn">Filter</button></form>
    <p class="muted">Consensus requires ≥5 votes with ≥2/3 agreeing with the sign of the evidence-backed median.
    Add new incidents: pick the case above closest in spirit — or send a PR adding rows to <span class="kbd">data/scores.csv</span>;
    intake UI for brand-new cases lands in P3.</p>
    <table><thead><tr><th>Case</th><th>Tags / actors</th><th class="num">Weight</th><th class="num">Score (median·w)</th><th>Status</th></tr></thead>
    <tbody>{''.join(rows)}</tbody></table>"""
    return R.page("Cases", body, user, profile, db.PROFILE_LABELS[profile])

@app.get("/case/{cid}", response_class=HTMLResponse)
def case_detail(request: Request, cid: str):
    user, profile = ctx(request)
    c = db.q("SELECT * FROM cases WHERE id=?", (cid,), one=True)
    if not c: return HTMLResponse(R.page("Not found", "<div class='alert'>Unknown case.</div>", user, profile, db.PROFILE_LABELS[profile]), 404)
    params = db.q("SELECT * FROM case_params WHERE case_id=? ORDER BY rowid", (cid,))
    rows_html = []
    for p in params:
        m, n = db.param_median(cid, p["param"], profile)
        ent = entity_name(p["entity_id"])
        votes = db.vote_count(cid, p["param"])
        pfs = db.param_funds(cid, p["param"])
        raw = db.compose_points(pfs) if pfs else None
        fund_chips = "" if not pfs else ("<div class='fundchips'>⚖ composed of " +
            " ".join(f'<a class="fund {"v" if f["polarity"]=="virtue" else "h"}">{R.esc(f["name"])}×{f["strength"]:g}</a>' for f in pfs)
            + f' → <b>{raw:+.1f} pts</b> fundamental-scale</div>')
        rows_html.append(f"""<tr>
          <td><b>{R.esc(p['param'])}</b><br><span class="muted">{R.esc(ent)} · {R.esc(p['role'])}</span>{fund_chips}</td>
          <td>{R.chip(p['seed_score'])} <span class="muted">seed</span></td>
          <td>{R.chip(m)} <span class="muted">{n} evidence-passing source(s) · {votes} crowd vote(s)</span></td>
          <td>{R.esc(p['justification'])}<br>{R.grade_pill(db.best_grade(p['sources']))} {R.source_links(p['sources'])}</td></tr>""")
    st = db.case_status(cid)
    only = ""
    if st == "CHALLENGED":
        only = """<div class="alert">⚔ This case is under an OPEN CHALLENGE. Its scores keep counting but are
        flagged disputed until the jury loop (P3) resolves. Bring evidence, not volume.</div>"""
    login_note = "" if user else '<div class="flash">You are browsing anonymously — <a href="/auth">join/login</a> to vote or challenge.</div>'
    body = f"""<div class="card">
      <h1>{R.esc(c['title'])}</h1>
      <p class="muted">{R.esc(c['period'])} · domain <span class="tag">{R.esc(c['domain'])}</span> · weight
      <b>w{c['weight']}</b> · status {R.badge(st)}</p></div>
      {only}{login_note}
      <h2>Parameters & evidence (each line independently challengeable)</h2>
      <table><thead><tr><th>Parameter / actor</th><th>Seed score</th><th>Live median</th><th>Basis · grade · sources</th></tr></thead>
      <tbody>{''.join(rows_html)}</tbody></table>
      <h2>Cast your vote <span class="muted">(one per parameter; evidence link + event date or it doesn't count)</span></h2>
      <form class="card" id="voteform" onsubmit="event.preventDefault();">
        <label>Case</label><input name="case_id" value="{R.esc(cid)}" readonly>
        <label>Parameter (must match one above)</label>
        <input id="p" name="param" list="params" required>
        <datalist id="params">{''.join(f'<option value="{R.esc(p["param"])}">' for p in params)}</datalist>
        <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr))">
          <div><label>Your score (−5 … +5)</label><input name="score" type="number" min="-5" max="5" step="0.5" required></div>
          <div><label>📅 Event date of the conduct you're scoring</label><input name="when" type="text" placeholder="YYYY-MM-DD" pattern="\\d{{4}}(-\\d{{2}}){{0,2}}" required></div>
        </div>
        <label>Evidence URL (court/CAG/RBI/ECI links grade highest)</label><input name="evidence_url" type="url" required placeholder="https://…">
        <br><br><button class="btn">Submit vote</button><span id="msg" class="muted"></span>
      </form>
      <h2>Missing a parameter? Compose one from fundamentals</h2>
      <form class="card" id="paramform" onsubmit="event.preventDefault();">
        <label>Parameter name (short, neutral)</label><input name="param" required maxlength="120" placeholder="e.g. press freedom enforcement, not 'raid')" >
        <input type="hidden" name="case_id" value="{R.esc(cid)}">
        <label>Composition — fundamental slugs with strength (see <a href="/fundamentals" target="_blank">scale</a>)</label>
        <input name="funds" required placeholder="e.g. power-misuse:0.8, corruption-alleged:0.5">
        <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr))">
          <div><label>📅 Event date</label><input name="when" type="text" placeholder="YYYY-MM-DD" required></div>
          <div><label>Evidence URL</label><input name="evidence_url" type="url" required placeholder="https://…"></div>
        </div>
        <br><button class="btn">Compute & add parameter</button><span id="pmsg" class="muted"></span>
      </form>
      <h2>Challenge this case <span class="muted">(even a 50-year-old verdict — re-open it with evidence)</span></h2>
      <form class="card" onsubmit="event.preventDefault();">
        <label>What is wrong? (datum, grading, weight, framing)</label><input name="note" required>
        <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr))">
          <div><label>Your counter-evidence URL (required)</label><input name="evidence_url" type="url" required placeholder="https://…"></div>
          <div><label>📅 Date of the item you're challenging</label><input name="when" type="text" placeholder="YYYY-MM-DD" required></div>
        </div>
        <br><br><button class="btn warn">Open challenge</button><span id="cmsg" class="muted"></span>
      </form>"""
    js = R.JS_UTILS + """
      const f0=document.getElementById('voteform'), f1=document.getElementById('paramform'), f2=document.querySelectorAll('form.card')[2];
      f0.onsubmit=async()=>{const r=await postJSON('/api/vote',formVals(f0));
        f0.querySelector('#msg').textContent=r.ok?' ✔ vote sealed — thank you':(' ✖ '+(r.body.detail||'error')); if(r.ok)setTimeout(()=>location.reload(),900);};
      f1.onsubmit=async()=>{const r=await postJSON('/api/param/add',formVals(f1));
        f1.querySelector('#pmsg').textContent=r.ok?(' ✔ added — fundamental-scale '+r.body.raw_points+' pts, normalised '+r.body.normalised):(' ✖ '+(r.body.detail||'error')); if(r.ok)setTimeout(()=>location.reload(),1100);};
      f2.onsubmit=async()=>{const d=formVals(f2); d.kind='case'; d.object_id=d.case_id||document.querySelector('[name=case_id]').value;
        const r=await postJSON('/api/challenge',d);
        f2.querySelector('#cmsg').textContent=r.ok?' ⚔ challenge is open — flagged site-wide':(' ✖ '+(r.body.detail||'error')); if(r.ok)setTimeout(()=>location.reload(),900);};
    """
    return R.page(c["title"], body, user, profile, db.PROFILE_LABELS[profile], extra_js=js)

@app.get("/timeline", response_class=HTMLResponse)
def timeline(request: Request, frm: str = "1947", to: str = "2026"):
    user, profile = ctx(request)
    rows = []
    for t in sorted(db.q("SELECT * FROM timeline"), key=lambda t: (int(re.sub(r'[^0-9]','',t['year'][:6])[:4] or 0), t['id'])):
        try:
            y = int(t["year"].split("-")[0])
        except Exception:
            y = 0
        if not (int(frm) <= y <= int(to)): continue
        rows.append(f"""<tr><td><b>{R.esc(t['year'])}</b> <span class="muted">{R.esc(t['date'])}</span></td>
          <td>{R.esc(t['event'])}<br><span class="muted">{R.esc(t['actor'])} · {R.esc(t['category'])}</span></td>
          <td>{R.source_links(t['proof'])}</td></tr>""")
    acts = []
    for v in db.q("""SELECT v."when" w, v.score, v.case_id, v.param, u.username FROM votes v
                     LEFT JOIN users u ON u.id=v.user_id WHERE v."when"!='' ORDER BY v.created DESC"""):
        acts.append((v["w"], f'<b>vote</b> by {R.esc(v["username"] or "?")}: <a href="/case/{R.esc(v["case_id"])}">{R.esc(v["case_id"])}</a>'
                     f' · {R.esc(v["param"])} {R.chip(v["score"])}', ""))
    for ch in db.q("""SELECT c."when" w, c.kind, c.object_id, c.note, u.username FROM challenges c
                     LEFT JOIN users u ON u.id=c.user_id WHERE c."when"!='' ORDER BY c.created DESC"""):
        acts.append((ch["w"], f'<b>challenge</b> by {R.esc(ch["username"] or "?")} on '
                     f'<a href="/case/{R.esc(ch["object_id"])}">{R.esc(ch["object_id"])}</a>: {R.esc(ch["note"])}', ""))
    for fd in db.q("""SELECT slug, name, position, created FROM fundamentals WHERE status='PROPOSED'"""):
        d = time.strftime("%Y-%m-%d", time.localtime(fd["created"])) if fd["created"] else ""
        acts.append((d, f'<b>new fundamental proposed</b>: <a href="/fundamentals#{R.esc(fd["slug"])}">{R.esc(fd["name"])}</a>'
                     f' (proposed position {fd["position"]:g})', ""))
    acts.sort(key=lambda a: a[0], reverse=True)
    act_html = "".join(f'<tr><td class="muted">{R.esc(w)}</td><td>{txt}</td></tr>' for w, txt, _ in acts)
    body = f"""<h1>Master timeline of Indian governance (proof-linked)</h1>
    <form class="inline filters" method="get"><label>From <input name="frm" value="{R.esc(frm)}" style="width:90px"></label>
    <label>To <input name="to" value="{R.esc(to)}" style="width:90px"></label><button class="btn">Go</button></form>
    <table><thead><tr><th>When</th><th>What</th><th>Proof</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
    <h2>Community activity layer <span class="muted">(every vote/challenge/fundamental carries its event date)</span></h2>
    {'<table><tbody>'+act_html+'</tbody></table>' if acts else '<p class="muted">No activity yet — cast the first dated vote on any case.</p>'}"""
    return R.page("Timeline", body, user, profile, db.PROFILE_LABELS[profile])

@app.get("/tour", response_class=HTMLResponse)
def tour(request: Request):
    user, profile = ctx(request)
    steps = "".join(f'<div class="card"><h2>{i+1} · {R.esc(t)}</h2><p>{b}</p></div>'
                    for i, (t, b) in enumerate(R.TOUR_STEPS))
    body = f"""<h1>📖 The 6-step RajScore walkthrough</h1>
    <p class="muted">This is the same tour that pops up for first-time visitors. Two minutes, and you can operate the whole platform.</p>
    {steps}
    <p><a class="btn" href="/?tour=1">Back to home</a></p>"""
    return R.page("Tutorial", body, user, profile, db.PROFILE_LABELS[profile])

@app.get("/claims", response_class=HTMLResponse)
def claims(request: Request):
    user, profile = ctx(request)
    rows = []
    for c in db.q("SELECT * FROM claims ORDER BY id"):
        rows.append(f"""<tr><td><b>"{R.esc(c['text'])}"</b></td>
          <td>{R.chip(0) if False else ''}<span class="badge {'ok' if c['verdict']=='TRUE' else ('bad' if c['verdict']=='FALSE' else 'warn')}">{R.esc(c['verdict'])}</span></td>
          <td><a href="/entity/{R.esc(c['actor_id'])}">{R.esc(entity_name(c['actor_id']))}</a></td>
          <td>{R.esc(c['detail'])}<br>{R.source_links(c['evidence'])}</td></tr>""")
    body = f"""<h1>Claim-checks (fact-check vernacular)</h1>
    <p class="muted">Verdict vocabulary: TRUE / MOSTLY TRUE / HALF TRUE / MOSTLY FALSE / FALSE / UNVERIFIABLE.
    Add a claim by challenging an entity with the claim as the note — P4 adds first-class claim intake.</p>
    <table><thead><tr><th>Claim</th><th>Verdict</th><th>Against</th><th>Why · evidence</th></tr></thead>
    <tbody>{''.join(rows)}</tbody></table>"""
    return R.page("Fact-check", body, user, profile, db.PROFILE_LABELS[profile])

@app.get("/rules", response_class=HTMLResponse)
def rules(request: Request):
    user, profile = ctx(request)
    prof_opts = "".join(f'<option value="{k}" {"selected" if k==profile else ""}>{v}</option>'
                        for k, v in db.PROFILE_LABELS.items())
    lean_opts = "".join(f'<option>{x}</option>' for x in ["none", "BJP-lean", "Congress-lean", "Left-lean", "Regional-lean", "AAP-lean"])
    body = f"""<h1>Rules & Trust — the operating manual</h1>
    <div class="card"><h2>1 · Your trust dial (personalises every number you see)</h2>
    <form method="get" action="/rules/set"><label>Evidence profile</label>
    <select name="profile">{prof_opts}</select><br><br><button class="btn">Apply dial</button></form>
    <p class="muted">Official = courts · commissions · CAG/ECI/RBI · WHO/World Bank (govt press releases flagged self-interested).
    Evidence is graded per link (A/B/C badges on every case line). Your dial decides which grades count into
    <i>your</i> medians. Nothing is hidden — the recipe prints with the number.</p></div>
    <div class="card"><h2>2 · Declared leaning (kept honest by sunlight)</h2>
    <p>At signup you wear a public leaning badge. Aggregation always shows the breakdown; when BJP-lean and
    Congress-lean voters diverge, a case shows a <b>polarisation band</b>, not a fake single truth.</p></div>
    <div class="card"><h2>3 · The status machine</h2>
    <p><span class="kbd">SEEDED</span> (from the research corpus) → <span class="kbd">COMMUNITY REVIEW</span> →
    <span class="kbd">CONSENSUS</span> (≥5 votes, ≥2/3 sign agreement) — and everything, at any age, can be
    <span class="kbd">CHALLENGED</span> with a counter-evidence link. Resolution by random leaning-balanced juries ships in P3.</p></div>
    <div class="card"><h2>4 · Scoring grammar</h2>
    <p>Per-case parameters, each −5..+5; case score = median(parameter medians) × case weight (1 minor / 2 major / 3 landmark).
    No fixed parameter menu — the case says what it is about; you add the missing parameter.</p></div>
    <div class="card"><h2>5 · The built-in rubric preset this computes with</h2>
    <p><b>Ideal-Party Charter</b>: internal democracy · fact-based policy · funding transparency · continuous civic
    engagement · support-in-crises / oppose-on-institution-damage ("state permanent, government temporary, party secondary").
    Forkable preset system ships in P2.</p></div>
    <div class="card"><h2>6 · Your leaning is {esc_attr(user) if user else 'not set'}</h2></div>"""
    return R.page("Rules & Trust", body, user, profile, db.PROFILE_LABELS[profile])

def esc_attr(x): return R.esc(x["leaning"]) if x else ""

@app.get("/rules/set")
def rules_set(profile: str = "balanced"):
    if profile not in db.PROFILE_RULES: profile = "balanced"
    resp = RedirectResponse("/cases", status_code=303)
    resp.set_cookie("rs_trust", profile, max_age=60*60*24*365)
    return resp

@app.get("/auth", response_class=HTMLResponse)
def auth(request: Request):
    user, profile = ctx(request)
    if user: return RedirectResponse("/")
    body = """<h1>Join / login</h1>
    <div class="grid">
    <div class="card"><h2>Join</h2>
      <form onsubmit="event.preventDefault();" id="su">
      <label>Username (public)</label><input name="username" required minlength="2">
      <label>Password</label><input name="password" type="password" required minlength="6">
      <label>Declared leaning (public badge — keeps the maths honest)</label>
      <select name="leaning"><option>none</option><option>BJP-lean</option><option>Congress-lean</option>
      <option>Left-lean</option><option>Regional-lean</option><option>AAP-lean</option></select>
      <br><br><button class="btn">Create account</button><span id="msg1" class="muted"></span></form></div>
    <div class="card"><h2>Login</h2>
      <form onsubmit="event.preventDefault();" id="li">
      <label>Username</label><input name="username" required>
      <label>Password</label><input name="password" type="password" required>
      <br><br><button class="btn">Login</button><span id="msg2" class="muted"></span></form></div>
    </div>"""
    js = R.JS_UTILS + """
    document.getElementById('su').onsubmit=async(e)=>{const r=await postJSON('/api/auth/signup',formVals(e.target));
      document.getElementById('msg1').textContent = r.ok?' ✔ welcome — redirecting':(' ✖ '+(r.body.detail||'')); if(r.ok)setTimeout(()=>location.href='/',900);};
    document.getElementById('li').onsubmit=async(e)=>{const r=await postJSON('/api/auth/login',formVals(e.target));
      document.getElementById('msg2').textContent = r.ok?' ✔ redirecting':(' ✖ '+(r.body.detail||'')); if(r.ok)setTimeout(()=>location.href='/',900);};
    """
    return R.page("Join / login", body, None, profile, db.PROFILE_LABELS[profile], extra_js=js)

@app.get("/auth/logout")
def logout():
    resp = RedirectResponse("/")
    resp.delete_cookie("rs_session")
    return resp

@app.get("/report/{eid}", response_class=HTMLResponse)
def report_card(request: Request, eid: str, frm: str = "1947", to: str = "2026"):
    user, profile = ctx(request)
    e = db.q("SELECT * FROM entities WHERE id=?", (eid,), one=True)
    if not e: return HTMLResponse(R.page("Not found", "<div class='alert'>Unknown entity.</div>", user, profile, db.PROFILE_LABELS[profile]), 404)
    rows, total, n = [], 0.0, 0
    for r in db.q("SELECT case_id, role FROM case_params WHERE entity_id=? GROUP BY case_id, role", (eid,)):
        c = db.q("SELECT * FROM cases WHERE id=?", (r["case_id"],), one=True)
        y = db.first_year(c["period"])
        if not (int(frm) <= y <= int(to)): continue
        m = case_median(c["id"], c["weight"], profile)
        if m is None: continue
        total += m; n += 1
        rows.append(f"<tr><td>{y}</td><td><a href='/case/{c['id']}'>{R.esc(c['title'])}</a><br>"
                    f"<span class='muted'>{R.esc(c['role'] if 'role' in c.keys() else r['role'])} · w{c['weight']}</span></td>"
                    f"<td class='num'>{R.chip(m)}</td></tr>")
    rows.sort()
    body = f"""<div class="card"><h1>Report card — {R.esc(e['name'])}</h1>
      <p class="muted">Window {R.esc(frm)}–{R.esc(to)} · trust profile: <b>{R.esc(db.PROFILE_LABELS[profile])}</b>
      · generated {today()} · {n} cases</p>
      <form class="inline filters" method="get"><label>From <input name="frm" value="{R.esc(frm)}" style="width:90px"></label>
      <label>To <input name="to" value="{R.esc(to)}" style="width:90px"></label>
      <button class="btn">Regenerate</button></form>
      <p style="font-size:1.4rem"><b>Composite: {R.chip(round(total,1))}</b></p></div>
      <table><thead><tr><th>Year</th><th>Case</th><th class="num">Score</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
      <p class="muted">Print/PDF: Ctrl+P. Weekly & yearly cards (PDF + share image) ship in P4.</p>"""
    return R.page(f"Report card — {e['name']}", body, user, profile, db.PROFILE_LABELS[profile])

# ---------- JSON API (the future Next.js front end consumes these) ---------
@app.get("/api/health")
def health(): return {"ok": True, "ts": time.time()}

@app.get("/api/entities")
def api_entities(): return db.q("SELECT * FROM entities")

@app.get("/api/cases")
def api_cases():
    return [{**dict(c), "status": db.case_status(c["id"])} for c in db.q("SELECT * FROM cases")]

@app.get("/api/case/{cid}")
def api_case(cid: str, trust: str = "balanced"):
    c = db.q("SELECT * FROM cases WHERE id=?", (cid,), one=True)
    if not c: return JSONResponse({"detail": "not found"}, 404)
    ps = []
    for p in db.q("SELECT * FROM case_params WHERE case_id=?", (cid,)):
        m, n = db.param_median(cid, p["param"], trust)
        ps.append({"param": p["param"], "seed": p["seed_score"], "median": m,
                   "evidence_passing": n, "grade": db.best_grade(p["sources"]),
                   "justification": p["justification"], "sources": db.links(p["sources"])})
    return {"case": dict(c), "status": db.case_status(cid), "params": ps}

@app.get("/api/totals")
def api_totals(trust: str = "balanced"):
    return {e["id"]: entity_totals(e["id"], trust) for e in db.q("SELECT id FROM entities")}

@app.get("/api/timeline")
def api_timeline(): return db.q("SELECT * FROM timeline")

@app.get("/api/claims")
def api_claims(): return db.q("SELECT * FROM claims")

DATE_RE = re.compile(r"^\d{4}(-\d{2})?(-\d{2})?$")
def valid_when(w): return bool(w) and bool(DATE_RE.match(w.strip()))

class VoteIn(BaseModel):
    case_id: str; param: str; score: float; evidence_url: str; when: str = ""

@app.post("/api/vote")
def api_vote(request: Request, v: VoteIn):
    user, _ = ctx(request)
    if not user: return JSONResponse({"detail": "login required"}, 401)
    if not (-5 <= v.score <= 5): return JSONResponse({"detail": "score must be −5..+5"}, 400)
    if not v.evidence_url.startswith("http"): return JSONResponse({"detail": "evidence URL required"}, 400)
    if not valid_when(v.when): return JSONResponse({"detail": "event date required (YYYY-MM-DD). Everything on RajScore is timestamped — that is how the timeline stays honest."}, 400)
    ok = db.q("SELECT entity_id FROM case_params WHERE case_id=? AND param=?", (v.case_id, v.param), one=True)
    if not ok: return JSONResponse({"detail": "unknown parameter for this case"}, 400)
    con = __import__("sqlite3").connect(db.DB)
    con.execute("""INSERT INTO votes(user_id,case_id,entity_id,param,score,evidence_url,"when",created)
                   VALUES(?,?,?,?,?,?,?,?)
                   ON CONFLICT(user_id,case_id,param) DO UPDATE SET score=excluded.score,
                   evidence_url=excluded.evidence_url, "when"=excluded."when", created=excluded.created""",
                (user["id"], v.case_id, ok["entity_id"], v.param, v.score, v.evidence_url, v.when, time.time()))
    # refresh case status
    newstatus = db.case_status(v.case_id)
    con.execute("UPDATE cases SET status=? WHERE id=? AND status!='CHALLENGED'", (newstatus, v.case_id))
    con.commit(); con.close()
    return {"ok": True}

class ChallengeIn(BaseModel):
    kind: str = "case"; object_id: str = ""; note: str; evidence_url: str; case_id: str = ""; when: str = ""

@app.post("/api/challenge")
def api_challenge(request: Request, ch: ChallengeIn):
    user, _ = ctx(request)
    if not user: return JSONResponse({"detail": "login required"}, 401)
    obj = ch.object_id or ch.case_id
    if not obj or not ch.evidence_url.startswith("http"):
        return JSONResponse({"detail": "object id and evidence URL required"}, 400)
    if not valid_when(ch.when):
        return JSONResponse({"detail": "date of the item you are challenging is required (YYYY-MM-DD)"}, 400)
    if not re.match(r"^\d{4}(-\d{2})?(-\d{2})?$", ch.when.strip()):
        return JSONResponse({"detail": "bad date format — use YYYY-MM-DD"}, 400)
    con = __import__("sqlite3").connect(db.DB)
    con.execute('INSERT INTO challenges(kind,object_id,note,evidence_url,"when",user_id,created) VALUES(?,?,?,?,?,?,?)',
                (ch.kind, obj, ch.note, ch.evidence_url, ch.when, user["id"], time.time()))
    if ch.kind == "case":
        con.execute("UPDATE cases SET status='CHALLENGED' WHERE id=?", (obj,))
    con.commit(); con.close()
    return {"ok": True}

# ----- fundamentals layer ---------------------------------------------------
@app.get("/fundamentals", response_class=HTMLResponse)
def fundamentals(request: Request):
    user, profile = ctx(request)
    funds = db.fund_rows()
    spec = R.spectrum_svg(funds)
    def band(pol):
        out = []
        for f in [x for x in funds if x["polarity"] == pol]:
            m, c = db.fund_vote_stats(f["slug"])
            crowd = f'<span class="muted">crowd mean {m:.1f} from {c} placement(s)</span>' if c else '<span class="muted">anchor position (seeded)</span>'
            out.append(f"""<tr id="{f['slug']}">
              <td><b>{R.esc(f['name'])}</b><br><span class="muted">{R.esc(f['definition'])}</span></td>
              <td class="num"><b>{f['position']:g}</b><br><span class="muted">range {f['range_lo']:g}–{f['range_hi']:g}</span></td>
              <td>{R.badge(f['status'])}<br>{crowd}</td>
              <td><form class="inline placeform" data-slug="{R.esc(f['slug'])}">
                <input name="position" type="number" min="0" max="100" step="0.5" placeholder="0–100" style="width:86px" required>
                <input name="when" type="text" placeholder="YYYY-MM-DD" style="width:120px" required>
                <button class="btn ghost">place</button><span class="fm muted"></span></form></td>
            </tr>""")
        return "".join(out)
    body = f"""<h1>The fundamentals scale</h1>
    <p>This platform's bedrock: <b>atomic, irreplaceable building blocks</b> — things like
    <i>opacity</i>, <i>proven corruption</i>, <i>loss of lives</i>, <i>institution-building</i> — each with a
    position on a 0–100 severity scale. <b>Parameters are compositions of fundamentals</b>, so unlike acts can
    never be scored equal by careless labels: a press-shy leader (opacity ≈ 6) and a proven institutional scam
    (≈ 50) land in different universes by construction.</p>
    {spec}
    <div class="card"><b>How placement works.</b> New fundamentals are proposed below with a definition and a
    suggested position roughly relative to its neighbours ("worse than promise-breaking, milder than power misuse").
    Members then <b>place</b> it on the scale (with a date — everything here is timestamped). At ≥5 placements the
    consensus position locks to the crowd mean, and stays re-challengeable forever. Weights are relative: the
    whole scale can be rescaled by any positive constant without changing any ranking — what matters is
    <i>where something sits beside everything else</i>.</div>
    <h2 id="harm-band">Harm fundamentals (score −)</h2>
    <table><thead><tr><th>Fundamental</th><th class="num">Position (0–100)</th><th>Status</th><th>Cast your placement</th></tr></thead>
    <tbody>{band('harm')}</tbody></table>
    <h2 id="virtue-band">Virtue fundamentals (score +)</h2>
    <table><thead><tr><th>Fundamental</th><th class="num">Position (0–100)</th><th>Status</th><th>Cast your placement</th></tr></thead>
    <tbody>{band('virtue')}</tbody></table>
    <div class="card"><h2>Propose a new fundamental <span class="badge warn">irreplaceable once in ledger</span></h2>
    <p class="muted">Ask first: is it <b>atomic</b> (can't be explained as two existing fundamentals combined)?
    Does it deserve its own slot on the scale for decades? Examples rejected: 'Gujarat 2002' (not atomic — an event,
    not a fundamental). Example accepted: 'state capacity failure in crisis'.</p>
    <form class="grid" id="propform" style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr))">
      <div><label>Name (short)</label><input name="name" required maxlength="60"></div>
      <div><label>Definition (one sentence, objective)</label><input name="definition" required></div>
      <div><label>Polarity</label><select name="polarity"><option>harm</option><option>virtue</option></select></div>
      <div><label>Your proposed position (0–100)</label><input name="position" type="number" min="0" max="100" step="0.5" required></div>
      <div><label>Date</label><input name="when" type="text" placeholder="YYYY-MM-DD" required></div>
      <div><label>&nbsp;</label><button class="btn">Propose</button><span class="pm muted"></span></div>
    </form></div>"""
    js = R.JS_UTILS + """
    document.querySelectorAll('form.placeform').forEach(f=>{f.addEventListener('submit',async e=>{e.preventDefault();
      const d=formVals(f); d.slug=f.dataset.slug;
      const r=await postJSON('/api/fundamental/place',d);
      f.querySelector('.fm').textContent = r.ok?' ✔ placed':(' ✖ '+(r.body.detail||'error'));
      if(r.ok) setTimeout(()=>location.reload(),900);});});
    const pf=document.getElementById('propform'); if(pf) pf.onsubmit=async e=>{e.preventDefault();
      const r=await postJSON('/api/fundamental/propose',formVals(pf));
      pf.querySelector('.pm').textContent = r.ok?' ✔ proposed — visible in the ledger':(' ✖ '+(r.body.detail||'error'));
      if(r.ok) setTimeout(()=>location.reload(),900);};
    """
    return R.page("Fundamentals", body, user, profile, db.PROFILE_LABELS[profile], extra_js=js)

class FundPlaceIn(BaseModel):
    slug: str; position: float; when: str = ""

@app.post("/api/fundamental/place")
def api_fund_place(request: Request, fp: FundPlaceIn):
    user, _ = ctx(request)
    if not user: return JSONResponse({"detail": "login required"}, 401)
    if not (0 <= fp.position <= 100): return JSONResponse({"detail": "position must be 0–100"}, 400)
    if not valid_when(fp.when): return JSONResponse({"detail": "date required (YYYY-MM-DD)"}, 400)
    if not db.q("SELECT slug FROM fundamentals WHERE slug=?", (fp.slug,), one=True):
        return JSONResponse({"detail": "unknown fundamental"}, 400)
    con = __import__("sqlite3").connect(db.DB)
    con.execute('INSERT INTO fund_votes(slug,user_id,position,"when",created) VALUES(?,?,?,?,?) '
                'ON CONFLICT(slug,user_id) DO UPDATE SET position=excluded.position, "when"=excluded."when", created=excluded.created',
                (fp.slug, user["id"], fp.position, fp.when, time.time()))
    con.commit(); con.close()
    db.fund_consensus_refresh(fp.slug)
    return {"ok": True}

class FundPropIn(BaseModel):
    name: str; definition: str; polarity: str = "harm"; position: float; when: str = ""

@app.post("/api/fundamental/propose")
def api_fund_propose(request: Request, fp: FundPropIn):
    user, _ = ctx(request)
    if not user: return JSONResponse({"detail": "login required"}, 401)
    if not valid_when(fp.when): return JSONResponse({"detail": "date required (YYYY-MM-DD)"}, 400)
    if fp.polarity not in ("harm", "virtue"): return JSONResponse({"detail": "polarity = harm|virtue"}, 400)
    slug = re.sub(r"[^a-z0-9]+", "-", fp.name.strip().lower()).strip("-")[:40]
    if not slug: return JSONResponse({"detail": "bad name"}, 400)
    if db.q("SELECT slug FROM fundamentals WHERE slug=?", (slug,), one=True):
        return JSONResponse({"detail": "a fundamental with this name already exists"}, 409)
    con = __import__("sqlite3").connect(db.DB)
    con.execute("INSERT INTO fundamentals(slug,name,definition,polarity,position,range_lo,range_hi,status,created_by,created) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (slug, fp.name.strip(), fp.definition.strip(), fp.polarity, fp.position,
                 max(0.0, float(fp.position)-5), min(100.0, float(fp.position)+5), "PROPOSED", user["id"], time.time()))
    con.execute('INSERT INTO fund_votes(slug,user_id,position,"when",created) VALUES(?,?,?,?,?)',
                (slug, user["id"], fp.position, fp.when, time.time()))
    con.commit(); con.close()
    return {"ok": True, "slug": slug}

class ParamAddIn(BaseModel):
    case_id: str; param: str; funds: str; evidence_url: str; when: str = ""

@app.post("/api/param/add")
def api_param_add(request: Request, pa: ParamAddIn):
    """Add a parameter to a case as a composition of fundamentals."""
    user, _ = ctx(request)
    if not user: return JSONResponse({"detail": "login required"}, 401)
    if not db.q("SELECT id FROM cases WHERE id=?", (pa.case_id,), one=True):
        return JSONResponse({"detail": "unknown case"}, 400)
    if not pa.evidence_url.startswith("http"): return JSONResponse({"detail": "evidence URL required"}, 400)
    if not valid_when(pa.when): return JSONResponse({"detail": "event date required (YYYY-MM-DD)"}, 400)
    combo = []
    for part in pa.funds.split(","):
        part = part.strip()
        if not part: continue
        m = re.match(r"^([a-z0-9-]+)(?::([0-9.]+))?$", part)
        if not m: return JSONResponse({"detail": f"bad fund token '{part}' — use slug or slug:strength"}, 400)
        slug, strength = m.group(1), float(m.group(2) or 1)
        f = db.q("SELECT * FROM fundamentals WHERE slug=?", (slug,), one=True)
        if not f: return JSONResponse({"detail": f"unknown fundamental '{slug}'"}, 400)
        if not (0.1 <= strength <= 1.0): return JSONResponse({"detail": "strength 0.1–1.0"}, 400)
        combo.append({"slug": slug, "strength": strength, **{k: f[k] for k in f.keys()}})
    if not combo: return JSONResponse({"detail": "choose at least one fundamental"}, 400)
    raw = db.compose_points(combo)
    norm = db.composed_to_five(raw)
    ent = db.q("SELECT DISTINCT entity_id FROM case_params WHERE case_id=? LIMIT 1", (pa.case_id,), one=True)
    combo_txt = ", ".join("{}x{}".format(c["name"], c["strength"]) for c in combo)
    just_txt = "community-composed: {} (fundamental-scale {:+.1f} pts)".format(combo_txt, raw)
    con = __import__("sqlite3").connect(db.DB)
    try:
        con.execute("""INSERT INTO case_params(case_id,entity_id,role,param,seed_score,justification,sources,creator,created)
                       VALUES(?,?,?,?,?,?,?,?,?)""",
                    (pa.case_id, ent["entity_id"] if ent else "party:bjp", "crowd", pa.param.strip()[:120],
                     norm, just_txt, pa.evidence_url, user["id"], time.time()))
        for c in combo:
            con.execute("INSERT OR IGNORE INTO param_funds(case_id,param,slug,strength) VALUES(?,?,?,?)",
                        (pa.case_id, pa.param.strip()[:120], c["slug"], c["strength"]))
        con.execute("UPDATE cases SET status='COMMUNITY REVIEW' WHERE id=? AND status='SEEDED'", (pa.case_id,))
        con.commit()
    except Exception as e:
        con.close(); return JSONResponse({"detail": f"could not add: {e}"}, 500)
    con.close()
    return {"ok": True, "raw_points": raw, "normalised": norm}

class AuthIn(BaseModel):
    username: str; password: str; leaning: str = "none"

@app.post("/api/auth/signup")
def api_signup(a: AuthIn):
    uid = db.create_user(a.username.strip(), a.password, a.leaning)
    if not uid: return JSONResponse({"detail": "username taken"}, 409)
    tok = db.new_session(uid)
    resp = JSONResponse({"ok": True})
    resp.set_cookie("rs_session", tok, max_age=60*60*24*30, httponly=True)
    return resp

@app.post("/api/auth/login")
def api_login(a: AuthIn):
    r = db.q("SELECT id FROM users WHERE username=? AND pw=?", (a.username.strip(), db.hash_pw(a.password)), one=True)
    if not r: return JSONResponse({"detail": "wrong credentials"}, 401)
    resp = JSONResponse({"ok": True})
    resp.set_cookie("rs_session", db.new_session(r["id"]), max_age=60*60*24*30, httponly=True)
    return resp
