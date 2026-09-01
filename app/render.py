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

def spectrum_svg(funds, w=980, h=96, master=None, anchors=None):
    """The master 0-300 ledger: 0-100 harm zone, 100-200 neutral, 200-300 virtue."""
    if master is None:
        master = {f["slug"]: (100.0 - f["position"] if f["polarity"]=="harm" else 200.0+f["position"])
                  for f in funds}
    if anchors is None: anchors = DEFAULT_ANCHORS
    rows = [f for f in funds if f["polarity"] != "modifier"]
    def markers(items, upcolor):
        out, lane = [], {}
        for f in items:
            m = master.get(f["slug"])
            if m is None: continue
            x = round(m / 300 * (w - 14) + 7, 1)
            lab = f["name"] if len(f["name"]) <= 22 else f["name"][:21] + "…"
            above = m < 150
            y = (23 - 11) * 0 + 22 if above else h - 34
            k = int(x / 40) if above else int(x / 40)
            lane.setdefault((above, k), 0)
            n = lane[(above, k)]
            lane[(above, k)] += 1
            ly = y + (-10 if above else 11) * n
            ty = y if above else h - 6 - (h - 6 - (m/300 and 0))
            anchor_y = mid - 6 if above else mid + 14
            out.append(f'<a href="/fundamentals#{f["slug"]}"><line x1="{x}" x2="{x}" y1="{mid}" y2="{anchor_y}" stroke="{upcolor}" stroke-width="2"/>'
                       f'<circle cx="{x}" cy="{anchor_y + (-6 if above else 6)}" r="3.2" fill="{upcolor}">'
                       f'<title>{esc(f["name"])} — master {m:.0f}</title></circle>'
                       f'<text x="{x}" y="{ly}" text-anchor="middle" font-size="9" fill="{upcolor}">{esc(lab)}</text></a>')
        return "".join(out)
    mid = h/2
    ants = "".join(f'<g><line x1="{round(a[1]/300*(w-14)+7,1)}" x2="{round(a[1]/300*(w-14)+7,1)}" y1="{mid-4}" y2="{mid+4}" stroke="#64748b" stroke-width="1"/>'
                   f'<title>anchor: {esc(a[0])} ({a[1]})</title></g>' for a in anchors)
    w3 = w/3.0
    return (f'<div class="spectrum"><svg width="100%" viewBox="0 0 {w} {h}" style="height:{h}px">'
            f'<rect x="0" y="{mid-9}" width="{w3*1.425:.0f}" height="18" rx="4" fill="#fee2e2"/>'
            f'<rect x="{w3*1.425:.0f}" y="{mid-9}" width="{w3*0.575+w3*0.5:.0f}" height="18" fill="#f1f5f9"/>'
            f'<rect x="{w3*2.425:.0f}" y="{mid-9}" width="{w-w3*2.425-7:.0f}" height="18" rx="4" fill="#dcfce7"/>'
            f'<text x="4" y="{mid+3}" font-size="9.5" fill="#b91c1c">worse</text>'
            f'<text x="{w3-34:.0f}" y="{mid+3}" font-size="9.5" fill="#b91c1c">less bad</text>'
            f'<text x="{w3*1.55:.0f}" y="{mid+3}" font-size="9.5" fill="#64748b">neutral</text>'
            f'<text x="{w3*2.28:.0f}" y="{mid+3}" font-size="9.5" fill="#166534">less good</text>'
            f'<text x="{w-30:.0f}" y="{mid+3}" font-size="9.5" fill="#166534">better</text>'
            f'<line x1="{w3*1.425:.0f}" x2="{w3*1.425:.0f}" y1="{mid-12}" y2="{mid+12}" stroke="#cbd5e1"/>'
            f'<line x1="{w3*2.425:.0f}" x2="{w3*2.425:.0f}" y1="{mid-12}" y2="{mid+12}" stroke="#cbd5e1"/>'
            + ants
            + markers([f for f in rows if master.get(f["slug"],150) < 165], "#b91c1c")
            + markers([f for f in rows if master.get(f["slug"],150) >= 165], "#166534")
            + f'<text x="7" y="12" font-size="9.5" fill="#7f1d1d">harm 0–100</text>'
            f'<text x="{w-7}" y="12" text-anchor="end" font-size="9.5" fill="#166534">virtue 200–300</text>'
            f'<text x="{w/2:.0f}" y="{h-2}" text-anchor="middle" font-size="9" fill="#94a3b8">master 0–300 ledger · ⏺ anchors on the band are universal references</text>'
            + "</svg></div>")

