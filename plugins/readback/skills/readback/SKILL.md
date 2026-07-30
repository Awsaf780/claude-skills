---
name: readback
description: "Use this whenever you are about to hand the user a finished deliverable (a report, a review, a written .md/doc file, a solved bug, a completed feature, a code/PR review, a resolved merge conflict, a finished analysis) or about to make a judgment call on the user's behalf that they should be the one deciding. Forces active engagement instead of a rubber-stamp: presents a real multiple-choice decision before acting on a judgment call, or requires a graded gist of understanding after delivering finished work — and does not let a failing gist pass. Triggers on phrases like 'quiz me', 'test my understanding', 'make me explain it back', 'don't let me off the hook', 'gate this', 'make me decide', 'check my understanding', as well as proactively before ending any turn that delivers one of the artifact types above."
---

# Readback

The user's problem: they receive AI output — reports, reviews, finished features, resolved conflicts — and skim-approve it without engaging. Sometimes they also let the assistant make calls that should have been theirs. This skill exists to force two things: (1) real decisions get made *by the user*, not rubber-stamped, and (2) finished work gets *understood*, not just accepted, verified by a graded write-back with a real pass bar.

This is a protocol, not a suggestion — follow it literally. Two distinct modes, triggered at two distinct moments. Do not blend them.

## Triggers

Invoke this skill on any of the following — don't wait for all of them to line up, one is enough:

- **Explicit command:** `/readback`.
- **Explicit phrases** from the user, anywhere in a message: "quiz me", "test my understanding", "make me explain it back", "don't let me off the hook", "gate this", "make me decide", "check my understanding", "readback".
- **Proactively, without being asked** — right before you end a turn that delivers any of: a report, a written `.md`/doc file, a solved bug, a completed feature, a code/PR review, a resolved merge conflict, a finished analysis — or right before you act on a judgment call the user hasn't actually weighed in on (see Mode 1 below).

## Mode 1 — Decision Gate (before you act on a judgment call)

Trigger: you are about to choose between real alternatives on the user's behalf — which fix to apply, how to resolve a merge conflict, which architectural direction to take, which of several valid approaches to use — and the user hasn't actually weighed in yet.

1. Stop before acting. Do not silently pick what you think is best and proceed.
2. Present the real options via `AskUserQuestion` (or, if unavailable in the current surface, a short numbered list inline). 2–4 mutually exclusive, concretely different options — not a fake choice where every branch leads to the same outcome.
3. You may recommend one, clearly labeled as a recommendation, but the user must make the actual selection.
4. Wait for their answer before proceeding. Do not treat silence or an unrelated reply as approval.

## Mode 2 — Comprehension Gate (after you deliver finished work)

Trigger: you just produced one of — a report, a written `.md`/doc file, a solved bug/problem, a completed feature, a code/PR review, a resolved merge conflict, a finished analysis.

1. Before considering the turn done, ask the user to write a short gist in their own words — 2 to 4 sentences, not a transcript — covering:
   - **What** actually happened/changed/was concluded.
   - **Why** — the key reason or trade-off behind it, not just the fact of it.
   - **Risk or caveat** — anything that could go wrong, is incomplete, or needs their attention.
2. Do not summarize the work for them first and ask them to confirm it — that defeats the point. Ask them to produce it cold.

### Grading — there is a real threshold

Grade the gist against what you actually did. This is the part the user explicitly asked for: **do not let a weak gist pass just because they wrote something.**

- **PASS bar:** correctly captures the core outcome, AND states at least one real reason or risk in their own words (not lifted verbatim from your output). Missing minor/secondary detail is fine.
- **FAIL bar:** wrong or missing on the core outcome; a generic non-answer ("looks good", "makes sense", "ok", "sounds right"); or a claim that contradicts what was actually done.

On **FAIL**: do not let it go and do not soften it into a pass out of politeness. State plainly and specifically what's missing or wrong — point at the exact gap (the decision, the file, the line, the trade-off) — and ask them to revise. Repeat.

**Attempt cap:** after 2 failed attempts on the same gate, stop making them guess blind — give a direct, specific hint pointing at exactly what they're missing, then ask for one more short confirmation. The goal is engagement, not an endurance test.

On **PASS**: say what they got right, correct any small residual misconception, and only then consider the gate closed.

## When NOT to use

- Trivial one-line answers, clarifying questions you're asking them, or routine status updates mid-task.
- Purely mechanical, easily-reversible actions (running a command, formatting, a typo fix).
- When the user has explicitly opted out for the current task or session ("skip the gate", "just do it", "no gate this time") — honor that, but don't let it become the silent default; the opt-out should come from them, not from you deciding the gate is inconvenient.

## Style

- Keep prompts short. This is a friction mechanism against passivity, not an essay assignment — if the ask feels like homework, you've overbuilt it.
- Never write the gist for them, even partially, before they've attempted it.
- One gate per deliverable/decision — don't stack multiple gates on a single turn unless there were genuinely multiple independent decisions or deliverables.
