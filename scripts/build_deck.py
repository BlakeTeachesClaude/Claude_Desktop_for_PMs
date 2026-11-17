"""Builds deck/index.html: a self-contained HTML deck (no network needed). Run: python scripts/build_deck.py"""
from pathlib import Path
# ---- deck engine: renders SLIDES + META into one self-contained HTML file (no network, works from file://) ----
import html
from pathlib import Path

CSS = """
:root{--bg:#0f1b2d;--panel:#16263d;--ink:#eef3fa;--mute:#9db0c8;--accent:#ffb454;--accent2:#5ac8c8;--line:#27405f;--code:#0a1424}
*{box-sizing:border-box}html,body{margin:0;height:100%;background:var(--bg);color:var(--ink);font:20px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.deck{position:relative;height:100vh;overflow:hidden}
.slide{display:none;position:absolute;inset:0;padding:6vh 7vw 9vh;flex-direction:column;justify-content:center}
.slide.active{display:flex}
.no-js .slide{display:flex;position:relative;min-height:100vh;border-bottom:1px solid var(--line)}
.kicker{color:var(--accent);letter-spacing:.14em;text-transform:uppercase;font-size:.62em;font-weight:700;margin-bottom:.6em;display:flex;gap:1em;align-items:center}
.badge{background:var(--panel);border:1px solid var(--line);color:var(--accent2);border-radius:999px;padding:.1em .8em;letter-spacing:.05em}
h1{font-size:2.6em;line-height:1.1;margin:0 0 .4em}h2{font-size:2em;line-height:1.15;margin:0 0 .6em}
.sub{color:var(--mute);font-size:1.15em;margin:0 0 1em}
ul{list-style:none;padding:0;margin:0}li{margin:.5em 0;padding-left:1.3em;position:relative}
li::before{content:"";position:absolute;left:0;top:.62em;width:.45em;height:.45em;border-radius:50%;background:var(--accent)}
.grid{display:grid;gap:1em;grid-template-columns:repeat(auto-fit,minmax(15em,1fr))}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:1em 1.2em}
.card h3{margin:0 0 .4em;color:var(--accent2);font-size:1em;letter-spacing:.04em}
.card p{margin:.2em 0;color:var(--ink)}
dl{display:grid;grid-template-columns:max-content 1fr;gap:.55em 1.4em;margin:0}dt{color:var(--accent);font-weight:700}dd{margin:0;color:var(--ink)}
.flow{display:flex;gap:1em;align-items:stretch}.flow .card{flex:1}.flow .arrow{align-self:center;color:var(--accent);font-size:1.6em}
table{width:100%;border-collapse:collapse;font-size:.78em}th{text-align:left;color:var(--accent);font-size:.8em;letter-spacing:.1em;text-transform:uppercase;padding:.3em .8em;border-bottom:2px solid var(--line)}td{padding:.38em .8em;border-bottom:1px solid var(--line);vertical-align:top}td:first-child{color:var(--accent2);font-weight:700;white-space:nowrap}
.layer{display:block}.layer .card{margin:.5em 0}.layer b{color:var(--accent)}
pre{background:var(--code);border:1px solid var(--line);border-radius:12px;padding:1em 1.2em;overflow:auto;font:.68em/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;margin:.4em 0 1em;white-space:pre}
.cols{display:grid;grid-template-columns:1.6fr 1fr;gap:1.4em;align-items:start}
.try{border-left:4px solid var(--accent);padding-left:1em}.try h3{margin:0 0 .3em;color:var(--accent)}
.note{color:var(--mute);font-size:.85em;margin-top:1em}
.cmd{font:.8em ui-monospace,Menlo,Consolas,monospace;background:var(--code);border:1px solid var(--line);border-radius:8px;padding:.4em .8em;margin:.4em 0;display:block;color:var(--accent2)}
.foot{position:absolute;left:7vw;right:7vw;bottom:2.4vh;display:flex;justify-content:space-between;color:var(--mute);font-size:.55em;letter-spacing:.08em;text-transform:uppercase}
.bar{position:fixed;left:0;top:0;height:4px;background:var(--accent);width:0;transition:width .2s}
.help{position:fixed;right:1em;top:1em;color:var(--mute);font-size:.55em;opacity:.0;transition:opacity .3s}.deck:hover .help{opacity:.8}
.overview .slide{display:flex;position:relative;transform:scale(.9)}
.overview.deck{overflow:auto;height:auto;min-height:100vh;display:grid;grid-template-columns:repeat(auto-fill,minmax(22em,1fr));gap:1em;padding:1em}
.overview .slide{height:15em;padding:1em;font-size:.45em;border:1px solid var(--line);border-radius:10px;cursor:pointer;overflow:hidden;transform:none;background:var(--bg)}
@media(max-width:800px){html,body{font-size:16px}.cols,.flow{display:block}.flow .arrow{display:none}.slide{padding:5vh 5vw 9vh;justify-content:flex-start;overflow:auto}}
@media print{@page{size:landscape;margin:0}html,body{background:#fff;color:#000;font-size:14px}.deck{height:auto;overflow:visible}.slide{display:flex!important;position:relative;height:100vh;page-break-after:always;background:#fff}
:root{--bg:#fff;--panel:#f3f6fa;--ink:#111;--mute:#445;--accent:#b35c00;--accent2:#005f73;--line:#ccd;--code:#f3f6fa}.bar,.help,.foot{display:none}}
"""

