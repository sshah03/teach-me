# Notes for AI agents

## Installing teach-me for a user

If someone has asked you to install this skill, these are the steps. Tell them briefly what you're
about to do, then do it.

1. **Check the basics.** Run `python3 --version` (on Windows, `python --version`). It needs 3.9 or
   newer. If Python is missing or older, stop and tell them they can get it from
   https://www.python.org/downloads/. Then run `gh --version` and `gh auth status`. The GitHub CLI
   is only needed for pull requests, so if it's missing or logged out, tell them how to fix it
   (install from https://cli.github.com, then `gh auth login`) and carry on.

2. **Install the plugin.** The repo is its own plugin marketplace:

   ```bash
   claude plugin marketplace add sshah03/teach-me
   claude plugin install teach-me@teach-me
   ```

   If it's already installed, run `claude plugin marketplace update teach-me` and
   `claude plugin update teach-me@teach-me` instead.

3. **Check it works.** Build a page from the test lesson in the repo and make sure it writes HTML:

   ```bash
   ROOT="$(claude plugin list --json | python3 -c "import json,sys; print(next(p['installPath'] for p in json.load(sys.stdin) if p['id'] == 'teach-me@teach-me'))")"
   python3 "$ROOT/.claude/skills/teach-me/scripts/build_page.py" "$ROOT/tests/bloom/lessons.json" --standalone > /tmp/teach-me-check.html && echo ok
   ```

   On Windows, use `python` in place of `python3`, and a temp folder that exists. It should print
   "ok". If it fails, show them the error rather than carrying on.

4. **Tell them how to use it.** Keep it short:
   - Start a new Claude Code session first, so the plugin loads.
   - Type `/teach-me` with a pull request number or link, `my uncommitted changes`, or an idea,
     for example `/teach-me how a Bloom filter answers "maybe"`.
   - It only runs when they type `/teach-me`.

To update later: `claude plugin marketplace update teach-me`, then
`claude plugin update teach-me@teach-me`. To uninstall: `claude plugin uninstall teach-me@teach-me`.

## Working on this repo

- The skill is in `.claude/skills/teach-me/`. `SKILL.md` is what Claude follows when someone types
  `/teach-me`. `references/` holds the briefs it reads at each step: picking ideas, writing a
  lesson and quiz, drawing the diagram, and checking it. `scripts/build_page.py` turns the lesson
  files into the page, and `assets/` has the style kit the diagrams draw with and the layout check. `tests/bloom/` is a
  finished lesson for checking an install and the page builder. It's kept outside the skill folder so
  Claude doesn't copy it.
- The repo is also a Claude Code plugin: `.claude-plugin/plugin.json` points at `.claude/skills/`,
  and `.claude-plugin/marketplace.json` lists the plugin. Leave `version` out of both, so installs
  follow new commits. Check them with `claude plugin validate .`. In SKILL.md, refer to the skill's
  own files through `${CLAUDE_SKILL_DIR}`, never a fixed path.
- Don't add `disable-model-invocation: true` to SKILL.md. Cowork runs a typed skill by having
  Claude load it, and that setting forbids exactly that. The skill stays typed-only through its
  description and its "How it is started" section instead.
- `build_page.py` uses only the standard library and has to run on Python 3.9, so don't nest
  f-strings with the same quote type or put a backslash inside an f-string expression. After a
  change, run `python tests/check_build.py`, then build `tests/bloom/lessons.json` with `--standalone` and
  open it in a browser. CI runs the same checks on Linux, Windows and macOS. `.github/workflows/e2e.yml`
  runs `/teach-me` for real with Haiku, only when started by hand, and needs an `ANTHROPIC_API_KEY` secret.
- The briefs in `references/` were tuned by comparing lessons written with and without each change,
  checked against the real code. Prefer a short principle with its reason over a new rule for one
  case; long rule lists made the diagrams cluttered and alike.
- Write docs and comments in plain English: short sentences, no jargon where a normal word works.
