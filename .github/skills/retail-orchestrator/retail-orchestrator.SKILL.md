# Retail Orchestrator Skill

See [Agent, Skill, and Harness Value Map](../../agent-skill-value-map.md). This legacy entry point
coordinates delivery only and must not make runtime inventory or analytics decisions.

## Purpose
Coordinate end-to-end delivery for the eight-story retail replenishment v1 scope while enforcing constitution constraints.

## Value Boundary

Use this skill for delivery sequencing and governance. Use runtime agents only for bounded explanation
of deterministic outputs, and use harnesses for executable operational automation outside narration.

## Use This Skill When
- Work spans multiple feature streams
- Prioritization, sequencing, and dependency control are needed
- Readiness validation is needed before handoff to planning or implementation

## Inputs
- Current spec, plan, tasks, and checklist state
- Current backlog of open decisions and risks
- Capability ownership for US1 through US8, including US7 under alerting and US8 under transfer balancing

## Outputs
- Ordered execution plan by capability
- Cross-capability dependency map
- Readiness summary and blockers

## Readiness Gate

This legacy entry point is aligned with `SKILL.md` and the `retail.orchestrator` agent. The
orchestrator MUST pass explicit story/FR scope, dependencies, constitution, executable harness,
contract-test, authorization, audit, and cost evidence through every handoff. A capability MUST NOT
be marked Ready without file paths, commands, and passing validation results.

## Guardrails
- Keep v1 scope limited to the eight active user stories
- Enforce Python backend with Microsoft Agent Framework and Copilot SDK
- Enforce responsive React with dark/light mode for user-facing paths
- Require harness coverage per capability
- Require executable contract tests for every exposed contract
- Require authorization, audit, and cost/Azure Well-Architected evidence
- Track Azure Well-Architected and cost guardrail impacts
