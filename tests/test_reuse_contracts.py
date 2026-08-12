from __future__ import annotations

import hashlib
from importlib.metadata import distribution, version
from pathlib import Path

import pytest
from leaddock.contracts import (
    LeadDockError,
    LocalCalendarAdapter,
    LocalCrmAdapter,
)

WHEEL_SHA256 = "3c2e98295a89b5e36c11b2fc423ef6589e1babe3f3433b261889d09ed09993e9"
LEADDOCK_WHEEL_SHA256 = (
    "0e5715972675973a039b2489fc86c224b5a656689ec23300f6159dea989e5a16"
)


def test_deliveryguard_wheel_matches_pinned_checkpoint() -> None:
    wheel = (
        Path(__file__).parents[1] / "vendor" / "deliveryguard-0.2.0-py3-none-any.whl"
    )

    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == WHEEL_SHA256


def test_leaddock_contract_resolves_from_exact_installed_distribution() -> None:
    repository_root = Path(__file__).parents[1]
    manifest = repository_root / "vendor" / "leaddock-1.1.0.sha256"
    expected_hash, relative_wheel_path = manifest.read_text().split()
    wheel = repository_root / relative_wheel_path

    assert expected_hash == LEADDOCK_WHEEL_SHA256
    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == expected_hash
    assert version("leaddock") == "1.1.0"
    files = {str(path) for path in distribution("leaddock").files or ()}
    assert "leaddock/contracts.py" in files
    assert "leaddock/py.typed" in files


def test_leaddock_calendar_preserves_idempotency_and_collision_rules() -> None:
    calendar = LocalCalendarAdapter()
    slot = "2026-08-03T06:00:00+00:00"

    first, replayed = calendar.book("lead_one", slot, "Europe/Vilnius")
    again, replayed_again = calendar.book("lead_one", slot, "Europe/Vilnius")

    assert not replayed
    assert replayed_again
    assert first == again
    assert len(calendar.bookings) == 1
    with pytest.raises(LeadDockError, match="already booked"):
        calendar.book("lead_two", slot, "Europe/Vilnius")


def test_leaddock_crm_mapping_keeps_provider_neutral_fields() -> None:
    crm = LocalCrmAdapter()
    lead = {
        "id": "lead_1234567890",
        "identity_key": "mira@example.test",
        "name": "Mira Chen",
        "email": "mira@example.test",
        "phone": "+37060010001",
        "company": "Voice caller",
        "qualification": {"tier": "inbound", "score": 100},
    }

    record = crm.upsert(lead)

    assert record["external_key"] == "mira@example.test"
    assert record["fields"]["full_name"] == "Mira Chen"
    assert record["fields"]["qualification_tier"] == "inbound"


def test_leaddock_availability_is_timezone_aware() -> None:
    slots = LocalCalendarAdapter().availability("America/New_York")

    assert len(slots) == 15
    assert slots[0]["timezone"] == "America/New_York"
    assert slots[0]["label"].endswith("02:00")
