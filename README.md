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

## Contributing

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a new skill.
