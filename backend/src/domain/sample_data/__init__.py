"""Sample-data seeding domain module (feature 002, US1).

Populates every existing domain (inventory, alerting, replenishment, forecasting,
transfer_balance, admin) with realistic, pilot-scale, fictitious data for demo/dev
environments, tracked in an isolated ledger (`SampleDataSeedRecord`) so the data can be
cleared without touching genuine records. Gated to non-production environments and the
`admin` role (FR-004, FR-011).
"""
