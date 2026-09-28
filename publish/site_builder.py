import json, os, re, shutil
from datetime import datetime
from pathlib import Path
from core.io import read_json, write_json, timestamp
from core.log import info
from core.config import DATA_ROOT, SEASON

DATE_FOLDER = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def build_season_history(season: int = SEASON):
    """Scan every dated weekly snapshot (data/<season>/YYYY-MM-DD/standings.json,
    written by the weekly workflow's "preserve dated snapshot" step and by
    scripts/backfill_season.py for past weeks) and emit season_data.js: one
    array entry per week, in chronological order, for the site's week
    selector. The "current" working folder is excluded -- it's a duplicate
    of whichever dated folder is most recent.
    """
    season_root = Path("data") / str(season)
    if not season_root.exists():
        return
    week_folders = sorted(p for p in season_root.iterdir() if p.is_dir() and DATE_FOLDER.match(p.name))
    weeks = []
    for i, folder in enumerate(week_folders, 1):
        standings_path = folder / "standings.json"
        if not standings_path.exists():
            continue
        data = read_json(standings_path)
        date = datetime.strptime(folder.name, "%Y-%m-%d")
        weeks.append({
            "week_number": i,
            "week_tag": folder.name,
            "label": f"Week {i} · {date.strftime('%b %d').replace(' 0', ' ')}",
            "computer_systems": data.get("computer_systems", []),
            "rows": data.get("rows", []),
        })
    if not weeks:
        return
    weeks[-1]["is_current"] = True
    season_data = {"season": season, "weeks": weeks}
    write_json(Path("data") / "season.json", season_data)
    with open("season_data.js", "w", encoding="utf-8") as f:
        f.write("const SEASON_DATA = " + json.dumps(season_data, indent=2) + ";\n")
    info(f"Updated season_data.js with {len(weeks)} week(s)")

def build_site(week_path: str = str(DATA_ROOT)):
    """Build the static site and create latest.json symlink."""
    
    # Create data directory for latest.json at root
    site_data_dir = Path("data")
    site_data_dir.mkdir(exist_ok=True)
    
    # Copy standings to data/latest.json
    standings_path = Path(week_path) / "standings.json"
    if standings_path.exists():
        latest_path = site_data_dir / "latest.json"
        shutil.copy2(standings_path, latest_path)
        info(f"Copied {standings_path} to {latest_path}")
        
        # Add build metadata
        data = read_json(latest_path)
        data["build_time"] = timestamp()
        data["source_week"] = week_path
        write_json(latest_path, data)

        # Keep the static site's embedded dataset in sync with standings.
        # app.js reads BCS_DATA directly, so updating latest.json alone is not enough.
        import json
        with open("bcs_data.js", "w", encoding="utf-8") as f:
            # NB: this must be a real newline ("\n"), not the two literal
            # characters "\" + "n" -- a doubled backslash here writes a bare
            # backslash into the .js file, which is a SyntaxError the moment
            # a browser tries to parse it (verified: it left BCS_DATA
            # permanently undefined and the whole site blank).
            f.write("const BCS_DATA = " + json.dumps(data, indent=2) + ";\n")
        info("Updated bcs_data.js")
        
    else:
        info(f"Warning: {standings_path} not found, skipping latest.json")
    
    # Generate social image if standings exist
    if standings_path.exists():
        from publish.social_image import main as gen_social
        gen_social()
        info("Generated social image: top25.png")

    build_season_history()

    info(f"Site build complete for {week_path}")

if __name__ == "__main__":
    import sys
    week_path = sys.argv[1] if len(sys.argv) > 1 else str(DATA_ROOT)
    build_site(week_path)


