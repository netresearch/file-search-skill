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
```

### npx ([skills.sh](https://skills.sh))

Install with any [Agent Skills](https://agentskills.io)-compatible agent:

```bash
npx skills add https://github.com/netresearch/file-search-skill --skill file-search
```

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
```

## License

This project uses split licensing:

- **Code** (scripts, workflows, configs): [MIT](LICENSE-MIT)
- **Content** (skill definitions, documentation, references): [CC-BY-SA-4.0](LICENSE-CC-BY-SA-4.0)

See the individual license files for full terms.
