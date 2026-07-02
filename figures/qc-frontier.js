/*
 * qc-frontier.js — "the kept negative" render module for Open Dossier living
 * figures (Dossier QC-Accelerate-002, Chapter 1).
 *
 * WHAT THIS IS
 *   A vendored, zero-dependency, reader-side render module that plots the AI
 *   bias-preserving-gate search result: search gain (search frontier / hand-
 *   designed baseline) vs cat size α², with a reference line at gain = 1.0 (the
 *   baseline = the wall). A discrete TOGGLE compares the two-quadrature search
 *   (lands ON the baseline, gain ≈ 1, ε_y driven to 0) against the single-
 *   quadrature shaped pulse (falls BELOW baseline, margin −0.29). Loaded after
 *   figures.js; extends window.DossierFigures with renderQCFrontier(container, spec).
 *
 * THE COMPOSITION LAW
 *   Every GENERAL primitive comes from the runtime (figures.js), never re-rolled:
 *     - SVG nodes   -> DossierFigures.el(tag, attrs)
 *     - string-emit -> DossierFigures.r2 / escAttr / escTxt    (poster path)
 *     - dedup floor -> DossierFigures.dedupPoster(container)
 *   The engine ships NO charting primitives, so this module carries its own small
 *   charting layer (linear x and y) — written HERE, NOT cross-imported from another
 *   figure module (no load-order dependency). Geometry is computed ONCE in
 *   computeFrontier(spec) and consumed by BOTH the live el() emitter AND the pure
 *   poster string emitter, so the JS-off floor can never drift from the live ceiling.
 *   Text is sized by ROLE via tier classes (lf-tick / lf-axis / lf-callout — the
 *   runtime owns the px), NEVER a raw font-size; keep both emit paths in lockstep.
 *
 * THE DATA (REAL + CITED — do NOT add or interpolate points)
 *   Published search points: α²=2 → gain 1.04 ; α²=3 → gain 1.00. α²=4 is
 *   baseline-only (search compute-bound, N≥24 Fock states) — a baseline marker,
 *   no search point. The bias-breaking knob ε_y is driven to 0 by the search; the
 *   single-quadrature shaped pulse falls BELOW baseline at margin −0.29. This is a
 *   DISCRETE comparison, not a continuous sweep — there is NO fabricated curve.
 *   Values from the prior lineage's current (working) edition,
 *   github.com/m4gr4th34/dossier-QC-Accelerate — the working-draft result, sparse
 *   (three cat sizes, as published), not DOI-archived. [reported]
 *
 * SUSTAINABILITY LAWS (same as the runtime)
 *   Zero external dependencies, pure vanilla, vendored first-party. Reader-side
 *   only; NEVER executed by CI (the stdlib-only verify floor stays untouched).
 */
