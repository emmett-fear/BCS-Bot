"""Blind résumé rating.

Deliberately excludes conference, polls, preseason priors, recruiting, betting
markets and margin of victory. Inputs are only current-season FBS game results
and site. The rating is an iterative opponent-strength model, not part of BCS+.
"""
from collections import defaultdict

HOME_WIN=1.00
ROAD_WIN=1.10
NEUTRAL_WIN=1.05
HOME_LOSS=0.90
ROAD_LOSS=1.00
NEUTRAL_LOSS=0.95

def rate(games, iterations=100, damping=.85):
    teams=set()
    for g in games: teams|={g["winner"],g["loser"]}
    if not teams:return {}
    rating={t:1.0 for t in teams}
    played=defaultdict(int)
    for g in games: played[g["winner"]]+=1; played[g["loser"]]+=1
    for _ in range(iterations):
        nxt={}
        for t in teams:
            value=0.0
            for g in games:
                if g["winner"]==t:
                    loc=g.get("winner_site","neutral")
                    mult={"home":HOME_WIN,"road":ROAD_WIN,"neutral":NEUTRAL_WIN}[loc]
                    value+=mult*(1.0+rating[g["loser"]])
                elif g["loser"]==t:
                    loc=g.get("loser_site","neutral")
                    mult={"home":HOME_LOSS,"road":ROAD_LOSS,"neutral":NEUTRAL_LOSS}[loc]
                    value+=mult*rating[g["winner"]]
            avg=value/max(played[t],1)
            nxt[t]=(1-damping)+damping*avg
        scale=sum(nxt.values())/len(nxt) or 1
        rating={t:v/scale for t,v in nxt.items()}
    ordered=sorted(rating.items(),key=lambda x:(x[1],x[0]),reverse=True)
    return {team:{"score":round(score,6),"rank":i} for i,(team,score) in enumerate(ordered,1)}
