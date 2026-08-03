from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz import fuzz, process

FAQS = {
    "what are your hours": "We are open Monday through Friday from nine to five.",
    "how long is an appointment": "A standard appointment lasts thirty minutes.",
    "what is your appointment policy": (
        "Appointments are thirty minutes. You can reschedule before the start "
        "time, and a receptionist can help with exceptional requests."
    ),
}


@dataclass(frozen=True)
class FaqMatch:
    found: bool
    question: str | None
    answer: str | None
    score: float


def lookup_faq(query: str, threshold: float = 72.0) -> FaqMatch:
    match = process.extractOne(query.lower(), FAQS.keys(), scorer=fuzz.token_set_ratio)
    if match is None or float(match[1]) < threshold:
        return FaqMatch(False, None, None, float(match[1]) if match else 0.0)
    question = str(match[0])
    return FaqMatch(True, question, FAQS[question], float(match[1]))
