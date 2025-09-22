import re, sys
import requests
from bs4 import BeautifulSoup
from core.io import write_json
from core.schema import poll_payload
from core.teams import canon
from core.log import info, warn

# CONFIG: pick the current week landing page that shows the AP table.
AP_WEEK_URL = "https://www.ncaa.com/news/football/article/2025-09-21/college-football-scores-top-25-rankings-schedule-scores-week-5"  # example week page showing AP table.  [oai_citation:5‡NCAA.com](https://www.ncaa.com/news/football/article/2025-09-21/college-football-scores-top-25-rankings-schedule-scores-week-5?utm_source=chatgpt.com)
OUT = "data/2025/week05/ap.json"
WEEK_TAG = "2025-09-21"

UA = {"User-Agent": "bcs-sim (contact: you@example.com)"}

def parse():
    r = requests.get(AP_WEEK_URL, headers=UA, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    # Look for the AP table with columns: Rank, School, (First-place in parens), Points
    # NCAA article prints lines like:
    # 1 Ohio State (52) 1629 ...
    # We'll parse a table or a list; fallback to regex over page text for robustness.
    teams = []
    ballots = 0

    # 1) Try structured table rows first:
    rows = soup.select("table tr")
    if rows and len(rows) > 5:
        for tr in rows[1:]:
            cols = [c.get_text(" ", strip=True) for c in tr.find_all(["td","th"])]
            if len(cols) < 3: 
                continue
            # Typical format: rank, school (maybe with (##) ), points ...
            rank_txt, school_txt, *rest = cols
            pts_txt = None
            # find points among rest (numbers like 1629)
            for x in rest:
                if re.fullmatch(r"\d{2,4}", x):
                    pts_txt = x
                    break
            if not pts_txt:
                continue
            m = re.search(r"\((\d{1,3})\)", school_txt)
            first = int(m.group(1)) if m else 0
            ballots += first
            rank = int(re.sub(r"[^\d]", "", rank_txt) or "0")
            team = canon(re.sub(r"\s*\(\d+\)\s*", "", school_txt).strip())
            points = int(pts_txt)
            teams.append({"rank": rank, "team": team, "points": points, "first_place": first})

    # 2) Fallback: regex scan of article text lines (covers changes in HTML shape)
    if not teams:
        text = soup.get_text("\n", strip=True)
        for m in re.finditer(r"^\s*(\d+)\s+([A-Za-z .&()'-]+)\s+\((\d{1,3})\)\s+(\d{3,4})\s*$", text, flags=re.M):
            rank = int(m.group(1))
            team = canon(re.sub(r"\s*\(\d+\)\s*", "", m.group(2)).strip())
            first = int(m.group(3))
            points = int(m.group(4))
            ballots += first
            teams.append({"rank": rank, "team": team, "points": points, "first_place": first})

    if not teams:
        warn("AP: Could not parse any teams. Check AP_WEEK_URL or selectors.")
        # fail gracefully with empty file to not break pipeline
        write_json(OUT, poll_payload("ap", WEEK_TAG, 0, []))
        sys.exit(0)

    write_json(OUT, poll_payload("ap", WEEK_TAG, ballots, teams))

if __name__ == "__main__":
    parse()


