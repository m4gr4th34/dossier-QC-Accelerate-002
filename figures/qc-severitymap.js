/*
 * qc-severitymap.js — "one code, three noise regimes" render module for Open
 * Dossier living figures (Dossier QC-Accelerate-002, Chapter 4, Fig 1).
 *
 * WHAT THIS IS
 *   The chapter's payload in one glance: the campaign's winning code
 *   (rep3 x extended-Hamming [24,4,12], w<=4, 13 qubits/logical) compared to
 *   plain budget-matched repetition across the THREE measured noise regimes.
 *   Y axis = advantage over repetition (log; up = better, 1 = even). Left
 *   panel (dirty gates, kappa1/kappa2 = 1e-3): it LOSES 12x — the deeper
 *   sibling loses 63x. Middle panel (today's hardware, Ocelot-calibrated):
 *   NOBODY WINS — both architectures drown in the unprotected bit-flip floor
 *   at ~2-5% per cycle; the contest is irrelevant. Right panel (high bias,
 *   kappa1/kappa2 = 1e-4 — the regime the search was aimed at): it WINS ~4x,
 *   with its measured 95% CI drawn. Codes must match their bias regime; the
 *   mismatch penalty is orders of magnitude, both directions.
 *
 * HARD DATA DISCIPLINE
 *   Every number is a LITERAL with a source comment naming its committed
 *   record (expedition NOTEBOOK.md / PREREG_search1.md, commits eea98d5 and
 *   0300eac). Ratios only — no absolute rates are re-derived here. The middle
 *   panel deliberately carries NO marker: at that operating point the honest
 *   statement is a regime label, not a datapoint.
 *
 * STATIC FIGURE (no animation): geometry is computed ONCE into a draw-list,
 *   consumed by BOTH the live el() emitter and the pure poster string emitter
 *   — the JS-off floor cannot drift from the JS-on ceiling.
 *
 * SUSTAINABILITY LAWS: zero deps, pure vanilla, vendored first-party;
 *   reader-side only; NEVER executed by CI.
 */
