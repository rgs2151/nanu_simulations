"""Record installed software versions for the simulation workspace."""
from __future__ import annotations

import argparse
import csv
import json
import platform
from importlib.metadata import distributions
from pathlib import Path

UNIT_DIR = Path(__file__).resolve().parent
CACHE_PATH = UNIT_DIR / "cache" / "environment_inventory.json"
TABLE_PATH = UNIT_DIR / "plots" / "environment_inventory.csv"


def collect_inventory() -> list[dict[str, str]]:
    rows = [{"component": "Python", "version": platform.python_version()}]
    rows.extend(
        {"component": dist.metadata["Name"], "version": dist.version}
        for dist in distributions()
        if dist.metadata["Name"]
    )
    return sorted(rows, key=lambda row: (row["component"].casefold(), row["version"]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recompute", action="store_true", help="Refresh the cached environment inventory.")
    args = parser.parse_args()
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if CACHE_PATH.exists() and not args.recompute:
        rows = json.loads(CACHE_PATH.read_text())
    else:
        rows = collect_inventory()
        CACHE_PATH.write_text(json.dumps(rows, indent=2) + "\n")

    TABLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TABLE_PATH.unlink(missing_ok=True)
    with TABLE_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["component", "version"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
