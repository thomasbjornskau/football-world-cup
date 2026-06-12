#!/usr/bin/env python3
"""
Bygger datafiler for VM-prototypen.

Kanoniske data ligger i dette scriptet (Python-dicts), og skrives ut som:
  - data/worldcup-history.json  (rådata, kan brukes av andre verktøy)
  - data/team-analysis.json
  - data/worldcup-history.js    (samme innhold, pakket som window.WC_HISTORY)
  - data/team-analysis.js       (window.WC_ANALYSIS)

.js-speilene finnes fordi fetch() av lokale JSON-filer blokkeres på file://,
og siden skal kunne åpnes direkte fra disk. Rediger data her og kjør:

    python3 tools/build_data.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# stageLevel:
# 0 = Did not qualify / did not enter
# 1 = Group stage (incl. first round in early formats)
# 2 = Round of 16 (incl. 1934/1938 first knockout round, 1974-82 second group stage mapped case by case)
# 3 = Quarter-final (incl. second group stage 1974/1978/1982 when it meant top 8)
# 4 = Semi-final / 3rd / 4th place
# 5 = Final (runner-up)
# 6 = Champion

YEARS = [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 1978,
         1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026]

STAGE_LABELS = {
    0: "Did not qualify",
    1: "Group stage",
    2: "Round of 16",
    3: "Quarter-final",
    4: "Semi-final",
    5: "Final",
    6: "Champion",
}


def wc(year, level, stage=None, m=None, w=None, d=None, l=None, gf=None, ga=None,
       results=None, note=None):
    entry = {
        "year": year,
        "participated": level > 0,
        "stage": stage or STAGE_LABELS[level],
        "stageLevel": level,
    }
    if m is not None:
        entry.update({"matches": m, "wins": w, "draws": d, "losses": l,
                      "goalsFor": gf, "goalsAgainst": ga})
    if results is not None:
        entry["matchResults"] = results
    if note:
        entry["note"] = note
    return entry


def dnq(year, note=None):
    return wc(year, 0, note=note)


TEAMS = [
    {
        "id": "morocco", "name": "Morocco", "confederation": "CAF", "qualified2026": True,
        "worldCups": [
            dnq(1930, "Did not enter"), dnq(1934, "Did not enter"), dnq(1938, "Did not enter"),
            dnq(1950, "Did not enter"), dnq(1954, "Did not enter"), dnq(1958, "Did not enter"),
            dnq(1962), dnq(1966, "Withdrew"),
            wc(1970, 1, m=3, w=0, d=1, l=2, gf=2, ga=6, results=["L", "L", "D"]),
            dnq(1974), dnq(1978), dnq(1982),
            wc(1986, 2, m=4, w=1, d=2, l=1, gf=3, ga=2, results=["D", "D", "W", "L"],
               note="First African side to reach the knockout stage"),
            dnq(1990),
            wc(1994, 1, m=3, w=0, d=0, l=3, gf=2, ga=5, results=["L", "L", "L"]),
            wc(1998, 1, m=3, w=1, d=1, l=1, gf=5, ga=5, results=["D", "L", "W"]),
            dnq(2002), dnq(2006), dnq(2010), dnq(2014),
            wc(2018, 1, m=3, w=0, d=1, l=2, gf=2, ga=4, results=["L", "L", "D"]),
            wc(2022, 4, m=7, w=3, d=2, l=2, gf=6, ga=5,
               results=["D", "W", "W", "D", "W", "L", "L"],
               note="First African semi-finalist; finished fourth"),
            wc(2026, 1, stage="Qualified", note="Qualified for 2026"),
        ],
    },
    {
        "id": "argentina", "name": "Argentina", "confederation": "CONMEBOL", "qualified2026": True,
        "worldCups": [
            wc(1930, 5, m=5, w=4, d=0, l=1, gf=18, ga=9, results=["W", "W", "W", "W", "L"]),
            wc(1934, 2, stage="Round of 16", m=1, w=0, d=0, l=1, gf=2, ga=3, results=["L"],
               note="Straight knockout format"),
            dnq(1938, "Did not enter"), dnq(1950, "Did not enter"), dnq(1954, "Did not enter"),
            wc(1958, 1, m=3, w=1, d=0, l=2, gf=5, ga=10, results=["L", "W", "L"]),
            wc(1962, 1, m=3, w=1, d=1, l=1, gf=2, ga=3, results=["W", "L", "D"]),
            wc(1966, 3, m=4, w=2, d=1, l=1, gf=4, ga=2, results=["W", "D", "W", "L"]),
            dnq(1970),
            wc(1974, 3, stage="Second group stage", m=6, w=1, d=2, l=3, gf=9, ga=12,
               results=["L", "D", "W", "L", "L", "D"], note="Second group stage = last eight"),
            wc(1978, 6, m=7, w=5, d=1, l=1, gf=15, ga=4,
               results=["W", "W", "L", "W", "W", "D", "W"], note="Champions as hosts"),
            wc(1982, 3, stage="Second round", m=5, w=2, d=0, l=3, gf=8, ga=7,
               results=["L", "W", "W", "L", "L"], note="Second group stage = last twelve"),
            wc(1986, 6, m=7, w=6, d=1, l=0, gf=14, ga=5,
               results=["W", "D", "W", "W", "W", "W", "W"]),
            wc(1990, 5, m=7, w=2, d=3, l=2, gf=5, ga=4,
               results=["L", "W", "D", "W", "D", "D", "L"],
               note="Two knockout wins on penalties (counted as draws)"),
            wc(1994, 2, m=4, w=2, d=0, l=2, gf=8, ga=6, results=["W", "W", "L", "L"]),
            wc(1998, 3, m=5, w=3, d=1, l=1, gf=10, ga=4, results=["W", "W", "W", "D", "L"]),
            wc(2002, 1, m=3, w=1, d=1, l=1, gf=2, ga=2, results=["W", "L", "D"]),
            wc(2006, 3, m=5, w=3, d=2, l=0, gf=11, ga=3, results=["W", "W", "D", "W", "D"],
               note="Eliminated on penalties in the quarter-final"),
            wc(2010, 3, m=5, w=4, d=0, l=1, gf=10, ga=6, results=["W", "W", "W", "W", "L"]),
            wc(2014, 5, m=7, w=5, d=1, l=1, gf=8, ga=4,
               results=["W", "W", "W", "W", "W", "D", "L"]),
            wc(2018, 2, m=4, w=1, d=1, l=2, gf=6, ga=9, results=["D", "L", "W", "L"]),
            wc(2022, 6, m=7, w=4, d=2, l=1, gf=15, ga=8,
               results=["L", "W", "W", "W", "D", "W", "D"],
               note="Final and quarter-final won on penalties (counted as draws)"),
            wc(2026, 1, stage="Qualified", note="Qualified for 2026"),
        ],
    },
    {
        "id": "france", "name": "France", "confederation": "UEFA", "qualified2026": True,
        "worldCups": [
            wc(1930, 1, m=3, w=1, d=0, l=2, gf=4, ga=3, results=["W", "L", "L"]),
            wc(1934, 2, stage="Round of 16", m=1, w=0, d=0, l=1, gf=2, ga=3, results=["L"],
               note="Straight knockout format"),
            wc(1938, 3, m=2, w=1, d=0, l=1, gf=4, ga=4, results=["W", "L"]),
            dnq(1950, "Withdrew after qualifying"),
            wc(1954, 1, m=2, w=1, d=0, l=1, gf=3, ga=3, results=["L", "W"]),
            wc(1958, 4, stage="Semi-final", m=6, w=4, d=0, l=2, gf=23, ga=15,
               results=["W", "L", "W", "W", "L", "W"], note="Third place; Fontaine scored 13"),
            dnq(1962),
            wc(1966, 1, m=3, w=0, d=1, l=2, gf=2, ga=5, results=["D", "L", "L"]),
            dnq(1970), dnq(1974),
            wc(1978, 1, m=3, w=1, d=0, l=2, gf=5, ga=5, results=["L", "L", "W"]),
            wc(1982, 4, stage="Semi-final", m=7, w=3, d=2, l=2, gf=16, ga=12,
               results=["L", "W", "D", "W", "W", "D", "L"], note="Fourth place"),
            wc(1986, 4, stage="Semi-final", m=7, w=4, d=2, l=1, gf=12, ga=6,
               results=["W", "D", "W", "W", "D", "L", "W"], note="Third place"),
            dnq(1990), dnq(1994),
            wc(1998, 6, m=7, w=6, d=1, l=0, gf=15, ga=2,
               results=["W", "W", "W", "W", "D", "W", "W"], note="Champions as hosts"),
            wc(2002, 1, m=3, w=0, d=1, l=2, gf=0, ga=3, results=["L", "D", "L"]),
            wc(2006, 5, m=7, w=4, d=3, l=0, gf=9, ga=3,
               results=["D", "D", "W", "W", "W", "W", "D"],
               note="Lost the final on penalties (counted as a draw)"),
            wc(2010, 1, m=3, w=0, d=1, l=2, gf=1, ga=4, results=["D", "L", "L"]),
            wc(2014, 3, m=5, w=3, d=1, l=1, gf=10, ga=3, results=["W", "W", "D", "W", "L"]),
            wc(2018, 6, m=7, w=6, d=1, l=0, gf=14, ga=6,
               results=["W", "W", "D", "W", "W", "W", "W"]),
            wc(2022, 5, m=7, w=5, d=1, l=1, gf=16, ga=8,
               results=["W", "W", "L", "W", "W", "W", "D"],
               note="Lost the final on penalties (counted as a draw)"),
            wc(2026, 1, stage="Qualified", note="Qualified for 2026"),
        ],
    },
    {
        "id": "brazil", "name": "Brazil", "confederation": "CONMEBOL", "qualified2026": True,
        "worldCups": [
            wc(1930, 1, m=2, w=1, d=0, l=1, gf=5, ga=2, results=["L", "W"]),
            wc(1934, 2, stage="Round of 16", m=1, w=0, d=0, l=1, gf=1, ga=3, results=["L"],
               note="Straight knockout format"),
            wc(1938, 4, stage="Semi-final", m=5, w=3, d=1, l=1, gf=14, ga=11,
               results=["W", "D", "W", "L", "W"], note="Third place"),
            wc(1950, 5, m=6, w=4, d=1, l=1, gf=22, ga=6,
               results=["W", "D", "W", "W", "W", "L"],
               note="Final round-robin; decisive match lost to Uruguay"),
            wc(1954, 3, m=3, w=1, d=1, l=1, gf=8, ga=5, results=["W", "D", "L"]),
            wc(1958, 6, m=6, w=5, d=1, l=0, gf=16, ga=4,
               results=["W", "D", "W", "W", "W", "W"]),
            wc(1962, 6, m=6, w=5, d=1, l=0, gf=14, ga=5,
               results=["W", "D", "W", "W", "W", "W"]),
            wc(1966, 1, m=3, w=1, d=0, l=2, gf=4, ga=6, results=["W", "L", "L"]),
            wc(1970, 6, m=6, w=6, d=0, l=0, gf=19, ga=7,
               results=["W", "W", "W", "W", "W", "W"], note="Won every match"),
            wc(1974, 4, stage="Semi-final", m=7, w=3, d=2, l=2, gf=6, ga=4,
               results=["D", "D", "W", "W", "W", "L", "L"], note="Fourth place"),
            wc(1978, 4, stage="Semi-final", m=7, w=4, d=3, l=0, gf=10, ga=3,
               results=["D", "D", "W", "W", "D", "W", "W"],
               note="Third place, unbeaten"),
            wc(1982, 3, stage="Second round", m=5, w=4, d=0, l=1, gf=15, ga=6,
               results=["W", "W", "W", "W", "L"], note="Second group stage = last twelve"),
            wc(1986, 3, m=5, w=4, d=1, l=0, gf=10, ga=1, results=["W", "W", "W", "W", "D"],
               note="Eliminated on penalties in the quarter-final"),
            wc(1990, 2, m=4, w=3, d=0, l=1, gf=4, ga=2, results=["W", "W", "W", "L"]),
            wc(1994, 6, m=7, w=5, d=2, l=0, gf=11, ga=3,
               results=["W", "W", "D", "W", "W", "W", "D"],
               note="Final won on penalties (counted as a draw)"),
            wc(1998, 5, m=7, w=4, d=1, l=2, gf=14, ga=10,
               results=["W", "W", "L", "W", "W", "D", "L"]),
            wc(2002, 6, m=7, w=7, d=0, l=0, gf=18, ga=4,
               results=["W", "W", "W", "W", "W", "W", "W"], note="Won every match"),
            wc(2006, 3, m=5, w=4, d=0, l=1, gf=10, ga=2, results=["W", "W", "W", "W", "L"]),
            wc(2010, 3, m=5, w=3, d=1, l=1, gf=9, ga=4, results=["W", "W", "D", "W", "L"]),
            wc(2014, 4, stage="Semi-final", m=7, w=3, d=2, l=2, gf=11, ga=14,
               results=["W", "D", "W", "D", "W", "L", "L"], note="Fourth place as hosts"),
            wc(2018, 3, m=5, w=3, d=1, l=1, gf=8, ga=3, results=["D", "W", "W", "W", "L"]),
            wc(2022, 3, m=5, w=3, d=1, l=1, gf=8, ga=3, results=["W", "W", "L", "W", "D"],
               note="Eliminated on penalties in the quarter-final"),
            wc(2026, 1, stage="Qualified", note="Qualified for 2026 — the only team to appear at every World Cup"),
        ],
    },
    {
        "id": "england", "name": "England", "confederation": "UEFA", "qualified2026": True,
        "worldCups": [
            dnq(1930, "Did not enter"), dnq(1934, "Did not enter"), dnq(1938, "Did not enter"),
            wc(1950, 1, m=3, w=1, d=0, l=2, gf=2, ga=2, results=["W", "L", "L"]),
            wc(1954, 3, m=3, w=1, d=1, l=1, gf=8, ga=8, results=["D", "W", "L"]),
            wc(1958, 1, m=4, w=0, d=3, l=1, gf=4, ga=5, results=["D", "D", "D", "L"],
               note="Eliminated in a group play-off"),
            wc(1962, 3, m=4, w=1, d=1, l=2, gf=5, ga=6, results=["L", "W", "D", "L"]),
            wc(1966, 6, m=6, w=5, d=1, l=0, gf=11, ga=3,
               results=["D", "W", "W", "W", "W", "W"], note="Champions as hosts"),
            wc(1970, 3, m=4, w=2, d=0, l=2, gf=4, ga=4, results=["W", "L", "W", "L"]),
            dnq(1974), dnq(1978),
            wc(1982, 3, stage="Second round", m=5, w=3, d=2, l=0, gf=6, ga=1,
               results=["W", "W", "W", "D", "D"],
               note="Unbeaten, eliminated in the second group stage"),
            wc(1986, 3, m=5, w=2, d=1, l=2, gf=7, ga=3, results=["L", "D", "W", "W", "L"]),
            wc(1990, 4, stage="Semi-final", m=7, w=3, d=3, l=1, gf=8, ga=6,
               results=["D", "D", "W", "W", "W", "D", "L"],
               note="Fourth place; semi-final lost on penalties (counted as a draw)"),
            dnq(1994),
            wc(1998, 2, m=4, w=2, d=1, l=1, gf=7, ga=4, results=["W", "L", "W", "D"],
               note="Eliminated on penalties in the round of 16"),
            wc(2002, 3, m=5, w=2, d=2, l=1, gf=6, ga=3, results=["D", "W", "D", "W", "L"]),
            wc(2006, 3, m=5, w=3, d=2, l=0, gf=6, ga=2, results=["W", "W", "D", "W", "D"],
               note="Eliminated on penalties in the quarter-final"),
            wc(2010, 2, m=4, w=1, d=2, l=1, gf=3, ga=5, results=["D", "D", "W", "L"]),
            wc(2014, 1, m=3, w=0, d=1, l=2, gf=2, ga=4, results=["L", "L", "D"]),
            wc(2018, 4, stage="Semi-final", m=7, w=3, d=1, l=3, gf=12, ga=8,
               results=["W", "W", "L", "D", "W", "L", "L"],
               note="Fourth place; round-of-16 win on penalties (counted as a draw)"),
            wc(2022, 3, m=5, w=3, d=1, l=1, gf=13, ga=4, results=["W", "D", "W", "W", "L"]),
            wc(2026, 1, stage="Qualified", note="Qualified for 2026"),
        ],
    },
    {
        "id": "japan", "name": "Japan", "confederation": "AFC", "qualified2026": True,
        "worldCups": [
            dnq(1930, "Did not enter"), dnq(1934, "Did not enter"), dnq(1938, "Withdrew"),
            dnq(1950, "Not a FIFA member"), dnq(1954), dnq(1958, "Did not enter"),
            dnq(1962), dnq(1966, "Did not enter"), dnq(1970), dnq(1974), dnq(1978),
            dnq(1982), dnq(1986), dnq(1990),
            dnq(1994, "Missed out on the final qualifying matchday"),
            wc(1998, 1, m=3, w=0, d=0, l=3, gf=1, ga=4, results=["L", "L", "L"],
               note="First World Cup appearance"),
            wc(2002, 2, m=4, w=2, d=1, l=1, gf=5, ga=3, results=["D", "W", "W", "L"],
               note="Co-hosts"),
            wc(2006, 1, m=3, w=0, d=1, l=2, gf=2, ga=7, results=["L", "D", "L"]),
            wc(2010, 2, m=4, w=2, d=1, l=1, gf=4, ga=2, results=["W", "L", "W", "D"],
               note="Eliminated on penalties in the round of 16"),
            wc(2014, 1, m=3, w=0, d=1, l=2, gf=2, ga=6, results=["L", "D", "L"]),
            wc(2018, 2, m=4, w=1, d=1, l=2, gf=6, ga=7, results=["W", "D", "L", "L"]),
            wc(2022, 2, m=4, w=2, d=1, l=1, gf=5, ga=4, results=["W", "L", "W", "D"],
               note="Beat Germany and Spain; eliminated on penalties"),
            wc(2026, 1, stage="Qualified", note="First team to qualify for 2026"),
        ],
    },
    {
        "id": "usa", "name": "United States", "confederation": "CONCACAF", "qualified2026": True,
        "worldCups": [
            wc(1930, 4, stage="Semi-final", m=3, w=2, d=0, l=1, gf=7, ga=6,
               results=["W", "W", "L"], note="Third place — still the best US finish"),
            wc(1934, 2, stage="Round of 16", m=1, w=0, d=0, l=1, gf=1, ga=7, results=["L"],
               note="Straight knockout format"),
            dnq(1938, "Withdrew"),
            wc(1950, 1, m=3, w=1, d=0, l=2, gf=4, ga=8, results=["L", "W", "L"],
               note="Famous 1-0 win over England"),
            dnq(1954), dnq(1958), dnq(1962), dnq(1966), dnq(1970), dnq(1974),
            dnq(1978), dnq(1982), dnq(1986),
            wc(1990, 1, m=3, w=0, d=0, l=3, gf=2, ga=8, results=["L", "L", "L"]),
            wc(1994, 2, m=4, w=1, d=1, l=2, gf=3, ga=4, results=["D", "W", "L", "L"],
               note="Hosts"),
            wc(1998, 1, m=3, w=0, d=0, l=3, gf=1, ga=5, results=["L", "L", "L"]),
            wc(2002, 3, m=5, w=2, d=1, l=2, gf=7, ga=7, results=["W", "D", "L", "W", "L"]),
            wc(2006, 1, m=3, w=0, d=1, l=2, gf=2, ga=6, results=["L", "D", "L"]),
            wc(2010, 2, m=4, w=1, d=2, l=1, gf=5, ga=5, results=["D", "D", "W", "L"]),
            wc(2014, 2, m=4, w=1, d=1, l=2, gf=5, ga=6, results=["W", "D", "L", "L"]),
            dnq(2018),
            wc(2022, 2, m=4, w=1, d=2, l=1, gf=3, ga=4, results=["D", "D", "W", "L"]),
            wc(2026, 1, stage="Qualified", note="Co-hosts in 2026"),
        ],
    },
    {
        "id": "norway", "name": "Norway", "confederation": "UEFA", "qualified2026": True,
        "worldCups": [
            dnq(1930, "Did not enter"), dnq(1934, "Did not enter"),
            wc(1938, 2, stage="Round of 16", m=1, w=0, d=0, l=1, gf=1, ga=2, results=["L"],
               note="Straight knockout format; lost to eventual champions Italy after extra time"),
            dnq(1950), dnq(1954), dnq(1958), dnq(1962), dnq(1966), dnq(1970),
            dnq(1974), dnq(1978), dnq(1982), dnq(1986), dnq(1990),
            wc(1994, 1, m=3, w=1, d=1, l=1, gf=1, ga=1, results=["W", "L", "D"],
               note="Eliminated on goals scored in a group where all four teams finished on four points"),
            wc(1998, 2, m=4, w=1, d=2, l=1, gf=5, ga=5, results=["D", "D", "W", "L"],
               note="Beat Brazil in the group stage"),
            dnq(2002), dnq(2006), dnq(2010), dnq(2014), dnq(2018), dnq(2022),
            wc(2026, 1, stage="Qualified",
               note="First World Cup since 1998 — won the qualifying group ahead of Italy"),
        ],
    },
]

HISTORY = {
    "meta": {
        "years": YEARS,
        "stageLabels": {str(k): v for k, v in STAGE_LABELS.items()},
        "notes": [
            "Pre-1986 formats are mapped to the nearest modern equivalent (see README).",
            "Knockout matches decided on penalties are counted as draws.",
        ],
        "source": "Compiled manually from public historical records (FIFA archives, openfootball, Fjelstul World Cup Database).",
    },
    "teams": TEAMS,
}

ANALYSIS = {
    "disclaimer": ("Open tactical data is limited and squads change quickly. These summaries are "
                   "curated from publicly available analysis and recent match reports, and should "
                   "be read as indicative rather than definitive."),
    "teams": [
        {
            "teamId": "morocco",
            "styleSummary": "Compact, disciplined and transition-oriented. Morocco tend to defend in a mid or low block, close central spaces and break quickly through their wide players.",
            "defensiveStyle": "Organised mid-to-low block with strong central protection and aggressive duels when pressing triggers appear.",
            "attackingStyle": "Fast transitions, combinations in wide areas and late runs from midfield rather than sustained positional play.",
            "strengths": ["Defensive compactness", "Transitions and counter-attacks", "Collective discipline and intensity"],
            "weaknesses": ["Can struggle to create against deep blocks", "May become passive when protecting a lead"],
            "keyPlayers": ["Achraf Hakimi", "Sofyan Amrabat", "Brahim Díaz"],
            "sources": [
                {"title": "FIFA Training Centre — tactical analyses", "url": "https://fifatrainingcentre.com"},
                {"title": "FBref — team statistics", "url": "https://fbref.com"}
            ],
            "lastUpdated": "2026-06-01"
        },
        {
            "teamId": "argentina",
            "styleSummary": "Flexible and possession-comfortable, with a strong collective identity built under Lionel Scaloni. Recent analyses describe a side that controls midfield, presses in coordinated waves and still creates its decisive moments around Lionel Messi.",
            "defensiveStyle": "Well-drilled mid block with energetic counter-pressing after losses; rarely concedes large volumes of chances.",
            "attackingStyle": "Patient circulation that accelerates through central combinations; full-backs and midfield runners provide width and depth around the front line.",
            "strengths": ["Midfield control and pressing coordination", "Tournament experience and composure", "Set-piece organisation"],
            "weaknesses": ["An ageing core in key positions", "A recurring reliance on individual moments to unlock deep defences"],
            "keyPlayers": ["Lionel Messi", "Enzo Fernández", "Julián Álvarez"],
            "sources": [
                {"title": "FIFA Training Centre — tactical analyses", "url": "https://fifatrainingcentre.com"},
                {"title": "The Analyst — international football", "url": "https://theanalyst.com"}
            ],
            "lastUpdated": "2026-06-01"
        },
        {
            "teamId": "france",
            "styleSummary": "Pragmatic and devastating in transition. France tend to concede territory selectively and strike vertically at pace, with the attack heavily oriented towards Kylian Mbappé's side.",
            "defensiveStyle": "Medium block with a strong, athletic spine; comfortable defending without the ball for long spells.",
            "attackingStyle": "Direct, vertical attacks into the channels; quick release to the left side and runners arriving from midfield.",
            "strengths": ["Transition speed and individual quality", "Depth across the squad", "Big-tournament pedigree"],
            "weaknesses": ["Can drop too deep and invite pressure", "Build-up can look laboured against an organised press"],
            "keyPlayers": ["Kylian Mbappé", "Aurélien Tchouaméni", "Michael Olise"],
            "sources": [
                {"title": "FIFA Training Centre — tactical analyses", "url": "https://fifatrainingcentre.com"},
                {"title": "The Analyst — international football", "url": "https://theanalyst.com"}
            ],
            "lastUpdated": "2026-06-01"
        },
        {
            "teamId": "brazil",
            "styleSummary": "In transition between eras. Under Carlo Ancelotti the side has moved towards a more structured 4-3-3, balancing Brazil's traditional individual expression in wide areas with a more disciplined defensive base.",
            "defensiveStyle": "More compact and positionally cautious than earlier cycles; the midfield screens centrally while full-backs pick their moments.",
            "attackingStyle": "Wide attackers carrying the ball at pace in one-against-one situations, supported by overlaps and quick central combinations.",
            "strengths": ["Individual quality in the front line", "Pace and unpredictability in wide areas"],
            "weaknesses": ["A recurring pattern is instability from frequent coaching changes", "Balance between attacking talents is still being worked out"],
            "keyPlayers": ["Vinícius Júnior", "Raphinha", "Rodrygo"],
            "sources": [
                {"title": "FIFA Training Centre — tactical analyses", "url": "https://fifatrainingcentre.com"},
                {"title": "FBref — team statistics", "url": "https://fbref.com"}
            ],
            "lastUpdated": "2026-06-01"
        },
        {
            "teamId": "england",
            "styleSummary": "More direct and front-footed under Thomas Tuchel than in previous cycles. Recent analyses describe a side that wants to win the ball higher and move it forward with fewer touches, built around an experienced attacking core.",
            "defensiveStyle": "Higher, more aggressive pressing structure than before, with a back line comfortable defending larger spaces.",
            "attackingStyle": "Quicker progression into the final third; Harry Kane dropping to link while runners attack the space beyond him.",
            "strengths": ["Depth of attacking talent", "Set pieces", "A settled, experienced spine"],
            "weaknesses": ["One possible weakness is creativity against very deep blocks", "A history of conceding momentum in knockout ties"],
            "keyPlayers": ["Harry Kane", "Jude Bellingham", "Bukayo Saka"],
            "sources": [
                {"title": "FIFA Training Centre — tactical analyses", "url": "https://fifatrainingcentre.com"},
                {"title": "The Analyst — international football", "url": "https://theanalyst.com"}
            ],
            "lastUpdated": "2026-06-01"
        },
        {
            "teamId": "japan",
            "styleSummary": "Energetic, well-organised and dangerous in transition. Japan typically alternate between a patient 3-4-2-1 structure and sudden, high-intensity pressing phases that have repeatedly unsettled stronger opponents.",
            "defensiveStyle": "Compact 5-4-1 mid block out of possession, with sharp, coordinated pressing triggers in chosen phases.",
            "attackingStyle": "Quick vertical breaks through technically strong wide players and wing-backs; intelligent rotations between the lines.",
            "strengths": ["Pressing intensity and discipline", "Transitions through wide areas", "Squad depth from players in top European leagues"],
            "weaknesses": ["Chance conversion has been a recurring issue", "Sustained possession against deep blocks"],
            "keyPlayers": ["Kaoru Mitoma", "Takefusa Kubo", "Wataru Endo"],
            "sources": [
                {"title": "FIFA Training Centre — tactical analyses", "url": "https://fifatrainingcentre.com"},
                {"title": "FBref — team statistics", "url": "https://fbref.com"}
            ],
            "lastUpdated": "2026-06-01"
        },
        {
            "teamId": "usa",
            "styleSummary": "Athletic and transition-heavy under Mauricio Pochettino, with an emphasis on energy, pressing and quick attacks. As co-hosts, they enter 2026 with a young core that has grown up together.",
            "defensiveStyle": "Front-foot pressing in spells, dropping into a compact 4-4-2 block; relies on athleticism to recover space.",
            "attackingStyle": "Fast breaks through the wide channels, with Christian Pulisic as the main creative outlet.",
            "strengths": ["Athleticism and pressing energy", "Home advantage and crowd momentum", "A core entering its prime"],
            "weaknesses": ["Chance creation in settled possession", "Limited experience of deep tournament runs"],
            "keyPlayers": ["Christian Pulisic", "Weston McKennie", "Antonee Robinson"],
            "sources": [
                {"title": "FIFA Training Centre — tactical analyses", "url": "https://fifatrainingcentre.com"},
                {"title": "The Analyst — international football", "url": "https://theanalyst.com"}
            ],
            "lastUpdated": "2026-06-01"
        },
        {
            "teamId": "norway",
            "styleSummary": "Direct, vertical and ruthlessly efficient. Under Ståle Solbakken, Norway have built a clear identity around fast forward play towards Erling Haaland, with Martin Ødegaard dictating tempo behind him.",
            "defensiveStyle": "Disciplined mid block in a 4-4-2 shape; happy to concede possession and protect central areas.",
            "attackingStyle": "Quick, direct attacks with early balls into Haaland's running channels; dangerous on set pieces and second balls.",
            "strengths": ["Elite finishing through Haaland", "Clarity of game plan", "Set pieces and transitions"],
            "weaknesses": ["One possible weakness is defending wide areas against quick wingers", "Depth beyond the first-choice spine"],
            "keyPlayers": ["Erling Haaland", "Martin Ødegaard", "Antonio Nusa"],
            "sources": [
                {"title": "FIFA Training Centre — tactical analyses", "url": "https://fifatrainingcentre.com"},
                {"title": "FBref — team statistics", "url": "https://fbref.com"}
            ],
            "lastUpdated": "2026-06-01"
        },
    ],
}


def write(name, payload, global_name):
    json_path = DATA / f"{name}.json"
    js_path = DATA / f"{name}.js"
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    json_path.write_text(text + "\n", encoding="utf-8")
    js_path.write_text(
        f"// Generated by tools/build_data.py — do not edit by hand. Edit the script and rerun.\n"
        f"window.{global_name} = {text};\n",
        encoding="utf-8",
    )
    print(f"wrote {json_path.name} and {js_path.name}")


if __name__ == "__main__":
    write("worldcup-history", HISTORY, "WC_HISTORY")
    write("team-analysis", ANALYSIS, "WC_ANALYSIS")
