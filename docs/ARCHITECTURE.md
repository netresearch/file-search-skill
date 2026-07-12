# Architecture — file-search-skill

## Overview

An AI agent skill that teaches efficient CLI-based code and file search strategies. Covers tool selection (ripgrep, fd, ast-grep, rga, tokei, scc), targeting patterns, and best practices for searching codebases of any size.

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
- **fd-guide.md** — fd file finder usage and patterns
- **rga-guide.md** — ripgrep-all for PDFs, Office docs, archives
- **search-strategies.md** — search targeting and narrowing strategies
- **code-metrics.md** — tokei and scc for code statistics and complexity
- **remote-handoff.md** — guidance on when to hand off to remote tools (issues, PRs, wikis)

### Evals (`skills/file-search/evals/`)

Evaluation definitions for testing skill effectiveness with AI agents.

### Build Infrastructure (`Build/`)

- **Scripts/check-plugin-version.sh** — validates plugin.json and SKILL.md versions stay in sync
- **hooks/pre-push** — git pre-push hook that runs version validation before pushing

### CI Workflows (`.github/workflows/`)

- **release.yml** — creates releases on tag push (reusable from skill-repo-skill)
- **lint.yml** — skill structure validation and linting (reusable from skill-repo-skill)
- **harness-verify.yml** — AGENTS.md harness consistency checks
- **auto-merge-deps.yml** — auto-merge Dependabot/Renovate PRs

## Design Decisions

- **No runtime code**: this repo contains only documentation and skill metadata.
- **Split licensing**: code under MIT, content under CC-BY-SA-4.0.
- **Composer integration**: published as a PHP package for projects using the composer-agent-skill-plugin.
- **Comprehensive references**: each tool has its own dedicated reference doc for deep-dive usage.
- **Cross-platform scripts**: all shell scripts use `grep -E` (not `-P`) for macOS/Linux compatibility.
