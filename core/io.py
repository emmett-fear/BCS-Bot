import json, os, time
from pathlib import Path
from core.log import info

def ensure_dir(p: str):
    Path(p).mkdir(parents=True, exist_ok=True)

def write_json(path: str, payload: dict):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def timestamp():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


