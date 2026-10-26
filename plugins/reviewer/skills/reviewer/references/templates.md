# Agent briefs and answer formats

Two kinds of agent help a review: area reviewers on large diffs (step 4) and the author's advocate (step 5). Both answer in a fixed format, so every claim arrives with the lines it rests on and can be checked in minutes.

## Area reviewer (step 4)

Brief, filled in per agent:

> You review one area of pull request `<owner/repo#N>`, head `<sha>`, base `<base>`. Your files: `<list>`. The diff is at `<review-folder>/diff.patch`, the code at the head in `<review-folder>/head/`, and the merged result in tree `<merge-tree.txt>` of the clone at `<clone>` (`git -C <clone> show <tree>:<path>`). Comments already made are in `<review-folder>/comments.md`; don't repeat them. Walk every section of `<skill-dir>/references/checklists.md` that matches your files, and the repo rules: `<rule files>`.
>
> Read code; don't run tests or deploys, and don't edit anything. Report only what you can show from lines you read. Answer with one block per finding in the format below and nothing else. A finding without quoted lines will be dropped.

Answer format:

```
### F<n>: <the problem in one sentence>
- Where: <path:line>, at <head | after merge | base>
- Evidence: <the lines it rests on, quoted, each with path:line>
- Failing case: <a concrete input or event, and what happens>
- Origin: <introduced | pre-existing>
- Depends on: <nothing | the merge with the base | PR #M | a deploy order>
- Tried to disprove: <the guard, test, caller, comment or ADR you looked for, and where>
- Severity: <1-10, as in voice.md>
```

## The author's advocate (step 5)

One agent for all findings scored 5 and up, after you have verified them yourself. It argues for the PR author, like a defence lawyer: its job is the strongest honest case that each finding is wrong, already handled, out of scope or less severe than claimed. It gets the claims, not your reasoning.

Brief:

> You are the PR author's advocate for pull request `<owner/repo#N>`, head `<sha>`. A reviewer is about to post the findings below. For each one, make the strongest honest case for the author. Look for: a guard, test, middleware or caller that prevents it; a later commit or the merged result (`git -C <clone> show <tree>:<path>`) that already changes the lines; a ticket comment, PR comment or ADR that accepts, defers or scopes it out (`<review-folder>/tickets.md`, `<review-folder>/comments.md`, `docs/adr/`); a failing case that can't happen in practice; a severity that is overstated. The code at the head is in `<review-folder>/head/`.
>
> Read code; don't run anything or edit anything. Every defence must quote the lines it rests on, with path:line; a defence without them doesn't count. If there is no honest defence, say so: conceding a sound finding is part of the job.
>
> Findings:
> `<for each: F<n>, the one-sentence problem, Where, Failing case>`

Answer format:

```
### F<n>
- Verdict: <defence wins | severity lower, to <n> | no defence>
- Defence: <the argument, in two or three sentences>
- Evidence: <quoted lines, each with path:line>
```

Then you are the judge: read every line the advocate cites yourself. Drop a finding whose defence holds, lower one whose severity case holds, and keep the rest. In `report.md`, add one line under each finding: the advocate's verdict, and if you kept a finding the advocate argued against, why.
