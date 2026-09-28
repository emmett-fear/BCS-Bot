import re, requests
from bs4 import BeautifulSoup
from core.config import SEASON, WEEK_TAG, WEEK_NUMBER, output_path
import os
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon
from core.log import info

# CFRC's own week index runs one ahead of the AP poll's (their "Week 5" page
# reflects the same 4-games-played state as the AP's "Week 4" poll — verified
# by comparing win totals across both pages for the same date). Allow an
# explicit override for the rare week this drifts, but default to the offset.
BILLINGSLEY_WEEK = int(os.getenv("BCS_BILLINGSLEY_WEEK", str(WEEK_NUMBER + 1)))
URL = f"https://cfrc.com/weekly-rankings/{SEASON}/{BILLINGSLEY_WEEK}"
OUT = output_path("billingsley")
UA = {"User-Agent":"BCS-Bot/2.0"}

def parse():
    r=requests.get(URL,headers=UA,timeout=30); r.raise_for_status()
    soup=BeautifulSoup(r.text,"lxml"); teams=[]
    for tr in soup.select("table tr"):
        cells=[td.get_text(" ",strip=True) for td in tr.find_all("td")]
        # Current CFRC columns: Season, Week, Rank, Team, ...
        if len(cells)<4 or not cells[2].isdigit(): continue
        teams.append({"rank":int(cells[2]),"team":canon(cells[3])})
    if len(teams)<25: raise RuntimeError(f"Billingsley parse produced {len(teams)} teams")
    write_json(OUT,comp_payload("billingsley",WEEK_TAG,teams))
    info(f"Billingsley: {len(teams)} teams from {URL}")

if __name__=="__main__": parse()
