#!/usr/bin/env python3
"""SessionStart hook: the first session after install, ask Claude to offer /notify:setup.

Runs once. It stays quiet when ~/.claude/notify.env already exists or after it has asked.
"""
import json
import os

ENV_FILE = os.path.expanduser("~/.claude/notify.env")
MARKER = os.path.expanduser("~/.claude/notify.asked")

if not os.path.exists(ENV_FILE) and not os.path.exists(MARKER):
    try:
        os.makedirs(os.path.dirname(MARKER), exist_ok=True)
        open(MARKER, "w").close()
    except OSError:
        pass
    context = (
        "The notify plugin was just installed and is not set up yet. Desktop notifications "
        "already work when a turn ends. In your first reply, before anything else, tell the user "
        "that in one sentence and ask whether they also want phone notifications through ntfy. "
        "If they say yes, run the notify:setup skill. If they say no, run it anyway so it can "
        "save that choice."
    )
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}))
