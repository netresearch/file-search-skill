<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- SPDX-FileCopyrightText: Netresearch DTT GmbH -->

# semgrep Pattern Recipes

Rule-driven structural code search with semgrep, focused on security and
lint patterns. Use when `sg` (ast-grep) is the wrong tool: semgrep ships
with curated rule packs, supports taint analysis (source → sink dataflow),
and is the standard for security CI gates.

## semgrep vs ast-grep

| | `sg` (ast-grep) | `semgrep` |
|--|-----------------|-----------|
| **Primary use** | Structural search & rewrite | Security/lint rules at scale |
| **Patterns live in** | CLI flag or YAML | YAML rules (file or registry) |
| **Rewrite support** | Yes (first-class) | Limited (`autofix:`) |
| **Taint tracking** | No | Yes (`mode: taint`) |
| **Rule registry** | No | https://semgrep.dev/r |
| **Per-language config** | `--lang` flag | `languages:` in rule |
| **CI integration** | Manual | `semgrep ci` (native) |

**Rule of thumb:** reach for `sg` when you have a structural pattern in
your head; reach for `semgrep` when you want to apply a *catalog* of
patterns (OWASP, CWE, framework-specific lints).

## Quick Examples

```bash
# Apply the curated security rule pack (no local rules needed)
semgrep --config=auto .

# Run a specific rule pack
semgrep --config=p/security-audit .
semgrep --config=p/owasp-top-ten .
semgrep --config=p/r2c-ci .

# Single inline pattern (ad-hoc, no YAML)
semgrep -e 'eval(...)' --lang python .
semgrep -e 'exec($CMD)' -e 'os.system($CMD)' --lang python .

# JSON output for pipelines
semgrep --config=auto --json --quiet .

# Only report severity ERROR (skip WARNING/INFO)
semgrep --config=auto --severity=ERROR .

# Limit scope
semgrep --config=auto --include='*.py' src/
```

## Inline Patterns by Language

```bash
# Python: dangerous deserialization
semgrep -e 'pickle.loads($X)' --lang python .
semgrep -e 'yaml.load($X)' --lang python .   # missing SafeLoader

# Python: SQL string concatenation
semgrep -e 'cursor.execute("..." + $X)' --lang python .

# JavaScript/TypeScript: dangerous DOM sinks
semgrep -e '$EL.innerHTML = $X' --lang js .
semgrep -e 'document.write($X)' --lang js .

# Go: ignored errors (both assignment and short-declaration forms)
semgrep -e '_, _ = $F(...)' -e '_, _ := $F(...)' --lang go .

# PHP: unsafe shell
semgrep -e 'shell_exec($X)' --lang php .
semgrep -e 'eval($X)' --lang php .
```

## Custom Rule (YAML)

For anything you want to reuse, write a rule file:

```yaml
# .semgrep/no-eval.yml
rules:
  - id: no-eval
    message: "Avoid eval() — use ast.literal_eval or a parser."
    severity: ERROR
    languages: [python]
    pattern: eval(...)
```

Run it:

```bash
semgrep --config=.semgrep/ .
```

## Taint Mode (Dataflow)

Use when you need to track that *user input* flows into a *dangerous
sink*. Pattern-only matches miss this; taint mode tracks it across
assignments and function calls.

```yaml
# .semgrep/sql-injection.yml
rules:
  - id: sql-from-request
    mode: taint
    message: "User input flows into raw SQL."
    severity: ERROR
    languages: [python]
    pattern-sources:
      - pattern: request.args.get($X)
      - pattern: request.form.get($X)
    pattern-sinks:
      - pattern: cursor.execute($Q)
```

## CI Integration

```bash
# Fail the build on findings of severity ERROR
semgrep --config=auto --severity=ERROR --error .

# Diff-aware: only scan changed lines (fast CI mode)
semgrep ci --baseline-ref=origin/main
```

## When NOT to Use semgrep

- **Unstructured text search** → use `rg` instead. semgrep parses code
  (and structured formats like YAML/JSON); it cannot match log lines or
  free-form prose.
- **One-off structural refactor with a rewrite** → use `sg` instead. Its
  `--rewrite` is first-class; semgrep autofix is more constrained.
- **Files semgrep cannot parse** → semgrep reports parse errors on
  stderr but produces no findings for those files. If a file is
  unsupported or unparseable, fall back to `rg`/`sg`.

## Further Reading

- semgrep docs: https://semgrep.dev/docs
- Rule registry: https://semgrep.dev/r
- Writing rules: https://semgrep.dev/docs/writing-rules/overview
