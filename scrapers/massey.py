import re, requests
from bs4 import BeautifulSoup
from core.config import WEEK_TAG, output_path
from core.io import write_json
from core.schema import comp_payload
from core.teams import canon
from core.log import info, warn

URL="https://masseyratings.com/cf/ratings"
OUT=output_path("massey")
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}

def _unavailable(reason):
    write_json(OUT,comp_payload("massey",WEEK_TAG,[]))
    warn(f"Massey: {reason}, publishing no rows this run")

def parse():
    # masseyratings.com sits behind Cloudflare and returns a "Just a
    # moment..." JS challenge page to any non-browser request, including
    # this one with a browser-like User-Agent -- there's no header-only way
    # around it, and exactly what that block page looks like (status code,
    # exact wording) varies by which IP range the request comes from. Rather
    # than hard-fail the whole weekly run by trying to enumerate every shape
    # that block can take, treat ANY failure to fetch or parse a real ranking
    # from this one source as "not available this week": compute_bcs already
    # averages whichever computer systems are actually available.
    try:
        r=requests.get(URL,headers=UA,timeout=30)
        if r.status_code != 200:
            return _unavailable(f"got HTTP {r.status_code}")
        soup=BeautifulSoup(r.text,"lxml"); teams=[]
        for tr in soup.select("table tr"):
            cells=[c.get_text(" ",strip=True) for c in tr.find_all("td")]
            if len(cells)<4: continue
            # Rat column begins with the ordinal rank, e.g. "1 9.09".
            m=re.match(r"^(\d+)\s+",cells[3])
            if not m: continue
            name=re.sub(r"(?:FBS|NCAA D1)$","",cells[0]).strip()
            if name and name!="Correlation":
                teams.append({"rank":int(m.group(1)),"team":canon(name)})
    except requests.exceptions.RequestException as exc:
        return _unavailable(f"request failed ({exc})")

    if len(teams)<25:
        return _unavailable(f"parsed only {len(teams)} teams (likely a bot-protection page, not real ratings)")
    teams=sorted({t["rank"]:t for t in teams}.values(),key=lambda x:x["rank"])
    write_json(OUT,comp_payload("massey",WEEK_TAG,teams))
    info(f"Massey: {len(teams)} teams")

if __name__=="__main__": parse()
