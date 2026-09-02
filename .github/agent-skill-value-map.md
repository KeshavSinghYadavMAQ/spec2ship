# Agent, Skill, and Harness Value Map

This repository uses three different automation layers. They are intentionally not interchangeable.

## Value Boundary

| Layer | Configured components | Primary value | Must not do |
|---|---|---|---|
| Delivery agents | `retail.orchestrator`, `retail.stock-levels`, `retail.alerting`, `retail.replenishment`, `retail.forecasting`, `retail.transfer-balance`, `retail.analytics`, and the Spec Kit workflow agents | Sequence work, resolve dependencies, refine requirements, and enforce delivery gates | Make production decisions, replace tests, or claim readiness without evidence |
| Runtime agents | `ReplenishmentExplainerAgent`, `ForecastExplainerAgent`, `StorePriorityExplainerAgent` | Turn deterministic outputs into concise, auditable operator explanations | Calculate reorder quantities, forecast values, threshold breaches, priority scores, authorize actions, or mutate inventory |
| Skills | One capability skill per retail domain plus the orchestrator skill | Provide reusable checklists, scope boundaries, handoff format, and governance gates | Perform calculations, call production systems, or substitute for executable code |
| Harnesses | Backend harnesses, evaluation tests, contract tests, and frontend evaluation/E2E tests | Automate operational activities outside LLM reasoning: event replay, duplicate handling, threshold validation, alert suppression, routing failure, approvals, KPI checks, accessibility, and integration failures | Depend on a live LLM to prove deterministic business correctness |

## Why These Runtime Agents Exist

Only three runtime agent wrappers are configured because explanation is the part of this product where
language reasoning adds value without weakening control:

- `ReplenishmentExplainerAgent` explains why a deterministic reorder recommendation was produced.
- `ForecastExplainerAgent` explains trend, seasonality, promotion, and data-quality factors already
  computed by the forecast engine.
- `StorePriorityExplainerAgent` explains region and consumption factors already computed by the
  priority service.

There is deliberately no runtime agent for inventory arithmetic, threshold evaluation, alert routing,
reorder math, forecast math, transfer feasibility, KPI aggregation, authorization, or audit writing.
Those activities require deterministic, typed, testable services.

## What the Harness Automates

Harness scenarios are the operational automation layer. They exercise workflows such as:

- Receiving, replaying, and deduplicating POS/WMS/ERP events.
- Recovering from source outages and preserving freshness warnings.
- Suppressing repeated alerts and handling notification-channel failures.
- Validating policy edits, lock conflicts, approvals, overrides, and audit trails.
- Ranking transfers and stores under conflicting data signals.
- Checking KPI filters, bounded result sets, rate-limit behavior, and dependency failures.
- Verifying that explanation agents cannot change deterministic outputs.

A runtime agent may be included in a harness only as a component under test. The harness remains the
source of truth for business correctness and must pass with deterministic fixtures and mocked agent
responses.

## Selection Rule

Add a runtime agent only when all of the following are true:

1. The task requires language interpretation, summarization, explanation, or operator assistance.
2. The input is produced by a deterministic domain service.
3. The output is structured or bounded, validated, auditable, and safe to ignore on failure.
4. A harness test proves that the agent cannot bypass authorization, policy safeguards, or source data.

Use a skill when the need is repeatable guidance or a delivery checklist. Use a harness when the need
is repeatable executable operational behavior.
