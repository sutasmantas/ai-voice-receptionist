from __future__ import annotations

import json
from pathlib import Path

import pytest

from firstring.audio_harness import (
    AudioHarnessError,
    canonical_receipt_bytes,
    load_manifest,
    mutant_receipts,
    run_audio_harness,
    run_mutation_gate,
    validate_receipt,
    verify_audio_fixture,
)

MANIFEST = Path(__file__).parent / "fixtures" / "audio" / "manifest.json"
MANIFEST_SCHEMA = MANIFEST.with_name("manifest.schema.json")


def test_fixture_hash_and_wav_contract_match_manifest() -> None:
    manifest = load_manifest(MANIFEST)

    observed = verify_audio_fixture(manifest, MANIFEST)

    assert observed["channels"] == 2
    assert observed["sample_rate_hz"] == 8_000
    assert observed["frame_count"] == 9_600
    assert observed["compression"] == "NONE"


def test_replay_is_byte_identical_and_excludes_dynamic_identifiers() -> None:
    first = canonical_receipt_bytes(run_audio_harness(MANIFEST))
    second = canonical_receipt_bytes(run_audio_harness(MANIFEST))

    assert first == second
    assert b'"run_id"' not in first
    assert b'"action_id"' not in first
    assert b'"wall_clock"' not in first


def test_timeline_and_business_effect_are_grounded_in_existing_engine() -> None:
    receipt = run_audio_harness(MANIFEST)

    assert receipt["engine_observations"]["interruption_count"] == 1
    assert receipt["business_effect"]["booking"]["id"] == "book_31212940e5"
    assert receipt["business_effect"]["crm"]["id"] == "crm_505e3c6c8b"
    assert receipt["business_effect"]["handoff"] == {"state": "delivered"}
    assert receipt["timeline"][-1]["kind"] == "effect_receipt"


@pytest.mark.parametrize(
    "mutant_id",
    [
        "drop-final-transcript",
        "final-before-last-partial",
        "erase-critical-entity",
        "clause-pause-becomes-eot",
        "fail-agent-audio-cancel",
        "wrong-booking-crm-result",
        "duplicate-business-effect",
    ],
)
def test_each_frozen_mutant_is_killed(mutant_id: str) -> None:
    manifest = load_manifest(MANIFEST)
    clean = run_audio_harness(MANIFEST)

    with pytest.raises(AudioHarnessError):
        validate_receipt(mutant_receipts(clean)[mutant_id], manifest)


def test_mutation_gate_has_clean_control_and_kills_seven_of_seven() -> None:
    report = run_mutation_gate(MANIFEST)

    assert report["clean_control"] == "PASS"
    assert report["mutants_killed"] == 7
    assert report["mutants_total"] == 7
    assert all(result["killed"] for result in report["results"])


def test_manifest_is_plain_json_with_versioned_schema() -> None:
    raw = json.loads(MANIFEST.read_text(encoding="utf-8"))
    schema = json.loads(MANIFEST_SCHEMA.read_text(encoding="utf-8"))

    assert raw["schema_version"] == "firstring.audio-harness-manifest/v0"
    assert schema["properties"]["schema_version"]["const"] == raw["schema_version"]
    assert set(schema["required"]) <= set(raw)
