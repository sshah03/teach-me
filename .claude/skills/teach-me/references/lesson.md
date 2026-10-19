# Writing the lessons

Read this before writing any lesson. The page is described by `lessons.json` in the working folder, which lists one file per lesson (`lesson-c1.json`, `lesson-c2.json`…). Each figure is its own HTML file next to them (see figure.md). Writers and checkers each touch only their own lesson's files.

```json
{
  "mode": "change, or concept when the user described a concept",
  "title": "A name for the page, 2-6 words",
  "source": { "label": "owner/repo#123", "url": "https://github.com/owner/repo/pull/123", "title": "The PR title" },
  "intro": "Optional. One or two sentences on what the change does, for someone who hasn't read it.",
  "lessons": ["lesson-c1.json", "lesson-c2.json"]
}
```

Each `lesson-cN.json`:

```json
{
      "title": "The concept, 2-6 words",
      "kind": "architecture | design pattern | algorithm | data structure | concurrency | protocol | security | math | library | language",
      "why_here": "How this change uses it and why it matters for judging the change. Max 30 words.",
      "tldr": "One sentence, max 18 words: what the concept is and why it matters here.",
      "intuition": "30-60 words for someone meeting the concept for the first time.",
      "explanation": "About 100 words, never over 130: how it works, when it's the right choice, what it costs, how it fails.",
      "in_this_change": "30-70 words: where this change uses it and what a reviewer should check.",
      "figure": { "kind": "diagram", "title": "Max 8 words", "caption": "What to look at or do, max 20 words", "file": "c1.html" },
      "takeaways": ["The 1-3 things a reader must understand, max 12 words each. Most concepts have one or two."],
      "quiz": [ { "question": "…", "choices": ["…", "…", "…"], "answer": 0, "explanation": "…" } ],
      "sources": [ { "title": "Page title", "url": "https://…" } ]
}
```

Leave out `figure` when the concept's visual form is "none". For a concept the user described, with no code change: leave out `source` (or point it at what they gave you), `why_here` says where they'll meet the concept, and `in_this_change` becomes a short "where you'll see this" with one concrete example, or is left out. The page adds its own heading for that card, so don't start the text with a label, and don't mention these instructions in the lesson.

## Who it's for

Developers of every level reading the same page. A newcomer should get the idea from tldr, intuition and the figure. An expert should find explanation and in_this_change worth reading, not a rehash of basics. Don't repeat a point from one section in another.

## Writing rules (every text field, including the quiz)

- Write like a senior engineer explaining at a whiteboard: short sentences, concrete, every sentence earns its place. The word counts are ceilings, not targets: say it in fewer words when you can.
- explanation is for a developer who just read the intuition. Cover what they need to judge the change; leave out trivia, edge cases nobody here hits, and history.
- Define a term the first time you use it, in a few words. No filler ("It's important to note", "In summary", "Let's dive in"), no hype, no hedging stacks.
- intuition: plain words, one concrete example, or an analogy only if it's accurate. No code jargon left undefined.
- explanation: paragraphs separated by a blank line; "- " starts a list item. `code` in backticks, **bold** at most twice. No headings. Text fields are plain text with those marks only, so write a formula as `code` (for example `p ≈ (1 − e^(−kn/m))^k`) and leave MathML to the figure.
- in_this_change: name code in backticks; say what would go wrong if the concept were misused here.
- For an architecture or design decision, describe the system before and after: the parts, how data or control flows between them, what moved where, and the tradeoff that buys (what gets easier, what gets harder or slower, what can now fail).
- sources: 0-3 links to official documentation, specs, RFCs or well-known references (MDN, the language's own docs, docs.rs, Wikipedia, an RFC) that cover the concept. For a project-specific idea, a page in the repository under review works too. Only pages you are sure exist, with no query string. Leave the list empty rather than guess.
- Only state what the code supports. If something isn't shown, don't guess about it. Don't give reasons for a design that the code or the description doesn't give. Refer to code by symbol and file name.

## Quiz

Questions are about paths the code can really reach, and every answer agrees with the code and with the figure (if the figure can run the quiz's input, it gives the quiz's answer). One multiple-choice question per takeaway (the first one, on the core idea, counts), so most quizzes have 1 or 2 questions and none more than 3. When the core idea and how this change uses it are really the same point, that's one takeaway and one question.

3-4 choices each; "answer" is the 0-based index of the one correct choice. Start with the core idea (a newcomer who read the intuition can answer it); prefer questions about this change's own code ("what happens in `foo` if…") and its costs or failure modes. Wrong choices are plausible mistakes. Choices are shown in shuffled order, so in explanations refer to a choice by what it says, never by its letter or position. explanation: max 30 words, says why the answer is right and why the most tempting wrong choice is wrong, without restating the question.
