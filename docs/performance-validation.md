# Performance Validation Notes (T098 — SC-001, SC-003, SC-007)

Design-level validation of the three latency/usability success criteria from spec.md,
performed as part of Phase 11 polish. **No dedicated load-testing infrastructure exists
in this repo** (no k6/Locust/Artillery scripts); this document records the architectural
reasoning for why each target is expected to be met at pilot scale, plus what a
follow-up load-test pass should measure before scale-up.

## SC-001 — 95% of stock updates visible within 60 seconds

> "At least 95% of stock updates are visible to users within 60 seconds of event receipt."

- `POST /v1/inventory/events` (`backend/src/api/routers/inventory.py`) applies the event
  synchronously in the same request via `InventoryService.ingest_event`, and the
  `IntegrationEvent`/`InventoryPosition` rows are committed before the `202` response is
  returned. There is no batch/polling delay in the ingest path itself.
- `GET /v1/inventory/positions` reads directly from the same committed table — no cache
  staleness window sits between write and read.
- The only asynchronous path is the dead-letter **replay** flow
  (`backend/src/domain/inventory/replay_worker.py`), used only when a source system
  outage caused an event to be queued (FR-022); this is an explicit resilience trade-off
  ("eventually visible after replay"), not the common-case path SC-001 is measured
  against.
- **Conclusion**: the common-case (non-degraded) path has sub-second visibility by
  design; 60 seconds is a generous budget given no batching exists. Confirmed logically,
  not via a timed load test.
- **Follow-up recommendation**: once deployed to Azure SQL/Container Apps, run a timed
  ingest→read round-trip test under representative concurrent load to confirm p95 network
  + DB latency stays well under 60s, especially under Azure SQL autoscale cold-start
  conditions.

## SC-003 — 90% of low/out-of-stock breaches notified within 2 minutes

> "At least 90% of low stock and out-of-stock events are notified within 2 minutes of
> threshold breach."

- Alert evaluation happens inline as part of the same `ingest_event` call path (breach
  detection → `StockAlertRepository.create` → routing), not on a separate polling
  schedule — so detection-to-alert-creation latency is effectively the same as the
  ingest request latency (sub-second in the common case).
- `alert_suppression_window_seconds` (`backend/src/infrastructure/config.py`, default
  900s = 15 minutes) governs **duplicate-alert suppression** (FR-003), not the
  first-alert notification latency — it prevents repeat notifications for the same
  ongoing breach, which is a different concern from SC-003's "time to first notification."
- Routing/dispatch (`backend/src/domain/alerting/routing.py`'s `dispatch_notification`) is
  called synchronously in the same request; no message-queue hop sits between breach
  detection and dispatch in the current implementation.
- **Conclusion**: first-notification latency is dominated by request/DB latency (sub-second
  in the common case), well inside the 2-minute budget.
- **Follow-up recommendation**: if/when notification dispatch (email/SMS/webhook) is
  wired to a real external channel rather than the current logged/simulated dispatch,
  measure that channel's own delivery latency (e.g., SMS gateway p95) against the
  2-minute budget — that's the part not yet exercised by this codebase.

## SC-007 — 90% of triage workflows completed in under 2 minutes

> "Users complete critical dashboard triage workflows in under 2 minutes for at least 90%
> of observed sessions."

- This is a UX/workflow-efficiency criterion, not a backend latency criterion — validated
  by design review of the Alert Worklist, Recommendation Panel, and Transfer Suggestions
  screens plus the T100/T108 Playwright suites, rather than by a timed backend test.
- Supporting design decisions:
  - `AlertWorklist`/`RecommendationPanel`/`TransferSuggestions` show status, severity,
    and next valid actions inline in one table row — no drill-down navigation is required
    to act on an item (see `frontend/src/features/alerting/AlertWorklist.tsx`,
    `frontend/src/features/replenishment/RecommendationPanel.tsx`,
    `frontend/src/features/transfer-balance/TransferSuggestions.tsx`).
  - Recommendation decisions require only a rating selection + one button click (T105).
  - `tests/e2e/theme.spec.ts` and `tests/e2e/accessibility.spec.ts` (T100/T108) confirm
    these screens render without horizontal overflow at mobile/tablet/desktop widths and
    have no automatically detectable WCAG violations, both of which reduce interaction
    friction that would otherwise slow down triage.
- **Conclusion**: no code change identified as necessary; the workflow is structurally
  optimized for fast single-screen action.
- **Follow-up recommendation**: SC-007 ultimately requires real operator usage data
  (session timing telemetry) to confirm the 90%/2-minute target in practice — this should
  be measured post-pilot-launch via frontend interaction analytics, not something a static
  code review can fully certify.
