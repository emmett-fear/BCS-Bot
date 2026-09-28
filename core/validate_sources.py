import json
from pathlib import Path
from core.config import DATA_ROOT

RULES={
 "ap":25,"coaches":25,"marbles":130,
 "billingsley":25,"colley":100,"sagarin":100,
}
# anderson_hester and wolfe legitimately publish nothing before mid-season.
# massey is a legitimate computer system, but masseyratings.com sits behind a
# Cloudflare JS challenge that blocks plain HTTP scraping outright some weeks;
# when it does, compute_bcs falls back to the computer systems that are
# actually reachable rather than failing the whole run over one blocked host.
OPTIONAL={"anderson_hester","wolfe","massey"}

def load(name):
    p=DATA_ROOT/f"{name}.json"
    if not p.exists(): return None
    return json.loads(p.read_text())

def main():
    failures=[]; status={}
    for name,min_count in RULES.items():
        payload=load(name); count=len(payload.get("teams",[])) if payload else 0
        status[name]=count
        if count<min_count: failures.append(f"{name}: {count} < {min_count}")
    for name in OPTIONAL:
        payload=load(name); status[name]=len(payload.get("teams",[])) if payload else 0
    print("SOURCE HEALTH")
    for name,count in status.items(): print(f"{name:18} {count:3}")
    if failures: raise SystemExit("Invalid required sources: "+"; ".join(failures))

if __name__=="__main__": main()
