---
name: setup
description: Set up or change the notify plugin, which sends a desktop notification (and optionally a phone push through ntfy) when Claude finishes a turn or needs input. Use when the user runs /notify:setup, when the notify plugin's first-run message asks you to, or when the user wants to turn phone notifications on or off, change or reset their ntfy topic, use their own ntfy server, mute desktop popups, or fix notifications that do not arrive.
---

# Notify setup

The plugin's hooks already run on every Stop and Notification event. This skill only writes the settings file `~/.claude/notify.env` and helps the user subscribe on their phone. Follow the steps in order.

The notification script is at `../../scripts/notify.py`, relative to this skill's base directory. Call it `NOTIFY` below and always use its absolute path.

## 1. Check the basics

1. Find Python 3: try `python3 --version`, then `python --version`, then `py -3 --version`, and use the first that prints Python 3 as `PY` below. If none does, stop and tell the user the plugin needs Python 3 on `PATH` (python.org or the package manager; on macOS, `xcode-select --install` also provides it). On Windows, hooks run in Git Bash, which Claude Code uses by default.
2. Read `~/.claude/notify.env` if it exists and tell the user what is set now: phone push on or off, the server, and whether desktop popups are muted. Show the topic name; it belongs to them.
3. Check for a second notification hook that would make every notification arrive twice: search `~/.claude/settings.json` and `.claude/settings*.json` in the current project for `Stop` or `Notification` hooks that call `notify-send`, `osascript`, `ntfy` or a `notify` script. If you find one, show it and ask whether to remove it. Never remove it without a yes.

## 2. Ask what they want

Ask with one multiple-choice question:

- **Phone + desktop, new private topic (Recommended).** You generate a random topic on ntfy.sh.
- **Phone + desktop, my own topic or server.** They give a topic, and optionally a server URL and an access token.
- **Desktop only.** No phone push.

Then ask a second question only if it matters to them: keep desktop popups on (default) or turn them off (phone only).

Before they pick a public ntfy.sh topic, say plainly: anyone who knows the topic name can read the notifications, and each notification contains Claude's reply, which can include code. A long random topic is hard to guess. For private work, a self-hosted ntfy server or an access-protected topic with a token is safer.

## 3. Write the settings

1. For a new topic, generate it with:
   ```
   python3 -c "import secrets; print('claude-' + secrets.token_urlsafe(12).replace('_', '').replace('-', '')[:16])"
   ```
2. Write `~/.claude/notify.env` with only the keys that apply:
   ```
   NTFY_TOPIC=<topic, or empty for desktop only>
   NTFY_SERVER=<only when not https://ntfy.sh>
   NTFY_TOKEN=<only when they gave one>
   NOTIFY_DESKTOP=<off, only when they turned popups off>
   ```
   An empty file is a valid "desktop only" answer. Writing the file is what marks setup as done.
3. Run `chmod 600 ~/.claude/notify.env` on Linux and macOS, since it may hold a token.

Desktop only: skip to step 5.

## 4. Subscribe the phone

Give the user these steps, filled in with their real server and topic:

1. Install the ntfy app: Android from Google Play or F-Droid, iPhone from the App Store. Search "ntfy".
2. Open it, tap **+**, and enter the topic `<topic>`. When the server is not ntfy.sh, turn on "Use another server" and enter `<server>`.
3. Android only: turn on "Instant delivery" for the topic and allow the app to ignore battery optimisation, or notifications can arrive minutes late.

They can also read notifications in a browser at `<server>/<topic>`.

Wait until they say they have subscribed.

## 5. Send a test

Run `PY -I NOTIFY --test`. A non-zero exit means ntfy rejected the request; the error is on stderr.

Ask whether the test arrived (on the phone, and as a desktop popup unless muted). If it did not:

- Phone, exit 0: the topic or server in the app does not match the settings file, or the app is not set to instant delivery.
- Phone, non-zero exit with 401 or 403: the topic is protected and the token is missing or wrong.
- Desktop on Linux: `notify-send` is missing; it comes from the `libnotify-bin` (Debian, Ubuntu) or `libnotify` package.
- Desktop on macOS: notifications for Script Editor are turned off in System Settings → Notifications.
- Desktop on Windows: notifications for Windows PowerShell are turned off in Settings → System → Notifications, or Focus / Do not disturb is on.

Fix, then send the test again.

## 6. Finish

Tell the user in two or three lines what is now set up, that the first sentence of each reply becomes the notification header with the rest of the reply below it on the phone, and that `/notify:setup` changes any of it later.
