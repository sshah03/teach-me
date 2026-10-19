#!/usr/bin/env python3
"""Builds the teach-me page from a lesson file.

usage: build_page.py <lessons.json> [--standalone] [--check] > page.html

lessons.json holds the page title, where the lessons come from, and the list of lesson files, one per concept (the
format is in references/lesson.md). A figure is an HTML file next to lessons.json, named by the lesson's "figure.file".

By default the output is the page body for an Artifact, which wraps it in its own document. With --standalone
it's a complete HTML file to open in a browser. With --check, the page also runs a layout check on every figure, at
its own width and at 380px, and lists what it finds (overlapping or cut-off text, text too small to read, a figure
wider than its frame) in a box at the top, with id "layout-report".
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")


def esc(s):
    return html.escape(s or "", quote=True)


def inline(s):
    """`code`, **bold** and [text](https://url), on escaped text."""
    s = esc(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\[([^\]]+)\]\((https://[^)\s]+)\)", r'<a href="\2">\1</a>', s)
    return s


def blocks(text):
    """Paragraphs split by blank lines; lines starting with "- " make a list, even right after a paragraph line."""
    out = []
    for part in re.split(r"\n\s*\n", (text or "").strip()):
        para, items = [], []
        def flush():
            if para:
                out.append(f"<p>{inline(' '.join(para))}</p>")
                para.clear()
            if items:
                out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>")
                items.clear()
        for line in (l.strip() for l in part.splitlines() if l.strip()):
            if line.startswith("- "):
                if para:
                    flush()
                items.append(line[2:])
            else:
                if items:
                    flush()
                para.append(line)
        flush()
    return "".join(out)


def phone_problems(src):
    """What a phone-width reader would trip over, found without a browser. On a phone the figure is about
    350px wide, so an SVG drawn wider than about 480 units shrinks its 12px text below about 9px."""
    out = []
    for m in re.finditer(r'<svg\b[^>]*viewBox\s*=\s*["\']\s*[-\d.]+[ ,]+[-\d.]+[ ,]+([\d.]+)', src):
        width = float(m.group(1))
        if width > 480:
            out.append(f"an SVG is drawn {width:.0f} units wide, so on a phone its text shows at about "
                       f"{12 * 350 / width:.0f}px. Give narrow screens their own layout (stack the parts, or a "
                       "narrower viewBox chosen in script), or draw that part in HTML so it reflows.")
            break
    if re.search(r'viewBox["\'\s=:,]+["\']?\s*["\']\s*\+', src) or "setAttribute('viewBox'" in src or 'setAttribute("viewBox"' in src:
        out = []  # the script picks its own viewBox, likely by width
    return out


def lesson_html(i, l, figures, concept_mode=False, next_title=None):
    """One lesson's section. Built from small pieces, so it runs on older Pythons (3.8 and up)."""
    f = l.get("figure") or {}
    fig = ""
    if f.get("file") in figures:
        caption = " <span>" + inline(f.get("caption")) + "</span>" if f.get("caption") else ""
        fig = (
            '\n      <figure class="fig">'
            "\n        <figcaption><b>" + esc(f.get("title")) + "</b>" + caption + "</figcaption>"
            '\n        <iframe class="frame" sandbox="allow-scripts" data-figure="' + esc(f["file"]) + '" title="'
            + esc(f.get("title")) + '" loading="lazy"></iframe>'
            "\n      </figure>"
        )
    takeaways = "".join("<li>" + inline(t) + "</li>" for t in l.get("takeaways") or [])
    sources = "".join(
        '<li><a href="' + esc(s["url"]) + '">' + esc(s.get("title") or s["url"]) + "</a></li>"
        for s in l.get("sources") or [] if str(s.get("url", "")).startswith("https://")
    )
    quiz = l.get("quiz") or []
    questions = ""
    for q in quiz:
        choices = "".join(
            '<button type="button" class="choice" data-i="' + str(j) + '">' + inline(c) + "</button>"
            for j, c in enumerate(q.get("choices") or [])
        )
        questions += (
            '\n        <div class="q" data-answer="' + str(int(q.get("answer", 0))) + '">'
            '\n          <p class="qtext">' + inline(q.get("question")) + "</p>"
            '\n          <div class="choices">' + choices + "</div>"
            '\n          <p class="why" hidden>' + inline(q.get("explanation")) + "</p>"
            "\n        </div>"
        )
    n = len(quiz)
    plural = "question" if n == 1 else "questions"
    change = l.get("in_this_change")
    change_label = "Where you will see it" if concept_mode else "In this change"
    next_btn = (
        '<button type="button" class="next" data-go="c' + str(i + 2) + '">Next: ' + inline(next_title) + "</button>"
        if next_title else ""
    )
    tabs = ""
    to_quiz = ""
    quiz_pane = ""
    if questions:
        tabs = (
            '\n      <div class="tabs" role="tablist">'
            '\n        <button type="button" class="tab on" role="tab" aria-selected="true" data-tab="lesson">Lesson</button>'
            '\n        <button type="button" class="tab" role="tab" aria-selected="false" data-tab="quiz">Quiz <span class="count">'
            + str(n) + "</span></button>"
            "\n      </div>"
        )
        to_quiz = '<button type="button" class="toquiz" data-tab="quiz">Take the quiz: ' + str(n) + " " + plural + "</button>"
        quiz_pane = (
            '<div class="pane quiz" data-pane="quiz" hidden><p class="qintro">' + str(n) + " " + plural
            + " on this lesson. Pick an answer to see why it is right or wrong.</p>" + questions
            + '<p class="score" aria-live="polite"></p><div class="endrow">'
            + '<button type="button" class="toquiz back" data-tab="lesson">Back to the lesson</button>' + next_btn + "</div></div>"
        )
    parts = [
        '\n    <section class="lesson" id="c' + str(i + 1) + '">',
        '\n      <header class="lhead">',
        '\n        <span class="kind">' + esc(l.get("kind")) + "</span>",
        "\n        <h2>" + inline(l.get("title")) + "</h2>",
        '\n        <p class="whyhere">' + inline(l.get("why_here")) + "</p>" if l.get("why_here") else "",
        "\n      </header>" + tabs,
        '\n      <div class="pane" data-pane="lesson">',
        '\n        <p class="tldr">' + inline(l.get("tldr")) + "</p>" + fig,
        '\n        <div class="intuition">' + blocks(l.get("intuition")) + "</div>" if l.get("intuition") else "",
        '\n        <div class="explanation">' + blocks(l.get("explanation")) + "</div>",
        '\n        <div class="card change"><div class="label">' + change_label + "</div>" + blocks(change) + "</div>" if change else "",
        '\n        <div class="card"><div class="label">Takeaways</div><ul>' + takeaways + "</ul></div>" if takeaways else "",
        '\n        <div class="sources"><div class="label">Read more</div><ul>' + sources + "</ul></div>" if sources else "",
        '\n        <div class="endrow">' + to_quiz + next_btn + "</div>",
        "\n      </div>",
        "\n      " + quiz_pane,
        "\n    </section>",
    ]
    return "".join(parts)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    standalone = "--standalone" in sys.argv
    check = "--check" in sys.argv
    if not args:
        sys.exit(__doc__)
    path = args[0]
    base = os.path.dirname(os.path.abspath(path))
    data = json.loads(read(path))
    # Each lesson is its own file (lesson-c1.json…), or written inline.
    lessons = [json.loads(read(os.path.join(base, l))) if isinstance(l, str) else l for l in data.get("lessons") or []]
    figures = {}
    for l in lessons:
        f = (l.get("figure") or {}).get("file")
        if f:
            p = os.path.join(base, f)
            if os.path.exists(p):
                figures[f] = read(p)
            else:
                print(f"warning: figure {f} not found, leaving it out", file=sys.stderr)
    for name, src in figures.items():
        for problem in phone_problems(src):
            print(f"warning: {name}: {problem}", file=sys.stderr)
    kit_css = read(os.path.join(ASSETS, "kit.css"))
    kit_js = read(os.path.join(ASSETS, "kit.js"))
    lint_js = read(os.path.join(ASSETS, "lint.js")) if check else ""
    src = data.get("source") or {}
    src_line = ""
    if src.get("label"):
        label = f'<a href="{esc(src["url"])}">{esc(src["label"])}</a>' if str(src.get("url", "")).startswith("https://") else esc(src["label"])
        pr_title = " <span>" + inline(src.get("title")) + "</span>" if src.get("title") else ""
        src_line = '<p class="src">' + label + pr_title + "</p>"
    toc = ""
    if len(lessons) > 1:
        toc = '<nav class="cnav" aria-label="Concepts">' + "".join(
            '<button type="button" data-go="c' + str(i + 1) + '"><span>' + str(i + 1) + "</span>" + inline(l.get("title")) + "</button>"
            for i, l in enumerate(lessons)) + "</nav>"
    title = data.get("title") or "teach-me"
    # A "</" inside the JSON would end the script tag early.
    figures_json = json.dumps(figures).replace("</", "<\\/")
    kit_json = json.dumps({"css": kit_css, "js": kit_js, "lint": lint_js}).replace("</", "<\\/")
    intro = '<p class="intro">' + inline(data.get("intro")) + "</p>" if data.get("intro") else ""
    footer = ("Lessons written with Claude and checked against how it works. " if data.get("mode") == "concept"
              else "Lessons written with Claude and checked against the code. ") + "Figures run in a sandboxed frame."
    sections = "".join(
        lesson_html(i, l, figures, data.get("mode") == "concept", lessons[i + 1].get("title") if i + 1 < len(lessons) else None)
        for i, l in enumerate(lessons))
    body = f"""<title>{esc(title)}</title>
<style>
:root {{ --bg: #ffffff; --bg-alt: #f5f7fa; --fg: #16191d; --fg-2: #3f4852; --fg-muted: #66717e; --border: #d9e0e8;
  --accent: #0b63d1; --accent-soft: #e4eefb; --good: #1a7f37; --good-soft: #e5f4ea; --bad: #c62a2f; --bad-soft: #fbe9ea; --warn: #9a6700;
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: #0d1117; --bg-alt: #151b23; --fg: #e6edf3; --fg-2: #c2ccd6;
  --fg-muted: #8b98a6; --border: #262f3a; --accent: #58a6ff; --accent-soft: #58a6ff1f; --good: #3fb950; --good-soft: #3fb9501f; --bad: #f85149;
  --bad-soft: #f851491f; --warn: #d29922; color-scheme: dark; }} }}
:root[data-theme="dark"] {{ --bg: #0d1117; --bg-alt: #151b23; --fg: #e6edf3; --fg-2: #c2ccd6; --fg-muted: #8b98a6; --border: #262f3a;
  --accent: #58a6ff; --accent-soft: #58a6ff1f; --good: #3fb950; --good-soft: #3fb9501f; --bad: #f85149; --bad-soft: #f851491f; --warn: #d29922; color-scheme: dark; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--fg); font: 15px/1.6 var(--font); }}
.page {{ max-width: 820px; margin: 0 auto; padding-inline: 16px; padding-block: 36px 64px; }}
a {{ color: var(--accent); }}
code {{ font-family: var(--mono); font-size: 0.88em; background: var(--bg-alt); border: 1px solid var(--border); border-radius: 5px; padding: 0.05em 0.35em; overflow-wrap: anywhere; }}
.top h1 {{ font-size: clamp(26px, 4vw, 34px); line-height: 1.15; letter-spacing: -0.02em; margin: 0 0 8px; text-wrap: balance; }}
.src {{ margin: 0; color: var(--fg-muted); font-size: 14px; }}
.src a {{ font-family: var(--mono); font-size: 13px; }}
.src span {{ margin-left: 6px; }}
.intro {{ color: var(--fg-2); margin: 12px 0 0; max-width: 68ch; }}
.cnav {{ position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; display: flex; gap: 6px; overflow-x: auto; margin: 22px -16px 0; padding: 10px 16px; background: var(--bg); border-bottom: 1px solid var(--border); }}
.cnav button {{ flex: none; display: flex; gap: 8px; align-items: baseline; max-width: 300px; font: inherit; font-size: 14px; color: var(--fg-2); background: var(--bg); border: 1px solid var(--border); border-radius: 999px; padding: 5px 14px; cursor: pointer; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.cnav button:hover {{ color: var(--fg); border-color: var(--fg-muted); }}
.cnav button.on {{ color: var(--accent); border-color: var(--accent); background: var(--accent-soft); }}
@media (max-width: 500px) {{ .cnav button {{ max-width: 72vw; }} }}
.cnav span {{ font-size: 12px; color: var(--fg-muted); font-variant-numeric: tabular-nums; }}
.cnav button.on span {{ color: var(--accent); }}
.endrow {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px; }}
.endrow .toquiz {{ margin-top: 0; }}
.next {{ font: inherit; font-size: 14px; font-weight: 500; color: var(--fg-2); background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 9px 16px; cursor: pointer; }}
.next:hover {{ color: var(--fg); border-color: var(--fg-muted); }}
.totop {{ position: fixed; right: 16px; bottom: calc(16px + env(safe-area-inset-bottom, 0px)); z-index: 6; font: inherit; font-size: 13px; font-weight: 500; color: var(--fg-2); background: var(--bg); border: 1px solid var(--border); border-radius: 999px; padding: 8px 14px; cursor: pointer; box-shadow: 0 2px 8px rgb(0 0 0 / 0.08); }}
.totop:hover {{ color: var(--fg); border-color: var(--fg-muted); }}
.cnav button:focus-visible, .next:focus-visible, .totop:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
.lesson {{ padding-top: 28px; }}
.kind {{ display: inline-block; font-size: 12px; font-weight: 600; color: var(--accent); background: var(--accent-soft); border-radius: 6px; padding: 1px 8px; }}
.lhead h2 {{ font-size: 24px; line-height: 1.25; letter-spacing: -0.015em; margin: 8px 0 6px; text-wrap: balance; }}
.whyhere {{ margin: 0; color: var(--fg-muted); font-size: 14px; max-width: 70ch; }}
.tldr {{ font-size: 17px; font-weight: 500; margin: 18px 0; max-width: 68ch; text-wrap: pretty; }}
.fig {{ margin: 0 0 20px; border: 1px solid var(--border); border-radius: 12px; overflow: hidden; background: var(--bg); }}
.fig figcaption {{ display: flex; flex-wrap: wrap; gap: 2px 10px; padding: 9px 14px; font-size: 13px; color: var(--fg-muted); border-bottom: 1px solid var(--border); background: var(--bg-alt); }}
.fig figcaption b {{ color: var(--fg); font-weight: 600; }}
.frame {{ display: block; width: 100%; height: 420px; border: 0; background: transparent; }}
.intuition, .explanation {{ max-width: 68ch; }}
.intuition {{ color: var(--fg-2); }}
.intuition p, .explanation p {{ margin: 0 0 12px; }}
.explanation ul, .card ul, .sources ul {{ margin: 0 0 12px; padding-left: 20px; }}
.card {{ border: 1px solid var(--border); border-radius: 10px; padding: 12px 16px; margin: 16px 0; }}
.card p {{ margin: 0 0 8px; }} .card p:last-child, .card ul:last-child {{ margin-bottom: 0; }}
.card.change {{ border-left: 3px solid var(--accent); }}
.label {{ font-size: 13px; font-weight: 600; color: var(--fg-muted); margin-bottom: 6px; }}
.tabs {{ display: flex; gap: 4px; margin: 18px 0 4px; border-bottom: 1px solid var(--border); }}
.tab {{ font: inherit; font-size: 14px; font-weight: 500; color: var(--fg-muted); background: none; border: 0; border-bottom: 2px solid transparent; padding: 8px 12px; margin-bottom: -1px; cursor: pointer; }}
.tab:hover {{ color: var(--fg); }}
.tab.on {{ color: var(--fg); border-bottom-color: var(--accent); }}
.tab .count {{ display: inline-block; min-width: 20px; font-size: 12px; font-weight: 600; color: var(--accent); background: var(--accent-soft); border-radius: 999px; padding: 0 6px; margin-left: 4px; text-align: center; }}
.tab .count.done {{ color: var(--good); background: var(--good-soft); }}
.tab:focus-visible, .toquiz:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
.toquiz {{ font: inherit; font-size: 14px; font-weight: 600; color: var(--accent); background: var(--accent-soft); border: 0; border-radius: 8px; padding: 9px 16px; margin-top: 20px; cursor: pointer; }}
.toquiz.back {{ color: var(--fg-2); background: var(--bg-alt); font-weight: 500; }}
.quiz {{ padding-top: 14px; }}
.qintro {{ margin: 0 0 14px; color: var(--fg-muted); font-size: 14px; }}
.score {{ font-weight: 600; color: var(--fg-2); margin: 4px 0 0; }}
.score.all {{ color: var(--good); }}
.q {{ border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; margin-bottom: 12px; }}
.qtext {{ margin: 0 0 10px; font-weight: 500; }}
.choices {{ display: grid; gap: 6px; }}
.choice {{ text-align: left; font: inherit; font-size: 14px; color: var(--fg); background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 8px 12px; cursor: pointer; }}
.choice:hover:not(:disabled) {{ border-color: var(--accent); }}
.choice:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
.choice:disabled {{ cursor: default; }}
.choice.right {{ border-color: var(--good); background: var(--good-soft); }}
.choice.wrong {{ border-color: var(--bad); background: var(--bad-soft); }}
.why {{ margin: 10px 0 0; font-size: 14px; color: var(--fg-2); }}
.sources {{ font-size: 14px; margin-top: 20px; }}
footer {{ margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--border); font-size: 13px; color: var(--fg-muted); }}
</style>
<div class="page">
  {'<pre id="layout-report" style="white-space:pre-wrap;font:12px/1.5 var(--mono);border:1px dashed var(--warn);border-radius:8px;padding:10px;margin:0 0 20px">Checking layout…</pre>' if check else ''}
  <header class="top">
    <h1>{inline(title)}</h1>
    {src_line}
    {intro}
  </header>
  {toc}
  {sections}
  <button type="button" class="totop" hidden>Back to top</button>
  <footer>{footer}</footer>
</div>
<script type="application/json" id="figures">{figures_json}</script>
<script type="application/json" id="kit">{kit_json}</script>
<script>
(() => {{
  const figures = JSON.parse(document.getElementById('figures').textContent);
  const kit = JSON.parse(document.getElementById('kit').textContent);
  // The figure gets the page's colors as the kit's variables, so it follows the theme.
  const doc = src => {{
    const cs = getComputedStyle(document.documentElement), v = n => cs.getPropertyValue(n).trim();
    const vars = ['--bg', '--bg-alt', '--fg', '--fg-muted', '--border', '--accent', '--good', '--bad', '--warn', '--font', '--mono'].map(n => n + ':' + v(n)).join(';');
    const scheme = cs.colorScheme && cs.colorScheme.includes('dark') ? 'dark' : 'light';
    const head = '<!doctype html><html><head><meta charset="utf-8"><style>:root{{color-scheme:' + scheme + ';' + vars + '}}html,body{{margin:0;background:transparent;color:var(--fg);font:13px/1.45 var(--font)}}\\n' + kit.css + '</style><script>' + kit.js + '<\\/script></head>';
    const sizer = '<script>(()=>{{const post=()=>parent.postMessage({{learnFrameHeight:Math.ceil(document.documentElement.getBoundingClientRect().height)}},"*");new ResizeObserver(post).observe(document.documentElement);addEventListener("load",post);post();}})()<\\/script>';
    const lint = kit.lint ? '<script>' + kit.lint + '<\\/script>' : '';
    return head.replace('</head>', lint + '</head>') + src.replace(/^\\s*<!doctype[^>]*>/i, '') + sizer;
  }};
  // With --check: every figure is also drawn off screen at 380px, and each frame's layout check is listed.
  const report = document.getElementById('layout-report');
  if (report) {{
    const found = {{}}, frames = [...document.querySelectorAll('iframe[data-figure]')];
    frames.forEach(f => {{
      const phone = document.createElement('iframe');
      phone.setAttribute('sandbox', 'allow-scripts'); phone.dataset.phone = f.dataset.figure;
      phone.style.cssText = 'position:fixed;left:-10000px;top:0;width:380px;height:900px;border:0;opacity:0';
      document.body.appendChild(phone);
    }});
    addEventListener('message', e => {{
      const p = e.data && e.data.layoutProblems;
      if (!Array.isArray(p)) return;
      const f = [...document.querySelectorAll('iframe[data-figure], iframe[data-phone]')].find(x => x.contentWindow === e.source);
      if (!f) return;
      found[(f.dataset.figure || f.dataset.phone) + (f.dataset.phone ? ' at 380px' : ' at ' + f.clientWidth + 'px')] = p;
      const lines = Object.entries(found).map(([k, v]) => k + ': ' + (v.length ? '\\n  - ' + v.join('\\n  - ') : 'no problems'));
      const total = Object.values(found).reduce((n, v) => n + v.length, 0);
      report.textContent = (Object.keys(found).length < frames.length * 2 ? 'Checking layout…\\n' : (total ? total + ' layout problems\\n' : 'Layout check: no problems\\n')) + lines.join('\\n');
    }});
    setTimeout(() => document.querySelectorAll('iframe[data-phone]').forEach(f => {{ f.srcdoc = doc(figures[f.dataset.phone] || ''); }}), 50);
  }}
  const draw = () => document.querySelectorAll('iframe[data-figure]').forEach(f => {{ f.srcdoc = doc(figures[f.dataset.figure] || ''); }});
  addEventListener('message', e => {{
    const h = e.data && e.data.learnFrameHeight;
    if (typeof h !== 'number') return;
    document.querySelectorAll('iframe[data-figure]').forEach(f => {{ if (f.contentWindow === e.source) f.style.height = Math.max(120, Math.min(1400, h)) + 'px'; }});
  }});
  draw();
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', draw);
  new MutationObserver(draw).observe(document.documentElement, {{ attributes: true, attributeFilter: ['data-theme'] }});

  // One concept at a time, picked from the bar at the top or with Next.
  const lessons = [...document.querySelectorAll('.lesson')];
  const smooth = matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
  const nav = document.querySelector('.cnav');
  const go = (id, scroll) => {{
    const target = lessons.find(l => l.id === id) || lessons[0];
    // The layout check needs every figure drawn, so it shows all the lessons.
    if (lessons.length > 1 && !document.getElementById('layout-report')) lessons.forEach(l => {{ l.hidden = l !== target; }});
    document.querySelectorAll('.cnav button').forEach(b => b.classList.toggle('on', b.dataset.go === target.id));
    if (scroll) (nav || target).scrollIntoView({{ behavior: smooth, block: 'start' }});
  }};
  document.querySelectorAll('[data-go]').forEach(b => b.addEventListener('click', () => go(b.dataset.go, true)));
  go(location.hash.slice(1), false);
  const top = document.querySelector('.totop');
  addEventListener('scroll', () => {{ top.hidden = scrollY < 700; }}, {{ passive: true }});
  top.addEventListener('click', () => scrollTo({{ top: 0, behavior: smooth }}));

  // Lesson and quiz tabs.
  document.querySelectorAll('.lesson').forEach(lesson => {{
    const show = name => {{
      lesson.querySelectorAll('.pane').forEach(p => {{ p.hidden = p.dataset.pane !== name; }});
      lesson.querySelectorAll('.tab').forEach(t => {{ const on = t.dataset.tab === name; t.classList.toggle('on', on); t.setAttribute('aria-selected', on); }});
      if (name === 'quiz') lesson.querySelector('.tabs').scrollIntoView({{ block: 'nearest' }});
    }};
    lesson.querySelectorAll('[data-tab]').forEach(b => b.addEventListener('click', () => show(b.dataset.tab)));
  }});

  // Quiz: choices in a fresh order, one try per question.
  document.querySelectorAll('.quiz').forEach(quiz => {{
    const qs = [...quiz.querySelectorAll('.q')];
    const score = quiz.querySelector('.score');
    const count = quiz.closest('.lesson').querySelector('.tab .count');
    let right = 0, done = 0;
    qs.forEach(q => {{
      const box = q.querySelector('.choices');
      [...box.children].sort(() => Math.random() - 0.5).forEach(c => box.appendChild(c));
      box.addEventListener('click', e => {{
        const c = e.target.closest('.choice');
        if (!c || c.disabled) return;
        const ok = c.dataset.i === q.dataset.answer;
        box.querySelectorAll('.choice').forEach(b => {{ b.disabled = true; if (b.dataset.i === q.dataset.answer) b.classList.add('right'); }});
        if (!ok) c.classList.add('wrong');
        q.querySelector('.why').hidden = false;
        right += ok; done++;
        if (done === qs.length) {{
          score.textContent = right + ' of ' + qs.length + ' right';
          score.classList.toggle('all', right === qs.length);
          count.textContent = right + '/' + qs.length;
          count.classList.toggle('done', right === qs.length);
        }}
      }});
    }});
  }});
}})();
</script>"""
    if standalone:
        body = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">' + body.replace("<style>", "</head><body><style>", 1) + "</body></html>"
        # The title and style belong in the head.
        body = body.replace("</head><body><style>", "<style>", 1).replace("</style>\n<div class=\"page\">", "</style></head><body>\n<div class=\"page\">", 1)
    # Write UTF-8 bytes, since Windows would otherwise use its own code page.
    sys.stdout.buffer.write(body.encode("utf-8"))


if __name__ == "__main__":
    main()
