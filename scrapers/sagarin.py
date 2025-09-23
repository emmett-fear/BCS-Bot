import requests, re
from bs4 import BeautifulSoup
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon

URL = "http://sagarin.com/sports/cfsend.htm"
OUT = "data/2025/week05/sagarin.json"
WEEK_TAG = "2025-09-21"
UA = {"User-Agent":"bcs-sim (contact: you@example.com)"}

def parse():
    r = requests.get(URL, headers=UA, timeout=30); r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    teams = []
    
    # Look for the rankings in the text format
    text = soup.get_text("\n", strip=True)
    
    # Pattern to match lines like "1  Ohio State           A  =  93.31    3   0   0"
    # More precise pattern to avoid duplicates
    for m in re.finditer(r"^\s*(\d{1,3})\s+([A-Za-z .&'()-]+?)\s+[A-Z]\s*=\s*\d+\.\d+\s+\d+\s+\d+\s+\d+", text, re.M):
        rank = int(m.group(1))
        team_name = m.group(2).strip()
        if team_name and not team_name.startswith('RATING') and rank <= 25:
            teams.append({"rank": rank, "team": canon(team_name)})
    
    # Remove duplicates by rank (keep first occurrence)
    seen_ranks = set()
    unique_teams = []
    for team in teams:
        if team["rank"] not in seen_ranks:
            seen_ranks.add(team["rank"])
            unique_teams.append(team)
    
    write_json(OUT, comp_payload("sagarin", WEEK_TAG, unique_teams))

if __name__ == "__main__":
    parse()


