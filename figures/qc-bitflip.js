/*
 * qc-bitflip.js — "the self-protecting floor" render module for Open Dossier
 * living figures (Dossier QC-Accelerate-002, Chapter 1).
 *
 * WHAT THIS IS
 *   A vendored, zero-dependency, reader-side render module that draws the
 *   cat-qubit noise-bias chart: bit-flip error falling EXPONENTIALLY with cat
 *   size n̄ while phase-flip rises only LINEARLY — the exponentially growing
 *   noise bias that makes the cat a self-protecting memory. Loaded after
 *   figures.js; extends window.DossierFigures with renderQCBitflip(container, spec).
 *
 * THE COMPOSITION LAW (the whole point of the scaffold)
 *   Every GENERAL primitive comes from the runtime (figures.js), never re-rolled:
 *     - SVG nodes        -> DossierFigures.el(tag, attrs)
 *     - string-emit      -> DossierFigures.r2 / escAttr / escTxt   (poster path)
 *     - baked-floor dedup-> DossierFigures.dedupPoster(container)
 *   The engine ships NO charting primitives (axes / scales / line paths), so the
 *   small charting layer lives IN this module (linear x, log y). It is computed
 *   ONCE in computeChart(spec) and consumed by BOTH emitters — the live el() path
 *   AND the pure poster string path — so the sealed JS-off FLOOR can never drift
 *   from the live JS-on CEILING (the orrery.js shared-compute-split discipline).
 *
 * THE PHYSICS (illustrative scaling, established — Mirrahimi et al. 2014)
 *   Γ_bitflip(n̄) = exp(-2*n̄)     (suppressed exponentially as the cat grows)
 *   Γ_phaseflip(n̄) = gamma * n̄    (rises only linearly)
 *   Rates are normalized for legibility; the physics being shown is the
 *   exponential-vs-linear CONTRAST (the growing bias Γ_pf/Γ_bf), not absolute s^-1.
 *   This is a RECAP of the prior lineage's Chapter 1 (DOI 10.5281/zenodo.20838233),
 *   not a re-run of its simulation.
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
      root.console.error("[qc-bitflip] figures.js runtime not found — load figures.js before qc-bitflip.js");
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

  // ----- domain math (module-local; the cat-qubit scaling being recapped) -----
  function gammaBF(n) { return Math.exp(-2 * n); }          // bit-flip: exponential cliff
  function gammaPF(n, gamma) { return gamma * n; }          // phase-flip: linear rise
  function log10(x) { return Math.log(x) / Math.LN10; }
  function num(v, d) { return (typeof v === "number" && isFinite(v)) ? v : d; }
  function clamp(x, lo, hi) { return x < lo ? lo : x > hi ? hi : x; }

  // Compact, legible bias formatting (it spans many orders of magnitude).
  function fmtBias(b) {
    if (!isFinite(b)) return "∞";
    if (b >= 1000) {
      var e = Math.floor(log10(b));
      var m = b / Math.pow(10, e);
      return (Math.round(m * 10) / 10) + "×10^" + e;
    }
    if (b >= 10) return String(Math.round(b));
    return String(Math.round(b * 10) / 10);
  }

  // ===== SHARED CHARTING GEOMETRY ==========================================
  // Computed ONCE; consumed by the live el() emitter AND the pure poster string
  // emitter. Linear x (cat size n̄), log10 y (rates span ~7 decades). Returns
  // plain data + a PURE markerAt(n̄) the slider/poster both call — so the floor
  // (poster at the default n̄) and the ceiling (live at the dragged n̄) share one
  // source of truth for every coordinate.
  var W = 800, H = 480;
  var ML = 70, MR = 150, MT = 30, MB = 54;   // plot margins (wide right gutter for the legend)
  var SAMPLES = 180;

  function computeChart(spec) {
    spec = spec || {};
    var nMin = num(spec.nbarMin, 0.5);
    var nMax = num(spec.nbarMax, 8);
    if (nMax <= nMin) nMax = nMin + 1;
    var gamma = num(spec.gamma, 0.05);
    // Default marker sits at n̄ = 2 (α²=2, the cat size carried into Figure 2),
    // clamped into range — the live slider starts here, the poster bakes here.
    var nDef = clamp(2, nMin, nMax);

    var plot = { x: ML, y: MT, w: W - ML - MR, h: H - MT - MB };

    // y log-range from the actual data extremes (both curves), padded to decades.
    var lo = Math.min(gammaBF(nMax), gammaPF(nMin, gamma) || gammaBF(nMax));
    var hi = Math.max(gammaBF(nMin), gammaPF(nMax, gamma));
    var minExp = Math.floor(log10(lo));
    var maxExp = Math.ceil(log10(hi));
    if (maxExp <= minExp) maxExp = minExp + 1;

    function xPix(n) { return plot.x + (n - nMin) / (nMax - nMin) * plot.w; }
    function yPix(v) {
      var e = log10(v <= 0 ? Math.pow(10, minExp) : v);
      return plot.y + (maxExp - e) / (maxExp - minExp) * plot.h;
    }

    // The two curves as SVG path "d" (sampled identically for both emitters).
    function curveD(fn) {
      var d = "";
      for (var i = 0; i <= SAMPLES; i++) {
        var n = nMin + (i / SAMPLES) * (nMax - nMin);
        var p = [xPix(n), yPix(fn(n))];
        d += (i ? "L" : "M") + r2(p[0]) + " " + r2(p[1]);
      }
      return d;
    }
    var bfD = curveD(function (n) { return gammaBF(n); });
    var pfD = curveD(function (n) { return gammaPF(n, gamma); });

    // Axis ticks: integer n̄ on x; decade marks on log y.
    var xTicks = [];
    for (var n = Math.ceil(nMin); n <= Math.floor(nMax); n++) {
      xTicks.push({ n: n, px: r2(xPix(n)), label: String(n) });
    }
    var yTicks = [];
    for (var e2 = minExp; e2 <= maxExp; e2++) {
      yTicks.push({ exp: e2, py: r2(yPix(Math.pow(10, e2))), label: "10^" + e2 });
    }

    // PURE marker resolver — both paths call it (poster at nDef, live at drag n̄).
    function markerAt(nbar) {
      var nb = clamp(nbar, nMin, nMax);
      var bf = gammaBF(nb), pf = gammaPF(nb, gamma);
      return {
        nbar: nb,
        x: r2(xPix(nb)),
        bfY: r2(yPix(bf)), pfY: r2(yPix(pf)),
        bias: pf / bf
      };
    }

    return {
      W: W, H: H, plot: plot,
      nMin: nMin, nMax: nMax, gamma: gamma, nDef: nDef,
      minExp: minExp, maxExp: maxExp,
      bfD: bfD, pfD: pfD, xTicks: xTicks, yTicks: yTicks,
      bfColor: "#2f6f8f", pfColor: "#c2562f", axisColor: "#5a6b70", gridColor: "#d7dee0",
      ariaLabel: "Cat-qubit noise bias: bit-flip error falls exponentially with cat size while phase-flip rises linearly",
      markerAt: markerAt
    };
  }

  function readoutText(m) {
    return "n̄ = " + (Math.round(m.nbar * 100) / 100) + "   ·   bias  Γφ / Γx = " + fmtBias(m.bias);
  }

  function fail(container, msg) {
    if (root && root.console) root.console.error("[qc-bitflip] " + msg);
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
  // renderQCBitflip(container, spec) — the live entry point. dedupPoster first,
  // then build the static chart once and a marker layer the slider moves.
  // -------------------------------------------------------------------------
  function renderQCBitflip(container, spec) {
    if (!container) return fail(null, "no container");
    var doc = (root && root.document) || container.ownerDocument;

    if (spec == null && container.getAttribute) spec = container.getAttribute("data-figure");
    if (typeof spec === "string") {
      try { spec = JSON.parse(spec); }
      catch (e) { return fail(container, "data-figure is not valid JSON"); }
    }
    spec = spec || {};

    dedupPoster(container);   // RUNTIME: drop any sealed [data-poster] floor before going live

    var f = computeChart(spec);

    var svg = el("svg", {
      viewBox: "0 0 " + f.W + " " + f.H, width: "100%", "class": "lf-svg",
      role: "img", "aria-label": f.ariaLabel
    });

    // --- gridlines + axes ------------------------------------------------
    var gGrid = el("g", { "class": "lf-grid" });
    f.yTicks.forEach(function (t) {
      gGrid.appendChild(el("line", { x1: f.plot.x, y1: t.py, x2: f.plot.x + f.plot.w, y2: t.py,
        stroke: f.gridColor, "stroke-width": "1" }));
    });
    svg.appendChild(gGrid);

    var gAx = el("g", { "class": "lf-axes" });
    gAx.appendChild(el("line", { x1: f.plot.x, y1: f.plot.y, x2: f.plot.x, y2: f.plot.y + f.plot.h,
      stroke: f.axisColor, "stroke-width": "1.5" }));
    gAx.appendChild(el("line", { x1: f.plot.x, y1: f.plot.y + f.plot.h, x2: f.plot.x + f.plot.w, y2: f.plot.y + f.plot.h,
      stroke: f.axisColor, "stroke-width": "1.5" }));
    f.xTicks.forEach(function (t) {
      gAx.appendChild(el("line", { x1: t.px, y1: f.plot.y + f.plot.h, x2: t.px, y2: f.plot.y + f.plot.h + 5,
        stroke: f.axisColor, "stroke-width": "1" }));
      var tx = el("text", { x: t.px, y: f.plot.y + f.plot.h + 18, "text-anchor": "middle",
        "font-size": "11", fill: f.axisColor });
      tx.textContent = t.label; gAx.appendChild(tx);
    });
    f.yTicks.forEach(function (t) {
      var ty = el("text", { x: f.plot.x - 8, y: t.py + 3, "text-anchor": "end",
        "font-size": "10", fill: f.axisColor });
      ty.textContent = t.label; gAx.appendChild(ty);
    });
    var xlab = el("text", { x: f.plot.x + f.plot.w / 2, y: f.H - 12, "text-anchor": "middle",
      "font-size": "12", fill: f.axisColor });
    xlab.textContent = "cat size  n̄  (mean photon number)"; gAx.appendChild(xlab);
    var ylab = el("text", { x: 16, y: f.plot.y + f.plot.h / 2, "text-anchor": "middle",
      "font-size": "12", fill: f.axisColor, transform: "rotate(-90 16 " + (f.plot.y + f.plot.h / 2) + ")" });
    ylab.textContent = "error rate  (log, normalized)"; gAx.appendChild(ylab);
    svg.appendChild(gAx);

    // --- curves ----------------------------------------------------------
    var gC = el("g", { "class": "lf-curves" });
    gC.appendChild(el("path", { d: f.bfD, fill: "none", stroke: f.bfColor, "stroke-width": "2.5" }));
    gC.appendChild(el("path", { d: f.pfD, fill: "none", stroke: f.pfColor, "stroke-width": "2.5" }));
    svg.appendChild(gC);

    // --- legend (static) -------------------------------------------------
    var lx = f.plot.x + f.plot.w + 16, ly = f.plot.y + 8;
    var gL = el("g", { "class": "lf-legend" });
    gL.appendChild(el("line", { x1: lx, y1: ly, x2: lx + 22, y2: ly, stroke: f.bfColor, "stroke-width": "2.5" }));
    var l1 = el("text", { x: lx + 28, y: ly + 4, "font-size": "11", fill: f.axisColor });
    l1.textContent = "bit-flip  ∝ e^(−2n̄)"; gL.appendChild(l1);
    gL.appendChild(el("line", { x1: lx, y1: ly + 20, x2: lx + 22, y2: ly + 20, stroke: f.pfColor, "stroke-width": "2.5" }));
    var l2 = el("text", { x: lx + 28, y: ly + 24, "font-size": "11", fill: f.axisColor });
    l2.textContent = "phase-flip  ∝ n̄"; gL.appendChild(l2);
    svg.appendChild(gL);

    // --- marker layer (slider-driven) ------------------------------------
    var gM = el("g", { "class": "lf-marker" });
    var guide = el("line", { stroke: f.axisColor, "stroke-width": "1", "stroke-dasharray": "4 3", "stroke-opacity": "0.7" });
    var dotBF = el("circle", { r: "5", fill: f.bfColor, stroke: "#fff", "stroke-width": "1.5" });
    var dotPF = el("circle", { r: "5", fill: f.pfColor, stroke: "#fff", "stroke-width": "1.5" });
    gM.appendChild(guide); gM.appendChild(dotBF); gM.appendChild(dotPF);
    svg.appendChild(gM);

    function placeMarker(m) {
      guide.setAttribute("x1", m.x); guide.setAttribute("y1", f.plot.y);
      guide.setAttribute("x2", m.x); guide.setAttribute("y2", f.plot.y + f.plot.h);
      dotBF.setAttribute("cx", m.x); dotBF.setAttribute("cy", m.bfY);
      dotPF.setAttribute("cx", m.x); dotPF.setAttribute("cy", m.pfY);
    }

    // --- controls --------------------------------------------------------
    var controls = doc.createElement("div");
    controls.className = "lf-controls";
    var wrap = doc.createElement("label");
    wrap.className = "lf-field";
    wrap.appendChild(doc.createTextNode("Cat size n̄"));
    var input = doc.createElement("input");
    input.type = "range";
    input.min = String(f.nMin); input.max = String(f.nMax); input.step = "0.05";
    input.value = String(f.nDef); input.className = "lf-range";
    wrap.appendChild(input);
    controls.appendChild(wrap);
    var readout = doc.createElement("span");
    readout.className = "lf-readout";
    controls.appendChild(readout);

    function update(nbar) {
      var m = f.markerAt(nbar);
      placeMarker(m);
      readout.textContent = readoutText(m);
    }
    input.addEventListener("input", function () { update(parseFloat(input.value)); });

    container.appendChild(svg);
    container.appendChild(controls);
    update(f.nDef);

    return {
      runtimeVersion: DossierFigures.FIGURES_RUNTIME_VERSION,
      getState: function () { return f.markerAt(parseFloat(input.value)); },
      setNbar: function (v) { input.value = String(clamp(v, f.nMin, f.nMax)); update(parseFloat(input.value)); }
    };
  }

  // -------------------------------------------------------------------------
  // renderQCBitflipPosterSVG(spec) -> the SEALED FLOOR: a DETERMINISTIC <svg>
  // string for the default-n̄ frame. PURE — no DOM. Built from the SAME
  // computeChart() the live path uses, so floor == ceiling by construction. The
  // readout (interactive in the live ceiling) is baked as SVG text here.
  // -------------------------------------------------------------------------
  function renderQCBitflipPosterSVG(spec) {
    if (typeof spec === "string") { try { spec = JSON.parse(spec); } catch (e) { return ""; } }
    spec = spec || {};
    var f = computeChart(spec);
    var m = f.markerAt(f.nDef);
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
      s += '<text x="' + t.px + '" y="' + r2(py + ph + 18) + '" text-anchor="middle" font-size="11" fill="' + f.axisColor + '">' + escTxt(t.label) + '</text>';
    });
    f.yTicks.forEach(function (t) {
      s += '<text x="' + r2(px - 8) + '" y="' + r2(t.py + 3) + '" text-anchor="end" font-size="10" fill="' + f.axisColor + '">' + escTxt(t.label) + '</text>';
    });
    s += '<text x="' + r2(px + pw / 2) + '" y="' + r2(f.H - 12) + '" text-anchor="middle" font-size="12" fill="' + f.axisColor + '">' + escTxt("cat size  n̄  (mean photon number)") + '</text>';
    s += '<text x="16" y="' + r2(py + ph / 2) + '" text-anchor="middle" font-size="12" fill="' + f.axisColor + '" transform="rotate(-90 16 ' + r2(py + ph / 2) + ')">' + escTxt("error rate  (log, normalized)") + '</text>';
    s += '</g>';

    s += '<g class="lf-curves">';
    s += '<path d="' + f.bfD + '" fill="none" stroke="' + f.bfColor + '" stroke-width="2.5"></path>';
    s += '<path d="' + f.pfD + '" fill="none" stroke="' + f.pfColor + '" stroke-width="2.5"></path>';
    s += '</g>';

    var lx = r2(px + pw + 16), ly = r2(py + 8);
    s += '<g class="lf-legend">';
    s += '<line x1="' + lx + '" y1="' + ly + '" x2="' + r2(lx + 22) + '" y2="' + ly + '" stroke="' + f.bfColor + '" stroke-width="2.5"></line>';
    s += '<text x="' + r2(lx + 28) + '" y="' + r2(ly + 4) + '" font-size="11" fill="' + f.axisColor + '">' + escTxt("bit-flip  ∝ e^(−2n̄)") + '</text>';
    s += '<line x1="' + lx + '" y1="' + r2(ly + 20) + '" x2="' + r2(lx + 22) + '" y2="' + r2(ly + 20) + '" stroke="' + f.pfColor + '" stroke-width="2.5"></line>';
    s += '<text x="' + r2(lx + 28) + '" y="' + r2(ly + 24) + '" font-size="11" fill="' + f.axisColor + '">' + escTxt("phase-flip  ∝ n̄") + '</text>';
    s += '</g>';

    s += '<g class="lf-marker">';
    s += '<line x1="' + m.x + '" y1="' + py + '" x2="' + m.x + '" y2="' + r2(py + ph) + '" stroke="' + f.axisColor + '" stroke-width="1" stroke-dasharray="4 3" stroke-opacity="0.7"></line>';
    s += '<circle cx="' + m.x + '" cy="' + m.bfY + '" r="5" fill="' + f.bfColor + '" stroke="#fff" stroke-width="1.5"></circle>';
    s += '<circle cx="' + m.x + '" cy="' + m.pfY + '" r="5" fill="' + f.pfColor + '" stroke="#fff" stroke-width="1.5"></circle>';
    s += '</g>';

    s += '<text x="' + px + '" y="20" font-size="12" fill="' + f.axisColor + '">' + escTxt(readoutText(m)) + '</text>';
    s += '</svg>';
    return s;
  }

  DossierFigures.renderQCBitflip = renderQCBitflip;
  DossierFigures.renderQCBitflipPosterSVG = renderQCBitflipPosterSVG;   // back-compat (direct callers)
  DossierFigures.registerPoster("qc-bitflip", renderQCBitflipPosterSVG); // registry (the sealer dispatches by spec.type)
})(typeof window !== "undefined" ? window : null);
