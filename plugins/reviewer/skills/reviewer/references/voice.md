# Voice, scoring and posting

## Scoring

Every finding gets a magnitude from 1 to 10 and a severity label. Score consequence times likelihood: never by how big the fix is or how sure you feel.

| Magnitude | Label | Meaning |
| --- | --- | --- |
| 9–10 | blocker | Data loss, a security or tenant isolation hole, or a shipped path broken for everyone, including "can't deploy on the current base". |
| 7–8 | major | Wrong behaviour on a realistic input, a regression users or the pipeline will hit, a privilege broader than needed on a reachable path. |
| 5–6 | major or minor | Latent: wrong only once something else lands (plumbing not connected everywhere, a guard that works by accident). A broken written rule floors here. |
| 3–4 | minor | Duplication, drift risk, a missed reuse, an inconsistent pattern. |
| 1–2 | nit | Naming, wording, order. |

Report every finding that holds up in `report.md`, however small. Choosing what to post is a separate step.

A valid point outside the PR's scope (throttling, pagination, cleanup jobs that the backlog already plans) is offered as a follow-up ticket, not posted as a blocker: authors often answer these by filing a ticket and merging.

## How a comment reads

Good review comments share a shape:

1. **What happens**, with a concrete case: the input, the path it takes, the result.
2. **Why it matters**, in one sentence, if it isn't obvious.
3. **A suggestion**, often as a question, with enough detail to act on.
4. **How to keep it fixed**, when there is a cheap way: "a test that ... would keep it that way".

Rules:

- **Respectful, never aggressive.** Assume the author had a reason. "I think this can...", "Could we...?", "Maybe X would fit better?", "Isn't X ...?" are the house style. No "obviously", "wrong", "should have", no exclamation marks.
- **Short.** Two to four sentences: what happens, why it matters if that isn't obvious, the ask. The long form is for a blocker that needs it, and even then a short paragraph or two.
- **Only what matters, concisely.** No praise padding, no restating the PR, no "great work, but". A thanks or a "good catch" in a reply is fine.
- **One point per comment.** A bold title only on long, important ones.
- **Mark the weight.** Start a nit with `**Nit:**`; end an optional one with "Not blocking." Blockers say what breaks after merge or deploy.
- **Credit and link.** "On top of Sam's comment on `client.ts:18`..." when building on someone. Name other PRs and tickets in full when they are in another repository (`acme/tickets#130`).
- **Name names in code, not in blame.** `` `markerFor(login, requested)` ``, not "your code".
- **Uncertain? Say so and say how to check.** "I got this from reading the code without running it, so it's worth checking with a template-created chart."
- **No AI tells.** No em dashes, no "Here's the thing", no lists of three for rhythm, no closing summary. Never add "Generated with Claude Code".

### Examples from merged reviews

On a reminder script:

> I think this can send a second reminder for the same request. The marker uses `at`, which can move back to an earlier time: if Alex is reminded while Sam's changes request is open and Sam later approves, `at` falls back to Alex's request time and a new marker is written. Maybe `markerFor(login, requested)` would fit the "one reminder per request" rule better?

On a health route:

> Health is built on `createDomainApi()`, so it runs `requestContext`. Once the auth PR rejects requests without a token, this returns 401 and the pipeline smoke test fails. Could health use a base app without `requestContext` and `awsError`? That would also drop the DynamoDB SDK from its cold start.

On a permissions boundary, the long form:

> **Boundary allows AssumeRole on every bootstrap and environment role**
>
> This boundary applies to every role the stacks create, including the Lambda roles, so each of them may assume any `cdk-*` role and any `app-<env>-*` role. [...] A merged change can therefore add an inline `sts:AssumeRole` policy to a Lambda role and reach `cdk-hnb659fds-lookup-role-*` → `ReadOnlyAccess` on the account. [...]
>
> Suggestion: limit the resources to what the pipeline actually assumes [...]. A test that the boundary does not grant AssumeRole on the lookup role would keep it that way.

A nit:

> **Nit:** `autoDeleteObjects: true` with `RemovalPolicy.RETAIN` type-checks but throws at synth. A discriminated union would catch it at compile time instead: [snippet]. Not blocking.

## The review body

One plain, friendly line that sets the scene; the inline comments carry everything else. Example:

> Looks like dev branch has moved on quite a bit since the last merge. Some small feedback:

Add a second sentence only for something that applies to the whole PR and sits on no diff line, such as a deploy order. No list of findings, no "Not blocking" list: those go inline.

## Replies on your own PR

When the user answers review comments on their own PR (not this skill's main job, but it comes up): say what changed and where, then what was verified. "Fixed in `5396afc`." and a short list. Disagree with reasons and an offer: "I'd rather ... because ... That said, I'm happy to use 400 KB if you disagree with this reasoning."

## Posting

`review.json`:

```json
{
  "commit_id": "<head sha reviewed>",
  "event": "REQUEST_CHANGES",
  "body": "<review body>",
  "comments": [
    { "path": "infra/lib/constructs/data-access-role.ts", "line": 93, "side": "RIGHT", "body": "<comment>" },
    { "path": "apps/api/src/x.ts", "start_line": 20, "line": 24, "side": "RIGHT", "body": "<comment on a range>" }
  ]
}
```

- `line` must be a line of the PR's version of the file that sits inside a diff hunk. Check it against `diff.patch` before posting.
- A comment about a line the PR didn't touch goes in the body with its `file:line`.
- `event` is `REQUEST_CHANGES` whenever there is something to fix, `APPROVE` only when there isn't and the user agrees, never `COMMENT` for findings.
- A ```` ```suggestion ```` block works for a small, exact replacement of the commented lines.
