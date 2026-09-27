import re, requests
from bs4 import BeautifulSoup
from core.config import WEEK_TAG, output_path
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon
from core.log import info

URL="https://sagarin.com/sports/cfsend.htm"
OUT=output_path("sagarin")
UA={"User-Agent":"BCS-Bot/2.0"}

def parse():
    r=requests.get(URL,headers=UA,timeout=30); r.raise_for_status()
    text=BeautifulSoup(r.text,"lxml").get_text("\n")
    teams=[]
    # Sagarin marks FBS teams as A and FCS as AA. Only take A rows.
    pat=r"^\s*(\d{1,3})\s+(.+?)\s+A\s+=\s+\d+\.\d+\s+\d+\s+\d+"
    for m in re.finditer(pat,text,re.M):
        teams.append({"rank":int(m.group(1)),"team":canon(m.group(2).strip())})
    teams=sorted({t["rank"]:t for t in teams}.values(),key=lambda x:x["rank"])
    if len(teams)<100: raise RuntimeError(f"Sagarin parse produced only {len(teams)} FBS teams")
    write_json(OUT,comp_payload("sagarin",WEEK_TAG,teams))
    info(f"Sagarin: {len(teams)} FBS teams")

if __name__=="__main__": parse()
