#!/usr/bin/env python3
"""Desktop (and optional phone) notification for Claude Code Stop and Notification hooks.

Header:     the first sentence of Claude's reply (Stop) or what it is waiting for (Notification)
Sub header: session title, then "<project> · <branch>"
Body:       the rest of the reply

Settings live in ~/.claude/notify.env (written by /notify:setup):
  NTFY_TOPIC      phone push through ntfy when set
  NTFY_SERVER     ntfy server, default https://ntfy.sh
  NTFY_TOKEN      access token for a protected topic or self-hosted server
  NOTIFY_DESKTOP  "off" to skip the desktop popup

Run with --test to send a sample notification without a hook event.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request

ENV_FILE = os.path.expanduser("~/.claude/notify.env")
BODY_LIMIT = 220
HEADLINE_LIMIT = 90


def load_env():
    env = {}
    try:
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    except OSError:
        pass
    return env


def setting(env, key, default=""):
    return os.environ.get(key) or env.get(key) or default


def tail_lines(path, max_bytes=2_000_000):
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - max_bytes))
            data = f.read().decode("utf-8", "replace")
    except OSError:
        return []
    return data.splitlines()


def result_text(block):
    content = block.get("content")
    if isinstance(content, str):
        return content
    return " ".join(c.get("text", "") for c in content or [] if isinstance(c, dict))


def scan_transcript(path):
    """Return (session title, last assistant text, background tasks still running)."""
    custom = ai = last_text = None
    candidates, launched, finished = set(), set(), set()
    for line in tail_lines(path):
        # Completed, stopped and killed tasks all report back with their launching tool-use id.
        finished.update(re.findall(r"<tool-use-id>(toolu_\w+)</tool-use-id>", line))
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        kind = entry.get("type")
        if kind == "custom-title":
            custom = entry.get("customTitle") or custom
        elif kind == "ai-title":
            ai = entry.get("aiTitle") or ai
        elif kind == "assistant" and not entry.get("isSidechain"):
            content = (entry.get("message") or {}).get("content") or []
            texts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
            text = "\n".join(t for t in texts if t.strip())
            if text:
                last_text = text
            for c in content:
                if not isinstance(c, dict) or c.get("type") != "tool_use":
                    continue
                if c.get("name") == "Workflow" or (c.get("input") or {}).get("run_in_background"):
                    launched.add(c.get("id"))
                elif c.get("name") in ("Agent", "Bash"):
                    candidates.add(c.get("id"))
        elif kind == "user" and not entry.get("isSidechain"):
            content = (entry.get("message") or {}).get("content")
            for c in content if isinstance(content, list) else []:
                if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("tool_use_id") in candidates:
                    text = result_text(c)
                    # Match only the notice itself, at the start, so output that merely quotes
                    # the phrase (a cat of this file) doesn't count as a background task.
                    if text.startswith("Async agent launched") or (
                        text.startswith("Command") and "moved to the background" in text[:200]
                    ):
                        launched.add(c.get("tool_use_id"))
    return custom or ai, last_text, launched - finished


def git_info(cwd):
    def run(*args):
        try:
            return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=2).stdout.strip()
        except Exception:
            return ""

    top = run("rev-parse", "--show-toplevel")
    project = os.path.basename(top or cwd.rstrip("/")) or cwd
    branch = run("rev-parse", "--abbrev-ref", "HEAD") if top else ""
    return project, branch


def plain(text):
    """Drop markdown marks but keep line breaks, for the phone where there is room."""
    text = text.replace("`", "").replace("**", "")
    lines = [re.sub(r"^#+\s*", "", line).rstrip() for line in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def clean(text):
    """One short line for the desktop popup."""
    text = " ".join(plain(text).split())
    return text if len(text) <= BODY_LIMIT else text[: BODY_LIMIT - 1].rstrip() + "…"


def headline(text):
    """Split off the reply's first sentence to use as the header. Returns (header, rest)."""
    lines = [line for line in plain(text).splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        return "", ""
    first = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", lines[0]).strip()
    match = re.match(r"(.+?[.!?])(?:\s|$)", first)
    sentence = match.group(1) if match else first
    rest_of_line = first[len(sentence):].strip()
    rest = "\n".join(([rest_of_line] if rest_of_line else []) + lines[1:]).strip()
    sentence = sentence.rstrip(":")
    if len(sentence) <= HEADLINE_LIMIT:
        return sentence, rest
    cut = sentence[:HEADLINE_LIMIT].rsplit(" ", 1)[0].rstrip(",;") + "…"
    return cut, plain(text)


# PowerShell 5.1 ships with Windows and can reach the toast API; PowerShell 7 cannot.
WINDOWS_TOAST = r"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
$t = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
$x = $t.GetElementsByTagName('text')
$x.Item(0).AppendChild($t.CreateTextNode($env:NOTIFY_HEADING)) > $null
$x.Item(1).AppendChild($t.CreateTextNode($env:NOTIFY_BODY)) > $null
$app = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($app).Show([Windows.UI.Notifications.ToastNotification]::new($t))
"""


def desktop(heading, body, urgent):
    env = None
    if sys.platform == "win32":
        cmd = ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", WINDOWS_TOAST]
        env = dict(os.environ, NOTIFY_HEADING=heading, NOTIFY_BODY=body)
    elif shutil.which("notify-send"):
        cmd = ["notify-send", "-a", "Claude Code", "-u", "critical" if urgent else "normal", heading, body]
    elif shutil.which("osascript"):
        script = f"display notification {json.dumps(body)} with title {json.dumps(heading)}"
        cmd = ["osascript", "-e", script]
    else:
        return
    try:
        subprocess.run(cmd, env=env, timeout=5, capture_output=True)
    except Exception:
        pass


def phone(env, heading, body, priority, tag):
    topic = setting(env, "NTFY_TOPIC")
    if not topic:
        return True
    server = setting(env, "NTFY_SERVER", "https://ntfy.sh").rstrip("/")
    payload = {"topic": topic, "title": heading, "message": body, "priority": priority, "tags": [tag]}
    headers = {"Content-Type": "application/json"}
    token = setting(env, "NTFY_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(server, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception as e:
        print(f"ntfy: {e}", file=sys.stderr)
        return False


def main():
    if "--test" in sys.argv[1:]:
        data = {
            "hook_event_name": "Stop",
            "cwd": os.getcwd(),
            "last_assistant_message": "Notifications from Claude Code are working. "
            "The first sentence of each reply becomes the header.\n\n"
            "Your phone shows the full reply with its line breaks. "
            "The desktop popup shows one short line.",
        }
    else:
        try:
            data = json.load(sys.stdin)
        except ValueError:
            return 0
    event = data.get("hook_event_name", "")
    cwd = data.get("cwd") or os.getcwd()
    project, branch = git_info(cwd)
    title, last_text, running = scan_transcript(data.get("transcript_path") or "")

    if event == "Notification":
        # The idle reminder repeats the Done notification a minute later.
        if data.get("notification_type") == "idle_prompt":
            return 0
        heading = data.get("message") or "Claude needs your input"
        rest = ""
        tag, urgent, priority = "bell", True, 4
    else:
        # A turn that ends while agents or background commands still run is not the end of the work.
        if running:
            return 0
        heading, rest = headline(data.get("last_assistant_message") or last_text or "")
        # A one-word reply like "Done." says less than the session title does.
        if len(heading) < 12:
            heading, rest = title or "Claude finished", plain(f"{heading}\n\n{rest}")
        tag, urgent, priority = "white_check_mark", False, 3

    # Header: what happened. Sub header: which session. Then the rest of the message.
    where = f"{project} · {branch}" if branch and branch != "HEAD" else project
    subheader = "\n".join(([f"💬 {title}"] if title and title != heading else []) + [f"📁 {where}"])
    env = load_env()

    if setting(env, "NOTIFY_DESKTOP", "on").lower() != "off":
        desktop(heading, clean(f"{where}: {rest}") if rest else where, urgent)
    sent = phone(env, heading, f"{subheader}\n\n{rest}".strip(), priority, tag)
    return 0 if sent else 1


if __name__ == "__main__":
    sys.exit(main())
