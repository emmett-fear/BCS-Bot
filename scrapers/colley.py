import re, requests
from bs4 import BeautifulSoup
from core.config import WEEK_TAG, WEEK_NUMBER, output_path
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon
from core.log import info

# colleyrankings.com publishes a dated archive page per week (00 = preseason,
# 01, 02, ...) with the FULL ranking (100+ teams), unlike the homepage, which
# only ever shows the current week's top 25 mixed in with a basketball
# section. The dated page is both more complete and lets the same scraper
# backfill any past week of the season by week number.
URL=f"https://colleyrankings.com/foot2026/rankings/rank{WEEK_NUMBER:02d}_main.html"
OUT=output_path("colley")
UA={"User-Agent":"BCS-Bot/2.0"}

def parse():
    r=requests.get(URL,headers=UA,timeout=30); r.raise_for_status()
    soup=BeautifulSoup(r.text,"lxml"); teams=[]
    for tr in soup.select("table tr"):
        cells=[c.get_text(" ",strip=True) for c in tr.find_all("td")]
        if len(cells)<2: continue
        m=re.match(r"^(\d+)\.$",cells[0])
        if not m: continue
        # Below the individually-ranked teams, Colley lumps remaining FCS
        # opponents into aggregate placeholder rows ("FCS GROUP 1", "FCS
        # GROUP 2", ...) rather than real teams; they must not enter the
        # composite as if they were an FBS program.
        if cells[1].upper().startswith("FCS GROUP"): continue
        teams.append({"rank":int(m.group(1)),"team":canon(cells[1])})
    if len(teams)<25: raise RuntimeError(f"Colley parse produced {len(teams)} teams from {URL}")
    write_json(OUT,comp_payload("colley",WEEK_TAG,teams))
    info(f"Colley: {len(teams)} teams (week {WEEK_NUMBER}) from {URL}")

if __name__=="__main__": parse()
