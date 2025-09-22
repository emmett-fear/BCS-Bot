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
        if len(tds) < 4: 
            continue
        # Common pattern: Rank, Team, Record, Points, (First-place), ...
        rank_txt, team_txt, *_ = tds
        # Try to find a "First-place votes" cell or a parens in team cell
        first = 0
        m = re.search(r"\((\d{1,3})\)", team_txt)
        if m:
            first = int(m.group(1))
            team_txt = re.sub(r"\(\d{1,3}\)", "", team_txt).strip()

        # points often in a specific column; find the biggest 3-4 digit int in row as points
        pts = None
        for cell in tds:
            pm = re.search(r"\b(\d{3,4})\b", cell)
            if pm:
                val = int(pm.group(1))
                if pts is None or val > pts:
                    pts = val

        if not pts:
            continue
        ballots += first
        teams.append({
          "rank": int(re.sub(r"[^\d]", "", rank_txt) or "0"),
          "team": canon(team_txt),
          "points": int(pts),
          "first_place": first
        })

    if not teams:
        warn("Coaches: Could not parse any teams from USA TODAY page; verify URL/markup.")
        write_json(OUT, poll_payload("coaches", WEEK_TAG, 0, []))
        sys.exit(0)

    write_json(OUT, poll_payload("coaches", WEEK_TAG, ballots, teams))

if __name__ == "__main__":
    parse()


