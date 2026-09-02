"""One-off script to seed demo user accounts for local testing.

Usage:
    python -m scripts.seed_demo_accounts

Creates the accounts referenced in the quickstart:
    - admin_demo (admin, global scope)
    - store_mgr_a (store_manager, Store A)
    - regional_mgr_west (regional_manager, West region)

Safe to re-run: skips accounts that already exist.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.domain.admin.rbac import UserRoleAssignment
from src.domain.auth.models import UserAccount
from src.domain.auth.password_policy import hash_password
from src.infrastructure.db import SessionLocal, create_all_tables

DEMO_ACCOUNTS = [
    {
        "login_identifier": "admin_demo",
        "password": "StrongPass!123",
        "role": "admin",
        "location_scope": {"all_locations": True},
    },
    {
        "login_identifier": "store_mgr_a",
        "password": "SecurePass!123",
        "role": "store_manager",
        "location_scope": {"location_ids": ["STORE-A"]},
    },
    {
        "login_identifier": "regional_mgr_west",
        "password": "RegionalPass!123",
        "role": "regional_manager",
        "location_scope": {"location_ids": ["STORE-CHICAGO-001", "STORE-CHICAGO-002", "STORE-DENVER-001"]},
    },
]


def seed_demo_accounts() -> None:
    create_all_tables()

    with SessionLocal() as session:
        created = []
        for account_def in DEMO_ACCOUNTS:
            existing = (
                session.query(UserAccount)
                .filter(UserAccount.login_identifier == account_def["login_identifier"])
                .first()
            )
            if existing:
                print(f"  ✓ {account_def['login_identifier']} already exists — skipping")
                continue

            account_id = str(uuid.uuid4())
            now = datetime.now(UTC)

            account = UserAccount(
                id=account_id,
                login_identifier=account_def["login_identifier"],
                password_hash=hash_password(account_def["password"]),
                is_active=True,
                failed_attempt_count_window=0,
                created_at=now,
                updated_at=now,
            )
            session.add(account)

            assignment = UserRoleAssignment(
                id=str(uuid.uuid4()),
                user_id=account_id,
                role=account_def["role"],
                location_scope=account_def["location_scope"],
            )
            session.add(assignment)

            created.append(account_def["login_identifier"])

        session.commit()

    print(f"\nSeeded {len(created)} account(s): {', '.join(created)}")
    print("\nLogin credentials for local testing:")
    for account_def in DEMO_ACCOUNTS:
        print(f"  {account_def['login_identifier']} / {account_def['password']}")


if __name__ == "__main__":
    seed_demo_accounts()