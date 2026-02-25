---
name: file-search
description: "Use when searching codebases for text patterns, structural code patterns, finding files by name, searching non-code files, or analyzing codebase size. Provides efficient tool selection guidance."
---

# File Search Skill

Efficient CLI search tools for AI agents. Covers tool selection, targeting
strategies, and best practices.

## Tool Selection Guide

| Task | Use | Instead of |
|------|-----|------------|
| Search text in code files | `rg` (ripgrep) | `grep`, `grep -r` |
| Find files by name/path | `fd` | `find`, `ls -R` |
| Structural/syntax-aware code search | `sg` (ast-grep) | regex hacks |
| Search PDFs, Office docs, archives | `rga` (ripgrep-all) | manual extraction |
| Count lines of code by language | `tokei` | `cloc`, `wc -l` |
| Code stats with complexity metrics | `scc` | `cloc`, `tokei` |

**Decision flow:**

1. Text pattern in source code? --> `rg`
2. Code structure (function signatures, class patterns)? --> `sg`
3. Files by name, extension, or type? --> `fd`
4. Inside PDFs, Word docs, spreadsheets, archives? --> `rga`
5. Codebase size/language breakdown? --> `tokei` or `scc`

## Quick Examples

**rg** -- text/regex search:
```bash
rg 'def \w+\(' -t py src/          # Python function defs in src/
rg -c 'TODO' -t js | wc -l         # count files with TODOs
rg 'pattern' -g '!vendor/' -g '!node_modules/'  # exclude noise
```

**sg** -- structural/AST search:
```bash
sg --pattern 'if $ERR != nil { return $ERR }' --lang go   # unwrapped errors
sg --pattern 'console.log($$$)' --rewrite 'logger.info($$$)' --lang js
```

**fd** -- find files:
```bash
fd -e py --changed-within 1d        # Python files changed today
fd -g '*_test.go' -X rg 'func Test' # verify test files have tests
```

## Targeting Your Searches

- **Specify file types** (`rg -t py`, `sg --lang go`, `fd -e ts`) to cut
  search space dramatically.
- **Limit directory scope** (`rg pattern src/api/`) -- never search from root.
- **Count before viewing** (`rg -c pattern -t py | wc -l`) -- if results
  exceed ~50 files, narrow the search.
- **Exclude noise** (`-g '!vendor/'`, `fd -E node_modules`) -- skip generated
  and vendored code.

See [references/search-strategies.md](references/search-strategies.md) for
progressive refinement workflows.

## Best Practices

1. **Start narrow, widen if needed.** Begin with the most specific search.
2. **Use `fd` for files, `rg` for content.** Do not use `find` or `grep -r`.
3. **Use `rga` for non-code files.** Not manual text extraction from PDFs.
4. **Use `sg` for structural patterns.** If regex is fragile, use ast-grep.
5. **Use `--json` output** when results feed into further processing.
6. **Combine tools:** `fd -e py --changed-within 1d -X rg 'TODO'`

## References

| Topic | File |
|-------|------|
| rg flags, patterns, recipes | [references/ripgrep-patterns.md](references/ripgrep-patterns.md) |
| ast-grep patterns by language | [references/ast-grep-patterns.md](references/ast-grep-patterns.md) |
| fd flags, usage, fd+rg combos | [references/fd-guide.md](references/fd-guide.md) |
| rga formats, usage, caching | [references/rga-guide.md](references/rga-guide.md) |
| tokei and scc usage | [references/code-metrics.md](references/code-metrics.md) |
| Search targeting strategies | [references/search-strategies.md](references/search-strategies.md) |
| Tool comparison and decision guide | [references/tool-comparison.md](references/tool-comparison.md) |
