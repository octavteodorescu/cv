#!/usr/bin/env python3
"""Render cv.yaml -> docs/index.html (+JSON-LD), docs/llms.txt, docs/CNAME, and ../octavteodorescu/README.md.

Single source of truth: cv.yaml. Edit it, run `python3 build.py`, every public surface updates.
Static-first: the HTML needs no JavaScript and no agent to convey the full CV.
`phone` is never rendered to any public surface.
"""
import html
import json
import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parent
DOCS = ROOT / "docs"
BUILD = ROOT / "build"
PROFILE_README = ROOT.parent / "octavteodorescu" / "README.md"
DOMAIN = "cv.oteelab.org"
SITE_URL = f"https://{DOMAIN}"

CV = yaml.safe_load((ROOT / "cv.yaml").read_text(encoding="utf-8"))
# Optional display fields default to empty so removing a line in cv.yaml never breaks the build.
for _k in ("availability", "tagline", "certifications_intro", "currently_building"):
    CV.setdefault(_k, "")
e = html.escape


def chips(items):
    return "".join(f'<li class="chip">{e(str(i))}</li>' for i in items)


# ---------------------------------------------------------------- HTML site
def render_html():
    c = CV
    focus = "".join(f"<li>{e(x)}</li>" for x in c["focus"])
    highlights = "".join(f"<li>{e(x)}</li>" for x in c["highlights"])

    exp = ""
    for j in c["experience"]:
        blist = j.get("bullets") or []
        bl = ""
        if blist:
            lis = "".join(f"<li>{e(b)}</li>" for b in blist)
            bl = f"<p class='bul-lead'>Selected highlights</p><ul class='bul'>{lis}</ul>"
        exp += f"""
        <article class="role">
          <div class="role-head">
            <h3>{e(j['role'])}</h3>
            <span class="role-co">{e(j['company'])}</span>
            <span class="role-dates">{e(j['dates'])}</span>
          </div>
          <p>{e(j['summary'])}</p>
          {bl}
        </article>"""

    indep = "".join(f"<li>{e(x)}</li>" for x in c["independent"]["items"])

    tech = ""
    for cat, items in c["tech"].items():
        tech += f"""
        <div class="tech-group">
          <h4>{e(cat)}</h4>
          <ul class="chips">{chips(items)}</ul>
        </div>"""

    certs = "".join(f"<li>{e(x)}</li>" for x in c["certifications"])
    cert_intro_html = f"<p class='cert-intro'>{e(c['certifications_intro'])}</p>" if c["certifications_intro"] else ""
    kicker_html = f'<span class="mono kicker">{e(c["availability"])}</span>' if c["availability"] else ""
    tagline_html = f'<p class="tagline">{e(c["tagline"])}</p>' if c["tagline"] else ""
    edu = "".join(f"<li>{e(x)}</li>" for x in c["education"])
    langs = "".join(f'<li class="chip">{e(x)}</li>' for x in c["languages"])

    links_nav = "".join(
        f'<a href="{e(url)}" rel="me noopener" target="_blank">{e(name)}</a>'
        for name, url in c["links"].items()
        if name != "Website"
    )

    jsonld = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": c["name"],
        "jobTitle": c["title"],
        "description": " ".join(c["profile"].split()),
        "email": f"mailto:{c['email']}",
        "url": SITE_URL,
        "address": {"@type": "PostalAddress", "addressLocality": "Bucharest", "addressCountry": "RO"},
        "sameAs": [c["links"]["LinkedIn"], c["links"]["GitHub"]],
        "knowsAbout": sorted({i for v in c["tech"].values() for i in v}),
        "alumniOf": "Academy of Economic Studies, Bucharest",
    }
    jsonld_s = json.dumps(jsonld, ensure_ascii=False, indent=2)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(c['name'])} - {e(c['title'])}</title>
