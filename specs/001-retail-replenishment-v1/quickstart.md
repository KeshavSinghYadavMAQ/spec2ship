# Quickstart: Retail Replenishment V1 Foundation

This guide gets a contributor from clone to running backend + frontend locally, and running the constitution's
required harness scenarios. See [plan.md](./plan.md) for full technical context and [research.md](./research.md)
for stack rationale.

## Prerequisites

- Python 3.12+
- Node.js 20+ (for the React frontend)
- Docker (for a local SQL Server instance, Redis, and a Service Bus emulator or local substitute)
- Azure CLI (only needed for deploying to Azure environments, not for local development)

## 1. Backend setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Start local dependencies (SQL Server, Redis)
docker compose up -d sqlserver redis

# Apply schema migrations
alembic upgrade head

# Run the API
uvicorn src.api.main:app --reload --port 8000
```

## 2. Frontend setup

```powershell
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000/v1` (configurable via `.env.local`).

## 3. Running tests and harness scenarios

```powershell
# Backend unit + contract + integration tests
cd backend
pytest tests/unit tests/contract tests/integration

# Harness scenarios (Constitution III — non-negotiable before merge)
pytest tests/harness

# Frontend unit tests
cd ../frontend
npm run test

# Critical-path UI flows
npm run test:e2e
```

## 4. Validating a user story end-to-end (example: US2 alerting)

1. Seed a `ProductLocationPolicy` with a low-stock threshold via `POST /v1/admin/product-location-policies`.
2. Post an `IntegrationEvent` (`event_type: sale`) via `POST /v1/inventory/events` that drops shelf stock below the
   threshold.
3. Confirm a `StockAlert` is created in `Open` status via `GET /v1/alerts`.
4. Confirm duplicate breaches within the suppression window do not create duplicate alerts (FR-003).
5. Transition the alert through its lifecycle via `POST /v1/alerts/{alertId}/transition`.

## 5. Constitution gate self-check before opening a PR

- [ ] Specification gate: change traces to a user story ID (US1-US8) and FR ID(s).
- [ ] Architecture gate: backend changes stay in Python using MAF/Copilot SDK conventions; frontend changes stay
      in React with Fluent UI theming.
- [ ] Azure architecture gate: any new infrastructure maps to an Azure Well-Architected pillar and a cost note.
- [ ] Harness gate: new/changed capability has a harness scenario under `backend/tests/harness`.
- [ ] Observability and security gate: logs/metrics/traces and RBAC/audit coverage added where applicable.
- [ ] UX gate: new UI is responsive and validated in both dark and light themes.
