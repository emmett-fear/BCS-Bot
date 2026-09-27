import math, re
import requests
from bs4 import BeautifulSoup
from core.io import write_json
from core.schema import poll_payload
from core.teams import canon
from core.log import info

URL = "https://www.ncaa.com/rankings/football/fbs/associated-press"
OUT = "data/2026/current/ap.json"
WEEK_TAG = "current"
UA = {"User-Agent": "BCS-Bot/2.0"}

def parse():
    r = requests.get(URL, headers=UA, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    teams = []
    for tr in soup.select("table tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td","th"])]
        if len(cells) < 3:
            continue
        rank_match = re.match(r"^(?:T)?(\d+)$", cells[0])
        if not rank_match:
            continue
        points_idx = next((i for i, v in enumerate(cells[2:], 2) if re.fullmatch(r"[\d,]+", v)), None)
        if points_idx is None:
            continue
        school = cells[1]
        first_match = re.search(r"\((\d+)\)\s*$", school)
        first = int(first_match.group(1)) if first_match else 0
        team = canon(re.sub(r"\s*\(\d+\)\s*$", "", school))
        teams.append({"rank": int(rank_match.group(1)), "team": team,
                      "points": int(cells[points_idx].replace(",", "")), "first_place": first})
    if len(teams) < 25:
        raise RuntimeError(f"AP parse produced {len(teams)} teams; refusing to publish")
    ballots = math.ceil(max(t["points"] for t in teams) / 25)
    write_json(OUT, poll_payload("ap", WEEK_TAG, ballots, teams))
    info(f"AP: {len(teams)} teams, inferred {ballots} ballots")

if __name__ == "__main__":
    parse()
