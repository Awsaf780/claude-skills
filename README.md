# claude-skills

A public [Claude Code](https://claude.com/claude-code) plugin marketplace — a growing collection of generic, repo-agnostic skills anyone can install with two commands.

## Install

Inside Claude Code:

```
/plugin marketplace add awsaf780/claude-skills
/plugin install readback@claude-skills
/reload-plugins
```

Update later with `/plugin marketplace update`.

## Plugins

| Plugin | What it does |
| --- | --- |
| [`readback`](plugins/readback) | Forces active engagement with AI output — a real multiple-choice decision before a judgment call gets made on your behalf, and a graded understanding check before a finished deliverable (report, review, feature, resolved conflict) counts as done. Invoke with `/readback` or phrases like "quiz me" / "don't let me off the hook". |
| [`explaining-plainly`](plugins/explaining-plainly) | Changes how findings get explained in chat — what actually happens, in the order you'd encounter it, instead of a trail of `file:line` citations you can't verify. Code references become separate evidence rather than the spine of the explanation, and sequences or before/after differences get drawn as small plain-text diagrams. Applies to chat only; review reports and plan files stay code-precise. |
| [`notify`](plugins/notify) | Sends a notification when Claude finishes a turn or needs your input: a short desktop popup, plus the full reply on your phone through [ntfy](https://ntfy.sh) if you want it. After install, Claude offers to set up phone push; `/notify:setup` changes it later. |

## Contributing

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a new skill.
