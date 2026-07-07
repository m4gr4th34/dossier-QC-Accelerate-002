/*
 * qc-scoreboard.js — "the scoreboard" render module for Open Dossier living
 * figures (Dossier QC-Accelerate-002, Chapter 3, Fig 1).
 *
 * WHAT THIS IS
 *   Five platform lanes on one time axis, each lane DRAWN AT ITS EVIDENCE GRADE
 *   (solid = peer-reviewed floor, dashed = preprint/company floor, dotted =
 *   contested), carrying its dated ENTRY (up triangle) and EXIT (down triangle)
 *   signposts from this chapter's portfolio cards. Beneath the axis: the
 *   chapter's own bets as diamonds at their resolution dates, percent attached.
 *   A left GATED RAIL holds the two honestly undated items (Majorana's
 *   evidence-gated entry; the conditional venue bet). EVERY marker is HOLLOW in
 *   this edition — the figure exists to be filled by later editions (hit =
 *   filled green, miss = filled coral; states live in this module's STATE map).
 *
 * HARD DATA DISCIPLINE
 *   Every date, criterion, and percentage below is a LITERAL with a source
 *   comment naming its avenues.json card. No measured data; no interpolation.
 *   The NOW line is this edition's date. Dates are decimal years (Dec 31 ->
 *   .99 of the same year, so a deadline never renders inside the next year).
 *
 * LAYOUT (collision-free by construction)
 *   Entry labels pack upward above their lane, exit labels downward below it,
 *   horizontal text, exact-bbox greedy tiering (same pack as qc-adoption).
 *   Live el() emitter and pure poster string emitter read ONE geometry.
 *
 * SUSTAINABILITY LAWS: zero deps, pure vanilla, vendored first-party; reader-side only.
 */
