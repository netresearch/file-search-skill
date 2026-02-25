# Code Metrics: tokei and scc

Fast codebase analysis tools for counting lines of code, comments, and blanks
by language.

---

## tokei

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

---

## scc

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

---

## When to Use Which

| Need | Tool |
|------|------|
| Quick language breakdown | `tokei` |
| Complexity estimates / cost modeling | `scc` |
| CI integration / badge generation | `scc` (has badge output) |
| Fastest possible count | `tokei` |
