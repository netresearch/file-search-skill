<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- SPDX-FileCopyrightText: Netresearch DTT GmbH -->

# Beyond Local Files — Remote Handoff Guide

This skill covers local CLI search tools. When the context you need lives
outside the repository, hand off to the appropriate tool or skill.

---

## Handoff Table

| Need | Hand off to |
|------|-------------|
| Issue/ticket context (Jira, GitHub Issues) | jira-communication skill or `gh issue view` |
| PR/MR discussion, review comments | git-workflow skill or `gh pr view` |
| Wiki pages, project documentation sites | WebFetch or documentation skills |
| Upstream/fork differences | `git log`, `git diff`, `gh repo view` |
| Live API responses, external services | WebFetch, Playwright |

---

## When to Hand Off

- `rg`/`fd` return no results and the answer likely lives in issues, PRs,
  or external docs
- Code comments reference issue keys (`#123`, `PROJ-456`, `JIRA-789`)
- You need the rationale behind a change (check the PR/MR, not just the diff)
- The user asks about deployment status, CI results, or external service state

---

## Combining Local and Remote Search

A common pattern is local-first, then remote:

1. **Local**: `rg 'PROJ-1234'` — find where the issue is referenced in code
2. **Local**: `git log --grep='PROJ-1234'` — find commits mentioning it
3. **Remote**: `gh issue view 1234` or Jira API — get current status
4. **Decision**: combine local context with remote status to answer the question

---

## Signals That Context Is Remote

- Comments like `// TODO: see #456`, `// Workaround for PROJ-123`
- Commit messages referencing PRs (`Merge pull request #89`)
- Configuration referencing external services (URLs, API endpoints)
- Questions about "why" something was done (rationale lives in PRs/issues)
