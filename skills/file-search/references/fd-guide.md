# fd Guide

Fast, user-friendly file finder. Replaces `find` with sane defaults: respects
`.gitignore`, colorized output, regex by default, smart case.

---

## Key Flags

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

---

## Common Usage

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

---

## fd + rg Combinations

```bash
# Find Python files, then search for a pattern
fd -e py -x rg -l 'async def'

# Find recently changed files and search them
fd --changed-within 2h -e ts -X rg 'TODO'

# Find config files and search for a key
fd -g '*.{yml,yaml,toml,json}' -X rg 'database'
```
