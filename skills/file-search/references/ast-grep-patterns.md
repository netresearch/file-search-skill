# ast-grep Pattern Recipes

Structural search patterns for `sg` (ast-grep), organized by language.

ast-grep matches code by AST structure, not text. This means patterns are
immune to whitespace differences, comment variations, and formatting styles.

---

## Metavariable Reference

| Syntax | Description | Example |
|--------|-------------|---------|
| `$VAR` | Single AST node (expression, identifier, literal) | `console.log($MSG)` |
| `$$$` | Zero or more AST nodes (variadic) | `function($$$)` |
| `$$_` | Zero or more unnamed nodes (wildcard) | `[$$$]` |
| `$_` | Any single node (unnamed wildcard) | `if ($_) { $$$ }` |

**Key rules:**
- Named metavariables (`$VAR`) capture their match and must match consistently
  within a pattern (same `$VAR` = same value).
- `$$$` is greedy and matches any number of arguments, statements, etc.
- Use `$_` when you do not care about capturing the value.

---

## JavaScript / TypeScript

### React Patterns

```bash
# useState hooks
sg --pattern 'const [$STATE, $SETTER] = useState($$$)' --lang tsx

# useEffect with dependency array
sg --pattern 'useEffect(() => { $$$ }, [$$$])' --lang tsx

# useEffect without dependencies (runs every render)
sg --pattern 'useEffect(() => { $$$ })' --lang tsx

# Component definitions (function)
sg --pattern 'function $NAME($$$) { $$$ return $$$ }' --lang tsx

# Arrow function components
sg --pattern 'const $NAME = ($$$) => { $$$ }' --lang tsx

# JSX with specific prop
sg --pattern '<$COMP className={$$$} />' --lang tsx
sg --pattern '<$COMP onClick={$$$}>$$$</$COMP>' --lang tsx

# Custom hook calls
sg --pattern 'const $RESULT = use$HOOK($$$)' --lang tsx
```

### Async/Await Patterns

```bash
# Async function declarations
sg --pattern 'async function $NAME($$$) { $$$ }' --lang js

# Await expressions
sg --pattern 'await $EXPR' --lang js

# Try/catch around await
sg --pattern 'try { $$$ await $EXPR $$$ } catch ($ERR) { $$$ }' --lang ts

# Promise.all usage
sg --pattern 'await Promise.all([$$$])' --lang ts

# Unhandled promise (missing await)
sg --pattern '$VAR.$METHOD($$$).then($$$)' --lang ts
```

### Error Handling

```bash
# Empty catch blocks
sg --pattern 'try { $$$ } catch ($ERR) { }' --lang js

# Console.log in catch (often should be proper logging)
sg --pattern 'catch ($ERR) { $$$ console.log($$$) $$$ }' --lang js

# Throw new Error
sg --pattern 'throw new Error($MSG)' --lang ts

# Throw non-Error objects
sg --pattern 'throw $MSG' --lang ts
```

### Module Patterns

```bash
# Default exports
sg --pattern 'export default $EXPR' --lang ts

# Named exports
sg --pattern 'export const $NAME = $VALUE' --lang ts
sg --pattern 'export function $NAME($$$) { $$$ }' --lang ts

# Dynamic imports
sg --pattern 'import($PATH)' --lang ts
sg --pattern 'await import($PATH)' --lang ts
```

### Common Anti-Patterns

```bash
# Direct DOM manipulation in React
sg --pattern 'document.getElementById($$$)' --lang tsx
sg --pattern 'document.querySelector($$$)' --lang tsx

# setState in useEffect without cleanup
sg --pattern 'useEffect(() => { $$$ $SETTER($$$) $$$ })' --lang tsx

# Object mutation
sg --pattern '$OBJ.$PROP = $VALUE' --lang ts
```

---

## Python

### Function and Class Patterns

