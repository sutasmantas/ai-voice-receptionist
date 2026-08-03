from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from firstring.app import create_app


def client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(tmp_path / "api.sqlite3"))


def test_health_and_scenario_inventory(tmp_path: Path) -> None:
    with client(tmp_path) as test_client:
        assert test_client.get("/health").json() == {
            "status": "ok",
            "mode": "deterministic-simulator",
        }
        scenarios = test_client.get("/api/scenarios").json()

    assert len(scenarios) == 6
    assert {item["id"] for item in scenarios} >= {
        "successful-booking",
        "caller-interruption",
        "recovery-dead-letter",
    }


def test_run_and_replay_endpoints(tmp_path: Path) -> None:
    with client(tmp_path) as test_client:
        booking = test_client.post("/api/runs/successful-booking")
        failed = test_client.post("/api/runs/recovery-dead-letter")
        replayed = test_client.post(f"/api/runs/{failed.json()['id']}/replay-handoff")

    assert booking.status_code == 201
    assert booking.json()["outcome"] == "booked"
    assert booking.json()["handoff_state"] == "delivered"
    assert failed.json()["handoff_state"] == "dead_letter"
    assert replayed.json()["handoff_state"] == "delivered"


def test_call_score_is_the_working_home_surface(tmp_path: Path) -> None:
    with client(tmp_path) as test_client:
        response = test_client.get("/")

    assert response.status_code == 200
    assert "CALL SCORE" in response.text
    assert "Outcome ticket" in response.text
    assert 'data-lane="caller"' in response.text
    assert "sidebar" not in response.text.lower()
