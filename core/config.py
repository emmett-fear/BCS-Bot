import os
from pathlib import Path

SEASON = int(os.getenv("BCS_SEASON", "2026"))
WEEK = os.getenv("BCS_WEEK", "current")
WEEK_TAG = os.getenv("BCS_WEEK_TAG", "2026-09-27")

# The AP-poll week number (1 = the poll released after week 1's games, etc.).
# Sources that publish week-indexed archives (Colley, Billingsley) are keyed
# off this rather than WEEK_TAG's date, since their own week numbering can be
# offset from the AP's (see scrapers/billingsley.py).
WEEK_NUMBER = int(os.getenv("BCS_WEEK_NUMBER", "4"))

DATA_ROOT = Path("data") / str(SEASON) / WEEK

def output_path(name: str) -> str:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    return str(DATA_ROOT / f"{name}.json")
