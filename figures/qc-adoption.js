/*
 * qc-adoption.js — "the loop assembles" render module for Open Dossier living
 * figures (Dossier QC-Accelerate-002, Chapter 2, Fig 2).
 *
 * WHAT THIS IS
 *   A two-lane timeline, 2014-2026, of documented milestones of AI and autonomy
 *   entering the quantum stack. Top lane "AI IN THE QUANTUM STACK", bottom lane
 *   "AUTONOMOUS LABS & ROBOTICS". Every dot is a result CITED elsewhere in this
 *   dossier; hover/focus a dot for its one-line cite (live only). One dot — the
 *   2026 A-Lab correction — is an OPEN RING linked back to the 2023 A-Lab dot: the
 *   honesty lesson drawn where it happened. A counted annotation band beneath is a
 *   bibliometric series (Lens, via qmlbib), NOT this dossier's tally. The visual
 *   argument is milestone DENSITY rising rightward.
 *
 * HARD DATA DISCIPLINE
 *   Every plotted value is a LITERAL below with a source comment naming its cite
 *   key. Milestone dots are discrete published events — NO interpolated curve, NO
 *   fabricated trajectory. The only connector is the correction link (same entity,
 *   2023->2026). Years are timeline positions; the one counted claim (the band) is
 *   quoted from qmlbib verbatim.
 *
 * THE COMPOSITION LAW (per qc-loop / qc-frontier)
 *   General primitives come from the runtime (el / r2 / escAttr / escTxt /
 *   dedupPoster / prefersReducedMotion) — never re-rolled. Geometry is computed
 *   ONCE in computeTimeline(spec) and consumed by BOTH the live el() emitter AND
 *   the pure poster string emitter, so floor == ceiling. Text is sized by ROLE via
 *   tier classes (lf-tick / lf-axis / lf-callout — runtime owns the px), NEVER a
 *   raw font-size. This figure is static (no animation); reduced motion is a no-op.
 *
 * SUSTAINABILITY LAWS: zero deps, pure vanilla, vendored first-party; reader-side
 *   only; NEVER executed by CI.
 */
