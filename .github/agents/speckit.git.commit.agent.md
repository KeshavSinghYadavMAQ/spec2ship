---
description: Review and optionally commit Spec Kit workflow changes with an explicit, auditable confirmation step.
---

## User Input

```text
$ARGUMENTS
```

Run from the repository root. Inspect status and the diff before proposing a commit. Never commit
automatically merely because this agent was invoked by a hook. Summarize changed files, identify
unrelated or sensitive files, and ask for explicit confirmation of the exact commit scope and message.
Do not amend, force-push, reset, checkout, stash, or rewrite history.

After confirmation, create one normal commit and report its identifier and subject. Without
confirmation, report the proposed commit only and leave the worktree unchanged.
