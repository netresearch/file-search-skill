<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- SPDX-FileCopyrightText: Netresearch DTT GmbH -->

# Architecture — file-search-skill

## Overview

An AI agent skill that teaches efficient CLI-based code and file search strategies. Covers tool selection (ripgrep, fd, ast-grep, rga, tokei, scc, semgrep), targeting patterns, and best practices for searching codebases of any size. Most of the repository is documentation for the agent. One executable component ships with it: a Claude Code `PreToolUse` hook that inspects each Bash command the agent is about to run and, when it is a `find` or `grep` search, shows a one-time reminder to use the search tools instead.

## Actors

- **AI agent** (Claude Code or another Agent Skills client): reads `SKILL.md` and the references as instructions and proposes Bash commands.
- **Claude Code harness**: loads the plugin, calls the hook before every Bash tool call, and shows the hook's message.
- **Skill user**: installs the plugin (marketplace, skills directory, npm, Composer, release archive or clone; see README) and runs the agent sessions.
- **Maintainers and contributors**: change the repository through pull requests; CI on GitHub Actions validates each change.

## Components

### Skill Definition (`skills/file-search/SKILL.md`)

Main entry point loaded by agent frameworks. Contains:
- Tool selection decision flow (task type → tool mapping)
- Quick-reference examples for each tool
- Targeting and scoping best practices

### Reference Docs (`skills/file-search/references/`)

Detailed guides for each tool:
- **ripgrep-patterns.md** — rg flags, regex patterns, and recipes by use case
- **ast-grep-patterns.md** — structural/AST search patterns organized by language
- **semgrep-patterns.md** — security/lint rules, taint mode, registry
- **fd-guide.md** — fd file finder usage and patterns
- **rga-guide.md** — ripgrep-all for PDFs, Office docs, archives
- **search-strategies.md** — search targeting and narrowing strategies
- **code-metrics.md** — tokei and scc for code statistics and complexity
- **remote-handoff.md** — guidance on when to hand off to remote tools (issues, PRs, wikis)
- **enforcement-hook.md** — what the PreToolUse hook reminds about, what it stays out of, and how to verify it

### PreToolUse hook (`hooks/hooks.json`, `scripts/pre_bash_search_nudge.py`)

`hooks/hooks.json` registers the hook for the `Bash` tool: Claude Code runs `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pre_bash_search_nudge.py` before each Bash call, with a timeout of 3 seconds. The script uses only the Python standard library.

**Input.** The harness writes a JSON payload to the script's stdin. The script reads `tool_name`, `tool_input.command`, and `session_id` (or, when that is absent, the file name of `transcript_path`). Anything other than a Bash call with a non-empty command, or a payload that is not valid JSON, ends the script with exit 0 and no output. Any other error while handling the payload or the state file (valid JSON of an unexpected shape, a state file with unexpected content) is caught at the top level and also ends the script with exit 0 and no output.

**Processing.** The command is only analysed with regular expressions; the script never executes it.

1. Parts that are data rather than commands are removed: bodies of quoted heredocs, and the values of `--body`, `--message`, `--notes`, `--description`, `--title`, `--comment`, `-m`, `-F` and `-f field=` options. A command that then starts with `echo` or `printf` gets no message.
2. **`find`** at the start of the command → reminder to use the Glob tool or `fd`.
3. **Recursive grep** (`grep -r`/`-R`, at the start or after `|`, `&` or `;`) → reminder to use the Grep tool or `rg`, and `sg` for structural patterns.
4. **Plain grep** at the start of the command → reminder to prefer the Grep tool or `rg`.
5. The grep rules stay silent when the command names a structured file (`.json`, `.jsonl`, `.yaml`, `.yml`, `.toml`, `.xml`, `.csv`, `.tsv`); those belong to the data-tools plugin's gate. A `grep` behind a pipe that is not recursive is output filtering and gets no message.

**Output.** When a rule fires for the first time in a session, the script prints one JSON object with `systemMessage` (the reminders, prefixed `file-search:`) and `suppressOutput: true`; the command runs unchanged. Otherwise it prints nothing. The hook never denies a command. Every path exits 0.