```bash
# Function definitions
sg --pattern 'def $NAME($$$):
    $$$' --lang py

# Async function definitions
sg --pattern 'async def $NAME($$$):
    $$$' --lang py

# Class with inheritance
sg --pattern 'class $NAME($BASE):
    $$$' --lang py

# Static methods
sg --pattern '@staticmethod
def $NAME($$$):
    $$$' --lang py

# Class methods
sg --pattern '@classmethod
def $NAME(cls, $$$):
    $$$' --lang py

# Property definitions
sg --pattern '@property
def $NAME(self):
    $$$' --lang py
```

### Decorator Patterns

```bash
# Any decorated function
sg --pattern '@$DECORATOR
def $NAME($$$):
    $$$' --lang py

# Specific decorator
sg --pattern '@app.route($$$)
def $NAME($$$):
    $$$' --lang py

# Decorator with arguments
sg --pattern '@$DECORATOR($$$)
def $NAME($$$):
    $$$' --lang py

# Pytest fixtures
sg --pattern '@pytest.fixture($$$)
def $NAME($$$):
    $$$' --lang py
```

### Error Handling

```bash
# Bare except (catches everything including SystemExit)
sg --pattern 'try:
    $$$
except:
    $$$' --lang py

# Except with pass (silenced errors)
sg --pattern 'except $EXCEPTION:
    pass' --lang py

# Broad exception catching
sg --pattern 'except Exception as $ERR:
    $$$' --lang py

# Context managers
sg --pattern 'with $EXPR as $VAR:
    $$$' --lang py
```

### Type Annotation Patterns

```bash
# Typed function signatures
sg --pattern 'def $NAME($$$) -> $RETURN:
    $$$' --lang py

# Optional types
sg --pattern 'Optional[$TYPE]' --lang py

# Union types
sg --pattern 'Union[$$$]' --lang py
```

---

## PHP

### Class and Method Patterns

```bash
# Class definitions
sg --pattern 'class $NAME { $$$ }' --lang php
sg --pattern 'class $NAME extends $BASE { $$$ }' --lang php
sg --pattern 'class $NAME implements $IFACE { $$$ }' --lang php

# Method definitions
sg --pattern 'public function $NAME($$$) { $$$ }' --lang php
sg --pattern 'protected function $NAME($$$) { $$$ }' --lang php
sg --pattern 'private function $NAME($$$) { $$$ }' --lang php

# Static methods
sg --pattern 'public static function $NAME($$$) { $$$ }' --lang php

# Constructor
sg --pattern 'public function __construct($$$) { $$$ }' --lang php

# Constructor property promotion (PHP 8+)
sg --pattern 'public function __construct(
    $$$
) { $$$ }' --lang php
```

### Common PHP Patterns

```bash
# Array operations
sg --pattern 'array_map($CALLBACK, $$$)' --lang php
sg --pattern 'array_filter($ARRAY, $$$)' --lang php

# Method chaining
sg --pattern '$OBJ->$METHOD1($$$)->$METHOD2($$$)' --lang php

# Type-hinted parameters
sg --pattern 'function $NAME($TYPE $PARAM) { $$$ }' --lang php

# Null coalescing
sg --pattern '$EXPR ?? $DEFAULT' --lang php

# Match expression (PHP 8+)
sg --pattern 'match ($EXPR) { $$$ }' --lang php
```

### TYPO3/Symfony/Laravel Patterns

```bash
# Dependency injection
sg --pattern 'public function __construct($TYPE $PARAM) { $$$ }' --lang php

# Route annotations
sg --pattern '#[Route($$$)]' --lang php

# Doctrine annotations
sg --pattern '#[ORM\Column($$$)]' --lang php
```

---

## Go

### Function and Method Patterns

