BCS Bot
=======

Minimal scaffold for scraping polls/ratings and producing weekly outputs.

Setup
-----

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Structure
---------

- `data/` weekly snapshots
- `scrapers/` individual scrapers and `run_all.py`
- `core/` computation, IO, logging
- `publish/` site builder, social image
- `site/` static site assets

Run
---

```bash
python -m scrapers.run_all
```


