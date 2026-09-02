# Retail Replenishment Skill

See [Agent, Skill, and Harness Value Map](../../agent-skill-value-map.md). This legacy entry point is
guidance only and must not calculate reorder decisions.

## Purpose
Define explainable replenishment recommendations using policy-driven inventory controls.

## Use This Skill When
- Designing reorder decision logic
- Refining recommendation rationale content
- Modeling policy overrides and acceptance actions

## Checklist
- Confirm min-max and reorder point behavior
- Confirm safety stock and lead-time inputs
- Confirm explanation fields for user trust
- Confirm acceptance/override audit behavior

## Outputs
- Recommendation requirements
- Rationale schema
- Harness scenarios for policy and demand shifts

## Governance Gate

This legacy entry point is aligned with `SKILL.md` and the `retail.replenishment` agent. Deliverables
MUST include executable harness and contract-test paths, commands, and results, plus authorization,
audit, cost, and Azure Well-Architected evidence before handoff to `retail.orchestrator`.
