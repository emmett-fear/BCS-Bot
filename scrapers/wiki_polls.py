"""Reconstruct a past week's AP and Coaches polls from Wikipedia.

ncaa.com and USA Today only ever show the CURRENT week's poll — there is no
public date- or week-indexed archive to scrape for a past week (verified by
probing both sites' URL patterns; see project notes). Wikipedia's season
rankings article, by contrast, keeps a season-long table with one column per
week, so it is the only practical source for backfilling AP/Coaches history.

The table's rows are RANKS, not teams: row 1 shows whichever team held #1
each week, row 2 whichever team held #2, and so on, with each cell reading
"Team (W-L) (first-place votes)". That gives an accurate rank order for any
past week, but not the underlying vote-point totals (those were never
published anywhere that archives them). So historical weeks built from this
source use the same inverse-rank scale as the computer rankings
((26-rank)/25) rather than real ballot points, and the output is flagged
with "reconstructed": true so it's never confused with a live scrape.

This is deliberately a separate script from scrapers/ap.py and
scrapers/coaches.py, which keep scraping real point totals for the current
week. Only scripts/backfill_season.py calls this one.
"""
import re
import requests
from bs4 import BeautifulSoup
from core.config import SEASON, WEEK_TAG, WEEK_NUMBER, output_path
from core.io import write_json
from core.schema import poll_payload
from core.teams import canon
from core.log import info

URL = f"https://en.wikipedia.org/wiki/{SEASON}_NCAA_Division_I_FBS_football_rankings"
UA = {"User-Agent": "BCS-Bot/2.0"}

# Matches "<Team> (W-L)" within a cell, non-greedy so a parenthesized team
# name like "Miami (FL)" stays part of the name rather than getting cut at
# its own parenthesis. Used with finditer (not fullmatch) because a cell can
# hold more than one team when two teams tied for that rank -- Wikipedia
# renders a tie as both teams' "Team (W-L)" back to back in the same cell,
# separated by a footnote glyph rather than a delimiter we can split on.
TEAM_RECORD = re.compile(r"([A-Za-z][A-Za-z0-9&'.() \-]*?)\s*\((\d+)[–‒-](\d+)\)")

def _extract(soup, section_id, week_number):
    header = soup.find(id=section_id)
    if header is None:
        raise RuntimeError(f"wiki_polls: could not find section {section_id!r} on {URL}")
    table = header.find_next("table")
    rows = table.find_all("tr")
    col = week_number + 1  # 0=rank label, 1=preseason, 2=week1, 3=week2, ...
    teams = []
    for tr in rows[1:26]:
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
        rank_match = re.match(r"^(\d+)\.$", cells[0]) if cells else None
        if not rank_match or col >= len(cells):
            continue
        cell = cells[col]
        if not cell:
            continue  # team hadn't cracked the poll yet that week
        rank = int(rank_match.group(1))
        names = [m.group(1).strip() for m in TEAM_RECORD.finditer(cell)]
        if not names:
            raise RuntimeError(f"wiki_polls: {section_id} week {week_number} rank {rank} cell {cell!r} didn't match the expected 'Team (W-L)' pattern")
        # Two or more names in one cell means a tie for that rank -- both (or
        # all) teams get the same rank, matching how the poll was actually
        # released, rather than silently keeping only the first.
        for name in names:
            teams.append({"rank": rank, "team": canon(name)})
    if len(teams) < 25:
        raise RuntimeError(f"wiki_polls: {section_id} week {week_number} produced only {len(teams)} teams")
    return teams

def parse():
    r = requests.get(URL, headers=UA, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    for section_id, source_name, out_name in (
        ("AP_poll", "ap", "ap"),
        ("Coaches_Poll", "coaches", "coaches"),
    ):
        ranked = _extract(soup, section_id, WEEK_NUMBER)
        teams = [
            {"rank": t["rank"], "team": t["team"], "points": 26 - t["rank"], "first_place": 0}
            for t in ranked
        ]
        payload = poll_payload(source_name, WEEK_TAG, ballots=1, teams=teams)
        payload["reconstructed"] = True
        payload["method"] = "wikipedia-rank-order (no historical point totals are publicly archived)"
        payload["source_url"] = URL
        write_json(output_path(out_name), payload)
        info(f"wiki_polls: {source_name} week {WEEK_NUMBER} reconstructed, {len(teams)} teams")

if __name__ == "__main__":
    parse()
