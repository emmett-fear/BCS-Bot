import os
from pathlib import Path

SEASON = int(os.getenv("BCS_SEASON", "2026"))
WEEK = os.getenv("BCS_WEEK", "current")
WEEK_TAG = os.getenv("BCS_WEEK_TAG", "2026-09-27")

DATA_ROOT = Path("data") / str(SEASON) / WEEK

def output_path(name: str) -> str:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    return str(DATA_ROOT / f"{name}.json")
