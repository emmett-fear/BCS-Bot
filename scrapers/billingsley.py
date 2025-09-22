import requests, re
from bs4 import BeautifulSoup
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon

URL = "https://cfrc.com/weekly-rankings/2025"
OUT = "data/2025/week05/billingsley.json"
WEEK_TAG = "2025-09-21"
UA = {"User-Agent":"bcs-sim (contact: you@example.com)"}

def parse():
    r = requests.get(URL, headers=UA, timeout=30); r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    teams = []
    # Prefer the table listing "Week ..." with Rank/Team; adapt to their markup
    rows = soup.select("table tr")
    for tr in rows:
        tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        if len(tds) < 3: continue
        if not tds[0].isdigit(): continue
        rank = int(tds[0])
        team = canon(tds[2] if tds[1].isdigit() else tds[1])
        teams.append({"rank": rank, "team": team})
    if not teams:
        # Some weeks are per-week subpages; add code to follow first "Week 5" link if present
        pass
    write_json(OUT, comp_payload("billingsley", WEEK_TAG, teams))

if __name__ == "__main__":
    parse()