(function (root) {
  "use strict";

  var NS = root && root.DossierFigures;
  if (!NS) {
    if (root && root.console) {
      root.console.error("[qc-frontier] figures.js runtime not found — load figures.js before qc-frontier.js");
    }
    return;
  }

  // COMPOSITION: every GENERAL primitive below IS the runtime's — never re-rolled.
  var DossierFigures = NS;
  var el          = DossierFigures.el;
  var r2          = DossierFigures.r2;       // string-emit helpers (poster path)
  var escAttr     = DossierFigures.escAttr;
  var escTxt      = DossierFigures.escTxt;
  var dedupPoster = DossierFigures.dedupPoster;

  function num(v, d) { return (typeof v === "number" && isFinite(v)) ? v : d; }

  var W = 800, H = 480;
  var ML = 70, MR = 168, MT = 36, MB = 56;   // wide right gutter for the legend/annotation

  // ===== SHARED CHART GEOMETRY =============================================
  // Computed ONCE; consumed by the live el() emitter AND the pure poster string
  // emitter. Linear x (cat size α²) and y (gain). Only the points the spec
  // carries are plotted — nothing is interpolated.
  function computeFrontier(spec) {
    spec = spec || {};
    var points = (spec.points || []).map(function (p) { return { nbar: num(p.nbar, 0), gain: num(p.gain, 1) }; });
    var baselineOnly = (spec.baselineOnly || []).map(function (p) { return { nbar: num(p.nbar, 0) }; });
    var epsilonY = num(spec.epsilonY, 0);
    var margin = num(spec.singleQuadMargin, -0.29);
    var baseline = 1.0;
    var singleQuadGain = baseline + margin;   // margin is signed; below baseline = negative

    var plot = { x: ML, y: MT, w: W - ML - MR, h: H - MT - MB };

    // x domain: the discrete cat sizes present, padded.
    var nbars = points.map(function (p) { return p.nbar; }).concat(baselineOnly.map(function (p) { return p.nbar; }));
    var xLo = (nbars.length ? Math.min.apply(null, nbars) : 1) - 0.6;
    var xHi = (nbars.length ? Math.max.apply(null, nbars) : 4) + 0.6;

    // y domain: fixed to frame baseline=1 with the search points and the single-quad level.
    var gains = points.map(function (p) { return p.gain; }).concat([baseline, singleQuadGain]);
    var yLo = Math.min.apply(null, gains) - 0.11;
    var yHi = Math.max.apply(null, gains) + 0.08;

    function xPix(n) { return plot.x + (n - xLo) / (xHi - xLo) * plot.w; }
    function yPix(g) { return plot.y + (yHi - g) / (yHi - yLo) * plot.h; }

    var baselineY = r2(yPix(baseline));
    var singleY = r2(yPix(singleQuadGain));

    var searchPts = points.map(function (p) {
      return { x: r2(xPix(p.nbar)), y: r2(yPix(p.gain)), nbar: p.nbar, gain: p.gain,
        label: "α²=" + p.nbar + ": " + p.gain.toFixed(2) };
    });
    var basePts = baselineOnly.map(function (p) {
      return { x: r2(xPix(p.nbar)), y: baselineY, nbar: p.nbar, label: "α²=" + p.nbar + " (baseline only)" };
    });

    // x ticks at the integer cat sizes present; y ticks every 0.1.
    var xTickVals = nbars.slice().sort(function (a, b) { return a - b; });
    var xTicks = xTickVals.map(function (n) { return { px: r2(xPix(n)), label: "α²=" + n }; });
    var yTicks = [];
    var yStart = Math.ceil(yLo * 10) / 10, yEnd = Math.floor(yHi * 10) / 10;
    for (var g = yStart; g <= yEnd + 1e-9; g += 0.1) {
      var gg = Math.round(g * 10) / 10;
      yTicks.push({ py: r2(yPix(gg)), label: gg.toFixed(1) });
    }

    return {
      W: W, H: H, plot: plot,
      baseline: baseline, baselineY: baselineY,
      singleQuadGain: singleQuadGain, singleY: singleY, margin: margin, epsilonY: epsilonY,
      searchPts: searchPts, basePts: basePts, xTicks: xTicks, yTicks: yTicks,
      baseColor: "#9aa3a6", searchColor: "#2f6f8f", singleColor: "#c2562f",
      axisColor: "#5a6b70", gridColor: "#d7dee0",
      ariaLabel: "AI-search gain versus cat size: the search lands on the hand-designed baseline (gain about 1) and the bias-breaking knob is driven to zero; a single-quadrature pulse falls below baseline"
    };
  }

  function subtitleFor(f, mode) {
    if (mode === "single-quad") {
      return "Single-quadrature shaped pulse — falls " + Math.abs(f.margin).toFixed(2) + " below baseline (margin " + f.margin.toFixed(2) + ")";
    }
    return "Two-quadrature search — lands on baseline (gain ≈ 1.00); bias-breaking ε_y → " + f.epsilonY;
  }

  function fail(container, msg) {
    if (root && root.console) root.console.error("[qc-frontier] " + msg);
    if (container && container.appendChild) {
      var doc = (root && root.document) || container.ownerDocument;
      var p = doc.createElement("p");
      p.className = "lf-fallback";
      p.textContent = "Figure unavailable: " + msg;
      container.appendChild(p);
    }
    return null;
  }

  // -------------------------------------------------------------------------
  // renderQCFrontier(container, spec) — live entry point. dedupPoster first,
  // build the static chart once, then a discrete TOGGLE swaps which result set
  // (two-quadrature search vs single-quadrature pulse) is highlighted.
  // -------------------------------------------------------------------------
  function renderQCFrontier(container, spec) {
    if (!container) return fail(null, "no container");
    var doc = (root && root.document) || container.ownerDocument;

    if (spec == null && container.getAttribute) spec = container.getAttribute("data-figure");
    if (typeof spec === "string") {
      try { spec = JSON.parse(spec); }
      catch (e) { return fail(container, "data-figure is not valid JSON"); }
    }
    spec = spec || {};

    dedupPoster(container);   // RUNTIME: drop any sealed [data-poster] floor before going live

    var f = computeFrontier(spec);
    var px = f.plot.x, py = f.plot.y, pw = f.plot.w, ph = f.plot.h;

    var svg = el("svg", {
      viewBox: "0 0 " + f.W + " " + f.H, width: "100%", "class": "lf-svg",
      role: "img", "aria-label": f.ariaLabel
    });

    // --- gridlines + axes ------------------------------------------------
    var gGrid = el("g", { "class": "lf-grid" });
    f.yTicks.forEach(function (t) {
      gGrid.appendChild(el("line", { x1: px, y1: t.py, x2: px + pw, y2: t.py, stroke: f.gridColor, "stroke-width": "1" }));
    });
    svg.appendChild(gGrid);

    var gAx = el("g", { "class": "lf-axes" });
    gAx.appendChild(el("line", { x1: px, y1: py, x2: px, y2: py + ph, stroke: f.axisColor, "stroke-width": "1.5" }));
    gAx.appendChild(el("line", { x1: px, y1: py + ph, x2: px + pw, y2: py + ph, stroke: f.axisColor, "stroke-width": "1.5" }));
    f.xTicks.forEach(function (t) {
      gAx.appendChild(el("line", { x1: t.px, y1: py + ph, x2: t.px, y2: py + ph + 5, stroke: f.axisColor, "stroke-width": "1" }));
      var tx = el("text", { "class": "lf-tick", x: t.px, y: py + ph + 18, "text-anchor": "middle", fill: f.axisColor });
      tx.textContent = t.label; gAx.appendChild(tx);
    });
    f.yTicks.forEach(function (t) {
      var ty = el("text", { "class": "lf-tick", x: px - 8, y: t.py + 3, "text-anchor": "end", fill: f.axisColor });
      ty.textContent = t.label; gAx.appendChild(ty);
    });
    var xlab = el("text", { "class": "lf-axis", x: px + pw / 2, y: f.H - 12, "text-anchor": "middle", fill: f.axisColor });
    xlab.textContent = "cat size  α²  (mean photon number)"; gAx.appendChild(xlab);
    var ylab = el("text", { "class": "lf-axis", x: 16, y: py + ph / 2, "text-anchor": "middle", fill: f.axisColor,
      transform: "rotate(-90 16 " + (py + ph / 2) + ")" });
    ylab.textContent = "AI-search gain  (search / baseline)"; gAx.appendChild(ylab);
    svg.appendChild(gAx);

    // --- baseline reference line (gain = 1.0 = the wall) -----------------
    var gBase = el("g", { "class": "lf-baseline" });
    gBase.appendChild(el("line", { x1: px, y1: f.baselineY, x2: px + pw, y2: f.baselineY,
      stroke: f.baseColor, "stroke-width": "2", "stroke-dasharray": "7 4" }));
    var baseLab = el("text", { "class": "lf-axis", x: px + pw - 4, y: f.baselineY + 16, "text-anchor": "end", fill: f.axisColor });
    baseLab.textContent = "hand-designed baseline = the wall (gain 1.0)"; gBase.appendChild(baseLab);
    svg.appendChild(gBase);

    // --- TWO-QUADRATURE group (default) ----------------------------------
    var gTwo = el("g", { "class": "lf-two-quad" });
    f.searchPts.forEach(function (p) {
      gTwo.appendChild(el("circle", { cx: p.x, cy: p.y, r: "6", fill: f.searchColor, stroke: "#fff", "stroke-width": "1.5" }));
      var tl = el("text", { "class": "lf-tick", x: p.x, y: p.y - 12, "text-anchor": "middle", fill: f.searchColor });
      tl.textContent = p.label; gTwo.appendChild(tl);
    });
    f.basePts.forEach(function (p) {
      gTwo.appendChild(el("circle", { cx: p.x, cy: p.y, r: "6", fill: "none", stroke: f.baseColor, "stroke-width": "2" }));
      var tl2 = el("text", { "class": "lf-tick", x: p.x, y: p.y - 12, "text-anchor": "middle", fill: f.axisColor });
      tl2.textContent = p.label; gTwo.appendChild(tl2);
    });
    svg.appendChild(gTwo);

    // --- SINGLE-QUADRATURE group (toggled) -------------------------------
    var gSingle = el("g", { "class": "lf-single-quad" });
    gSingle.appendChild(el("line", { x1: px, y1: f.singleY, x2: px + pw, y2: f.singleY,
      stroke: f.singleColor, "stroke-width": "2", "stroke-dasharray": "4 3" }));
    var sx = f.searchPts.length ? f.searchPts[0].x : (px + pw / 2);
    gSingle.appendChild(el("circle", { cx: sx, cy: f.singleY, r: "6", fill: f.singleColor, stroke: "#fff", "stroke-width": "1.5" }));
    var sLab = el("text", { "class": "lf-axis", x: px + pw - 4, y: f.singleY + 16, "text-anchor": "end", fill: f.singleColor });
    sLab.textContent = "single-quadrature shaped pulse · margin " + f.margin.toFixed(2); gSingle.appendChild(sLab);
    gSingle.setAttribute("style", "display:none");
    svg.appendChild(gSingle);

    // --- subtitle text (inside the SVG, top-left) ------------------------
    var subEl = el("text", { "class": "lf-callout", x: px, y: 22, fill: f.axisColor });
    subEl.textContent = subtitleFor(f, "two-quad"); svg.appendChild(subEl);

    // --- controls: the discrete toggle -----------------------------------
    var currentMode = "two-quad";   // the PUBLISHED start (what the sealed poster freezes) — Reset restores it
    var controls = doc.createElement("div");
    controls.className = "lf-controls";
    var btnTwo = doc.createElement("button");
    btnTwo.type = "button"; btnTwo.className = "lf-btn"; btnTwo.textContent = "Two-quadrature search";
    var btnSingle = doc.createElement("button");
    btnSingle.type = "button"; btnSingle.className = "lf-btn"; btnSingle.textContent = "Single-quadrature pulse";
    controls.appendChild(btnTwo); controls.appendChild(btnSingle);

    // Reset: restore the PUBLISHED start view (the two-quadrature mode the poster freezes).
    var resetBtn = doc.createElement("button");
    resetBtn.type = "button"; resetBtn.className = "lf-btn"; resetBtn.textContent = "Reset";
    controls.appendChild(resetBtn);

    var readout = doc.createElement("span");
    readout.className = "lf-readout";
    controls.appendChild(readout);

    function setMode(mode) {
      currentMode = mode;
      var single = (mode === "single-quad");
      gSingle.setAttribute("style", single ? "display:inline" : "display:none");
      gTwo.setAttribute("style", single ? "display:none" : "display:inline");
      subEl.textContent = subtitleFor(f, mode);
      readout.textContent = subtitleFor(f, mode);
      btnTwo.setAttribute("aria-pressed", single ? "false" : "true");
      btnSingle.setAttribute("aria-pressed", single ? "true" : "false");
    }
    btnTwo.addEventListener("click", function () { setMode("two-quad"); });
    btnSingle.addEventListener("click", function () { setMode("single-quad"); });
    resetBtn.addEventListener("click", function () { setMode("two-quad"); });

    container.appendChild(svg);
    container.appendChild(controls);
    setMode("two-quad");

    // A discrete-toggle figure carries no slider, so it exposes no setSlider: the lightbox
    // handoff finds no {slider} and gracefully opens at the published start (two-quadrature).
    var handle = {
      runtimeVersion: DossierFigures.FIGURES_RUNTIME_VERSION,
      getState: function () { return { mode: currentMode, baseline: f.baseline, points: f.searchPts.map(function (p) { return { nbar: p.nbar, gain: p.gain }; }),
        epsilonY: f.epsilonY, singleQuadMargin: f.margin }; },
      setMode: setMode
    };
    container.__lfHandle = handle;
    return handle;
  }

  // -------------------------------------------------------------------------
  // renderQCFrontierPosterSVG(spec) -> the SEALED FLOOR: a DETERMINISTIC <svg>
  // string for the DEFAULT (two-quadrature) view. PURE — no DOM. Built from the
  // SAME computeFrontier() the live path uses, so floor == ceiling by construction.
  // -------------------------------------------------------------------------
  function renderQCFrontierPosterSVG(spec) {
    if (typeof spec === "string") { try { spec = JSON.parse(spec); } catch (e) { return ""; } }
    spec = spec || {};
    var f = computeFrontier(spec);
    var px = f.plot.x, py = f.plot.y, pw = f.plot.w, ph = f.plot.h;

    var s = '<svg viewBox="0 0 ' + f.W + ' ' + f.H + '" width="100%" class="lf-svg" role="img" aria-label="' + escAttr(f.ariaLabel) + '">';

    s += '<g class="lf-grid">';
    f.yTicks.forEach(function (t) {
      s += '<line x1="' + px + '" y1="' + t.py + '" x2="' + r2(px + pw) + '" y2="' + t.py + '" stroke="' + f.gridColor + '" stroke-width="1"></line>';
    });
    s += '</g>';

    s += '<g class="lf-axes">';
    s += '<line x1="' + px + '" y1="' + py + '" x2="' + px + '" y2="' + r2(py + ph) + '" stroke="' + f.axisColor + '" stroke-width="1.5"></line>';
    s += '<line x1="' + px + '" y1="' + r2(py + ph) + '" x2="' + r2(px + pw) + '" y2="' + r2(py + ph) + '" stroke="' + f.axisColor + '" stroke-width="1.5"></line>';
    f.xTicks.forEach(function (t) {
      s += '<line x1="' + t.px + '" y1="' + r2(py + ph) + '" x2="' + t.px + '" y2="' + r2(py + ph + 5) + '" stroke="' + f.axisColor + '" stroke-width="1"></line>';
      s += '<text class="lf-tick" x="' + t.px + '" y="' + r2(py + ph + 18) + '" text-anchor="middle" fill="' + f.axisColor + '">' + escTxt(t.label) + '</text>';
    });
    f.yTicks.forEach(function (t) {
      s += '<text class="lf-tick" x="' + r2(px - 8) + '" y="' + r2(t.py + 3) + '" text-anchor="end" fill="' + f.axisColor + '">' + escTxt(t.label) + '</text>';
    });
    s += '<text class="lf-axis" x="' + r2(px + pw / 2) + '" y="' + r2(f.H - 12) + '" text-anchor="middle" fill="' + f.axisColor + '">' + escTxt("cat size  α²  (mean photon number)") + '</text>';
    s += '<text class="lf-axis" x="16" y="' + r2(py + ph / 2) + '" text-anchor="middle" fill="' + f.axisColor + '" transform="rotate(-90 16 ' + r2(py + ph / 2) + ')">' + escTxt("AI-search gain  (search / baseline)") + '</text>';
    s += '</g>';

    s += '<g class="lf-baseline">';
    s += '<line x1="' + px + '" y1="' + f.baselineY + '" x2="' + r2(px + pw) + '" y2="' + f.baselineY + '" stroke="' + f.baseColor + '" stroke-width="2" stroke-dasharray="7 4"></line>';
    s += '<text class="lf-axis" x="' + r2(px + pw - 4) + '" y="' + r2(f.baselineY + 16) + '" text-anchor="end" fill="' + f.axisColor + '">' + escTxt("hand-designed baseline = the wall (gain 1.0)") + '</text>';
    s += '</g>';

    s += '<g class="lf-two-quad">';
    f.searchPts.forEach(function (p) {
      s += '<circle cx="' + p.x + '" cy="' + p.y + '" r="6" fill="' + f.searchColor + '" stroke="#fff" stroke-width="1.5"></circle>';
      s += '<text class="lf-tick" x="' + p.x + '" y="' + r2(p.y - 12) + '" text-anchor="middle" fill="' + f.searchColor + '">' + escTxt(p.label) + '</text>';
    });
    f.basePts.forEach(function (p) {
      s += '<circle cx="' + p.x + '" cy="' + p.y + '" r="6" fill="none" stroke="' + f.baseColor + '" stroke-width="2"></circle>';
      s += '<text class="lf-tick" x="' + p.x + '" y="' + r2(p.y - 12) + '" text-anchor="middle" fill="' + f.axisColor + '">' + escTxt(p.label) + '</text>';
    });
    s += '</g>';

    // single-quad group baked but hidden (the live toggle reveals it).
    var sx = f.searchPts.length ? f.searchPts[0].x : r2(px + pw / 2);
    s += '<g class="lf-single-quad" style="display:none">';
    s += '<line x1="' + px + '" y1="' + f.singleY + '" x2="' + r2(px + pw) + '" y2="' + f.singleY + '" stroke="' + f.singleColor + '" stroke-width="2" stroke-dasharray="4 3"></line>';
    s += '<circle cx="' + sx + '" cy="' + f.singleY + '" r="6" fill="' + f.singleColor + '" stroke="#fff" stroke-width="1.5"></circle>';
    s += '<text class="lf-axis" x="' + r2(px + pw - 4) + '" y="' + r2(f.singleY + 16) + '" text-anchor="end" fill="' + f.singleColor + '">' + escTxt("single-quadrature shaped pulse · margin " + f.margin.toFixed(2)) + '</text>';
    s += '</g>';

    s += '<text class="lf-callout" x="' + px + '" y="22" fill="' + f.axisColor + '">' + escTxt(subtitleFor(f, "two-quad")) + '</text>';
    s += '</svg>';
    return s;
  }

  DossierFigures.renderQCFrontier = renderQCFrontier;
  DossierFigures.renderQCFrontierPosterSVG = renderQCFrontierPosterSVG;   // back-compat (direct callers)
  DossierFigures.registerPoster("qc-frontier", renderQCFrontierPosterSVG); // registry (the sealer dispatches by spec.type)
  DossierFigures.registerRenderer("qc-frontier", renderQCFrontier);        // live-renderer registry (the lightbox dispatches by spec.type)
})(typeof window !== "undefined" ? window : null);