TOUR_STEPS = [
    ("Welcome to RajScore", "This is a crowd-run accountability platform: every score comes from people voting with evidence, and nothing is ever permanent."),
    ("Step 1 — Read a case", "Cases are incidents/policies with per-case parameters. Every parameter shows its evidence links and evidence grade (A/B/C). <a href='/cases'>Open the case ledger</a>."),
    ("Step 2 — Set your trust dial", "Go to Rules &amp; Trust and pick which evidence grades YOU accept: official-only, balanced, or open. All scores on the site recompute for your choice."),
    ("Step 3 — Fundamentals: atoms, parts & multipliers", "Parameters are composed from atomic fundamentals on a 0–100 scale — and atoms split further (opacity → press-access, data-withholding…), while <b>modifiers</b> multiply context: Parliament ×1.5, social media ×0.6, chief ×1.25, supporter ×0.7, riots followed ×1.8. See <a href='/fundamentals'>Fundamentals</a>."),
    ("Step 4 — Slide, don't type", "No bare numbers anywhere: votes and placements happen on ONE master 0–300 ledger — red (worse) 0–100, neutral 100–200, green (better) 200–300 — with universal anchors (murder, traffic violation, founding an institution…) printed on it. Bounded sliders keep each item inside its agreed band (anti-national can only sit in 0–50 territory). Community dots show how others placed it; consensus locks to the MEDIAN, so one extreme slider can't rig anything."),
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

DEFAULT_ANCHORS = [
    ("mass killing / communal massacre", 3), ("murder", 5), ("an act against the nation", 14),
    ("institutional scam", 50), ("casteist/communal hate speech", 74), ("traffic violation", 93),
    ("littering", 97), ("jury duty done well", 215), ("a stranger's donation worth crores", 228),
    ("founding an enduring institution", 285),
]

BAND_WORD_JS = """function bandWord(m){return m<50?'very bad':m<100?'bad':m<140?'neutral-bad':m<=160?'neutral':m<=200?'neutral-good':m<=250?'good':'very good';}"""

def master_slider(name, lo, hi, value, anchors=None, cloud=None, conv=""):
    """Big 0-300 slider bounded to [lo,hi] (master coords), painted with the ledger's
    three zones, universal anchor ticks and the community placement cloud."""
    anchors = anchors if anchors is not None else DEFAULT_ANCHORS
    frac = lambda a: round((a - lo) / (hi - lo) * 100, 2)
    # zone proportions within the visible window
    def zp(a, b, col):
        l = 100 * max(lo, a) / 300; r = 100 * min(hi, b) / 300
        if b <= lo or a >= hi: return ""
        l = (max(lo, a) - lo) / (hi - lo) * 100; r = (min(hi, b) - lo) / (hi - lo) * 100
        return f'{col} {l:.1f}%, {col} {r:.1f}%, '
    stops = (zp(0, 100, "#fca5a5") + zp(100, 200, "#e2e8f0") + zp(200, 300, "#86efac"))
    stops = stops.rstrip(", ") 
    ticks = "".join(
        f'<span class="mtick" style="left:{frac(a[1]):.1f}%" title="{esc(a[0])} — {a[1]}">▾</span><span class="mlab" style="left:{frac(a[1]):.1f}%">{esc(a[0])}</span>'
        for a in anchors if lo <= a[1] <= hi)
    cl = "".join(
        f'<span class="mdot" style="left:{frac(v):.1f}%" title="a member placed {v:.0f}"></span>'
        for v in (cloud or []) if lo <= v <= hi)
    return (f'<div class="mslide" data-pol-lo="{lo}" data-pol-hi="{hi}">'
            f'<div class="mwrap"><input type="range" class="mast" name="{name}" '
            f'min="{lo:g}" max="{hi:g}" step="0.5" value="{value:g}" required '
            f'oninput="msout(this)" data-convert="{conv}" style="background:linear-gradient(90deg,{stops if stops else "#e2e8f0,#e2e8f0"})">'
            f'<div class="ticks">{ticks}</div><div class="cloud">{cl}</div></div>'
            f'<output class="mout">—</output></div>')

MS_JS = BAND_WORD_JS + """
function msout(el){
  var v=parseFloat(el.value), o=el.closest('.mslide').querySelector('.mout');
  var conv=el.getAttribute('data-convert')||'';
  if(conv==='harm'){o.textContent='master '+v+'  ('+bandWord(v)+')  → polarity value '+(100-v).toFixed(1);}
  else if(conv==='virtue'){o.textContent='master '+v+'  ('+bandWord(v)+')  → polarity value '+(v-200).toFixed(1);}
  else if(conv==='score'){var s=Math.round((v-150)/30*2)/2; el.dataset.score=s; o.textContent='master '+v+'  ('+bandWord(v)+')  → submits score '+(s>0?'+':'')+s;}
  else {o.textContent='master '+v+'  ('+bandWord(v)+')';}
}
document.querySelectorAll('.mslide input.mast').forEach(msout);
"""
