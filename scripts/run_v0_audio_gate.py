from __future__ import annotations

import argparse
import json
from pathlib import Path

from firstring.audio_harness import (
    canonical_receipt_bytes,
    run_audio_harness,
    run_mutation_gate,
)

DEFAULT_MANIFEST = Path("tests/fixtures/audio/manifest.json")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic V0 audio gate")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--mutation-report", type=Path)
    arguments = parser.parse_args()

    receipt = run_audio_harness(arguments.manifest)
    report = run_mutation_gate(arguments.manifest)
    if arguments.receipt:
        arguments.receipt.parent.mkdir(parents=True, exist_ok=True)
        arguments.receipt.write_bytes(canonical_receipt_bytes(receipt))
    if arguments.mutation_report:
        arguments.mutation_report.parent.mkdir(parents=True, exist_ok=True)
        arguments.mutation_report.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["mutants_killed"] == report["mutants_total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
