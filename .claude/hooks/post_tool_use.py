#!/usr/bin/env python3
"""PostToolUse hook (matcher: Write|Edit).

After Claude writes or edits a file, auto-format/lint it. For Python files we
run `ruff` (format + autofix). We never fail the tool here — linting is advisory
post-write; the Stop hook is the real gate. We just nudge Claude with feedback.

Exit code 0 -> success (stdout shown to Claude as context).
"""
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    path = payload.get("tool_input", {}).get("file_path", "")
    if not path or not Path(path).exists():
        return 0

    if path.endswith(".py"):
        # Best-effort format + autofix. Don't crash if ruff isn't installed.
        try:
            subprocess.run(["ruff", "format", path], check=False, capture_output=True)
            result = subprocess.run(
                ["ruff", "check", "--fix", path],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.stdout.strip():
                print(f"ruff applied fixes to {path}:\n{result.stdout}")
        except FileNotFoundError:
            print("ruff not found; skipping auto-lint (run `pip install ruff`).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
