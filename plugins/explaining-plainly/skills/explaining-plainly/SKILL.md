---
name: explaining-plainly
description: Use when explaining, in chat, a code finding, bug, workflow, or design tradeoff to this user — including when summarizing a review report, plan file, or PR you just wrote. Applies before writing a chat message that would otherwise lean on file:line citations, function/selector names, or "grepped and confirmed" as the way of making the point. Does not apply to the code-precise artifacts themselves — only to how they're discussed in chat.
---

# Explaining Plainly

## Overview

The user did not read the code you grepped through. A chat explanation built out of `file:line` citations and function names asks them to trust a trail they can't verify themselves. Lead with what actually happens — a workflow narrative — and treat code references as optional backup, added at the end or only if asked, never as the spine of the explanation.

## When to use

- Explaining a review finding, bug, or "is this actually a problem" in chat
- Walking through why a design/plan decision matters
- Summarizing a review report, plan `.md`, or PR you just wrote — the file stays code-precise, the chat summary of each finding follows this skill
- Any chat message about to open with a function name, selector, or "confirmed via grep" instead of an action or an effect

**Does not apply** to the artifact files themselves (a review report, a plan `.md`, a PR body) — those are implementer-facing and stay code-precise with full citations. This skill governs the chat conversation *about* them.

## The structure

Five parts, in order, skip any that don't apply:

1. **Setup** — where this happens, in terms the user can picture. A screen or control if there's a UI; the job, trigger, or pipeline stage if there isn't. Not a component or module name.
2. **What happens** — the actual behavior, plain language. No selectors, no reducer/action names.
3. **Why it's a problem** (or isn't) — the concrete, observable consequence.
4. **Comparison** (if relevant) — how a similar, correctly-working case behaves, so the gap is obvious by contrast.
5. **Bottom line** — one or two sentences, the takeaway a decision gets made from.

## Example

Bad — code-path narration:
> `fly_to`'s `startAtFirstFeature` branch at animation.ts:485-494 snaps frame0, but the main loop's fly_to branch at line 607 doesn't check `startAtFirstFeature` before `transitions.push(...)`, unlike multihop's `startIdx` skip at line 550.

Good — workflow:
> When "Fly to location" is the first step and you check "Start on this feature," the camera's supposed to open already there — no flying. But it still plays a fake transition to the exact same spot, spending the step's whole duration on a move that goes nowhere. You'd see it as an extra, pointless card in the timeline. Multihop already handles the identical case correctly — Fly To never got the same fix.

## Shaping the message

A chat message is scanned in a terminal, not read in a chair. Give the eye landing points.

Count your paragraphs. **Three or more, every one of them opens with a bolded two-to-four-word lead-in** — including the first. Read the bolded fragments alone and they give the shape of the answer:

> **Yes, it's real.** … **The window is narrow.** … **Nothing alerts on it.** … **Bottom line:** …

The rest:

- **Two to three sentences per paragraph.** A second idea starts a new paragraph.
- **Verdict first.** The answer to what they asked goes in the opening sentence, ahead of the reasoning that supports it.
- **Nothing else gets bolded** except a key term or the one number that matters. A paragraph with four bold phrases has none.

**One or two paragraphs: no bold, no bullets, no headers.** Formatting a short reply makes it read as a report instead of an answer.

## Drawing it

When the thing being explained is a **sequence, a set of durations, or a before/after difference**, prose makes the user hold several things in their head at once. A small plain-text diagram removes that work. Draw one when any of these is true:

- Timing/ordering matters (what happens, in what order, for how long)
- You are contrasting two states — today vs. after the change, expected vs. actual, option A vs. option B
- The point is "these two cases disagree" and the disagreement is structural

**Pick the shape from what you're showing:**

| What you're showing | Shape |
|---|---|
| Durations or proportions | Proportional bars, before stacked over after |
| A sequence where the *values* matter more than proportion | One line per beat |
| Two options or states differing on several named points | Two-column table, one row per point of difference |
| An ordering with a break in it | Steps left to right, the break marked inline |

**Bars mean quantity.** `█` and `░` are only for durations, sizes, and proportions. A bar with no measurement behind it is decoration that implies a precision you don't have — if there's no number, use the table or the step-sequence shape instead.

**How to draw one:**

- **Plain text in a fenced code block.** It renders in a terminal; mermaid and images do not. Box-drawing characters and block glyphs (`┃ █ ░ ▒ └ ←`) are fine.
- **Label rows in the user's language** — "what you expected", "what plays", "today", "after the change" — never with internal names.
- **Stack the two states adjacent** so the difference is seen, not asserted.
- **Annotate the one thing to notice** with a trailing `←`. One or two annotations, not a key for every glyph.
- **Keep it small.** If it needs a legend longer than the diagram, the diagram is doing too much — split it or drop it.

Durations as proportional bars, before over after:

```
  today  ┃████████████████┃                     total 5s
         └ opens framed on the feature

after    ┃░░░░░░┃████████████████┃              total 8s
         └ opens framed, waits 3s, then the 5s hold

         ░ delay   █ hold
```

A sequence as one line per beat, when the *values* matter more than proportion:

```
at A   wait 1.5s   ← your 0.5s hold + your 1s delay
fly    2s
at B   wait 1.5s
fly    2s
at C   wait 0.5s   ← hold only; no next hop to delay before
```

An ordering with a break in it, when nothing is being measured:

```
  today    push image ──► upload config ──► job runs
                              ✗ fails        picks up NEW image, OLD config  ←

  reorder  upload config ──► push image ──► job runs
                ✗ fails                     never starts; image never goes live
```

**Don't draw** for a single value, a yes/no answer, or anything with no sequence and nothing to compare against — a sentence is better and a decorative diagram costs the reader time.

## Combining with code evidence

Code citations aren't banned — they're evidence, not narration. If the user wants to verify a claim, or the finding is going into a report/plan file, add `file:line` references *after* the plain explanation, clearly separated (e.g. under a "Where" or "Evidence" heading), not woven through it.

## Red flags — you're about to violate this

- First sentence of a chat explanation names a function, selector, or file path instead of an action or an effect
- 3+ `file:line` citations with no sentence describing what would actually be observable
- "I grepped for X and confirmed Y" stands in for an explanation of what Y means to the user
- You are about to narrate a sequence, or an expected-vs-actual difference, in a paragraph the reader has to re-read to follow — draw it instead
- You are drawing `█` bars for something that has no duration, size, or proportion behind it
- Four or more paragraphs in a row, none of them opening with a bolded lead-in
