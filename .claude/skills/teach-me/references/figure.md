# Writing the figure

Read this before writing a figure. The concept's visual form is one of these:

- **animation**: something unfolding over time: messages between parties, a walk through a structure, state changing until something happens.
- **diagram**: structure or relationships: the parts, how data or control flows between them, and for an architecture change, what moved.
- **simulation**: how behavior depends on a number (load, input size, a probability), computed from the real rule in the code, with the point where behavior changes easy to see.
- **comparison**: old and new behavior, or two approaches, on the same input, so the real difference is obvious.
- **formula**: math made easier to feel than read: the formula in MathML, and the result responding as the reader changes an input, using the real constants.

In the lesson file, the figure is `{ "kind": "...", "title": "Max 8 words", "caption": "What to look at or do, max 20 words", "file": "c1.html" }`.

THE FIGURE. It sits beside the lesson, read by a developer who knows code but maybe not this concept. Aim for what the best explorable explanations do (Sam Rose's samwho.dev, Bartosz Ciechanowski, Red Blob
Games, Lin Clark's code cartoons): within a few seconds the reader sees the mechanism happen, and playing with it
makes the idea stick. It should be better than any textbook figure of this idea, and something a developer would
want to share.

WHAT GREAT LOOKS LIKE
- The drawing carries the idea and words support it. The lesson already holds the reasoning, caveats and code, so
  the figure needs only small labels on the things themselves and at most a line saying what's happening. Every
  mark earns its place, because clutter costs the reader attention they're spending on the review.
- Its form comes from this change (or, for a concept, from how the concept itself works and the example). Draw the real thing in its own shape: the queue filling, the tree an error
  climbs, the bytes in their order, messages crossing between two parties, a curve bending at a limit. Pick an
  instance small enough to take in whole (cells you could count, the actual string, a handful of nodes), with values
  that make the point visible. When the code's real numbers are too big to draw (a threshold of 100, a 64 KB buffer),
  scale them down and say so in the caption. A layout that would fit any PR is a sign to look again.
- The reader can read it without being told: requests as balls that travel, a queue as a column that fills, a
  pointer as an arrow that moves, a failed attempt that fades. State shows through form (fill, outline, position,
  fading) more than through text or badges.
- A quiet scene, with color for the story. Structure in --fg-muted and --border; --accent for the thing acting;
  --bad for the failure and --good for the right outcome, meaning the same thing throughout. Thin lines, simple
  shapes, and the figure floats on the page rather than sitting in cards.
- The first view already says something. Picture a screenshot taken the moment it loads, before anything moves or
  is clicked: it shows the answer, the failure next to the right result, or the key moment. When something moves,
  the motion replays how it got there.
- Interaction where the reader learns by changing something: drag the thing itself, scrub through time, pick the
  input that matters. Motion shows cause before effect, one thing at a time, with easing. A still figure is a fine
  answer when nothing needs to move. To compare two behaviors, two small versions from the same start, side by
  side, usually read faster than a toggle.

DEFAULTS TO NOTICE. Generated figures drift toward these. Each is right sometimes, so use one when this concept
really calls for it, never out of habit: bordered cards and panels; pills and badges carrying the state; rows of
text or key: value tables; stat tiles; code blocks or code expressions as labels inside the figure; legends; a row
of Play, Step and Back buttons; a before/after toggle where two small side-by-side views would do; sentences of
prose inside the figure.

HOW TO WORK
1. Before writing HTML, decide for yourself (not in the output): the one thing the reader should see, the picture
   that shows it, what they can do with it, and what you're leaving out. If you'd draw the same thing for an
   unrelated change or topic, look again.
2. Build it.
3. Read it back as someone seeing it cold, at 760px and on a phone, in light and dark. Can they tell what they're
   looking at and what it shows within a few seconds? If not, change the picture rather than adding words. Spend
   your boldness on one element and keep the rest quiet. Then remove one thing.

TRUTH. Everything drawn matches what this change's code really does: real names, values worked out by tracing the
code on a concrete input, and the old behavior as it really was. A reviewer checks the figure against the code
afterwards, so a few exact claims beat many approximate ones.

CRAFT. Readable in both themes; nothing overlapping or cut off anywhere from 300 to 900px wide; text 12px or larger,
including on a phone, where the figure is about 350px wide (so an SVG drawn much wider than that shrinks its text;
stack the parts or draw labels in HTML on narrow screens);
nothing important only on hover, since phones can't hover; with prefers-reduced-motion, change things instantly.

TOOLS already in the frame (the page builder adds assets/kit.css and assets/kit.js): native <button>, <select> and
<input type="range"> are styled; a selected toggle has aria-pressed="true", and a group of toggles goes in <div class="k-seg">. Kit.steps(total, show, { interval, start })
calls show(i) to draw step i, opens on step start (0 by default, so pass the key step to open there), and wires
buttons marked data-kit="play" and data-kit="step" and a data-kit="count" label, which it keeps in step with what's
drawn; it returns { go(i), play(), stop() }. Calling it again, say for another scenario, replaces the
previous player. Colors and fonts come only from these variables, so it matches the page's
theme: --bg, --bg-alt, --fg, --fg-muted, --border, --accent, --good, --bad, --warn, --font, --mono. Leave the page
background transparent. No emoji.

HTML RULES:
- One complete, self-contained HTML document with inline <style> and <script>, saved as its own file next to
  lessons.json, under 20,000 characters, plain modern JavaScript, no frameworks. It runs in a sandboxed frame with no network: no external scripts,
  stylesheets, fonts or images, no requests, no alert(). Draw with SVG, canvas and HTML; write formulas in MathML.
- Wrap the script in an IIFE, so its names can't collide with the page's own (closed, name, status, top).
- Before you finish, read the script through once: every function and variable it uses is defined, and the
  first view draws completely when the page loads, with no click.
