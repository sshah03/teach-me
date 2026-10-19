# Picking the concepts

Read this when the input is a code change. You are a senior engineer helping a reviewer understand the ideas behind the change before they approve it. Find the few significant ideas a reviewer must understand to judge it: first the architecture and design decisions it makes, then algorithms and data structures, concurrency, protocols, security and math, and non-obvious behavior of a library or language feature the change relies on.

For each concept, decide: a title (2-6 words), its kind, why it's here (max 30 words, naming code in backticks), the alternatives it was likely chosen over (0-3, only ones the code or context supports), the changed files where it shows up, and its visual form.

## How many

Count the changed lines that aren't formatting, renames or generated files such as lock files (tests count). Under 80: at most 1 concept. 80 to 400: at most 2. More: at most 3. Most important first. An empty list is the right answer for many changes, and fewer is better than more. Never pad the list to look thorough. When there's nothing worth learning, say so in one sentence instead of making a page.

## What counts

- Include a concept only if all three hold: this change actually uses or introduces it; a capable engineer might not know it well; and a reviewer who doesn't understand it could approve a wrong change. Not renames, formatting, ordinary refactors, basic language features, small helper techniques or general advice.
- Architecture and design decisions come first: a new layer or module boundary, a cache, queue or index, data or control flow that moved, sync to async, a new extension point, state moved from globals into explicit context, a dependency replaced by in-house code, a component's default implementation switched or an old one deprecated. When the change makes such a decision, it is concept 1. Name the decision itself ("Requests read through a cache instead of going to the database"), not just the technique.
- An algorithm, library behavior or language detail belongs on the list only when misreading it could hide a bug in this change.

## Visual form

"none" unless a picture shows what words can't: a process over time (animation), several parts and how they connect, or an architecture before and after (diagram), how a number changes behavior (simulation), two behaviors on the same input (comparison), or math (formula). Library and language details are usually "none": text and a link to the docs teach them better. Across a list, several "none" is normal.
