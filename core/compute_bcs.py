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

    # Build poll percentages and ranks
    ap_pct = { canon(t["team"]): poll_pct(t.get("points"), ap.get("ballots", 0)) for t in ap.get("teams",[]) }
    co_pct = { canon(t["team"]): poll_pct(t.get("points"), co.get("ballots", 0)) for t in co.get("teams",[]) }
    ap_rank = { canon(t["team"]): t.get("rank") for t in ap.get("teams",[]) }
    co_rank = { canon(t["team"]): t.get("rank") for t in co.get("teams",[]) }

    # Load computers into per-team dict of system->inverse points and ranks
    all_systems = ["sagarin","anderson_hester","billingsley","colley","massey","wolfe"]
    comp_map = {}
    comp_ranks = {}
    comp_used_count = { k:0 for k in all_systems }
    available_systems = []

    for sysname in all_systems:
        payload = load_comp(sysname)
        if payload.get("teams"):  # Only include systems that have data
            available_systems.append(sysname)
            for t in payload.get("teams", []):
                team = canon(t["team"])
                rank = t.get("rank")
                cp = comp_points(rank)
                comp_map.setdefault(team, {})[sysname] = cp
                comp_ranks.setdefault(team, {})[sysname] = rank
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
          "comp_inputs_used": len(vals),
          "ap_rank": ap_rank.get(team),
          "coaches_rank": co_rank.get(team)
        })

    rows.sort(key=lambda r: (r["bcs_score"], r["computers"], r["ap_pct"], r["coaches_pct"], r["team"]), reverse=True)
    for i,r in enumerate(rows, 1): r["rank"] = i

    # Calculate computer ranks based on computer scores with tie handling
    comp_scores = [(i, r["computers"]) for i, r in enumerate(rows)]
    comp_scores.sort(key=lambda x: x[1], reverse=True)
    
    comp_ranks = {}
    current_rank = 1
    i = 0
    while i < len(comp_scores):
        score = comp_scores[i][1]
        tied_indices = [j for j in range(i, len(comp_scores)) if comp_scores[j][1] == score]
        
        if len(tied_indices) == 1:
            comp_ranks[comp_scores[i][0]] = str(current_rank)
        else:
            # All tied teams get the same rank with T prefix
            for idx in tied_indices:
                comp_ranks[comp_scores[idx][0]] = f"T{current_rank}"
        
        current_rank += len(tied_indices)
        i += len(tied_indices)
    
    # Add computer ranks to rows
    for i, r in enumerate(rows):
        r["comp_rank"] = comp_ranks.get(i, "—")

    write_json(OUT, {"week":"2025-09-21","rows":rows})

if __name__ == "__main__":
    main()


