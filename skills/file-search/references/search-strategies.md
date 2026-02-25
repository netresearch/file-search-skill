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