(function (root) {
  "use strict";

  var NS = root && root.DossierFigures;
  if (!NS) { if (root && root.console) root.console.error("[qc-scoreboard] figures.js runtime not found — load figures.js before qc-scoreboard.js"); return; }
  var DossierFigures = NS;
  var el = DossierFigures.el, r2 = DossierFigures.r2, escAttr = DossierFigures.escAttr,
      escTxt = DossierFigures.escTxt, dedupPoster = DossierFigures.dedupPoster;

  var XL = 208, XR = 942;                 // plot range (left rail holds platform names + gated items)
  var LANE0 = 128, LANE_DY = 58;          // first lane y, lane spacing
  var CW = 6.6, FH = 15, STEP = 15;       // label metrics for the bbox pack
  var COL = {
    atoms: "#0c8f86", ions: "#2f6f8f", sc: "#7a5ca8", bosonic: "#b06e2a", majorana: "#8a8f93",
    axis: "#5a6b70", grid: "#d7dee0", exit: "#c2562f", ink: "#3a474b", bet: "#3a474b"
  };
  var NOW = 2026.52;                      // this edition: July 2026
  var DMIN = 2026.35, DMAX = 2033.4;      // domain: now .. past the farthest bet (2032.99)
  function X(t) { return XL + (t - DMIN) / (DMAX - DMIN) * (XR - XL); }

  // ---- DATA (literals; each marker's source comment names its avenues.json card) ----
  // grade: "peer" (solid) | "pre" (dashed) | "contested" (dotted)
  var LANES = [
    { key: "atoms", name: "NEUTRAL ATOMS", grade: "peer", gradeTxt: "peer-reviewed floor", col: COL.atoms,
      entries: [
        { t: 2027.50, name: "Magne >=40 LQ",  detail: "ENTRY · Portfolio: neutral atoms — Magne customer-operational at 40+ logical qubits by 2027-06-30. UNSCORED — hollow until a later edition fills it." },   // [card: Portfolio: neutral atoms — ENTRY A]
        { t: 2027.99, name: "any >=100 LQ",   detail: "ENTRY · Portfolio: neutral atoms — any neutral-atom system at 100+ logical qubits by 2027-12-31. UNSCORED." } ],                                                  // [card: Portfolio: neutral atoms — ENTRY B]
      exits: [
        { t: 2028.99, name: "neither", detail: "EXIT · Portfolio: neutral atoms — neither entry met by 2028-12-31: the disconfirming door. UNSCORED." } ] },                                                             // [card: Portfolio: neutral atoms — EXIT]
    { key: "ions", name: "TRAPPED IONS", grade: "pre", gradeTxt: "preprint / company floor", col: COL.ions,
      entries: [
        { t: 2027.50, name: "peer-pub + 256q", detail: "ENTRY · Portfolio: trapped ions — the iceberg 94/48 result peer-published AND the promised 256-qubit system demonstrated, both by 2027-06-30. UNSCORED." } ],     // [card: Portfolio: trapped ions — ENTRY]
      exits: [
        { t: 2028.99, name: "prototype-only", detail: "EXIT · Portfolio: trapped ions — four-nines fidelity still confined to R&D prototypes (no customer system) by 2028-12-31. UNSCORED." } ] },                        // [card: Portfolio: trapped ions — EXIT]
    { key: "sc", name: "SUPERCONDUCTING", grade: "peer", gradeTxt: "peer-reviewed floor", col: COL.sc,
      entries: [
        { t: 2027.99, name: "d>=9 / 1e-5 mem", detail: "ENTRY · Portfolio: superconducting — a peer-reviewed below-threshold result at distance 9+, or a logical memory at 1e-5 error, by 2027-12-31. UNSCORED." } ],     // [card: Portfolio: superconducting — ENTRY]
      exits: [
        { t: 2028.99, name: "no advance", detail: "EXIT · Portfolio: superconducting — no larger-distance below-threshold result anywhere by 2028-12-31. UNSCORED." } ] },                                               // [card: Portfolio: superconducting — EXIT]
    { key: "bosonic", name: "BOSONIC (CAT)", grade: "peer", gradeTxt: "peer-reviewed floor", col: COL.bosonic,
      entries: [
        { t: 2028.99, name: "logical ops", detail: "ENTRY · Portfolio: bosonic — a multi-logical-qubit bosonic device demonstrating logical OPERATIONS (not just memory) beyond break-even by 2028-12-31. UNSCORED." } ], // [card: Portfolio: bosonic — ENTRY]
      exits: [
        { t: 2029.99, name: "single-digit", detail: "EXIT · Portfolio: bosonic — cat/GKP scaling still single-digit by 2029-12-31. UNSCORED." } ] },                                                                     // [card: Portfolio: bosonic — EXIT]
    { key: "majorana", name: "MAJORANA", grade: "contested", gradeTxt: "contested signal", col: COL.majorana,
      entries: [], exits: [],
      gated: { name: "evidence-gated", detail: "GATED · Portfolio: Majorana — ENTRY only on independent reproduction resolving the published critique; no date can be honest. The EXIT flag is already armed, unchanged from Chapter 2." } } // [card: Portfolio: Majorana]
  ];
  var BETS = [
    { t: 2027.01, pct: 55, name: "NQI reauthorized",  detail: "BET · The reauthorization clock — 55% that NQI reauthorization is enacted by 2027-01-03, the end of the 119th Congress. UNSCORED." },                      // [card: The reauthorization clock]
    { t: 2028.99, pct: 35, name: "loop layer funded", detail: "BET · The loop layer at the park — 35% that loop infrastructure is funded as a named deliverable at IQMP or an equivalent allied site by 2028-12-31. UNSCORED." }, // [card: The loop layer at the park]
    { t: 2030.99, pct: 55, name: "defect loop demo",  detail: "BET · The defect loop, demonstrated — 55% that a published, independently verifiable autonomous loop iterates a defect-qubit figure of merit over 3+ unattended cycles by 2030-12-31. UNSCORED." }, // [card: The defect loop, demonstrated]
    { t: 2032.99, pct: 35, name: "incumbent adopts",  detail: "BET · The loop feeds the incumbent — 35% that a loop-discovered materials improvement is adopted, credited, on a flagship superconducting chip by 2032-12-31. UNSCORED." } // [card: The loop feeds the incumbent]
  ];
  var GATED_BET = { pct: 60, name: "venue 60% (cond.)", detail: "BET · First to loop, the venue — conditional on Chapter 2's loop bet resolving true: 60% the first venue is defect/materials qubits. Undated by construction; scored when and if that bet resolves." }; // [card: First to loop — the venue]
  // STATE map — this edition everything is "unscored"; a later edition flips
  // entries here to "hit" / "miss" and the fill colors follow. [scored in later editions]
  var STATE = {};  // e.g. STATE["atoms/2027.5"] = "hit";
  var FILL = { hit: "#2f8f5b", miss: "#c2562f" };

  function dashFor(grade) { return grade === "peer" ? null : (grade === "pre" ? "7 5" : "2 5"); }

  // ---- exact bbox of horizontal text anchored middle at (x,y) ----
  function bbox(x, y, w) { return { x0: x - w / 2, x1: x + w / 2, y0: y - FH, y1: y }; }
  function hit(a, b) { return a.x0 < b.x1 && b.x0 < a.x1 && a.y0 < b.y1 && b.y0 < a.y1; }

  // ===== SHARED COMPUTE =====
  function compute() {
    var boxes = [], lanes = [], i;
    for (i = 0; i < LANES.length; i++) {
      var L = LANES[i], y = LANE0 + i * LANE_DY, marks = [];
      L.entries.forEach(function (e) {
        var x = r2(X(e.t)), w = e.name.length * CW, ly = y - 16, bb = bbox(x, ly, w);
        while (boxes.some(function (o) { return hit(bb, o); })) { ly -= STEP; bb = bbox(x, ly, w); }
        boxes.push(bb);
        marks.push({ kind: "entry", x: x, y: y, lx: x, ly: r2(ly), name: e.name, detail: e.detail, col: L.col, state: STATE[L.key + "/" + e.t] || "unscored" });
      });
      L.exits.forEach(function (e) {
        var x = r2(X(e.t)), w = e.name.length * CW, ly = y + 30, bb = bbox(x, ly, w);
        while (boxes.some(function (o) { return hit(bb, o); })) { ly += STEP; bb = bbox(x, ly, w); }
        boxes.push(bb);
        marks.push({ kind: "exit", x: x, y: y, lx: x, ly: r2(ly), name: e.name, detail: e.detail, col: COL.exit, state: STATE[L.key + "/x" + e.t] || "unscored" });
      });
      lanes.push({ key: L.key, name: L.name, gradeTxt: L.gradeTxt, col: L.col, y: y, dash: dashFor(L.grade), marks: marks, gated: L.gated || null });
    }
    var axisY = LANE0 + LANES.length * LANE_DY + 6;
    var bets = BETS.map(function (b) {
      var x = r2(X(b.t)), w = (b.pct + "% " + b.name).length * CW, ly = axisY + 58, bb = bbox(x, ly, w);
      while (boxes.some(function (o) { return hit(bb, o); })) { ly += STEP; bb = bbox(x, ly, w); }
      boxes.push(bb);
      return { x: x, y: axisY + 34, lx: x, ly: r2(ly), pct: b.pct, name: b.name, detail: b.detail };
    });
    var ticks = [];
    for (var yr = 2027; yr <= 2033; yr++) ticks.push({ x: r2(X(yr)), label: String(yr) });
    var H = Math.ceil(Math.max.apply(null, boxes.map(function (b) { return b.y1; }).concat([axisY + 80])) + 16);
    return { W: 960, H: H, lanes: lanes, bets: bets, ticks: ticks, axisY: axisY, nowX: r2(X(NOW)),
      ariaLabel: "A scoreboard: five quantum-platform lanes on one time axis from mid-2026 to 2033, each lane drawn at its evidence grade (solid for peer-reviewed, dashed for preprint or company sources, dotted for contested), carrying hollow up-triangle entry signposts and down-triangle exit signposts at their dated deadlines; a left rail holds the two honestly undated, evidence-gated items; beneath the axis, four hollow diamonds mark the chapter's own probability bets at their resolution dates. Every marker is hollow: unscored in this edition, to be filled by later ones." };
  }

  // ---- marker path helpers (shared literals) ----
  function triUp(x, y)   { return "M" + r2(x) + " " + r2(y - 8) + " L" + r2(x + 7.5) + " " + r2(y + 5) + " L" + r2(x - 7.5) + " " + r2(y + 5) + " Z"; }
  function triDown(x, y) { return "M" + r2(x) + " " + r2(y + 8) + " L" + r2(x + 7.5) + " " + r2(y - 5) + " L" + r2(x - 7.5) + " " + r2(y - 5) + " Z"; }
  function diamond(x, y) { return "M" + r2(x) + " " + r2(y - 8) + " L" + r2(x + 7) + " " + r2(y) + " L" + r2(x) + " " + r2(y + 8) + " L" + r2(x - 7) + " " + r2(y) + " Z"; }
  function fillFor(state) { return state === "hit" ? FILL.hit : state === "miss" ? FILL.miss : "#ffffff"; }

  function fail(container, msg) {
    if (root && root.console) root.console.error("[qc-scoreboard] " + msg);
    if (container && container.appendChild) {
      var doc = (root && root.document) || container.ownerDocument;
      var p = doc.createElement("p"); p.className = "lf-fallback"; p.textContent = "Figure unavailable: " + msg; container.appendChild(p);
    }
    return null;
  }

  // ===== LIVE =====
  function renderQCScoreboard(container, spec) {
    if (!container) return fail(null, "no container");
    var doc = (root && root.document) || container.ownerDocument;
    if (spec == null && container.getAttribute) spec = container.getAttribute("data-figure");
    if (typeof spec === "string") { try { spec = JSON.parse(spec); } catch (e) { return fail(container, "data-figure is not valid JSON"); } }

    dedupPoster(container);
    var g = compute();
    var svg = el("svg", { viewBox: "0 0 " + g.W + " " + g.H, width: "100%", "class": "lf-svg", role: "img", "aria-label": g.ariaLabel });

    // legend (top-left)
    svg.appendChild(el("path", { d: triUp(20, 24), fill: "#fff", stroke: COL.ink, "stroke-width": "2" }));
    svg.appendChild(txt(34, 28, "start", "lf-tick lf-scale-with-art", COL.axis, "ENTRY signpost"));
    svg.appendChild(el("path", { d: triDown(150, 24), fill: "#fff", stroke: COL.exit, "stroke-width": "2" }));
    svg.appendChild(txt(164, 28, "start", "lf-tick lf-scale-with-art", COL.axis, "EXIT signpost"));
    svg.appendChild(el("path", { d: diamond(276, 24), fill: "#fff", stroke: COL.bet, "stroke-width": "2" }));
    svg.appendChild(txt(290, 28, "start", "lf-tick lf-scale-with-art", COL.axis, "the chapter's bet"));
    svg.appendChild(txt(20, 52, "start", "lf-tick lf-scale-with-art", COL.axis, "hollow = unscored (this edition) · filled = scored by a later one"));
    svg.appendChild(txt(20, 70, "start", "lf-tick lf-scale-with-art", COL.axis, "lane stroke = evidence grade: solid peer-reviewed · dashed preprint/company · dotted contested"));

    drawInto(svg, g, doc, true);

    container.appendChild(svg);
    var controls = doc.createElement("div"); controls.className = "lf-controls";
    var readout = doc.createElement("span"); readout.className = "lf-readout"; readout.setAttribute("aria-live", "polite");
    var HINT = "Hover a marker for its criterion, deadline, and card. Everything is hollow: this edition places the bets; later editions fill them in.";
    var resetBtn = doc.createElement("button"); resetBtn.type = "button"; resetBtn.className = "lf-btn"; resetBtn.textContent = "Reset";
    resetBtn.addEventListener("click", function () { readout.textContent = HINT; });
    controls.appendChild(resetBtn); controls.appendChild(readout); container.appendChild(controls);
    readout.textContent = HINT;
    svg.__readout = readout; svg.__hint = HINT;

    // wire details (live only)
    Array.prototype.forEach.call(svg.querySelectorAll("[data-detail]"), function (node) {
      var detail = node.getAttribute("data-detail");
      node.setAttribute("tabindex", "0"); node.setAttribute("role", "img"); node.setAttribute("aria-label", detail); node.style.cursor = "pointer";
      var show = function () { readout.textContent = detail; }, clear = function () { readout.textContent = HINT; };
      node.addEventListener("mouseenter", show); node.addEventListener("mouseleave", clear);
      node.addEventListener("focus", show); node.addEventListener("blur", clear); node.addEventListener("click", show);
    });

    var handle = { runtimeVersion: DossierFigures.FIGURES_RUNTIME_VERSION, getState: function () { return { view: "scoreboard" }; }, reset: function () { readout.textContent = HINT; } };
    container.__lfHandle = handle;
    return handle;

    function txt(x, y, anchor, cls, fill, str) { var t = el("text", { x: x, y: y, "text-anchor": anchor, fill: fill, "class": cls }); t.textContent = str; return t; }
  }

  // shared draw (live DOM): lanes, rail, markers, axis, bets — mirrors the poster exactly
  function drawInto(svg, g, doc, live) {
    function txt(x, y, anchor, cls, fill, str) { var t = el("text", { x: x, y: y, "text-anchor": anchor, fill: fill, "class": cls }); t.textContent = str; return t; }
    // NOW line
    svg.appendChild(el("line", { x1: g.nowX, y1: 92, x2: g.nowX, y2: g.axisY + 46, stroke: COL.axis, "stroke-width": "1", "stroke-dasharray": "3 3" }));
    svg.appendChild(txt(g.nowX, 86, "middle", "lf-tick lf-scale-with-art", COL.axis, "this edition · Jul 2026"));
    g.lanes.forEach(function (L) {
      var lane = el("line", { x1: XL, y1: L.y, x2: XR, y2: L.y, stroke: L.col, "stroke-width": "2", "stroke-opacity": L.dash === "2 5" ? "0.65" : "0.9" });
      if (L.dash) lane.setAttribute("stroke-dasharray", L.dash);
      svg.appendChild(lane);
      svg.appendChild(txt(XL - 12, L.y - 2, "end", "lf-axis lf-scale-with-art", L.col, L.name));
      svg.appendChild(txt(XL - 12, L.y + 14, "end", "lf-tick lf-scale-with-art", COL.axis, L.gradeTxt));
      if (L.gated) {
        var gp = el("path", { d: diamond(XL + 16, L.y), fill: "#fff", stroke: L.col, "stroke-width": "2", "data-detail": L.gated.detail });
        svg.appendChild(gp);
        svg.appendChild(txt(XL + 30, L.y + 4, "start", "lf-tick lf-scale-with-art", L.col, L.gated.name + " · EXIT armed"));
      }
      L.marks.forEach(function (m) {
        svg.appendChild(el("line", { x1: m.x, y1: m.kind === "entry" ? m.ly + 3 : m.y + 8, x2: m.x, y2: m.kind === "entry" ? m.y - 8 : m.ly - FH + 3, stroke: COL.grid, "stroke-width": "1" }));
        var p = el("path", { d: m.kind === "entry" ? triUp(m.x, m.y) : triDown(m.x, m.y), fill: fillFor(m.state), stroke: m.col, "stroke-width": "2.2", "data-detail": m.detail });
        svg.appendChild(p);
        svg.appendChild(txt(m.lx, m.ly, "middle", "lf-tick lf-scale-with-art", m.kind === "entry" ? m.col : COL.exit, m.name));
      });
    });
    // axis
    svg.appendChild(el("line", { x1: XL, y1: g.axisY, x2: XR, y2: g.axisY, stroke: COL.axis, "stroke-width": "1.5" }));
    g.ticks.forEach(function (t) {
      svg.appendChild(el("line", { x1: t.x, y1: g.axisY - 4, x2: t.x, y2: g.axisY + 4, stroke: COL.axis, "stroke-width": "1" }));
      svg.appendChild(txt(t.x, g.axisY + 18, "middle", "lf-tick lf-scale-with-art", COL.axis, t.label));
    });
    // bets band
    svg.appendChild(txt(XL - 12, g.axisY + 40, "end", "lf-axis lf-scale-with-art", COL.bet, "THE BETS"));
    var gb = el("path", { d: diamond(XL + 16, g.axisY + 34), fill: "#fff", stroke: COL.bet, "stroke-width": "2", "data-detail": GATED_BET.detail });
    svg.appendChild(gb);
    svg.appendChild(txt(XL + 30, g.axisY + 38, "start", "lf-tick lf-scale-with-art", COL.bet, GATED_BET.name));
    g.bets.forEach(function (b) {
      svg.appendChild(el("line", { x1: b.x, y1: g.axisY + 6, x2: b.x, y2: b.y - 8, stroke: COL.grid, "stroke-width": "1" }));
      var p = el("path", { d: diamond(b.x, b.y), fill: "#fff", stroke: COL.bet, "stroke-width": "2.2", "data-detail": b.detail });
      svg.appendChild(p);
      svg.appendChild(txt(b.lx, b.ly, "middle", "lf-tick lf-scale-with-art", COL.bet, b.pct + "% " + b.name));
    });
  }

  // ===== POSTER (pure string; identical geometry) =====
  function renderQCScoreboardPosterSVG() {
    var g = compute(), s = '<svg viewBox="0 0 ' + g.W + ' ' + g.H + '" width="100%" class="lf-svg" role="img" aria-label="' + escAttr(g.ariaLabel) + '">';
    s += '<path d="' + triUp(20, 24) + '" fill="#fff" stroke="' + COL.ink + '" stroke-width="2"></path>' + tS(34, 28, "start", COL.axis, "ENTRY signpost");
    s += '<path d="' + triDown(150, 24) + '" fill="#fff" stroke="' + COL.exit + '" stroke-width="2"></path>' + tS(164, 28, "start", COL.axis, "EXIT signpost");
    s += '<path d="' + diamond(276, 24) + '" fill="#fff" stroke="' + COL.bet + '" stroke-width="2"></path>' + tS(290, 28, "start", COL.axis, "the chapter's bet");
    s += tS(20, 52, "start", COL.axis, "hollow = unscored (this edition) · filled = scored by a later one");
    s += tS(20, 70, "start", COL.axis, "lane stroke = evidence grade: solid peer-reviewed · dashed preprint/company · dotted contested");
    s += '<line x1="' + g.nowX + '" y1="92" x2="' + g.nowX + '" y2="' + (g.axisY + 46) + '" stroke="' + COL.axis + '" stroke-width="1" stroke-dasharray="3 3"></line>';
    s += tS(g.nowX, 86, "middle", COL.axis, "this edition · Jul 2026");
    g.lanes.forEach(function (L) {
      s += '<line x1="' + XL + '" y1="' + L.y + '" x2="' + XR + '" y2="' + L.y + '" stroke="' + L.col + '" stroke-width="2" stroke-opacity="' + (L.dash === "2 5" ? "0.65" : "0.9") + '"' + (L.dash ? ' stroke-dasharray="' + L.dash + '"' : "") + '></line>';
      s += aS(XL - 12, L.y - 2, "end", L.col, L.name) + tS(XL - 12, L.y + 14, "end", COL.axis, L.gradeTxt);
      if (L.gated) s += '<path d="' + diamond(XL + 16, L.y) + '" fill="#fff" stroke="' + L.col + '" stroke-width="2"></path>' + tS(XL + 30, L.y + 4, "start", L.col, L.gated.name + " · EXIT armed");
      L.marks.forEach(function (m) {
        s += '<line x1="' + m.x + '" y1="' + r2(m.kind === "entry" ? m.ly + 3 : m.y + 8) + '" x2="' + m.x + '" y2="' + r2(m.kind === "entry" ? m.y - 8 : m.ly - FH + 3) + '" stroke="' + COL.grid + '" stroke-width="1"></line>';
        s += '<path d="' + (m.kind === "entry" ? triUp(m.x, m.y) : triDown(m.x, m.y)) + '" fill="' + fillFor(m.state) + '" stroke="' + m.col + '" stroke-width="2.2"></path>';
        s += tS(m.lx, m.ly, "middle", m.kind === "entry" ? m.col : COL.exit, m.name);
      });
    });
    s += '<line x1="' + XL + '" y1="' + g.axisY + '" x2="' + XR + '" y2="' + g.axisY + '" stroke="' + COL.axis + '" stroke-width="1.5"></line>';
    g.ticks.forEach(function (t) {
      s += '<line x1="' + t.x + '" y1="' + (g.axisY - 4) + '" x2="' + t.x + '" y2="' + (g.axisY + 4) + '" stroke="' + COL.axis + '" stroke-width="1"></line>' + tS(t.x, g.axisY + 18, "middle", COL.axis, t.label);
    });
    s += aS(XL - 12, g.axisY + 40, "end", COL.bet, "THE BETS");
    s += '<path d="' + diamond(XL + 16, g.axisY + 34) + '" fill="#fff" stroke="' + COL.bet + '" stroke-width="2"></path>' + tS(XL + 30, g.axisY + 38, "start", COL.bet, GATED_BET.name);
    g.bets.forEach(function (b) {
      s += '<line x1="' + b.x + '" y1="' + (g.axisY + 6) + '" x2="' + b.x + '" y2="' + r2(b.y - 8) + '" stroke="' + COL.grid + '" stroke-width="1"></line>';
      s += '<path d="' + diamond(b.x, b.y) + '" fill="#fff" stroke="' + COL.bet + '" stroke-width="2.2"></path>' + tS(b.lx, b.ly, "middle", COL.bet, b.pct + "% " + b.name);
    });
    s += '</svg>';
    return s;
    function tS(x, y, anchor, fill, str) { return '<text class="lf-tick lf-scale-with-art" x="' + r2(x) + '" y="' + r2(y) + '" text-anchor="' + anchor + '" fill="' + fill + '">' + escTxt(str) + '</text>'; }
    function aS(x, y, anchor, fill, str) { return '<text class="lf-axis lf-scale-with-art" x="' + r2(x) + '" y="' + r2(y) + '" text-anchor="' + anchor + '" fill="' + fill + '">' + escTxt(str) + '</text>'; }
  }

  DossierFigures.renderQCScoreboard = renderQCScoreboard;
  DossierFigures.renderQCScoreboardPosterSVG = renderQCScoreboardPosterSVG;
  DossierFigures.registerPoster("qc-scoreboard", renderQCScoreboardPosterSVG);
  DossierFigures.registerRenderer("qc-scoreboard", renderQCScoreboard);
})(typeof window !== "undefined" ? window : null);
