import re, sys
import requests
from bs4 import BeautifulSoup
from core.io import write_json
from core.schema import poll_payload
from core.teams import canon
from core.log import info, warn

# Use the dated USA TODAY Sports data URL for the current week (points + firsts).  [oai_citation:6‡USA TODAY](https://sportsdata.usatoday.com/football/ncaaf/coaches-poll/2025-2026/2025-09-21?utm_source=chatgpt.com)
COACHES_URL = "https://sportsdata.usatoday.com/football/ncaaf/coaches-poll/2025-2026/2025-09-21"
OUT = "data/2025/week05/coaches.json"
WEEK_TAG = "2025-09-21"
UA = {"User-Agent": "bcs-sim (contact: you@example.com)"}

def parse():
    r = requests.get(COACHES_URL, headers=UA, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    teams = []
    ballots = 0

    rows = soup.select("table tr")
    for tr in rows[1:]:
        tds = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
        if len(tds) < 5: 
            continue
        # Pattern: Rank, Team, Record, Points, First-place votes, ...
        rank_txt, team_txt, record, points_txt, first_txt, *_ = tds
        
        try:
            rank = int(re.sub(r"[^\d]", "", rank_txt) or "0")
            points = int(points_txt)
            first = int(first_txt)
        except (ValueError, IndexError):
            continue
            
        ballots += first
        teams.append({
          "rank": rank,
          "team": canon(team_txt),
          "points": points,
          "first_place": first
        })

    if not teams:
        warn("Coaches: Could not parse any teams from USA TODAY page; verify URL/markup.")
        write_json(OUT, poll_payload("coaches", WEEK_TAG, 0, []))
        sys.exit(0)

    write_json(OUT, poll_payload("coaches", WEEK_TAG, ballots, teams))

if __name__ == "__main__":
    parse()


