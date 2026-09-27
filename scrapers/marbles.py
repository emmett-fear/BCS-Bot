import re, requests
from bs4 import BeautifulSoup
from core.config import WEEK_TAG, output_path
from core.io import write_json
from core.teams import canon
from core.log import info

URL="https://cfbmarblegame.com/"
OUT=output_path("marbles")
UA={"User-Agent":"BCS-Bot/2.0"}

def parse():
    r=requests.get(URL,headers=UA,timeout=30); r.raise_for_status()
    soup=BeautifulSoup(r.text,"lxml"); teams=[]
    for tr in soup.select("table tr"):
        cells=[c.get_text(" ",strip=True) for c in tr.find_all(["td","th"])]
        if len(cells)<3 or not re.fullmatch(r"\d+",cells[0]): continue
        # FCS entries are marked with * and are not part of the FBS composite.
        if "*" in cells[1]: continue
        teams.append({"rank":int(cells[0]),"team":canon(cells[1]),"marbles":float(cells[2].replace(",",""))})
    if len(teams)<130: raise RuntimeError(f"Marbles parse produced only {len(teams)} FBS teams")
    write_json(OUT,{"source":"college_football_marbles","week":WEEK_TAG,"url":URL,"teams":teams})
    info(f"Marbles: {len(teams)} FBS teams")

if __name__=="__main__": parse()
