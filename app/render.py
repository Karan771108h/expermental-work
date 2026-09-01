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
    ("/timeline", "Timeline"), ("/claims", "Fact-check"), ("/rules", "Rules & Trust"),
]

def page(title, body, user=None, profile="balanced", profile_label="", extra_js=""):
    nav = "".join(f'<a href="{h}">{t}</a>' for h, t in NAV)
    auth = (f'<span class="userchip">👤 {esc(user["username"])} · {esc(user["leaning"])}</span>'
            f' <a href="/auth/logout">logout</a>') if user else '<a href="/auth">login / join</a>'
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · RajScore</title>
<link rel="stylesheet" href="/static/style.css">
<link rel="icon" href="/static/logo.png">
</head><body>
<div class="tricolor"></div>
<header>
  <a class="brand" href="/"><img src="/static/logo.png" alt="RajScore"><span>RajScore</span><small>run by people, checked by everyone</small></a>
  <nav>{nav}</nav><div class="authbox">{auth}</div>
</header>
<div class="trustbar">🎛 Trust profile: <b>{esc(profile_label)}</b> · scores recompute on your dial —
  <a href="/rules">change</a></div>
<main>{body}</main>
<footer>
  <b>RajScore is a civic experiment.</b> Scores are produced by users under published rules
  (see <a href="/rules">Rules & Trust</a>); every figure shows its evidence links, and every
  item can be challenged — nothing here is "final", including this disclaimer's favourite scores.
  Seed corpus: the Ideal-Party Audit (1947–Sep 2026). <a href="https://github.com/Karan771108h/expermental-work">Source</a>.
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
