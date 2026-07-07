/*
 * qc-race.js — "rates, not stocks" render module for Open Dossier living figures
 * (Dossier QC-Accelerate-002, Chapter 2, Fig 3).
 *
 * WHAT THIS IS
 *   Three small-multiple panels of the race section's OWN cited numbers, drawn.
 *   MONEY: China R&D as a share of the US (PPP), to the 2024 crossover. PEOPLE: the
 *   top-cited-scientist flip, 2020-2024. QUANTUM (log y): BOTH blocs' published
 *   superconducting trajectories — Google (US) and Zuchongzhi (CN), same metric,
 *   DIFFERENT verification — plus China's photonic Jiuzhang series (reported). All
 *   three panels always visible; the buttons FOCUS one (others dim); default MONEY.
 *   Points carry a tap/hover detail naming the MACHINE and BLOC (live only).
 *
 * HARD DATA DISCIPLINE
 *   Every plotted value is a LITERAL below with a source comment naming its cite
 *   key — NO interpolated curve. Dashed arrows are GUIDES between the published
 *   points of a SINGLE source's series. The REPORTED series (Jiuzhang) is labelled
 *   "(reported)"; the supply-chain marks "(trade press)". The verification contrast
 *   is stated, not implied: Willow's below-threshold EC is peer-reviewed, the
 *   Zuchongzhi-line EC claim is program-reported.
 *
 * THE COMPOSITION LAW (per qc-loop): general primitives from the runtime; geometry
 *   computed ONCE as an OP LIST, consumed by BOTH the live el() and poster string
 *   emitters (floor == ceiling); tier classes only. Long/legend text opts out of
 *   text-fit counter-scale (lf-scale-with-art) so it never clips. Static figure.
 */
