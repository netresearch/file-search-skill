# ripgrep Pattern Recipes

Practical `rg` patterns organized by use case. All examples assume you are in
the project root directory.

---

## Security Scanning

```bash
# Hardcoded passwords/secrets
rg -i '(password|passwd|secret|api_key|apikey|token)\s*[:=]' -g '!*.lock'
rg -i '(password|secret|key)\s*=\s*["\x27][^"\x27]{8,}' -g '!*.lock' -g '!*.md'

# AWS credentials
rg '(AKIA|ASIA)[A-Z0-9]{16}'
rg 'aws_secret_access_key\s*[:=]'

# Private keys
rg 'BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY'

# JWT tokens
rg 'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}'

# Dangerous functions
rg '\beval\s*\(' -t py -t js -t php -t ruby
rg '\bexec\s*\(' -t py -t php
rg 'innerHTML\s*=' -t js -t ts

# SQL injection vectors
rg '(query|execute)\s*\(.*["\x27]\s*\+' -t py -t js -t java
rg '\$\w+.*->query\(\s*["\x27]' -t php
rg 'raw\s*\(\s*f["\x27]' -t py  # f-string in raw SQL (Python)

# Insecure HTTP
rg 'http://' -t py -t js -t go -t java -g '!*.lock' -g '!*.md'
rg 'verify\s*=\s*False' -t py    # disabled SSL verification
rg 'rejectUnauthorized.*false' -t js -t ts

# Debug/dev artifacts left in code
rg '(console\.log|print\(|fmt\.Print)' -t js -t py -t go --count-matches
rg 'binding\.pry' -t ruby
rg 'debugger;' -t js -t ts
rg 'dd\(' -t php
```

---

## Dependency Analysis

```bash
# Python imports
rg '^from (\S+) import' -t py -o -r '$1' --no-filename | sort -u
rg '^import (\S+)' -t py -o -r '$1' --no-filename | sort -u

# JavaScript/TypeScript imports
rg "^import .+ from ['\"]([^'\"]+)" -t js -t ts -o -r '$1' --no-filename | sort -u
rg "require\(['\"]([^'\"]+)" -t js -o -r '$1' --no-filename | sort -u

# Go imports
rg '"([\w./]+)"' -t go -o -r '$1' --no-filename | sort -u

# PHP use statements
rg '^use\s+([\w\\\\]+)' -t php -o -r '$1' --no-filename | sort -u

# Java imports
rg '^import\s+([\w.]+)' -t java -o -r '$1' --no-filename | sort -u

# Rust use statements
rg '^use\s+([\w:]+)' -t rust -o -r '$1' --no-filename | sort -u

# Find unused imports (files that import X but never reference it again)
# Step 1: find files importing the module
rg -l 'import someModule' -t js
# Step 2: check if the module is used beyond the import line
rg -c 'someModule' -t js  # files with count=1 likely only have the import
```

---

## Code Quality

```bash
# TODO/FIXME/HACK/XXX with context
rg '(TODO|FIXME|HACK|XXX|WARN|DEPRECATED):?\s' -n --trim
rg '(TODO|FIXME)\((\w+)\)' -o -r '$1 by $2' --no-filename  # extract assignee

# Deprecated usage
rg '@deprecated' -n -t py -t js -t ts -t java -t php
rg '@Deprecated' -t java

# Magic numbers (numeric literals in logic, not in declarations)
rg 'if.*[^=!<>]==[^=].*\d{2,}' -t py -t js -t go

# Long functions (find function start, count lines until next function)
rg -n 'def \w+\(' -t py  # list all function definitions with line numbers

# Empty exception handling
rg -U 'except.*:\s*\n\s*(pass|\.\.\.)\s*$' -t py
rg -U 'catch\s*\(.*\)\s*\{\s*\}' -t js -t ts -t java

# Commented-out code (heuristic)
rg '^\s*//\s*(if|for|while|return|function|var|let|const)\b' -t js -t ts
rg '^\s*#\s*(if|for|while|return|def|class|import)\b' -t py

# Dead code indicators
rg 'noinspection' -t java -t py
rg '@ts-ignore' -t ts
rg '// eslint-disable' -t js -t ts
rg '# type: ignore' -t py
rg '# noqa' -t py
rg '# noinspection' -t py
```

---

## Refactoring

