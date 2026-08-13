from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

SAMPLE_RATE_HZ = 8_000
FRAME_COUNT = 9_600
OUTPUT = Path(__file__).parents[1] / "tests" / "fixtures" / "audio" / "v0_call.wav"


def active(frame: int, ranges_ms: tuple[tuple[int, int], ...]) -> bool:
    at_ms = frame * 1_000 // SAMPLE_RATE_HZ
    return any(start <= at_ms < end for start, end in ranges_ms)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    caller_ranges = ((0, 105), (260, 700))
    agent_ranges = ((120, 260), (380, 920))
    with wave.open(str(OUTPUT), "wb") as target:
        target.setnchannels(2)
        target.setsampwidth(2)
        target.setframerate(SAMPLE_RATE_HZ)
        for frame in range(FRAME_COUNT):
            caller = (
                int(4_000 * math.sin(2 * math.pi * 220 * frame / SAMPLE_RATE_HZ))
                if active(frame, caller_ranges)
                else 0
            )
            agent = (
                int(3_000 * math.sin(2 * math.pi * 440 * frame / SAMPLE_RATE_HZ))
                if active(frame, agent_ranges)
                else 0
            )
            target.writeframesraw(struct.pack("<hh", caller, agent))


if __name__ == "__main__":
    main()
