<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- SPDX-FileCopyrightText: Netresearch DTT GmbH -->

# File Search Skill

[![CI](https://github.com/netresearch/file-search-skill/actions/workflows/lint.yml/badge.svg)](https://github.com/netresearch/file-search-skill/actions/workflows/lint.yml)
[![Release](https://img.shields.io/github/v/release/netresearch/file-search-skill?sort=semver)](https://github.com/netresearch/file-search-skill/releases)
[![License](https://img.shields.io/badge/license-MIT%20AND%20CC--BY--SA--4.0-blue.svg)](#license)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/netresearch/file-search-skill/badge)](https://securityscorecards.dev/viewer/?uri=github.com/netresearch/file-search-skill)

An AI agent skill that teaches efficient CLI-based code and file search
strategies. Provides tool selection guidance, pattern recipes, and best
practices for searching codebases of any size.

## Tools Covered

| Tool | Purpose | Replaces |
|------|---------|----------|
| [ripgrep](https://github.com/BurntSushi/ripgrep) (`rg`) | Ultra-fast text/regex search | `grep`, `grep -r` |
| [ast-grep](https://github.com/ast-grep/ast-grep) (`sg`) | Structural/syntax-aware code search | complex regex hacks |
| [semgrep](https://semgrep.dev/docs) (`semgrep`) | Security/lint rules at scale with taint analysis | hand-rolled regex CI checks |
| [fd](https://github.com/sharkdp/fd) (`fd`) | Fast file finder | `find` |
| [ripgrep-all](https://github.com/phiresky/ripgrep-all) (`rga`) | Search PDFs, Office docs, archives | manual text extraction |
| [tokei](https://github.com/XAMPPRocky/tokei) | Fast code statistics by language | `cloc`, `wc -l` |
| [scc](https://github.com/boyter/scc) | Code counter with complexity analysis | `cloc`, `tokei` (when complexity needed) |

## Key Principles

- **Use `rg` instead of `grep`** for text search in source code
- **Use `fd` instead of `find`** for file discovery
- **Use `rga` instead of `rg`** when searching non-code files (PDFs, Office docs, archives)
- **Use `sg` instead of regex** when matching code structure
- **Use `semgrep`** when you want a *catalog* of security/lint rules (taint, registry) — not just a single pattern
- **Use `tokei` or `scc`** to assess codebase size, not `cloc` or `wc -l`
- **Always start with targeted, narrow searches** and widen only if needed
- **Always specify file types/languages** to limit search scope
- **Count matches before viewing** full results to avoid overwhelming output

## Installation

### Marketplace (Recommended)

Add the [Netresearch marketplace](https://github.com/netresearch/claude-code-marketplace) once, then browse and install skills:

```bash
# Claude Code
/plugin marketplace add netresearch/claude-code-marketplace
/plugin install file-search@netresearch-claude-code-marketplace
```

### Without a marketplace

Since Claude Code 2.1.157 a plugin directory under your personal skills directory loads on its own, including the hooks this repo ships:

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/netresearch/file-search-skill.git \
  ~/.claude/skills/file-search
```

It loads as `file-search@skills-dir` on the next session. Update with `git -C ~/.claude/skills/file-search pull` and start a new session; remove it by deleting the directory. This route has no `claude plugin update`.

### npx ([skills.sh](https://skills.sh))

Install with any [Agent Skills](https://agentskills.io)-compatible agent:

```bash
npx skills add https://github.com/netresearch/file-search-skill --skill file-search
```

> **Limitation:** `npx skills` installs `SKILL.md`-based skills only. This repo also ships `hooks`, which it does not install — use the marketplace or the skills directory for those.

### Download Release

Download the [latest release](https://github.com/netresearch/file-search-skill/releases/latest) and extract to your agent's skills directory.

### Git Clone

```bash
git clone https://github.com/netresearch/file-search-skill.git
```

### Composer (PHP Projects)

```bash
composer require netresearch/file-search-skill
```

Requires [netresearch/composer-agent-skill-plugin](https://github.com/netresearch/composer-agent-skill-plugin).

### npm (Node Projects)

```bash
npm install --save-dev \
  @netresearch/agent-skill-coordinator \
  github:netresearch/file-search-skill
```

Requires [@netresearch/agent-skill-coordinator](https://github.com/netresearch/node-agent-skill-coordinator), which discovers the skill in `node_modules` and registers it in `AGENTS.md` via a `postinstall` hook. For pnpm, also allowlist the coordinator's postinstall:

```json
{
  "pnpm": {
    "onlyBuiltDependencies": ["@netresearch/agent-skill-coordinator"]
  }
}
```

## Skill Structure

```
skills/file-search/
  SKILL.md                          # Main skill file (tool selection, usage, best practices)
  evals/
    evals.json                      # Evaluation definitions for testing skill effectiveness
  references/
    ripgrep-patterns.md             # Extensive rg pattern recipes by use case
    ast-grep-patterns.md            # Structural search patterns by language
    semgrep-patterns.md             # Security/lint rules, taint mode, registry
    fd-guide.md                     # fd file finder guide
    rga-guide.md                    # ripgrep-all for non-code files
    search-strategies.md            # Search targeting strategies
    code-metrics.md                 # tokei/scc code statistics guide
    remote-handoff.md               # When to hand off to remote tools
    enforcement-hook.md             # What the PreToolUse search nudge says and stays out of
hooks/hooks.json                    # Registers the PreToolUse search nudge for the Bash tool
scripts/
  pre_bash_search_nudge.py          # The hook (Python, standard library only)
  test_pre_bash_search_nudge.py     # Its behavioural tests
```

The components and the hook's data flow are described in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Contributing

Contributions follow the [Netresearch contributing guide](https://github.com/netresearch/.github/blob/main/CONTRIBUTING.md). `pre-commit run --all-files` runs the Skill Validation linters locally; `pre-commit install --install-hooks` installs them as a commit hook, but pre-commit refuses while `core.hooksPath` is set, which `.envrc` does (it points git at `Build/hooks`). The local linters are stricter than CI in two places: markdownlint checks every Markdown file (CI: the root files), and ShellCheck runs at its default `style` severity (CI: `error`).

### Tests

The behavioural tests of the PreToolUse hook need only Python 3.10 or later:

```bash
python3 scripts/test_pre_bash_search_nudge.py
```

- The script runs `scripts/pre_bash_search_nudge.py` as a subprocess with a hook payload per case and checks the output. It covers the three reminders (`find`, recursive `grep`, plain `grep`), the commands that must stay silent (`rg`, `fd`, a `grep` behind a pipe, a `grep` on a `.json` file, search commands that only appear in a PR body, an `echo` or a `gh api -f body=` value), the once-per-rule-per-session deduplication (a second firing of the same rule is silent, another rule still fires, a new session warns again), and that a session id cannot steer the state file out of the temp directory.
- Each case prints one line: `OK` or `FEHL`, the case name, the expected result (`erwartet`) and the actual one (`ok` or `erhalten`). The last line is `---- Fehlschlaege: N`, the number of failing cases; the script exits 1 when N is not 0.
- When it finishes, the script deletes every `file-search-hook-seen-*` file in the system temp directory, so reminders already shown in a running session appear once more.

In CI, the Skill Tests workflow (`.github/workflows/tests.yml`) runs the script on every pull request and on pushes to `main`.

A pull request that changes what the hook reports or stays silent about adds a case to `scripts/test_pre_bash_search_nudge.py` that fails without the change.

## Governance and policies

This repository follows the Netresearch organisation policies:

- [Governance](https://github.com/netresearch/.github/blob/main/GOVERNANCE.md): ownership, roles, how decisions are made and disputes resolved, and continuity.
- [Roadmap](https://github.com/netresearch/.github/blob/main/ROADMAP.md): planned and explicitly excluded work for the coming year.
- [Handling of dependency and code analysis findings](https://github.com/netresearch/.github/blob/main/SECURITY.md#handling-of-dependency-and-code-analysis-findings): thresholds, deadlines and the exception process for dependency (SCA) and static analysis (SAST) findings.
- [Secret management](https://github.com/netresearch/.github/blob/main/SECURITY.md#secret-management): how CI and release credentials are stored, accessed and rotated.
- [Access roster](https://github.com/netresearch/.github/blob/main/docs/access-roster.md): who holds administrative access to this repository and the organisation.

The security assurance case for this skill (threat model, trust boundaries, countermeasures and limits) is in [docs/SECURITY-ASSURANCE.md](docs/SECURITY-ASSURANCE.md).

Checks that run on pull requests in this repository:

- Every pull request: Skill Validation (`lint.yml`: skill structure, manifest sync, markdownlint, yamllint, actionlint, JSON syntax, version parity, ShellCheck on `*.sh` files, ruff), Eval Validation (`eval-validate.yml`) and Skill Tests (`tests.yml`).
- Pull requests to `main`: `security.yml` with Betterleaks (secret scanning), zizmor (workflow static analysis), dependency review (fails on vulnerabilities of severity high or above), Composer Audit and Opengrep SAST (`--severity WARNING`: fails on findings of WARNING-level rules only; ERROR-level rules are not reported, see netresearch/typo3-ci-workflows#268); Harness Verification (`harness-verify.yml`) and Template Drift (`check-template-drift.yml`).

## License

This project uses split licensing:

- **Code** (scripts, workflows, configs): [MIT](LICENSE-MIT)
- **Content** (skill definitions, documentation, references): [CC-BY-SA-4.0](LICENSE-CC-BY-SA-4.0)

See the individual license files for full terms.
