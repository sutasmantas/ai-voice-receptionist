from __future__ import annotations

import hashlib
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any, cast

from deliveryguard import (
    ActionState,
    DeliveryExecutor,
    RetryPolicy,
    make_idempotency_key,
)

from firstring.contracts import DeterministicStt, DeterministicTts
from firstring.faq import lookup_faq
from firstring.integrations.delivery import ClosingDeliveryStore, FixtureWebhookAdapter
from firstring.integrations.leaddock import LocalCalendarAdapter, LocalCrmAdapter
from firstring.models import CallEvent, CallRun
from firstring.store import CallStore


class ScenarioError(ValueError):
    pass


class CallEngine:
    RESPONSE_LATENCY_MS = 120

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.store = CallStore(self.database_path)
        self.delivery_store = ClosingDeliveryStore(
            self.database_path.with_name(
                f"{self.database_path.stem}-deliveries.sqlite3"
            )
        )
        self.calendar = LocalCalendarAdapter()
        self.crm = LocalCrmAdapter()
        self.stt = DeterministicStt()
        self.tts = DeterministicTts()
        self._runs: dict[str, CallRun] = {}
        self._adapters: dict[str, FixtureWebhookAdapter] = {}
        self._handoff_payloads: dict[str, dict[str, Any]] = {}

    def run(self, raw_scenario: dict[str, object]) -> CallRun:
        scenario = self._validate(raw_scenario)
        run_id = f"call_{uuid.uuid4().hex[:12]}"
        events = [CallEvent("call_started", 0, "system", data={"run_id": run_id})]
        outcome = "answered"
        transfer_reason: str | None = None
        booking: dict[str, Any] | None = None
        captured_entities: dict[str, str] = {}
        topics: list[str] = []
        final_transcripts = 0
        interruption_count = 0
        active_speech_end = 0

        for turn in scenario["turns"]:
            at_ms = cast("int", turn["at_ms"])
            text = cast("str", turn["text"])
            intent = cast("str", turn["intent"])
            if turn.get("interrupt") and active_speech_end > at_ms:
                events.append(
                    CallEvent(
                        "assistant_interrupted",
                        at_ms,
                        "receptionist",
                        data={"original_end_ms": active_speech_end},
                    )
                )
                interruption_count += 1
                active_speech_end = at_ms

            if failure := turn.get("failure"):
                events.append(
                    CallEvent(
                        "provider_failure",
                        at_ms,
                        "system",
                        text=str(failure),
                        data={"provider": "stt", "recoverable": True},
                    )
                )
                continue
            if recovery := turn.get("recovery"):
                events.append(
                    CallEvent(
                        "provider_recovered",
                        at_ms,
                        "system",
                        text=str(recovery),
                    )
                )

            for chunk in self.stt.transcribe(text):
                kind = "stt_final" if chunk.final else "stt_partial"
                events.append(
                    CallEvent(kind, at_ms + chunk.offset_ms, "caller", chunk.text)
                )
                if chunk.final:
                    final_transcripts += 1

            response = ""
            response_data: dict[str, Any] = {}
            if intent == "faq":
                topics.append("faq")
                match = lookup_faq(text)
                if match.found:
                    response = cast("str", match.answer)
                    response_data = {
                        "question": match.question,
                        "score": round(match.score, 1),
                    }
                    events.append(
                        CallEvent(
                            "faq_answered",
                            at_ms + 90,
                            "tool",
                            data=response_data,
                        )
                    )
                else:
                    outcome = "transfer"
                    transfer_reason = "faq_not_found"
                    response = (
                        "I do not have that in the approved information. "
                        "I will transfer you to a person."
                    )
                    events.append(
                        CallEvent(
                            "faq_not_found",
                            at_ms + 90,
                            "tool",
                            data={"score": round(match.score, 1)},
                        )
                    )
                    events.append(
                        CallEvent(
                            "human_transfer",
                            at_ms + 100,
                            "tool",
                            data={"reason": transfer_reason},
                        )
                    )
            elif intent == "book":
                topics.append("booking")
                if not scenario["business_open"]:
                    outcome = "transfer"
                    transfer_reason = "after_hours"
                    response = (
                        "The desk is closed. I will record your request for a callback."
                    )
                    events.append(
                        CallEvent(
                            "human_transfer",
                            at_ms + 90,
                            "tool",
                            data={"reason": transfer_reason},
                        )
                    )
                else:
                    entities = cast("dict[str, str]", turn.get("entities", {}))
                    self._require_booking_entities(entities)
                    captured_entities.update(entities)
                    lead = self._lead(entities)
                    crm = self.crm.upsert(lead)
                    booked, replayed = self.calendar.book(
                        lead["id"], entities["slot_start"], entities["timezone"]
                    )
                    booking = asdict(booked)
                    outcome = "booked"
                    event_kind = "booking_replayed" if replayed else "booking_created"
                    events.append(
                        CallEvent(
                            event_kind,
                            at_ms + 90,
                            "tool",
                            data={"booking": booking, "crm_id": crm["id"]},
                        )
                    )
                    response = "Your thirty-minute appointment is confirmed."
            elif intent == "opt_out":
                topics.append("opt_out")
                outcome = "opted_out"
                transfer_reason = "caller_opt_out"
                response = "Understood. I will not create a booking or follow-up."
                events.append(CallEvent("opt_out_recorded", at_ms + 90, "tool"))
            else:
                raise ScenarioError(f"unsupported intent: {intent}")

            response_at = at_ms + self.RESPONSE_LATENCY_MS
            chunks = self.tts.synthesize(response)
            speech_duration = sum(chunk.duration_ms for chunk in chunks)
            active_speech_end = response_at + speech_duration
            events.append(
                CallEvent(
                    "assistant_response",
                    response_at,
                    "receptionist",
                    response,
                    {"end_ms": active_speech_end, **response_data},
                )
            )

        expected = cast("dict[str, str]", scenario.get("expected_entities", {}))
        entity_accuracy = self._entity_accuracy(expected, captured_entities)
        summary = {
            "outcome": outcome,
            "topics": list(dict.fromkeys(topics)),
            "caller": {
                key: captured_entities[key]
                for key in ("name", "email", "phone")
                if key in captured_entities
            },
            "booking": booking,
            "transfer_reason": transfer_reason,
        }
        metrics: dict[str, float | int] = {
            "entity_accuracy": entity_accuracy,
            "max_response_latency_ms": self.RESPONSE_LATENCY_MS,
            "final_transcript_count": final_transcripts,
            "interruption_count": interruption_count,
        }
        events.append(
            CallEvent(
                "summary_created",
                max((event.at_ms for event in events), default=0) + 20,
                "system",
                data=summary,
            )
        )
        run = CallRun(
            id=run_id,
            scenario_id=cast("str", scenario["id"]),
            title=cast("str", scenario["title"]),
            outcome=outcome,
            events=sorted(events, key=lambda event: event.at_ms),
            summary=summary,
            metrics=metrics,
            booking=booking,
        )
        self._deliver_handoff(run, cast("int", scenario["handoff_failures"]))
        self._runs[run.id] = run
        self.store.save(run)
        return run

    def replay_handoff(self, run_id: str) -> CallRun:
        if run_id not in self._runs:
            raise KeyError(f"unknown call run: {run_id}")
        run = self._runs[run_id]
        if run.handoff_action_id is None:
            raise ScenarioError("call run has no handoff action")
        adapter = self._adapters[run.id]
        adapter.failures_remaining = 0
        executor = DeliveryExecutor(
            self.delivery_store,
            adapter,
            policy=RetryPolicy(max_attempts=3, wait_seconds=0),
        )
        record = executor.replay(
            run.handoff_action_id,
            payload=self._handoff_payloads[run.id],
            correlation_id=f"replay-{run.id}",
        )
        run.handoff_state = record.state.value
        run.events.append(
            CallEvent(
                "handoff_replayed",
                max(event.at_ms for event in run.events) + 20,
                "tool",
                data={"state": record.state.value, "action_id": record.id},
            )
        )
        self.store.save(run)
        return run

    def _deliver_handoff(self, run: CallRun, failures: int) -> None:
        if (
            run.outcome in {"opted_out"}
            or run.summary["transfer_reason"] == "after_hours"
        ):
            run.handoff_state = "suppressed"
            run.events.append(
                CallEvent(
                    "handoff_suppressed",
                    max(event.at_ms for event in run.events) + 20,
                    "tool",
                    data={"reason": run.summary["transfer_reason"]},
                )
            )
            return
        payload = {"call_id": run.id, **run.summary}
        adapter = FixtureWebhookAdapter(failures)
        executor = DeliveryExecutor(
            self.delivery_store,
            adapter,
            policy=RetryPolicy(max_attempts=3, wait_seconds=0),
        )
        record = executor.deliver(
            idempotency_key=make_idempotency_key("firstring", payload),
            destination="generic-crm-webhook",
            payload=payload,
            correlation_id=run.id,
        )
        run.handoff_state = record.state.value
        run.handoff_action_id = record.id
        self._adapters[run.id] = adapter
        self._handoff_payloads[run.id] = payload
        kind = (
            "handoff_dead_letter"
            if record.state is ActionState.DEAD_LETTER
            else "handoff_delivered"
        )
        run.events.append(
            CallEvent(
                kind,
                max(event.at_ms for event in run.events) + 20,
                "tool",
                data={"state": record.state.value, "action_id": record.id},
            )
        )

    @staticmethod
    def _validate(raw: dict[str, object]) -> dict[str, Any]:
        required = ("id", "title", "business_open", "turns")
        missing = [key for key in required if key not in raw]
        if missing:
            raise ScenarioError(f"missing scenario fields: {', '.join(missing)}")
        turns = raw["turns"]
        if not isinstance(turns, list) or not turns:
            raise ScenarioError("turns must be a non-empty list")
        previous = -1
        for turn in turns:
            if not isinstance(turn, dict):
                raise ScenarioError("each turn must be an object")
            at_ms = turn.get("at_ms")
            if not isinstance(at_ms, int) or at_ms <= previous:
                raise ScenarioError("turn timestamps must be strictly increasing")
            for field in ("text", "intent"):
                if not isinstance(turn.get(field), str) or not turn[field]:
                    raise ScenarioError(f"turn {field} must be a non-empty string")
            previous = at_ms
        handoff_failures = raw.get("handoff_failures", 0)
        if not isinstance(handoff_failures, int) or not 0 <= handoff_failures <= 10:
            raise ScenarioError("handoff_failures must be an integer from zero to ten")
        scenario = dict(raw)
        scenario["handoff_failures"] = handoff_failures
        return scenario

    @staticmethod
    def _require_booking_entities(entities: dict[str, str]) -> None:
        required = ("name", "email", "phone", "timezone", "slot_start")
        missing = [field for field in required if not entities.get(field)]
        if missing:
            raise ScenarioError(f"missing booking entities: {', '.join(missing)}")

    @staticmethod
    def _lead(entities: dict[str, str]) -> dict[str, Any]:
        identity = entities["email"].lower()
        return {
            "id": f"lead_{hashlib.sha1(identity.encode()).hexdigest()[:10]}",
            "identity_key": identity,
            "name": entities["name"],
            "email": identity,
            "phone": entities["phone"],
            "company": "Voice caller",
            "qualification": {"tier": "inbound", "score": 100},
        }

    @staticmethod
    def _entity_accuracy(expected: dict[str, str], captured: dict[str, str]) -> float:
        if not expected:
            return 1.0
        correct = sum(captured.get(key) == value for key, value in expected.items())
        return round(correct / len(expected), 3)
