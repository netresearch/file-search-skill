---
name: file-search
description: "Use when searching codebases (text, structural/AST, files by name, PDFs/archives, code stats) or building context before a task."
license: "(MIT AND CC-BY-SA-4.0). See LICENSE-MIT and LICENSE-CC-BY-SA-4.0"
compatibility: "Requires ripgrep (rg). Optional: fd, ast-grep, rga, tokei, scc, semgrep."
metadata:
  author: Netresearch DTT GmbH
  version: "1.6.1"
  repository: https://github.com/netresearch/file-search-skill
allowed-tools: Bash(rg:*) Bash(fd:*) Bash(sg:*) Bash(rga:*) Bash(tokei:*) Bash(scc:*) Bash(semgrep:*) Read Glob Grep
---

# File Search Skill

Efficient CLI search tools for AI agents.

## Tool Selection Guide

| Task | Use | Instead of |
|------|-----|------------|
| Search text in code files | `rg` (ripgrep) | `grep`, `grep -r` |
| Find files by name/path | `fd` | `find`, `ls -R` |
| Structural/syntax-aware code search | `sg` (ast-grep) | regex hacks |
| Apply rule packs (security/lint, taint) | `semgrep` | regex CI checks |
| Search PDFs, Office docs, archives | `rga` (ripgrep-all) | manual extraction |
| Count lines of code by language | `tokei` | `cloc`, `wc -l` |
| Code stats with complexity metrics | `scc` | `cloc`, `tokei` |

**Decision flow:** text → `rg` | structural → `sg` | rule packs →
`semgrep` | filenames → `fd` | PDFs/archives → `rga` | LOC →
`tokei`/`scc`

## Quick Examples

```bash
rg 'def \w+\(' -t py src/          # rg: text search in Python files
rg -c 'TODO' -t js | wc -l         # rg: count first, then drill down
sg --pattern 'console.log($$$)' --rewrite 'logger.info($$$)' --lang js  # sg: structural replace
fd -g '*.test.ts' --changed-within 1d  # fd: -g for compound suffixes (NOT -e)
fd -g '*_test.go' -X rg 'func Test'   # fd+rg: find files, verify contents
rga 'quarterly revenue' docs/       # rga: search inside PDFs/archives
tokei --sort code                   # tokei: language stats
scc --wide                          # scc: complexity + COCOMO
```

## Best Practices

1. **Start narrow.** Specify types (`-t`, `--lang`, `-e`), scope dirs, count first (`rg -c`).
2. **Exclude noise** (`-g '!vendor/'`, `fd -E node_modules`).
3. **Batch independent queries.** Union patterns with `rg -e P1 -e P2 -e P3` (one walk, one process), or issue distinct queries as parallel tool calls in a single message — never sequential `&&` chains for independent searches.
4. **`--json`** for programmatic processing.
5. **rg ≠ fd types.** `rg -t ts` includes `.tsx`; `fd -e ts` does NOT. No `-t tsx` in rg.

See [references/search-strategies.md](references/search-strategies.md).

## Beyond Local Files

If local search finds nothing and context lives in issues/PRs/external
docs — hand off (`gh`, Jira, WebFetch). Issue keys in comments signal this.

See [references/remote-handoff.md](references/remote-handoff.md).

## References

| Topic | File |
|-------|------|
| rg flags, patterns, recipes | [references/ripgrep-patterns.md](references/ripgrep-patterns.md) |
| ast-grep patterns by language | [references/ast-grep-patterns.md](references/ast-grep-patterns.md) |
| semgrep rules and taint mode | [references/semgrep-patterns.md](references/semgrep-patterns.md) |
| fd flags, usage, fd+rg combos | [references/fd-guide.md](references/fd-guide.md) |
| rga formats, usage, caching | [references/rga-guide.md](references/rga-guide.md) |
| tokei and scc usage | [references/code-metrics.md](references/code-metrics.md) |
| Search targeting strategies | [references/search-strategies.md](references/search-strategies.md) |
| Tool comparison and decision guide | [references/tool-comparison.md](references/tool-comparison.md) |
| Remote context handoff guide | [references/remote-handoff.md](references/remote-handoff.md) |
