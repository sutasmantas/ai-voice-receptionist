from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from firstring.models import CallRun


class CallStore:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS call_runs (
                    id TEXT PRIMARY KEY,
                    scenario_id TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    run_json TEXT NOT NULL
                )
                """
            )

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def save(self, run: CallRun) -> None:
        payload = json.dumps(run.to_dict(), sort_keys=True)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO call_runs (id, scenario_id, outcome, run_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    outcome = excluded.outcome,
                    run_json = excluded.run_json
                """,
                (run.id, run.scenario_id, run.outcome, payload),
            )

    def list_payloads(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT run_json FROM call_runs ORDER BY rowid DESC"
            ).fetchall()
        return [json.loads(row["run_json"]) for row in rows]