(function (root) {
  "use strict";
  var NS = root && root.DossierFigures;
  if (!NS) { if (root && root.console) root.console.error("[qc-race] figures.js runtime not found — load figures.js before qc-race.js"); return; }
  var DossierFigures = NS;
  var el = DossierFigures.el, r2 = DossierFigures.r2, escAttr = DossierFigures.escAttr,
      escTxt = DossierFigures.escTxt, dedupPoster = DossierFigures.dedupPoster;

  var W = 990, H = 460, DIM = "0.25";
  var COL = { us: "#c2562f", cn: "#2f6f8f", photon: "#8a6fb0", axis: "#5a6b70", grid: "#d7dee0", mark: "#5a6b70", ref: "#9aa3a6", shade: "#0c8f86" };
  var DEFAULT = 0;
  function log10(x) { return Math.log(x) / Math.LN10; }

  function computeRace() {
    var panels = [moneyPanel(70), peoplePanel(395), quantumPanel(720)];
    // figure-level QUANTUM key: bloc-explicit legend + verification-contrast note (always visible).
    var key = [
      { t: "circle", x: 76, y: 344, r: 5, fill: COL.cn },
      { t: "text", x: 88, y: 348, anchor: "start", cls: "lf-tick", color: COL.axis, sa: 1, str: "Zuchongzhi (CN, superconducting processor) — qubits" },      // [zuchongzhi]
      { t: "circle", x: 76, y: 362, r: 5, fill: COL.us },
      { t: "text", x: 88, y: 366, anchor: "start", cls: "lf-tick", color: COL.axis, sa: 1, str: "Google (US, superconducting) — qubits" },                    // [google]
      { t: "circle", x: 76, y: 380, r: 5, fill: COL.photon },
      { t: "text", x: 88, y: 384, anchor: "start", cls: "lf-tick", color: COL.axis, sa: 1, str: "Jiuzhang (CN, photonic machine) — detected photons (reported)" }, // [talent, reported]
      { t: "text", x: 70, y: 414, anchor: "start", cls: "lf-tick", color: COL.axis, sa: 1, str: "same scale, different verification — Willow below-threshold EC: peer-reviewed (Nature 2024) ·" },   // [google]
      { t: "text", x: 70, y: 432, anchor: "start", cls: "lf-tick", color: COL.axis, sa: 1, str: "Zuchongzhi-line EC claim: program-reported · Zuchongzhi-3 sampling: 6 orders beyond SYC-67/70 (PRL 2025)" }  // [zuchongzhi]
    ];
    return { W: W, H: H, panels: panels, key: key,
      ariaLabel: "Three panels of cited figures from the race section: China's R&D reaching and passing the US on a purchasing-power-parity basis by 2024; the top-cited-scientist counts of China and the US crossing over between 2020 and 2024; and, on a log scale, both blocs' published superconducting quantum trajectories — Google and Zuchongzhi qubit counts, same metric but Google's error-correction peer-reviewed and the Zuchongzhi line's program-reported — plus China's photonic Jiuzhang detected-photon count, labelled reported." };
  }

  function frame(px, py, pw, ph) {
    return [
      { t: "line", x1: px, y1: py, x2: px, y2: py + ph, color: COL.axis, w: 1.5 },
      { t: "line", x1: px, y1: py + ph, x2: px + pw, y2: py + ph, color: COL.axis, w: 1.5 }
    ];
  }

  // ---- MONEY: China R&D as % of US (PPP). 72% (2013), 96% (2023), 102% (2024). [oecd/talent] ----
  function moneyPanel(px) {
    var py = 100, pw = 200, ph = 175, yLo = 60, yHi = 110, xLo = 2012.5, xHi = 2024.5;
    function X(y) { return r2(px + (y - xLo) / (xHi - xLo) * pw); }
    function Y(p) { return r2(py + (yHi - p) / (yHi - yLo) * ph); }
    var pts = [
      { yr: 2013, v: 72,  d: "2013 · China R&D ≈ 72% of the US (PPP) — the trajectory the crossover sits on." },  // [oecd/talent]
      { yr: 2023, v: 96,  d: "2023 · ≈ 96% of the US (PPP)." },                                                    // [oecd/talent]
      { yr: 2024, v: 102, d: "2024 · $1.03T vs $1.01T — China crosses the US on PPP." }                            // [oecd] $1.03T/$1.01T ≈ 102%
    ];
    var ops = frame(px, py, pw, ph);
    ops.push({ t: "line", x1: px, y1: Y(100), x2: px + pw, y2: Y(100), color: COL.ref, w: 1.5, dash: "6 4" });
    ops.push({ t: "text", x: px + pw, y: Y(100) - 5, anchor: "end", cls: "lf-tick", color: COL.axis, str: "US = 100%" });
    [60, 80, 100].forEach(function (p) { ops.push({ t: "text", x: px - 6, y: Y(p) + 3, anchor: "end", cls: "lf-tick", color: COL.axis, str: p + "%" }); });
    [2013, 2024].forEach(function (y) { ops.push({ t: "text", x: X(y), y: py + ph + 16, anchor: "middle", cls: "lf-tick", color: COL.axis, str: String(y) }); });
    ops.push({ t: "path", d: "M" + X(2013) + " " + Y(72) + "L" + X(2023) + " " + Y(96) + "L" + X(2024) + " " + Y(102), color: COL.cn, w: 2, dash: "5 4", marker: 1 });
    pts.forEach(function (p) { ops.push({ t: "circle", x: X(p.yr), y: Y(p.v), r: 5, fill: COL.cn, detail: p.d }); });
    ops.push({ t: "text", x: X(2024), y: Y(102) - 10, anchor: "end", cls: "lf-axis", color: COL.cn, str: "102% · crossover" });
    ops.push({ t: "text", x: px, y: py + ph + 36, anchor: "start", cls: "lf-tick", color: COL.axis, str: "avg >14%/yr since 2004 — about 2x the US pace" });  // [oecd]
    return { key: "money", header: "MONEY — China R&D as % of US (PPP)", cx: px + pw / 2, ops: ops };
  }

  // ---- PEOPLE: top-cited scientists. US 36,599->31,781 ; China 18,805->32,511 (2020-2024). [talent] ----
  function peoplePanel(px) {
    var py = 100, pw = 200, ph = 175, yLo = 15000, yHi = 38000, xLo = 2019.5, xHi = 2024.5;
    function X(y) { return r2(px + (y - xLo) / (xHi - xLo) * pw); }
    function Y(v) { return r2(py + (yHi - v) / (yHi - yLo) * ph); }
    var ops = frame(px, py, pw, ph);
    ops.push({ t: "rect", x: X(2022.4), y: Y(34000), w: X(2024) - X(2022.4), h: Y(30000) - Y(34000), fill: COL.shade, opacity: "0.08" });
    ops.push({ t: "text", x: X(2023.2), y: Y(35200), anchor: "middle", cls: "lf-tick", color: COL.axis, str: "flip, 2020-2024" });
    [20000, 30000].forEach(function (v) { ops.push({ t: "text", x: px - 6, y: Y(v) + 3, anchor: "end", cls: "lf-tick", color: COL.axis, str: (v / 1000) + "k" }); });
    [2020, 2024].forEach(function (y) { ops.push({ t: "text", x: X(y), y: py + ph + 16, anchor: "middle", cls: "lf-tick", color: COL.axis, str: String(y) }); });
    ops.push({ t: "path", d: "M" + X(2020) + " " + Y(36599) + "L" + X(2024) + " " + Y(31781), color: COL.us, w: 2, dash: "5 4", marker: 1 });
    ops.push({ t: "circle", x: X(2020), y: Y(36599), r: 5, fill: COL.us, detail: "2020 · US top-cited scientists: 36,599." });
    ops.push({ t: "circle", x: X(2024), y: Y(31781), r: 5, fill: COL.us, detail: "2024 · US top-cited scientists: 31,781 (down)." });
    ops.push({ t: "text", x: X(2020) - 6, y: Y(36599) - 6, anchor: "start", cls: "lf-tick", color: COL.us, str: "US" });
    ops.push({ t: "path", d: "M" + X(2020) + " " + Y(18805) + "L" + X(2024) + " " + Y(32511), color: COL.cn, w: 2, dash: "5 4", marker: 1 });
    ops.push({ t: "circle", x: X(2020), y: Y(18805), r: 5, fill: COL.cn, detail: "2020 · China top-cited scientists: 18,805." });
    ops.push({ t: "circle", x: X(2024), y: Y(32511), r: 5, fill: COL.cn, detail: "2024 · China top-cited scientists: 32,511 (up)." });
    ops.push({ t: "text", x: X(2020) - 6, y: Y(18805) + 14, anchor: "start", cls: "lf-tick", color: COL.cn, str: "China" });
    ops.push({ t: "text", x: px, y: py + ph + 36, anchor: "start", cls: "lf-tick", color: COL.axis, str: "40,000-paper bibliometric study (CSIS 2026)" });  // [talent]
    return { key: "people", header: "PEOPLE — top-cited scientists", cx: px + pw / 2, ops: ops };
  }

  // ---- QUANTUM (log y): both blocs' superconducting lines + China photonic. ----
  //   Google (US): 53 (2019) · 72 (2023) · 105 (2024, Willow)  [google]
  //   Zuchongzhi (CN sc): 66 (2021) · 105 (2025)               [zuchongzhi]
  //   Jiuzhang (CN photonic): 76 (2020) · 3,050 (2025)         [talent, REPORTED]
  function quantumPanel(px) {
    var py = 100, pw = 200, ph = 175, eLo = 1, eHi = 4, xLo = 2018.5, xHi = 2025.5;
    function X(y) { return r2(px + (y - xLo) / (xHi - xLo) * pw); }
    function Y(v) { return r2(py + (eHi - log10(v)) / (eHi - eLo) * ph); }
    var ops = frame(px, py, pw, ph);
    [1, 2, 3, 4].forEach(function (e) { ops.push({ t: "text", x: px - 6, y: Y(Math.pow(10, e)) + 3, anchor: "end", cls: "lf-tick", color: COL.axis, str: "10^" + e }); });
    [2019, 2022, 2025].forEach(function (y) { ops.push({ t: "text", x: X(y), y: py + ph + 16, anchor: "middle", cls: "lf-tick", color: COL.axis, str: String(y) }); });
    // supply-chain marks (trade press)
    ops.push({ t: "line", x1: X(2024.7), y1: py, x2: X(2024.7), y2: py + ph, color: COL.mark, w: 1, dash: "3 3" });
    ops.push({ t: "text", x: X(2024.7), y: py - 4, anchor: "end", cls: "lf-tick", color: COL.mark, sa: 1, str: "Sept 2024 controls · ~14 mo → ~10 mK domestic (trade press)" });  // [supplychain]
    // Google (US superconducting): 53 -> 72 -> 105
    ops.push({ t: "path", d: "M" + X(2019) + " " + Y(53) + "L" + X(2023) + " " + Y(72) + "L" + X(2024) + " " + Y(105), color: COL.us, w: 2, dash: "5 4", marker: 1 });
    ops.push({ t: "circle", x: X(2019), y: Y(53),  r: 5, fill: COL.us, detail: "2019 · Google Sycamore (US, superconducting): 53-qubit quantum-supremacy experiment." });
    ops.push({ t: "circle", x: X(2023), y: Y(72),  r: 5, fill: COL.us, detail: "2023 · Google (US, superconducting): 72-qubit surface-code scaling result." });
    ops.push({ t: "circle", x: X(2024), y: Y(105), r: 5, fill: COL.us, detail: "2024 · Google Willow (US, superconducting): 105 qubits — first peer-reviewed below-threshold surface-code memory." });
    ops.push({ t: "text", x: X(2024) + 4, y: Y(105) - 6, anchor: "end", cls: "lf-tick", color: COL.us, str: "Google" });
    // Zuchongzhi (CN superconducting): 66 -> 105
    ops.push({ t: "path", d: "M" + X(2021) + " " + Y(66) + "L" + X(2025) + " " + Y(105), color: COL.cn, w: 2, dash: "5 4", marker: 1 });
    ops.push({ t: "circle", x: X(2021), y: Y(66),  r: 5, fill: COL.cn, detail: "2021 · Zuchongzhi (China, superconducting): 66 qubits." });
    ops.push({ t: "circle", x: X(2025), y: Y(105), r: 5, fill: COL.cn, detail: "2025 · Zuchongzhi 3.0 (China, superconducting): 105 qubits; sampling 6 orders beyond SYC-67/70 (PRL 2025). EC claim program-reported." });
    ops.push({ t: "text", x: X(2025), y: Y(105) + 16, anchor: "end", cls: "lf-tick", color: COL.cn, str: "Zuchongzhi" });
    // Jiuzhang (CN photonic, REPORTED): 76 -> 3,050
    ops.push({ t: "path", d: "M" + X(2020) + " " + Y(76) + "L" + X(2025) + " " + Y(3050), color: COL.photon, w: 2, dash: "5 4", marker: 1 });
    ops.push({ t: "circle", x: X(2020), y: Y(76),   r: 5, fill: COL.photon, detail: "2020 · Jiuzhang (China, photonic): 76 detected photons (reported)." });
    ops.push({ t: "circle", x: X(2025), y: Y(3050), r: 5, fill: COL.photon, detail: "2025 · Jiuzhang (China, photonic): ~3,050 detected photons — fortyfold in five years (reported)." });
    ops.push({ t: "text", x: X(2025), y: Y(3050) - 8, anchor: "end", cls: "lf-tick", color: COL.photon, str: "Jiuzhang (rep.)" });
    return { key: "quantum", header: "QUANTUM — published trajectories (log)", cx: px + pw / 2, ops: ops };
  }

  function fail(container, msg) {
    if (root && root.console) root.console.error("[qc-race] " + msg);
    if (container && container.appendChild) {
      var doc = (root && root.document) || container.ownerDocument;
      var p = doc.createElement("p"); p.className = "lf-fallback"; p.textContent = "Figure unavailable: " + msg; container.appendChild(p);
    }
    return null;
  }
  function injectToggleStyle(doc) {
    if (!doc || !doc.getElementById || doc.getElementById("qc-race-toggle-style")) return;
    var st = doc.createElement("style"); st.id = "qc-race-toggle-style";
    st.textContent =
      '.lf-controls .lf-btn{border-radius:var(--r-sm,10px);}' +
      '.lf-controls .lf-btn[aria-pressed="true"]{background:#5a6b70;color:#fff;border-color:#5a6b70;}' +
      '#lf-lightbox .lf-controls .lf-btn[aria-pressed="true"]{background:#5a6b70;color:#fff;border-color:#5a6b70;}';
    (doc.head || doc.documentElement).appendChild(st);
  }

  // ===== LIVE =====
  function renderQCRace(container, spec) {
    if (!container) return fail(null, "no container");
    var doc = (root && root.document) || container.ownerDocument;
    injectToggleStyle(doc);
    if (spec == null && container.getAttribute) spec = container.getAttribute("data-figure");
    if (typeof spec === "string") { try { spec = JSON.parse(spec); } catch (e) { return fail(container, "data-figure is not valid JSON"); } }
    dedupPoster(container);
    var g = computeRace();

    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, width: "100%", "class": "lf-svg", role: "img", "aria-label": g.ariaLabel });
    var defs = el("defs", {});
    var mk = el("marker", { id: "race-arr", viewBox: "0 0 10 10", refX: "8", refY: "5", markerWidth: "6.5", markerHeight: "6.5", orient: "auto-start-reverse" });
    mk.appendChild(el("path", { d: "M0 1L9 5L0 9z", fill: COL.axis })); defs.appendChild(mk); svg.appendChild(defs);

    var readout = doc.createElement("span"); readout.className = "lf-readout"; readout.setAttribute("aria-live", "polite");
    var HINT = "Focus a panel; hover a point for its figure. Points as published — dashed arrows are reading guides, not data.";
    var groups = [];
    g.panels.forEach(function (P) {
      var gp = el("g", { "class": "lf-panel", "data-panel": P.key });
      gp.appendChild(mkText(P.cx, 72, "middle", "lf-callout lf-scale-with-art", COL.axis, P.header));
      P.ops.forEach(function (op) { drawOp(gp, op, readout, HINT); });
      svg.appendChild(gp); groups.push(gp);
    });
    // figure-level quantum key (always visible)
    var gk = el("g", { "class": "lf-key" });
    g.key.forEach(function (op) { drawOp(gk, op, readout, HINT); });
    svg.appendChild(gk);
    container.appendChild(svg);

    var controls = doc.createElement("div"); controls.className = "lf-controls";
    var labels = [["money", "Money"], ["people", "People"], ["quantum", "Quantum"]];
    var btns = labels.map(function (L) { var b = doc.createElement("button"); b.type = "button"; b.className = "lf-btn"; b.textContent = L[1]; controls.appendChild(b); return b; });
    var resetBtn = doc.createElement("button"); resetBtn.type = "button"; resetBtn.className = "lf-btn"; resetBtn.textContent = "Reset"; controls.appendChild(resetBtn);
    controls.appendChild(readout); container.appendChild(controls);

    var current = DEFAULT;
    function setMode(i) {
      current = (i < 0 || i > 2) ? DEFAULT : i;
      groups.forEach(function (gp, k) { gp.setAttribute("opacity", k === current ? "1" : DIM); });
      btns.forEach(function (b, k) { b.setAttribute("aria-pressed", k === current ? "true" : "false"); });
      readout.textContent = HINT;
    }
    btns.forEach(function (b, i) { b.addEventListener("click", function () { setMode(i); }); });
    resetBtn.addEventListener("click", function () { setMode(DEFAULT); });
    setMode(DEFAULT);

    var handle = { runtimeVersion: DossierFigures.FIGURES_RUNTIME_VERSION, getState: function () { return { panel: current }; }, setMode: setMode };
    container.__lfHandle = handle;
    return handle;

    function mkText(x, y, anchor, cls, fill, str) { var t = el("text", { x: x, y: y, "text-anchor": anchor, fill: fill, "class": cls }); t.textContent = str; return t; }
    function drawOp(parent, op, readout, HINT) {
      if (op.t === "line") { var l = el("line", { x1: op.x1, y1: op.y1, x2: op.x2, y2: op.y2, stroke: op.color, "stroke-width": String(op.w || 1) }); if (op.dash) l.setAttribute("stroke-dasharray", op.dash); parent.appendChild(l); }
      else if (op.t === "path") { var pa = el("path", { d: op.d, fill: "none", stroke: op.color, "stroke-width": String(op.w || 1) }); if (op.dash) pa.setAttribute("stroke-dasharray", op.dash); if (op.marker) pa.setAttribute("marker-end", "url(#race-arr)"); parent.appendChild(pa); }
      else if (op.t === "rect") { parent.appendChild(el("rect", { x: op.x, y: op.y, width: op.w, height: op.h, fill: op.fill, "fill-opacity": op.opacity })); }
      else if (op.t === "circle") { var c = el("circle", { cx: op.x, cy: op.y, r: String(op.r), fill: op.fill, stroke: "#fff", "stroke-width": "1.5" }); if (op.detail) attachDetail(c, op.detail, readout, HINT); parent.appendChild(c); }
      else if (op.t === "text") { var t = el("text", { x: op.x, y: op.y, "text-anchor": op.anchor, fill: op.color, "class": op.cls + (op.sa ? " lf-scale-with-art" : "") }); t.textContent = op.str; parent.appendChild(t); }
    }
    function attachDetail(node, detail, readout, HINT) {
      node.setAttribute("tabindex", "0"); node.setAttribute("role", "img"); node.setAttribute("aria-label", detail); node.style.cursor = "pointer";
      var show = function () { readout.textContent = detail; }, clear = function () { readout.textContent = HINT; };
      node.addEventListener("mouseenter", show); node.addEventListener("mouseleave", clear);
      node.addEventListener("focus", show); node.addEventListener("blur", clear); node.addEventListener("click", show);
    }
  }

  // ===== POSTER (pure string; all panels + key, static) =====
  function renderQCRacePosterSVG() {
    var g = computeRace();
    var s = '<svg viewBox="0 0 ' + W + ' ' + H + '" width="100%" class="lf-svg" role="img" aria-label="' + escAttr(g.ariaLabel) + '">';
    s += '<defs><marker id="race-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse"><path d="M0 1L9 5L0 9z" fill="' + COL.axis + '"></path></marker></defs>';
    g.panels.forEach(function (P) {
      s += '<g class="lf-panel" data-panel="' + P.key + '">';
      s += textS(P.cx, 72, "middle", "lf-callout", COL.axis, P.header, 1);
      P.ops.forEach(function (op) { s += opS(op); });
      s += '</g>';
    });
    s += '<g class="lf-key">'; g.key.forEach(function (op) { s += opS(op); }); s += '</g>';
    s += '</svg>';
    return s;
  }
  function opS(op) {
    if (op.t === "line") return '<line x1="' + op.x1 + '" y1="' + op.y1 + '" x2="' + op.x2 + '" y2="' + op.y2 + '" stroke="' + op.color + '" stroke-width="' + (op.w || 1) + '"' + (op.dash ? ' stroke-dasharray="' + op.dash + '"' : '') + '></line>';
    if (op.t === "path") return '<path d="' + op.d + '" fill="none" stroke="' + op.color + '" stroke-width="' + (op.w || 1) + '"' + (op.dash ? ' stroke-dasharray="' + op.dash + '"' : '') + (op.marker ? ' marker-end="url(#race-arr)"' : '') + '></path>';
    if (op.t === "rect") return '<rect x="' + op.x + '" y="' + op.y + '" width="' + op.w + '" height="' + op.h + '" fill="' + op.fill + '" fill-opacity="' + op.opacity + '"></rect>';
    if (op.t === "circle") return '<circle cx="' + op.x + '" cy="' + op.y + '" r="' + op.r + '" fill="' + op.fill + '" stroke="#fff" stroke-width="1.5"></circle>';
    if (op.t === "text") return textS(op.x, op.y, op.anchor, op.cls, op.color, op.str, op.sa);
    return "";
  }
  function textS(x, y, anchor, cls, fill, str, sa) {
    return '<text class="' + cls + (sa ? " lf-scale-with-art" : "") + '" x="' + r2(x) + '" y="' + r2(y) + '" text-anchor="' + anchor + '" fill="' + fill + '">' + escTxt(str) + '</text>';
  }

  DossierFigures.renderQCRace = renderQCRace;
  DossierFigures.renderQCRacePosterSVG = renderQCRacePosterSVG;
  DossierFigures.registerPoster("qc-race", renderQCRacePosterSVG);
  DossierFigures.registerRenderer("qc-race", renderQCRace);
})(typeof window !== "undefined" ? window : null);
