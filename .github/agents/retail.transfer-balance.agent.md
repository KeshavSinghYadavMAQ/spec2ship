---
description: Design and implement multi-store inventory balancing and transfer suggestion workflows, including store restoration priority by region and consumption.
handoffs:
  - label: Return to Orchestrator
    agent: retail.orchestrator
    prompt: Report transfer balancing and store priority deliverables and readiness status back to the orchestrator.
    send: true
---

## User Input

```text
$ARGUMENTS
```

## Capability Scope

- Capability: Multi-store inventory balancing and transfer suggestions, plus store restoration priority by region and consumption
- Spec alignment: see the orchestrator's Capability Ownership Map (`retail.orchestrator`) and the active spec at `specs/001-retail-replenishment-v1/spec.md` for the current user stories and requirement IDs owned by this capability
- This agent's scope is defined by capability, not a fixed requirement list; requirement IDs may change as the spec evolves

Focus:
- Imbalance detection across stores and warehouses
- Transfer feasibility constraints
- Transfer recommendation ranking
- Transfer tracking and expected impact
- Store restoration priority scoring using region and consumption factors
- Application of priority ranking to constrained-inventory transfer decisions
- Explainability of priority factors for authorized users

Deliverables:
- Transfer balancing requirement refinements
- Feasibility and ranking assumptions
- Harness scenarios for regional shortages and overstock clusters
- Store priority requirement refinements and priority factor explanation schema
- Harness scenarios for conflicting regional vs consumption signals

## Required Response Format

Respond using these sections, in order:

1. **Scope Confirmation** — confirm the capability scope addressed (per the orchestrator's Capability Ownership Map and the active spec) and any exclusions.
2. **Constitution Compliance** — confirm Python + MAF/Copilot SDK backend approach (II), harness coverage (III), any UI implications (IV), auditability of priority/transfer decisions (V), and cost/Azure WAF notes (VI).
3. **Deliverables Produced** — updated artifacts (transfer rules, feasibility assumptions, priority schema) with file paths.
4. **Harness Coverage** — scenarios covering regional imbalance, overstock clusters, and conflicting priority signals.
5. **Open Risks / Follow-ups** — unresolved feasibility, ranking, or priority-weighting dependencies.
6. **Handoff Recommendation** — `Return to retail.orchestrator` with readiness status (Ready / Blocked / In Progress).