```bash
# Find all usages of a function
rg '\bfunctionName\b' -t py -n

# Find function definitions (various languages)
rg 'def functionName\(' -t py
rg 'function functionName\(' -t js
rg 'func functionName\(' -t go
rg 'fn functionName\(' -t rust

# Find class definitions
rg 'class ClassName' -t py -t java -t ts

# Find method calls on a specific type
rg '\.methodName\(' -t go -t java -t ts

# Find variable assignments
rg '\bvarName\s*[:=]' -t py -t js -t ts

# Find all files referencing a module (across languages)
rg -l '(import|require|use|from).*moduleName'

# Rename preview (show what would change)
rg 'oldName' -t py -r 'newName'   # shows replacements, does not write

# Find interface implementations (Go)
rg 'func \(.*\) MethodName\(' -t go

# Find all routes/endpoints
rg '(@app\.(get|post|put|delete|patch)|router\.(get|post|put|delete|patch))' -t py
rg 'app\.(get|post|put|delete|patch)\(' -t js -t ts
rg '(GET|POST|PUT|DELETE|PATCH)\s+/' -t go
```

---

## Configuration and Infrastructure

```bash
# Find all config files
rg -l '.' -g '*.{yml,yaml,toml,ini,cfg,conf,json,env,env.*}'

# Find Docker-related configs
rg -l '.' -g 'Dockerfile*' -g 'docker-compose*' -g '.dockerignore'

# Find port bindings
rg '(port|PORT)\s*[:=]\s*\d+' -g '*.{yml,yaml,toml,json,env,py,js,go}'
rg ':\d{4,5}' -g '*.{yml,yaml,toml,env}'

# Find database connection strings
rg '(postgres|mysql|mongo|redis|sqlite)://' -g '!*.lock' -g '!*.md'

# Find environment variable references
rg 'os\.environ\[' -t py
rg 'os\.Getenv\(' -t go
rg 'process\.env\.' -t js -t ts
rg '\$_ENV\[' -t php
rg 'getenv\(' -t php

# Find CI/CD references
rg -l '.' -g '.github/workflows/*.yml'
rg -l '.' -g '.gitlab-ci.yml' -g 'Jenkinsfile' -g '.circleci/*'
```

---

## Advanced Flags and Techniques

```bash
# Invert match (show lines NOT matching)
rg -v 'pattern' file.txt

# Show only the matched portion
rg -o 'pattern' -t py

# Capture groups with replacement (extract data)
rg 'version:\s*"([^"]+)"' -o -r '$1' --no-filename

# Search binary files
rg --binary 'pattern'

# Search compressed files (use rga instead for full support)
rg -z 'pattern' archive.gz

# Null-byte separated output (for xargs -0)
rg -l0 'pattern' | xargs -0 wc -l

# Limit number of results
rg 'pattern' --max-count 5   # max 5 matches per file
rg 'pattern' -l | head -20   # first 20 matching files

# Search with lookahead/lookbehind (PCRE2)
rg -P '(?<=import\s)\w+' -t py    # word after "import "
rg -P 'def \w+\((?=.*self)' -t py  # methods (have self param)

# Stats about the search
rg 'pattern' --stats

# Sorted output by file path
rg 'pattern' --sort path

# Glob patterns for includes
rg 'pattern' -g '*.{ts,tsx}' -g '!*.test.*' -g '!*.spec.*'
```

---

## Performance Tips

- **Always specify file types** (`-t`) when possible. This avoids scanning
  irrelevant files entirely.
- **Limit directory scope** to the relevant subtree.
- **Use `-l`** (list files) when you only need to know which files match, not
  the matching lines.
- **Use `--max-count N`** to stop searching a file after N matches.
- **Exclude large directories** like `vendor/`, `node_modules/`, `dist/`,
  `.git/` with `-g '!dir/'`.
- **Use `-F`** (fixed string) when your pattern has no regex metacharacters.
  This is faster than regex matching.
- **Pipe to `head`** when exploring. You do not need all 10,000 results to
  understand the pattern.

---

## Key Flags Reference

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
--count-matches Count individual matches per file (vs -c which counts matching lines)
-r REPLACEMENT  Replace matches in output (preview, does not modify files)
```

---

## Progressive Refinement Strategy

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

---

## Common Patterns

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

---

## File Type Targeting

ripgrep has built-in type definitions. List all with `rg --type-list`.

Common types: `py`, `js`, `ts`, `go`, `rust`, `java`, `php`, `ruby`, `css`,
`html`, `json`, `yaml`, `toml`, `md`, `sh`, `sql`, `c`, `cpp`.

```bash
# Multiple types
rg 'pattern' -t js -t ts

# Custom type definition (one-off)
rg --type-add 'web:*.{html,css,js}' -t web 'pattern'
```
