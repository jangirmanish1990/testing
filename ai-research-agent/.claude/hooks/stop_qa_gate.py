#!/usr/bin/env python3
"""Stop hook — the QA gate.

Runs when Claude Code thinks it is done. If the test suite fails, we block the
stop (exit 2) and hand the failure back to Claude so it keeps working until
tests pass. If there are no tests yet, or pytest isn't installed, we allow.

Exit code 0 -> allow stop.
Exit code 2 -> block stop; stderr is fed back to Claude.
"""
import subprocess
import sys
from pathlib import Path


def main() -> int:
    if not Path("backend/tests").exists():
        return 0  # no tests yet; nothing to gate on

    try:
        result = subprocess.run(
            ["pytest", "-q", "backend/tests"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print("pytest not installed; skipping QA gate.", file=sys.stderr)
        return 0

    if result.returncode != 0:
        tail = (result.stdout + result.stderr)[-3000:]
        print(
            "QA gate failed: pytest is not green. Fix the failing tests before "
            "finishing.\n\n" + tail,
            file=sys.stderr,
        )
        return 2

    print("QA gate passed: all tests green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
