import re, requests
from bs4 import BeautifulSoup
from core.config import WEEK_TAG, output_path
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon
from core.log import info

URL="https://colleyrankings.com/"
OUT=output_path("colley")
UA={"User-Agent":"BCS-Bot/2.0"}

def parse():
    r=requests.get(URL,headers=UA,timeout=30); r.raise_for_status()
    soup=BeautifulSoup(r.text,"lxml")
    text=soup.get_text("\n",strip=True); teams=[]
    # Current homepage exposes the football ranking as numbered text/links.
    for line in text.splitlines():
        m=re.match(r"^\s*(\d+)\.\s+(.+?)\s*$",line)
        if m and 1<=int(m.group(1))<=200:
            teams.append({"rank":int(m.group(1)),"team":canon(m.group(2))})
    # If DOM text separates rank/team, parse linked team labels from the football block.
    if len(teams)<25:
        teams=[]
        for a in soup.find_all("a"):
            label=a.get_text(" ",strip=True)
            parent=a.parent.get_text(" ",strip=True) if a.parent else ""
            m=re.search(r"(\d+)\.\s*"+re.escape(label),parent)
            if m and label:
                rank=int(m.group(1))
                if rank<=200: teams.append({"rank":rank,"team":canon(label)})
    dedup={t["rank"]:t for t in teams}
    teams=[dedup[k] for k in sorted(dedup)]
    if len(teams)<25: raise RuntimeError(f"Colley parse produced {len(teams)} teams")
    write_json(OUT,comp_payload("colley",WEEK_TAG,teams))
    info(f"Colley: {len(teams)} teams")

if __name__=="__main__": parse()
