#!/usr/bin/env python3
"""PreToolUse hook for Bash: point shell searches at the search tools.

This skill's table — `rg` instead of `grep`/`grep -r`, `fd` instead of `find`,
`sg` for structural patterns — is an instruction, and instructions get skipped.
In the retro that produced this hook, Bash carried 63% of all tool calls while
the dedicated Grep and Glob tools went unused.

Warn-only, and once per rule per session. The value sits in the first firing:
it is read once and either changes the next command or has a deliberate reason
not to — batching several searches into one call, or probing a scratch file.
Firings 2..n change nothing and only cost the reader attention while scrolling
(measured on the source machine: 23 firings of these three rules in a single
session).

Exit code is always 0; a hook that crashes must never block a shell.
"""

import hashlib
import json
import os
import re
import sys
import tempfile

# Structured data belongs to the data-tools gate, which denies extraction from
# it. Staying out of that lane keeps one command from collecting two messages.
STRUCT = re.compile(r"\.(json|jsonl|ya?ml|toml|xml|csv|tsv)(\b|['\"])", re.IGNORECASE)

# A quoted heredoc body is data being written, not a command being run.
QUOTED_HEREDOC = re.compile(r"<<-?\s*(['\"])(\w+)\1.*?^\2$", re.DOTALL | re.MULTILINE)


# Prose passed as an option value is text ABOUT commands (a PR body, a commit
# message), so it must not be scanned for commands. `--body-file` names a path
# and is left alone.
def _quoted(group: str) -> str:
    return rf"(?P<{group}>['\"])(?:\\.|(?!(?P={group})).)*(?P={group})"


OPTION_VALUES = (
    re.compile(
        r"(?:--(?:body|message|notes|description|title|comment)(?!-file)"
        r"|(?<!\w)-[mF](?!\w))[= ]\s*" + _quoted("q"),
        re.DOTALL,
    ),
    re.compile(r"(?<!\w)-f\s+\w+=\s*" + _quoted("q"), re.DOTALL),
)
ECHOES_TEXT = re.compile(r"^\s*(echo|printf)\b")

RECURSIVE_GREP = re.compile(r"(^|[|&;])\s*grep\s+-[a-zA-Z]*[rR]")
PLAIN_GREP = re.compile(r"^\s*grep\s")
FIND = re.compile(r"^\s*find\s")


def executable_text(cmd: str) -> str:
    """The command with its data parts (heredocs, prose option values) removed."""
    cmd = QUOTED_HEREDOC.sub(" ", cmd or "")
    for pattern in OPTION_VALUES:
        cmd = pattern.sub(" ", cmd)
    return cmd


def detect(cmd: str) -> list[str]:
    """Ordered, de-duplicated nudges for one command string."""
    cmd = executable_text(cmd)
    if ECHOES_TEXT.match(cmd.strip()):
        return []
    nudges: list[str] = []
    structured = bool(STRUCT.search(cmd))

    if FIND.match(cmd):
        nudges.append(
            "`find` — use the Glob tool, or `fd` (faster, .gitignore-aware, sane defaults)."
        )
    if not structured:
        if RECURSIVE_GREP.search(cmd):
            nudges.append(
                "recursive grep over code — use the Grep tool or `rg` (respects .gitignore, "
                "faster); for structural or multi-language patterns `sg` (ast-grep)."
            )
        elif PLAIN_GREP.match(cmd):
            nudges.append("plain grep — prefer the Grep tool or `rg`.")
    return nudges


# ─── once-per-session dedup ──────────────────────────────────────────────────


def _session_key(payload: dict) -> str:
    """A filename-safe digest of the session identity, or "" when there is none.

    The raw identifier comes from the harness payload and is hashed rather than
    interpolated: a value carrying `/` or `..` would otherwise steer the state
    file out of the temp directory.
    """
    raw = payload.get("session_id") or os.path.basename(
        payload.get("transcript_path") or ""
    )
    raw = str(raw).strip()
    if not raw:
        return ""
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def first_per_session(nudges: list[str], payload: dict) -> list[str]:
    """Keep only nudges whose rule has not fired in this session yet.

    Without a session identity, or when the state cannot be read or written,
    this fails OPEN — a broken temp dir must never swallow the first firing.
    """
    key = _session_key(payload)
    if not key:
        return nudges
    path = os.path.join(tempfile.gettempdir(), f"file-search-hook-seen-{key}.json")
    try:
        with open(path, encoding="utf-8") as fh:
            seen = set(json.load(fh))
    except (OSError, ValueError):
        seen = set()
    fresh = []
    for n in nudges:
        h = hashlib.sha256(n.encode("utf-8")).hexdigest()[:12]
        if h in seen:
            continue
        seen.add(h)
        fresh.append(n)
    if fresh:
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(sorted(seen), fh)
        except OSError:
            pass
    return fresh


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    cmd = (payload.get("tool_input") or {}).get("command", "")
    if not cmd:
        return 0

    nudges = first_per_session(detect(cmd), payload)
    if nudges:
        print(
            json.dumps(
                {
                    "systemMessage": "file-search: "
                    + " ".join(nudges)
                    + " (warned once per rule per session)",
                    "suppressOutput": True,
                }
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
