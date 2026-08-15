# Enforcement Hook

This skill's tool table — `rg` instead of `grep`, `fd` instead of `find`, `sg`
for structural patterns — is an instruction, and instructions get skipped. The
reminder that makes it stick **ships with this plugin**: `hooks/hooks.json`
registers `scripts/pre_bash_search_nudge.py` as a `PreToolUse` hook on `Bash`.
Installing the plugin installs it; there is no per-machine setup and no copy to
keep in sync.

The retro that produced it measured the problem: Bash carried 63% of all tool
calls in a session while the dedicated Grep and Glob tools went unused.

## What it says, and how often

Three rules, all **warn-only** — a shell search is never wrong enough to block:

| Command shape | Message |
|---|---|
| `find …` | use the Glob tool, or `fd` |
| `grep -r` / `grep -R` | use the Grep tool or `rg`; `sg` for structural patterns |
| `grep …` as the first command | prefer the Grep tool or `rg` |

Each rule speaks **once per session**. The value sits in the first firing: it is
read once and either changes the next command or has a deliberate reason not to
— several searches batched into one call, or a probe against a scratch file.
Firings 2..n change nothing and only cost the reader attention while scrolling
(measured on the source machine: 23 firings of these three rules in one
session).

## What it deliberately stays out of

- **A pipe into grep** (`gh pr list | grep open`) filters another command's
  output. That is not a search over the tree, and `rg` would not replace it.
- **Structured files** (`.json`, `.yaml`, `.toml`, `.csv`, …). The `data-tools`
  plugin ships its own gate for those, which *denies* field extraction. Two
  hooks must not both speak up for one command.
- **Prose about commands** — a PR body, a commit message, an `echo`. Option
  values carrying text (`--body`, `-m`, `-f body=`) are stripped before the
  scan; `--body-file` names a path and is left alone.

## Verify

```bash
H="$CLAUDE_PLUGIN_ROOT/scripts/pre_bash_search_nudge.py"   # or the plugin cache path
echo '{"tool_name":"Bash","tool_input":{"command":"find . -name x"}}'    | python3 "$H"  # warns
echo '{"tool_name":"Bash","tool_input":{"command":"rg TODO src/"}}'      | python3 "$H"  # silent
```

The full case list runs as `python3 scripts/test_pre_bash_search_nudge.py`.

If nothing happens on a real `find .`, the plugin's hooks have not been picked
up — open `/hooks` once, or restart the session.
