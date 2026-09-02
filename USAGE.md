# Usage Guide

This guide explains how to install, start, and use the Retail Replenishment solution locally. It is
written for an operator or evaluator starting from a fresh checkout on Windows PowerShell.

## What the Solution Provides

The application gives authenticated users scoped visibility into retail operations:

- Inventory positions and stock events
- Low-stock and out-of-stock alerts
- Replenishment recommendations
- Demand forecasts
- Store transfer suggestions and store priority
- Analytics and KPI summaries
- Admin policy and sample-data management

Access is controlled by a server-side session cookie and each user only receives data allowed by their
role and location scope.

## Prerequisites

Install the following before starting:

- Python 3.12 or newer
- Node.js 20 or newer, including npm
- Git
- Docker Desktop, required for the local Redis service

SQLite is used by default, so SQL Server is not required for normal local use.

## First-Time Local Setup

Open PowerShell in the repository root and create the backend environment:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
alembic upgrade head
```

If PowerShell blocks activation, run this once in an elevated PowerShell window or use the Python
executable directly from `backend\.venv\Scripts\python.exe`.

Start Redis in Docker. Keep Docker Desktop running:

```powershell
cd backend
docker compose up -d redis
```

Seed the local demo accounts. This command is safe to run more than once; existing accounts are
skipped:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python scripts/seed_demo_accounts.py
```

Install frontend dependencies in a separate PowerShell terminal:

```powershell
cd frontend
npm ci
```

## Start the Application

Use two terminals after completing first-time setup.

Terminal 1, backend:

```powershell
cd backend
.venv\Scripts\Activate.ps1
uvicorn src.api.main:app --reload --port 8000
```

Terminal 2, frontend:

```powershell
cd frontend
npm run dev
```

Open the application at <http://localhost:5173/>. The API is available at <http://localhost:8000/>;
interactive API documentation is at <http://localhost:8000/docs>.

Check that the backend is running with:

```powershell
Invoke-RestMethod http://localhost:8000/healthz
```

Expected response:

```text
status
------
ok
```

## Demo Login Accounts

These accounts are created by `python scripts/seed_demo_accounts.py` for local testing only.

| Username | Password | Role | Access |
|---|---|---|---|
| `admin_demo` | `StrongPass!123` | Admin | All locations and admin tools |
| `store_mgr_a` | `SecurePass!123` | Store manager | `STORE-A` |
| `regional_mgr_west` | `RegionalPass!123` | Regional manager | Configured West-region stores |

Do not use these passwords in a shared or production environment. The application locks an account
after five failed attempts within fifteen minutes.

## Using the Web Application

1. Open <http://localhost:5173/>.
2. Sign in with one of the demo accounts.
3. Use the navigation to open Inventory, Alerts, Replenishment, Forecasts, Transfers, Store
   Priority, Analytics, or Admin.
4. Use the theme control to switch between light and dark mode.
5. Select Logout when finished. The session cookie is revoked server-side.

The `store_mgr_a` account is useful for verifying row-level security: it should only see records for
its assigned location. The admin account is useful for creating policies and running sample-data
operations.

## Populate Demo Operational Data

The login-account script creates users only. To populate inventory, alerts, forecasts, recommendations,
transfers, and store-priority data, sign in as `admin_demo` and use the Admin sample-data controls, or
call the API:

```powershell
curl.exe -i -X POST "http://localhost:8000/v1/admin/sample-data/seed?store_count=10&catalog_size=100&assortment_size=20" `
  -H "X-User-Id: admin-1" `
  -H "X-User-Role: admin"
```

For a normal browser session, use the session cookie created by the login request instead of the local
development headers. The query parameters above keep a demo run small; the endpoint defaults to the
pilot seed size when they are omitted.

## Basic API Workflow

Login and store the returned session cookie in a browser or API client:

```powershell
curl.exe -i -c cookies.txt -X POST http://localhost:8000/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"identifier":"admin_demo","password":"StrongPass!123"}'
```

Use the cookie for protected requests:

```powershell
curl.exe -i -b cookies.txt http://localhost:8000/v1/inventory/positions
curl.exe -i -b cookies.txt http://localhost:8000/v1/alerts
curl.exe -i -b cookies.txt http://localhost:8000/v1/analytics/kpis
```

To log out:

```powershell
curl.exe -i -b cookies.txt -c cookies.txt -X POST http://localhost:8000/v1/auth/logout
```

A stock event uses a stable `event_id` so retries are idempotent:

```powershell
curl.exe -i -b cookies.txt -X POST http://localhost:8000/v1/inventory/events `
  -H "Content-Type: application/json" `
  -d '{"source_system":"local-pos","event_id":"local-event-001","event_type":"stock_update","sku_id":"SKU-1","location_id":"STORE-1","shelf_delta":20,"backroom_delta":5,"metadata":{}}'
```

## Configuration

The backend reads optional settings from environment variables with the `APP_` prefix. The most
useful local overrides are:

```powershell
$env:APP_DATABASE_URL = "sqlite:///./dev.db"
$env:APP_REDIS_URL = "redis://localhost:6379/0"
$env:APP_CORS_ALLOW_ORIGINS = '["http://localhost:5173"]'
```

The frontend uses `http://localhost:8000/v1` by default. To use another API URL, create
`frontend\.env.local`:

```dotenv
VITE_API_BASE_URL=http://localhost:8000/v1
```

Never commit `.env.local`, passwords, connection strings, or bearer tokens.

## Troubleshooting

**The API cannot connect to Redis:** confirm Docker Desktop is running, then run
`docker compose up -d redis` from `backend`.

**The API reports missing tables:** run `alembic upgrade head` from `backend` and restart Uvicorn.

**Login returns `Authentication failed`:** run the demo-account script from `backend` with
`$env:PYTHONPATH = (Get-Location).Path`, and confirm the username and password exactly match the
table above.

**The browser shows a network error:** confirm both servers are running and that the frontend API URL
matches the backend URL.

**A scoped user sees no records:** this is expected when the records are outside the assigned scope.
Use `admin_demo` to seed or inspect all locations.

## Validate Changes

Backend checks:

```powershell
cd backend
.venv\Scripts\python.exe -m compileall -q src tests
.venv\Scripts\ruff.exe check src tests
.venv\Scripts\pytest.exe tests/unit tests/contract tests/integration tests/harness -q
```

Frontend checks:

```powershell
cd frontend
npm run lint
npm run build
npm run test
npm run test:e2e
```

## Azure Staging

Azure staging is an operator-owned deployment activity. It requires Azure CLI, an Azure subscription,
permissions to create the resources in `infra/main.bicep`, approved container images, and secret
values for the database, Redis, and Service Bus. Do not use the local demo credentials in staging.

Before deployment, configure the staging secrets through the approved secret-management process,
apply Alembic migrations through the deployment job, and verify `/healthz`, authentication, scoped
access, queue processing, alerts, logs, metrics, traces, cost controls, and rollback behavior. Azure
credentials, Entra configuration, provider identities, publisher details, pricing, and Partner Center
certification remain release-owner responsibilities.
