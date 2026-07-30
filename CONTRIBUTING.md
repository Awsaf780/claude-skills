# Contributing

Pull requests for new skills are welcome. A few ground rules to keep this collection useful:

- **Generic, not repo-specific.** Skills here should work in any repo, for any user — no hardcoded paths, project names, or assumptions about a particular stack. If your skill only makes sense inside one project, it belongs in that project's own `.claude/skills/`, not here.
- **One skill, one job.** Prefer a focused skill that does one thing well over a skill that tries to cover many unrelated cases.
- **A skill is a protocol, not a vibe.** Write the `SKILL.md` as literal steps Claude should follow, not a loose description of intent.

## Adding a new skill

1. Create a new plugin folder:
   ```
   plugins/<your-skill-name>/
     .claude-plugin/
       plugin.json
     skills/<your-skill-name>/
       SKILL.md
   ```
2. Write `plugin.json` (see [`plugins/readback/.claude-plugin/plugin.json`](plugins/readback/.claude-plugin/plugin.json) for the shape — `name`, `description`, `version`, `author`).
3. Write `SKILL.md` with YAML frontmatter (`name`, `description`) followed by the protocol body. The `description` field drives auto-invocation, so make it specific about *when* the skill should trigger, not just what it does.
4. Add an entry to [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json):
   ```json
   {
     "name": "<your-skill-name>",
     "source": "./plugins/<your-skill-name>",
     "description": "..."
   }
   ```
5. Add a row to the plugin table in [`README.md`](README.md).
6. Test locally before opening a PR:
   ```
   /plugin marketplace add ./claude-skills
   /plugin install <your-skill-name>@claude-skills
   /reload-plugins
   ```
7. Open a PR. Include a short note on what problem the skill solves and why it needs to be a skill (vs. just a good prompt).

## Versioning

Bump `version` in `plugin.json` when you change a published skill's behavior — that's what tells existing installers an update is available.
