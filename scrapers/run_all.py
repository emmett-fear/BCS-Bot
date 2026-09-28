import os, subprocess, sys
from pathlib import Path

SCRIPTS=[
 "ap.py","coaches.py","marbles.py",
 "colley.py","massey.py","billingsley.py",
 "anderson_hester.py","sagarin.py","wolfe.py"
]

ROOT = str(Path(__file__).resolve().parent.parent)

def _child_env():
    # Scrapers do `from core...` assuming the repo root is importable.
    # Running them as plain scripts (python scrapers/x.py) only puts
    # scrapers/ on sys.path, not the repo root, so `core` fails to import
    # unless we hand the child process a PYTHONPATH that includes ROOT.
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = ROOT if not existing else (ROOT + os.pathsep + existing)
    return env

failed=[]
for s in SCRIPTS:
    print(f"==> {s}",flush=True)
    rc=subprocess.call([sys.executable,f"scrapers/{s}"], cwd=ROOT, env=_child_env())
    if rc!=0:
        failed.append(s)
        print(f"[ERROR] {s} exited with {rc}",flush=True)

if failed:
    raise SystemExit("Scraper failures: "+", ".join(failed))
