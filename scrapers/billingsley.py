import requests, re
from bs4 import BeautifulSoup
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon

URL = "https://cfrc.com/weekly-rankings/2025/5"
OUT = "data/2025/week05/billingsley.json"
WEEK_TAG = "2025-09-21"
UA = {"User-Agent":"bcs-sim (contact: you@example.com)"}

def parse():
    r = requests.get(URL, headers=UA, timeout=30); r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    teams = []
    
    # Look for the rankings table
    rows = soup.select("table tr")
    for tr in rows:
        tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        if len(tds) < 4: continue
        
        # Skip empty rows
        if not tds[0]:
            continue
            
        # Check if this row has a rank (3rd column should be numeric)
        try:
            rank = int(tds[2])
            # Team name is in the 4th column (index 3)
            team_name = tds[3].strip()
            if team_name:
                teams.append({"rank": rank, "team": canon(team_name)})
        except (ValueError, IndexError):
            continue
    
    write_json(OUT, comp_payload("billingsley", WEEK_TAG, teams))

if __name__ == "__main__":
    parse()


