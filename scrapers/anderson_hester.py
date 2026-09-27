import re, requests
from bs4 import BeautifulSoup
from core.config import WEEK_TAG, output_path
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon
from core.log import info

URL="https://www.andersonsports.com/football/acf_frnk.html"
OUT=output_path("anderson_hester")
UA={"User-Agent":"BCS-Bot/2.0"}

def parse():
    r=requests.get(URL,headers=UA,timeout=45); r.raise_for_status()
    soup=BeautifulSoup(r.text,"lxml"); teams=[]
    for tr in soup.select("table tr"):
        cells=[c.get_text(" ",strip=True) for c in tr.find_all("td")]
        if len(cells)>=2 and re.fullmatch(r"\d+",cells[0]):
            teams.append({"rank":int(cells[0]),"team":canon(cells[1])})
    # A&H historically starts later. Empty early-season pages are legitimate,
    # but a nonempty malformed page must not silently enter the composite.
    if 0 < len(teams) < 25: raise RuntimeError(f"Anderson-Hester parse produced only {len(teams)} teams")
    write_json(OUT,comp_payload("anderson_hester",WEEK_TAG,teams))
    info(f"Anderson-Hester: {len(teams)} teams" if teams else "Anderson-Hester: no ratings published/parsed yet")

if __name__=="__main__": parse()
