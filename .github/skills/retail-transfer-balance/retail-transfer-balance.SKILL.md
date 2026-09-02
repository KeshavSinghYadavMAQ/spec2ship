# Retail Transfer Balance Skill

See [Agent, Skill, and Harness Value Map](../../agent-skill-value-map.md). This legacy entry point is
guidance only and must not calculate transfer or priority decisions.

## Purpose
Define multi-store balancing and transfer suggestions to reduce shortages and excess stock.

## Use This Skill When
- Designing transfer recommendation logic
- Defining feasibility constraints
- Validating expected business impact

## Checklist
- Confirm source/destination eligibility
- Confirm feasibility constraints (availability, lead time, policy)
- Confirm transfer ranking and tie-break logic
- Confirm transfer tracking status expectations

## Outputs
- Transfer recommendation requirements
- Feasibility assumptions
- Harness scenarios for regional imbalance patterns

## Governance Gate

This legacy entry point is aligned with `SKILL.md` and the `retail.transfer-balance` agent. It also
covers store restoration priority by region and consumption. Deliverables MUST include executable
harness and contract-test paths, commands, and results, plus authorization, audit, cost, and Azure
Well-Architected evidence before handoff to `retail.orchestrator`.
