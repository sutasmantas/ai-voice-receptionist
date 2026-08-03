from __future__ import annotations

import json
from pathlib import Path

import pytest

from firstring.engine import CallEngine, ScenarioError

FIXTURES = Path(__file__).parent / "fixtures"


def fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def kinds(run: object) -> list[str]:
    return [event.kind for event in run.events]


def test_grounded_answer_and_booking_are_idempotent(tmp_path: Path) -> None:
    engine = CallEngine(tmp_path / "state.sqlite3")

    run = engine.run(fixture("successful_booking.json"))

    assert run.outcome == "booked"
    assert run.booking is not None
    assert len(engine.calendar.bookings) == 1
    assert "faq_answered" in kinds(run)
    assert "booking_created" in kinds(run)
    assert "booking_replayed" in kinds(run)
    assert run.handoff_state == "delivered"


def test_interruption_splices_active_assistant_turn(tmp_path: Path) -> None:
    run = CallEngine(tmp_path / "state.sqlite3").run(fixture("interruption.json"))

    interrupted = [
        event for event in run.events if event.kind == "assistant_interrupted"
    ]
    assert len(interrupted) == 1
    assert interrupted[0].at_ms == 260
    assert interrupted[0].data["original_end_ms"] > 260
    assert run.metrics["interruption_count"] == 1


def test_unknown_faq_fails_closed_and_transfers(tmp_path: Path) -> None:
    run = CallEngine(tmp_path / "state.sqlite3").run(fixture("unknown_faq.json"))

    assert run.outcome == "transfer"
    assert run.summary["transfer_reason"] == "faq_not_found"
    assert "faq_not_found" in kinds(run)
    assert "human_transfer" in kinds(run)


@pytest.mark.parametrize(
    ("fixture_name", "outcome", "reason"),
    [
        ("after_hours.json", "transfer", "after_hours"),
        ("opt_out.json", "opted_out", "caller_opt_out"),
    ],
)
def test_operating_rules_prevent_booking_and_handoff(
    tmp_path: Path, fixture_name: str, outcome: str, reason: str
) -> None:
    run = CallEngine(tmp_path / f"{outcome}.sqlite3").run(fixture(fixture_name))

    assert run.outcome == outcome
    assert run.booking is None
    assert run.handoff_state == "suppressed"
    assert run.summary["transfer_reason"] == reason


def test_provider_recovery_and_dead_letter_replay(tmp_path: Path) -> None:
    engine = CallEngine(tmp_path / "state.sqlite3")
    run = engine.run(fixture("recovery_and_dead_letter.json"))

    assert kinds(run)[:3] == ["call_started", "provider_failure", "provider_recovered"]
    assert run.handoff_state == "dead_letter"
    assert run.handoff_action_id is not None

    replayed = engine.replay_handoff(run.id)

    assert replayed.handoff_state == "delivered"
    assert replayed.handoff_action_id == run.handoff_action_id
    assert "handoff_replayed" in kinds(replayed)


def test_entity_accuracy_and_latency_fixtures_are_reported(tmp_path: Path) -> None:
    run = CallEngine(tmp_path / "state.sqlite3").run(fixture("successful_booking.json"))

    assert run.metrics["entity_accuracy"] == 1.0
    assert run.metrics["max_response_latency_ms"] <= 250
    assert run.metrics["final_transcript_count"] == 3


def test_non_monotonic_turns_are_rejected(tmp_path: Path) -> None:
    scenario = fixture("interruption.json")
    scenario["turns"][1]["at_ms"] = -1

    with pytest.raises(ScenarioError, match="strictly increasing"):
        CallEngine(tmp_path / "state.sqlite3").run(scenario)
