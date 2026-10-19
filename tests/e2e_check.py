"""Checks the page from an end-to-end run, where Claude ran /teach-me without the Artifact tool and saved the page
as teach-me-<name>.html in the working folder.

usage: python tests/e2e_check.py <working folder> <stream-json log> [--pr]
"""
import glob
import json
import os
import re
import sys

folder, log = sys.argv[1], sys.argv[2]
want_pr = "--pr" in sys.argv
failures = []


def check(ok, what):
    print(("ok    " if ok else "FAIL  ") + what)
    if not ok:
        failures.append(what)


result = {}
with open(log, encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "result":
            result = event
print(f"cost ${result.get('total_cost_usd', 0):.2f}, {result.get('num_turns', '?')} turns")
check(bool(result) and not result.get("is_error"), "the run finished without an error")

pages = glob.glob(os.path.join(folder, "teach-me-*.html"))
check(len(pages) == 1, "one page saved in the working folder")
if not pages:
    print("\nlast reply:\n" + str(result.get("result", ""))[-2000:])
    sys.exit(1)

with open(pages[0], encoding="utf-8") as f:
    page = f.read()
print(f"page: {os.path.basename(pages[0])}, {len(page) // 1024} KB")
check(page.lstrip().lower().startswith("<!doctype html>"), "page is a full document")
m = re.search(r'<script type="application/json" id="figures">(.*?)</script>', page, re.S)
figures = json.loads(m.group(1).replace("<\\/", "</")) if m else {}
check(len(figures) >= 1, "page has at least one figure")
check(all(re.search(r"<(svg|canvas|div|table)\b", src) for src in figures.values()), "every figure draws something")
check(page.count('class="q"') >= 1, "page has a quiz")
if want_pr:
    check('class="src"' in page, "page names the pull request it came from")

print()
print("all checks passed" if not failures else f"{len(failures)} failed")
sys.exit(1 if failures else 0)
