/*
 * qc-gapmap.js — "two stacks, one missing crown" render module for Open Dossier
 * living figures (Dossier QC-Accelerate-002, Chapter 3, Fig 2).
 *
 * WHAT THIS IS
 *   Two co-location stacks drawn cell-by-cell FROM THIS DOSSIER'S OWN CITATIONS:
 *   the Hefei stack and the allied park (IQMP). Cell states are an evidence
 *   grammar — SOLID = cited in this dossier; HATCHED = reported / interested-
 *   party grade; EMPTY = absent from the public record (the gap, coral-dashed).
 *   Rows build upward like a building; the top row — the closed loop on qubits —
 *   is the missing crown on BOTH towers. Hefei has the robots; the allies have
 *   the referee; nobody has the loop. The chapter's ask is the empty allied cells.
 *
 * HARD DATA DISCIPLINE
 *   Every cell is a LITERAL below with a source comment naming its cite card or
 *   ledger row. A cell this dossier cannot support is drawn EMPTY or HATCHED —
 *   never filled in. No measured data; a status map, statuses as audited.
 *
 * SUSTAINABILITY LAWS: zero deps, pure vanilla, vendored first-party; reader-side only.
 */
(function (root) {
  "use strict";

  var NS = root && root.DossierFigures;
  if (!NS) { if (root && root.console) root.console.error("[qc-gapmap] figures.js runtime not found — load figures.js before qc-gapmap.js"); return; }
  var DossierFigures = NS;
  var el = DossierFigures.el, r2 = DossierFigures.r2, escAttr = DossierFigures.escAttr,
      escTxt = DossierFigures.escTxt, dedupPoster = DossierFigures.dedupPoster;

  var COL = { hefei: "#2f6f8f", allied: "#0c8f86", axis: "#5a6b70", gap: "#c2562f", grid: "#d7dee0", ink: "#3a474b" };
  var W = 960, CELL_W = 300, CELL_H = 56, GAP = 10;
  var HX = 60, AX = 600;                     // tower left edges (Hefei, allied)
  var MIDX = (HX + CELL_W + AX) / 2;          // center rail x for row labels
  var TOP = 120;                              // first (crown) row y

  // ---- DATA (bottom-to-top rows; every cell names its source) ----
  // state: "solid" (cited) | "hatched" (reported / interested-party) | "empty" (absent from record)
  var ROWS = [
    { label: "THE LOOP, ON QUBITS",        // crown row — drawn first (top)
      hefei:  { state: "empty",  text: "closed by no public system", detail: "Hefei · THE LOOP — no public system anywhere closes an autonomous decide-make-measure-learn loop on a qubit figure of merit; the finish line is empty on both towers. [ledger C06]" },   // [C06]
      allied: { state: "empty",  text: "closed by no public system", detail: "Allied · THE LOOP — same absence: the loop on qubits is closed by no public system anywhere. The chapter's ask is to fund this row first — single-digit $B/yr. [ledger C06, C16]" } }, // [C06, C16]
    { label: "VERIFICATION CULTURE",
      hefei:  { state: "hatched", text: "EC claims program-reported", detail: "Hefei · VERIFICATION — the Zuchongzhi line's error-correction claims are program-reported, not peer-published: the verification contrast this dossier tracks, restated as this tower's weak layer. [zuchongzhi card]" }, // [zuchongzhi — EC caveat]
      allied: { state: "solid",  text: "DARPA Quantum Proving Ground", detail: "Allied · VERIFICATION — a DARPA proving ground sits on the park site: adversarial benchmarking funded as infrastructure, the allied comparative advantage. [iqmp card]" } },        // [iqmp]
    { label: "AUTONOMOUS LABS & ROBOTS",
      hefei:  { state: "solid",  text: "Xiao Lai / ChemAgents, 24/7", detail: "Hefei · ROBOTS — the 24/7 Xiao Lai / ChemAgents robotic-chemist lineage runs at USTC / Hefei National Laboratory, peer-published. [chemagents card, JACS 2025]" },                      // [chemagents]
      allied: { state: "empty",  text: "not in the public record", detail: "Allied · ROBOTS — no public IQMP document funds autonomous experimentation, wafer-scale probers, robotic synthesis, or active-learning stacks as deliverables. The gap the chapter prices at 35% to close by end-2028. [section 04; ledger C16]" } }, // [§04, C16]
    { label: "CRYOGENICS",
      hefei:  { state: "hatched", text: "10+ domestic makers, ~10 mK", detail: "Hefei · CRYO — after the 2024 five-party controls, China fielded 10+ domestic dilution-fridge makers with production near 10 mK — trade-press and interested-party figures, carried at REPORTED grade. [supplychain card]" }, // [supplychain]
      allied: { state: "solid",  text: "shared industrial cryoplant", detail: "Allied · CRYO — a shared industrial cryoplant is in IQMP phase one, publicly documented. [iqmp card]" } },                                                                                  // [iqmp]
    { label: "QUBIT PLATFORMS",
      hefei:  { state: "solid",  text: "Zuchongzhi 105q (PRL)", detail: "Hefei · QUBITS — the Zuchongzhi superconducting line, 66 to 105 qubits 2021-2025, random-circuit sampling peer-published in PRL; its error-correction claims stay program-reported (see the verification row). [zuchongzhi card]" }, // [zuchongzhi]
      allied: { state: "solid",  text: "PsiQuantum · IBM · 4 more", detail: "Allied · QUBITS — tenants publicly committed: PsiQuantum (anchor), IBM (Quantum System Two + National Quantum Algorithm Center), Diraq, Infleqtion, Quantum Machines, Pasqal. [iqmp card]" } }, // [iqmp]
    { label: "CO-LOCATED SITE",
      hefei:  { state: "solid",  text: "fab · robots · lab · compute, one city", detail: "Hefei · SITE — fab, robots, national lab and compute assembled in one city; the robotic-chemist platform is co-located with USTC’s fabrication and computing centers. [chemagents card]" }, // [chemagents + Ch2 §04]
      allied: { state: "solid",  text: "groundbroken 2025-09-30", detail: "Allied · SITE — the Illinois Quantum and Microelectronics Park broke ground 30 Sep 2025 on the former U.S. Steel South Works site; ~$700M state funding, $1.2B federal LOIs (May 2026). [iqmp card; ledger C13]" } } // [iqmp, C13]
  ];
  var TAKEAWAY = "Hefei has the robots · the allies have the referee · nobody has the loop";   // the chiasmus [C06, C16, chemagents, iqmp]
  var ASK = "the ask: fund the empty allied cells first — single-digit $B/yr, quantum-specific";  // [§04; ledger C16]

  function rowY(i) { return TOP + i * (CELL_H + GAP); }   // i=0 is the crown row
  function stateStroke(s, bloc) { return s === "empty" ? COL.gap : (bloc === "hefei" ? COL.hefei : COL.allied); }

  function compute() {
    var H = rowY(ROWS.length - 1) + CELL_H + 96;
    return { W: W, H: H,
      ariaLabel: "Two co-location stacks drawn cell-by-cell from this dossier's citations: the Hefei stack and the allied Illinois park, six rows each, building upward — site, qubits, cryogenics, robots, verification, and on top the closed loop on qubits. Solid cells are cited, hatched cells are reported-grade, empty coral-dashed cells are absent from the public record. Hefei's robots row is solid and its verification row hatched; the allied verification row is solid and its robots row empty; the loop row — the crown — is empty on both towers." };
  }

  function fail(container, msg) {
    if (root && root.console) root.console.error("[qc-gapmap] " + msg);
    if (container && container.appendChild) {
      var doc = (root && root.document) || container.ownerDocument;
      var p = doc.createElement("p"); p.className = "lf-fallback"; p.textContent = "Figure unavailable: " + msg; container.appendChild(p);
    }
    return null;
  }

  // ---- shared cell emitters (live + poster read one geometry) ----
  function cellRect(x, y, cell, bloc) {
    var st = stateStroke(cell.state, bloc);
    var a = { x: x, y: y, width: CELL_W, height: CELL_H, rx: 7, "stroke-width": "2", stroke: st };
    if (cell.state === "solid")   { a.fill = st; a["fill-opacity"] = "0.10"; }
    if (cell.state === "hatched") { a.fill = st; a["fill-opacity"] = "0.04"; a["stroke-dasharray"] = "7 5"; }
    if (cell.state === "empty")   { a.fill = "none"; a["stroke-dasharray"] = "4 4"; }
    return a;
  }
  function cellTextColor(cell, bloc) { return cell.state === "empty" ? COL.gap : (bloc === "hefei" ? COL.hefei : COL.allied); }
  function tagFor(state) { return state === "solid" ? "cited" : state === "hatched" ? "reported" : "absent from the record"; }

  // ===== LIVE =====
  function renderQCGapmap(container, spec) {
    if (!container) return fail(null, "no container");
    var doc = (root && root.document) || container.ownerDocument;
    if (spec == null && container.getAttribute) spec = container.getAttribute("data-figure");
    if (typeof spec === "string") { try { spec = JSON.parse(spec); } catch (e) { return fail(container, "data-figure is not valid JSON"); } }

    dedupPoster(container);
    var g = compute();
    var svg = el("svg", { viewBox: "0 0 " + g.W + " " + g.H, width: "100%", "class": "lf-svg", role: "img", "aria-label": g.ariaLabel });

    function txt(x, y, anchor, cls, fill, str) { var t = el("text", { x: x, y: y, "text-anchor": anchor, fill: fill, "class": cls }); t.textContent = str; return t; }

    // headers + legend
    svg.appendChild(txt(HX + CELL_W / 2, 46, "middle", "lf-callout lf-scale-with-art", COL.hefei, "THE HEFEI STACK"));
    svg.appendChild(txt(HX + CELL_W / 2, 64, "middle", "lf-tick lf-scale-with-art", COL.axis, "as cited in this dossier"));
    svg.appendChild(txt(AX + CELL_W / 2, 46, "middle", "lf-callout lf-scale-with-art", COL.allied, "THE ALLIED PARK (IQMP)"));
    svg.appendChild(txt(AX + CELL_W / 2, 64, "middle", "lf-tick lf-scale-with-art", COL.axis, "as publicly documented"));
    svg.appendChild(txt(W / 2, 92, "middle", "lf-tick lf-scale-with-art", COL.axis, "solid = cited · hatched = reported-grade · coral dashes = absent from the public record"));

    ROWS.forEach(function (row, i) {
      var y = rowY(i);
      svg.appendChild(txt(MIDX, y + CELL_H / 2 - 4, "middle", "lf-tick lf-scale-with-art", COL.axis, row.label));
      [["hefei", HX], ["allied", AX]].forEach(function (pair) {
        var bloc = pair[0], x = pair[1], cell = row[bloc];
        var rect = el("rect", cellRect(x, y, cell, bloc)); rect.setAttribute("data-detail", cell.detail);
        svg.appendChild(rect);
        var tcol = cellTextColor(cell, bloc);
        var t1 = txt(x + CELL_W / 2, y + 24, "middle", "lf-axis lf-scale-with-art", tcol, cell.text); t1.setAttribute("data-detail", cell.detail); svg.appendChild(t1);
        var t2 = txt(x + CELL_W / 2, y + 42, "middle", "lf-tick lf-scale-with-art", COL.axis, tagFor(cell.state)); t2.setAttribute("data-detail", cell.detail); svg.appendChild(t2);
      });
      if (i === 0) {
        svg.appendChild(txt(MIDX, y - 14, "middle", "lf-tick lf-scale-with-art", COL.gap, "the missing crown — on both towers"));
      }
    });

    var by = rowY(ROWS.length - 1) + CELL_H;
    svg.appendChild(txt(W / 2, by + 40, "middle", "lf-axis lf-scale-with-art", COL.ink, TAKEAWAY));
    svg.appendChild(txt(W / 2, by + 62, "middle", "lf-tick lf-scale-with-art", COL.axis, ASK));

    container.appendChild(svg);
    var controls = doc.createElement("div"); controls.className = "lf-controls";
    var readout = doc.createElement("span"); readout.className = "lf-readout"; readout.setAttribute("aria-live", "polite");
    var HINT = "Hover a cell for its statement and source. Solid cells are cited; hatched, reported; empty, absent from the public record.";
    var resetBtn = doc.createElement("button"); resetBtn.type = "button"; resetBtn.className = "lf-btn"; resetBtn.textContent = "Reset";
    resetBtn.addEventListener("click", function () { readout.textContent = HINT; });
    controls.appendChild(resetBtn); controls.appendChild(readout); container.appendChild(controls);
    readout.textContent = HINT;

    Array.prototype.forEach.call(svg.querySelectorAll("[data-detail]"), function (node) {
      var detail = node.getAttribute("data-detail");
      node.setAttribute("tabindex", "0"); node.setAttribute("role", "img"); node.setAttribute("aria-label", detail); node.style.cursor = "pointer";
      var show = function () { readout.textContent = detail; }, clear = function () { readout.textContent = HINT; };
      node.addEventListener("mouseenter", show); node.addEventListener("mouseleave", clear);
      node.addEventListener("focus", show); node.addEventListener("blur", clear); node.addEventListener("click", show);
    });

    var handle = { runtimeVersion: DossierFigures.FIGURES_RUNTIME_VERSION, getState: function () { return { view: "gapmap" }; }, reset: function () { readout.textContent = HINT; } };
    container.__lfHandle = handle;
    return handle;
  }

  // ===== POSTER (pure string; identical geometry) =====
  function renderQCGapmapPosterSVG() {
    var g = compute();
    var s = '<svg viewBox="0 0 ' + g.W + ' ' + g.H + '" width="100%" class="lf-svg" role="img" aria-label="' + escAttr(g.ariaLabel) + '">';
    function tS(x, y, anchor, cls, fill, str) { return '<text class="' + cls + '" x="' + r2(x) + '" y="' + r2(y) + '" text-anchor="' + anchor + '" fill="' + fill + '">' + escTxt(str) + '</text>'; }
    s += tS(HX + CELL_W / 2, 46, "middle", "lf-callout lf-scale-with-art", COL.hefei, "THE HEFEI STACK");
    s += tS(HX + CELL_W / 2, 64, "middle", "lf-tick lf-scale-with-art", COL.axis, "as cited in this dossier");
    s += tS(AX + CELL_W / 2, 46, "middle", "lf-callout lf-scale-with-art", COL.allied, "THE ALLIED PARK (IQMP)");
    s += tS(AX + CELL_W / 2, 64, "middle", "lf-tick lf-scale-with-art", COL.axis, "as publicly documented");
    s += tS(W / 2, 92, "middle", "lf-tick lf-scale-with-art", COL.axis, "solid = cited · hatched = reported-grade · coral dashes = absent from the public record");
    ROWS.forEach(function (row, i) {
      var y = rowY(i);
      s += tS(MIDX, y + CELL_H / 2 - 4, "middle", "lf-tick lf-scale-with-art", COL.axis, row.label);
      [["hefei", HX], ["allied", AX]].forEach(function (pair) {
        var bloc = pair[0], x = pair[1], cell = row[bloc], a = cellRect(x, y, cell, bloc), attrs = "";
        for (var k in a) attrs += " " + k + '="' + a[k] + '"';
        s += "<rect" + attrs + "></rect>";
        s += tS(x + CELL_W / 2, y + 24, "middle", "lf-axis lf-scale-with-art", cellTextColor(cell, bloc), cell.text);
        s += tS(x + CELL_W / 2, y + 42, "middle", "lf-tick lf-scale-with-art", COL.axis, tagFor(cell.state));
      });
      if (i === 0) s += tS(MIDX, y - 14, "middle", "lf-tick lf-scale-with-art", COL.gap, "the missing crown — on both towers");
    });
    var by = rowY(ROWS.length - 1) + CELL_H;
    s += tS(W / 2, by + 40, "middle", "lf-axis lf-scale-with-art", COL.ink, TAKEAWAY);
    s += tS(W / 2, by + 62, "middle", "lf-tick lf-scale-with-art", COL.axis, ASK);
    s += "</svg>";
    return s;
  }

  DossierFigures.renderQCGapmap = renderQCGapmap;
  DossierFigures.renderQCGapmapPosterSVG = renderQCGapmapPosterSVG;
  DossierFigures.registerPoster("qc-gapmap", renderQCGapmapPosterSVG);
  DossierFigures.registerRenderer("qc-gapmap", renderQCGapmap);
})(typeof window !== "undefined" ? window : null);
