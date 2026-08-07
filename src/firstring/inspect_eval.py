from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.model import ModelOutput
from inspect_ai.solver import Generate, TaskState, solver
from proofgrid.inspect_integration import (
    CONTRACT_VERSION,
    INSPECT_AI_REVISION,
    json_schema_contract,
)

from firstring.engine import CallEngine

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures"
ORACLES = ROOT / "evals" / "firstring_oracles.json"
CASES = (
    ("successful_booking.json", "booking"),
    ("unknown_faq.json", "grounding-failure"),
    ("recovery_and_dead_letter.json", "provider-failure"),
    ("interruption.json", "turn-taking"),
)


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _observation(run: Any) -> dict[str, Any]:
    return {
        "scenario_id": run.scenario_id,
        "outcome": run.outcome,
        "handoff_state": run.handoff_state,
        "event_kinds": [event.kind for event in run.events],
        "summary": run.summary,
        "metrics": run.metrics,
    }


@solver
def execute_firstring(*, fail_open_mutant: bool = False) -> Any:
    """Execute FirstRing's real deterministic engine for one Inspect sample."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        fixture = FIXTURES / str(state.metadata["fixture"])
        database = Path(str(state.metadata["run_dir"])) / f"{state.sample_id}.sqlite3"
        database.parent.mkdir(parents=True, exist_ok=True)
        observed = _observation(CallEngine(database).run(_json(fixture)))
        if fail_open_mutant and observed["scenario_id"] == "unknown-faq":
            observed["outcome"] = "answered"
            observed["summary"]["transfer_reason"] = None
            observed["event_kinds"] = [
                kind
                for kind in observed["event_kinds"]
                if kind not in {"faq_not_found", "human_transfer"}
            ]
        state.output = ModelOutput.from_content(
            model="firstring/deterministic-engine",
            content=json.dumps(observed, ensure_ascii=False, sort_keys=True),
        )
        return state

    return solve


@task
def firstring_contracts(
    *, run_dir: str = ".inspect/firstring", fail_open_mutant: bool = False
) -> Task:
    """Evaluate grounded routing, recovery, delivery, and interruption contracts."""

    oracles = _json(ORACLES)
    samples = []
    for fixture_name, category in CASES:
        scenario = _json(FIXTURES / fixture_name)
        scenario_id = str(scenario["id"])
        samples.append(
            Sample(
                id=scenario_id,
                input=f"Execute FirstRing scenario {scenario_id}",
                target=json.dumps(
                    oracles[scenario_id], ensure_ascii=False, sort_keys=True
                ),
                metadata={
                    "fixture": fixture_name,
                    "run_dir": run_dir,
                    "split": "heldout",
                    "category": category,
                },
            )
        )
    return Task(
        dataset=samples,
        solver=execute_firstring(fail_open_mutant=fail_open_mutant),
        scorer=json_schema_contract(),
        name="firstring_contracts",
        version="1",
        metadata={
            "proofgrid_contract": CONTRACT_VERSION,
            "inspect_revision": INSPECT_AI_REVISION,
            "mutation": "fail-open-unknown-faq" if fail_open_mutant else None,
        },
    )
