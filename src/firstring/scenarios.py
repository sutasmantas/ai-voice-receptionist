from __future__ import annotations

from copy import deepcopy
from typing import Any

SCENARIOS: list[dict[str, Any]] = [
    {
        "id": "successful-booking",
        "title": "Grounded answer and idempotent booking",
        "business_open": True,
        "expected_entities": {
            "name": "Mira Chen",
            "email": "mira@northstar.example",
            "phone": "+37060010001",
            "timezone": "Europe/Vilnius",
            "slot_start": "2026-08-03T06:00:00+00:00",
        },
        "turns": [
            {"at_ms": 0, "text": "How long is an appointment?", "intent": "faq"},
            {
                "at_ms": 1800,
                "text": "Book me for Monday at nine.",
                "intent": "book",
                "entities": {
                    "name": "Mira Chen",
                    "email": "mira@northstar.example",
                    "phone": "+37060010001",
                    "timezone": "Europe/Vilnius",
                    "slot_start": "2026-08-03T06:00:00+00:00",
                },
            },
            {
                "at_ms": 3200,
                "text": "Please confirm that same booking.",
                "intent": "book",
                "entities": {
                    "name": "Mira Chen",
                    "email": "mira@northstar.example",
                    "phone": "+37060010001",
                    "timezone": "Europe/Vilnius",
                    "slot_start": "2026-08-03T06:00:00+00:00",
                },
            },
        ],
    },
    {
        "id": "caller-interruption",
        "title": "Caller interrupts a long answer",
        "business_open": True,
        "turns": [
            {
                "at_ms": 0,
                "text": "Tell me about your appointment policy.",
                "intent": "faq",
            },
            {
                "at_ms": 260,
                "text": "Actually, what are your hours?",
                "intent": "faq",
                "interrupt": True,
            },
        ],
    },
    {
        "id": "unknown-faq",
        "title": "Unknown question transfers to a human",
        "business_open": True,
        "turns": [{"at_ms": 0, "text": "Do you repair submarines?", "intent": "faq"}],
    },
    {
        "id": "after-hours",
        "title": "After-hours caller receives a transfer fallback",
        "business_open": False,
        "turns": [
            {
                "at_ms": 0,
                "text": "I need to book an appointment.",
                "intent": "book",
                "entities": {},
            }
        ],
    },
    {
        "id": "opt-out",
        "title": "Caller opts out",
        "business_open": True,
        "turns": [
            {"at_ms": 0, "text": "Do not contact me again.", "intent": "opt_out"}
        ],
    },
    {
        "id": "recovery-dead-letter",
        "title": "Speech recovery and failed webhook",
        "business_open": True,
        "handoff_failures": 3,
        "turns": [
            {
                "at_ms": 0,
                "text": "static",
                "intent": "failure",
                "failure": "stt_unavailable",
            },
            {
                "at_ms": 400,
                "text": "What are your hours?",
                "intent": "faq",
                "recovery": "stt",
            },
        ],
    },
]


def scenario_inventory() -> list[dict[str, str]]:
    return [{"id": item["id"], "title": item["title"]} for item in SCENARIOS]


def get_scenario(scenario_id: str) -> dict[str, Any]:
    for scenario in SCENARIOS:
        if scenario["id"] == scenario_id:
            return deepcopy(scenario)
    raise KeyError(f"unknown scenario: {scenario_id}")