```bash
# Function definitions
sg --pattern 'func $NAME($$$) $RETURN { $$$ }' --lang go

# Methods with receiver
sg --pattern 'func ($RECV $TYPE) $NAME($$$) $RETURN { $$$ }' --lang go

# Pointer receiver methods
sg --pattern 'func ($RECV *$TYPE) $NAME($$$) $RETURN { $$$ }' --lang go

# Init functions
sg --pattern 'func init() { $$$ }' --lang go

# Main functions
sg --pattern 'func main() { $$$ }' --lang go
```

### Error Handling

```bash
# Standard error check
sg --pattern 'if $ERR != nil { $$$ }' --lang go

# Error return without wrapping
sg --pattern 'if $ERR != nil { return $ERR }' --lang go

# Error wrapping with fmt.Errorf
sg --pattern 'fmt.Errorf($FMT, $$$)' --lang go

# errors.Is / errors.As
sg --pattern 'errors.Is($ERR, $TARGET)' --lang go
sg --pattern 'errors.As($ERR, $TARGET)' --lang go
```

### Concurrency

```bash
# Goroutine launches
sg --pattern 'go $FUNC($$$)' --lang go

# Channel operations
sg --pattern '$CH <- $VALUE' --lang go
sg --pattern '<-$CH' --lang go

# Select statements
sg --pattern 'select { $$$ }' --lang go

# Mutex usage
sg --pattern '$MU.Lock()' --lang go
sg --pattern 'defer $MU.Unlock()' --lang go

# WaitGroup
sg --pattern '$WG.Add($N)' --lang go
sg --pattern 'defer $WG.Done()' --lang go
```

### Struct and Interface Patterns

```bash
# Struct definitions
sg --pattern 'type $NAME struct { $$$ }' --lang go

# Interface definitions
sg --pattern 'type $NAME interface { $$$ }' --lang go

# Struct literal initialization
sg --pattern '$TYPE{ $$$ }' --lang go
```

### Testing

```bash
# Test functions
sg --pattern 'func Test$NAME(t *testing.T) { $$$ }' --lang go

# Benchmark functions
sg --pattern 'func Benchmark$NAME(b *testing.B) { $$$ }' --lang go

# Table-driven tests
sg --pattern 'for $_, $TC := range $CASES { $$$ }' --lang go

# t.Run subtests
sg --pattern 't.Run($NAME, func(t *testing.T) { $$$ })' --lang go
```

---

## Rust

### Function Patterns

```bash
# Function definitions
sg --pattern 'fn $NAME($$$) -> $RETURN { $$$ }' --lang rust

# Async functions
sg --pattern 'async fn $NAME($$$) -> $RETURN { $$$ }' --lang rust

# Impl blocks
sg --pattern 'impl $TYPE { $$$ }' --lang rust

# Trait implementations
sg --pattern 'impl $TRAIT for $TYPE { $$$ }' --lang rust
```

### Error Handling

```bash
# unwrap calls (potential panics)
sg --pattern '$EXPR.unwrap()' --lang rust

# expect calls
sg --pattern '$EXPR.expect($MSG)' --lang rust

# Match on Result
sg --pattern 'match $EXPR { Ok($VAL) => $$$, Err($ERR) => $$$ }' --lang rust

# Question mark operator
sg --pattern '$EXPR?' --lang rust
```

---

## Tips for Writing ast-grep Patterns

1. **Start simple.** Begin with a small pattern and add complexity. If
   `$FUNC($$$)` matches too broadly, add more structure.

2. **Use `--json` output** for programmatic processing. The JSON includes
   file path, line/column ranges, and matched metavariable bindings.

3. **Test patterns interactively** at https://ast-grep.github.io/playground
   to verify they match what you expect.

4. **Language matters.** Always specify `--lang` -- the same text may parse
   differently in different languages.

5. **Metavariable consistency.** Within a single pattern, the same `$NAME`
   must match the same text. Use different names (`$A`, `$B`) for different
   captures.

6. **Whitespace is ignored** in pattern matching. `func ( $ARG )` matches
   `func(arg)`, `func( arg )`, etc.
