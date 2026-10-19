"""Checks the page builder without Claude: builds the test lesson, checks the page has what it should, and checks
the phone-width warning. Uses only the standard library, so it runs anywhere Python 3.9+ does.

usage: python tests/check_build.py
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, ".claude", "skills", "teach-me")
BUILDER = os.path.join(SKILL, "scripts", "build_page.py")
LESSON = os.path.join(ROOT, "tests", "bloom", "lessons.json")
failures = []


def check(ok, what):
    print(("ok    " if ok else "FAIL  ") + what)
    if not ok:
        failures.append(what)


def build(lessons, *flags):
    r = subprocess.run([sys.executable, BUILDER, lessons, *flags], capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout, r.stderr


spec = importlib.util.spec_from_file_location("build_page", BUILDER)
bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)

# The page body for an Artifact.
code, page, err = build(LESSON)
check(code == 0, "builds the test lesson")
check(page.startswith("<title>"), "page starts with its title")
check("<html" not in page[:200], "Artifact page has no document wrapper of its own")
figures = re.search(r'<script type="application/json" id="figures">(.*?)</script>', page, re.S)
check(bool(figures) and "c1.html" in json.loads(figures.group(1).replace("<\\/", "</")), "figure is embedded")
check(page.count('class="q"') == 2, "both quiz questions are on the page")
check('data-tab="quiz"' in page, "quiz has its own tab")
check("Where you will see it" in page, "concept page uses the concept heading")
check("checked against how it works" in page, "concept page footer doesn't claim a code check")

# A complete file to open in a browser, and the layout check.
code, full, err = build(LESSON, "--standalone")
check(code == 0 and full.lstrip().lower().startswith("<!doctype html>"), "standalone page is a full document")
code, chk, err = build(LESSON, "--standalone", "--check")
check(code == 0 and 'id="layout-report"' in chk and "layoutProblems" in chk, "check mode adds the layout report")

# Lists right after a sentence, and plain paragraphs.
html = bp.blocks("Two cases:\n- first\n- second\nAfter.\n\nNext")
check(html == "<p>Two cases:</p><ul><li>first</li><li>second</li></ul><p>After.</p><p>Next</p>", "lists and paragraphs")

# The phone-width warning: a wide fixed SVG is flagged, a narrow one isn't.
check(bool(bp.phone_problems('<svg viewBox="0 0 760 300"><text>x</text></svg>')), "wide SVG is flagged for phones")
check(not bp.phone_problems('<svg viewBox="0 0 360 360"><text>x</text></svg>'), "narrow SVG passes")

# Folders with spaces in their names, on every platform.
tmp = tempfile.mkdtemp()
try:
    spaced = os.path.join(tmp, "a folder with spaces")
    shutil.copytree(os.path.join(ROOT, "tests", "bloom"), spaced)
    code, page2, err = build(os.path.join(spaced, "lessons.json"))
    check(code == 0 and "c1.html" in page2, "builds from a folder with spaces")
    # Lesson files listed by name, as the skill writes them.
    data = json.load(open(os.path.join(spaced, "lessons.json"), encoding="utf-8"))
    lesson = data["lessons"][0]
    json.dump(lesson, open(os.path.join(spaced, "lesson-c1.json"), "w", encoding="utf-8"))
    data["lessons"] = ["lesson-c1.json"]
    json.dump(data, open(os.path.join(spaced, "lessons.json"), "w", encoding="utf-8"))
    code, page3, err = build(os.path.join(spaced, "lessons.json"))
    check(code == 0 and "c1.html" in page3, "reads lessons from separate lesson files")
    # Text outside ASCII, which Windows would otherwise read and write in its own code page.
    word = "na\u00efve \u201cmaybe\u201d \u2192 \u2265 1 \u2014 \u5e03\u9686"
    lesson["title"] = word
    with open(os.path.join(spaced, "lesson-c1.json"), "w", encoding="utf-8") as f:
        json.dump(lesson, f, ensure_ascii=False)
    with open(os.path.join(spaced, "c1.html"), "a", encoding="utf-8") as f:
        f.write("<!-- " + word + " -->")
    code, page4, err = build(os.path.join(spaced, "lessons.json"))
    check(code == 0 and word in page4 and word in json.loads(re.search(r'id="figures">(.*?)</script>', page4, re.S).group(1).replace("<\\/", "</"))["c1.html"], "keeps text outside ASCII in lessons and figures")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print()
print("all checks passed" if not failures else f"{len(failures)} failed")
sys.exit(1 if failures else 0)
