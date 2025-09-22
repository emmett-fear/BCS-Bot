import os, shutil
from pathlib import Path
from core.io import read_json, write_json, timestamp
from core.log import info

def build_site(week_path: str = "data/2025/week05"):
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
        
    else:
        info(f"Warning: {standings_path} not found, skipping latest.json")
    
    # Generate social image if standings exist
    if standings_path.exists():
        from publish.social_image import main as gen_social
        gen_social()
        info("Generated social image: top25.png")
    
    info(f"Site build complete for {week_path}")

if __name__ == "__main__":
    import sys
    week_path = sys.argv[1] if len(sys.argv) > 1 else "data/2025/week05"
    build_site(week_path)


