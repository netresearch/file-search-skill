#!/usr/bin/env python3
"""Cases for scripts/pre_bash_search_nudge.py — run it, read what it says."""

import json
import os
import subprocess
import sys
import tempfile
import uuid

HOOK = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "pre_bash_search_nudge.py"
)

# (name, expected substring or None, command)
CASES = [
    ("find nudgt auf Glob/fd", "fd", "find . -name '*.ts'"),
    ("rekursives grep nudgt auf rg", "rg", "grep -rn TODO src/"),
    ("einfaches grep nudgt", "Grep tool", "grep TODO notes.txt"),
    # A pipe into grep filters another command's output — that is not a search
    # over the tree and rg would not replace it.
    ("grep hinter einer Pipe nudgt nicht", None, "gh pr list | grep open"),
    # Structured data belongs to the data-tools gate; two hooks must not both
    # speak up for one command.
    ("grep auf .json ueberlassen wir data-tools", None, "grep -rn name pkg.json"),
    ("rg selbst nudgt nicht", None, "rg TODO src/"),
    ("fd selbst nudgt nicht", None, "fd -e ts"),
    # Prose about commands is not a command.
    (
        "Muster nur im PR-Body",
        None,
        """gh pr create --body "use find . -name x instead" """,
    ),
    ("Muster nur in echo", None, """echo "find . -name '*.ts'" """),
    (
        "Muster nur in gh api -f body=",
        None,
        """gh api repos/o/r/issues/1/comments -f body='we ran grep -rn TODO src/'""",
    ),
]


def run(cmd: str, session_id: str | None = None) -> str:
    payload = {"tool_name": "Bash", "tool_input": {"command": cmd}}
    if session_id is not None:
        payload["session_id"] = session_id
    p = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )
    return p.stdout


def main() -> int:
    fails = 0
    sid = f"test-{uuid.uuid4()}"
    try:
        for name, want, cmd in CASES:
            out = run(cmd, f"{sid}-{uuid.uuid4()}")
            got = (want in out) if want else ("systemMessage" not in out)
            fails += 0 if got else 1
            print(
                f"  {'OK  ' if got else 'FEHL'} {name:44} erwartet={want or 'still':12} ok={got}"
            )

        # Dedup: one message per rule per session, a new session speaks again.
        first = "systemMessage" in run("grep -rn A src/", sid)
        second = "systemMessage" in run("grep -rn B lib/", sid)
        other_rule = "systemMessage" in run("find . -name '*.py'", sid)
        new_session = "systemMessage" in run("grep -rn A src/", f"{sid}-2")
        for name, want, got in (
            ("erste Warnung feuert", True, first),
            ("zweite Warnung derselben Regel schweigt", False, second),
            ("andere Regel feuert weiterhin", True, other_rule),
            ("neue Session warnt wieder", True, new_session),
        ):
            ok = got == want
            fails += 0 if ok else 1
            print(
                f"  {'OK  ' if ok else 'FEHL'} {name:44} erwartet={want!s:12} erhalten={got}"
            )

        # A session id carrying separators must not steer the state file out of
        # the temp directory.
        run("grep -rn A src/", "../../../../tmp/evil-search")
        escaped = os.path.exists("/tmp/evil-search")
        ok = not escaped
        fails += 0 if ok else 1
        print(
            f"  {'OK  ' if ok else 'FEHL'} {'Pfad-Traversal in der Session-ID':44} "
            f"erwartet=False        erhalten={escaped}"
        )
    finally:
        for stale in os.listdir(tempfile.gettempdir()):
            if stale.startswith("file-search-hook-seen-"):
                os.unlink(os.path.join(tempfile.gettempdir(), stale))

    print("  ---- Fehlschlaege:", fails)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
