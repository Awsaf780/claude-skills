# reviewer

A code reviewer for any repository, run as `/reviewer`.

| Command | What it does |
| --- | --- |
| `/reviewer <pr-url \| owner/repo#N \| N>` | Reviews a pull request and drafts a review. Nothing is posted until you say "post". |
| `/reviewer` | Reviews the current branch against its base, plus uncommitted work, and gives a fix list. |
| `/reviewer quick ...` | Blockers and majors only, no subagents. |
| `/reviewer learn <pr>` | Compares the review with what people raised later and records lessons. |

## Needs

- [`gh`](https://cli.github.com), signed in, and `jq`.
- A local clone of the repo helps: the review then reads whole files at the PR head from a temporary worktree and sees what the base gained since the branch was cut. The script looks in the current directory and under `~/Workspace`, `~/code`, `~/src` and `~/projects`. Set `REVIEWER_CLONE_DIRS` to change that.

## Where things are kept

- `~/.claude/reviews/<owner>__<repo>/pr-<n>/`: the gathered PR, the report and the review draft.
- `~/.claude/reviewer/lessons.md`: lessons from past reviews, created on first use.
- `~/.claude/reviewer/checklists.md`: lessons confirmed three times, read with the built-in checklists.
- `~/.claude/reviewer/repos/<owner>__<repo>.md`: optional notes for one repository, written by you.

Nothing in the repository you review is edited.
