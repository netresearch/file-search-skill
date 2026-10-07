<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- SPDX-FileCopyrightText: Netresearch DTT GmbH -->

# Security assurance case — file-search-skill

This document states what a user can expect from this repository in terms of security, and argues why that expectation holds. Every claim names the file that implements it. Reporting a vulnerability: see the [security policy](https://github.com/netresearch/.github/blob/main/SECURITY.md). Components and data flow: [ARCHITECTURE.md](ARCHITECTURE.md).

## What the repository ships

| Part | Files | Runs where |
| --- | --- | --- |
| Skill instructions for an AI agent | `skills/file-search/SKILL.md`, `skills/file-search/references/*.md` | Read by the agent as instructions; not executed |
| PreToolUse hook | `hooks/hooks.json`, `scripts/pre_bash_search_nudge.py` | On the user's machine, started by Claude Code before each Bash tool call |
| Repository checks | `scripts/test_pre_bash_search_nudge.py`, `Build/Scripts/check-plugin-version.sh`, `Build/hooks/pre-push`, `scripts/verify-harness.sh` | In this repository's CI and on contributors' machines |

The skill has no server component and handles no user accounts or credentials.

## Security requirements

1. The hook never executes the command it inspects, nor any other part of its input.
2. The hook never blocks or changes a command; its only effect on the session is an advisory message.
3. The hook sends nothing over the network.
4. The only files the hook writes are its once-per-session state files, in a directory that belongs to the user and is closed to others; its input cannot choose the directory.
5. Nothing committed to this repository contains a secret.

## Actors and trust boundaries

- **Agent → hook.** The command text in the payload is written by the AI agent, which may have been steered by content it read. The hook treats it as untrusted text: it matches regular expressions against it and does nothing else with it (`scripts/pre_bash_search_nudge.py`).
- **Claude Code → hook.** The harness starts the hook with the command from `hooks/hooks.json` and passes the payload on stdin. The hook's output is a `systemMessage` that Claude Code displays; it contains only fixed reminder texts from the script, never text taken from the payload.
- **Hook → temp directory.** The state files live in `file-search-hook-<uid>/` under the system temp directory (`tempfile.gettempdir()`). The hook creates that directory with mode 0700 and uses it only while it is a real directory owned by the user and closed to group and others; otherwise it keeps no state and shows every reminder. A state file's content only decides which reminders are suppressed as repeats.
- **CI.** Workflows run on GitHub-hosted runners. Every workflow sets `permissions: {}` at the top level and grants each job only what its reusable workflow needs (`.github/workflows/*.yml`).

## Threats and countermeasures

| Threat | Countermeasure | Evidence |
| --- | --- | --- |
| The hook runs the inspected command or text from it (CWE-78, CWE-94) | The script imports only `hashlib`, `json`, `os`, `re`, `stat`, `sys` and `tempfile`; it uses no `subprocess`, `eval`, `exec` or shell. The command is only matched with `re` | `scripts/pre_bash_search_nudge.py` |
| Payload text is echoed into the agent's context (prompt injection through the hook) | `main()` builds the message only from the fixed strings in `detect()`; no part of the command or session id is copied into the output | `detect()` and `main()` in `scripts/pre_bash_search_nudge.py` |
| A crafted `session_id` steers the state file out of the state directory (CWE-22) | The file name is built from the first 16 hex digits of the SHA-256 of the session id, never from the id itself | `_session_key()` in `scripts/pre_bash_search_nudge.py`; the case "Pfad-Traversal in der Session-ID" in `scripts/test_pre_bash_search_nudge.py` passes `../../../../tmp/evil-search` and asserts that the state file appears in the state directory under the digest name and that `/tmp/evil-search` is not created |
| Another local user reads, replaces or redirects the state (CWE-377, CWE-59) | The state directory is the user's own (mode 0700, checked with `lstat` for type, owner and permissions before use); files are opened with `O_NOFOLLOW` and written through a new file (`O_CREAT \| O_EXCL`) that is renamed into place | `_state_dir()`, `_read_seen()` and `_write_seen()` in `scripts/pre_bash_search_nudge.py`; the cases "Zustand in eigenem 0700-Verzeichnis", "Zustandsverzeichnis ist ein Symlink" and "Zustandsverzeichnis fuer alle schreibbar" in `scripts/test_pre_bash_search_nudge.py` |
| A malformed payload or an unusable state file makes the hook break the shell | Invalid JSON on stdin ends the script with exit 0 and no output; an `OSError` or invalid JSON when reading the state file, and an `OSError` when writing it, are caught and the reminders are shown; any other exception, from a payload of an unexpected shape or a state file with unexpected content, is caught by the top-level guard and ends with exit 0 and no output | `main()`, `first_per_session()` and the `__main__` guard in `scripts/pre_bash_search_nudge.py`; the four "exit 0 ohne Ausgabe" cases in `scripts/test_pre_bash_search_nudge.py` |
| A regression changes what the hook reports or suppresses | The behavioural tests run on every pull request and push to `main`; the script exits 1 when a case fails | `.github/workflows/tests.yml`, `scripts/test_pre_bash_search_nudge.py` |
| A release is tagged with inconsistent version metadata | Skill Validation checks that `SKILL.md` `metadata.version` matches `.claude-plugin/plugin.json`; the local pre-push hook runs `check-plugin-version.sh` for the same comparison | `.github/workflows/lint.yml`, `Build/hooks/pre-push`, `Build/Scripts/check-plugin-version.sh` |
| A secret is committed | Betterleaks scans every push to `main` and every pull request to `main` | `.github/workflows/security.yml` |
| A vulnerable or malicious dependency is added | Dependency review fails a pull request on vulnerabilities of severity high or above; Composer Audit checks the Composer dependencies against known advisories; Renovate proposes updates, including pre-commit hook revisions | `.github/workflows/security.yml`, `renovate.json` |
| Insecure code or workflow patterns | Opengrep scans the code (failure threshold: [organisation SAST rule](https://github.com/netresearch/.github/blob/main/SECURITY.md#static-analysis-sast)); zizmor analyses the workflows; Skill Validation runs ShellCheck at severity `error` on every `*.sh` file and `ruff check` / `ruff format --check` on every Python file | `.github/workflows/security.yml`, `.github/workflows/lint.yml` |

Which of these checks must pass before a pull request can merge is set in the branch protection of `main`, not in this repository.

## Secure design principles applied

- **Economy of mechanism:** the hook is one Python file using only the standard library, with three rules and no configuration.
- **Least privilege:** the hook needs no credentials, opens no network connection and writes only its state files, in a directory private to the user; the CI workflows start from `permissions: {}`.
- **Input treated as data:** the command is matched, never parsed into anything that runs, and the session id is hashed before it becomes part of a path.
- **Fail-safe for the user's work:** the hook cannot deny a command, so a defect in it can at worst produce a wrong or missing reminder.

## What a user cannot expect

- The hook is a reminder, not a control. It recognises the command shapes listed in `skills/file-search/references/enforcement-hook.md`; an agent can ignore the reminder or search by other means.
- The hook fails open by design: on a payload it cannot read, and on any other error while handling it, it prints nothing and exits 0; when its state directory or state file cannot be used it shows the reminder again. Under Claude Code's hook semantics a hook that exceeds its 3-second timeout (`hooks/hooks.json`) or fails does not block the command either.
- The commands the skill recommends are examples for the agent. The skill does not install rg, fd, ast-grep, rga, tokei, scc or semgrep; users obtain and update those tools from their own sources.
