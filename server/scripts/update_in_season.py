"""End-to-end in-season refresh.

Fetches latest Cricsheet data, rebuilds the real ball-by-ball CSV and priors,
regenerates the 2026 roster from updated appearances, then runs the full
pipeline (setup -> train -> predict -> visualize) so predictions reflect every
match played up to yesterday.

Run this daily (or after each match day) to keep predictions current.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def step(label: str, cmd: list[str]) -> None:
    print(f"\n{'=' * 70}\n{label}\n{'=' * 70}")
    result = subprocess.run(cmd, cwd=ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit(f"Step failed: {label} (rc={result.returncode})")


def main() -> None:
    py = sys.executable
    step("[1/5] Fetch latest Cricsheet IPL archive", [py, "scripts/fetch_cricsheet_ipl.py"])
    step(
        "[2/5] Rebuild real ball-by-ball CSV + priors from Cricsheet",
        [py, "scripts/rebuild_from_cricsheet.py"],
    )
    step("[3/5] Regenerate projected 2026 rosters", [py, "scripts/build_rosters_2026.py"])
    step(
        "[4/5] Extract matches.csv + player_stats.csv from JSONs",
        [py, "-c", "from src.data.create_dataset import run_ingestion; run_ingestion()"],
    )
    step(
        "[5/5] DB setup -> preprocess -> features -> train -> predict",
        [py, "scripts/rebuild_all.py", "--tournament", "ipl"],
    )
    print("\n[OK] In-season refresh complete.")


if __name__ == "__main__":
    main()
