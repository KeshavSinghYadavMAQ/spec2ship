# Retail Stock Levels Skill

See [Agent, Skill, and Harness Value Map](../../agent-skill-value-map.md). This legacy entry point is
guidance only and must not calculate stock state.

## Purpose
Define and validate near real-time inventory visibility across shelf, backroom, store, and warehouse stock states.

## Use This Skill When
- Updating stock visibility requirements
- Designing inventory ingest and reconciliation behavior
- Defining freshness and lag targets

## Checklist
- Confirm SKU-location inventory model
- Confirm shelf vs backroom tracking rules
- Confirm event deduplication and ordering behavior
- Confirm freshness SLA and monitoring signals

## Outputs
- Updated acceptance scenarios
- Data contract assumptions
- Harness scenarios for data-quality edge cases

## Governance Gate

This legacy entry point is aligned with `SKILL.md` and the `retail.stock-levels` agent. Deliverables
MUST include executable harness and contract-test paths, commands, and results, plus authorization,
audit, cost, and Azure Well-Architected evidence before handoff to `retail.orchestrator`.
