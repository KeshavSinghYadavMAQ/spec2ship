---
description: Initialize Git repository state required by the Spec Kit workflow without overwriting existing repository configuration.
---

## User Input

```text
$ARGUMENTS
```

Run from the repository root. Inspect whether Git metadata already exists before changing anything.
If the repository is already initialized, report that state and make no changes. If initialization is
requested and the directory is not a Git repository, initialize it and report the resulting status.
Do not create commits, branches, remotes, hooks, or credentials in this step.

Return:

1. Repository state before the operation.
2. Operation performed, or why no operation was needed.
3. Repository state after the operation.
4. Any follow-up required by the calling Spec Kit workflow.
