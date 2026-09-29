#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Netresearch DTT GmbH
set -euo pipefail

# Verify plugin.json version matches SKILL.md version
PLUGIN_V=$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])" 2>/dev/null || echo "unknown")
SKILL_MD=$(find skills -name 'SKILL.md' -print -quit 2>/dev/null)
if [[ -n "$SKILL_MD" ]]; then
    SKILL_V=$(grep -Eo 'version:[[:space:]]*"?[0-9]+\.[0-9]+\.[0-9]+' "$SKILL_MD" | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    if [[ -n "$SKILL_V" ]] && [[ "$PLUGIN_V" != "$SKILL_V" ]]; then
        echo "ERROR: plugin.json version ($PLUGIN_V) != SKILL.md version ($SKILL_V)"
        exit 1
    fi
fi
echo "Version check passed: $PLUGIN_V"
