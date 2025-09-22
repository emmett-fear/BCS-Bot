import requests
from bs4 import BeautifulSoup
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon

URL = "https://wolferatings.com/ratings.htm"
OUT = "data/2025/week05/wolfe.json"
WEEK_TAG = "2025-09-21"
UA = {"User-Agent":"bcs-sim (contact: you@example.com)"}

def parse():
    r = requests.get(URL, headers=UA, timeout=30); r.raise_for_status()
    # If page says "first ratings will be posted on October 12, 2025", return empty.
    if "first ratings will be posted on October 12, 2025" in r.text:
        write_json(OUT, comp_payload("wolfe", WEEK_TAG, []))
        return
    # Otherwise parse table similarly (rank, team)
    soup = BeautifulSoup(r.text, "lxml")
    teams = []
    for tr in soup.select("table tr"):
        tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        if len(tds) >= 2 and tds[0].isdigit():
            teams.append({"rank": int(tds[0]), "team": canon(tds[1])})
    write_json(OUT, comp_payload("wolfe", WEEK_TAG, teams))

if __name__ == "__main__":
    parse()


