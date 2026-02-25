---
name: file-search
description: "Use when searching codebases for text patterns, structural code patterns, finding files by name, searching non-code files, or analyzing codebase size. Provides efficient tool selection guidance."
---

# File Search Skill

Efficient CLI search tools for AI agents. This skill covers tool selection,
targeting strategies, and best practices for searching codebases and files.

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

1. Searching for a text pattern in source code? --> `rg`
2. Searching for a code structure (function signatures, class patterns)? --> `sg`
3. Finding files by name, extension, or type? --> `fd`
4. Searching inside PDFs, Word docs, spreadsheets, archives? --> `rga`
5. Need codebase size/language breakdown? --> `tokei` or `scc`

---

## ripgrep (rg)

Ultra-fast recursive text search. Respects `.gitignore` by default, supports
PCRE2 regex, and provides structured output options.

### Key Flags

```
-i              Case-insensitive search
-w              Match whole words only
-l              List matching file paths only (no content)
-c              Count matches per file
-n              Show line numbers (default)
-t TYPE         Restrict to file type (e.g., -t py, -t js, -t go)
-T TYPE         Exclude file type
-g 'GLOB'       Filter by glob pattern (e.g., -g '*.tsx')
--json          Machine-readable JSON output
-A N / -B N     Show N lines after/before match
-C N            Show N lines of context (before + after)
-U              Enable multiline matching
--hidden        Include hidden files (dotfiles)
--no-ignore     Search files ignored by .gitignore
-F              Treat pattern as fixed string (no regex)
-e PATTERN      Specify pattern (useful for multiple patterns or leading dashes)
--count-matches Total match count (not per-file)
-r REPLACEMENT  Replace matches in output (preview, does not modify files)
```

### Progressive Refinement Strategy

Start narrow, widen only if needed:

```bash
# 1. Count matches first to gauge scope
rg -c 'pattern' -t py

# 2. If too many, narrow by directory
rg -c 'pattern' -t py src/core/

# 3. View results with context
rg -n -C 2 'pattern' -t py src/core/

# 4. If still too many, add word boundaries or refine regex
rg -nw 'exactFunction' -t py src/core/
```

### Common Patterns

```bash
# Find function definitions in Python
rg 'def \w+\(' -t py

# Find class definitions in TypeScript
rg 'class \w+' -t ts

# Find all imports of a module
rg "from ['\"](react|vue)" -t js -t ts

# Find TODO/FIXME comments
rg '(TODO|FIXME|HACK|XXX):' -n

# Find environment variable usage
rg '\$\{?\w+\}?' -t sh

# Find SQL injection risks
rg 'execute\(.*\+.*\)' -t py
rg '\$\w+.*->query\(' -t php

# Search with multiple patterns
rg -e 'pattern1' -e 'pattern2' -t js

# Search for multiline patterns (e.g., function with decorator)
rg -U '@deprecated\n.*def \w+' -t py

# Exclude directories
rg 'pattern' -g '!vendor/' -g '!node_modules/'

# Fixed string search (no regex interpretation)
rg -F 'array_map($callback, $items)' -t php
```

### File Type Targeting

ripgrep has built-in type definitions. List all with `rg --type-list`.

Common types: `py`, `js`, `ts`, `go`, `rust`, `java`, `php`, `ruby`, `css`,
`html`, `json`, `yaml`, `toml`, `md`, `sh`, `sql`, `c`, `cpp`.

```bash
# Multiple types
rg 'pattern' -t js -t ts

# Custom type definition (one-off)
rg --type-add 'web:*.{html,css,js}' -t web 'pattern'
```

See [references/ripgrep-patterns.md](references/ripgrep-patterns.md) for
extensive pattern recipes.

---

## ast-grep (sg)

Structural code search using AST (Abstract Syntax Tree) matching. Finds code
by structure, not text -- immune to formatting differences and comments.

### When to Use ast-grep Over ripgrep

- Matching code **structure** regardless of formatting/whitespace
- Finding function calls with specific argument patterns
- Matching patterns that span multiple lines unpredictably
- Refactoring patterns (find + replace structurally)
- When regex would be too fragile for the code pattern

### Metavariable Syntax

| Syntax | Meaning |
|--------|---------|
| `$VAR` | Matches a single AST node (expression, identifier, etc.) |
| `$$$` | Matches zero or more nodes (variadic, like `...args`) |
| `$$_` | Matches zero or more nodes (unnamed wildcard) |

