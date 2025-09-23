import requests, re
from bs4 import BeautifulSoup
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon
from core.log import warn

URL = "https://www.colleyrankings.com/foot2025/rankings/rank04_main.html"
OUT = "data/2025/week05/colley.json"
WEEK_TAG = "2025-09-21"
UA = {"User-Agent":"bcs-sim (contact: you@example.com)"}

def parse():
    r = requests.get(URL, headers=UA, timeout=30); r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    teams = []
    # First column rank, second team; skip header row(s)
    for tr in soup.select("table tr"):
        tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        if len(tds) < 2: continue
        # Check if first column is a rank (number followed by period)
        rank_match = re.match(r"^(\d+)\.$", tds[0])
        if not rank_match: continue
        rank = int(rank_match.group(1))
        team = canon(tds[1].strip())
        teams.append({"rank": rank, "team": team})
    write_json(OUT, comp_payload("colley", WEEK_TAG, teams))

if __name__ == "__main__":
    parse()


