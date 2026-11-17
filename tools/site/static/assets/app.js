(function () {
  "use strict";

  var app = document.getElementById("app");
  var foot = document.getElementById("foot");
  var SITE = null;
  var FILMS = {};
  var PENDING = false;

  var STATUS = {
    "development": "In development",
    "pre-production": "Pre-production",
    "generation": "Shooting",
    "post": "In the cutting room",
    "released": "Now showing"
  };
  var STAGES = [
    ["story", "Story"], ["analysis", "Analysis"], ["bible", "Bible"], ["shotlist", "Shotlist"],
    ["shot_plan", "Shot plan"], ["sound_list", "Sound list"], ["references", "References"],
    ["generation", "Generation"], ["framerate", "Framerate fix"], ["edit", "Edit"],
    ["sound_design", "Sound design"], ["music", "Music"], ["release", "Release"]
  ];
  var GROUPS = { style: "Style", world: "World", characters: "Characters", locations: "Locations", props: "Props", vehicles: "Vehicles" };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function num(n) { return (n || 0).toLocaleString("en-US"); }
  function getJSON(p) {
    return fetch(p, { cache: "no-cache" }).then(function (r) { if (!r.ok) throw new Error(p); return r.json(); });
  }
  function getText(p) {
    return fetch(p, { cache: "no-cache" }).then(function (r) { if (!r.ok) throw new Error(p); return r.text(); });
  }
  function stripTitle(md) {
    return md.replace(/<!--[\s\S]*?-->/g, "").replace(/^# .*\n?/m, "").trim();
  }
  function renderMarkdown(md, base) {
    var html = window.marked ? window.marked.parse(stripTitle(md)) : "<pre>" + esc(md) + "</pre>";
    var box = document.createElement("div");
    box.innerHTML = html;
    box.querySelectorAll("img").forEach(function (img) {
      var src = img.getAttribute("src") || "";
      if (!/^(https?:|data:|\/)/.test(src)) img.setAttribute("src", base + src);
      img.loading = "lazy";
    });
    box.querySelectorAll("a").forEach(function (a) {
      if (/^https?:/.test(a.getAttribute("href") || "")) { a.target = "_blank"; a.rel = "noopener"; }
    });
    return box.innerHTML;
  }
  function stamp(status) {
    return '<span class="stamp' + (status === "released" ? " released" : "") + '">' + esc(STATUS[status] || status || "") + "</span>";
  }
  function frame(src, alt) {
    return '<div class="frame">' + (src
      ? '<img src="' + esc(src) + '" alt="' + esc(alt || "") + '" loading="lazy">'
      : '<div class="empty">No picture yet</div>') + "</div>";
  }
  function strip(cells) {
    if (!cells || !cells.length) return '<p class="label">Shotlist not written yet</p>';
    return '<div class="strip" aria-label="one square per shot, filled when a take is approved">' +
      cells.map(function (c) {
        return '<span class="cell ' + (c.loved ? "loved" : esc(c.status)) + (c.quality ? " q" + c.quality : "") + '" title="' + esc(c.id + (c.quality ? " · best " + c.quality + "/5" : "")) + '"></span>';
      }).join("") + "</div>";
  }
  function numbers(st, withCredits) {
    var items = [["Shots", st.shots_done + "/" + st.shots_total], ["Takes", num(st.takes)], ["Loved", num(st.loved)]];
    if (withCredits && st.credits != null) items.push(["Credits", num(st.credits)]);
    return '<dl class="numbers">' + items.map(function (i) {
      return "<div><dt>" + i[0] + "</dt><dd>" + i[1] + "</dd></div>";
    }).join("") + "</dl>";
  }
  function discordBtn() {
    return SITE && SITE.discord ? '<a class="btn red" href="' + esc(SITE.discord) + '" target="_blank" rel="noopener">Join the Discord</a>' : "";
  }

  // ---------- production board ----------
  var DAY = 86400000;
  var WEEKDAY = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  var MONTH = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  function localISO(d) {
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }
  function parseISO(s) { var p = s.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function dayLabel(s) { var d = parseISO(s); return WEEKDAY[d.getDay()] + " " + d.getDate() + " " + MONTH[d.getMonth()]; }
  function daysBetween(a, b) { return Math.round((parseISO(b) - parseISO(a)) / DAY); }
  function mmss(sec) { sec = Math.round(sec || 0); return Math.floor(sec / 60) + ":" + String(sec % 60).padStart(2, "0"); }
  function pct(a, b) { return b ? Math.round(a / b * 100) : 0; }
  function ago(iso) {
    if (!iso) return "";
    var m = Math.max(0, Math.round((Date.now() - Date.parse(iso)) / 60000));
    if (m < 1) return "just now";
    if (m < 60) return m + " min ago";
    var h = Math.floor(m / 60);
    if (h < 24) return h + " h " + (m % 60) + " min ago";
    return Math.floor(h / 24) + " d ago";
  }

  function sceneStats(sc) {
    var live = sc.shots.filter(function (s) { return s.status !== "cut"; });
    var st = { id: sc.id, total: live.length, approved: 0, review: 0, todo: 0, sec: 0, secDone: 0, takes: 0 };
    live.forEach(function (s) {
      st.sec += s.duration_s || 0;
      st.takes += s.takes.length;
      if (s.status === "approved") { st.approved++; st.secDone += s.duration_s || 0; }
      else if (s.status === "review" || s.status === "generating") st.review++;
      else st.todo++;
    });
    return st;
  }

  function segbar(st, tall) {
    var parts = [["approved", st.approved, "Approved"], ["review", st.review, "In review"], ["todo", st.todo, "Not shot"]];
    var name = parts.map(function (p) { return p[2] + " " + p[1] + " (" + pct(p[1], st.total) + "%)"; }).join(", ");
    return '<div class="seg' + (tall ? " tall" : "") + '" role="img" aria-label="' + esc(name) + '">' + parts.map(function (p) {
      if (!p[1]) return "";
      var share = pct(p[1], st.total);
      return '<span class="part ' + p[0] + '" style="flex:' + p[1] + '" title="' + esc(p[2] + ": " + p[1] + " shots, " + share + "%") + '">' +
        (tall && share >= 7 ? share + "%" : "") + "</span>";
    }).join("") + "</div>";
  }

  function tile(f, sc, sh) {
    var q = sh.quality;
    var cls = "tile " + esc(sh.status) + (q ? " q" + q : "");
    var info = [sc.id + " " + sh.id, sh.framing, sh.duration_s ? sh.duration_s + " s" : "",
      sh.takes.length + (sh.takes.length === 1 ? " take" : " takes"), q ? "best " + q + "/5" : (sh.takes.length ? "unrated" : ""),
      sh.status === "approved" ? "approved" : sh.status].filter(Boolean).join(" · ");
    return '<a class="' + cls + '" href="#/film/' + esc(f.slug) + "/shotlist/" + esc(sc.id + "-" + sh.id) + '" title="' + esc(info) + '" aria-label="' + esc(info) + '">' +
      '<span class="n">' + esc(sh.id.replace(/^SH/, "")) + "</span>" +
      '<span class="q">' + (sh.loved ? "♥" : "") + (q || (sh.takes.length ? "?" : "")) + "</span></a>";
  }

  function scheduleRows(f, byScene, today) {
    var days = (f.schedule && f.schedule.days) || [];
    return days.map(function (d) {
      var sts = (d.scenes || []).map(function (id) { return byScene[id]; }).filter(Boolean);
      var tot = sts.reduce(function (a, s) { return a + s.total; }, 0);
      var ok = sts.reduce(function (a, s) { return a + s.approved; }, 0);
      var state = d.date === today ? "today" : (d.date < today ? "past" : "next");
      var flag = "";
      if (tot) {
        if (ok === tot) flag = '<span class="flag done">✓ Done</span>';
        else if (d.date < today) flag = '<span class="flag late">! Behind ' + (tot - ok) + "</span>";
        else if (d.date === today) flag = '<span class="flag now">● Today</span>';
      } else if (d.date === today) flag = '<span class="flag now">● Today</span>';
      return '<li class="day ' + state + '"><time>' + esc(dayLabel(d.date)) + "</time>" +
        '<div class="day-body"><div class="day-scenes">' + (sts.length ? sts.map(function (s) {
          return '<a href="#scene-' + esc(s.id) + '" class="chip">' + esc(s.id) + " <b>" + s.approved + "/" + s.total + "</b></a>";
        }).join("") : "") + '<span class="task">' + esc(d.task || "") + "</span></div>" +
        (tot ? '<div class="mini"><span style="width:' + pct(ok, tot) + '%"></span></div>' : "") + "</div>" + flag + "</li>";
    }).join("");
  }

  function qualityPanel(f) {
    var counts = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0, u: 0 };
    var weak = [], pick = [], unrated = [];
    f.scenes.forEach(function (sc) {
      sc.shots.forEach(function (sh) {
        if (sh.status === "cut" || !sh.takes.length) return;
        var ref = { f: f, sc: sc, sh: sh };
        if (sh.quality) counts[sh.quality]++; else counts.u++;
        if (sh.quality && sh.quality <= 2 && !sh.loved) weak.push(ref);
        if (sh.quality && sh.quality >= 4 && !sh.loved) pick.push(ref);
        if (sh.takes.some(function (t) { return !t.rating && !t.love; })) unrated.push(ref);
      });
    });
    var shot = Object.keys(counts).reduce(function (a, k) { return a + counts[k]; }, 0);
    var max = Math.max.apply(null, Object.keys(counts).map(function (k) { return counts[k]; }).concat([1]));
    var rows = [["5", "5 great"], ["4", "4 good"], ["3", "3 usable"], ["2", "2 meh"], ["1", "1 no"], ["u", "Unrated"]];
    function list(items, label) {
      if (!items.length) return "";
      return '<div class="qlist"><div class="label">' + label + " (" + items.length + ")</div>" + items.map(function (r) {
        return '<a href="#/film/' + esc(r.f.slug) + "/shotlist/" + esc(r.sc.id + "-" + r.sh.id) + '">' + esc(r.sc.id + " " + r.sh.id) +
          (r.sh.quality ? " <b>" + r.sh.quality + "</b>" : "") + "</a>";
      }).join("") + "</div>";
    }
    return '<div class="panel"><div class="label">Quality of the shots with takes (' + shot + ")</div>" +
      '<p class="hint">Best take per shot, or the loved one. Ratings 1 to 5 from your reviews.</p>' +
      '<table class="qdist">' + rows.map(function (r) {
        var n = counts[r[0]];
        return "<tr><th>" + r[1] + '</th><td><span class="qbar ' + (r[0] === "u" ? "qu" : "q" + r[0]) + '" style="width:' + (n / max * 100) + '%"></span></td><td class="v">' + n + "</td></tr>";
      }).join("") + "</table>" +
      list(pick, "Strong, no select yet") + list(weak, "Weak, retake or cut") + list(unrated, "Takes waiting for a rating") + "</div>";
  }

  function renderProduction(f) {
    var today = localISO(new Date());
    var all = { total: 0, approved: 0, review: 0, todo: 0, sec: 0, secDone: 0, takes: 0 };
    var byScene = {};
    f.scenes.forEach(function (sc) {
      var s = sceneStats(sc);
      byScene[sc.id] = s;
      ["total", "approved", "review", "todo", "sec", "secDone", "takes"].forEach(function (k) { all[k] += s[k]; });
    });
    var sched = f.schedule || {};
    var days = sched.days || [];
    var dueIds = {};
    var lastGen = "";
    days.forEach(function (d) {
      if ((d.scenes || []).length && d.date > lastGen) lastGen = d.date;
      if (d.date <= today) (d.scenes || []).forEach(function (id) { dueIds[id] = 1; });
    });
    var due = 0, dueOk = 0;
    Object.keys(dueIds).forEach(function (id) { if (byScene[id]) { due += byScene[id].total; dueOk += byScene[id].approved; } });
    var left = all.total - all.approved;

    var tiles = [];
    tiles.push(["Approved", pct(all.approved, all.total) + "<small>%</small>", all.approved + " of " + all.total + " shots"]);
    tiles.push(["Left", left, left === 1 ? "shot to approve" : "shots to approve"]);
    var due_by = sched.shots_due || lastGen;
    if (sched.shots_due) {
      var sd = daysBetween(today, sched.shots_due);
      tiles.push(["Shots due", sd >= 0 ? sd + (sd === 1 ? "<small> day</small>" : "<small> days</small>") : "passed", dayLabel(sched.shots_due) + ", then edit"]);
    }
    tiles.push(["Runtime approved", mmss(all.secDone), "of " + mmss(all.sec) + " planned"]);
    if (sched.deadline) {
      var dl = daysBetween(today, sched.deadline);
      tiles.push(["Deadline", dl >= 0 ? dl + (dl === 1 ? "<small> day</small>" : "<small> days</small>") : "passed", dayLabel(sched.deadline)]);
    }
    if (f.stats.credits != null) tiles.push(["Credits spent", num(f.stats.credits), all.takes + " takes"]);

    var pace = "";
    if (due_by && left) {
      var genDays = daysBetween(today, due_by) + 1;
      pace = genDays > 0
        ? "To approve every shot by " + dayLabel(due_by) + ": <b>" + Math.ceil(left / genDays) + " shots a day</b>, today included."
        : "Shots were due " + dayLabel(due_by) + ": " + left + " still to approve.";
    }
    var plan = due
      ? "Plan up to today: <b>" + due + "</b> shots approved. Actual: <b>" + dueOk + "</b>" + (due > dueOk ? ", behind by <b>" + (due - dueOk) + "</b>." : ", on plan.")
      : "";

    var html = '<div class="board-head"><span class="live" title="The page checks for new data every minute">Live</span>' +
      '<span class="label">Data from the repository, built ' + esc(ago(SITE.built)) + (SITE.commit ? " · " + esc(SITE.commit) : "") + "</span></div>" +
      '<div class="tiles">' + tiles.map(function (t) {
        return '<div class="tile-stat"><div class="label">' + t[0] + '</div><div class="val">' + t[1] + '</div><div class="sub2">' + esc(t[2]) + "</div></div>";
      }).join("") + "</div>" +
      '<div class="panel">' + segbar(all, true) +
      '<div class="legend"><span><i class="sw approved"></i>Approved (a loved take)</span><span><i class="sw review"></i>In review (takes, no select)</span><span><i class="sw todo"></i>Not shot</span></div>' +
      (plan || pace ? '<p class="plan">' + plan + (plan && pace ? "<br>" : "") + pace + "</p>" : "") + "</div>";

    if (days.length) {
      html += '<h2 class="h2">Schedule</h2>' + (sched.source ? '<p class="hint">' + esc(sched.source) + "</p>" : "") +
        '<ol class="schedule">' + scheduleRows(f, byScene, today) + "</ol>";
    }

    html += '<h2 class="h2">Shots by scene</h2>' +
      '<div class="legend"><span><i class="sw tile-k q5"></i>5</span><span><i class="sw tile-k q4"></i>4</span><span><i class="sw tile-k q3"></i>3</span><span><i class="sw tile-k q2"></i>2</span><span><i class="sw tile-k q1"></i>1</span>' +
      '<span><i class="sw tile-k un"></i>? takes, unrated</span><span><i class="sw tile-k pl"></i>not shot</span><span>♥ approved</span><span class="hint">Number: best rating. Click a shot for its takes.</span></div>' +
      '<div class="scenes-board">' + f.scenes.map(function (sc) {
        var s = byScene[sc.id];
        var planned = days.filter(function (d) { return (d.scenes || []).indexOf(sc.id) >= 0; }).map(function (d) { return dayLabel(d.date); });
        return '<section class="srow" id="scene-' + esc(sc.id) + '"><div class="srow-head"><h3>' + esc(sc.id) + "</h3>" +
          '<div class="srow-meta"><div class="stitle">' + esc(sc.title || "") + "</div>" +
          '<div class="label">' + s.approved + "/" + s.total + " approved · " + s.review + " in review · " + mmss(s.secDone) + " of " + mmss(s.sec) +
          (planned.length ? " · planned " + esc(planned.join(", ")) : "") + "</div></div></div>" +
          segbar(s, false) +
          '<div class="tiles-grid">' + sc.shots.filter(function (sh) { return sh.status !== "cut"; }).map(function (sh) { return tile(f, sc, sh); }).join("") + "</div></section>";
      }).join("") + "</div>";

    var stages = '<ul class="stages">' + STAGES.map(function (s) {
      var v = (f.stages || {})[s[0]] || "todo";
      return '<li class="' + esc(v) + '"><span class="box ' + esc(v) + '"></span>' + s[1] + "</li>";
    }).join("") + "</ul>";
    var log = (f.log || []).map(function (l, i) { return [l, i]; }).sort(function (a, b) {
      return (b[0].date || "").localeCompare(a[0].date || "") || b[1] - a[1];
    }).map(function (p) { return "<li><time>" + esc(p[0].date) + "</time><span>" + esc(p[0].text) + "</span></li>"; }).join("");
    var final = f.links && f.links.final ? '<a class="btn" href="' + esc(f.links.final) + '" target="_blank" rel="noopener">Watch the film</a>' : "";

    html += '<div class="grid-2 lower">' + qualityPanel(f) +
      '<div class="panel"><div class="label" style="margin-bottom:10px">Stages ' + f.stats.stages_done + "/" + f.stats.stages_total + "</div>" + stages +
      '<div class="links">' + final + discordBtn() + "</div></div></div>" +
      (log ? '<h2 class="h2">Production log</h2><ul class="log">' + log + "</ul>" : "");
    return html;
  }

  // ---------- index ----------
  function renderIndex() {
    document.title = SITE.title || "SHORT FILMS";
    var films = SITE.films || [];
    var html = '<header class="masthead">' +
      '<div class="label">' + esc(SITE.author || "") + " presents</div>" +
      '<h1 class="marquee">' + esc(SITE.title || "SHORT FILMS") + "</h1>" +
      '<p class="sub">' + esc(SITE.subtitle || "") + "</p>" +
      '<div class="links">' + discordBtn() + "</div></header>" +
      '<div class="section-title"><span class="label">Program</span><span class="label">' + films.length + (films.length === 1 ? " film" : " films") + "</span></div>";
    if (!films.length) {
      html += '<div class="empty-state">The first reel is being loaded. Come back soon.</div>';
    } else {
      html += '<div class="reels">' + films.map(function (f) {
        return '<a class="reel" href="#/film/' + esc(f.slug) + '">' + frame(f.poster, f.title) +
          '<div class="reel-body"><div class="label">No. ' + esc(f.id) + (f.format && f.format.aspect ? " / " + esc(f.format.aspect) : "") + "</div>" +
          "<h2>" + esc(f.title) + "</h2>" +
          (f.logline ? '<p class="logline">' + esc(f.logline) + "</p>" : "") +
          stamp(f.status) + strip(f.strip) + numbers(f.stats, true) + "</div></a>";
      }).join("") + "</div>";
    }
    app.innerHTML = html;
  }

  // ---------- film ----------
  function tabsFor(f) {
    var t = [["production", "Production"]];
    if (f.docs.story) t.push(["story", "Story"]);
    if (f.docs.analysis) t.push(["analysis", "Analysis"]);
    if (f.docs.questions) t.push(["questions", "Questions"]);
    if (f.bible && f.bible.length) t.push(["bible", "Bible"]);
    if (f.scenes && f.scenes.length) t.push(["shotlist", "Shotlist"]);
    if (f.docs.budget) t.push(["budget", "Budget"]);
    if (f.docs.sound) t.push(["sound", "Sound"]);
    if (f.docs.music) t.push(["music", "Music"]);
    if (f.docs.edit) t.push(["edit", "Edit"]);
    return t;
  }

  function renderDoc(target, doc, asScreenplay) {
    target.innerHTML = '<p class="label">Loading...</p>';
    getText(doc.path).then(function (md) {
      target.innerHTML = asScreenplay
        ? '<pre class="screenplay">' + esc(stripTitle(md)) + "</pre>"
        : '<div class="doc">' + renderMarkdown(md, doc.base) + "</div>";
    }).catch(function () { target.innerHTML = '<p class="label">Could not load this document.</p>'; });
  }

  function renderBible(f) {
    return f.bible.map(function (g) {
      return '<section class="bible-group"><h2 class="label" style="margin:0 0 12px">' + esc(GROUPS[g.name] || g.name) + "</h2>" +
        '<div class="bible-cards">' + g.items.map(function (it, i) {
          var img = it.images && it.images[0];
          return '<details class="bcard" data-doc="' + esc(g.name + ":" + i) + '"><summary>' +
            (img ? '<img src="' + esc(img) + '" alt="' + esc(it.title) + '" loading="lazy">' : (g.name === "world" || g.name === "style" ? "" : '<div class="noimg">No reference yet</div>')) +
            "<h4>" + esc(it.title) + "</h4><p>" + esc(it.summary) + '</p></summary><div class="doc-slot"></div></details>';
        }).join("") + "</div></section>";
    }).join("");
  }

  // ---------- shotlist with the take viewer ----------
  var SHOTS = {};      // "S01-SH030" -> { sc, sh }
  var SELECTED = {};   // "S01-SH030" -> take id the viewer shows

  function stars(n) { return n ? new Array(n + 1).join("★") : ""; }

  function takeRow(t, costs, active) {
    return '<tr data-take="' + esc(t.id) + '" class="pick' + (t.love ? " is-loved" : "") + (active ? " is-active" : "") + '" tabindex="0">' +
      '<td class="play">' + (t.video ? "▶" : "") + "</td><td>" + esc(t.id) + (t.love ? " ♥" : "") + "</td><td>" + esc(t.date || "") +
      "</td><td>" + esc([t.duration_s ? t.duration_s + "s" : "", t.resolution, t.mode].filter(Boolean).join(" / ")) +
      '</td><td title="' + (t.rating_source === "inferred" ? "inferred from your reaction" : "") + '">' + stars(t.rating) + (t.rating_source === "inferred" ? "<sup>i</sup>" : "") +
      "</td>" + (costs ? "<td>" + (t.credits != null ? num(t.credits) : "") + "</td>" : "") + "</tr>";
  }

  function defaultTake(sh) {
    var key = sh.__key;
    var pick = null;
    sh.takes.forEach(function (t) { if (t.id === SELECTED[key]) pick = t; });
    if (pick) return pick;
    sh.takes.forEach(function (t) { if (t.id === sh.loved) pick = t; });
    if (pick) return pick;
    for (var i = sh.takes.length - 1; i >= 0; i--) if (sh.takes[i].video) return sh.takes[i];
    return sh.takes[sh.takes.length - 1] || null;
  }

  function viewerHTML(sh, t) {
    if (!t) return "";
    var cap = [t.id + (t.love ? " ♥" : ""), t.duration_s ? t.duration_s + " s" : "", t.resolution, t.mode,
      t.rating ? t.rating + "/5" + (t.rating_source === "inferred" ? " (inferred)" : "") : "unrated",
      t.credits != null ? num(t.credits) + " credits" : "", t.date].filter(Boolean).join(" · ");
    return '<div class="player"><div class="screen">' + (t.video
      ? '<video controls playsinline preload="metadata" src="' + esc(t.video) + '"' + (t.poster ? ' poster="' + esc(t.poster) + '"' : "") + "></video>"
      : '<div class="novideo">No video file for ' + esc(t.id) + "</div>") +
      '</div><div class="take-cap">' + esc(cap) + "</div></div>" +
      '<div class="ptext"><div class="label">Prompt · ' + esc(t.id) + "</div>" +
      (t.prompt ? '<pre class="prompt">' + esc(t.prompt) + "</pre>" : '<p class="label">No prompt file</p>') +
      (t.notes ? '<div class="label" style="margin-top:12px">Notes</div><p class="note">' + esc(t.notes) + "</p>" : "") + "</div>";
  }

  function showTake(details, takeId, play) {
    var hit = SHOTS[details.id.replace(/^shot-/, "")];
    if (!hit) return;
    var sh = hit.sh;
    if (takeId) SELECTED[sh.__key] = takeId;
    var t = defaultTake(sh);
    details.querySelector(".viewer").innerHTML = viewerHTML(sh, t);
    details.querySelectorAll("tr[data-take]").forEach(function (r) { r.classList.toggle("is-active", !!t && r.dataset.take === t.id); });
    var v = details.querySelector("video");
    if (v && play) { var pr = v.play(); if (pr && pr.catch) pr.catch(function () {}); }
  }

  function wireShotlist(box) {
    box.querySelectorAll("details.shot").forEach(function (d) {
      d.addEventListener("toggle", function () {
        if (d.open) { if (!d.querySelector(".viewer").innerHTML) showTake(d, null, false); }
        else d.querySelectorAll("video").forEach(function (v) { v.pause(); });
      });
    });
    function pick(e) {
      var row = e.target.closest && e.target.closest("tr[data-take]");
      if (!row) return;
      if (e.type === "keydown" && e.key !== "Enter" && e.key !== " ") return;
      e.preventDefault();
      var d = row.closest("details.shot");
      d.querySelectorAll("video").forEach(function (v) { v.pause(); });
      showTake(d, row.dataset.take, true);
    }
    box.addEventListener("click", pick);
    box.addEventListener("keydown", pick);
  }

  function renderShotlist(f) {
    var costs = f.stats.credits != null;
    SHOTS = {};
    return f.scenes.map(function (sc) {
      return '<section class="scene"><div class="scene-head"><h3>' + esc(sc.id) + (sc.title ? " &middot; " + esc(sc.title) : "") + "</h3>" +
        '<span class="label">' + esc([sc.location, sc.time].filter(Boolean).join(" / ")) + "</span></div>" +
        (sc.summary ? '<p class="note">' + esc(sc.summary) + "</p>" : "") +
        sc.shots.map(function (sh) {
          var key = sc.id + "-" + sh.id;
          sh.__key = key;
          SHOTS[key] = { sc: sc, sh: sh };
          var lt = null;
          sh.takes.forEach(function (t) { if (t.id === sh.loved) lt = t; });
          var thumb = lt && lt.poster ? '<img class="thumb" src="' + esc(lt.poster) + '" alt="" loading="lazy">' : '<div class="thumb empty">' + esc(sh.id) + "</div>";
          var spec = [sh.framing, sh.angle, sh.lens, sh.movement, sh.duration_s ? sh.duration_s + "s" : "", sh.transition_in && sh.transition_in !== "cut" ? sh.transition_in : ""].filter(Boolean).join(" / ");
          var cur = sh.takes.length ? defaultTake(sh) : null;
          var info = (sh.purpose ? '<p class="note"><span class="label">Why this shot</span><br>' + esc(sh.purpose) + "</p>" : "") +
            (sh.note ? '<p class="note"><span class="label">Screenplay note</span><br>' + esc(sh.note) + "</p>" : "") +
            (sh.dialogue ? '<p class="note"><span class="label">Dialogue</span><br>' + esc(sh.dialogue) + "</p>" : "");
          var body = '<div class="shot-open">' +
            (sh.takes.length
              ? '<div class="viewer"></div>' +
                '<table class="takes"><tr><th></th><th>Take</th><th>Date</th><th>Settings</th><th>Rating</th>' + (costs ? "<th>Credits</th>" : "") + "</tr>" +
                sh.takes.map(function (t) { return takeRow(t, costs, cur && t.id === cur.id); }).join("") + "</table>" +
                '<p class="hint">Click a take to play it with its prompt.</p>'
              : '<div class="viewer"></div><p class="label">No takes yet' + (sh.method ? " &middot; method: " + esc(sh.method) : "") + "</p>") +
            info +
            (lt && lt.references && lt.references.filter(Boolean).length ? '<div class="refs">' + lt.references.filter(Boolean).map(function (r) { return '<img src="' + esc(r) + '" alt="reference" loading="lazy">'; }).join("") + "</div>" : "") +
            "</div>";
          return '<details class="shot" id="shot-' + esc(key) + '"><summary>' + thumb +
            '<div class="sid-col"><div class="sid">' + esc(sh.id) + "</div></div>" +
            '<div><div class="spec">' + esc(spec) + '</div><p class="desc">' + esc(sh.description) + "</p></div>" +
            '<div class="state ' + esc(sh.status) + '">' + (sh.loved ? '<span class="heart">♥</span> ' : "") + esc(sh.status) +
            (sh.quality ? ' <span class="qnum q' + sh.quality + '">' + sh.quality + "</span>" : "") +
            "<br>" + sh.takes.length + (sh.takes.length === 1 ? " take" : " takes") + "</div>" +
            "</summary>" + body + "</details>";
        }).join("") + "</section>";
    }).join("");
  }

  function renderFilm(slug, tab, focus, keepScroll) {
    var load = FILMS[slug] ? Promise.resolve(FILMS[slug]) : getJSON("data/films/" + encodeURIComponent(slug) + ".json");
    load.then(function (f) {
      FILMS[slug] = f;
      document.title = f.title + " / " + (SITE.title || "SHORT FILMS");
      var tabs = tabsFor(f);
      if (!tabs.some(function (t) { return t[0] === tab; })) tab = "production";
      var fmt = f.format || {};
      app.innerHTML = '<a class="back label" href="#/">&larr; All films</a>' +
        '<header class="film-head"><div class="label">No. ' + esc(f.id) + "</div><h1>" + esc(f.title) + "</h1>" +
        (f.logline ? '<p class="logline">' + esc(f.logline) + "</p>" : "") +
        '<div class="film-meta">' + stamp(f.status) + '<span class="label">' +
        esc([fmt.aspect, fmt.fps ? fmt.fps + " fps" : "", fmt.resolution].filter(Boolean).join(" / ")) + "</span></div></header>" +
        '<nav class="tabs">' + tabs.map(function (t) {
          return '<a href="#/film/' + esc(slug) + "/" + t[0] + '"' + (t[0] === tab ? ' aria-current="page"' : "") + ">" + t[1] + "</a>";
        }).join("") + '</nav><section id="tab"></section>';
      var box = document.getElementById("tab");
      if (tab === "production") box.innerHTML = renderProduction(f);
      else if (tab === "story") renderDoc(box, f.docs.story, true);
      else if (tab === "bible") {
        box.innerHTML = renderBible(f);
        box.querySelectorAll("details.bcard").forEach(function (d) {
          d.addEventListener("toggle", function () {
            var slot = d.querySelector(".doc-slot");
            if (d.open && !slot.dataset.done) {
              var key = d.dataset.doc.split(":");
              var group = f.bible.filter(function (g) { return g.name === key[0]; })[0];
              renderDoc(slot, group.items[+key[1]], false);
              slot.dataset.done = "1";
            }
          });
        });
      } else if (tab === "shotlist") { box.innerHTML = renderShotlist(f); wireShotlist(box); }
      else renderDoc(box, f.docs[tab], false);
      var target = focus && document.getElementById("shot-" + focus);
      if (target) target.open = true;
      if (keepScroll != null) window.scrollTo(0, keepScroll);
      else if (target) target.scrollIntoView();
      else window.scrollTo(0, 0);
    }).catch(function () {
      app.innerHTML = '<a class="back label" href="#/">&larr; All films</a><div class="empty-state" style="margin-top:30px">This reel is missing.</div>';
    });
  }

  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#scene-"]');
    if (!a) return;
    e.preventDefault();
    var el = document.getElementById(a.getAttribute("href").slice(1));
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  function route(keepScroll) {
    var parts = (location.hash || "#/").replace(/^#\/?/, "").split("/").filter(Boolean);
    if (parts[0] === "film" && parts[1]) renderFilm(decodeURIComponent(parts[1]), parts[2] || "production", parts[3], keepScroll);
    else renderIndex();
  }

  getJSON("data/site.json").then(function (s) {
    SITE = s;
    foot.innerHTML = '<span class="label">Made shot by shot</span><span class="label">' +
      (s.discord ? '<a href="' + esc(s.discord) + '" target="_blank" rel="noopener">Discord</a> &middot; ' : "") +
      (s.home_url ? '<a href="' + esc(s.home_url) + '">' + esc(s.home_url.replace(/^https?:\/\//, "").replace(/\/$/, "")) + "</a>" : "") + "</span>";
    window.addEventListener("hashchange", function () { route(); });
    route();
    setInterval(function () {
      if (document.hidden) return;
      fetch("data/site.json", { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; }).then(function (n) {
        if (!n) return;
        var fresh = n.built !== SITE.built || PENDING;
        SITE = n;
        if (fresh) FILMS = {};
        var playing = [].some.call(document.querySelectorAll("video"), function (v) { return !v.paused && !v.ended; });
        if (playing) { PENDING = fresh; return; }
        PENDING = false;
        var open = [].map.call(document.querySelectorAll("details[open][id]"), function (d) { return d.id; });
        if (fresh || /#\/film\/[^/]+\/?(production)?$/.test(location.hash)) {
          route(window.scrollY);
          setTimeout(function () { open.forEach(function (id) { var d = document.getElementById(id); if (d) d.open = true; }); }, 300);
        }
      }).catch(function () {});
    }, 60000);
  }).catch(function () {
    app.innerHTML = '<div class="empty-state" style="margin-top:30vh">The projector is warming up. Try again in a minute.</div>';
  });
})();
