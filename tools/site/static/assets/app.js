(function () {
  "use strict";

  var app = document.getElementById("app");
  var foot = document.getElementById("foot");
  var SITE = null;
  var FILMS = {};

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
  var GROUPS = { world: "World", characters: "Characters", locations: "Locations", props: "Props", vehicles: "Vehicles" };

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
        return '<span class="cell ' + (c.loved ? "loved" : esc(c.status)) + '" title="' + esc(c.id) + '"></span>';
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

  // ---------- index ----------
  function renderIndex() {
    document.title = SITE.title || "FILM AI";
    var films = SITE.films || [];
    var html = '<header class="masthead">' +
      '<div class="label">' + esc(SITE.author || "") + " presents</div>" +
      '<h1 class="marquee">' + esc(SITE.title || "FILM AI") + "</h1>" +
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
    var t = [["overview", "Overview"]];
    if (f.docs.story) t.push(["story", "Story"]);
    if (f.docs.analysis) t.push(["analysis", "Analysis"]);
    if (f.bible && f.bible.length) t.push(["bible", "Bible"]);
    if (f.scenes && f.scenes.length) t.push(["shotlist", "Shotlist"]);
    if (f.docs.sound) t.push(["sound", "Sound"]);
    if (f.docs.music) t.push(["music", "Music"]);
    return t;
  }

  function renderOverview(f) {
    var st = f.stats;
    var pct = Math.round((st.shot_progress || 0) * 100);
    var cells = [];
    (f.scenes || []).forEach(function (sc) {
      sc.shots.forEach(function (sh) { if (sh.status !== "cut") cells.push({ id: sc.id + " " + sh.id, status: sh.status, loved: !!sh.loved }); });
    });
    var stages = '<ul class="stages">' + STAGES.map(function (s) {
      var v = (f.stages || {})[s[0]] || "todo";
      return '<li class="' + esc(v) + '"><span class="box ' + esc(v) + '"></span>' + s[1] + "</li>";
    }).join("") + "</ul>";
    var log = (f.log || []).map(function (l, i) { return [l, i]; }).sort(function (a, b) {
      return (b[0].date || "").localeCompare(a[0].date || "") || b[1] - a[1];
    }).map(function (p) { return p[0]; }).map(function (l) {
      return "<li><time>" + esc(l.date) + "</time><span>" + esc(l.text) + "</span></li>";
    }).join("");
    var final = f.links && f.links.final ? '<a class="btn" href="' + esc(f.links.final) + '" target="_blank" rel="noopener">Watch the film</a>' : "";
    return '<div class="grid-2">' +
      '<div class="panel"><div class="label">Shots approved</div><div class="big">' + pct + "<small>%</small></div>" +
      strip(cells) + '<div style="height:12px"></div>' + numbers(st, st.credits != null) +
      (st.estimated_credits ? '<p class="label" style="margin-top:10px">Planned budget ' + num(st.estimated_credits) + " credits</p>" : "") +
      '<div class="links">' + final + discordBtn() + "</div></div>" +
      '<div class="panel"><div class="label" style="margin-bottom:10px">Stages ' + st.stages_done + "/" + st.stages_total + "</div>" + stages + "</div>" +
      "</div>" +
      (log ? '<h2 class="label" style="margin:34px 0 8px">Production log</h2><ul class="log">' + log + "</ul>" : "");
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
            (img ? '<img src="' + esc(img) + '" alt="' + esc(it.title) + '" loading="lazy">' : (g.name === "world" ? "" : '<div class="noimg">No reference yet</div>')) +
            "<h4>" + esc(it.title) + "</h4><p>" + esc(it.summary) + '</p></summary><div class="doc-slot"></div></details>';
        }).join("") + "</div></section>";
    }).join("");
  }

  function takeRow(t, costs) {
    var stars = t.rating ? new Array(t.rating + 1).join("★") : "";
    return '<tr class="' + (t.love ? "is-loved" : "") + '"><td>' + esc(t.id) + (t.love ? " ♥" : "") + "</td><td>" + esc(t.date || "") +
      "</td><td>" + esc([t.duration_s ? t.duration_s + "s" : "", t.resolution, t.mode].filter(Boolean).join(" / ")) +
      "</td><td>" + stars + "</td>" + (costs ? "<td>" + (t.credits != null ? num(t.credits) : "") + "</td>" : "") + "</tr>";
  }

  function renderShotlist(f) {
    var costs = f.stats.credits != null;
    return f.scenes.map(function (sc) {
      return '<section class="scene"><div class="scene-head"><h3>' + esc(sc.id) + (sc.title ? " &middot; " + esc(sc.title) : "") + "</h3>" +
        '<span class="label">' + esc([sc.location, sc.time].filter(Boolean).join(" / ")) + "</span></div>" +
        (sc.summary ? '<p class="note">' + esc(sc.summary) + "</p>" : "") +
        sc.shots.map(function (sh) {
          var lt = null;
          sh.takes.forEach(function (t) { if (t.id === sh.loved) lt = t; });
          var thumb = lt && lt.poster ? '<img class="thumb" src="' + esc(lt.poster) + '" alt="" loading="lazy">' : '<div class="thumb empty">' + esc(sh.id) + "</div>";
          var spec = [sh.framing, sh.angle, sh.lens, sh.movement, sh.duration_s ? sh.duration_s + "s" : "", sh.transition_in && sh.transition_in !== "cut" ? sh.transition_in : ""].filter(Boolean).join(" / ");
          var body = '<div class="shot-body"><div>' +
            (lt && lt.preview ? '<div class="frame"><video src="' + esc(lt.preview) + '" poster="' + esc(lt.poster || "") + '" controls muted loop playsinline preload="none"></video></div>' : "") +
            (sh.purpose ? '<p class="note"><span class="label">Why this shot</span><br>' + esc(sh.purpose) + "</p>" : "") +
            (sh.dialogue ? '<p class="note"><span class="label">Dialogue</span><br>' + esc(sh.dialogue) + "</p>" : "") +
            "</div><div>" +
            (lt && lt.prompt ? '<div class="label">Prompt of the loved take ' + esc(lt.id) + '</div><pre class="prompt">' + esc(lt.prompt) + "</pre>" : "") +
            (lt && lt.references && lt.references.filter(Boolean).length ? '<div class="refs">' + lt.references.filter(Boolean).map(function (r) { return '<img src="' + esc(r) + '" alt="reference" loading="lazy">'; }).join("") + "</div>" : "") +
            (sh.takes.length ? '<table class="takes"><tr><th>Take</th><th>Date</th><th>Settings</th><th>Rating</th>' + (costs ? "<th>Credits</th>" : "") + "</tr>" +
              sh.takes.map(function (t) { return takeRow(t, costs); }).join("") + "</table>" : '<p class="label">No takes yet' + (sh.method ? " &middot; method: " + esc(sh.method) : "") + "</p>") +
            (lt && lt.notes ? '<p class="note">' + esc(lt.notes) + "</p>" : "") +
            "</div></div>";
          return '<details class="shot"><summary>' + thumb +
            '<div class="sid-col"><div class="sid">' + esc(sh.id) + "</div></div>" +
            '<div><div class="spec">' + esc(spec) + '</div><p class="desc">' + esc(sh.description) + "</p></div>" +
            '<div class="state ' + esc(sh.status) + '">' + (sh.loved ? '<span class="heart">♥</span> ' : "") + esc(sh.status) +
            "<br>" + sh.takes.length + (sh.takes.length === 1 ? " take" : " takes") + "</div>" +
            "</summary>" + body + "</details>";
        }).join("") + "</section>";
    }).join("");
  }

  function renderFilm(slug, tab) {
    var load = FILMS[slug] ? Promise.resolve(FILMS[slug]) : getJSON("data/films/" + encodeURIComponent(slug) + ".json");
    load.then(function (f) {
      FILMS[slug] = f;
      document.title = f.title + " / " + (SITE.title || "FILM AI");
      var tabs = tabsFor(f);
      if (!tabs.some(function (t) { return t[0] === tab; })) tab = "overview";
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
      if (tab === "overview") box.innerHTML = renderOverview(f);
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
      } else if (tab === "shotlist") box.innerHTML = renderShotlist(f);
      else renderDoc(box, f.docs[tab], false);
      window.scrollTo(0, 0);
    }).catch(function () {
      app.innerHTML = '<a class="back label" href="#/">&larr; All films</a><div class="empty-state" style="margin-top:30px">This reel is missing.</div>';
    });
  }

  function route() {
    var parts = (location.hash || "#/").replace(/^#\/?/, "").split("/").filter(Boolean);
    if (parts[0] === "film" && parts[1]) renderFilm(decodeURIComponent(parts[1]), parts[2] || "overview");
    else renderIndex();
  }

  getJSON("data/site.json").then(function (s) {
    SITE = s;
    foot.innerHTML = '<span class="label">Made shot by shot</span><span class="label">' +
      (s.discord ? '<a href="' + esc(s.discord) + '" target="_blank" rel="noopener">Discord</a> &middot; ' : "") +
      (s.home_url ? '<a href="' + esc(s.home_url) + '">' + esc(s.home_url.replace(/^https?:\/\//, "").replace(/\/$/, "")) + "</a>" : "") + "</span>";
    window.addEventListener("hashchange", route);
    route();
  }).catch(function () {
    app.innerHTML = '<div class="empty-state" style="margin-top:30vh">The projector is warming up. Try again in a minute.</div>';
  });
})();
