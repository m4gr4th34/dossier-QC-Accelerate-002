/*
 * qc-phasespace.js — "the self-protecting floor, cause and consequence" render
 * module for Open Dossier living figures (Dossier QC-Accelerate-002, Chapter 1).
 *
 * WHAT THIS IS
 *   Two linked panels driven by ONE cat-size slider n̄:
 *     LEFT (phase space, the CAUSE): the complex plane with the two coherent-state
 *       lobes |0_L>=|+α>, |1_L>=|-α> at (±α,0), α=√n̄. Lobe WIDTH is α-independent
 *       (coherent-state σ = 1/√2 — a bigger cat moves the lobes apart, it does NOT
 *       fatten them). The shaded overlap is the actual Gaussian PRODUCT of the two
 *       lobes, whose peak magnitude is exp(-α²/σ²) = exp(-2n̄) EXACTLY. A caliper
 *       marks the separation 2√n̄; an arrow marks "bit-flip: cross the gap"; a note
 *       marks "phase-flip: dephasing, ~ n̄".
 *     RIGHT (rates, the CONSEQUENCE): the validated rate chart — log-y, bit-flip
 *       = e^(-2n̄) (the cliff), phase-flip = γ·n̄ (the line), marker at n̄.
 *   THE IDENTITY (the whole point): the LEFT overlap value and the RIGHT bit-flip
 *   height are the SAME number, e^(-2n̄). The slider makes that visible.
 *
 * THE COMPOSITION LAW (the scaffold)
 *   Every GENERAL primitive comes from the runtime (figures.js), never re-rolled:
 *     - SVG nodes -> el ; string-emit -> r2/escAttr/escTxt ; dedup -> dedupPoster.
 *   The engine ships NO charting and NO 2D-density primitives, so the linear+log
 *   scales, axes/ticks, the Gaussian-lobe renderer, the overlap-shade, and the
 *   curve paths all live IN this module. Geometry is computed ONCE in
 *   computeFrame(spec, n̄) and consumed by BOTH the live el() emitter AND the pure
 *   poster string emitter — the JS-off floor can never drift from the JS-on ceiling
 *   (the orrery.js shared-compute-split discipline). Self-contained: no cross-module
 *   dependency, so auto-load order does not matter.
 *
 *   Type sizes below are this module's OWN choices (tuned against the rendered
 *   half-panel size for legibility), NOT a template standard; keep the live el()
 *   and poster string emitters in lockstep so floor == ceiling.
 *
 * THE PHYSICS (illustrative, established — Mirrahimi et al. 2014)
 *   α=√n̄ ; coherent-state overlap |<α|-α>| = exp(-2α²) = exp(-2n̄) = the bit-flip
 *   amplitude ; phase-flip (dephasing) ∝ n̄. σ=1/√2 is chosen so the rendered
 *   Gaussian-product peak equals exp(-2n̄) exactly. Rates normalized for legibility;
 *   the lobes are SCHEMATIC coherent states, not a computed Wigner function. Recap
 *   of the prior lineage's Chapter 1 (DOI 10.5281/zenodo.20838233).
 *
 * SUSTAINABILITY LAWS: zero deps, pure vanilla, vendored first-party; reader-side
 *   only; NEVER executed by CI (the stdlib-only verify floor stays untouched).
 */
