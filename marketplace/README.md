# Azure Marketplace Release Package

This directory contains the repository-owned release checklist for publishing the Retail
Replenishment platform as an Azure Marketplace offer. It is not a substitute for Microsoft
partner enrollment, offer certification, legal review, or subscription deployment.

## Included Repository Artifacts

- `infra/main.bicep`: parameterized Azure resource deployment baseline.
- `infra/dev.bicepparam`: non-secret development parameter example.
- `backend/Dockerfile`: backend API image.
- `frontend/Dockerfile`: frontend static web image.
- `.github/workflows/quality-gates.yml`: backend, frontend, contract, and Bicep quality gates.
- `specs/001-retail-replenishment-v1/contracts/openapi.yaml`: versioned API contract.
- `docs/security-review.md`: security assessment and residual risks.
- `docs/reliability-and-cost.md`: availability and cost validation plan.

## Pre-Submission Checklist

- [ ] Entra ID tenant, app registration, issuer, audience, and JWKS configuration supplied.
- [ ] Secure `APP_DATABASE_URL`, `APP_REDIS_URL`, and `APP_SERVICE_BUS_CONNECTION_STRING` values supplied to the deployment.
- [ ] Azure subscription, resource group, region, quota, and naming values approved.
- [ ] Container image built, vulnerability-scanned, signed, and pushed to a registry.
- [ ] Database migrations applied in a staging deployment and rollback tested.
- [ ] Service Bus, SQL, Redis, and monitoring private networking/secret references validated.
- [ ] Azure Cost Management budget configured at the approved ceiling.
- [ ] Synthetic availability, load, dependency-failure, and restore tests passed.
- [ ] Notification provider sender identity, channels, retries, and delivery monitoring configured.
- [ ] Privacy policy, terms of use, EULA, support SLA, support contact, and data residency statement published.
- [ ] SBOM and dependency vulnerability report attached to the release.
- [ ] Publisher profile, offer metadata, commercial plan, screenshots, architecture diagram, and support details completed in Partner Center.
- [ ] Marketplace technical validation and certification completed.

## External Blockers

Partner Center enrollment, publisher/legal identity, public legal/support URLs, Azure subscription
access, Entra configuration, provider credentials, pricing/commercial terms, and Marketplace
certification cannot be completed from this repository alone. The checklist must be signed off by
the release owner before calling the offer Marketplace-ready.
