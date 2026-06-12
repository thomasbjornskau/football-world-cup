/* ---------------------------------------------------------------
   World Cup 2026 — team history & style explorer
   Plain JS, no dependencies. Data is loaded as window.WC_HISTORY
   and window.WC_ANALYSIS (generated mirrors of /data/*.json).
   --------------------------------------------------------------- */

(function () {
  "use strict";

  // ---------- data guards ----------

  var HISTORY = window.WC_HISTORY;
  var ANALYSIS = window.WC_ANALYSIS;

  if (!HISTORY || !ANALYSIS) {
    document.getElementById("empty-state").innerHTML =
      "<p>Data unavailable. The files in <code>/data/</code> could not be loaded.</p>";
    return;
  }

  var TEAMS = HISTORY.teams;
  var YEARS = HISTORY.meta.years;

  var LEVELS = [
    { level: 6, label: "Champion" },
    { level: 5, label: "Final" },
    { level: 4, label: "Semi-final" },
    { level: 3, label: "Quarter-final" },
    { level: 2, label: "Round of 16" },
    { level: 1, label: "Group stage" },
    { level: 0, label: "Not qualified" }
  ];

  var LEVEL_COLORS = {
    0: "var(--lvl0)", 1: "var(--lvl1)", 2: "var(--lvl2)", 3: "var(--lvl3)",
    4: "var(--lvl4)", 5: "var(--lvl5)", 6: "var(--lvl6)"
  };

  // ---------- state ----------

  var state = {
    team: null,          // selected team object
    year: null,          // selected tournament year
    appearancesOnly: false
  };

  // ---------- helpers ----------

  function $(id) { return document.getElementById(id); }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function isUpcoming(entry) { return entry.stage === "Qualified"; }

  function completed(team) {
    return team.worldCups.filter(function (w) { return w.participated && !isUpcoming(w); });
  }

  function bestEntry(team) {
    var best = null;
    completed(team).forEach(function (w) {
      if (!best || w.stageLevel >= best.stageLevel) best = w; // >= keeps the most recent at the best level
    });
    return best;
  }

  function bestYears(team, level) {
    return completed(team)
      .filter(function (w) { return w.stageLevel === level; })
      .map(function (w) { return w.year; });
  }

  function findAnalysis(teamId) {
    for (var i = 0; i < ANALYSIS.teams.length; i++) {
      if (ANALYSIS.teams[i].teamId === teamId) return ANALYSIS.teams[i];
    }
    return null;
  }

  // ---------- picker ----------

  var input = $("team-input");
  var sugBox = $("suggestions");
  var activeIndex = -1;

  function matches(query) {
    var q = query.trim().toLowerCase();
    if (!q) return TEAMS.slice();
    return TEAMS.filter(function (t) {
      return t.name.toLowerCase().indexOf(q) !== -1 || t.id.indexOf(q) !== -1;
    });
  }

  function showSuggestions(list) {
    sugBox.innerHTML = "";
    activeIndex = -1;
    if (!list.length) {
      sugBox.innerHTML = '<li class="no-match">No team in this prototype matches that — try one of the quick picks.</li>';
    } else {
      list.forEach(function (t, i) {
        var li = document.createElement("li");
        li.setAttribute("role", "option");
        li.dataset.id = t.id;
        li.innerHTML = "<span>" + esc(t.name) + '</span><span class="conf">' + esc(t.confederation) + "</span>";
        li.addEventListener("mousedown", function (e) { e.preventDefault(); selectTeam(t.id); });
        sugBox.appendChild(li);
      });
    }
    sugBox.hidden = false;
    input.setAttribute("aria-expanded", "true");
  }

  function hideSuggestions() {
    sugBox.hidden = true;
    input.setAttribute("aria-expanded", "false");
  }

  input.addEventListener("input", function () { showSuggestions(matches(input.value)); });
  input.addEventListener("focus", function () { showSuggestions(matches(input.value)); });
  input.addEventListener("blur", function () { setTimeout(hideSuggestions, 120); });

  input.addEventListener("keydown", function (e) {
    var items = sugBox.querySelectorAll("li[data-id]");
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      if (!items.length) return;
      activeIndex = e.key === "ArrowDown"
        ? (activeIndex + 1) % items.length
        : (activeIndex - 1 + items.length) % items.length;
      items.forEach(function (li, i) {
        li.setAttribute("aria-selected", i === activeIndex ? "true" : "false");
      });
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (activeIndex >= 0 && items[activeIndex]) {
        selectTeam(items[activeIndex].dataset.id);
      } else {
        var m = matches(input.value);
        if (m.length) selectTeam(m[0].id);
      }
    } else if (e.key === "Escape") {
      hideSuggestions();
    }
  });

  // quick-pick chips
  var chipsBox = $("chips");
  TEAMS.forEach(function (t) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "chip";
    b.textContent = t.name;
    b.dataset.id = t.id;
    b.addEventListener("click", function () { selectTeam(t.id); });
    chipsBox.appendChild(b);
  });

  // ---------- team selection ----------

  function selectTeam(id) {
    var team = null;
    TEAMS.forEach(function (t) { if (t.id === id) team = t; });
    if (!team) return;

    state.team = team;
    var best = bestEntry(team);
    state.year = best ? best.year : null;

    input.value = team.name;
    hideSuggestions();

    document.querySelectorAll(".chip").forEach(function (c) {
      c.classList.toggle("active", c.dataset.id === id);
    });

    $("empty-state").hidden = true;
    $("main").hidden = false;

    renderTeamHead(team);
    renderLadder();
    renderDetail();
    renderStats(team);
    renderAnalysis(team);
  }

  function renderTeamHead(team) {
    $("team-name").textContent = team.name;
    $("team-conf").textContent = team.confederation;

    var apps = completed(team).length;
    var best = bestEntry(team);
    var intro;
    if (!best) {
      intro = "First World Cup appearance in 2026.";
    } else {
      var years = bestYears(team, best.stageLevel);
      intro = apps + (apps === 1 ? " appearance" : " appearances") + " before 2026. Best result: " +
        best.stage + " (" + years.join(", ") + ").";
    }
    $("team-intro").textContent = intro;
  }

  // ---------- ladder visualization ----------

  var ladderBox = $("ladder");
  var tooltip = $("tooltip");

  function visibleYears(team) {
    if (!state.appearancesOnly) return YEARS.slice();
    return team.worldCups
      .filter(function (w) { return w.participated; })
      .map(function (w) { return w.year; });
  }

  function renderLadder() {
    var team = state.team;
    var years = visibleYears(team);
    var byYear = {};
    team.worldCups.forEach(function (w) { byYear[w.year] = w; });

    var W = 940, H = 320;
    var padL = 112, padR = 26, padT = 18, padB = 40;
    var innerW = W - padL - padR;
    var innerH = H - padT - padB;

    function x(i) {
      if (years.length === 1) return padL + innerW / 2;
      return padL + (innerW * i) / (years.length - 1);
    }
    function y(level) { return padT + innerH * (1 - level / 6); }

    var s = '<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="' +
      esc(team.name) + ' World Cup ladder, 1930 to 2026">';

    // level grid lines + labels
    LEVELS.forEach(function (lv) {
      var yy = y(lv.level);
      s += '<line x1="' + padL + '" y1="' + yy + '" x2="' + (W - padR) + '" y2="' + yy +
        '" stroke="var(--line)" stroke-width="1"' +
        (lv.level === 0 ? ' stroke-dasharray="none"' : ' stroke-dasharray="2 4"') + "/>";
      s += '<text class="lvl-label" x="' + (padL - 12) + '" y="' + (yy + 4) +
        '" text-anchor="end">' + lv.label + "</text>";
    });

    // path through participated tournaments (completed ones only)
    var pts = [];
    years.forEach(function (yr, i) {
      var w = byYear[yr];
      if (w && w.participated && !isUpcoming(w)) pts.push([x(i), y(w.stageLevel)]);
    });
    if (pts.length > 1) {
      s += '<polyline fill="none" stroke="var(--lvl3)" stroke-width="1.5" opacity="0.55" points="' +
        pts.map(function (p) { return p[0] + "," + p[1]; }).join(" ") + '"/>';
    }

    // markers + year labels
    years.forEach(function (yr, i) {
      var w = byYear[yr] || { year: yr, participated: false, stage: "Did not qualify", stageLevel: 0 };
      var xx = x(i), yy = y(w.stageLevel);
      var upcoming = isUpcoming(w);
      var sel = state.year === yr;
      var color = LEVEL_COLORS[w.stageLevel];

      s += '<g class="marker' + (sel ? " selected" : "") + '" tabindex="0" role="button" ' +
        'data-year="' + yr + '" aria-label="' + yr + ": " + esc(w.stage) + '">';
      s += '<circle class="halo" cx="' + xx + '" cy="' + yy + '" r="13" fill="none" ' +
        'stroke="var(--ink)" stroke-width="1.5" opacity="' + (sel ? 1 : 0) + '"/>';

      if (upcoming) {
        s += '<circle class="dot" cx="' + xx + '" cy="' + yy + '" r="8" fill="var(--card)" ' +
          'stroke="var(--lvl4)" stroke-width="2" stroke-dasharray="3 3"/>';
        s += '<text x="' + xx + '" y="' + (yy + 3.5) + '" text-anchor="middle" ' +
          'font-family="var(--display)" font-size="9" font-weight="700" fill="var(--lvl4)">Q</text>';
      } else if (!w.participated) {
        s += '<circle class="dot" cx="' + xx + '" cy="' + yy + '" r="4" fill="var(--paper)" ' +
          'stroke="var(--lvl0)" stroke-width="1.5"/>';
      } else if (w.stageLevel === 6) {
        // champion: gold star
        s += '<path class="dot" transform="translate(' + xx + "," + yy + ') scale(1.15)" fill="' + color +
          '" stroke="#a8841a" stroke-width="0.8" d="M0,-9 L2.4,-2.9 L9,-2.6 L3.8,1.4 L5.6,8 L0,4.2 L-5.6,8 L-3.8,1.4 L-9,-2.6 L-2.4,-2.9 Z"/>';
      } else {
        var r = 4.5 + w.stageLevel * 0.9;
        var ring = w.stageLevel === 5 ? ' stroke="#0c3f25" stroke-width="1.5"' : "";
        s += '<circle class="dot" cx="' + xx + '" cy="' + yy + '" r="' + r + '" fill="' + color + '"' + ring + "/>";
      }
      s += "</g>";

      // year label (every year if compressed, else every other + selected)
      var show = state.appearancesOnly || i % 2 === 0 || sel || yr === 2026;
      if (show) {
        s += '<text class="year-label' + (w.participated ? " on" : "") + '" x="' + xx + '" y="' +
          (H - 14) + '" text-anchor="middle">' + yr + "</text>";
      }
    });

    s += "</svg>";
    ladderBox.innerHTML = s;

    // marker interaction
    ladderBox.querySelectorAll(".marker").forEach(function (g) {
      var yr = parseInt(g.dataset.year, 10);
      g.addEventListener("click", function () { selectYear(yr); });
      g.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); selectYear(yr); }
      });
      g.addEventListener("mouseenter", function (e) { showTooltip(e, yr); });
      g.addEventListener("mousemove", function (e) { moveTooltip(e); });
      g.addEventListener("mouseleave", hideTooltip);
    });
  }

  function selectYear(yr) {
    state.year = yr;
    renderLadder();
    renderDetail();
  }

  function showTooltip(e, yr) {
    var w = null;
    state.team.worldCups.forEach(function (x) { if (x.year === yr) w = x; });
    if (!w) w = { stage: "Did not qualify" };
    var line2 = "";
    if (w.matches != null) {
      line2 = "<small>" + w.wins + "–" + w.draws + "–" + w.losses +
        " · GF " + w.goalsFor + " · GA " + w.goalsAgainst + "</small>";
    } else if (isUpcoming(w)) {
      line2 = "<small>Qualified — no result yet</small>";
    }
    tooltip.innerHTML = yr + " · " + esc(w.stage) + line2;
    tooltip.hidden = false;
    moveTooltip(e);
  }

  function moveTooltip(e) {
    tooltip.style.left = e.clientX + "px";
    tooltip.style.top = e.clientY + "px";
  }

  function hideTooltip() { tooltip.hidden = true; }

  $("toggle-appearances").addEventListener("change", function (e) {
    state.appearancesOnly = e.target.checked;
    renderLadder();
  });

  // ---------- tournament detail ----------

  function renderDetail() {
    var card = $("detail-card");
    var team = state.team;
    var w = null;
    team.worldCups.forEach(function (x) { if (x.year === state.year) w = x; });

    if (!w) { card.hidden = true; return; }
    card.hidden = false;

    $("detail-title").textContent = team.name + " at the " + w.year + " World Cup";
    var tag = $("detail-stage");
    tag.textContent = w.stage;
    tag.classList.toggle("gold", w.stageLevel === 6);

    var html = "";

    if (isUpcoming(w)) {
      html += '<p class="detail-numbers">Qualified for the 2026 tournament — no results yet.</p>';
    } else if (!w.participated) {
      html += '<p class="detail-numbers">' + esc(team.name) + " did not take part in this tournament.</p>";
    } else if (w.matches == null) {
      html += '<p class="detail-numbers">Detailed match data is not available for this tournament in the prototype dataset.</p>';
    } else {
      if (w.matchResults) {
        html += '<div class="match-dots" aria-label="Match results in order">';
        w.matchResults.forEach(function (r) {
          var cls = r === "W" ? "w" : r === "D" ? "d" : "l";
          var name = r === "W" ? "Win" : r === "D" ? "Draw" : "Loss";
          html += '<span class="dot ' + cls + '" title="' + name + '" role="img" aria-label="' + name + '"></span>';
        });
        html += "</div>";
        html += '<p class="dots-legend">One dot per match, in order played — green win, grey draw, red loss.</p>';
      }
      html += '<p class="detail-numbers"><strong>' + w.wins + "–" + w.draws + "–" + w.losses +
        "</strong> in " + w.matches + (w.matches === 1 ? " match" : " matches") +
        " &nbsp;·&nbsp; GF <strong>" + w.goalsFor + "</strong> &nbsp;·&nbsp; GA <strong>" + w.goalsAgainst +
        "</strong> &nbsp;·&nbsp; GD <strong>" + fmtGD(w.goalsFor - w.goalsAgainst) + "</strong></p>";
    }

    if (w.note) html += '<p class="detail-note">' + esc(w.note) + "</p>";
    $("detail-body").innerHTML = html;
  }

  function fmtGD(n) { return n > 0 ? "+" + n : String(n); }

  // ---------- all-time stats ----------

  function renderStats(team) {
    var played = completed(team);
    var apps = played.length;
    var totals = { w: 0, d: 0, l: 0, gf: 0, ga: 0, m: 0 };
    var titles = 0;

    played.forEach(function (w) {
      if (w.stageLevel === 6) titles++;
      if (w.matches != null) {
        totals.m += w.matches; totals.w += w.wins; totals.d += w.draws; totals.l += w.losses;
        totals.gf += w.goalsFor; totals.ga += w.goalsAgainst;
      }
    });

    var best = bestEntry(team);
    var bestLabel = best ? best.stage : "—";
    var bestSub = best ? bestYears(team, best.stageLevel).join(", ") : "Debut in 2026";

    var rows = [
      ["Appearances", apps + '<small>+ 2026</small>'],
      ["Best result", esc(bestLabel) + "<small>" + esc(bestSub) + "</small>"],
      ["Record (W–D–L)", totals.w + "–" + totals.d + "–" + totals.l + "<small>" + totals.m + " matches</small>"],
      ["Goals", totals.gf + "–" + totals.ga + "<small>GD " + fmtGD(totals.gf - totals.ga) + "</small>"]
    ];
    if (titles > 0) rows.splice(2, 0, ["Titles", titles + "<small>World champion" + (titles > 1 ? "s" : "") + "</small>"]);

    $("stats-grid").innerHTML = rows.map(function (r) {
      return "<div><dt>" + r[0] + "</dt><dd>" + r[1] + "</dd></div>";
    }).join("");
  }

  // ---------- analysis box ----------

  function renderAnalysis(team) {
    var a = findAnalysis(team.id);
    var box = $("analysis-body");

    if (!a) {
      box.innerHTML = '<p class="analysis-disclaimer">Open tactical data is limited for this team. ' +
        "No curated analysis is available in the prototype dataset.</p>";
      return;
    }

    var html = '<p class="analysis-summary">' + esc(a.styleSummary) + "</p>";

    html += block("In defence", "<p>" + esc(a.defensiveStyle) + "</p>");
    html += block("In attack", "<p>" + esc(a.attackingStyle) + "</p>");
    html += block("Strengths", listOf(a.strengths));
    html += block("Possible weaknesses", listOf(a.weaknesses));
    html += block("Players to watch",
      '<div class="players">' + a.keyPlayers.map(function (p) {
        return '<span class="player">' + esc(p) + "</span>";
      }).join("") + "</div>");

    html += '<p class="analysis-disclaimer">' + esc(ANALYSIS.disclaimer) + "</p>";

    if (a.sources && a.sources.length) {
      html += '<p class="analysis-sources">Sources: ' + a.sources.map(function (s) {
        return '<a href="' + esc(s.url) + '" rel="noopener">' + esc(s.title) + "</a>";
      }).join(" · ") + " · Updated " + esc(a.lastUpdated) + "</p>";
    }

    box.innerHTML = html;
  }

  function block(title, inner) {
    return '<div class="analysis-block"><h4>' + title + "</h4>" + inner + "</div>";
  }

  function listOf(items) {
    return "<ul>" + items.map(function (i) { return "<li>" + esc(i) + "</li>"; }).join("") + "</ul>";
  }

})();
