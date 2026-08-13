from __future__ import annotations

import hashlib
import json
import wave
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast

from firstring.engine import CallEngine
from firstring.models import CallRun

SCHEMA_VERSION = "firstring.audio-harness-manifest/v0"
RECEIPT_VERSION = "firstring.audio-harness-receipt/v0"


class AudioHarnessError(ValueError):
    """Raised when a fixture, manifest, or normalized receipt violates V0."""


class ScriptedEventRecorder:
    """Append-only recorder for construction-known relative-time events."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def record(self, event: dict[str, Any]) -> None:
        sequence = len(self._events) + 1
        if event.get("sequence") != sequence:
            raise AudioHarnessError(
                "scripted event sequence must be contiguous from one"
            )
        at_ms = event.get("at_ms")
        if not isinstance(at_ms, int):
            raise AudioHarnessError("scripted event at_ms must be an integer")
        if self._events and at_ms < self._events[-1]["at_ms"]:
            raise AudioHarnessError("scripted event times must be monotonic")
        self._events.append(deepcopy(event))

    def snapshot(self) -> list[dict[str, Any]]:
        return deepcopy(self._events)


def _object(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AudioHarnessError(f"{label} must be an object")
    return cast("dict[str, Any]", value)


def _objects(value: object, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise AudioHarnessError(f"{label} must be a list of objects")
    return cast("list[dict[str, Any]]", value)


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AudioHarnessError(f"cannot load manifest: {exc}") from exc
    manifest = _object(raw, "manifest")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise AudioHarnessError(f"schema_version must be {SCHEMA_VERSION}")
    for key in ("case_id", "audio", "scenario", "scripted_events", "expected"):
        if key not in manifest:
            raise AudioHarnessError(f"manifest is missing {key}")
    _object(manifest["audio"], "audio")
    _object(manifest["scenario"], "scenario")
    _objects(manifest["scripted_events"], "scripted_events")
    _object(manifest["expected"], "expected")
    return manifest


def verify_audio_fixture(
    manifest: dict[str, Any], manifest_path: Path
) -> dict[str, Any]:
    audio = _object(manifest["audio"], "audio")
    relative_path = audio.get("path")
    if not isinstance(relative_path, str) or not relative_path:
        raise AudioHarnessError("audio.path must be a non-empty string")
    fixture_path = manifest_path.parent / relative_path
    try:
        payload = fixture_path.read_bytes()
    except OSError as exc:
        raise AudioHarnessError(f"cannot read audio fixture: {exc}") from exc
    digest = hashlib.sha256(payload).hexdigest()
    if digest != audio.get("sha256"):
        raise AudioHarnessError("audio fixture SHA-256 does not match manifest")
    try:
        with wave.open(str(fixture_path), "rb") as source:
            observed = {
                "channels": source.getnchannels(),
                "sample_rate_hz": source.getframerate(),
                "sample_width_bytes": source.getsampwidth(),
                "frame_count": source.getnframes(),
                "compression": source.getcomptype(),
            }
    except (OSError, wave.Error) as exc:
        raise AudioHarnessError(f"audio fixture is not a readable WAV: {exc}") from exc
    for key, value in observed.items():
        if audio.get(key) != value:
            raise AudioHarnessError(
                f"audio.{key} expected {audio.get(key)!r}, observed {value!r}"
            )
    return {
        "path": relative_path,
        "sha256": digest,
        **observed,
        "language": audio.get("language"),
        "speaker_case_id": audio.get("speaker_case_id"),
    }


def _normalize_effect(engine: CallEngine, run: CallRun) -> dict[str, Any]:
    booking_events = [
        event
        for event in run.events
        if event.kind in {"booking_created", "booking_replayed"}
    ]
    if not booking_events or run.booking is None:
        raise AudioHarnessError("scenario produced no booking receipt")
    crm_id = booking_events[-1].data.get("crm_id")
    caller = _object(run.summary.get("caller"), "run.summary.caller")
    email = caller.get("email")
    if not isinstance(email, str) or email not in engine.crm.records:
        raise AudioHarnessError("scenario produced no CRM receipt")
    crm_record = deepcopy(engine.crm.records[email])
    if crm_record.get("id") != crm_id:
        raise AudioHarnessError("booking event and CRM receipt disagree")
    return {
        "outcome": run.outcome,
        "booking": deepcopy(run.booking),
        "crm": crm_record,
        "handoff": {"state": run.handoff_state},
    }


def run_audio_harness(manifest_path: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    source_audio = verify_audio_fixture(manifest, manifest_path)
    scenario = deepcopy(_object(manifest["scenario"], "scenario"))
    with TemporaryDirectory(prefix="firstring-v0-") as directory:
        engine = CallEngine(Path(directory) / "state.sqlite3")
        run = engine.run(scenario)
        effect = _normalize_effect(engine, run)
    raw_events = _objects(manifest["scripted_events"], "scripted_events")
    recorder = ScriptedEventRecorder()
    for event in raw_events:
        recorder.record(event)
    events = recorder.snapshot()
    effect_events = [event for event in events if event.get("kind") == "effect_receipt"]
    if len(effect_events) != 1:
        raise AudioHarnessError("scripted timeline must contain one effect_receipt")
    effect_events[0]["data"] = deepcopy(effect)
    expected = _object(manifest["expected"], "expected")
    final_transcripts = [
        event.get("text", "")
        for event in events
        if event.get("kind") == "transcript_final"
    ]
    receipt = {
        "schema_version": RECEIPT_VERSION,
        "case_id": manifest["case_id"],
        "source_audio": source_audio,
        "normalization": {
            "contract": "relative-event-time-only",
            "excludes": [
                "model inference",
                "network timing",
                "provider identifiers",
                "run identifiers",
                "wall clock",
            ],
        },
        "raw_script": {
            "sha256": hashlib.sha256(
                json.dumps(
                    raw_events,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
            ).hexdigest(),
            "events": deepcopy(raw_events),
        },
        "timeline": events,
        "transcript": {"finals": final_transcripts},
        "critical_entities": deepcopy(expected.get("critical_entities")),
        "task_facts": deepcopy(expected.get("task_facts")),
        "business_effect": effect,
        "engine_observations": {
            "event_kinds": [event.kind for event in run.events],
            "final_transcript_count": run.metrics["final_transcript_count"],
            "interruption_count": run.metrics["interruption_count"],
        },
        "evidence_boundary": (
            "Committed PCM/WAV bytes plus construction-known scripted events; "
            "this is orchestration evidence, not acoustic-model quality evidence."
        ),
    }
    validate_receipt(receipt, manifest)
    return receipt


def canonical_receipt_bytes(receipt: dict[str, Any]) -> bytes:
    return (
        json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode()


def _timeline(receipt: dict[str, Any]) -> list[dict[str, Any]]:
    return _objects(receipt.get("timeline"), "receipt.timeline")


def _validate_timeline(events: list[dict[str, Any]]) -> None:
    if not events:
        raise AudioHarnessError("timeline must not be empty")
    previous_ms = -1
    for index, event in enumerate(events, start=1):
        if event.get("sequence") != index:
            raise AudioHarnessError("timeline sequence must be contiguous from one")
        at_ms = event.get("at_ms")
        if not isinstance(at_ms, int) or at_ms < previous_ms:
            raise AudioHarnessError("timeline event times must be monotonic")
        previous_ms = at_ms
    kinds = [event.get("kind") for event in events]
    if kinds[0] != "audio_source_start" or kinds.count("audio_source_end") != 1:
        raise AudioHarnessError("timeline must contain exact source audio bounds")
    if kinds.count("effect_receipt") != 1 or kinds[-1] != "effect_receipt":
        raise AudioHarnessError("timeline must end with exactly one effect_receipt")
    for turn_id in {event.get("turn_id") for event in events if event.get("turn_id")}:
        turn_events = [event for event in events if event.get("turn_id") == turn_id]
        turn_kinds = [event.get("kind") for event in turn_events]
        if turn_kinds.count("transcript_final") != 1:
            raise AudioHarnessError(f"{turn_id} must contain one final transcript")
        final_index = turn_kinds.index("transcript_final")
        partial_indexes = [
            index
            for index, kind in enumerate(turn_kinds)
            if kind == "transcript_partial"
        ]
        if not partial_indexes or max(partial_indexes) > final_index:
            raise AudioHarnessError(
                f"{turn_id} final transcript must follow all partials"
            )
        eot_indexes = [
            index for index, kind in enumerate(turn_kinds) if kind == "end_of_turn"
        ]
        if len(eot_indexes) != 1 or eot_indexes[0] < final_index:
            raise AudioHarnessError(f"{turn_id} end_of_turn must follow its final")
        relation = [
            "transcript_final",
            "end_of_turn",
            "llm_start",
            "tool_start",
            "tool_end",
            "llm_end",
        ]
        try:
            positions = [turn_kinds.index(kind) for kind in relation]
        except ValueError as exc:
            raise AudioHarnessError(
                f"{turn_id} is missing a processing boundary"
            ) from exc
        if positions != sorted(positions) or len(set(positions)) != len(positions):
            raise AudioHarnessError(f"{turn_id} processing boundaries are out of order")
        response_kind = (
            "agent_audio_start" if turn_id == "turn-1" else "agent_audio_resumed"
        )
        if (
            response_kind not in turn_kinds
            or turn_kinds.index(response_kind) < positions[-1]
        ):
            raise AudioHarnessError(f"{turn_id} agent audio precedes processing end")
    interruption_indexes = [
        index
        for index, event in enumerate(events)
        if event.get("kind") == "caller_interruption"
    ]
    if len(interruption_indexes) != 1:
        raise AudioHarnessError("timeline must contain one caller_interruption")
    interruption_index = interruption_indexes[0]
    cancellation_indexes = [
        index
        for index, event in enumerate(events)
        if event.get("kind") == "agent_audio_cancelled"
    ]
    resume_indexes = [
        index
        for index, event in enumerate(events)
        if event.get("kind") == "agent_audio_resumed"
    ]
    if (
        len(cancellation_indexes) != 1
        or len(resume_indexes) != 1
        or not interruption_index < cancellation_indexes[0] < resume_indexes[0]
    ):
        raise AudioHarnessError("interruption must cancel agent audio before resume")


def _reject_nondeterministic_keys(value: object) -> None:
    forbidden = {"action_id", "created_at", "run_id", "timestamp", "wall_clock"}
    if isinstance(value, dict):
        overlap = forbidden.intersection(value)
        if overlap:
            raise AudioHarnessError(
                f"normalized receipt contains forbidden keys: {', '.join(sorted(overlap))}"
            )
        for child in value.values():
            _reject_nondeterministic_keys(child)
    elif isinstance(value, list):
        for child in value:
            _reject_nondeterministic_keys(child)


def validate_receipt(receipt: dict[str, Any], manifest: dict[str, Any]) -> None:
    if receipt.get("schema_version") != RECEIPT_VERSION:
        raise AudioHarnessError("receipt schema version is invalid")
    if receipt.get("case_id") != manifest.get("case_id"):
        raise AudioHarnessError("receipt case_id does not match manifest")
    events = _timeline(receipt)
    _validate_timeline(events)
    raw_script = _object(receipt.get("raw_script"), "receipt.raw_script")
    expected_raw_events = _objects(manifest["scripted_events"], "scripted_events")
    if raw_script.get("events") != expected_raw_events:
        raise AudioHarnessError("raw scripted events changed after manifest load")
    expected_raw_hash = hashlib.sha256(
        json.dumps(
            expected_raw_events,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    if raw_script.get("sha256") != expected_raw_hash:
        raise AudioHarnessError("raw scripted event hash does not match manifest")
    expected = _object(manifest["expected"], "expected")
    expected_finals = expected.get("transcript_finals")
    transcript = _object(receipt.get("transcript"), "receipt.transcript")
    if transcript.get("finals") != expected_finals:
        raise AudioHarnessError("final transcripts do not match construction truth")
    final_text = "\n".join(cast("list[str]", transcript["finals"]))
    entities = _objects(expected.get("critical_entities"), "critical_entities")
    for entity in entities:
        surface = entity.get("surface")
        if not isinstance(surface, str) or surface not in final_text:
            raise AudioHarnessError(
                f"critical entity is absent from final transcript: {entity.get('field')}"
            )
    if receipt.get("task_facts") != expected.get("task_facts"):
        raise AudioHarnessError("task facts do not match construction truth")
    if receipt.get("business_effect") != expected.get("business_effect"):
        raise AudioHarnessError("business effect does not match construction truth")
    effect_event = next(
        event for event in events if event.get("kind") == "effect_receipt"
    )
    if effect_event.get("data") != receipt.get("business_effect"):
        raise AudioHarnessError("timeline and normalized business effect disagree")
    observations = _object(receipt.get("engine_observations"), "engine_observations")
    if observations.get("event_kinds") != expected.get("engine_event_kinds"):
        raise AudioHarnessError(
            "engine event sequence does not match construction truth"
        )
    if observations.get("interruption_count") != 1:
        raise AudioHarnessError("engine did not observe exactly one interruption")
    _reject_nondeterministic_keys(receipt)


def _renumber(events: list[dict[str, Any]]) -> None:
    for sequence, event in enumerate(events, start=1):
        event["sequence"] = sequence


def mutant_receipts(clean: dict[str, Any]) -> dict[str, dict[str, Any]]:
    mutants: dict[str, dict[str, Any]] = {}

    dropped_final = deepcopy(clean)
    dropped_final["timeline"] = [
        event
        for event in _timeline(dropped_final)
        if not (
            event.get("kind") == "transcript_final" and event.get("turn_id") == "turn-2"
        )
    ]
    _renumber(_timeline(dropped_final))
    mutants["drop-final-transcript"] = dropped_final

    final_before_partial = deepcopy(clean)
    turn_two = [
        event
        for event in _timeline(final_before_partial)
        if event.get("turn_id") == "turn-2"
    ]
    partial = next(
        event for event in turn_two if event.get("kind") == "transcript_partial"
    )
    final = next(event for event in turn_two if event.get("kind") == "transcript_final")
    partial["kind"], final["kind"] = final["kind"], partial["kind"]
    mutants["final-before-last-partial"] = final_before_partial

    erased_entity = deepcopy(clean)
    erased_entity["transcript"]["finals"][1] = erased_entity["transcript"]["finals"][
        1
    ].replace("Mira Chen", "[erased]")
    for event in _timeline(erased_entity):
        if event.get("kind") == "transcript_final" and event.get("turn_id") == "turn-2":
            event["text"] = str(event.get("text", "")).replace("Mira Chen", "[erased]")
    mutants["erase-critical-entity"] = erased_entity

    early_eot = deepcopy(clean)
    pause = next(
        event for event in _timeline(early_eot) if event.get("kind") == "caller_pause"
    )
    pause["kind"] = "end_of_turn"
    mutants["clause-pause-becomes-eot"] = early_eot

    no_cancel = deepcopy(clean)
    no_cancel["timeline"] = [
        event
        for event in _timeline(no_cancel)
        if event.get("kind") != "agent_audio_cancelled"
    ]
    _renumber(_timeline(no_cancel))
    mutants["fail-agent-audio-cancel"] = no_cancel

    wrong_effect = deepcopy(clean)
    wrong_effect["business_effect"]["booking"]["id"] = "book_wrong"
    next(
        event
        for event in _timeline(wrong_effect)
        if event.get("kind") == "effect_receipt"
    )["data"] = deepcopy(wrong_effect["business_effect"])
    mutants["wrong-booking-crm-result"] = wrong_effect

    duplicate_effect = deepcopy(clean)
    events = _timeline(duplicate_effect)
    events.append(deepcopy(events[-1]))
    _renumber(events)
    mutants["duplicate-business-effect"] = duplicate_effect
    return mutants


def run_mutation_gate(manifest_path: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    clean = run_audio_harness(manifest_path)
    validate_receipt(clean, manifest)
    results: list[dict[str, object]] = []
    for mutant_id, receipt in mutant_receipts(clean).items():
        try:
            validate_receipt(receipt, manifest)
        except AudioHarnessError as exc:
            results.append({"id": mutant_id, "killed": True, "reason": str(exc)})
        else:
            results.append({"id": mutant_id, "killed": False, "reason": "survived"})
    return {
        "schema_version": "firstring.audio-harness-mutation-report/v0",
        "clean_control": "PASS",
        "mutants_killed": sum(result["killed"] is True for result in results),
        "mutants_total": len(results),
        "results": results,
    }
