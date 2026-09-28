import re, requests
from bs4 import BeautifulSoup
from core.config import SEASON, WEEK_TAG, output_path
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon
from core.log import info

# andersonsports.com's HTTPS listener resets the connection on every request
# (broken TLS termination); plain HTTP on the same host serves the identical
# page and works fine.
URL="http://www.andersonsports.com/football/acf_frnk.html"
OUT=output_path("anderson_hester")
UA={"User-Agent":"BCS-Bot/2.0"}
SEASON_TAG=f"{SEASON}-{str(SEASON+1)[-2:]}"

def parse():
    r=requests.get(URL,headers=UA,timeout=45); r.raise_for_status()
    soup=BeautifulSoup(r.text,"lxml")
    page_text=soup.get_text(" ",strip=True)
    # A&H rankings first appear after week 12. Before then, the default page
    # keeps showing the PRIOR season's final rankings rather than a blank
    # page. Ingesting that would silently mix last season's results into this
    # season's composite, so only accept rows when the page actually
    # advertises the current season.
    if SEASON_TAG not in page_text:
        write_json(OUT,comp_payload("anderson_hester",WEEK_TAG,[]))
        info(f"Anderson-Hester: page still shows a prior season (no {SEASON_TAG} rankings yet)")
        return
    teams=[]
    for tr in soup.select("table tr"):
        cells=[c.get_text(" ",strip=True) for c in tr.find_all("td")]
        if len(cells)>=2:
            rank_match=re.fullmatch(r"(\d+)\.?",cells[0])
            if rank_match:
                teams.append({"rank":int(rank_match.group(1)),"team":canon(cells[1])})
    if len(teams)<25: raise RuntimeError(f"Anderson-Hester page advertises {SEASON_TAG} but parser found only {len(teams)} teams")
    write_json(OUT,comp_payload("anderson_hester",WEEK_TAG,teams))
    info(f"Anderson-Hester: {len(teams)} teams")

if __name__=="__main__": parse()
