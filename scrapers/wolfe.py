import re
import requests
from bs4 import BeautifulSoup
from core.config import WEEK_TAG, output_path
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon
from core.log import info

URL="https://wolferatings.com/ratings.htm"
OUT=output_path("wolfe")
UA={"User-Agent":"BCS-Bot/2.0"}

def parse():
    r=requests.get(URL,headers=UA,timeout=30); r.raise_for_status()
    text=BeautifulSoup(r.text,"lxml").get_text(" ",strip=True)
    # The page's placeholder copy wraps mid-sentence in the source HTML
    # ("first ratings \nwill be posted"), so a plain substring match on
    # normalized whitespace is required or the placeholder is missed and
    # the parser below finds nothing.
    normalized = re.sub(r"\s+", " ", text).lower()
    if "first ratings will be posted" in normalized:
        write_json(OUT,comp_payload("wolfe",WEEK_TAG,[]))
        info("Wolfe: ratings not published yet")
        return
    soup=BeautifulSoup(r.text,"lxml"); teams=[]
    for tr in soup.select("table tr"):
        cells=[c.get_text(" ",strip=True) for c in tr.find_all("td")]
        if len(cells)>=2 and cells[0].isdigit():
            teams.append({"rank":int(cells[0]),"team":canon(cells[1])})
    if len(teams)<25: raise RuntimeError(f"Wolfe page is live but parser found {len(teams)} teams")
    write_json(OUT,comp_payload("wolfe",WEEK_TAG,teams))
    info(f"Wolfe: {len(teams)} teams")

if __name__=="__main__": parse()
