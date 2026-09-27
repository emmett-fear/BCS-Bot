import re, requests
from bs4 import BeautifulSoup
from core.config import SEASON, WEEK_TAG, output_path
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon
from core.log import info

URL = f"https://cfrc.com/weekly-rankings/{SEASON}/5"
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
