import subprocess, sys

SCRIPTS=[
 "ap.py","coaches.py","marbles.py",
 "colley.py","massey.py","billingsley.py",
 "anderson_hester.py","sagarin.py","wolfe.py"
]

failed=[]
for s in SCRIPTS:
    print(f"==> {s}",flush=True)
    rc=subprocess.call([sys.executable,f"scrapers/{s}"])
    if rc!=0:
        failed.append(s)
        print(f"[ERROR] {s} exited with {rc}",flush=True)

if failed:
    raise SystemExit("Scraper failures: "+", ".join(failed))