JS = """
(function(){
  var deck=document.querySelector('.deck'),slides=[].slice.call(document.querySelectorAll('.slide')),bar=document.querySelector('.bar'),i=0;
  document.documentElement.classList.remove('no-js');
  function show(n){i=Math.max(0,Math.min(slides.length-1,n));slides.forEach(function(s,k){s.classList.toggle('active',k===i)});
    bar.style.width=((i+1)/slides.length*100)+'%';try{history.replaceState(null,'','#'+(i+1))}catch(e){}document.title=META_TITLE+' ('+(i+1)+'/'+slides.length+')'}
  function toggleOverview(){deck.classList.toggle('overview');if(!deck.classList.contains('overview')){show(i)}else{slides.forEach(function(s){s.classList.remove('active')})}}
  document.addEventListener('keydown',function(e){
    if(e.metaKey||e.ctrlKey||e.altKey)return;var k=e.key;
    if(k==='ArrowRight'||k==='PageDown'||k===' '||k==='Enter'){e.preventDefault();show(i+1)}
    else if(k==='ArrowLeft'||k==='PageUp'||k==='Backspace'){e.preventDefault();show(i-1)}
    else if(k==='Home'){show(0)}else if(k==='End'){show(slides.length-1)}
    else if(k==='f'||k==='F'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen&&document.documentElement.requestFullscreen()}
    else if(k==='o'||k==='O'||k==='g'||k==='G'||k==='Escape'){toggleOverview()}
  });
  slides.forEach(function(s,k){s.addEventListener('click',function(){if(deck.classList.contains('overview')){i=k;toggleOverview()}})});
  var x0=null;document.addEventListener('touchstart',function(e){x0=e.touches[0].clientX},{passive:true});
  document.addEventListener('touchend',function(e){if(x0===null)return;var d=e.changedTouches[0].clientX-x0;if(Math.abs(d)>50)show(i+(d<0?1:-1));x0=null});
  window.addEventListener('hashchange',function(){var n=parseInt(location.hash.slice(1),10);if(n)show(n-1)});
  show((parseInt(location.hash.slice(1),10)||1)-1);
})();
"""

def e(s):
    return html.escape(s, quote=False)

def lis(items):
    return "<ul>" + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul>"

