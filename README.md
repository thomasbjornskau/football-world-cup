# World Cup 2026 — team history & style explorer

A small, self-contained static site. Pick a team heading to the 2026 World Cup,
see its entire World Cup history visualized as a **ladder** (one marker per
tournament — the higher it sits, the further the team went), and read a short,
source-based note on how the side plays today.

No build step, no backend, no API keys. Plain HTML, CSS and JavaScript.

## Run it

**Locally:** open `index.html` directly in a browser. (Data is loaded via
`<script>` tags rather than `fetch()`, so it also works on `file://`.)

**GitHub Pages:** push the folder to a repository and enable Pages
(Settings → Pages → Deploy from branch → root). The site is fully static.

## Files

```text
index.html                    page structure
style.css                     all styling
script.js                     picker, ladder visualization, detail card, stats, analysis box
data/worldcup-history.json    canonical historical data
data/team-analysis.json       canonical tactical notes
data/worldcup-history.js      generated mirror (window.WC_HISTORY) — do not edit
data/team-analysis.js         generated mirror (window.WC_ANALYSIS) — do not edit
tools/build_data.py           single source of truth for the data; regenerates all four data files
```

## Editing or adding data

The data is defined in `tools/build_data.py`. Edit the Python dicts there and run:

```bash
python3 tools/build_data.py
```

This rewrites both the `.json` files (canonical, reusable by other tools) and
the `.js` mirrors the page actually loads. The script also keeps W–D–L counts
consistent with the `matchResults` arrays. If you prefer to edit the JSON
directly, you can — just keep the `.js` mirrors in sync (they are the same
content wrapped in `window.WC_HISTORY = …;` / `window.WC_ANALYSIS = …;`).

### Adding a team

Add an entry to `TEAMS` in `tools/build_data.py` with one `worldCups` item per
tournament year (1930–2026), and a matching entry in `ANALYSIS["teams"]` with
the same id. The page handles missing detail gracefully: a tournament can have
just `year` + `stageLevel`, and match dots only appear when `matchResults` is
present.

### Stage levels

```text
0  Did not qualify / did not enter
1  Group stage
2  Round of 16
3  Quarter-final
4  Semi-final (incl. 3rd/4th place)
5  Final (runner-up)
6  Champion
```

## Data conventions and caveats

- **Early formats are mapped to the nearest modern stage.** 1934/1938 were
  straight knockouts (first round → level 2). The second group stages of
  1974/1978 (last eight → level 3) and 1982 (last twelve → level 3) are mapped
  as shown in each entry's `note`.
- **Penalty shoot-outs count as draws**, following standard statistical
  convention. Argentina's 2022 title therefore shows as 4–2–1.
- **2026 entries are markers only** (`stage: "Qualified"`): they appear on the
  ladder as a dashed "Q" and are excluded from all-time totals and best-result
  calculations.
- Third-place play-offs are folded into the semi-final level, not shown
  separately.

## Sources

- Historical results: compiled manually from public records, cross-checkable
  against [openfootball/worldcup.json](https://github.com/openfootball/worldcup.json)
  (CC0) and the [Fjelstul World Cup Database](https://github.com/jfjelstul/worldcup).
- Tactical notes: curated summaries informed by openly available analysis such
  as the [FIFA Training Centre](https://fifatrainingcentre.com),
  [The Analyst](https://theanalyst.com) and [FBref](https://fbref.com).
  Each note carries a `lastUpdated` date and the page labels them explicitly
  as indicative rather than definitive.

## Known limitations

- Prototype dataset: **8 teams** (Morocco, Argentina, France, Brazil, England,
  Japan, United States, Norway). The data model supports all 48.
- Historical figures were entered by hand and validated for internal
  consistency (W–D–L vs. match sequences), but should be verified against the
  source databases before any serious use.
- Tactical notes are snapshots (June 2026) and will age quickly.
- No team comparison view yet — listed in the brief as a possible extension.