### Basic Usage

```bash
# Search with a pattern in a language
sg --pattern 'console.log($$$)' --lang js

# Search in specific directory
sg --pattern 'fmt.Errorf($$$)' --lang go src/

# JSON output for programmatic use
sg --pattern '$FUNC($$$)' --lang py --json
```

### Quick Examples by Language

```bash
# JavaScript/TypeScript: find useState hooks
sg --pattern 'const [$STATE, $SETTER] = useState($$$)' --lang tsx

# Python: find decorated functions
sg --pattern '@$DECORATOR
def $NAME($$$):
    $$$' --lang py

# Go: find error handling without wrap
sg --pattern 'if $ERR != nil { return $ERR }' --lang go

# PHP: find method calls
sg --pattern '$this->$METHOD($$$)' --lang php
```

See [references/ast-grep-patterns.md](references/ast-grep-patterns.md) for
comprehensive patterns by language (JS/TS, Python, PHP, Go, Rust).

---

## fd

Fast, user-friendly file finder. Replaces `find` with sane defaults: respects
`.gitignore`, colorized output, regex by default, smart case.

### Key Flags

```
-e EXT          Filter by extension (-e py, -e rs)
-t TYPE         Filter by type: f (file), d (directory), l (symlink), x (executable)
-H              Include hidden files
-I              Do not respect .gitignore
-E PATTERN      Exclude glob pattern
-d DEPTH        Limit directory depth
-x CMD          Execute command for each result
-X CMD          Execute command with all results at once
-0              Null-byte separator (for xargs -0)
-a              Show absolute paths
-L              Follow symlinks
-g GLOB         Use glob pattern instead of regex
-p              Match against full path (not just filename)
--changed-within TIME   Files modified within duration (e.g., 1h, 2d, 1w)
--changed-before TIME   Files modified before duration
-S / --size     Filter by size (e.g., +1m for >1MB)
```

### Common Usage

```bash
# Find Python files
fd -e py

# Find all test files
fd 'test_.*\.py$'
fd -g '*_test.go'

# Find files modified in the last day
fd -e js --changed-within 1d

# Find large files
fd -S +10m

# Find and delete all .pyc files
fd -e pyc -x rm {}

# Find directories named "test" or "tests"
fd -t d '^tests?$'

# Find executable files
fd -t x

# Find files excluding certain directories
fd -e ts -E node_modules -E dist

# Find hidden config files
fd -H '^\.' -t f

# Find files and pipe to rg for content search
fd -e py | xargs rg 'import os'
```

### fd + rg Combinations

```bash
# Find Python files, then search for a pattern
fd -e py -x rg -l 'async def'

# Find recently changed files and search them
fd --changed-within 2h -e ts -X rg 'TODO'

# Find config files and search for a key
fd -g '*.{yml,yaml,toml,json}' -X rg 'database'
```

---

## rga (ripgrep-all)

Extends ripgrep to search inside PDFs, Word/Excel/PowerPoint, SQLite databases,
compressed archives, and more.

### When to Use rga Instead of rg

- Searching PDF documents for text
- Searching Word (.docx), Excel (.xlsx), PowerPoint (.pptx) files
- Searching inside .zip, .tar.gz, .tar.bz2 archives
- Searching SQLite database contents
- Searching EPUB ebooks

### Supported Formats

| Format | Extension |
|--------|-----------|
| PDF | `.pdf` |
| Word | `.docx`, `.doc` |
| Excel | `.xlsx`, `.xls` |
| PowerPoint | `.pptx`, `.ppt` |
| OpenDocument | `.odt`, `.ods`, `.odp` |
| Archive | `.zip`, `.tar`, `.tar.gz`, `.tar.bz2`, `.tar.xz` |
| SQLite | `.db`, `.sqlite`, `.sqlite3` |
| EPUB | `.epub` |

### Usage

```bash
# Search PDFs for a term
rga 'quarterly revenue' docs/

# Search all document types
rga 'confidential' --rga-adapters=+pdfpages,poppler /path/to/docs/

# Search inside archives
rga 'config' backups/*.tar.gz

# Search with ripgrep flags (most rg flags work)
rga -i -c 'error' logs/

# List matching files only
rga -l 'password' /shared/docs/
```

### Cache Behavior

