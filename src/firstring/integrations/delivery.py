from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from types import TracebackType
from typing import Any, Literal

from deliveryguard import Classification, DeliveryFailure, DeliveryResult, DeliveryStore


class ClosingConnection(sqlite3.Connection):
    """Give DeliveryGuard's context-managed connections a real close boundary."""

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        try:
            super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()
        return False


class ClosingDeliveryStore(DeliveryStore):
    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path,
            factory=ClosingConnection,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection


class FixtureWebhookAdapter:
    """Deterministic DeliveryGuard adapter with injectable network failures."""

    def __init__(self, failures: int = 0) -> None:
        self.failures_remaining = failures
        self.receipts: list[dict[str, Any]] = []

    def send(
        self,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str,
        correlation_id: str,
    ) -> DeliveryResult:
        if self.failures_remaining:
            self.failures_remaining -= 1
            raise DeliveryFailure(
                Classification.NETWORK_ERROR,
                "Injected receptionist webhook outage.",
                retryable=True,
            )
        receipt = {
            "receipt_id": f"receipt-{len(self.receipts) + 1}",
            "idempotency_key": idempotency_key,
            "correlation_id": correlation_id,
            "outcome": payload.get("outcome"),
        }
        self.receipts.append(receipt)
        return DeliveryResult(Classification.SUCCESS, 202, receipt)