<meta name="description" content="{e(' '.join(c['profile'].split())[:230])}">
<meta property="og:title" content="{e(c['name'])} - {e(c['title'])}">
<meta property="og:description" content="{e(c['tagline'])}">
<meta property="og:type" content="profile">
<meta property="og:url" content="{SITE_URL}">
<link rel="canonical" href="{SITE_URL}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,900&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<script type="application/ld+json">
{jsonld_s}
</script>
<style>
:root{{
  --bg:#0c0e11; --bg2:#121519; --ink:#e9e6df; --muted:#9aa0a8;
  --line:#23282f; --accent:#f0b429; --accent-dim:#7a5f1c;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{
  background:var(--bg); color:var(--ink);
  font-family:"IBM Plex Sans",system-ui,sans-serif; font-weight:300;
  line-height:1.5; font-size:17px; letter-spacing:.005em;
  background-image:radial-gradient(900px 500px at 78% -8%,rgba(240,180,41,.06),transparent 60%);
}}
body::before{{
  content:"";position:fixed;inset:0;pointer-events:none;z-index:1;opacity:.035;
  background-image:linear-gradient(var(--line) 1px,transparent 1px),linear-gradient(90deg,var(--line) 1px,transparent 1px);
  background-size:48px 48px;
}}
.wrap{{max-width:920px;margin:0 auto;padding:0 28px;position:relative;z-index:2}}
.mono{{font-family:"IBM Plex Mono",monospace;font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}}