(function (root) {
  "use strict";

  var NS = root && root.DossierFigures;
  if (!NS) {
    if (root && root.console) {
      root.console.error("[qc-phasespace] figures.js runtime not found — load figures.js first");
    }
    return;
  }

  // COMPOSITION: every GENERAL primitive below IS the runtime's — never re-rolled.
  var DossierFigures = NS;
  var el          = DossierFigures.el;
  var r2          = DossierFigures.r2;
  var escAttr     = DossierFigures.escAttr;
  var escTxt      = DossierFigures.escTxt;
  var dedupPoster = DossierFigures.dedupPoster;

  // ----- domain math (module-local) -----
  var SIGMA = 1 / Math.sqrt(2);   // coherent-state σ: makes the Gaussian-product peak == exp(-2n̄)
  function gammaBF(n) { return Math.exp(-2 * n); }   // bit-flip: exponential cliff == lobe overlap
  function gammaPF(n, g) { return g * n; }           // phase-flip: linear (dephasing)
  function log10(x) { return Math.log(x) / Math.LN10; }
  function num(v, d) { return (typeof v === "number" && isFinite(v)) ? v : d; }
  function clamp(x, lo, hi) { return x < lo ? lo : x > hi ? hi : x; }

  function fmtSmall(v) {   // overlap value (tiny -> sci)
    if (v >= 0.01) return String(Math.round(v * 1000) / 1000);
    var e = Math.floor(log10(v)), m = v / Math.pow(10, e);
    return (Math.round(m * 10) / 10) + "×10^" + e;
  }
  function fmtBig(v) {     // bias value (huge -> sci)
    if (!isFinite(v)) return "∞";
    if (v < 1000) return String(v >= 10 ? Math.round(v) : Math.round(v * 10) / 10);
    var e = Math.floor(log10(v)), m = v / Math.pow(10, e);
    return (Math.round(m * 10) / 10) + "×10^" + e;
  }

  // ----- type sizes (module-local; tuned for the half-panel render) -----
  var FS_TITLE = 14, FS_AXTITLE = 14, FS_TICK = 13, FS_LEGEND = 13,
      FS_ANNO = 13, FS_LOBE = 13, FS_READOUT = 13, FS_AXHINT = 12;
  // direction cues (short intuition tags — both error rates: lower better; bias: higher better)
  var CUE_LOWER = "  ↓ lower = better", CUE_HIGHER = "  ↑ higher = better";

  // ----- layout constants (one 1040×490 canvas, two panels; widened for the larger text) -----
  var W = 1040, H = 490;
  var LCX = 250, LCY = 222, LHALF = 162, LPAD = 2.2;   // LEFT: center, content half-width (px), α-range pad
  var KLOBE = 1.9;                                       // visual blob radius in σ-units
  var RX = 648, RY = 60, RW = 356, RH = 300, RSAMP = 180;   // RIGHT rate-chart plot rect

  var COL = {
    lobe: "#5b7a99", overlap: "#2f6f8f",               // overlap uses the bit-flip color (the identity)
    bf: "#2f6f8f", pf: "#c2562f", axis: "#5a6b70", grid: "#d7dee0", faint: "#9fb0b5"
  };

  // ===== SHARED COMPUTE ====================================================
  // computeFrame(spec, n̄) -> ALL drawing coordinates for both panels at n̄.
  // Called per-slider-input by the live path and once (at posterNbar) by the
  // poster. Static geometry (axes/ticks/curves) is nbar-independent but recomputed
  // here so the two emitters read ONE source of truth.
  function computeFrame(spec, nbar) {
    spec = spec || {};
    var nMin = num(spec.nbarMin, 0.5), nMax = num(spec.nbarMax, 8);
    if (nMax <= nMin) nMax = nMin + 1;
    var gamma = num(spec.gamma, 0.05);
    var nb = clamp(nbar, nMin, nMax);

    // --- physics ---
    var alpha = Math.sqrt(nb);
    var overlap = gammaBF(nb);            // exp(-2n̄) == bit-flip amplitude (the identity)
    var pf = gammaPF(nb, gamma), bf = overlap, bias = pf / bf;

    // --- LEFT panel: α -> pixels (scale fixed by nMax so lobes never fatten) ---
    var REmax = Math.sqrt(nMax) + LPAD;
    var s = LHALF / REmax;
    var rLobe = KLOBE * SIGMA * s;                 // fixed px (σ fixed) — bigger cat != fatter lobe
    var rOv = KLOBE * (SIGMA / Math.sqrt(2)) * s;  // product-Gaussian width = σ/√2
    var lxR = LCX + alpha * s, lxL = LCX - alpha * s;
    var overlapOpacity = clamp(overlap, 0.03, 0.85);   // fades as exp(-2n̄); small floor keeps a sliver

    // caliper (separation 2√n̄) sits below the lobes
    var calY = LCY + rLobe + 30;
    // bit-flip arrow crosses the gap through the origin
    var arrY = LCY;

    // --- RIGHT panel: the rate chart (log-y) ---
    function xPix(n) { return RX + (n - nMin) / (nMax - nMin) * RW; }
    var yLo = Math.min(gammaBF(nMax), gammaPF(nMin, gamma) || gammaBF(nMax));
    var yHi = Math.max(gammaBF(nMin), gammaPF(nMax, gamma));
    var minExp = Math.floor(log10(yLo)), maxExp = Math.ceil(log10(yHi));
    if (maxExp <= minExp) maxExp = minExp + 1;
    function yPix(v) { return RY + (maxExp - log10(v <= 0 ? Math.pow(10, minExp) : v)) / (maxExp - minExp) * RH; }
    function curveD(fn) {
      var d = "";
      for (var i = 0; i <= RSAMP; i++) {
        var n = nMin + (i / RSAMP) * (nMax - nMin);
        d += (i ? "L" : "M") + r2(xPix(n)) + " " + r2(yPix(fn(n)));
      }
      return d;
    }
    var xTicks = [];
    for (var xt = Math.ceil(nMin); xt <= Math.floor(nMax); xt++) xTicks.push({ px: r2(xPix(xt)), label: String(xt) });
    var yTicks = [];
    for (var ye = minExp; ye <= maxExp; ye++) yTicks.push({ py: r2(yPix(Math.pow(10, ye))), label: "10^" + ye });

    var readout = "n̄ = " + (Math.round(nb * 100) / 100) +
      "   ·   separation 2α = " + (Math.round(2 * alpha * 100) / 100) +
      "   ·   overlap e^(−2n̄) = " + fmtSmall(overlap) +
      "   ·   bias Γpf/Γbf = " + fmtBig(bias) + CUE_HIGHER;

    return {
      W: W, H: H, nMin: nMin, nMax: nMax, gamma: gamma, nb: nb, alpha: alpha,
      // left
      LCX: LCX, LCY: LCY, s: s, rLobe: r2(rLobe), rOv: r2(rOv),
      lxL: r2(lxL), lxR: r2(lxR), overlapOpacity: r2(overlapOpacity),
      calY: calY, arrY: arrY,
      // right
      bfD: curveD(function (n) { return gammaBF(n); }),
      pfD: curveD(function (n) { return gammaPF(n, gamma); }),
      xTicks: xTicks, yTicks: yTicks,
      mX: r2(xPix(nb)), mBFy: r2(yPix(bf)), mPFy: r2(yPix(pf)),
      readout: readout,
      ariaLabel: "Linked phase-space and rate view of the cat qubit: two coherent-state lobes separate as the cat grows, their overlap e^(-2n-bar) equals the bit-flip rate on the right chart"
    };
  }

  function fail(container, msg) {
    if (root && root.console) root.console.error("[qc-phasespace] " + msg);
    if (container && container.appendChild) {
      var doc = (root && root.document) || container.ownerDocument;
      var p = doc.createElement("p"); p.className = "lf-fallback";
      p.textContent = "Figure unavailable: " + msg; container.appendChild(p);
    }
    return null;
  }

  // -------------------------------------------------------------------------
  // LIVE: renderQCPhasespace(container, spec)
  // -------------------------------------------------------------------------
  function renderQCPhasespace(container, spec) {
    if (!container) return fail(null, "no container");
    var doc = (root && root.document) || container.ownerDocument;
    if (spec == null && container.getAttribute) spec = container.getAttribute("data-figure");
    if (typeof spec === "string") { try { spec = JSON.parse(spec); } catch (e) { return fail(container, "data-figure is not valid JSON"); } }
    spec = spec || {};

    dedupPoster(container);   // drop any sealed [data-poster] floor before going live

    var nMin = num(spec.nbarMin, 0.5), nMax = num(spec.nbarMax, 8);
    var nStart = clamp(2, nMin, nMax);
    var f = computeFrame(spec, nStart);

    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, width: "100%", "class": "lf-svg", role: "img", "aria-label": f.ariaLabel });

    // defs: soft radial gradients for the lobes + overlap, and the arrowhead
    var defs = el("defs", {});
    defs.appendChild(radialGrad("ps-lobe", COL.lobe));
    defs.appendChild(radialGrad("ps-ov", COL.overlap));
    defs.appendChild(arrowMarker("ps-arr", COL.pf));
    svg.appendChild(defs);

    // ---- panel titles ----
    svg.appendChild(txt(LCX, 32, "middle", FS_TITLE, COL.axis, "Phase space  ·  the cause"));
    svg.appendChild(txt(RX + RW / 2, 32, "middle", FS_TITLE, COL.axis, "Rates  ·  the consequence"));

    // ============ LEFT: phase-space crosshair + labels (static) ============
    var gL = el("g", { "class": "lf-phase" });
    gL.appendChild(el("line", { x1: LCX - LHALF, y1: LCY, x2: LCX + LHALF, y2: LCY, stroke: COL.grid, "stroke-width": "1" }));
    gL.appendChild(el("line", { x1: LCX, y1: LCY - LHALF + 22, x2: LCX, y2: LCY + LHALF - 4, stroke: COL.grid, "stroke-width": "1" }));
    gL.appendChild(txt(LCX + LHALF, LCY - 6, "end", FS_AXHINT, COL.faint, "Re", "lf-tick"));
    gL.appendChild(txt(LCX + 8, LCY - LHALF + 28, "start", FS_AXHINT, COL.faint, "Im", "lf-tick"));
    svg.appendChild(gL);

    // ---- lobes + overlap (dynamic) ----
    var lobeL = el("circle", { cy: LCY, r: f.rLobe, fill: "url(#ps-lobe)" });
    var lobeR = el("circle", { cy: LCY, r: f.rLobe, fill: "url(#ps-lobe)" });
    var overlapEl = el("ellipse", { cx: LCX, cy: LCY, rx: f.rOv, ry: f.rLobe, fill: "url(#ps-ov)" });
    svg.appendChild(overlapEl); svg.appendChild(lobeL); svg.appendChild(lobeR);
    var labL = txt(0, LCY - f.rLobe - 8, "middle", FS_LOBE, COL.lobe, "|−α⟩");
    var labR = txt(0, LCY - f.rLobe - 8, "middle", FS_LOBE, COL.lobe, "|+α⟩");
    svg.appendChild(labL); svg.appendChild(labR);

    // ---- bit-flip arrow across the gap (dynamic endpoints) ----
    var arrLine = el("line", { y1: f.arrY, y2: f.arrY, stroke: COL.pf, "stroke-width": "1.6", "marker-end": "url(#ps-arr)", "marker-start": "url(#ps-arr)" });
    svg.appendChild(arrLine);
    svg.appendChild(txt(LCX, f.arrY - 10, "middle", FS_ANNO, COL.pf, "bit-flip (X): cross the gap", "lf-callout"));

    // ---- separation caliper (dynamic endpoints, static label) ----
    var calLine = el("line", { y1: f.calY, y2: f.calY, stroke: COL.axis, "stroke-width": "1" });
    var calTickL = el("line", { y1: f.calY - 4, y2: f.calY + 4, stroke: COL.axis, "stroke-width": "1" });
    var calTickR = el("line", { y1: f.calY - 4, y2: f.calY + 4, stroke: COL.axis, "stroke-width": "1" });
    svg.appendChild(calLine); svg.appendChild(calTickL); svg.appendChild(calTickR);
    svg.appendChild(txt(LCX, f.calY + 19, "middle", FS_ANNO, COL.axis, "separation  2√n̄"));

    // ---- phase-flip note (static) ----
    svg.appendChild(txt(LCX, LCY + LHALF - 2, "middle", FS_ANNO, COL.axis, "phase-flip (Z): dephasing, ~ n̄"));

    // ============ RIGHT: the rate chart (static scaffold) ============
    var gGrid = el("g", { "class": "lf-grid" });
    f.yTicks.forEach(function (t) { gGrid.appendChild(el("line", { x1: RX, y1: t.py, x2: RX + RW, y2: t.py, stroke: COL.grid, "stroke-width": "1" })); });
    svg.appendChild(gGrid);
    var gAx = el("g", { "class": "lf-axes" });
    gAx.appendChild(el("line", { x1: RX, y1: RY, x2: RX, y2: RY + RH, stroke: COL.axis, "stroke-width": "1.5" }));
    gAx.appendChild(el("line", { x1: RX, y1: RY + RH, x2: RX + RW, y2: RY + RH, stroke: COL.axis, "stroke-width": "1.5" }));
    f.xTicks.forEach(function (t) {
      gAx.appendChild(el("line", { x1: t.px, y1: RY + RH, x2: t.px, y2: RY + RH + 5, stroke: COL.axis, "stroke-width": "1" }));
      gAx.appendChild(txt(t.px, RY + RH + 20, "middle", FS_TICK, COL.axis, t.label, "lf-tick"));
    });
    f.yTicks.forEach(function (t) { gAx.appendChild(txt(RX - 8, t.py + 4, "end", FS_TICK, COL.axis, t.label, "lf-tick")); });
    gAx.appendChild(txt(RX + RW / 2, H - 12, "middle", FS_AXTITLE, COL.axis, "cat size  n̄  (mean photon number)"));
    var yl = txt(RX - 50, RY + RH / 2, "middle", FS_AXTITLE, COL.axis, "error rate  (log, normalized)");
    yl.setAttribute("transform", "rotate(-90 " + (RX - 50) + " " + (RY + RH / 2) + ")");
    gAx.appendChild(yl);
    svg.appendChild(gAx);
    var gC = el("g", { "class": "lf-curves" });
    gC.appendChild(el("path", { d: f.bfD, fill: "none", stroke: COL.bf, "stroke-width": "2.5" }));
    gC.appendChild(el("path", { d: f.pfD, fill: "none", stroke: COL.pf, "stroke-width": "2.5" }));
    svg.appendChild(gC);
    // compact legend (bottom-left inside plot) with per-curve direction cues
    var lgx = RX + 14, lgy = RY + RH - 40;
    var gLg = el("g", { "class": "lf-legend" });
    gLg.appendChild(el("line", { x1: lgx, y1: lgy, x2: lgx + 22, y2: lgy, stroke: COL.bf, "stroke-width": "2.5" }));
    gLg.appendChild(txt(lgx + 30, lgy + 4, "start", FS_LEGEND, COL.axis, "bit-flip  ∝ e^(−2n̄)" + CUE_LOWER));
    gLg.appendChild(el("line", { x1: lgx, y1: lgy + 22, x2: lgx + 22, y2: lgy + 22, stroke: COL.pf, "stroke-width": "2.5" }));
    gLg.appendChild(txt(lgx + 30, lgy + 26, "start", FS_LEGEND, COL.axis, "phase-flip  ∝ n̄" + CUE_LOWER));
    svg.appendChild(gLg);
    // marker (dynamic)
    var gM = el("g", { "class": "lf-marker" });
    var mGuide = el("line", { y1: RY, y2: RY + RH, stroke: COL.axis, "stroke-width": "1", "stroke-dasharray": "4 3", "stroke-opacity": "0.7" });
    var mBF = el("circle", { r: "5", fill: COL.bf, stroke: "#fff", "stroke-width": "1.5" });
    var mPF = el("circle", { r: "5", fill: COL.pf, stroke: "#fff", "stroke-width": "1.5" });
    gM.appendChild(mGuide); gM.appendChild(mBF); gM.appendChild(mPF);
    svg.appendChild(gM);

    // ---- dynamic updater (reads a fresh frame; both panels) ----
    function apply(fr) {
      lobeL.setAttribute("cx", fr.lxL); lobeR.setAttribute("cx", fr.lxR);
      labL.setAttribute("x", fr.lxL); labR.setAttribute("x", fr.lxR);
      overlapEl.setAttribute("fill-opacity", fr.overlapOpacity);
      arrLine.setAttribute("x1", fr.lxL + parseFloat(fr.rLobe) * 0.55); arrLine.setAttribute("x2", fr.lxR - parseFloat(fr.rLobe) * 0.55);
      calLine.setAttribute("x1", fr.lxL); calLine.setAttribute("x2", fr.lxR);
      calTickL.setAttribute("x1", fr.lxL); calTickL.setAttribute("x2", fr.lxL);
      calTickR.setAttribute("x1", fr.lxR); calTickR.setAttribute("x2", fr.lxR);
      mGuide.setAttribute("x1", fr.mX); mGuide.setAttribute("x2", fr.mX);
      mBF.setAttribute("cx", fr.mX); mBF.setAttribute("cy", fr.mBFy);
      mPF.setAttribute("cx", fr.mX); mPF.setAttribute("cy", fr.mPFy);
      readout.textContent = fr.readout;
    }

    // ---- controls ----
    var controls = doc.createElement("div"); controls.className = "lf-controls";
    var wrap = doc.createElement("label"); wrap.className = "lf-field";
    wrap.appendChild(doc.createTextNode("Cat size n̄"));
    var input = doc.createElement("input");
    input.type = "range"; input.min = String(nMin); input.max = String(nMax); input.step = "0.1";
    input.value = String(nStart); input.className = "lf-range";
    wrap.appendChild(input); controls.appendChild(wrap);
    var readout = doc.createElement("span"); readout.className = "lf-readout"; controls.appendChild(readout);
    input.addEventListener("input", function () { apply(computeFrame(spec, parseFloat(input.value))); });

    container.appendChild(svg); container.appendChild(controls);
    apply(f);

    return {
      runtimeVersion: DossierFigures.FIGURES_RUNTIME_VERSION,
      getState: function () { var fr = computeFrame(spec, parseFloat(input.value)); return { nbar: fr.nb, separation: 2 * fr.alpha, overlap: gammaBF(fr.nb), bias: gammaPF(fr.nb, fr.gamma) / gammaBF(fr.nb) }; },
      setNbar: function (v) { input.value = String(clamp(v, nMin, nMax)); apply(computeFrame(spec, parseFloat(input.value))); }
    };

    // small DOM helper (live path); closes over el so the poster's string helpers stay separate
    function txt(x, y, anchor, size, fill, str, cls) {
      var a = { x: x, y: y, "text-anchor": anchor, "font-size": String(size), fill: fill };
      if (cls) a["class"] = cls;   // annotation tier (runtime v0.4.0 owns the px size)
      var t = el("text", a);
      t.textContent = str; return t;
    }
    function radialGrad(id, color) {
      var g = el("radialGradient", { id: id, cx: "50%", cy: "50%", r: "50%" });
      g.appendChild(el("stop", { offset: "0%", "stop-color": color, "stop-opacity": "0.92" }));
      g.appendChild(el("stop", { offset: "70%", "stop-color": color, "stop-opacity": "0.35" }));
      g.appendChild(el("stop", { offset: "100%", "stop-color": color, "stop-opacity": "0" }));
      return g;
    }
    function arrowMarker(id, color) {
      var m = el("marker", { id: id, viewBox: "0 0 10 10", refX: "5", refY: "5", markerWidth: "5", markerHeight: "5", orient: "auto-start-reverse" });
      m.appendChild(el("path", { d: "M0 1L9 5L0 9z", fill: color }));
      return m;
    }
  }

  // -------------------------------------------------------------------------
  // POSTER: renderQCPhasespacePosterSVG(spec) — pure string, static at posterNbar.
  // Same computeFrame + same type sizes -> floor == ceiling by construction.
  // -------------------------------------------------------------------------
  function renderQCPhasespacePosterSVG(spec) {
    if (typeof spec === "string") { try { spec = JSON.parse(spec); } catch (e) { return ""; } }
    spec = spec || {};
    var nMin = num(spec.nbarMin, 0.5), nMax = num(spec.nbarMax, 8);
    var f = computeFrame(spec, clamp(num(spec.posterNbar, (nMin + nMax) / 2), nMin, nMax));
    var rLobe = f.rLobe, s = "";

    s += '<svg viewBox="0 0 ' + W + ' ' + H + '" width="100%" class="lf-svg" role="img" aria-label="' + escAttr(f.ariaLabel) + '">';
    s += '<defs>';
    s += radialGradS("ps-lobe", COL.lobe) + radialGradS("ps-ov", COL.overlap);
    s += '<marker id="ps-arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 1L9 5L0 9z" fill="' + COL.pf + '"></path></marker>';
    s += '</defs>';

    s += textS(LCX, 32, "middle", FS_TITLE, COL.axis, "Phase space  ·  the cause");
    s += textS(RX + RW / 2, 32, "middle", FS_TITLE, COL.axis, "Rates  ·  the consequence");

    // LEFT crosshair + labels
    s += '<g class="lf-phase">';
    s += lineS(LCX - LHALF, LCY, LCX + LHALF, LCY, COL.grid, 1);
    s += lineS(LCX, LCY - LHALF + 22, LCX, LCY + LHALF - 4, COL.grid, 1);
    s += textS(LCX + LHALF, LCY - 6, "end", FS_AXHINT, COL.faint, "Re", "lf-tick");
    s += textS(LCX + 8, LCY - LHALF + 28, "start", FS_AXHINT, COL.faint, "Im", "lf-tick");
    s += '</g>';

    // overlap + lobes
    s += '<ellipse cx="' + LCX + '" cy="' + LCY + '" rx="' + f.rOv + '" ry="' + rLobe + '" fill="url(#ps-ov)" fill-opacity="' + f.overlapOpacity + '"></ellipse>';
    s += '<circle cx="' + f.lxL + '" cy="' + LCY + '" r="' + rLobe + '" fill="url(#ps-lobe)"></circle>';
    s += '<circle cx="' + f.lxR + '" cy="' + LCY + '" r="' + rLobe + '" fill="url(#ps-lobe)"></circle>';
    s += textS(f.lxL, LCY - parseFloat(rLobe) - 8, "middle", FS_LOBE, COL.lobe, "|−α⟩");
    s += textS(f.lxR, LCY - parseFloat(rLobe) - 8, "middle", FS_LOBE, COL.lobe, "|+α⟩");

    // bit-flip arrow
    s += '<line x1="' + r2(f.lxL + parseFloat(rLobe) * 0.55) + '" y1="' + f.arrY + '" x2="' + r2(f.lxR - parseFloat(rLobe) * 0.55) + '" y2="' + f.arrY + '" stroke="' + COL.pf + '" stroke-width="1.6" marker-end="url(#ps-arr)" marker-start="url(#ps-arr)"></line>';
    s += textS(LCX, f.arrY - 10, "middle", FS_ANNO, COL.pf, "bit-flip (X): cross the gap", "lf-callout");

    // caliper + phase-flip note
    s += lineS(f.lxL, f.calY, f.lxR, f.calY, COL.axis, 1);
    s += lineS(f.lxL, f.calY - 4, f.lxL, f.calY + 4, COL.axis, 1);
    s += lineS(f.lxR, f.calY - 4, f.lxR, f.calY + 4, COL.axis, 1);
    s += textS(LCX, f.calY + 19, "middle", FS_ANNO, COL.axis, "separation  2√n̄");
    s += textS(LCX, LCY + LHALF - 2, "middle", FS_ANNO, COL.axis, "phase-flip (Z): dephasing, ~ n̄");

    // RIGHT chart
    s += '<g class="lf-grid">';
    f.yTicks.forEach(function (t) { s += lineS(RX, t.py, RX + RW, t.py, COL.grid, 1); });
    s += '</g><g class="lf-axes">';
    s += lineS(RX, RY, RX, RY + RH, COL.axis, 1.5) + lineS(RX, RY + RH, RX + RW, RY + RH, COL.axis, 1.5);
    f.xTicks.forEach(function (t) {
      s += lineS(t.px, RY + RH, t.px, RY + RH + 5, COL.axis, 1);
      s += textS(t.px, RY + RH + 20, "middle", FS_TICK, COL.axis, t.label, "lf-tick");
    });
    f.yTicks.forEach(function (t) { s += textS(RX - 8, t.py + 4, "end", FS_TICK, COL.axis, t.label, "lf-tick"); });
    s += textS(RX + RW / 2, H - 12, "middle", FS_AXTITLE, COL.axis, "cat size  n̄  (mean photon number)");
    s += '<text x="' + (RX - 50) + '" y="' + (RY + RH / 2) + '" text-anchor="middle" font-size="' + FS_AXTITLE + '" fill="' + COL.axis + '" transform="rotate(-90 ' + (RX - 50) + ' ' + (RY + RH / 2) + ')">' + escTxt("error rate  (log, normalized)") + '</text>';
    s += '</g><g class="lf-curves">';
    s += '<path d="' + f.bfD + '" fill="none" stroke="' + COL.bf + '" stroke-width="2.5"></path>';
    s += '<path d="' + f.pfD + '" fill="none" stroke="' + COL.pf + '" stroke-width="2.5"></path>';
    s += '</g>';
    var lgx = RX + 14, lgy = RY + RH - 40;
    s += '<g class="lf-legend">';
    s += lineS(lgx, lgy, lgx + 22, lgy, COL.bf, 2.5) + textS(lgx + 30, lgy + 4, "start", FS_LEGEND, COL.axis, "bit-flip  ∝ e^(−2n̄)" + CUE_LOWER);
    s += lineS(lgx, lgy + 22, lgx + 22, lgy + 22, COL.pf, 2.5) + textS(lgx + 30, lgy + 26, "start", FS_LEGEND, COL.axis, "phase-flip  ∝ n̄" + CUE_LOWER);
    s += '</g>';
    s += '<g class="lf-marker">';
    s += '<line x1="' + f.mX + '" y1="' + RY + '" x2="' + f.mX + '" y2="' + (RY + RH) + '" stroke="' + COL.axis + '" stroke-width="1" stroke-dasharray="4 3" stroke-opacity="0.7"></line>';
    s += '<circle cx="' + f.mX + '" cy="' + f.mBFy + '" r="5" fill="' + COL.bf + '" stroke="#fff" stroke-width="1.5"></circle>';
    s += '<circle cx="' + f.mX + '" cy="' + f.mPFy + '" r="5" fill="' + COL.pf + '" stroke="#fff" stroke-width="1.5"></circle>';
    s += '</g>';

    // baked readout (interactive in the ceiling)
    s += textS(LCX - LHALF + 8, H - 12, "start", FS_READOUT, COL.axis, f.readout);
    s += '</svg>';
    return s;
  }

  // string-emit helpers (poster path)
  function lineS(x1, y1, x2, y2, c, w) { return '<line x1="' + r2(x1) + '" y1="' + r2(y1) + '" x2="' + r2(x2) + '" y2="' + r2(y2) + '" stroke="' + c + '" stroke-width="' + w + '"></line>'; }
  function textS(x, y, anchor, size, fill, str, cls) { return '<text ' + (cls ? 'class="' + cls + '" ' : '') + 'x="' + r2(x) + '" y="' + r2(y) + '" text-anchor="' + anchor + '" font-size="' + size + '" fill="' + fill + '">' + escTxt(str) + '</text>'; }
  function radialGradS(id, color) {
    return '<radialGradient id="' + id + '" cx="50%" cy="50%" r="50%">' +
      '<stop offset="0%" stop-color="' + color + '" stop-opacity="0.92"></stop>' +
      '<stop offset="70%" stop-color="' + color + '" stop-opacity="0.35"></stop>' +
      '<stop offset="100%" stop-color="' + color + '" stop-opacity="0"></stop></radialGradient>';
  }

  DossierFigures.renderQCPhasespace = renderQCPhasespace;
  DossierFigures.renderQCPhasespacePosterSVG = renderQCPhasespacePosterSVG;
  DossierFigures.registerPoster("qc-phasespace", renderQCPhasespacePosterSVG);
})(typeof window !== "undefined" ? window : null);
