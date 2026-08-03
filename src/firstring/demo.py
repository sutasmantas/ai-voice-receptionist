from __future__ import annotations

import argparse
import json
from pathlib import Path

from firstring.engine import CallEngine
from firstring.scenarios import get_scenario, scenario_inventory


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a deterministic FirstRing call")
    parser.add_argument("--scenario", default="successful-booking")
    parser.add_argument("--database", type=Path, default=Path("runtime/demo.sqlite3"))
    parser.add_argument("--list", action="store_true", dest="list_scenarios")
    args = parser.parse_args()
    if args.list_scenarios:
        print(json.dumps(scenario_inventory(), indent=2))
        return 0
    run = CallEngine(args.database).run(get_scenario(args.scenario))
    print(json.dumps(run.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
