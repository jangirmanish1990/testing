#!/usr/bin/env python3
"""PreToolUse hook (matcher: Bash).

Receives the pending tool call as JSON on stdin. Logs every shell command to
.claude/audit.log and blocks a small denylist of obviously destructive ones.

Exit code 0  -> allow.
Exit code 2  -> block; stderr is shown to Claude as the reason.
"""
import datetime
import json
import re
import sys
from pathlib import Path

DENY_PATTERNS = [
    r"rm\s+-rf\s+/",          # nuke from root
    r":\(\)\s*\{",             # fork bomb
    r"git\s+push\s+.*\bmain\b",  # direct push to main
    r"curl\s+.*\|\s*(ba)?sh",  # pipe-to-shell
]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # nothing to inspect; don't block

    command = payload.get("tool_input", {}).get("command", "")

    log_dir = Path(".claude")
    log_dir.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    with (log_dir / "audit.log").open("a", encoding="utf-8") as fh:
        fh.write(f"{stamp}\t{command}\n")

    for pattern in DENY_PATTERNS:
        if re.search(pattern, command):
            print(
                f"Blocked by pre_tool_use hook: command matches denied "
                f"pattern /{pattern}/. Refusing to run: {command}",
                file=sys.stderr,
            )
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
