# Retail Alerting Skill

See [Agent, Skill, and Harness Value Map](../../agent-skill-value-map.md). This legacy entry point is
guidance only and must not calculate alert decisions.

## Purpose
Define low stock and out-of-stock alerting that is actionable, deduplicated, and role-routed.

## Use This Skill When
- Designing threshold policy behavior
- Defining urgency and escalation logic
- Mapping channels to role responsibilities

## Checklist
- Confirm threshold hierarchy (global, category, SKU, location)
- Confirm deduplication and suppression windows
- Confirm urgency tiers and escalation rules
- Confirm notification routing and delivery assumptions

## Outputs
- Alert policy definitions
- Alert acceptance scenarios
- Harness scenarios for burst and repeated breaches

## Governance Gate

This legacy entry point is aligned with `SKILL.md` and the `retail.alerting` agent. It also covers
the product-location threshold admin panel and audit trail. Deliverables MUST include executable
harness and contract-test paths, commands, and results, plus authorization, audit, cost, and
Azure Well-Architected evidence before handoff to `retail.orchestrator`.