def render_slide(s, n, total, meta):
    t = s["type"]
    badge = f'<span class="badge">{e(s["minutes"])}</span>' if s.get("minutes") else ""
    head = f'<div class="kicker"><span>{e(s.get("kicker", meta["kicker"]))}</span>{badge}</div>'
    title = s.get("title", "")
    if t == "title":
        body = f'<h1>{e(title)}</h1><p class="sub">{e(s.get("sub",""))}</p>{lis(s.get("points", []))}'
    elif t == "bullets":
        body = f'<h2>{e(title)}</h2>' + lis(s["points"])
        if s.get("note"): body += f'<p class="note">{e(s["note"])}</p>'
    elif t == "glossary":
        body = f'<h2>{e(title)}</h2><dl>' + "".join(f"<dt>{e(a)}</dt><dd>{e(b)}</dd>" for a, b in s["terms"]) + "</dl>"
    elif t == "flow":
        cards = [f'<div class="card"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a, b in s["stages"]]
        body = f'<h2>{e(title)}</h2><div class="flow">' + '<div class="arrow">&rarr;</div>'.join(cards) + "</div>"
        if s.get("note"): body += f'<p class="note">{e(s["note"])}</p>'
    elif t == "table":
        head_cells = "".join(f"<th>{e(h)}</th>" for h in s["headers"])
        rows = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in s["rows"])
        body = f'<h2>{e(title)}</h2><table><thead><tr>{head_cells}</tr></thead><tbody>{rows}</tbody></table>'
        if s.get("note"): body += f'<p class="note">{e(s["note"])}</p>'
    elif t == "layers":
        body = f'<h2>{e(title)}</h2><div class="layer">' + "".join(f'<div class="card"><b>{e(a)}</b> &mdash; {e(b)}</div>' for a, b in s["layers"]) + "</div>"
    elif t == "code":
        try_html = f'<div class="try"><h3>Try it</h3>{lis(s["try"])}</div>' if s.get("try") else ""
        body = f'<h2>{e(title)}</h2><div class="cols"><pre><code>{e(s["code"])}</code></pre>{try_html}</div>'
        if s.get("note"): body += f'<p class="note">{e(s["note"])}</p>'
    elif t == "commands":
        body = f'<h2>{e(title)}</h2>' + "".join(f'<code class="cmd">{e(c)}</code>' for c in s["commands"]) + lis(s.get("points", []))
    elif t == "cards":
        body = f'<h2>{e(title)}</h2><div class="grid">' + "".join(
            f'<div class="card"><h3>{e(h)}</h3>' + "".join(f"<p>{e(p)}</p>" for p in ps) + "</div>" for h, ps in s["cards"]) + "</div>"
        if s.get("note"): body += f'<p class="note">{e(s["note"])}</p>'
    else:
        raise ValueError(f"unknown slide type {t}")
    foot = f'<div class="foot"><span>{e(meta["footer"])}</span><span>{n} / {total}</span></div>'
    return f'<section class="slide" id="s{n}" aria-label="Slide {n}">{head}{body}{foot}</section>'

def build(meta, slides, out):
    total = len(slides)
    sections = "\n".join(render_slide(s, i + 1, total, meta) for i, s in enumerate(slides))
    doc = f"""<!doctype html>
<html lang="en" class="no-js"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(meta["title"])}</title><style>{CSS}</style></head>
<body><div class="bar"></div>
<main class="deck">{sections}<div class="help">&larr; &rarr; navigate &middot; F fullscreen &middot; O overview &middot; print for PDF</div></main>
<script>var META_TITLE={meta["title"]!r};{JS}</script></body></html>
"""
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(doc, encoding="utf-8")
    return total

