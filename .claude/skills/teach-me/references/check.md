# Checking a lesson

This is the brief for the checking pass. Give it to a separate agent (one per lesson), with the paths to the lesson's `lesson-cN.json`, its figure file, and the code: the diff file and the repo or files it can read.

---

CHECK THE LESSON. Another engineer wrote the lesson you were given (a lesson-cN.json file) and its figure (an HTML file next to it). Before it reaches readers, check it against the code, as a careful reviewer would, and fix what's wrong. You can read the repository, search it and run small snippets, so look things up instead of guessing. Work through each point:

1. Every claim in the title, tldr, intuition, explanation, in_this_change, quiz and the figure (in every state its controls can reach) is true for this code and for the real runtime. Anything that only holds in a simplified model says so briefly in the lesson text.
2. Trace each number, output and string by hand on its input, the way this code computes it, or run the code when that's cheap. Numbers, defaults and labels come from this code (its own constants, conversions and default settings), not from a reference table, a spec or memory. A default set in another file or a library's exact output: look it up in the repository. A count or badge covers every item drawn, unchanged ones included, and has the same scope as its sentence.
3. "Before" is the real old behavior. If something is called hypothetical, check the removed code (and any removed dependency) first: when the old code really did it, show it as the real before. Before saying what is public, what was shared, or what the code did before, look at the old revision itself, including the package's entry point (its index or exports) and the old version of each file.
4. For each absolute (every, only, always, never, can't, forever, "if X then Y"), look for a counterexample in the code, the tests and the rest of the diff, including the figure's own cases. A claimed cost or failure (spins forever, leaks, can't be caught) holds only if every exit path and every other check in the code allows it. A claim copied from a code comment is checked too: a changelog entry or a test can contradict it. Qualify it or remove it. The tldr and title agree with every case the figure shows.
5. Everything the diff adds is accounted for: no "breaks", "requires" or "can't catch" when the diff has code that handles it.
6. The lesson and figure together show what sets the problem up, the condition that decides the outcome, and the outcome a user would see for the input shown. A case that was right before and is an error now is a regression, not colored as a fix.
7. Highlighted code is the line that causes the behavior. A part's detail quotes that part's own code. Each state change is pinned to the function that makes it.
8. Quiz answers agree with the code and with the figure, ask about paths the code can reach, and every question's premise is true. The "answer" index points at the right choice.
9. A fact you correct in one place is corrected everywhere it appears: tldr, intuition, explanation, quiz, figure.
10. The figure's script defines everything it uses and runs inside an IIFE, and the first view draws with no click.
11. The figure's first view, before any click and still after a minute untouched, shows the lesson's main point, not an edge case or an empty stage. The figure reads clearly at a glance: verdicts and colors match the outcomes they label, emphasis lands on what matters, captions and labels agree with what's drawn, and no text overlaps other text or lines. Text that only repeats what's already drawn or said can go.

HOW TO FIX: edit the lesson file and the figure file directly, with small targeted edits. Fix only what's wrong or confusing, and keep the lesson about as long as it is: correct a claim in place, or cut it, rather than explaining around it. Don't restyle or reword correct text, and never remove a true claim unless it only repeats one. In the figure, change only what's wrong: keep its elements, classes and layout, and fix the wrong labels, values or states rather than redrawing. When the lesson leaves out something a reader needs (points 5 and 6), add it to the lesson text in a sentence, not to the figure. Keep the lesson file valid JSON.

FOR A CONCEPT WITH NO CODE CHANGE: "the code" is the example in the lesson and the figure's own logic, plus the concept's documented behavior. Points 3, 5 and 7 apply only to a code change. Check the figure's numbers by running its own logic, and the lesson's claims against documentation.

Edit only the lesson file and figure you were given.

REPORT: one line per fix (what was wrong, what the code says), or "No changes" if nothing needed fixing.
