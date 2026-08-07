from __future__ import annotations

import pytest

# inspect_ai and proofgrid are not declared dependencies of this project and are
# not installed by CI, so this module cannot collect there. Skip explicitly
# rather than breaking collection for the whole suite. The recorded evaluation
# artifacts live in docs/evidence/inspect/; they are committed results, not
# something this workflow re-executes.
inspect_ai = pytest.importorskip("inspect_ai", reason="inspect_ai is not installed")
proofgrid_integration = pytest.importorskip(
    "proofgrid.inspect_integration", reason="proofgrid is not installed"
)

inspect_eval = inspect_ai.eval
import_inspect_log = proofgrid_integration.import_inspect_log

from firstring.inspect_eval import firstring_contracts  # noqa: E402


def execute(tmp_path, *, fail_open_mutant: bool = False):
    task = firstring_contracts(
        run_dir=str(tmp_path / "state"),
        fail_open_mutant=fail_open_mutant,
    )
    return inspect_eval(
        task,
        model="mockllm/model",
        log_dir=str(tmp_path / "logs"),
        log_format="json",
        display="none",
    )[0]


def test_real_firstring_scenarios_pass_the_shared_contract(tmp_path):
    result = import_inspect_log(execute(tmp_path))

    summary = result["candidates"][0]["summary"]
    rows = {row["case_id"]: row for row in result["candidates"][0]["rows"]}
    assert result["decision"]["winner"] == "firstring_contracts"
    assert summary["evaluated_cases"] == 4
    assert summary["pass_rate"] == 1
    assert rows["recovery-dead-letter"]["passed"] is True
    assert rows["unknown-faq"]["passed"] is True


def test_shared_contract_kills_the_fail_open_faq_mutation(tmp_path):
    result = import_inspect_log(execute(tmp_path, fail_open_mutant=True))

    rows = {row["case_id"]: row for row in result["candidates"][0]["rows"]}
    assert result["decision"]["winner"] is None
    assert sum(row["passed"] for row in rows.values()) == 3
    assert rows["unknown-faq"]["passed"] is False
    assert rows["unknown-faq"]["failure_class"] == "contract_mismatch"
