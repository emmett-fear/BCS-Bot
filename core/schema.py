"""Uniform JSON shapes for poll and computer outputs."""

# Poll JSON shape:
# {"source":"ap","week":"2025-09-21","ballots":63,"teams":[{"rank":1,"team":"Ohio State","points":1629,"first_place":52}, ...]}
#
# Computer JSON shape:
# {"source":"colley","week":"2025-09-21","teams":[{"rank":1,"team":"LSU"}, ...]}

def poll_payload(source, week, ballots, teams):
    return {"source": source, "week": week, "ballots": ballots, "teams": teams}

def comp_payload(source, week, teams):
    return {"source": source, "week": week, "teams": teams}


