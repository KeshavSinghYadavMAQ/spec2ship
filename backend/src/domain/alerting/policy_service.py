"""Threshold validation rules and edit-lock enforcement service (T077, US7, FR-016,
FR-017, FR-023).

`ThresholdEvaluationService.evaluate()` (T043) holds `edit_lock_held` for the duration
of an in-flight evaluation; `PolicyService.upsert_policy` rejects concurrent edits while
that lock is held so an admin's change always lands cleanly on the next evaluation cycle
rather than racing an in-progress one.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.domain.admin.audit import AuditLogWriter
from src.domain.alerting.policy_models import ProductLocationPolicy


class PolicyValidationError(Exception):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class PolicyEditLockedError(Exception):
    def __init__(self, sku_id: str, location_id: str) -> None:
        super().__init__(
            f"Policy for sku_id={sku_id} location_id={location_id} is locked by an "
            "in-flight evaluation; retry after the current cycle completes"
        )


_POLICY_FIELDS = (
    "low_stock_threshold",
    "out_of_stock_threshold",
    "reorder_point",
    "min_qty",
    "max_qty",
    "safety_stock",
)


def _validate(
    *,
    low_stock_threshold: int,
    out_of_stock_threshold: int,
    reorder_point: int,
    min_qty: int,
    max_qty: int,
    safety_stock: int,
) -> None:
    errors: list[str] = []
    values = {
        "low_stock_threshold": low_stock_threshold,
        "out_of_stock_threshold": out_of_stock_threshold,
        "reorder_point": reorder_point,
        "min_qty": min_qty,
        "max_qty": max_qty,
        "safety_stock": safety_stock,
    }
    for name, value in values.items():
        if value < 0:
            errors.append(f"{name} must not be negative")
    if out_of_stock_threshold > low_stock_threshold:
        errors.append("out_of_stock_threshold must not exceed low_stock_threshold")
    if min_qty > max_qty:
        errors.append("min_qty must not exceed max_qty")
    if errors:
        raise PolicyValidationError(errors)


class PolicyService:
    def __init__(self, session: Session, audit_writer: AuditLogWriter | None = None) -> None:
        self._session = session
        self._audit = audit_writer or AuditLogWriter(session)

    def list_policies(
        self, sku_id: str | None = None, location_id: str | None = None
    ) -> list[ProductLocationPolicy]:
        query = self._session.query(ProductLocationPolicy)
        if sku_id:
            query = query.filter_by(sku_id=sku_id)
        if location_id:
            query = query.filter_by(location_id=location_id)
        return query.order_by(ProductLocationPolicy.sku_id, ProductLocationPolicy.location_id).all()

    def upsert_policy(
        self,
        *,
        sku_id: str,
        location_id: str,
        low_stock_threshold: int,
        out_of_stock_threshold: int,
        reorder_point: int,
        min_qty: int,
        max_qty: int,
        safety_stock: int,
        updated_by: str,
    ) -> ProductLocationPolicy:
        _validate(
            low_stock_threshold=low_stock_threshold,
            out_of_stock_threshold=out_of_stock_threshold,
            reorder_point=reorder_point,
            min_qty=min_qty,
            max_qty=max_qty,
            safety_stock=safety_stock,
        )

        new_values = {
            "low_stock_threshold": low_stock_threshold,
            "out_of_stock_threshold": out_of_stock_threshold,
            "reorder_point": reorder_point,
            "min_qty": min_qty,
            "max_qty": max_qty,
            "safety_stock": safety_stock,
        }

        existing = (
            self._session.query(ProductLocationPolicy)
            .filter_by(sku_id=sku_id, location_id=location_id)
            .one_or_none()
        )

        if existing is not None and existing.edit_lock_held:
            raise PolicyEditLockedError(sku_id, location_id)

        now = datetime.now(UTC)
        if existing is None:
            policy = ProductLocationPolicy(
                id=str(uuid.uuid4()),
                sku_id=sku_id,
                location_id=location_id,
                is_active=True,
                updated_by=updated_by,
                updated_at=now,
                change_history=[{"before": None, "after": new_values, "updated_by": updated_by}],
                **new_values,
            )
            self._session.add(policy)
            before = None
        else:
            before = {field: getattr(existing, field) for field in _POLICY_FIELDS}
            for field, value in new_values.items():
                setattr(existing, field, value)
            existing.updated_by = updated_by
            existing.updated_at = now
            existing.change_history = (existing.change_history or []) + [
                {"before": before, "after": new_values, "updated_by": updated_by}
            ]
            policy = existing

        self._session.flush()
        self._audit.record(
            actor_user_id=updated_by,
            action="policy_upsert",
            entity_type="ProductLocationPolicy",
            entity_id=policy.id,
            before=before,
            after=new_values,
        )
        return policy
