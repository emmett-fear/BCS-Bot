import math, os, json
from statistics import mean
from core.io import read_json, write_json
from core.teams import canon
from core.log import info, warn

ROOT = "data/2025/week05"
OUT  = "data/2025/week05/standings.json"

def poll_pct(points, ballots):
    # ballots * 25 is the maximum possible points for that week
    return (points / float(ballots * 25)) if ballots and points is not None and points > 0 else 0.0

def comp_points(rank):
    # BCS inverse scale for Top-25 only; unranked = 0
    return (26 - rank)/25.0 if rank and (1 <= rank <= 25) else 0.0

def drop_high_low(vals):
    # In BCS, with all six computer systems, drop max & min and average remaining 4.
    # Only drop high/low when we have all 6 systems available.
    # Until then, use all available computer rankings.
    if len(vals) < 6:
        return mean(vals) if vals else 0.0
    vals = sorted(vals)
    return mean(vals[1:-1])

def load_poll(name):
    try:
        return read_json(os.path.join(ROOT, f"{name}.json"))
    except FileNotFoundError:
        return {"ballots": 0, "teams": []}

def load_comp(name):
    try:
        return read_json(os.path.join(ROOT, f"{name}.json"))
    except FileNotFoundError:
        return {"teams": []}

def main():
    ap = load_poll("ap")
    co = load_poll("coaches")

    # Build poll percentages
    ap_pct = { canon(t["team"]): poll_pct(t.get("points"), ap.get("ballots", 0)) for t in ap.get("teams",[]) }
    co_pct = { canon(t["team"]): poll_pct(t.get("points"), co.get("ballots", 0)) for t in co.get("teams",[]) }

    # Load computers into per-team dict of system->inverse points
    all_systems = ["sagarin","anderson_hester","billingsley","colley","massey","wolfe"]
    comp_map = {}
    comp_used_count = { k:0 for k in all_systems }
    available_systems = []

    for sysname in all_systems:
        payload = load_comp(sysname)
        if payload.get("teams"):  # Only include systems that have data
            available_systems.append(sysname)
            for t in payload.get("teams", []):
                team = canon(t["team"])
                cp = comp_points(t.get("rank"))
                comp_map.setdefault(team, {})[sysname] = cp
                comp_used_count[sysname] += 1

    # Compute computer score with drop-high/low (if 6 present)
    rows = []
    teams = set(ap_pct) | set(co_pct) | set(comp_map)
    for team in teams:
        vals = [comp_map.get(team,{}).get(s) for s in available_systems]
        vals = [v for v in vals if isinstance(v, float)]
        comp_score = drop_high_low(vals) if vals else 0.0

        score = (ap_pct.get(team,0.0) + co_pct.get(team,0.0) + comp_score) / 3.0
        rows.append({
          "team": team,
          "bcs_score": round(score, 6),
          "computers": round(comp_score, 6),
          "ap_pct": round(ap_pct.get(team,0.0), 6),
          "coaches_pct": round(co_pct.get(team,0.0), 6),
          "comp_inputs_used": len(vals)
        })

    rows.sort(key=lambda r: (r["bcs_score"], r["computers"], r["ap_pct"], r["coaches_pct"], r["team"]), reverse=True)
    for i,r in enumerate(rows, 1): r["rank"] = i

    write_json(OUT, {"week":"2025-09-21","rows":rows})

if __name__ == "__main__":
    main()


