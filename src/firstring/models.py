from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class CallEvent:
    kind: str
    at_ms: int
    lane: str
    text: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CallRun:
    id: str
    scenario_id: str
    title: str
    outcome: str
    events: list[CallEvent]
    summary: dict[str, Any]
    metrics: dict[str, float | int]
    booking: dict[str, Any] | None = None
    handoff_state: str = "pending"
    handoff_action_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["events"] = [event.to_dict() for event in self.events]
        return value
