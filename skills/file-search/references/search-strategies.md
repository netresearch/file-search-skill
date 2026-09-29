<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- SPDX-FileCopyrightText: Netresearch DTT GmbH -->

# Search Strategies

Unfocused searches produce overwhelming output. Always scope searches
deliberately.

---

## 1. Specify File Types

```bash
# Good: targeted by type
rg 'pattern' -t py
sg --pattern '$FUNC($$$)' --lang go

# Bad: search everything
rg 'pattern'
```

---

## 2. Limit Directory Scope

```bash
# Good: specific directory
rg 'pattern' src/api/
fd -e ts src/components/

# Bad: search from root
rg 'pattern' /
```

---

## 3. Count Before Viewing

```bash
# First: how many matches?
rg -c 'pattern' -t py | wc -l    # number of files
rg --count-matches 'pattern' -t py  # total matches per file

# Then: view if manageable
rg -n 'pattern' -t py
```

---

## 4. Progressive Refinement

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

---

## 5. Exclude Noise

```bash
# Exclude generated/vendor code
rg 'pattern' -g '!vendor/' -g '!node_modules/' -g '!*.min.js' -g '!dist/'
fd -e py -E __pycache__ -E .venv -E '*.pyc'
```

---

## 6. Batch & Parallelize Independent Queries

`rg` walks the filesystem once per invocation. N sequential calls =
N walks + N startup costs. Two ways to collapse that:

### 6a. Union patterns in one process (`rg -e ... -e ...`)

When you want any of several patterns from the same scope, pass them all
to one `rg`:

```bash
# Good: one walk, one process
rg -t php -e 'RequestHandlerInterface' -e 'MiddlewareInterface' -e 'PSR-15'

# Bad: three walks
rg -t php 'RequestHandlerInterface'
rg -t php 'MiddlewareInterface'
rg -t php 'PSR-15'
```

Use `-f patterns.txt` for many patterns. Note: ripgrep does not annotate
output with which `-e`/`-f` pattern matched — neither plain text nor
`--json` exposes a stable pattern index. If you need provenance, run
separate searches or post-process by re-matching the captured text.

`rg` also accepts multiple `-t` flags and multiple path arguments, so
prefer batching scope into a single call:

```bash
# Good: one walk, multiple types
rg -t php -t js -t ts 'pattern'

# Good: one walk, multiple paths
rg 'pattern' src/ tests/ docs/
```

### 6b. Parallel tool calls for distinct intents

Use parallel tool calls when the queries can't collapse into one `rg`
invocation — different patterns in different scopes, different tools,
or different post-processing. Issue them as **parallel tool calls in a
single message**; the agent harness runs them concurrently and total
wall time ≈ slowest single call.

Good candidates for parallel calls:

- Different patterns in different scopes: `rg 'Error' logs/` + `rg 'TODO' src/`
- Different tools on same target: `rg X` + `fd -g '*X*'` + `tokei`
- Different search modes: `rg 'pattern'` + `sg --pattern 'func($$$)'`

Anti-pattern: chaining independent greps with `&&` in one Bash call —
the shell still runs them sequentially.
