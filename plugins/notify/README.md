# notify

Get a notification when Claude finishes a turn or needs your input, on your desktop and, if you want, on your phone through [ntfy](https://ntfy.sh).

```
✅ Login redirect loop is fixed.          ← first sentence of Claude's reply
💬 Fix the login redirect                ← session title
📁 my-app · feature/login                ← project · branch

<the rest of Claude's reply>
```

The phone gets the whole reply with its line breaks. The desktop popup shows the header and one short line. When Claude waits for a permission or an answer, a 🔔 notification says what it needs. Nothing is sent while background agents or commands are still running, so "done" means done.

## Install

```
/plugin marketplace add awsaf780/claude-skills
/plugin install notify@claude-skills
/reload-plugins
```

Desktop notifications work right away. In your next session Claude asks whether you also want phone notifications and walks you through it. Run `/notify:setup` at any time to set up, change the topic, mute desktop popups or troubleshoot.

## Requirements

- Python 3 on `PATH` as `python3`, `python` or `py`
- Desktop popups: `notify-send` on Linux (`libnotify-bin` / `libnotify`), built in on macOS and Windows 10/11
- Windows: Git Bash, which Claude Code uses for hooks by default
- Phone: the ntfy app (Android or iPhone)

## Settings

`/notify:setup` writes `~/.claude/notify.env`. You can edit it by hand:

| Key | Meaning |
| --- | --- |
| `NTFY_TOPIC` | ntfy topic to push to. Empty means desktop only. |
| `NTFY_SERVER` | ntfy server. Default `https://ntfy.sh`. |
| `NTFY_TOKEN` | Access token for a protected topic or self-hosted server. |
| `NOTIFY_DESKTOP` | `off` to skip desktop popups. |

## Privacy

Topics on the public ntfy.sh server can be read by anyone who knows the name, and each notification carries Claude's reply. Setup generates a long random topic. For private code, use a self-hosted ntfy server or a protected topic with a token.

Messages over 4096 bytes arrive in the ntfy app as a `.txt` attachment.
