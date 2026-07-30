# Retail Orchestrator Skill

## Purpose
Coordinate end-to-end delivery for the six-feature v1 replenishment scope while enforcing constitution constraints.

## Use This Skill When
- Work spans multiple feature streams
- Prioritization, sequencing, and dependency control are needed
- Readiness validation is needed before handoff to planning or implementation

## Inputs
- Current spec, plan, tasks, and checklist state
- Current backlog of open decisions and risks

## Outputs
- Ordered execution plan by capability
- Cross-capability dependency map
- Readiness summary and blockers

## Guardrails
- Keep v1 scope limited to the six launch features
- Enforce Python backend with Microsoft Agent Framework and Copilot SDK
- Enforce responsive React with dark/light mode for user-facing paths
- Require harness coverage per capability
- Track Azure Well-Architected and cost guardrail impacts
