"""RajScore — tiny server-side renderer (no build chain; API-first for future Next.js)."""
import html as _html

def esc(s): return _html.escape(str(s) if s is not None else "")

def chip(score):
    if score is None: return '<span class="chip none">n/a</span>'
    cls = "pos" if score > 0 else ("neg" if score < 0 else "zero")
    return f'<span class="chip {cls}">{score:+.1f}</span>'

def badge(status):
    cls = {"CONSENSUS": "ok", "CHALLENGED": "bad", "CONTESTED": "warn",
           "COMMUNITY REVIEW": "warn", "SEEDED (seed corpus)": "gray"}.get(status, "gray")
    return f'<span class="badge {cls}">{esc(status)}</span>'

def grade_pill(g):
    labels = {"A": "A · court/official", "B": "B · outlet of record", "C": "C · weak/single"}
    return f'<span class="badge g{g}" title="{labels.get(g,"")}">{labels.get(g,"")}</span>'

def source_links(sources):
    out = []
    for i, u in enumerate([s.strip() for s in str(sources).split(";") if s.strip().startswith("http")]):
        out.append(f'<a href="{esc(u)}" target="_blank" rel="noopener">[{i+1}]</a>')
    return " ".join(out) if out else '<span class="muted">(named report; link pending)</span>'

NAV = [
    ("/", "Home"), ("/entities", "Entities"), ("/cases", "Cases"),
    ("/fundamentals", "⚖ Fundamentals"), ("/timeline", "Timeline"),
    ("/claims", "Fact-check"), ("/rules", "Rules & Trust"),
]

def spectrum_svg(funds, w=980, h=96):
    """The 0-100 scale with every fundamental plotted — harm up, virtue down."""
    harms = [f for f in funds if f["polarity"] == "harm"]
    virts = [f for f in funds if f["polarity"] == "virtue"]
    def markers(rows, y, upcolor, dy):
        out, lane = [], {}
        for f in rows:
            x = round(f["position"] / 100 * (w - 14) + 7, 1)
            lane.setdefault(int(x / 46), 0)
            k = lane[int(x / 46)]
            lane[int(x / 46)] += 1
            ly = y + (dy * k)
            lab = f["name"] if len(f["name"]) <= 24 else f["name"][:23] + "…"
            out.append(f'<line x1="{x}" x2="{x}" y1="{h/2}" y2="{y}" stroke="{upcolor}" stroke-width="2"/>'
                       f'<a href="/fundamentals#{f["slug"]}"><text x="{x}" y="{ly}" text-anchor="middle" '
                       f'font-size="9.5" fill="{upcolor}">{esc(lab)} ({f["position"]:g})</text>'
                       f'<circle cx="{x}" cy="{y+ (4 if dy>0 else -4)}" r="3" fill="{upcolor}"/></a>')
        return "".join(out)
    mid = h/2
    return ('<div class="spectrum"><svg width="100%%" viewBox="0 0 %d %d" style="height:%dpx">' % (w, h, h)
            + f'<defs><linearGradient id="sg" x1="0" x2="1"><stop offset="0" stop-color="#e2e8f0"/>'
              f'<stop offset=".5" stop-color="#fde68a"/><stop offset="1" stop-color="#991b1b"/></linearGradient></defs>'
            + f'<a href="/fundamentals#virtue-band"><text x="6" y="{h-6}" font-size="10" fill="#166534">← virtue (positive acts)</text></a>'
            + markers(virts, mid+34, "#166534", 12)
            + f'<rect x="0" y="{mid-4}" width="{w}" height="8" rx="4" fill="url(#sg)"/>'
            + markers(harms, mid-12, "#991b1b", -11)
            + f'<a href="/fundamentals#harm-band"><text x="{w-6}" y="12" text-anchor="end" font-size="10" fill="#991b1b">harm (negative acts) →</text></a>'
            + "</svg></div>")

