# Tool Comparison and Decision Guide

Detailed comparison of the file search tools covered by this skill, with
guidance on when to use each one.

---

## Quick Decision Flowchart

```
What are you trying to do?
|
|-- Search for TEXT PATTERNS in files?
|   |
|   |-- In source code files?
|   |   --> Use rg (ripgrep)
|   |
|   |-- In PDFs, Word docs, Excel, archives?
|   |   --> Use rga (ripgrep-all)
|   |
|   |-- Need to match CODE STRUCTURE (not just text)?
|       --> Use sg (ast-grep)
|
|-- Find FILES by name, path, or attributes?
|   --> Use fd
|
|-- Count lines of code / analyze codebase?
    |
    |-- Just language breakdown and line counts?
    |   --> Use tokei
    |
    |-- Need complexity metrics or cost estimates?
        --> Use scc
```

---

## Feature Comparison: Text Search Tools

| Feature | rg (ripgrep) | rga (ripgrep-all) | sg (ast-grep) |
|---------|-------------|-------------------|---------------|
| **Primary use** | Text/regex search in files | Text search in any document | Structural code search |
| **Search method** | Regex (PCRE2) | Regex (via rg) | AST pattern matching |
| **Speed** | Extremely fast | Fast (with caching) | Fast (per language) |
| **Respects .gitignore** | Yes (default) | Yes (default) | Yes |
| **Multi-language** | Via file type filters | Via file type filters | Per-language parsers |
| **Format awareness** | Plain text only | PDF, Office, archives, SQLite | Source code ASTs |
| **Multiline** | With `-U` flag | With `-U` flag | Natural (AST-based) |
| **Replace support** | Preview only (`-r`) | No | Yes (structural rewrite) |
| **JSON output** | Yes (`--json`) | Yes | Yes (`--json`) |
| **Whitespace sensitive** | Yes | Yes | No (AST-based) |
| **Comment aware** | No | No | Yes (can skip comments) |

### When to Choose Which

**Choose rg when:**
- Searching for string literals, log messages, error codes
- Searching for simple patterns like function names, variable names
- Searching across all file types simultaneously
- You need maximum speed on large codebases
- The pattern is straightforward text or regex

**Choose rga when:**
- Searching inside PDF documents
- Searching inside Word, Excel, PowerPoint files
- Searching inside compressed archives (.zip, .tar.gz)
- Searching SQLite database contents
- You need rg features but on non-plaintext files

**Choose sg when:**
- Matching function calls with specific argument patterns
- Finding code structures regardless of formatting
- Matching patterns that span multiple lines unpredictably
- Finding anti-patterns or code smells structurally
- You need to ignore comments and whitespace in matches
- Regex would be too fragile for the code pattern

---

## Feature Comparison: File Finding

| Feature | fd | find (system) |
|---------|------|------|
| **Speed** | Very fast (parallel) | Slower (single-threaded) |
| **Respects .gitignore** | Yes (default) | No |
| **Regex support** | Yes (default mode) | Limited (`-regex`) |
| **Glob support** | Yes (`-g`) | Yes (`-name`) |
| **Smart case** | Yes (default) | No |
| **Colored output** | Yes | No |
| **Syntax** | Intuitive | Verbose |
| **Execution** | `-x` (each), `-X` (batch) | `-exec`, `-exec +` |
| **Size filter** | `-S` | `-size` |
| **Time filter** | `--changed-within/before` | `-mtime`, `-newer` |

### fd vs find: Syntax Comparison

| Task | fd | find |
|------|------|------|
| Find .py files | `fd -e py` | `find . -name '*.py'` |
| Find by regex | `fd 'test_.*'` | `find . -regex '.*test_.*'` |
| Find directories | `fd -t d` | `find . -type d` |
| Find + delete | `fd -e pyc -x rm {}` | `find . -name '*.pyc' -exec rm {} \;` |
| Exclude dir | `fd -E vendor` | `find . -path ./vendor -prune -o -print` |
| Modified today | `fd --changed-within 1d` | `find . -mtime 0` |
| Size > 1MB | `fd -S +1m` | `find . -size +1M` |

