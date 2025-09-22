import sys

def info(msg):  print(f"[INFO] {msg}")
def warn(msg):  print(f"[WARN] {msg}", file=sys.stderr)
def error(msg): print(f"[ERROR] {msg}", file=sys.stderr)


