# World Cup 2026 — team history & style explorer

A small, self-contained static site. Pick a team heading to the 2026 World Cup,
see its entire World Cup history visualized as a **ladder** (one marker per
tournament — the higher it sits, the further the team went), and read a short,
source-based note on how the side plays today.

No build step, no backend, no API keys. Plain HTML, CSS and JavaScript.

## Run it

**Locally:** open `index.html` directly in a browser. (Data is loaded via
`<script>` tags rather than `fetch()`, so it also works on `file://`.)

(https://thomasbjornskau.github.io/football-world-cup/)|[https://thomasbjornskau.github.io/football-world-cup/]

**GitHub Pages:** push the folder to a repository and enable Pages
(Settings → Pages → Deploy from branch → root). The site is fully static.

## Files

```text
index.html                    page structure
style.css                     all styling
script.js                     picker, ladder visualization, detail card, stats, analysis box
data/worldcup-history.json    generated historical data (canonical output)
data/team-analysis.json       curated tactical notes
data/worldcup-history.js      mirror loaded by the page (window.WC_HISTORY) — do not edit
data/team-analysis.js         mirror loaded by the page (window.WC_ANALYSIS) — do not edit
tools/build_data.py           generator + curated notes + analyses; rebuilds all four data files
tools/source/                 Fjelstul World Cup Database CSVs (1930–2022)
```

## How the data is built

Historical results are **generated**, not hand-typed. `tools/build_data.py`
reads the Fjelstul World Cup Database CSVs in `tools/source/` and computes,
per team per tournament: furthest stage (via match stages and final
standings), W–D–L with penalty shoot-outs recomputed as draws, goals, and the
match-by-match result sequence. Curated notes (`OVERRIDES`), the 2026 entries
and all tactical analyses (`ANALYSIS`) are maintained by hand in the same
script. Rebuild with:

```bash
python3 tools/build_data.py
```

The script validates internal consistency (W–D–L vs. match sequences, full
year coverage, history/analysis id parity) and refuses to write on failure.
To refresh the source CSVs, see the download command in the script's header.

### Adding a team

Add one line to `TEAM_CONFIG` (id, display name, confederation, and the
team's name(s) in the Fjelstul data) and a matching entry in
`ANALYSIS["teams"]`. Everything else is generated. The page handles missing
detail gracefully.

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
- **Successor states:** West Germany's results (1954–1990) are attributed to
  Germany, following FIFA convention. Yugoslavia and Czechoslovakia are *not*
  attributed to Croatia or any current team in this set, and East Germany is
  excluded.
- The 1950 final round-robin maps to Champion/Final for the top two and to a
  "Final round" label at semi-final level for third and fourth place.

## Sources

- Historical results: generated from the
  [Fjelstul World Cup Database](https://github.com/jfjelstul/worldcup)
  (all men's World Cup matches 1930–2022). The women's tournaments included
  in that database are filtered out.
- Tactical notes: curated summaries informed by openly available analysis such
  as the [FIFA Training Centre](https://fifatrainingcentre.com),
  [The Analyst](https://theanalyst.com) and [FBref](https://fbref.com).
  Each note carries a `lastUpdated` date and the page labels them explicitly
  as indicative rather than definitive.

## Team selection

**20 teams**: the 18 highest-ranked sides at the 2026 World Cup (FIFA Men's
World Ranking, April 2026 — Italy and Denmark are in the top 20 but did not
qualify), plus Norway and Iraq. This covers all of Group I (France, Norway,
Senegal, Iraq). The pipeline supports all 48 teams; adding one is a single
config line plus a curated analysis entry.

## Known limitations

- Tactical notes are hand-curated snapshots (June 2026) and will age quickly;
  each carries a `lastUpdated` date.
- Historical data quality is inherited from the Fjelstul database. Generated
  figures for the original eight hand-entered teams matched on every value
  except one match-order detail (where the database was right).
- No team comparison view yet — listed in the brief as a possible extension.
