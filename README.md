# BCS+

BCS+ is a modern BCS-style college football ranking, styled like the era the actual BCS came from.

**BCS+ = 25% AP + 25% Coaches + 25% classic BCS computer composite + 25% College Football Marbles.**

The project also preserves a **Classic BCS** comparison using one-third AP, one-third Coaches, and one-third computers, unchanged from the original formula (AP standing in for the retired Harris Poll).

The site (`index.html`) carries a season archive: every week computed so far is browsable from a week picker, not just whatever is "current."

## Components

- **AP Poll** — scraped live from ncaa.com; normalized from real poll points.
- **Coaches Poll** — scraped live from USA Today; normalized from real poll points.
- **Computers** — Anderson & Hester, Billingsley, Colley, Massey, Sagarin, and Wolfe. When all six publish, the highest and lowest scores are dropped and the remaining four are averaged; early in the season, whichever systems have actually published are averaged instead.
- **Marbles** — official College Football Marbles holdings, normalized proportionally to the current marble leader. This preserves the size of the gap between teams rather than reducing Marbles to ordinal rank.

If Marbles data is missing for a team, the bot leaves BCS+ blank for that team rather than silently treating missing data as zero. The same is true for the whole week: before Marbles data exists, BCS+ is blank and the site falls back to sorting by Classic BCS.

### Source availability, honestly

Not every source is reachable or exists every week, and this project would rather show nothing than a fabricated number:

- **Massey** sits behind a Cloudflare bot challenge that blocks plain HTTP scraping. It's marked optional; when blocked, the composite is computed from whichever computer systems *are* reachable that week.
- **Anderson & Hester** doesn't publish until after week 12 most seasons; before then, its page shows the *prior* season's final rankings, and the scraper explicitly checks for the current season's tag before accepting any rows, rather than ingesting last year's data as if it were this year's.
- **Wolfe** doesn't publish until mid-October most seasons; its "not posted yet" placeholder page is detected and treated as an empty result, not an error.
- **Sagarin** is reachable but has served a long-expired self-signed TLS certificate for years; the scraper deliberately skips verification for that one host.
- Historical weeks (see below) can only include sources that actually expose a past-week archive: Colley and Billingsley do; AP and Coaches don't (reconstructed from Wikipedia instead, see below); Marbles, Sagarin, Massey, Anderson & Hester, and Wolfe don't, so BCS+ is only ever computed from the week Marbles data starts existing onward.

## Run (this week)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python scrapers/run_all.py
PYTHONPATH=. python core/validate_sources.py
python -m core.compute_bcs
PYTHONPATH=. python publish/site_builder.py
```

`PYTHONPATH=.` is required for any script invoked directly (`python scrapers/x.py`, not `python -m ...`) so that `from core...` imports resolve — scripts run this way only get their own directory on `sys.path`, not the repo root. The GitHub Actions workflow sets this once at the job level.

## Backfilling past weeks

`scripts/backfill_season.py` fills in every week of the season so far, so the site's history isn't just whatever week happened to be current when it was last run:

```bash
PYTHONPATH=. python scripts/backfill_season.py         # every past week
PYTHONPATH=. python scripts/backfill_season.py 1 2 3    # specific weeks
```

It reconstructs AP and Coaches from Wikipedia's season-long rankings table (`scrapers/wiki_polls.py`) — ncaa.com and USA Today only ever show the *current* poll, with no date- or week-indexed archive to scrape for a past week — and scrapes Colley's and Billingsley's own dated per-week archives for real computer-ranking data. It does not invent historical Marbles, Sagarin, Massey, Anderson & Hester, or Wolfe data; none of those sources expose one.

Because Wikipedia's table gives rank order but not real vote-point totals for past weeks, backfilled AP/Coaches polls use the same inverse-rank scale as the computer rankings ((26 − rank) / 25) rather than actual ballot points, and are tagged `"reconstructed": true` in their JSON so they're never confused with a live scrape.

Add a new week's date to `WEEK_DATES` in that script once the season moves past week 4.

## Structure

- `scrapers/` — poll, computer, and Marbles ingestion (plus `wiki_polls.py`, used only for historical backfill)
- `scripts/backfill_season.py` — fills in past weeks of the current season
- `core/` — normalization, team aliases, and ranking computation
- `publish/` — static-site and social-image generation, including the season archive (`season_data.js`)
- `data/<season>/<week-tag>/` — one dated snapshot per week (`ap.json`, `coaches.json`, `marbles.json`, each computer system, `standings.json`); `data/<season>/current/` is the in-progress working copy for whichever week is running right now
- `.github/workflows/weekly.yml` — scheduled refresh; resolves the date and AP-poll week number itself each run, so no per-week hand-editing is needed

## Data integrity

The ranking should fail visibly when a required source changes shape rather than publish a plausible-looking zero. Team names are canonicalized before sources are joined — `core/teams.py` keeps both a hand-maintained alias table for known source-specific spellings/suffixes and `match_school()`, which resolves labels that bundle a mascot name into the cell (USA Today's Coaches Poll page renders "Texas Longhorns Tex" as one string) against the known FBS team list, longest match wins.

## Disclaimer

Independent simulation for analysis and entertainment. Not affiliated with the BCS, AP, USA TODAY, any computer ranking provider, or College Football Marbles.

## Blind résumé model

`core/resume.py` contains a separate experimental résumé rating. It is intentionally not an input to BCS+.

Allowed inputs: current-season FBS wins/losses, recursive opponent strength, and game site. Road wins receive a modest boost and home losses a modest penalty. Neutral games are neutral.

Explicitly excluded: conference identity, AP/Coaches/CFP rankings, preseason priors, previous seasons, recruiting, betting markets, FPI/SP+, and margin of victory.

The model remains experimental until a trustworthy current-season game-results feed is added and historical backtests are completed.
