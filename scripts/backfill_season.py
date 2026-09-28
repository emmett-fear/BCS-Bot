"""One-time (or re-runnable) job that fills in every past week of the
current season so the site can show week-by-week history, not just whatever
week happens to be "current" right now.

For each past week this scrapes:
  - AP + Coaches polls, reconstructed from Wikipedia's rank-order archive
    (see scrapers/wiki_polls.py for why -- ncaa.com/USA Today have no
    historical archive to scrape directly).
  - Colley and Billingsley, which both publish real dated per-week archives.

It deliberately does NOT invent historical Marbles, Sagarin, Massey,
Anderson-Hester, or Wolfe data -- none of those sources expose a past-week
archive, and compute_bcs already handles missing sources by scoring with
whichever ones are actually available that week (Classic BCS still computes
off AP + Coaches + Colley/Billingsley; BCS+ is left blank for weeks with no
Marbles data, exactly like any other week a source doesn't publish).

Usage:
    python scripts/backfill_season.py            # weeks 1..(current-1)
    python scripts/backfill_season.py 1 2 3       # specific week numbers

The current week itself is left to the normal scrapers/run_all.py pipeline,
which gets real point totals and live Marbles/computer data.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEASON = 2026
CURRENT_WEEK_NUMBER = 4

# AP-poll week number -> the Sunday date its poll was released, taken from
# the Week N column headers on the Wikipedia rankings table (the same dates
# ncaa.com and USA Today used for those weeks' own poll releases).
WEEK_DATES = {
    1: "2026-09-08",
    2: "2026-09-13",
    3: "2026-09-20",
    4: "2026-09-27",
}

def run(args, env_extra):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    env.update(env_extra)
    print("+ " + " ".join(args), flush=True)
    subprocess.check_call(args, cwd=ROOT, env=env)

def backfill_week(week_number):
    date_tag = WEEK_DATES[week_number]
    env = {
        "BCS_SEASON": str(SEASON),
        "BCS_WEEK": date_tag,
        "BCS_WEEK_TAG": date_tag,
        "BCS_WEEK_NUMBER": str(week_number),
    }
    run([sys.executable, "scrapers/wiki_polls.py"], env)
    run([sys.executable, "scrapers/colley.py"], env)
    run([sys.executable, "scrapers/billingsley.py"], env)
    run([sys.executable, "-m", "core.compute_bcs"], env)

    # compute_bcs compares against data/latest.json to compute movement.
    # Chaining that file forward through each backfilled week (in
    # chronological order) gives real week-over-week deltas through the
    # whole archive; the live pipeline overwrites it again afterward once
    # the current week is scraped for real.
    standings = ROOT / "data" / str(SEASON) / date_tag / "standings.json"
    latest = ROOT / "data" / "latest.json"
    latest.write_text(standings.read_text())

def main():
    weeks = [int(w) for w in sys.argv[1:]] or list(range(1, CURRENT_WEEK_NUMBER))
    print(f"Backfilling weeks: {weeks}")
    for week_number in weeks:
        if week_number not in WEEK_DATES:
            raise SystemExit(f"No known date for week {week_number}; add it to WEEK_DATES.")
        backfill_week(week_number)
    print("Backfill complete.")

if __name__ == "__main__":
    main()