TOUR_STEPS = [
    ("Welcome to RajScore", "This is a crowd-run accountability platform: every score comes from people voting with evidence, and nothing is ever permanent."),
    ("Step 1 — Read a case", "Cases are incidents/policies with per-case parameters. Every parameter shows its evidence links and evidence grade (A/B/C). <a href='/cases'>Open the case ledger</a>."),
    ("Step 2 — Set your trust dial", "Go to Rules &amp; Trust and pick which evidence grades YOU accept: official-only, balanced, or open. All scores on the site recompute for your choice."),
    ("Step 3 — Fundamentals: atoms, parts & multipliers", "Parameters are composed from atomic fundamentals on a 0–100 scale — and atoms split further (opacity → press-access, data-withholding…), while <b>modifiers</b> multiply context: Parliament ×1.5, social media ×0.6, chief ×1.25, supporter ×0.7, riots followed ×1.8. See <a href='/fundamentals'>Fundamentals</a>."),
    ("Step 4 — Vote with receipts", "Sign in, then on any case vote on a parameter: score −5..+5 + an evidence link + the EVENT DATE. Community consensus needs 5+ votes at ⅔ agreement. More aspects assessed = finer signal — check the coverage meter on each case."),
    ("Step 5 — Build case threads", "Every case has a dated <b>thread</b>: add milestones (who said/did/ruled what, when, with proof) and watch history assemble itself. Example: the Ayodhya case thread."),
    ("Step 5b — Challenge anything", "Even a 50-year-old verdict can be re-opened: hit 'challenge', supply counter-evidence and its date. A challenged item is flagged until the community resolves it."),
    ("Step 6 — Report cards", "On any entity page hit 'report card' to get a dated, windowed scorecard (Ctrl+P to PDF). The data is also a fact-check engine — see /claims."),
]

TOUR_HTML = """
<div id="tour" class="tour hidden">
  <div class="tour-card">
    <div class="tour-dots"></div>
    <h3 id="tourTitle"></h3><p id="tourText"></p>
    <div class="tour-actions">
      <button id="tourSkip" class="btn ghost">Skip</button>
      <button id="tourNext" class="btn">Next →</button>
    </div>
  </div>
</div>
<script>
(function(){
  var KEY='rs_tour_seen_v1';
  var steps=%TOUR_STEPS%;
  var el=document.getElementById('tour');
  function start(){ if(localStorage.getItem(KEY)) return; el.classList.remove('hidden'); show(0); }
  window.rsReplayTour=function(){ localStorage.removeItem(KEY); if(location.pathname!=='/'){location.href='/?tour=1';return;} start(); };
  var i=0;
  function show(k){ i=k; document.getElementById('tourTitle').textContent=steps[k][0];
    document.getElementById('tourText').innerHTML=steps[k][1];
    document.querySelector('.tour-dots').innerHTML=steps.map(function(_,j){return '<span class="dot'+(j===k?' on':'')+'"></span>';}).join('');
    document.getElementById('tourNext').textContent=(k===steps.length-1)?'Done ✔':'Next →'; }
  document.getElementById('tourNext').onclick=function(){ if(i+1>=steps.length){done();} else show(i+1); };
  document.getElementById('tourSkip').onclick=done;
  function done(){ localStorage.setItem(KEY,'1'); el.classList.add('hidden'); }
  if(location.pathname==='/'&&(/[?&]tour=1/.test(location.search)||!localStorage.getItem(KEY))) start();
})();
</script>
""".replace("%TOUR_STEPS%", "TOUR_STEPS_JSON")

def page(title, body, user=None, profile="balanced", profile_label="", extra_js="", tour=False):
    import json as _json
    nav = "".join(f'<a href="{h}">{t}</a>' for h, t in NAV)
    auth = (f'<span class="userchip">👤 {esc(user["username"])} · {esc(user["leaning"])}</span>'
            f' <a href="/auth/logout">logout</a>') if user else '<a href="/auth">login / join</a>'
    tour_html = (TOUR_HTML.replace("TOUR_STEPS_JSON", _json.dumps(TOUR_STEPS))
                 if tour or True else "")
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · RajScore</title>
<link rel="stylesheet" href="/static/style.css">
<link rel="icon" href="/static/logo.png">
</head><body>
<div class="tricolor"></div>
<header>
  <a class="brand" href="/"><img src="/static/logo.png" alt="RajScore"><span>RajScore</span><small>run by people, checked by everyone</small></a>
  <nav>{nav}</nav><div class="authbox">📖 <a href="/tour">tutorial</a> · {auth}</div>
</header>
<div class="trustbar">🎛 Trust profile: <b>{esc(profile_label)}</b> · scores recompute on your dial —
  <a href="/rules">change</a></div>
<main>{body}</main>
{tour_html}
<footer>
  <b>RajScore is a civic experiment.</b> Scores are produced by users under published rules
  (see <a href="/rules">Rules & Trust</a>); every figure shows its evidence links, and every
  item can be challenged — nothing here is "final", including this disclaimer's favourite scores.
  Seed corpus: the Ideal-Party Audit (1947–Sep 2026).
  <a href="javascript:rsReplayTour()">📖 Replay tutorial</a> ·
  <a href="https://github.com/Karan771108h/expermental-work">Source</a>.
</footer>
<script>{extra_js}</script>
</body></html>"""

JS_UTILS = """
async function postJSON(url, data){
  const r = await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  return {ok:r.ok, body: await r.json().catch(()=>({}))};
}
function formVals(form){ const o={}; for(const el of form.elements){ if(el.name) o[el.name]=el.value; } return o; }
"""