(function (root) {
  "use strict";

  var NS = root && root.DossierFigures;
  if (!NS) { if (root && root.console) root.console.error("[qc-severitymap] figures.js runtime not found — load figures.js first"); return; }
  var DossierFigures = NS;
  var el = DossierFigures.el, r2 = DossierFigures.r2,
      escAttr = DossierFigures.escAttr, escTxt = DossierFigures.escTxt,
      dedupPoster = DossierFigures.dedupPoster;

  var W = 960, H = 520;
  var COL = {
    win: "#0c8f86", lose: "#c2562f", none: "#8a8f93",
    ink: "#3a474b", axis: "#5a6b70", grid: "#d7dee0", band: "#eef1f2"
  };
  // plot frame: 3 log decades, advantage 0.01x .. 10x, 100 px/decade
  var PT = 120, PB = 420, AXX = 150;                 // plot top/bottom, axis x
  var PANELS = [
    { x0: 170, x1: 410, cx: 290 },                   // dirty gates
    { x0: 430, x1: 650, cx: 540 },                   // today's hardware
    { x0: 670, x1: 910, cx: 790 }                    // high bias (search target)
  ];
  function Y(v) { return PB - (Math.log(v / 0.01) / Math.LN10) * 100; }

  // ---- DATA (literals; source comments name the committed record) ----
  var ADV_HI  = 1 / 0.255;   // = 3.92x  [matched-depth ratio 0.255, s2_depth canonical @ eea98d5]
  var ADV_LO_CI = 1 / 0.337; // = 2.97x  [CI upper 0.337 -> advantage lower bound]
  var ADV_HI_CI = 1 / 0.172; // = 5.81x  [CI lower 0.172 -> advantage upper bound]
  var ADV_DIRTY = 1 / 12.1;  // = 0.083x [S3 L1 ratio 12.1, NOTEBOOK @ 0300eac]
  var ADV_SIB   = 1 / 62.6;  // = 0.016x [S3 L1 ratio 62.6, deeper sibling [40,4,20]]

  function compute() {
    var d = [];   // draw-list: {k:"line"|"rect"|"circle"|"diamond"|"text"|"hatch", ...}
    function ln(x1, y1, x2, y2, col, w, dash) { d.push({ k: "line", x1: x1, y1: y1, x2: x2, y2: y2, col: col, w: w || 1, dash: dash || "" }); }
    function tx(x, y, anchor, cls, fill, str) { d.push({ k: "text", x: x, y: y, a: anchor, cls: cls, fill: fill, s: str }); }
    function ci(x, y, r, fill, stroke, sw) { d.push({ k: "circle", x: x, y: y, r: r, fill: fill, stroke: stroke, sw: sw || 0 }); }

    // title
    tx(W / 2, 40, "middle", "lf-callout lf-scale-with-art", COL.ink, "ONE AI-FOUND CODE, THREE NOISE REGIMES");
    tx(W / 2, 64, "middle", "lf-tick lf-scale-with-art", COL.axis, "the searched-for regime is the only one it wins — codes must match their bias regime");

    // y axis: log advantage
    ln(AXX, PT, AXX, PB, COL.axis, 1.4);
    [[10, "10x"], [1, "even"], [0.1, "0.1x"], [0.01, "0.01x"]].forEach(function (t) {
      var y = Y(t[0]);
      ln(AXX - 6, y, AXX, y, COL.axis, 1.2);
      tx(AXX - 10, y + 4, "end", "lf-tick lf-scale-with-art", COL.axis, t[1]);
      if (t[0] !== 1) ln(AXX, y, 910, y, COL.grid, 1);
    });
    ln(AXX, Y(1), 910, Y(1), COL.axis, 1.2, "5,4");   // the even line
    tx(912, Y(1) - 6, "end", "lf-tick lf-scale-with-art", COL.axis, "even with plain repetition");
    tx(96, (PT + PB) / 2, "middle", "lf-axis lf-scale-with-art lf-yaxis-label", COL.axis, "advantage over repetition");

    // panel separators
    ln(420, PT, 420, PB, COL.grid, 1);
    ln(660, PT, 660, PB, COL.grid, 1);

    // PANEL 1 — dirty gates: LOSES
    var p = PANELS[0];
    tx(p.cx, 96, "middle", "lf-axis lf-scale-with-art", COL.lose, "LOSES 12x");
    ci(p.cx, Y(ADV_DIRTY), 8, COL.lose, "none");                    // [ratio 12.1, S3 L1 @ 0300eac]
    tx(p.cx + 16, Y(ADV_DIRTY) + 4, "start", "lf-tick lf-scale-with-art", COL.lose, "12x worse");
    ci(p.cx - 60, Y(ADV_SIB), 5, "#ffffff", COL.lose, 1.6);         // [ratio 62.6, S3 L1 @ 0300eac]
    tx(p.cx - 46, Y(ADV_SIB) + 4, "start", "lf-tick lf-scale-with-art", COL.axis, "deeper code: 63x worse");
    tx(p.cx, 452, "middle", "lf-axis lf-scale-with-art", COL.ink, "DIRTY GATES");
    tx(p.cx, 472, "middle", "lf-tick lf-scale-with-art", COL.axis, "kappa1/kappa2 = 1e-3");

    // PANEL 2 — today's hardware: NOBODY WINS (deliberately no marker)
    p = PANELS[1];
    d.push({ k: "hatch", x: p.x0 + 8, y: PT + 8, w: (p.x1 - p.x0) - 16, h: (PB - PT) - 16 });
    tx(p.cx, 96, "middle", "lf-axis lf-scale-with-art", COL.none, "NOBODY WINS");
    tx(p.cx, (PT + PB) / 2 - 10, "middle", "lf-tick lf-scale-with-art", COL.ink, "both architectures drown in the");
    tx(p.cx, (PT + PB) / 2 + 8, "middle", "lf-tick lf-scale-with-art", COL.ink, "unprotected bit-flip floor");
    tx(p.cx, (PT + PB) / 2 + 26, "middle", "lf-tick lf-scale-with-art", COL.axis, "(~2-5% per cycle; the contest is irrelevant)");  // [S3 L2 @ 0300eac]
    tx(p.cx, 452, "middle", "lf-axis lf-scale-with-art", COL.ink, "TODAY'S HARDWARE");
    tx(p.cx, 472, "middle", "lf-tick lf-scale-with-art", COL.axis, "Ocelot-calibrated, bias ~30");

    // PANEL 3 — high bias: WINS (with measured CI)
    p = PANELS[2];
    tx(p.cx, 96, "middle", "lf-axis lf-scale-with-art", COL.win, "WINS ~4x");
    ln(p.cx, Y(ADV_HI_CI), p.cx, Y(ADV_LO_CI), COL.win, 2);          // CI whisker [0.172..0.337 -> 2.97..5.81]
    ln(p.cx - 8, Y(ADV_HI_CI), p.cx + 8, Y(ADV_HI_CI), COL.win, 2);
    ln(p.cx - 8, Y(ADV_LO_CI), p.cx + 8, Y(ADV_LO_CI), COL.win, 2);
    ci(p.cx, Y(ADV_HI), 8, COL.win, "none");                         // [ratio 0.255, s2_depth @ eea98d5]
    tx(p.cx + 16, Y(ADV_HI) + 4, "start", "lf-tick lf-scale-with-art", COL.win, "3.9x better (95% CI 3.0-5.8)");
    tx(p.cx + 16, Y(ADV_HI) + 22, "start", "lf-tick lf-scale-with-art", COL.axis, "depth-matched, same instrument");
    tx(p.cx, 452, "middle", "lf-axis lf-scale-with-art", COL.ink, "HIGH BIAS — THE TARGET");
    tx(p.cx, 472, "middle", "lf-tick lf-scale-with-art", COL.axis, "kappa1/kappa2 = 1e-4");

    tx(W / 2, 504, "middle", "lf-tick lf-scale-with-art", COL.axis,
       "winner: rep3 x extended-Hamming [24,4,12], weight-4 checks, 13 qubits/logical — model-level result, not a hardware demonstration");

    return { W: W, H: H, list: d,
             ariaLabel: "The campaign's winning code compared to plain repetition across three measured noise regimes: it loses 12x under dirty gates, nobody wins at today's hardware (both drown in the bit-flip floor), and it wins about 4x at the high-bias operating point it was searched for." };
  }

  // ---- shared emitters: one draw-list, two surfaces ----
  var HATCH_ID = "qcsev-hatch";
  function hatchDefsStr() {
    return '<defs><pattern id="' + HATCH_ID + '" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">' +
           '<rect width="8" height="8" fill="' + COL.band + '"></rect>' +
           '<line x1="0" y1="0" x2="0" y2="8" stroke="#d7dee0" stroke-width="2"></line></pattern></defs>';
  }
  function itemStr(it) {
    if (it.k === "line") return '<line x1="' + r2(it.x1) + '" y1="' + r2(it.y1) + '" x2="' + r2(it.x2) + '" y2="' + r2(it.y2) + '" stroke="' + it.col + '" stroke-width="' + it.w + '"' + (it.dash ? ' stroke-dasharray="' + it.dash + '"' : "") + '></line>';
    if (it.k === "circle") return '<circle cx="' + r2(it.x) + '" cy="' + r2(it.y) + '" r="' + it.r + '" fill="' + it.fill + '"' + (it.stroke && it.stroke !== "none" ? ' stroke="' + it.stroke + '" stroke-width="' + it.sw + '"' : "") + '></circle>';
    if (it.k === "hatch") return '<rect x="' + r2(it.x) + '" y="' + r2(it.y) + '" width="' + r2(it.w) + '" height="' + r2(it.h) + '" fill="url(#' + HATCH_ID + ')" stroke="#d7dee0"></rect>';
    if (it.k === "text") {
      var tr = (it.cls.indexOf("lf-yaxis-label") >= 0) ? ' transform="rotate(-90 ' + r2(it.x) + ' ' + r2(it.y) + ')"' : "";
      return '<text class="' + it.cls + '" x="' + r2(it.x) + '" y="' + r2(it.y) + '" text-anchor="' + it.a + '" fill="' + it.fill + '"' + tr + '>' + escTxt(it.s) + '</text>';
    }
    return "";
  }
  function posterSVG(spec) {
    var g = compute();
    var s = '<svg viewBox="0 0 ' + g.W + " " + g.H + '" width="100%" class="lf-svg" role="img" aria-label="' + escAttr(g.ariaLabel) + '">';
    s += hatchDefsStr();
    for (var i = 0; i < g.list.length; i++) s += itemStr(g.list[i]);
    s += "</svg>";
    return s;
  }
  function renderQCSeverityMap(container, spec) {
    if (!container) return;
    dedupPoster(container);
    // static figure: the live view IS the sealed view (floor == ceiling by construction)
    container.insertAdjacentHTML("beforeend", posterSVG(spec));
  }

  DossierFigures.renderQCSeverityMap = renderQCSeverityMap;
  DossierFigures.renderQCSeverityMapPosterSVG = posterSVG;
  DossierFigures.registerPoster("qc-severitymap", posterSVG);
  DossierFigures.registerRenderer("qc-severitymap", renderQCSeverityMap);
})(typeof window !== "undefined" ? window : null);
