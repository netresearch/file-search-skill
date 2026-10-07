#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Netresearch DTT GmbH
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
import stat
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


_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
# Where the platform can, every access goes through a descriptor of the state
# directory, so the directory checked is the directory used.
_DIR_FD = (
    hasattr(os, "O_DIRECTORY")
    and os.open in os.supports_dir_fd
    # os.replace takes the same dir_fd arguments but is never listed in
    # supports_dir_fd; os.rename is, and on POSIX it also replaces the target.
    and os.rename in os.supports_dir_fd
)


def _state_dir() -> tuple[int | None, str] | None:
    """The user's own state directory under the temp directory, or None.

    Returns a descriptor of the directory (None where the platform has no
    dir_fd support) and its path. The directory is created with mode 0700. An
    existing one is used only when it is a real directory (not a symlink) owned
    by the current user and closed to group and others; anything else returns
    None and the caller shows every reminder.
    """
    getuid = getattr(os, "getuid", None)
    suffix = str(getuid()) if getuid else "user"
    path = os.path.join(tempfile.gettempdir(), f"file-search-hook-{suffix}")
    try:
        os.mkdir(path, 0o700)
    except FileExistsError:
        pass
    except OSError:
        return None
    fd = None
    try:
        if _DIR_FD:
            fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | _NOFOLLOW)
            st = os.fstat(fd)
        else:
            st = os.lstat(path)
    except OSError:
        return None
    if not stat.S_ISDIR(st.st_mode) or (
        getuid and (st.st_uid != getuid() or st.st_mode & 0o077)
    ):
        if fd is not None:
            os.close(fd)
        return None
    return fd, path


def _open(
    dir_fd: int | None, base: str, name: str, flags: int, mode: int = 0o600
) -> int:
    if dir_fd is None:
        return os.open(os.path.join(base, name), flags, mode)
    return os.open(name, flags, mode, dir_fd=dir_fd)


def _read_seen(dir_fd: int | None, base: str, name: str) -> set:
    fd = _open(dir_fd, base, name, os.O_RDONLY | _NOFOLLOW)
    with os.fdopen(fd, encoding="utf-8") as fh:
        return set(json.load(fh))


def _write_seen(dir_fd: int | None, base: str, name: str, seen: set) -> None:
    """Write the state through a new file next to it, then rename it into place."""
    tmp = f"{name}.{os.getpid()}.tmp"
    fd = _open(dir_fd, base, tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | _NOFOLLOW)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(sorted(seen), fh)
        if dir_fd is None:
            os.replace(os.path.join(base, tmp), os.path.join(base, name))
        else:
            os.rename(tmp, name, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
    except BaseException:
        try:
            if dir_fd is None:
                os.unlink(os.path.join(base, tmp))
            else:
                os.unlink(tmp, dir_fd=dir_fd)
        except OSError:
            pass
        raise


def first_per_session(nudges: list[str], payload: dict) -> list[str]:
    """Keep only nudges whose rule has not fired in this session yet.

    Without a session identity, or when the state cannot be read or written,
    this fails OPEN — a broken temp dir must never swallow the first firing.
    """
    key = _session_key(payload)
    if not key:
        return nudges
    state = _state_dir()
    if state is None:
        return nudges
    dir_fd, base = state
    name = f"seen-{key}.json"
    try:
        try:
            seen = _read_seen(dir_fd, base, name)
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
                _write_seen(dir_fd, base, name, seen)
            except OSError:
                pass
        return fresh
    finally:
        if dir_fd is not None:
            os.close(dir_fd)


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
    # Fail open: any error ends with exit 0, see the module docstring.
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001
        sys.exit(0)
