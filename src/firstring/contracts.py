from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class TranscriptChunk:
    text: str
    final: bool
    offset_ms: int


@dataclass(frozen=True)
class AgentDecision:
    text: str
    intent: str
    data: dict[str, Any]


@dataclass(frozen=True)
class AudioChunk:
    sequence: int
    duration_ms: int


class StreamingStt(Protocol):
    def transcribe(self, text: str) -> list[TranscriptChunk]: ...


class ReasoningAdapter(Protocol):
    def decide(
        self, intent: str, text: str, entities: dict[str, str]
    ) -> AgentDecision: ...


class StreamingTts(Protocol):
    def synthesize(self, text: str) -> list[AudioChunk]: ...


class DeterministicStt:
    """No-key streaming STT contract used by fixtures and tests."""

    def transcribe(self, text: str) -> list[TranscriptChunk]:
        words = text.split()
        midpoint = max(1, len(words) // 2)
        return [
            TranscriptChunk(" ".join(words[:midpoint]), False, 35),
            TranscriptChunk(text, True, 80),
        ]


class DeterministicTts:
    """No-key TTS timing contract; it emits durations, not synthetic audio."""

    def synthesize(self, text: str) -> list[AudioChunk]:
        total = max(360, len(text) * 16)
        first = total // 2
        return [AudioChunk(1, first), AudioChunk(2, total - first)]