**Always use fd instead of find.** It is faster, has better defaults, and
requires less typing.

---

## Feature Comparison: Code Statistics

| Feature | tokei | scc | cloc | wc -l |
|---------|-------|-----|------|-------|
| **Speed** | Very fast | Very fast | Slow | Fast |
| **Language detection** | Yes (200+) | Yes (200+) | Yes (200+) | No |
| **Separates code/comments/blanks** | Yes | Yes | Yes | No |
| **Complexity metrics** | No | Yes (per file) | No | No |
| **COCOMO estimates** | No | Yes | Yes | No |
| **Badge generation** | No | Yes | No | No |
| **Respects .gitignore** | Yes | Yes | No | No |
| **JSON output** | Yes | Yes | Yes | No |
| **Binary detection** | Yes | Yes | Yes | No |

### When to Choose Which

**Choose tokei when:**
- You need a fast, accurate language breakdown
- You want lines of code separated by code, comments, blanks
- You need reliable .gitignore support
- You want the fastest possible count

**Choose scc when:**
- You need complexity estimates alongside line counts
- You need COCOMO cost modeling
- You want to generate badges for a README
- You need per-file breakdowns with complexity

**Do NOT use:**
- `cloc` -- significantly slower, no advantage over tokei/scc
- `wc -l` -- counts all lines including blanks and comments, does not detect
  languages, gives misleading results

---

## Performance Characteristics

Approximate performance on a large codebase (~500K files, 50M lines):

| Tool | Typical Time | Notes |
|------|-------------|-------|
| rg (targeted, -t py) | < 1s | File type filter is key |
| rg (unfiltered) | 2-5s | Searches all text files |
| fd (by extension) | < 0.5s | Very fast for file listing |
| sg (single language) | 1-3s | Parses ASTs per file |
| tokei | 1-2s | Parallel counting |
| scc | 1-2s | Parallel counting |
| rga (with cache) | 2-5s | Depends on document count |
| rga (no cache) | 10-60s | First run extracts text |
| grep -r (same search as rg) | 30-120s | Single-threaded, no .gitignore |
| find (same search as fd) | 5-20s | Single-threaded |
| cloc (same as tokei) | 60-300s | Much slower |

---

## Tool Combinations

These tools work well together. Common combinations:

```bash
# Find files, then search contents
fd -e py --changed-within 1d -X rg 'TODO'

# Search for files, then analyze structurally
rg -l 'deprecated' -t py | xargs sg --pattern '@deprecated' --lang py

# Get codebase overview, then search largest language
tokei --sort code  # see which language dominates
rg 'pattern' -t py  # search that language

# Find config files, search for setting
fd -g '*.{yml,yaml}' -X rg 'database:'

# Find test files by name, verify they test something
fd -g '*_test.go' -X rg 'func Test'

# Combine fd size filter with rg
fd -S +100k -e js -X rg 'TODO'  # TODOs in large JS files
```

---

## Installation

All tools are available through common package managers:

```bash
# Ubuntu/Debian
sudo apt install ripgrep fd-find
# Note: fd binary is 'fdfind' on Debian/Ubuntu, alias to 'fd'

# macOS (Homebrew)
brew install ripgrep fd ast-grep ripgrep-all tokei scc

# Cargo (Rust)
cargo install ripgrep fd-find ast-grep tokei

# Go
go install github.com/boyter/scc/v3@latest

# npm (ast-grep)
npm install -g @ast-grep/cli
```

---

## Further Reading

- ripgrep: https://github.com/BurntSushi/ripgrep
- ast-grep: https://github.com/ast-grep/ast-grep
- fd: https://github.com/sharkdp/fd
- rga: https://github.com/phiresky/ripgrep-all
- tokei: https://github.com/XAcode/tokei
- scc: https://github.com/boyter/scc
