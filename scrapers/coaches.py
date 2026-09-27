import math, re
import requests
from bs4 import BeautifulSoup
from core.io import write_json
from core.schema import poll_payload
from core.teams import canon
from core.log import info

URL = "https://sportsdata.usatoday.com/football/ncaaf/coaches-poll/2026-2027/2026-09-27"
OUT = "data/2026/current/coaches.json"
WEEK_TAG = "current"
UA = {"User-Agent": "BCS-Bot/2.0"}

def parse():
    r = requests.get(URL, headers=UA, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    teams = []
    for tr in soup.select("table tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
        if len(cells) < 5:
            continue
        rank_match = re.match(r"^(?:T)?(\d+)", cells[0])
        if not rank_match:
            continue
        try:
            points = int(cells[3].replace(",", ""))
            first = int(re.sub(r"\D", "", cells[4]) or "0")
        except ValueError:
            continue
        teams.append({"rank": int(rank_match.group(1)), "team": canon(cells[1]),
                      "points": points, "first_place": first})
    if len(teams) < 25:
        raise RuntimeError(f"Coaches parse produced {len(teams)} teams; refusing to publish")
    ballots = math.ceil(max(t["points"] for t in teams) / 25)
    write_json(OUT, poll_payload("coaches", WEEK_TAG, ballots, teams))
    info(f"Coaches: {len(teams)} teams, inferred {ballots} ballots")

if __name__ == "__main__":
    parse()
