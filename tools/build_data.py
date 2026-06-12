#!/usr/bin/env python3
"""
Bygger datafiler for VM-prototypen — generator-utgave.

Historiske data GENERERES fra Fjelstul World Cup Database (CSV, 1930-2022),
som må ligge i tools/source/. Last ned med:

    cd tools/source
    for f in team_appearances.csv tournament_standings.csv; do
      curl -sLO https://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv/$f
    done

Kuraterte noter (OVERRIDES) og taktiske analyser (ANALYSIS) vedlikeholdes
manuelt i dette scriptet. Kjør:

    python3 tools/build_data.py

Output:
    data/worldcup-history.json / .js   (js-speil: window.WC_HISTORY)
    data/team-analysis.json   / .js    (js-speil: window.WC_ANALYSIS)

Konvensjoner:
- Straffekonkurranser telles som uavgjort (Fjelstul teller dem som seier/tap,
  så resultatet omregnes fra kampscore).
- Eldre formater mappes til naermeste moderne nivaa (se README).
- Vest-Tysklands resultater 1954-1990 tilskrives Tyskland (FIFA-praksis).
  Jugoslavia/Tsjekkoslovakia tilskrives IKKE Kroatia/Tsjekkia.
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "source"
DATA = ROOT / "data"

YEARS = [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 1978,
         1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026]

STAGE_LABELS = {0: "Did not qualify", 1: "Group stage", 2: "Round of 16",
                3: "Quarter-final", 4: "Semi-final", 5: "Final", 6: "Champion"}

STAGE_TO_LEVEL = {
    "group stage": 1,
    "round of 16": 2,
    "quarter-final": 3, "quarter-finals": 3,
    "second group stage": 3,          # 1974/1978 (top 8), 1982 (top 12)
    "semi-final": 4, "semi-finals": 4, "third-place match": 4,
    "final": 5,
    "final round": 4,                 # 1950; vinner/2.plass settes via standings
}

# ---------------------------------------------------------------------------
# Lagene: FIFAs 18 hoyest rankede VM-deltakere (april 2026-rankingen, Italia
# og Danmark er ikke kvalifisert) + Norge + Irak. dataNames = navn i Fjelstul.
# ---------------------------------------------------------------------------

TEAM_CONFIG = [
    {"id": "argentina",   "name": "Argentina",     "conf": "CONMEBOL", "dataNames": ["Argentina"]},
    {"id": "belgium",     "name": "Belgium",       "conf": "UEFA",     "dataNames": ["Belgium"]},
    {"id": "brazil",      "name": "Brazil",        "conf": "CONMEBOL", "dataNames": ["Brazil"]},
    {"id": "colombia",    "name": "Colombia",      "conf": "CONMEBOL", "dataNames": ["Colombia"]},
    {"id": "croatia",     "name": "Croatia",       "conf": "UEFA",     "dataNames": ["Croatia"]},
    {"id": "england",     "name": "England",       "conf": "UEFA",     "dataNames": ["England"]},
    {"id": "france",      "name": "France",        "conf": "UEFA",     "dataNames": ["France"]},
    {"id": "germany",     "name": "Germany",       "conf": "UEFA",     "dataNames": ["Germany", "West Germany"]},
    {"id": "iraq",        "name": "Iraq",          "conf": "AFC",      "dataNames": ["Iraq"]},
    {"id": "japan",       "name": "Japan",         "conf": "AFC",      "dataNames": ["Japan"]},
    {"id": "mexico",      "name": "Mexico",        "conf": "CONCACAF", "dataNames": ["Mexico"]},
    {"id": "morocco",     "name": "Morocco",       "conf": "CAF",      "dataNames": ["Morocco"]},
    {"id": "netherlands", "name": "Netherlands",   "conf": "UEFA",     "dataNames": ["Netherlands"]},
    {"id": "norway",      "name": "Norway",        "conf": "UEFA",     "dataNames": ["Norway"]},
    {"id": "portugal",    "name": "Portugal",      "conf": "UEFA",     "dataNames": ["Portugal"]},
    {"id": "senegal",     "name": "Senegal",       "conf": "CAF",      "dataNames": ["Senegal"]},
    {"id": "spain",       "name": "Spain",         "conf": "UEFA",     "dataNames": ["Spain"]},
    {"id": "switzerland", "name": "Switzerland",   "conf": "UEFA",     "dataNames": ["Switzerland"]},
    {"id": "uruguay",     "name": "Uruguay",       "conf": "CONMEBOL", "dataNames": ["Uruguay"]},
    {"id": "usa",         "name": "United States", "conf": "CONCACAF", "dataNames": ["United States"]},
]

# ---------------------------------------------------------------------------
# Kuraterte noter. (teamId, year) -> tekst. Overstyrer auto-genererte noter.
# ---------------------------------------------------------------------------

OVERRIDES = {
    # Morocco
    ("morocco", 1986): "First African side to reach the knockout stage",
    ("morocco", 2022): "First African semi-finalist; finished fourth",
    # Argentina
    ("argentina", 1930): "Runners-up at the first World Cup",
    ("argentina", 1934): "Straight knockout format",
    ("argentina", 1974): "Second group stage = last eight",
    ("argentina", 1978): "Champions as hosts",
    ("argentina", 1982): "Second group stage = last twelve",
    ("argentina", 1990): "Two knockout wins on penalties (counted as draws)",
    ("argentina", 2022): "Final and quarter-final won on penalties (counted as draws)",
    # France
    ("france", 1934): "Straight knockout format",
    ("france", 1958): "Third place; Fontaine scored 13",
    ("france", 1998): "Champions as hosts",
    # Brazil
    ("brazil", 1934): "Straight knockout format",
    ("brazil", 1950): "Lost the decisive match of the final round-robin to Uruguay — the Maracanazo",
    ("brazil", 1970): "Won every match",
    ("brazil", 1978): "Third place, unbeaten",
    ("brazil", 1982): "Second group stage = last twelve",
    ("brazil", 2002): "Won every match",
    ("brazil", 2014): "Fourth place as hosts",
    ("brazil", 2026): "Qualified for 2026 — the only team to appear at every World Cup",
    # England
    ("england", 1958): "Eliminated in a group play-off",
    ("england", 1966): "Champions as hosts",
    ("england", 1982): "Unbeaten, eliminated in the second group stage",
    # Japan
    ("japan", 1998): "First World Cup appearance",
    ("japan", 2002): "Co-hosts",
    ("japan", 2022): "Beat Germany and Spain; eliminated on penalties",
    ("japan", 2026): "First team to qualify for 2026",
    # USA
    ("usa", 1930): "Third place — still the best US finish",
    ("usa", 1934): "Straight knockout format",
    ("usa", 1950): "Famous 1-0 win over England",
    ("usa", 1994): "Hosts",
    ("usa", 2026): "Co-hosts in 2026",
    # Norway
    ("norway", 1938): "Straight knockout format; lost to eventual champions Italy after extra time",
    ("norway", 1994): "Eliminated on goals scored in a group where all four teams finished on four points",
    ("norway", 1998): "Beat Brazil in the group stage",
    ("norway", 2026): "First World Cup since 1998 — won the qualifying group ahead of Italy",
    # Spain
    ("spain", 1950): "Fourth in the final round-robin — Spain's best finish before 2010",
    ("spain", 2010): "Champions for the first time",
    # Germany
    ("germany", 1954): "Won as West Germany — the Miracle of Bern",
    ("germany", 1974): "Won as West Germany, as hosts",
    ("germany", 1990): "Won as West Germany",
    ("germany", 2014): "First title as reunified Germany",
    # Uruguay
    ("uruguay", 1930): "Champions as hosts at the first World Cup",
    ("uruguay", 1950): "Won the decisive match of the final round-robin against hosts Brazil — the Maracanazo",
    # Croatia
    ("croatia", 1998): "Third place at the first appearance as an independent nation",
    ("croatia", 2018): "Runners-up; two knockout wins on penalties (counted as draws)",
    ("croatia", 2022): "Third place",
    # Mexico
    ("mexico", 1970): "Quarter-final as hosts",
    ("mexico", 1986): "Quarter-final as hosts",
    ("mexico", 1990): "Banned from qualifying after fielding overage players in youth competition",
    ("mexico", 2026): "Hosts for a record third time",
    # Senegal
    ("senegal", 2002): "Beat holders France in the opening match; quarter-final on debut",
    # Switzerland
    ("switzerland", 1954): "Quarter-final as hosts",
    # Iraq
    ("iraq", 1986): "Iraq's only previous appearance",
    ("iraq", 2026): "First World Cup since 1986 — qualified via the intercontinental play-off",
    # Colombia
    ("colombia", 2014): "Quarter-final — Colombia's best finish",
    # Netherlands / Belgium / Portugal
    ("netherlands", 1974): "Runners-up at the first appearance since 1938 — the Total Football side",
    ("netherlands", 2010): "A third final, again lost",
    ("belgium", 2018): "Third place — Belgium's best finish",
    ("portugal", 1966): "Third place at the first appearance — Eusébio top scorer",
}

GENERIC_2026 = "Qualified for 2026"

# ---------------------------------------------------------------------------
# Taktiske analyser — kuratert, forsiktig formulert, med kilder.
# ---------------------------------------------------------------------------

SRC_FIFA = {"title": "FIFA Training Centre — tactical analyses", "url": "https://fifatrainingcentre.com"}
SRC_ANALYST = {"title": "The Analyst — international football", "url": "https://theanalyst.com"}
SRC_FBREF = {"title": "FBref — team statistics", "url": "https://fbref.com"}

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
            "sources": [SRC_FIFA, SRC_FBREF],
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
            "sources": [SRC_FIFA, SRC_ANALYST],
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
            "sources": [SRC_FIFA, SRC_ANALYST],
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
            "sources": [SRC_FIFA, SRC_FBREF],
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
            "sources": [SRC_FIFA, SRC_ANALYST],
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
            "sources": [SRC_FIFA, SRC_FBREF],
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
            "sources": [SRC_FIFA, SRC_ANALYST],
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
            "sources": [SRC_FIFA, SRC_FBREF],
            "lastUpdated": "2026-06-01"
        },
        {
            "teamId": "spain",
            "styleSummary": "The tournament's clearest positional-play side. Under Luis de la Fuente, Spain combine their traditional short-passing control with far more direct wing play than earlier eras, built around exceptionally young wide talents.",
            "defensiveStyle": "High line and immediate counter-press after losses; opponents rarely get settled possession in Spain's half.",
            "attackingStyle": "Patient central build-up that releases quick one-against-one wingers high and wide; midfielders arrive late in the box.",
            "strengths": ["Technical security under pressure", "Elite wide players on both flanks", "A defined, well-rehearsed model"],
            "weaknesses": ["Can be vulnerable to direct balls in behind the high line", "A recurring question is physicality in central defence"],
            "keyPlayers": ["Lamine Yamal", "Pedri", "Nico Williams"],
            "sources": [SRC_FIFA, SRC_ANALYST],
            "lastUpdated": "2026-06-12"
        },
        {
            "teamId": "portugal",
            "styleSummary": "Talent-rich and increasingly structured under Roberto Martínez. Recent analyses describe a possession-oriented side with overloads in wide areas, still balancing its system around Cristiano Ronaldo's role in the box.",
            "defensiveStyle": "Mid-to-high block with strong individual defenders; pressing intensity varies more than the top pressing sides.",
            "attackingStyle": "Patient circulation into wide overloads; creative full-backs and inverted wingers supply a fixed reference striker.",
            "strengths": ["Depth of creative midfielders and wingers", "Individual quality across every line"],
            "weaknesses": ["The balance around an ageing focal point in attack", "A tendency to dominate territory without converting it"],
            "keyPlayers": ["Bruno Fernandes", "Rafael Leão", "Vitinha"],
            "sources": [SRC_FIFA, SRC_ANALYST],
            "lastUpdated": "2026-06-12"
        },
        {
            "teamId": "netherlands",
            "styleSummary": "Structured, physical and pragmatic under Ronald Koeman. The Dutch tend to build calmly from a back three or four, defend with discipline, and rely on a powerful midfield axis rather than classic wing play.",
            "defensiveStyle": "Compact, well-organised block with strong aerial defenders; comfortable managing games without dominating them.",
            "attackingStyle": "Controlled build-up through central midfield, with full-backs or wing-backs providing the width and late box arrivals from midfield.",
            "strengths": ["Midfield power and control", "Set pieces and aerial strength", "Tournament-savvy game management"],
            "weaknesses": ["Creating high-quality chances against deep blocks", "A recurring lack of a prolific central striker"],
            "keyPlayers": ["Frenkie de Jong", "Virgil van Dijk", "Cody Gakpo"],
            "sources": [SRC_FIFA, SRC_ANALYST],
            "lastUpdated": "2026-06-12"
        },
        {
            "teamId": "belgium",
            "styleSummary": "A side renewing itself after its golden generation. Under Rudi Garcia, Belgium are described as more counter-oriented and less possession-dominant than before, organised around a young creative core.",
            "defensiveStyle": "Medium block with an emphasis on protecting central areas; less aggressive pressing than the top sides.",
            "attackingStyle": "Quick combinations through the half-spaces, with Kevin De Bruyne's successors and Jérémy Doku's carries as the main chance creators.",
            "strengths": ["Elite ball-carrying in wide areas", "Goalkeeping", "A talented emerging generation"],
            "weaknesses": ["A defence in generational transition", "Recent tournament performances have lagged the talent level"],
            "keyPlayers": ["Jérémy Doku", "Amadou Onana", "Thibaut Courtois"],
            "sources": [SRC_FIFA, SRC_ANALYST],
            "lastUpdated": "2026-06-12"
        },
        {
            "teamId": "germany",
            "styleSummary": "Rebuilt and re-energised under Julian Nagelsmann. Recent analyses describe a high-tempo side that presses aggressively, attacks the half-spaces with quick combinations and has rediscovered a clear identity after a difficult decade of tournaments.",
            "defensiveStyle": "High, coordinated pressing with an aggressive line; accepts risk in behind in exchange for territorial control.",
            "attackingStyle": "Fast vertical combinations through central zones, with technically elite midfielders arriving between the lines.",
            "strengths": ["Midfield creativity and pressing structure", "Home-style tournament pedigree", "Set pieces"],
            "weaknesses": ["Vulnerability to direct play against the high line", "A recurring search for a reliable goalscoring striker"],
            "keyPlayers": ["Jamal Musiala", "Florian Wirtz", "Joshua Kimmich"],
            "sources": [SRC_FIFA, SRC_ANALYST],
            "lastUpdated": "2026-06-12"
        },
        {
            "teamId": "croatia",
            "styleSummary": "Technical, patient and exceptionally tournament-hardened. Croatia under Zlatko Dalić still run games through a high-class midfield, controlling tempo and grinding out tight knockout matches — often via extra time and penalties.",
            "defensiveStyle": "Disciplined mid block that prioritises position over pressing; experienced defenders who manage risk well.",
            "attackingStyle": "Midfield-led control with measured progression; chances are constructed rather than counter-attacked.",
            "strengths": ["Midfield quality and composure", "Knockout-match resilience", "Penalty shoot-out record"],
            "weaknesses": ["An ageing core, with Luka Modrić's role gradually reduced", "Limited pace in wide areas"],
            "keyPlayers": ["Joško Gvardiol", "Mateo Kovačić", "Luka Modrić"],
            "sources": [SRC_FIFA, SRC_ANALYST],
            "lastUpdated": "2026-06-12"
        },
        {
            "teamId": "colombia",
            "styleSummary": "Expressive and attack-minded under Néstor Lorenzo, with a long unbeaten run in recent years built on technical midfield play and one of the world's most productive creators in James Rodríguez's successor generation — and Luis Díaz at the heart of everything.",
            "defensiveStyle": "Medium block with energetic central midfielders; full-backs push high, leaving space that quicker opponents can target.",
            "attackingStyle": "Fluid combination play through the left side, with Luis Díaz's dribbling and overlapping full-backs creating overloads.",
            "strengths": ["Creative quality in the final third", "Momentum and confidence from a strong qualifying cycle"],
            "weaknesses": ["Space behind advanced full-backs", "A tendency to drop intensity after taking leads"],
            "keyPlayers": ["Luis Díaz", "Richard Ríos", "Davinson Sánchez"],
            "sources": [SRC_FIFA, SRC_ANALYST],
            "lastUpdated": "2026-06-12"
        },
        {
            "teamId": "senegal",
            "styleSummary": "Physical, fast and front-footed. Under Pape Thiaw, Senegal press high from a 4-3-3, counter-press immediately after losses and release their forwards early — with Sadio Mané still the side's reference point, dropping in to link play.",
            "defensiveStyle": "Aggressive, coordinated high press backed by athletic, duel-strong defenders and an elite goalkeeper.",
            "attackingStyle": "Vertical attacks launched the moment the ball turns over; explosive carries from wide areas and runners breaking beyond the striker.",
            "strengths": ["Athleticism and duel strength across the pitch", "Transition speed", "A settled, experienced spine with continental titles"],
            "weaknesses": ["Sustained creation against teams that sit very deep", "A reliance on key veterans for composure in big matches"],
            "keyPlayers": ["Sadio Mané", "Pape Matar Sarr", "Édouard Mendy"],
            "sources": [
                {"title": "Coaches' Voice — Senegal tactical analysis", "url": "https://learning.coachesvoice.com"},
                SRC_FIFA
            ],
            "lastUpdated": "2026-06-12"
        },
        {
            "teamId": "mexico",
            "styleSummary": "Experienced and pragmatic under Javier Aguirre, hosting the World Cup for a record third time. Recent analyses describe a side that mixes patient possession at home with a more cautious, counter-oriented game against stronger opponents.",
            "defensiveStyle": "Organised mid block with experienced central defenders; Aguirre's sides are typically hard to break down rather than aggressive pressers.",
            "attackingStyle": "Build-up through wide rotations and full-back overlaps; relies on moments from quick attackers rather than a fixed pattern.",
            "strengths": ["Home advantage and tournament atmosphere", "Tactical discipline", "Depth of tournament experience"],
            "weaknesses": ["A long-running shortage of elite goalscoring", "The round-of-16 ceiling has become its own psychological weight"],
            "keyPlayers": ["Edson Álvarez", "Santiago Giménez", "Luis Romo"],
            "sources": [SRC_FIFA, SRC_ANALYST],
            "lastUpdated": "2026-06-12"
        },
        {
            "teamId": "uruguay",
            "styleSummary": "Intense, brave and unmistakably Marcelo Bielsa's team. Uruguay press man-to-man across the pitch, attack with verticality and numbers, and have traded their traditional pragmatism for one of the most aggressive styles in the tournament.",
            "defensiveStyle": "Man-oriented high pressing all over the pitch; physically demanding and deliberately high-risk.",
            "attackingStyle": "Direct, fast attacks with runners committed forward in waves; width from touchline wingers and overlapping backs.",
            "strengths": ["Pressing intensity and physical edge", "A young, athletic core", "Clear and distinctive game model"],
            "weaknesses": ["Man-marking leaves one-against-one risks at the back", "Intensity is hard to sustain across a seven-match tournament"],
            "keyPlayers": ["Federico Valverde", "Darwin Núñez", "Ronald Araújo"],
            "sources": [SRC_FIFA, SRC_ANALYST],
            "lastUpdated": "2026-06-12"
        },
        {
            "teamId": "switzerland",
            "styleSummary": "Stable, compact and quietly effective — the tournament's most consistent overachiever. Under Murat Yakin, Switzerland defend in an organised block, control games through technically secure midfielders and rarely beat themselves.",
            "defensiveStyle": "Disciplined 4-2-3-1 or back-three block with excellent collective shape; concedes few clear chances.",
            "attackingStyle": "Measured build-up through midfield, with set pieces and mid-range strikes as recurring weapons.",
            "strengths": ["Organisation and consistency", "Knockout-stage experience", "Set pieces"],
            "weaknesses": ["A limited ceiling in open attacking play", "Reliance on a small group of creators"],
            "keyPlayers": ["Granit Xhaka", "Manuel Akanji", "Dan Ndoye"],
            "sources": [SRC_FIFA, SRC_ANALYST],
            "lastUpdated": "2026-06-12"
        },
        {
            "teamId": "iraq",
            "styleSummary": "Resilient, compact and counter-attacking. Under Graham Arnold, Iraq have traded an inconsistent identity for a disciplined low-to-mid block — typically a 4-4-2 that absorbs pressure, keeps possession in the mid-40s and breaks with direct, physical running.",
            "defensiveStyle": "Deep, well-organised block with selective pressing; the priority is denying central space and staying in matches.",
            "attackingStyle": "Quick, direct transitions towards two strikers, with physical duels and wide running rather than build-up play.",
            "strengths": ["Defensive organisation under Arnold", "Composure in decisive matches — qualification went to the wire twice", "Emotional momentum from a 40-year wait"],
            "weaknesses": ["A large gap in class against top sides", "Limited creation when forced to take the initiative"],
            "keyPlayers": ["Aymen Hussein", "Amir Al-Ammari", "Zidane Iqbal"],
            "sources": [
                {"title": "Yahoo Sports — World Cup 2026 Group I preview", "url": "https://sports.yahoo.com"},
                SRC_FIFA
            ],
            "lastUpdated": "2026-06-12"
        },
    ],
}

# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

def load_rows():
    with open(SRC / "team_appearances.csv", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if "Men's" in r["tournament_name"]]
    with open(SRC / "tournament_standings.csv", encoding="utf-8") as f:
        standings = [r for r in csv.DictReader(f) if "Men's" in r["tournament_name"]]
    return rows, standings


def build_team(cfg, rows, standings):
    names = set(cfg["dataNames"])
    mine = [r for r in rows if r["team_name"] in names]
    by_year = {}
    for r in mine:
        by_year.setdefault(int(r["tournament_id"][-4:]), []).append(r)

    pos_by_year = {}
    for s in standings:
        if s["team_name"] in names:
            pos_by_year[int(s["tournament_id"][-4:])] = int(s["position"])

    world_cups = []
    for year in YEARS:
        if year == 2026:
            world_cups.append({
                "year": 2026, "participated": True, "stage": "Qualified", "stageLevel": 1,
                "note": OVERRIDES.get((cfg["id"], 2026), GENERIC_2026),
            })
            continue

        matches = by_year.get(year)
        if not matches:
            entry = {"year": year, "participated": False,
                     "stage": STAGE_LABELS[0], "stageLevel": 0}
            note = OVERRIDES.get((cfg["id"], year))
            if note:
                entry["note"] = note
            world_cups.append(entry)
            continue

        matches.sort(key=lambda r: (r["match_date"], r["match_id"]))

        # resultater: straffekonkurranser omregnes til uavgjort via kampscore
        results, w, d, l, gf, ga = [], 0, 0, 0, 0, 0
        furthest = 1
        last = matches[-1]
        for r in matches:
            g_for, g_against = int(r["goals_for"]), int(r["goals_against"])
            gf += g_for; ga += g_against
            if g_for > g_against:
                results.append("W"); w += 1
            elif g_for < g_against:
                results.append("L"); l += 1
            else:
                results.append("D"); d += 1
            furthest = max(furthest, STAGE_TO_LEVEL[r["stage_name"]])

        second_group = any(r["stage_name"] == "second group stage" for r in matches)

        # standings (topp 4) overstyrer nivå
        level = furthest
        pos = pos_by_year.get(year)
        if pos == 1:
            level = 6
        elif pos == 2:
            level = 5
        elif pos in (3, 4):
            level = max(level, 4)

        # etikett
        if level == 3 and second_group:
            label = "Second group stage"
        elif level == 4 and year == 1950:
            label = "Final round"
        else:
            label = STAGE_LABELS[level]

        # auto-noter
        notes = []
        if pos == 3:
            notes.append("Third place")
        elif pos == 4:
            notes.append("Fourth place")
        if last["penalty_shootout"] == "1":
            pen_won = int(last["penalties_for"]) > int(last["penalties_against"])
            if last["stage_name"] == "final":
                notes.append("Final " + ("won" if pen_won else "lost") +
                             " on penalties (counted as a draw)")
            elif not pen_won:
                notes.append("Eliminated on penalties in the " +
                             last["stage_name"].replace("-finals", "-final").replace("finals", "final"))

        entry = {
            "year": year, "participated": True, "stage": label, "stageLevel": level,
            "matches": len(matches), "wins": w, "draws": d, "losses": l,
            "goalsFor": gf, "goalsAgainst": ga, "matchResults": results,
        }
        note = OVERRIDES.get((cfg["id"], year)) or "; ".join(notes)
        if note:
            entry["note"] = note
        world_cups.append(entry)

    return {
        "id": cfg["id"], "name": cfg["name"], "confederation": cfg["conf"],
        "qualified2026": True, "worldCups": world_cups,
    }


def validate(teams):
    errs = []
    for t in teams:
        for w in t["worldCups"]:
            if "matches" in w:
                if w["wins"] + w["draws"] + w["losses"] != w["matches"]:
                    errs.append(f"{t['id']} {w['year']}: W+D+L != matches")
                r = w["matchResults"]
                if (len(r) != w["matches"] or r.count("W") != w["wins"]
                        or r.count("D") != w["draws"] or r.count("L") != w["losses"]):
                    errs.append(f"{t['id']} {w['year']}: matchResults inconsistent")
        years = [w["year"] for w in t["worldCups"]]
        if years != YEARS:
            errs.append(f"{t['id']}: year coverage incomplete")
    ana = {a["teamId"] for a in ANALYSIS["teams"]}
    hist = {t["id"] for t in teams}
    if ana != hist:
        errs.append(f"analysis/history id mismatch: {ana ^ hist}")
    return errs


def write(name, payload, global_name):
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    (DATA / f"{name}.json").write_text(text + "\n", encoding="utf-8")
    (DATA / f"{name}.js").write_text(
        f"// Generated by tools/build_data.py — do not edit by hand. Edit the script and rerun.\n"
        f"window.{global_name} = {text};\n", encoding="utf-8")
    print(f"wrote {name}.json and {name}.js")


if __name__ == "__main__":
    rows, standings = load_rows()
    teams = [build_team(cfg, rows, standings) for cfg in TEAM_CONFIG]
    teams.sort(key=lambda t: t["name"])

    errs = validate(teams)
    if errs:
        raise SystemExit("VALIDATION FAILED:\n" + "\n".join(errs))

    history = {
        "meta": {
            "years": YEARS,
            "stageLabels": {str(k): v for k, v in STAGE_LABELS.items()},
            "selection": ("The 18 highest-ranked teams at the 2026 World Cup "
                          "(FIFA Men's World Ranking, April 2026), plus Norway and Iraq — "
                          "covering all of Group I."),
            "notes": [
                "Generated from the Fjelstul World Cup Database (1930-2022).",
                "Pre-1986 formats are mapped to the nearest modern equivalent (see README).",
                "Knockout matches decided on penalties are counted as draws.",
                "West Germany's results (1954-1990) are attributed to Germany, per FIFA convention. "
                "Yugoslavia and Czechoslovakia are not attributed to Croatia or any current team in this set.",
            ],
            "source": "Fjelstul World Cup Database (github.com/jfjelstul/worldcup); curated notes and 2026 entries added manually.",
        },
        "teams": teams,
    }
    write("worldcup-history", history, "WC_HISTORY")
    write("team-analysis", ANALYSIS, "WC_ANALYSIS")
    print(f"{len(teams)} teams")