/* hero */
header.hero{{padding:7vh 0 4vh;border-bottom:1px solid var(--line)}}
.kicker{{display:block;margin-bottom:1.6rem;animation:rise .7s both}}
h1{{
  font-family:"Fraunces",serif;font-weight:900;font-size:clamp(2.8rem,8vw,5.4rem);
  line-height:.96;letter-spacing:-.02em;color:#fff;animation:rise .7s .06s both;
}}
.title{{font-family:"Fraunces",serif;font-weight:400;font-style:italic;font-size:clamp(1.2rem,3vw,1.8rem);color:var(--accent);margin-top:.5rem;animation:rise .7s .12s both}}
.tagline{{font-size:1.15rem;color:var(--muted);max-width:46ch;margin-top:1rem;animation:rise .7s .18s both}}
.meta{{display:flex;flex-wrap:wrap;gap:.5rem 1.8rem;margin-top:1.5rem;animation:rise .7s .24s both;font-size:.9rem;color:var(--muted)}}
.meta b{{color:var(--ink);font-weight:500}}
nav.links{{display:flex;flex-wrap:wrap;gap:.9rem;margin-top:1.3rem;animation:rise .7s .3s both}}
nav.links a,.btn{{
  font-family:"IBM Plex Mono",monospace;font-size:.82rem;letter-spacing:.04em;
  color:var(--ink);text-decoration:none;border:1px solid var(--line);
  padding:.5rem .9rem;border-radius:2px;transition:.2s;
}}
nav.links a:hover,.btn:hover{{border-color:var(--accent);color:var(--accent);transform:translateY(-2px)}}
.btn{{background:var(--accent);color:#1a1206;border-color:var(--accent);font-weight:500}}
.btn:hover{{background:#ffc845;color:#1a1206}}

/* sections */
section{{padding:3.2vh 0;border-bottom:1px solid var(--line)}}
.s-head{{display:flex;align-items:baseline;gap:1rem;margin-bottom:1.3rem}}
.s-head h2{{font-family:"Fraunces",serif;font-weight:600;font-size:1.9rem;color:#fff;letter-spacing:-.01em}}
.s-head .num{{font-family:"IBM Plex Mono",monospace;color:var(--accent-dim);font-size:.85rem}}
p.lead{{font-size:1.12rem;max-width:64ch}}
ul.clean{{list-style:none;display:grid;gap:.65rem}}
ul.clean li{{position:relative;padding-left:1.5rem;max-width:72ch;color:var(--ink)}}
ul.clean li::before{{content:"";position:absolute;left:0;top:.62em;width:8px;height:8px;background:var(--accent);transform:rotate(45deg)}}

/* experience */
.role{{padding:1.1rem 0;border-top:1px dashed var(--line)}}
.role:first-of-type{{border-top:none}}
.role-head{{display:flex;flex-wrap:wrap;align-items:baseline;gap:.4rem 1rem;margin-bottom:.7rem}}
.role-head h3{{font-family:"IBM Plex Sans";font-weight:600;font-size:1.18rem;color:#fff}}
.role-co{{color:var(--accent);font-weight:500}}
.role-dates{{margin-left:auto;font-family:"IBM Plex Mono",monospace;font-size:.78rem;color:var(--muted)}}
.role p{{color:var(--muted);max-width:74ch}}
ul.bul{{list-style:none;margin-top:.9rem;display:grid;gap:.55rem}}
ul.bul li{{position:relative;padding-left:1.3rem;font-size:.96rem;max-width:78ch}}
ul.bul li::before{{content:"+";position:absolute;left:0;color:var(--accent);font-family:"IBM Plex Mono"}}
.bul-lead{{font-family:"IBM Plex Mono",monospace;font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:.2rem 0 .5rem}}
.cert-intro{{color:var(--muted);font-size:.92rem;margin-bottom:.7rem;max-width:62ch}}

/* independent - the differentiator, given weight */
#independent{{background:linear-gradient(180deg,rgba(240,180,41,.04),transparent)}}
.indep-intro{{font-style:italic;font-family:"Fraunces",serif;color:var(--ink);font-size:1.2rem;margin-bottom:1.8rem;max-width:60ch}}

/* tech */
.tech-group{{margin-bottom:1.6rem}}
.tech-group h4{{font-family:"IBM Plex Mono",monospace;font-size:.74rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:.7rem}}
ul.chips{{list-style:none;display:flex;flex-wrap:wrap;gap:.5rem}}
.chip{{font-family:"IBM Plex Mono",monospace;font-size:.78rem;border:1px solid var(--line);padding:.34rem .7rem;border-radius:2px;color:var(--ink);transition:.18s}}
.chip:hover{{border-color:var(--accent);color:var(--accent)}}

/* two-col small */
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:2.5rem}}
.cols h4{{font-family:"IBM Plex Mono",monospace;font-size:.74rem;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin-bottom:.9rem}}
.cols ul{{list-style:none;display:grid;gap:.5rem}}
.cols li{{font-size:.94rem;color:var(--ink)}}

footer{{padding:6vh 0 8vh;text-align:center}}
footer .mono{{color:var(--muted)}}
footer h2{{font-family:"Fraunces",serif;font-style:italic;font-weight:400;font-size:1.6rem;color:#fff;margin:.8rem 0 1.8rem}}
.foot-links{{display:flex;justify-content:center;flex-wrap:wrap;gap:.9rem}}

@keyframes rise{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
@media(max-width:640px){{.cols{{grid-template-columns:1fr}} .role-dates{{margin-left:0}}}}
@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}

/* PRINT: clean light A4, compact (~3pp), no dark ink, no chrome */
@page{{margin:12mm 13mm}}
@media print{{
  :root{{--bg:#fff;--bg2:#fff;--ink:#1a1a1a;--muted:#555;--line:#d4d4d4;--accent:#9a6b00;--accent-dim:#9a6b00}}
  body{{background:#fff;color:#1a1a1a;font-size:9.3pt;line-height:1.3;letter-spacing:0}}
  body::before,nav.links,.btn,footer .foot-links,.tagline{{display:none!important}}
  .wrap{{max-width:none;padding:0}}
  .kicker{{margin-bottom:.3rem;font-size:.62rem}}
  h1{{color:#000;font-size:20pt;line-height:1}} .title{{color:#000;font-size:11pt;margin-top:.1rem}}
  .meta{{margin-top:.5rem;gap:.2rem 1.2rem;font-size:8.6pt}}
  header.hero{{padding:0 0 7pt}}
  section{{padding:7pt 0;border-color:#e0e0e0;break-inside:avoid}}
  .s-head{{margin-bottom:.5rem}} .s-head h2{{font-size:13pt;color:#000}}
  p.lead{{font-size:9.3pt}}
  ul.clean{{gap:.28rem}} ul.clean li{{padding-left:1rem}} ul.clean li::before{{width:5px;height:5px;top:.5em}}
  .role{{padding:.5rem 0;break-inside:avoid}} .role-head{{margin-bottom:.2rem}}
  .role-head h3{{font-size:10pt;color:#000}} .role p{{font-size:9pt}}
  ul.bul{{margin-top:.35rem;gap:.2rem}} ul.bul li{{font-size:8.8pt;padding-left:1rem}}
  .indep-intro{{font-size:10pt;margin-bottom:.6rem}}
  .tech-group{{margin-bottom:.6rem}} .tech-group h4,.cols h4{{margin-bottom:.3rem}}
  .chip{{border-color:#bbb;padding:.12rem .4rem;font-size:8pt}}
  .cols{{gap:1.4rem}} .cols li{{font-size:8.8pt}}
  #independent{{background:none}}
  footer{{padding:8pt 0 0;text-align:left}} footer h2{{font-size:11pt;margin:.2rem 0}}
  a{{color:#000;text-decoration:none}}
}}
</style>
</head>
<body>
<div class="wrap">

  <header class="hero">
    {kicker_html}
    <h1>{e(c['name'])}</h1>
    <div class="title">{e(c['title'])}</div>
    {tagline_html}
    <div class="meta">
      <span><b>Based in</b> {e(c['location'])}</span>
      <span><b>Email</b> <a href="mailto:{e(c['email'])}" style="color:inherit">{e(c['email'])}</a></span>
    </div>
    <nav class="links">
      {links_nav}
      <a class="btn" href="cv.pdf">Download PDF</a>
      <a href="cv.docx">Word version</a>
    </nav>
  </header>

  <section id="profile">
    <div class="s-head"><span class="num">01</span><h2>Profile</h2></div>
    <p class="lead">{e(c['profile'])}</p>
  </section>

  <section id="focus">
    <div class="s-head"><span class="num">02</span><h2>What I focus on</h2></div>
    <ul class="clean">{focus}</ul>
  </section>

  <section id="highlights">
    <div class="s-head"><span class="num">03</span><h2>Selected highlights</h2></div>
    <ul class="clean">{highlights}</ul>
  </section>

  <section id="experience">
    <div class="s-head"><span class="num">04</span><h2>Experience</h2></div>
    {exp}
  </section>

  <section id="independent">
    <div class="s-head"><span class="num">05</span><h2>Independent AI engineering</h2></div>
    <p class="indep-intro">{e(c['independent']['intro'])}</p>
    <ul class="clean">{indep}</ul>
  </section>

  <section id="tech">
    <div class="s-head"><span class="num">06</span><h2>Technology</h2></div>
    {tech}
  </section>

  <section id="more">
    <div class="cols">
      <div><h4>Certifications &amp; learning</h4>{cert_intro_html}<ul>{certs}</ul></div>
      <div>
        <h4>Education</h4><ul>{edu}</ul>
        <h4 style="margin-top:1.6rem">Languages</h4><ul class="chips">{langs}</ul>
      </div>
    </div>
  </section>

  <footer>
    <span class="mono">Currently building</span>
    <h2>{e(c['currently_building'])}</h2>
    <div class="foot-links">
      {links_nav}
      <a class="btn" href="mailto:{e(c['email'])}">Say hello</a>
    </div>
  </footer>

</div>
</body>
</html>"""


# ---------------------------------------------------------------- llms.txt
def render_llms():
    c = CV
    lines = [
        f"# {c['name']}",
        f"> {c['title']}. {c['tagline']}",
        "",
        " ".join(c["profile"].split()),
        "",
        f"Location: {c['location']}." + (f" {c['availability']}." if c['availability'] else ""),
        f"Contact: {c['email']}",
        f"LinkedIn: {c['links']['LinkedIn']}",
        f"GitHub: {c['links']['GitHub']}",
        "",
        "## Focus",
        *[f"- {x}" for x in c["focus"]],
        "",
        "## Experience",
        *[f"- {j['role']}, {j['company']} ({j['dates']})" for j in c["experience"]],
        "",
        "## Independent AI engineering",
        *[f"- {x}" for x in c["independent"]["items"]],
        "",
        "## Certifications",
        *[f"- {x}" for x in c["certifications"]],
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- profile README
def skill_badge(label):
    enc = label.replace("-", "--").replace(" ", "_")
    return f"![{label}](https://img.shields.io/badge/{enc}-0c0e11?style=flat-square&labelColor=0c0e11&color=f0b429)"


def render_readme():
    c = CV
    skills = ["AI Agents", "Multi-Agent Systems", "MCP", "RAG", "LLM Apps",
              "Fine-tuning (LoRA/QLoRA)", "Python", "Solution Architecture", "Azure/AWS/GCP"]
    skill_badges = " ".join(skill_badge(s) for s in skills)
    links = (f"[Website]({c['links']['Website']}) &middot; "
             f"[LinkedIn]({c['links']['LinkedIn']}) &middot; "
             f"[GitHub]({c['links']['GitHub']})")
    focus_short = "\n".join(f"- {x.split(':')[0]}" for x in c["focus"])
    avail = f" &nbsp;|&nbsp; {c['availability']}" if c["availability"] else ""
    return f"""## Hi, I'm Octavian

**{c['title']}** &nbsp;|&nbsp; Bucharest{avail}

{skill_badges}

{' '.join(c['profile'].split())}

**Currently building:** {c['currently_building']}

### What I focus on
{focus_short}

### Selected write-ups
- [mcp-second-brain](https://github.com/octavteodorescu/mcp-second-brain) - a personal MCP server over my own knowledge base
- [daily-intel-brief](https://github.com/octavteodorescu/daily-intel-brief) - an autonomous daily AI intelligence-brief agent
- [cv](https://github.com/octavteodorescu/cv) - the source for {c['links']['Website']} (single `cv.yaml` renders every surface)

### Find me
{links}

<sub>This profile is generated from a single source (`cv.yaml`) that also renders my CV site at {c['links']['Website']}. Edit once, every surface updates.</sub>
"""


# ---------------------------------------------------------------- CV document markdown (-> pandoc docx, public, no phone)
def render_cv_markdown():
    c = CV
    o = [f"# {c['name']}", "", f"**{c['title']}**", ""]
    o.append(c["location"] + (f" - {c['availability']}" if c["availability"] else "") + "  ")
    o.append(f"{c['email']} | {c['links']['Website']} | {c['links']['LinkedIn']} | {c['links']['GitHub']}")
    o += ["", "## Profile", "", " ".join(c["profile"].split()), "", "## What I focus on", ""]
    o += [f"- {x}" for x in c["focus"]]
    o += ["", "## Selected highlights", ""]
    o += [f"- {x}" for x in c["highlights"]]
    o += ["", "## Experience", ""]
    for j in c["experience"]:
        o += [f"### {j['role']}", "", f"**{j['company']}** | {j['dates']}", "", " ".join(j["summary"].split()), ""]
        bl = j.get("bullets") or []
        if bl:
            o += ["*Selected highlights:*", ""]
            o += [f"- {b}" for b in bl]
        o += [""]
    o += ["## Independent AI engineering and applied R&D", "", " ".join(c["independent"]["intro"].split()), ""]
    o += [f"- {x}" for x in c["independent"]["items"]]
    o += ["", "## Technology", ""]
    o += [f"- **{cat}:** " + ", ".join(items) for cat, items in c["tech"].items()]
    o += ["", "## Certifications and learning", ""]
    if c["certifications_intro"]:
        o += [c["certifications_intro"], ""]
    o += [f"- {x}" for x in (c.get("certifications_detail") or c["certifications"])]
    o += ["", "## Education", ""]
    o += [f"- {x}" for x in c["education"]]
    o += ["", "## Languages", "", ", ".join(c["languages"]), ""]
    # ---- Part 2: documents only (website renderer never reads these keys) ----
    if c.get("technical_proficiencies"):
        o += ["## Technical proficiencies", ""]
        o += [f"- **{k}:** {v}" for k, v in c["technical_proficiencies"].items()]
        o += [""]
    if c.get("courses"):
        o += ["## Courses and training", ""]
        o += [f"- {x}" for x in c["courses"]]
        o += [""]
    if c.get("detailed_experience"):
        de = c["detailed_experience"]
        o += ["## Detailed professional experience", "", " ".join(de["intro"].split()), ""]
        for it in de["items"]:
            o += [f"### {it['context']}", "", " ".join(it["detail"].split()), ""]
    return "\n".join(o) + "\n"


# ---------------------------------------------------------------- LinkedIn copy (rendered HTML page with per-block copy buttons)
def render_linkedin_html():
    c = CV
    li = c.get("linkedin") or {}
    headline = li.get("headline", "")
    about = (li.get("about", "") or "").strip()
    top_skills = li.get("top_skills", [])
    skills = li.get("skills", [])

    def block(idx, label, limit, text):
        n = len(text)
        over = " over" if (limit and n > limit) else ""
        lim = f"{n}/{limit}" if limit else f"{n} chars"
        return f"""<section>
      <div class="bhead"><h2>{e(label)}</h2><span class="count{over}">{lim}</span>
        <button class="copy" data-t="t{idx}">Copy</button></div>
      <pre id="t{idx}">{e(text)}</pre>
    </section>"""

    blocks = [block(0, "Headline", 220, headline), block(1, "About", 2600, about)]
    for i, j in enumerate(c["experience"], start=2):
        body = " ".join(j["summary"].split())
        bl = j.get("bullets") or []
        if bl:
            body += "\n\n" + "\n".join(f"- {b}" for b in bl)
        blocks.append(block(i, f"{j['role']} - {j['company']} ({j['dates']})", 2000, body))
    if top_skills:
        blocks.append(block(98, "Top 5 skills (About picker + top of Skills section)", 0, "\n".join(top_skills)))
    blocks.append(block(99, "All skills (Skills section, up to 50)", 0, "\n".join(skills)))
    body_html = "\n".join(blocks)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>LinkedIn copy - {e(c['name'])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{{--bg:#0c0e11;--ink:#e9e6df;--muted:#9aa0a8;--line:#23282f;--accent:#f0b429}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans",system-ui,sans-serif;font-weight:300;line-height:1.5;padding:5vh 6vw;max-width:880px;margin:0 auto}}
h1{{font-size:1.8rem;font-weight:500;margin-bottom:.3rem}}
.intro{{color:var(--muted);margin-bottom:2.2rem}}
.intro a{{color:var(--accent)}}
section{{border-top:1px solid var(--line);padding:1.3rem 0}}
.bhead{{display:flex;align-items:center;gap:.8rem;margin-bottom:.7rem;flex-wrap:wrap}}
.bhead h2{{font-size:1rem;font-weight:500}}
.count{{font-family:"IBM Plex Mono",monospace;font-size:.74rem;color:var(--muted)}}
.count.over{{color:#ff6b6b}}
.copy{{margin-left:auto;font-family:"IBM Plex Mono",monospace;font-size:.74rem;letter-spacing:.04em;background:var(--accent);color:#1a1206;border:0;border-radius:3px;padding:.35rem .8rem;cursor:pointer;transition:.15s}}
.copy:hover{{background:#ffc845}}
pre{{font-family:"IBM Plex Mono",monospace;font-size:.82rem;line-height:1.55;white-space:pre-wrap;word-break:break-word;background:#121519;border:1px solid var(--line);border-radius:4px;padding:1rem;color:var(--ink)}}
</style>
</head>
<body>
  <h1>LinkedIn copy</h1>
  <p class="intro">Generated from <code>cv.yaml</code>. Click <b>Copy</b> on any block and paste it into the matching LinkedIn field. Counts are checked against LinkedIn's 2026 limits. Back to <a href="/">the site</a>.</p>
  {body_html}
<script>
document.querySelectorAll(".copy").forEach(function(b){{
  b.addEventListener("click",function(){{
    var el=document.getElementById(b.dataset.t);
    navigator.clipboard.writeText(el.textContent).then(function(){{
      var o=b.textContent; b.textContent="Copied"; setTimeout(function(){{b.textContent=o;}},1200);
    }});
  }});
}});
</script>
</body>
</html>"""


def main():
    DOCS.mkdir(exist_ok=True)
    BUILD.mkdir(exist_ok=True)
    (DOCS / "index.html").write_text(render_html(), encoding="utf-8")
    (DOCS / "llms.txt").write_text(render_llms(), encoding="utf-8")
    (DOCS / "linkedin.html").write_text(render_linkedin_html(), encoding="utf-8")
    (DOCS / "CNAME").write_text(DOMAIN + "\n", encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (BUILD / "cv.md").write_text(render_cv_markdown(), encoding="utf-8")
    # profile README lives in a sibling repo; only write it when that checkout is present (skipped in CI)
    if PROFILE_README.parent.is_dir():
        PROFILE_README.write_text(render_readme(), encoding="utf-8")
        wrote_readme = "profile README.md"
    else:
        wrote_readme = "(profile repo absent, README skipped)"
    print(f"built: docs/index.html, docs/llms.txt, docs/CNAME, docs/.nojekyll, build/cv.md, {wrote_readme}")


if __name__ == "__main__":
    main()
