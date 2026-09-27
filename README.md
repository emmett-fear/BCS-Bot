# BCS+

BCS+ is a modern BCS-style college football ranking.

**BCS+ = 25% AP + 25% Coaches + 25% classic BCS computer composite + 25% College Football Marbles.**

The project also preserves a **Classic BCS** comparison using one-third AP, one-third Coaches, and one-third computers.

## Components

- **AP Poll** — normalized from poll points.
- **Coaches Poll** — normalized from poll points.
- **Computers** — Anderson & Hester, Billingsley, Colley, Massey, Sagarin, and Wolfe. When all six publish, the highest and lowest scores are dropped and the remaining four are averaged.
- **Marbles** — official College Football Marbles holdings, normalized proportionally to the current marble leader. This preserves the size of the gap between teams rather than reducing Marbles to ordinal rank.

If Marbles data is missing for a team, the bot leaves BCS+ blank rather than silently treating missing data as zero.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scrapers/run_all.py
python -c "from core import compute_bcs; compute_bcs.main()"
python publish/site_builder.py
```

## Structure

- `scrapers/` — poll, computer, and Marbles ingestion
- `core/` — normalization, team aliases, and ranking computation
- `publish/` — static-site and social-image generation
- `data/` — weekly source snapshots and computed standings
- `.github/workflows/weekly.yml` — scheduled refresh

## Data integrity

The ranking should fail visibly when a required source changes shape rather than publish a plausible-looking zero. Team names are canonicalized before sources are joined.

The current scaffold still uses a fixed season/week path. Moving season/week configuration into one shared runtime setting is the next major infrastructure improvement.

## Disclaimer

Independent simulation for analysis and entertainment. Not affiliated with the BCS, AP, USA TODAY, any computer ranking provider, or College Football Marbles.


## Blind résumé model

`core/resume.py` contains a separate experimental résumé rating. It is intentionally not an input to BCS+.

Allowed inputs: current-season FBS wins/losses, recursive opponent strength, and game site. Road wins receive a modest boost and home losses a modest penalty. Neutral games are neutral.

Explicitly excluded: conference identity, AP/Coaches/CFP rankings, preseason priors, previous seasons, recruiting, betting markets, FPI/SP+, and margin of victory.

The model remains experimental until a trustworthy current-season game-results feed is added and historical backtests are completed.
