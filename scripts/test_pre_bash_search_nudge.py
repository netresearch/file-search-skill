#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Netresearch DTT GmbH
"""Cases for scripts/pre_bash_search_nudge.py — run it, read what it says."""

import hashlib
import importlib.util
import json
import os
import shutil
import stat
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


# Every run gets a temp directory of its own (TMPDIR), so the cases neither see
# nor change state that a real session keeps in the system temp directory.
TMP = tempfile.mkdtemp(prefix="file-search-hook-test-")
_getuid = getattr(os, "getuid", None)
STATE_DIR = os.path.join(TMP, f"file-search-hook-{_getuid() if _getuid else 'user'}")


def run(cmd: str, session_id: str | None = None, tmpdir: str = TMP) -> str:
    payload = {"tool_name": "Bash", "tool_input": {"command": cmd}}
    if session_id is not None:
        payload["session_id"] = session_id
    p = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "TMPDIR": tmpdir, "TEMP": tmpdir, "TMP": tmpdir},
    )
    return p.stdout


def run_raw(payload_text: str) -> tuple[int, str]:
    """Run the hook on a literal stdin text; return exit code and stdout."""
    p = subprocess.run(
        [sys.executable, HOOK],
        input=payload_text,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "TMPDIR": TMP, "TEMP": TMP, "TMP": TMP},
    )
    return p.returncode, p.stdout


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

        # The state lives in a directory of the user's own under the temp
        # directory, closed to group and others.
        st = os.lstat(STATE_DIR) if os.path.lexists(STATE_DIR) else None
        private = (
            st is not None
            and stat.S_ISDIR(st.st_mode)
            and (os.name == "nt" or stat.S_IMODE(st.st_mode) == 0o700)
        )
        fails += 0 if private else 1
        print(
            f"  {'OK  ' if private else 'FEHL'} {'Zustand in eigenem 0700-Verzeichnis':44} "
            f"erwartet=True         erhalten={private}"
        )

        # A state directory that is not the user's own private directory is not
        # used: the hook shows every reminder and writes nothing through it.
        if os.name != "nt":
            for name, prepare in (
                ("Zustandsverzeichnis ist ein Symlink", "symlink"),
                ("Zustandsverzeichnis fuer die Gruppe lesbar", "open"),
            ):
                other_tmp = tempfile.mkdtemp(prefix="file-search-hook-test-", dir=TMP)
                target = os.path.join(other_tmp, "elsewhere")
                os.mkdir(target, 0o700)
                state = os.path.join(other_tmp, os.path.basename(STATE_DIR))
                if prepare == "symlink":
                    os.symlink(target, state)
                else:
                    os.mkdir(state)
                    # Owner may enter and write; the group may read and enter.
                    subprocess.run(["chmod", "750", state], check=True)
                usid = f"test-unsafe-{uuid.uuid4()}"
                warned = [
                    "systemMessage" in run("grep -rn A src/", usid, other_tmp)
                    for _ in range(2)
                ]
                written = os.listdir(target) + (
                    os.listdir(state) if prepare == "open" else []
                )
                ok = warned == [True, True] and written == []
                fails += 0 if ok else 1
                print(
                    f"  {'OK  ' if ok else 'FEHL'} {name:44} "
                    f"erwartet=2x Warnung, nichts geschrieben erhalten={warned} {written}"
                )

            # A state file that is a symlink is not followed: its target is
            # neither read as state nor written.
            key = hashlib.sha256(b"test-planted").hexdigest()[:16]
            sys.dont_write_bytecode = True  # no __pycache__ beside the hook
            spec = importlib.util.spec_from_file_location("nudge", HOOK)
            nudge = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(nudge)
            hashes = [
                hashlib.sha256(n.encode("utf-8")).hexdigest()[:12]
                for n in nudge.detect("grep -rn A src/")
            ]
            planted = os.path.join(TMP, "planted.json")
            with open(planted, "w", encoding="utf-8") as fh:
                json.dump(hashes, fh)
            os.symlink(planted, os.path.join(STATE_DIR, f"seen-{key}.json"))
            warned = "systemMessage" in run("grep -rn A src/", "test-planted")
            with open(planted, encoding="utf-8") as fh:
                untouched = json.load(fh) == hashes
            ok = warned and untouched
            fails += 0 if ok else 1
            print(
                f"  {'OK  ' if ok else 'FEHL'} {'Zustandsdatei ist ein Symlink':44} "
                f"erwartet=Warnung, Ziel unveraendert erhalten={warned} {untouched}"
            )

        # A session id carrying separators must not steer the state file out of
        # the state directory.
        evil_sid = "../../../../tmp/evil-search"
        run("grep -rn A src/", evil_sid)
        escaped = os.path.exists("/tmp/evil-search")
        # The state file must be named after the digest and sit in the state
        # directory itself; an unhashed id fails this even where the escaped
        # write itself went nowhere.
        digest = hashlib.sha256(evil_sid.encode("utf-8")).hexdigest()[:16]
        in_tmp = os.path.isfile(os.path.join(STATE_DIR, f"seen-{digest}.json"))
        escaped = escaped or not in_tmp
        ok = not escaped
        fails += 0 if ok else 1
        print(
            f"  {'OK  ' if ok else 'FEHL'} {'Pfad-Traversal in der Session-ID':44} "
            f"erwartet=False        erhalten={escaped}"
        )

        # Fail open: payloads of an unexpected shape and a state file with
        # unexpected content end with exit 0 and no output, never a traceback.
        bad_sid = f"test-badstate-{uuid.uuid4()}"
        bad_key = hashlib.sha256(bad_sid.encode("utf-8")).hexdigest()[:16]
        with open(
            os.path.join(STATE_DIR, f"seen-{bad_key}.json"),
            "w",
            encoding="utf-8",
        ) as fh:
            fh.write("5")
        bad_state = json.dumps(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "grep -rn A src/"},
                "session_id": bad_sid,
            }
        )
        for name, text in (
            ("Payload ist eine Liste", "[]"),
            (
                "command ist keine Zeichenkette",
                '{"tool_name": "Bash", "tool_input": {"command": 123}}',
            ),
            (
                "transcript_path ist eine Zahl",
                json.dumps(
                    {
                        "tool_name": "Bash",
                        "tool_input": {"command": "grep -rn A src/"},
                        "transcript_path": 5,
                    }
                ),
            ),
            ("Zustandsdatei ist eine Zahl", bad_state),
        ):
            got = run_raw(text)
            ok = got == (0, "")
            fails += 0 if ok else 1
            print(
                f"  {'OK  ' if ok else 'FEHL'} {'exit 0 ohne Ausgabe: ' + name:44} "
                f"erwartet=(0, '') erhalten=({got[0]}, {len(got[1])} Zeichen)"
            )
    finally:
        shutil.rmtree(TMP, ignore_errors=True)

    print("  ---- Fehlschlaege:", fails)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