# ---- deck content ----
ROOT = Path(__file__).resolve().parents[1]
K = "Claude for Project Managers / GitHub Shop Edition"
META = {"title": "Claude for Project Managers: GitHub Shop Edition", "kicker": K, "footer": "Blake Matthews / Instructor-led workshop"}
SLIDES = [
 {"type": "title", "minutes": "2 min", "title": "Today: build your own PM workspace", "sub": "Find and understand work across GitHub repositories.",
  "points": ["Build a local, repeatable snapshot of issues, PRs and projects.", "Schedule refreshes and create your first Claude Artifact."]},
 {"type": "bullets", "minutes": "2 min", "title": "Who I am", "points": ["Former classroom educator and robotics coach", "Disney Experience Technology: AI engineering and technical product leadership", "Former Scale AI and Meta", "Built agentic tooling for engineering and enterprise AI enablement"]},
 {"type": "bullets", "minutes": "5 min", "title": "GitHub in five concepts", "points": ["Organization: the container for a team’s repositories.", "Repository: code, files and history.", "Issue: a work item; pull request: a proposed change.", "Project: a cross-repository planning view with custom fields.", "GitHub CLI (gh): a command-line interface to GitHub."]},
 {"type": "table", "minutes": "4 min", "title": "GitHub for Jira Pros", "headers": ["In Jira", "In GitHub"], "rows": [
  ["Project", "Repository holds the work. A GitHub Project is a planning view across repositories."],
  ["Epic", "Parent issue with sub-issues, or a milestone."],
  ["Story / Task / Bug", "Issue. Use labels or issue types to tell them apart."],
  ["Sprint", "Milestone, or an iteration field in a Project."],
  ["Board and workflow status", "Project Status field. The issue itself is only Open or Closed."],
  ["JQL", "Search filters: gh issue list --search, and Project view filters."],
  ["Dev panel, linked commits", "Pull request. \"Fixes #12\" links it and closes the issue on merge."]],
  "note": "Biggest surprise: \"In Progress\" is not on the issue. It lives in the Project, which is why our sync pulls both."},
 {"type": "layers", "minutes": "3 min", "title": "One workspace, three layers", "layers": [
  ("SOURCE", "GitHub repositories, issues, pull requests and Projects"), ("SYNC", "gh + make sync → local clones and data/snapshot.json"), ("VIEW", "Claude Cowork → Claude Artifact or another presentation layer")]},
 {"type": "commands", "minutes": "4 min", "kicker": K + " / Code along 01", "title": "Connect", "commands": ["gh auth login --scopes read:project", "gh auth status", "gh repo list YOUR-ORG", "gh project list --owner YOUR-ORG"]},
 {"type": "bullets", "minutes": "4 min", "kicker": K + " / Code along 02", "title": "Define the team", "points": ["Copy config.json to config.local.json.", "Choose team repositories and project numbers.", "For a project-free team, set projects to [].", "Keep the manifest scoped to approved repositories."]},
 {"type": "commands", "minutes": "4 min", "kicker": K + " / Code along 03", "title": "Synchronize", "commands": ["make sync"],
  "points": ["Inspect repos/OWNER/REPO/ to see cloned repositories.", "Open data/snapshot.json and find an issue and PR.", "If authentication is blocked: make sample."]},
 {"type": "bullets", "minutes": "4 min", "kicker": K + " / Code along 04", "title": "Automate", "points": ["Open Claude Cowork and select the local workspace.", "Create a weekday 8 AM scheduled task to run make sync.", "Run once manually and confirm the timestamp changed.", "If local execution is unavailable, use OS scheduling."]},
 {"type": "bullets", "minutes": "6 min", "kicker": K + " / Code along 05", "title": "Create an Artifact", "points": ["Ask Claude to use data/snapshot.json as its source.", "Show issue lists, PR review status and actual project fields.", "Add repo filters, source links and last-sync timestamp.", "Request JSON import so the dashboard can be refreshed."]},
 {"type": "cards", "minutes": "10 min", "kicker": K + " / Make it yours", "title": "Let Claude interview you", "cards": [
  ("You decide", ["What decision should your view support?", "Which repos, fields and filters matter to you?", "How should it look, and how fresh must it be?"]),
  ("Claude coaches", ["Asks one question at a time.", "Explains each file, then writes it with your approval.", "Read-only on GitHub; checks your understanding."])],
  "note": "Use the coach prompt in guided-build.md. Design against the demo data first, then switch to your real repos."},
 {"type": "bullets", "minutes": "3 min", "title": "Quick check-in", "points": ["Show your local snapshot and Artifact.", "Which system is the source of truth?", "What changes when make sync runs?", "If the Artifact is stale, which layer do you troubleshoot?"]},
 {"type": "bullets", "minutes": "2 min", "title": "What would you do next?", "points": ["For those who have done something similar: where could we take this?", "How would you extend it for a real team?", "What advice would you share from personal experience?"]},
 {"type": "cards", "minutes": "16 min", "title": "Your own project management tool", "cards": [
  ("EXTEND", ["Choose Excel, enhanced Artifact, HTML dashboard or another format.", "Pick one real PM question; make the view answer it."]),
  ("SUPPORT", ["Work with the instructor one-on-one or in a small group.", "Retry the core task independently after support."])]},
 {"type": "bullets", "minutes": "5 min", "title": "Share out", "points": ["What did you build?", "Show your view and the PM question it answers.", "Explain how you verify the data and refresh it.", "Name one next step for your own team."]},
]

if __name__ == "__main__":
    n = build(META, SLIDES, ROOT / "deck" / "index.html")
    print(f"Wrote deck/index.html ({n} slides)")