rga caches extracted text for faster subsequent searches. The cache is stored
in the system cache directory. Use `--rga-no-cache` to disable.

---

## tokei and scc

Fast codebase analysis tools for counting lines of code, comments, and blanks
by language.

### tokei

```bash
# Basic usage -- counts all code in current directory
tokei

# Count specific directory
tokei src/

# Sort by lines of code
tokei --sort code

# Specific languages only
tokei --type=Python,JavaScript

# Output as JSON for processing
tokei --output json

# Exclude directories
tokei --exclude='vendor/*' --exclude='node_modules/*'
```

### scc

Like tokei but adds complexity estimation and COCOMO cost modeling.

```bash
# Basic usage
scc

# Specific directory
scc src/

# Sort by lines of code
scc --sort-by code

# Include complexity and COCOMO
scc --wide

# Specific languages
scc --include-ext py,js,ts

# Exclude directories
scc --exclude-dir vendor,node_modules

# Output as JSON
scc --format json
```

### When to Use Which

| Need | Tool |
|------|------|
| Quick language breakdown | `tokei` |
| Complexity estimates / cost modeling | `scc` |
| CI integration / badge generation | `scc` (has badge output) |
| Fastest possible count | `tokei` |

---

## Targeting Your Searches (Critical)

Unfocused searches produce overwhelming output. Always scope searches
deliberately:

### 1. Specify File Types

```bash
# Good: targeted by type
rg 'pattern' -t py
sg --pattern '$FUNC($$$)' --lang go

# Bad: search everything
rg 'pattern'
```

### 2. Limit Directory Scope

```bash
# Good: specific directory
rg 'pattern' src/api/
fd -e ts src/components/

# Bad: search from root
rg 'pattern' /
```

### 3. Count Before Viewing

```bash
# First: how many matches?
rg -c 'pattern' -t py | wc -l    # number of files
rg --count-matches 'pattern' -t py  # total matches per file

# Then: view if manageable
rg -n 'pattern' -t py
```

### 4. Progressive Refinement

```bash
# Start: broad count
rg -c 'import' -t py | wc -l
# => 847 files -- too many

# Narrow: specific module
rg -c 'from requests import' -t py | wc -l
# => 23 files -- manageable

# View: with context
rg -n -C 1 'from requests import' -t py
```

### 5. Exclude Noise

```bash
# Exclude generated/vendor code
rg 'pattern' -g '!vendor/' -g '!node_modules/' -g '!*.min.js' -g '!dist/'
fd -e py -E __pycache__ -E .venv -E '*.pyc'
```

---

## Best Practices

1. **Start narrow, widen if needed.** Begin with the most specific search you
   can formulate. Only broaden scope if you get no results.

2. **Always specify file types** when you know what you are looking for. This
   cuts search space dramatically.

3. **Count matches first** (`rg -c`, `rg -l | wc -l`) before viewing full
   output. If results exceed ~50 files, narrow the search.

4. **Use `fd` for file discovery, `rg` for content search.** Do not use
   `find` or `grep -r`. These are slower and lack `.gitignore` awareness.

5. **Use `rga` for non-code files.** Do not try to extract text from PDFs or
   Office docs manually. `rga` handles this transparently.

6. **Use `sg` for structural patterns.** If you find yourself writing complex
   regex to match code structure, switch to ast-grep.

7. **Use `tokei` or `scc` for codebase metrics.** Do not use `cloc` (slow)
   or `wc -l` (inaccurate -- counts blanks and comments).

8. **Combine tools** for powerful workflows:
   ```bash
   fd -e py --changed-within 1d -X rg 'TODO'  # TODOs in recently changed Python files
   rg -l 'deprecated' -t py | xargs sg --pattern 'def $NAME($$$)' --lang py
   ```

9. **Use `--json` output** when results feed into further processing or when
   you need structured data (file paths, line numbers, match text).

10. **Respect gitignore by default.** All tools here respect `.gitignore`
    unless told otherwise. Use `--hidden` / `--no-ignore` / `-H` / `-I` only
    when you explicitly need ignored or hidden files.

---

## References

- [ripgrep Pattern Recipes](references/ripgrep-patterns.md) - Extensive rg patterns by use case
- [ast-grep Pattern Recipes](references/ast-grep-patterns.md) - Structural search patterns by language
- [Tool Comparison](references/tool-comparison.md) - Detailed comparison and decision guide
