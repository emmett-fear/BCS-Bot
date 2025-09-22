import subprocess, sys

SCRIPTS = [
  "ap.py","coaches.py",
  "colley.py","massey.py","billingsley.py",
  "anderson_hester.py","sagarin.py","wolfe.py"
]

for s in SCRIPTS:
    print(f"==> {s}")
    rc = subprocess.call([sys.executable, f"scrapers/{s}"])
    if rc != 0:
        print(f"[WARN] {s} exited with {rc} (continuing)")