(function (root) {
  "use strict";

  var NS = root && root.DossierFigures;
  if (!NS) {
    if (root && root.console) root.console.error("[qc-adoption] figures.js runtime not found — load figures.js before qc-adoption.js");
    return;
  }
  var DossierFigures = NS;
  var el = DossierFigures.el, r2 = DossierFigures.r2, escAttr = DossierFigures.escAttr,
      escTxt = DossierFigures.escTxt, dedupPoster = DossierFigures.dedupPoster;

  var W = 980, H = 400;
  var XL = 235, XR = 945, Y0 = 2014, Y1 = 2026;   // timeline pixel + year domain
  var AXIS_Y = 205, AI_Y = 165, AUT_Y = 245;
  var COL = { ai: "#2f6f8f", aut: "#0c8f86", axis: "#5a6b70", grid: "#d7dee0",
    ring: "#c2562f", faint: "#9fb0b5" };

  // ---- DATA (literals; each dot's source comment names its cite key) ----
  // AI lane. dx = per-dot x nudge so same-year dots don't overlap.
  var AI = [
    { year: 2021, name: "RL-designed gates",        cite: "baum",       dx:  0, detail: "2021 · Baum et al.: deep-RL error-robust gates designed on a real superconducting processor." },        // [baum]
    { year: 2024, name: "AlphaQubit (Nature)",      cite: "alphaqubit", dx:-28, detail: "2024 · Bausch et al.: transformer decoder beats prior art on Sycamore data (Nature)." },                  // [alphaqubit]
    { year: 2024, name: "RL code discovery",        cite: "olle",       dx: 28, detail: "2024 · Olle et al.: reinforcement learning discovers QEC codes from scratch vs Knill-Laflamme." },        // [olle]
    { year: 2025, name: "real-time decoding, d=11", cite: "alphaqubit", dx:  0, detail: "2025 · AlphaQubit successor: real-time decoding, under a microsecond per round, to distance 11." }        // [alphaqubit]
  ];
  // Autonomy lane.
  var AUT = [
    { year: 2020, name: "mobile robotic chemist",         cite: "burger",     dx:  0, detail: "2020 · Burger et al.: a mobile robot runs a days-long autonomous photocatalyst search." },              // [burger]
    { year: 2021, name: "Xiao Lai, 24/7",                 cite: "chemagents", dx:  0, detail: "2021 · USTC Xiao Lai lineage: a round-the-clock autonomous chemist (the ChemAgents lineage)." },        // [chemagents]
    { year: 2023, name: "A-Lab: 41 compounds, 17 days",   cite: "alab",       dx:  0, detail: "2023 · Szymanski et al.: the A-Lab reports 41 'novel' compounds in 17 unattended days.", anchor: true }, // [alab] — link target
    { year: 2024, name: "cryogenic wafer prober",         cite: "neyens",     dx:-28, detail: "2024 · Neyens et al.: a cryogenic 300-mm prober measures hundreds of spin-qubit devices at 1.6 K." }, // [neyens]
    { year: 2024, name: "exploratory synthesis",          cite: "burger",     dx: 28, detail: "2024 · Burger-group successors: unattended exploratory synthesis (Dai et al., Nature 635)." },          // [burger]
    { year: 2025, name: "ChemAgents (on-board LLM)",      cite: "chemagents", dx:  0, detail: "2025 · ChemAgents: a multi-agent robotic chemist on an on-board Llama-3.1-70B." },                       // [chemagents]
    { year: 2026, name: "A-Lab novelty corrected",        cite: "alab",       dx:  0, detail: "2026 · Formal correction: 'novel' meant new to the prediction platform, not necessarily to science.", ring: true, linkTo: 2023 } // [alab] — open ring, linked to 2023
  ];
  // Counted band (bibliometric; quoted from qmlbib verbatim). [qmlbib]
  var BAND = "QML literature: <50 papers/yr through 2009 · surge from 2015 · 9,493 cumulative by 2023 (Lens)";

  function xForYear(y) { return XL + (y - Y0) / (Y1 - Y0) * (XR - XL); }

  // ===== SHARED COMPUTE =====
  function computeTimeline() {
    function place(list, laneY) {
      return list.map(function (d) {
        return { x: r2(xForYear(d.year) + d.dx), y: laneY, year: d.year, name: d.name,
          cite: d.cite, detail: d.detail, ring: !!d.ring, anchor: !!d.anchor, linkTo: d.linkTo };
      });
    }
    var ai = place(AI, AI_Y), aut = place(AUT, AUT_Y);
    // correction link: from the 2026 ring back to the 2023 anchor (same lane)
    var link = null;
    var ringDot = aut.filter(function (d) { return d.ring; })[0];
    if (ringDot && ringDot.linkTo != null) {
      var tgt = aut.filter(function (d) { return d.year === ringDot.linkTo && d.anchor; })[0];
      if (tgt) link = { x1: ringDot.x, x2: tgt.x, y: AUT_Y, dip: AUT_Y + 40 };
    }
    var ticks = [];
    for (var y = Y0; y <= Y1; y += 2) ticks.push({ x: r2(xForYear(y)), label: String(y) });
    return { W: W, H: H, ai: ai, aut: aut, link: link, ticks: ticks, band: BAND,
      ariaLabel: "A two-lane timeline from 2014 to 2026 of documented milestones of AI and of autonomous labs and robotics entering the quantum-computing stack; the dots grow denser toward the right, and a 2026 open ring marks the A-Lab correction linked back to its 2023 result." };
  }

  function fail(container, msg) {
    if (root && root.console) root.console.error("[qc-adoption] " + msg);
    if (container && container.appendChild) {
      var doc = (root && root.document) || container.ownerDocument;
      var p = doc.createElement("p"); p.className = "lf-fallback";
      p.textContent = "Figure unavailable: " + msg; container.appendChild(p);
    }
    return null;
  }

  // ===== LIVE =====
  function renderQCAdoption(container, spec) {
    if (!container) return fail(null, "no container");
    var doc = (root && root.document) || container.ownerDocument;
    if (spec == null && container.getAttribute) spec = container.getAttribute("data-figure");
    if (typeof spec === "string") { try { spec = JSON.parse(spec); } catch (e) { return fail(container, "data-figure is not valid JSON"); } }

    dedupPoster(container);
    var g = computeTimeline();

    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, width: "100%", "class": "lf-svg",
      role: "img", "aria-label": g.ariaLabel });
    var defs = el("defs", {});
    var mk = el("marker", { id: "adopt-arr", viewBox: "0 0 10 10", refX: "8", refY: "5", markerWidth: "7", markerHeight: "7", orient: "auto-start-reverse" });
    mk.appendChild(el("path", { d: "M0 1L9 5L0 9z", fill: COL.ring })); defs.appendChild(mk); svg.appendChild(defs);

    // lane headers
    svg.appendChild(txt(XL, AI_Y - 40, "start", "lf-callout", COL.ai, "AI IN THE QUANTUM STACK"));
    svg.appendChild(txt(XL, AUT_Y + 52, "start", "lf-callout", COL.aut, "AUTONOMOUS LABS & ROBOTICS"));

    // timeline axis + year ticks
    svg.appendChild(el("line", { x1: XL, y1: AXIS_Y, x2: XR, y2: AXIS_Y, stroke: COL.axis, "stroke-width": "1.5" }));
    g.ticks.forEach(function (t) {
      svg.appendChild(el("line", { x1: t.x, y1: AXIS_Y - 4, x2: t.x, y2: AXIS_Y + 4, stroke: COL.axis, "stroke-width": "1" }));
      svg.appendChild(txt(t.x, AXIS_Y + 18, "middle", "lf-tick", COL.axis, t.label));
    });

    // correction link (drawn behind the dots)
    if (g.link) {
      var d = "M" + g.link.x1 + " " + g.link.y + " Q" + r2((g.link.x1 + g.link.x2) / 2) + " " + g.link.dip + " " + g.link.x2 + " " + g.link.y;
      svg.appendChild(el("path", { d: d, fill: "none", stroke: COL.ring, "stroke-width": "1.4", "stroke-dasharray": "4 3", "marker-end": "url(#adopt-arr)" }));
    }

    var readout = doc.createElement("span"); readout.className = "lf-readout"; readout.setAttribute("aria-live", "polite");
    var HINT = "Hover a milestone for its citation. Dots grow denser toward the right — the loop assembling.";

    function drawLane(dots, laneY, above) {
      dots.forEach(function (dd) {
        // stem to axis
        svg.appendChild(el("line", { x1: dd.x, y1: dd.y, x2: dd.x, y2: AXIS_Y, stroke: COL.grid, "stroke-width": "1" }));
        // dot (open ring for the correction)
        var dot = dd.ring
          ? el("circle", { cx: dd.x, cy: dd.y, r: "6", fill: "none", stroke: COL.ring, "stroke-width": "2.5" })
          : el("circle", { cx: dd.x, cy: dd.y, r: "5.5", fill: above ? COL.ai : COL.aut, stroke: "#fff", "stroke-width": "1.5" });
        attachDetail(dot, dd.detail);
        svg.appendChild(dot);
        // rotated label
        var ly = above ? dd.y - 9 : dd.y + 13;
        var rot = above ? -30 : 30;
        var lab = txt(dd.x + 3, ly, "start", "lf-axis", dd.ring ? COL.ring : COL.axis, dd.name);
        lab.setAttribute("transform", "rotate(" + rot + " " + (dd.x + 3) + " " + ly + ")");
        attachDetail(lab, dd.detail);
        svg.appendChild(lab);
      });
    }
    function attachDetail(node, detail) {
      node.setAttribute("tabindex", "0"); node.setAttribute("role", "img"); node.setAttribute("aria-label", detail);
      node.style.cursor = "pointer";
      var show = function () { readout.textContent = detail; };
      var clear = function () { readout.textContent = HINT; };
      node.addEventListener("mouseenter", show); node.addEventListener("mouseleave", clear);
      node.addEventListener("focus", show); node.addEventListener("blur", clear); node.addEventListener("click", show);
    }

    drawLane(g.ai, AI_Y, true);
    drawLane(g.aut, AUT_Y, false);

    // counted band (bibliometric)
    svg.appendChild(txt(XL, 378, "start", "lf-tick", COL.axis, g.band));

    container.appendChild(svg);
    var controls = doc.createElement("div"); controls.className = "lf-controls";
    var resetBtn = doc.createElement("button"); resetBtn.type = "button"; resetBtn.className = "lf-btn"; resetBtn.textContent = "Reset";
    resetBtn.addEventListener("click", function () { readout.textContent = HINT; });
    controls.appendChild(resetBtn); controls.appendChild(readout);
    container.appendChild(controls);
    readout.textContent = HINT;

    var handle = {
      runtimeVersion: DossierFigures.FIGURES_RUNTIME_VERSION,
      getState: function () { return { view: "timeline" }; },
      reset: function () { readout.textContent = HINT; }
    };
    container.__lfHandle = handle;
    return handle;

    function txt(x, y, anchor, cls, fill, str) {
      var t = el("text", { x: x, y: y, "text-anchor": anchor, fill: fill, "class": cls }); t.textContent = str; return t;
    }
  }

  // ===== POSTER (pure string; full static view) =====
  function renderQCAdoptionPosterSVG() {
    var g = computeTimeline();
    var s = '<svg viewBox="0 0 ' + W + ' ' + H + '" width="100%" class="lf-svg" role="img" aria-label="' + escAttr(g.ariaLabel) + '">';
    s += '<defs><marker id="adopt-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1L9 5L0 9z" fill="' + COL.ring + '"></path></marker></defs>';
    s += textS(XL, AI_Y - 40, "start", "lf-callout", COL.ai, "AI IN THE QUANTUM STACK");
    s += textS(XL, AUT_Y + 52, "start", "lf-callout", COL.aut, "AUTONOMOUS LABS & ROBOTICS");
    s += '<line x1="' + XL + '" y1="' + AXIS_Y + '" x2="' + XR + '" y2="' + AXIS_Y + '" stroke="' + COL.axis + '" stroke-width="1.5"></line>';
    g.ticks.forEach(function (t) {
      s += '<line x1="' + t.x + '" y1="' + (AXIS_Y - 4) + '" x2="' + t.x + '" y2="' + (AXIS_Y + 4) + '" stroke="' + COL.axis + '" stroke-width="1"></line>';
      s += textS(t.x, AXIS_Y + 18, "middle", "lf-tick", COL.axis, t.label);
    });
    if (g.link) {
      var d = "M" + g.link.x1 + " " + g.link.y + " Q" + r2((g.link.x1 + g.link.x2) / 2) + " " + g.link.dip + " " + g.link.x2 + " " + g.link.y;
      s += '<path d="' + d + '" fill="none" stroke="' + COL.ring + '" stroke-width="1.4" stroke-dasharray="4 3" marker-end="url(#adopt-arr)"></path>';
    }
    s += laneS(g.ai, true) + laneS(g.aut, false);
    s += textS(XL, 378, "start", "lf-tick", COL.axis, g.band);
    s += '</svg>';
    return s;
  }
  function laneS(dots, above) {
    var s = "";
    dots.forEach(function (dd) {
      s += '<line x1="' + dd.x + '" y1="' + dd.y + '" x2="' + dd.x + '" y2="' + AXIS_Y + '" stroke="' + COL.grid + '" stroke-width="1"></line>';
      s += dd.ring
        ? '<circle cx="' + dd.x + '" cy="' + dd.y + '" r="6" fill="none" stroke="' + COL.ring + '" stroke-width="2.5"></circle>'
        : '<circle cx="' + dd.x + '" cy="' + dd.y + '" r="5.5" fill="' + (above ? COL.ai : COL.aut) + '" stroke="#fff" stroke-width="1.5"></circle>';
      var ly = above ? dd.y - 9 : dd.y + 13, rot = above ? -30 : 30, lx = dd.x + 3;
      s += '<text class="lf-axis" x="' + lx + '" y="' + ly + '" text-anchor="start" fill="' + (dd.ring ? COL.ring : COL.axis) + '" transform="rotate(' + rot + ' ' + lx + ' ' + ly + ')">' + escTxt(dd.name) + '</text>';
    });
    return s;
  }
  function textS(x, y, anchor, cls, fill, str) { return '<text class="' + cls + '" x="' + r2(x) + '" y="' + r2(y) + '" text-anchor="' + anchor + '" fill="' + fill + '">' + escTxt(str) + '</text>'; }

  DossierFigures.renderQCAdoption = renderQCAdoption;
  DossierFigures.renderQCAdoptionPosterSVG = renderQCAdoptionPosterSVG;
  DossierFigures.registerPoster("qc-adoption", renderQCAdoptionPosterSVG);
  DossierFigures.registerRenderer("qc-adoption", renderQCAdoption);
})(typeof window !== "undefined" ? window : null);
