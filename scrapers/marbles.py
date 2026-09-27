import re
import requests
from bs4 import BeautifulSoup
from core.io import write_json
from core.teams import canon
from core.log import info, warn

URL = "https://collegefootballmarbles.com/"
OUT = "data/2025/week05/marbles.json"
WEEK_TAG = "2025-09-21"
UA = {"User-Agent": "bcs-sim (College Football Marbles integration)"}

def _number(text):
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)", text.replace(",", ""))
    return float(m.group(1)) if m else None

def parse():
    r = requests.get(URL, headers=UA, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    teams = []

    # Prefer the site's rendered standings table. Identify columns by their
    # headers instead of fixed positions so harmless layout changes don't
    # silently attach marble totals to the wrong teams.
    for table in soup.find_all("table"):
        headers = [th.get_text(" ", strip=True).lower() for th in table.find_all("th")]
        if not headers:
            continue
        marble_idx = next((i for i, h in enumerate(headers) if "marble" in h), None)
        team_idx = next((i for i, h in enumerate(headers) if "team" in h or "school" in h), None)
        if marble_idx is None or team_idx is None:
            continue
        for tr in table.find_all("tr"):
            cells = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
            if max(marble_idx, team_idx) >= len(cells):
                continue
            value = _number(cells[marble_idx])
            team = canon(cells[team_idx])
            if team and value is not None:
                teams.append({"team": team, "marbles": value})
        if teams:
            break

    if not teams:
        raise RuntimeError("Could not locate a Team/Marbles standings table; refusing to publish zeroed BCS+ scores.")

    teams.sort(key=lambda t: t["marbles"], reverse=True)
    for i, team in enumerate(teams, 1):
        team["rank"] = i

    write_json(OUT, {"source": "college_football_marbles", "week": WEEK_TAG, "url": URL, "teams": teams})
    info(f"Marbles: scraped {len(teams)} teams")

if __name__ == "__main__":
    parse()
