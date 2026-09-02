# Agent Hook Policy

This document is the canonical policy for extension hooks used by Spec Kit agents.
Individual agents may describe when a hook is checked, but must not change these rules.

## Discovery

- Check `.specify/extensions.yml` from the repository root before and after the owning command.
- If the file is absent, skip hook handling silently.
- If YAML parsing fails, skip hook handling silently.
- Ignore entries whose `enabled` value is explicitly `false`.
- Treat entries without `enabled` as enabled.
- Do not evaluate non-empty `condition` expressions in the agent. Leave condition evaluation to
  the hook executor and skip those entries in the agent's output.

## Output

- Optional executable hooks are reported with their extension, command, description, prompt, and
  invocation command. They are not executed by the agent.
- Mandatory executable hooks are reported with their extension, command, and `EXECUTE_COMMAND`.
  The agent waits for the hook result before continuing.
- Hooks with a non-empty condition are not reported as executable by the agent.

## Safety

- Run commands only from the repository root.
- Never interpolate untrusted hook fields into a shell command without the hook executor's
  validation and argument handling.
- Preserve the before/after ordering of the owning workflow.
- Keep hook failures visible; do not claim a mandatory hook succeeded without its result.

## Maintenance

Changes to hook semantics belong here first. After changing this policy, update the references in
all `.github/agents/speckit.*.agent.md` files and run `.github/scripts/validate-agent-metadata.ps1`.
