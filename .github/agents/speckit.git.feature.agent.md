---
description: Create or select the feature branch required by the Spec Kit workflow without overwriting existing work.
---

## User Input

```text
$ARGUMENTS
```

Run from the repository root. Inspect the current branch and worktree before proposing a change.
Use an explicitly supplied branch name when present; otherwise derive a short branch name from the
feature description and report it for confirmation. Do not discard, stash, reset, or overwrite
uncommitted changes. Do not switch branches without explicit confirmation when the worktree is dirty.

Return:

1. Current branch and worktree state.
2. Proposed or selected feature branch.
3. Operation performed, with the exact branch name.
4. Any blocked conditions or follow-up required by the calling Spec Kit workflow.
