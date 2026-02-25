# File Search Skill

An AI agent skill that teaches efficient CLI-based code and file search
strategies. Provides tool selection guidance, pattern recipes, and best
practices for searching codebases of any size.

## Tools Covered

| Tool | Purpose | Replaces |
|------|---------|----------|
| [ripgrep](https://github.com/BurntSushi/ripgrep) (`rg`) | Ultra-fast text/regex search | `grep`, `grep -r` |
| [ast-grep](https://github.com/ast-grep/ast-grep) (`sg`) | Structural/syntax-aware code search | complex regex hacks |
| [fd](https://github.com/sharkdp/fd) (`fd`) | Fast file finder | `find` |
| [ripgrep-all](https://github.com/phiresky/ripgrep-all) (`rga`) | Search PDFs, Office docs, archives | manual text extraction |
| [tokei](https://github.com/XAMPPRocky/tokei) | Fast code statistics by language | `cloc`, `wc -l` |
| [scc](https://github.com/boyter/scc) | Code counter with complexity analysis | `cloc`, `tokei` (when complexity needed) |

## Key Principles

- **Use `rg` instead of `grep`** for text search in source code
- **Use `fd` instead of `find`** for file discovery
- **Use `rga` instead of `rg`** when searching non-code files (PDFs, Office docs, archives)
- **Use `sg` instead of regex** when matching code structure
- **Use `tokei` or `scc`** to assess codebase size, not `cloc` or `wc -l`
- **Always start with targeted, narrow searches** and widen only if needed
- **Always specify file types/languages** to limit search scope
- **Count matches before viewing** full results to avoid overwhelming output

## Installation

Requires [Composer](https://getcomposer.org/) and the
[composer-agent-skill-plugin](https://github.com/netresearch/composer-agent-skill-plugin).

```bash
composer require netresearch/agent-file-search
```

## Skill Structure

```
skills/file-search/
  SKILL.md                          # Main skill file (tool selection, usage, best practices)
  references/
    ripgrep-patterns.md             # Extensive rg pattern recipes by use case
    ast-grep-patterns.md            # Structural search patterns by language
    tool-comparison.md              # Detailed comparison and decision guide
```

## License

MIT - see [LICENSE](LICENSE) for details.
