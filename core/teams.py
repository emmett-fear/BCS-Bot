"""Canonical team name helpers."""

ALIAS = {
  "Miami (FL)": "Miami",
  "Miami (Fla.)": "Miami",
  "Texas-San Antonio": "UTSA",
  "Texas A&M": "Texas A&M",
  "Mississippi": "Ole Miss",
  "Southern California": "USC",
  "Central Florida": "UCF",
  "Brigham Young": "BYU",
  "Louisiana State": "LSU",
  "Pittsburgh": "Pitt",
  "Texas Christian": "TCU",
  # add as you encounter variants...
}

def canon(name: str) -> str:
    n = name.strip()
    return ALIAS.get(n, n)


