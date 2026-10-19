---
name: teach-me
description: >
  Explain the ideas behind a code change (a pull request, local changes, a commit) or a concept the user names,
  as short lessons with an interactive diagram and a quiz, checked against the code and saved as an Artifact.
  Run only when the user types /teach-me.
argument-hint: "[PR number or URL, owner/repo#123, \"my changes\", or a concept]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent, Artifact
---

# teach-me

## How it is started

Run this only when the user typed /teach-me or asked for teach-me by name. Don't start it on your own because a
conversation touches a code change or a concept.

The request: $ARGUMENTS

A teach-me page explains the few ideas a reader needs to judge a code change, or to understand a concept they named.
Each idea gets a short lesson, usually an interactive diagram, and a quiz. Every lesson is checked against the code
before it's published.

## 1. Work out what to teach

Make a new working folder with a unique name, for example with `mktemp -d`, in the session's scratchpad or temp directory and never inside the user's repo. Save everything there. A fresh folder keeps two runs from overwriting each other's files.

- **Nothing given:** use the current branch's pull request (`gh pr view --json number,title,body,url`). If there isn't one, use your uncommitted changes (`git diff HEAD`, plus new untracked files), and if there are none, the current branch's diff against its base.
- **Local changes, in words:** "my changes" or "uncommitted" is `git diff HEAD` plus new untracked files; "staged" is `git diff --cached`; "the last commit" or a commit hash is `git show <commit>`; a branch or range is `git diff <base>...<branch>`.
- **A PR number:** a PR in the current repo.
- **A PR URL or owner/repo#123:** a PR anywhere on GitHub, read with `gh` (`gh pr view <n> -R owner/repo --json title,body,url,files,headRefOid` and `gh pr diff <n> -R owner/repo`). Read whole files at the PR's head when the diff isn't enough: `gh api repos/owner/repo/contents/<path>?ref=<sha> -q .content | base64 -d`. For a big PR, clone it shallowly into the working folder instead.
- **Anything else:** it's a concept to explain. Teach that one concept, with one concrete example. If the user names a codebase or a file, ground the example in it.

For a change, save the diff as `change.diff` and note the PR's title, URL and description. For a concept there's no diff; note any files you ground the example in.

## 2. Pick the concepts

For a code change, read [references/concepts.md](references/concepts.md) and pick the concepts. Tell the user the list in one line each, then carry on without waiting. If there's nothing worth learning, say why in a sentence and stop: don't make a page. For a concept, that concept is the list; still decide its kind and visual form with concepts.md.

## 3. Write the lessons

Read [references/lesson.md](references/lesson.md) and [references/figure.md](references/figure.md). Write every lesson and figure new, from the code or the concept in front of you; don't start from any other lesson file. Write `lessons.json` for the page, and for each concept its own `lesson-c1.json` (c2, c3…) and, when it has a visual form, its figure `c1.html`. With more than one concept, you can write them in parallel with one subagent each: give each one the paths to the two reference files, the concept, the diff and the paths it may read. Each one writes only its own lesson and figure files.

## 4. Check each lesson against the code

For each lesson, start a separate agent and tell it to follow the brief below the line in `${CLAUDE_SKILL_DIR}/references/check.md`. Give it the paths to that lesson's `lesson-cN.json` and figure file, and what to check against: `change.diff` and the repository or files it can read, or for a concept, the files the example uses (if any). It fixes what's wrong in place and reports each fix. Run the checks in parallel and wait for all of them before building the page. Don't skip this step: the lessons are written to be checked.

## 5. Build the page and check the layout

Build the page:

    python3 "${CLAUDE_SKILL_DIR}/scripts/build_page.py" "<folder>/lessons.json" > "<folder>/page.html"

On Windows, use `python` instead of `python3` if `python3` isn't found or opens the Microsoft Store.

It prints a warning for each figure that won't read well on a phone. Fix those in the figure and build again before
going on.

If you can open a page in a browser (a browser tool, or Playwright), also build `--standalone --check` to `<folder>/check.html`, open it, and read the box with id `layout-report`. It lists text in each figure that overlaps, gets cut off or is too small to read, at the figure's width and at 380px. Fix those with small edits to the figure (move, shorten or wrap labels, let rows wrap, size drawings to their container), rebuild, and check again. Keep a fix only if the report gets shorter.

## 6. Publish

Publish `page.html` with the Artifact tool, as a new artifact. Its title is a short name for the page, like "Retry with backoff". When the Artifact tool isn't available, build with `--standalone` into the directory the session started in (not the working folder), as `teach-me-<short-name>.html`, so the user can find it after the temp files are gone. Give them its path.

Finish with one or two lines: the link (or path), and the concepts it covers.