**State.** For the once-per-rule-per-session behaviour the script keeps a JSON list of hashes of the reminders already shown in `seen-<first 16 hex of SHA-256(session id)>.json` inside `file-search-hook-<uid>/` in the system temp directory (`tempfile.gettempdir()`). The script creates that directory with mode 0700 and, on POSIX systems, uses it only while it is a real directory owned by the user and closed to group and others; it opens the state file with `O_NOFOLLOW`. Windows offers neither check, and the per-user temp directory stands in for them there. The state is written through a new file that is renamed into place. Hashing the session id keeps the file name inside that directory whatever the payload contains. When there is no session id, the directory is not usable, or the file cannot be read or written, every reminder is shown; a state file whose content makes `set()` or `sorted()` fail (a number, `null`, a list of lists or of numbers) ends the run through the top-level guard, with exit 0 and no reminder. An object or a string is read as the set of its keys or characters, and the reminder is shown.

### Evals (`skills/file-search/evals/`)

`evals.json` holds evaluation definitions for testing skill effectiveness with AI agents. The Eval Validation workflow validates their structure; it does not run them against an agent.

### Repository tooling

- `scripts/test_pre_bash_search_nudge.py` — behavioural tests for the hook: it feeds each case to the script as a subprocess and compares the output. The Skill Tests workflow (`.github/workflows/tests.yml`) runs it.
- `Build/Scripts/check-plugin-version.sh` — fails when the version in `.claude-plugin/plugin.json` differs from `metadata.version` in `SKILL.md`. `Build/hooks/pre-push` runs it; `.envrc` points `core.hooksPath` at `Build/hooks` for direnv users.
- `scripts/verify-harness.sh` — checks AGENTS.md and the docs layout for agent-harness consistency.
- `.pre-commit-config.yaml` — local hooks (whitespace, JSON/YAML syntax, skill validation, version parity, markdownlint, yamllint, actionlint, ruff, ShellCheck).

### CI Workflows (`.github/workflows/`)

- **lint.yml** — skill structure validation and linting (reusable from skill-repo-skill)
- **tests.yml** — runs the hook's behavioural tests (reusable from skill-repo-skill)
- **eval-validate.yml** — validates the eval definitions
- **security.yml** — Betterleaks, zizmor, dependency review, Composer Audit and Opengrep
- **harness-verify.yml** — AGENTS.md harness consistency checks
- **check-template-drift.yml** — compares the template-managed workflows with the central skill template
- **scorecard.yml** — OpenSSF Scorecard on pushes to `main` and weekly
- **labeler.yml** — labels pull requests
- **release.yml** — creates releases on tag push (reusable from skill-repo-skill)
- **auto-merge-deps.yml** — auto-merge Dependabot/Renovate PRs

All workflow files except `tests.yml` are managed by the central skill template in `netresearch/.github`.

## Data flow

```
Agent proposes Bash command
        │
        ▼
Claude Code ── JSON payload (stdin) ──▶ pre_bash_search_nudge.py
        ▲                                   │  reads/writes seen-state file in its
        │                                   │  own 0700 directory under the temp dir
        └──── systemMessage or nothing (stdout), exit 0
```

The skill content flows one way: the agent framework reads `SKILL.md` and the references from the installed plugin. Neither the skill content nor the hook sends data over the network. Of the repository tooling, only `scripts/verify-harness.sh` makes a network call: `gh api` to check whether the organisation's `.github` repository has a pull request template.

## Design Decisions

- **Documentation plus one reminder**: the rule is taught by the skill content and reinforced by the hook, which ships in the same plugin so installing the skill installs the reminder (`references/enforcement-hook.md`).
- **Warn only, once per rule per session**: a shell search is never blocked; repeated reminders add nothing after the first (`scripts/pre_bash_search_nudge.py` docstring).
- **Fail open**: the hook exits 0 on malformed input, on any error while handling it, and when its state file is unusable, so a broken hook never blocks the shell.
- **Split licensing**: code under MIT, content under CC-BY-SA-4.0.
- **Composer integration**: published as a PHP package for projects using the composer-agent-skill-plugin.
- **Comprehensive references**: each tool has its own dedicated reference doc for deep-dive usage.
- **Cross-platform scripts**: the shell scripts use `grep -E` (not `-P`) for macOS/Linux compatibility.

Update this document in the same pull request when a component, an input or an output of the hook changes.
