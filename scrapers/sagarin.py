import requests, re
from bs4 import BeautifulSoup
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon

URLS = [
  "https://sagarin.usatoday.com/",               # directory page to find the current season link
  "https://sagarin.com/sports/cfsend.htm"        # legacy ratings page
]
OUT = "data/2025/week05/sagarin.json"
WEEK_TAG = "2025-09-21"
UA = {"User-Agent":"bcs-sim (contact: you@example.com)"}

def parse_page(url):
    r = requests.get(url, headers=UA, timeout=30); r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    teams = []
    # Try a generic table parse; otherwise, look for lines like "  1  Ohio State  "
    for tr in soup.select("table tr"):
        tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        if len(tds) < 2: continue
        if not re.fullmatch(r"\d+", tds[0]): continue
        rank = int(tds[0]); team = canon(tds[1])
        teams.append({"rank": rank, "team": team})
    if not teams:
        text = soup.get_text("\n", strip=True)
        for m in re.finditer(r"^\s*(\d{1,3})\s+([A-Za-z .&'()-]+)\s*$", text, re.M):
            rank = int(m.group(1)); team = canon(m.group(2))
            teams.append({"rank": rank, "team": team})
    return teams

def parse():
    for u in URLS:
        teams = parse_page(u)
        if teams:
            write_json(OUT, comp_payload("sagarin", WEEK_TAG, teams))
            return
    # if both formats fail:
    write_json(OUT, comp_payload("sagarin", WEEK_TAG, []))

if __name__ == "__main__":
    parse()


