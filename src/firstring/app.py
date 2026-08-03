from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from firstring.engine import CallEngine, ScenarioError
from firstring.scenarios import get_scenario, scenario_inventory

PACKAGE_ROOT = Path(__file__).parent


def create_app(database_path: str | Path = "runtime/firstring.sqlite3") -> FastAPI:
    app = FastAPI(
        title="FirstRing",
        description="Deterministic voice-receptionist simulator evidence API",
        version="0.1.0",
    )
    engine = CallEngine(database_path)
    templates = Jinja2Templates(directory=PACKAGE_ROOT / "templates")
    app.mount("/static", StaticFiles(directory=PACKAGE_ROOT / "static"), name="static")
    initial = engine.run(get_scenario("successful-booking"))

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "deterministic-simulator"}

    @app.get("/api/scenarios")
    def scenarios() -> list[dict[str, str]]:
        return scenario_inventory()

    @app.post("/api/runs/{scenario_id}", status_code=status.HTTP_201_CREATED)
    def run_scenario(scenario_id: str) -> dict[str, object]:
        try:
            return engine.run(get_scenario(scenario_id)).to_dict()
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from None
        except ScenarioError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from None

    @app.post("/api/runs/{run_id}/replay-handoff")
    def replay_handoff(run_id: str) -> dict[str, object]:
        try:
            return engine.replay_handoff(run_id).to_dict()
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from None
        except ScenarioError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from None

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "scenarios": scenario_inventory(),
                "initial_json": json.dumps(initial.to_dict()),
            },
        )

    app.state.engine = engine
    return app


app = create_app()
