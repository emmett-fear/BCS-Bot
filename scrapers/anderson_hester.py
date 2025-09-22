import requests, re
from bs4 import BeautifulSoup
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon

URL = "https://www.andersonsports.com/football/acf_frnk.html"
OUT = "data/2025/week05/anderson_hester.json"
WEEK_TAG = "2025-09-21"
UA = {"User-Agent":"bcs-sim (contact: you@example.com)"}

def parse():
    r = requests.get(URL, headers=UA, timeout=30); r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    teams = []
    for tr in soup.select("table tr"):
        tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        if len(tds) < 2: continue
        if not re.fullmatch(r"\d+", tds[0]): continue
        rank = int(tds[0])
        team = canon(tds[1])
        teams.append({"rank": rank, "team": team})
    write_json(OUT, comp_payload("anderson_hester", WEEK_TAG, teams))

if __name__ == "__main__":
    parse()


