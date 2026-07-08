/*
 * qc-degenloop.js — "the discovery loop, run on itself" render module for Open
 * Dossier living figures (Dossier QC-Accelerate-002, Chapter 4, Fig 1).
 *
 * WHAT THIS IS
 *   The chapter's method in one glance: the five-station discovery loop —
 *   PROPOSE, VERIFY, SIMULATE, SCORE, LEARN — drawn as a ring played clockwise,
 *   each station with a one-line concrete description of what it does in this
 *   chapter. Two annotations mark where the campaign's two decisive events
 *   landed on the ring: the referee's kill (at VERIFY, coral) and the win (at
 *   SCORE, teal). The point the figure makes visually: this is the loop's
 *   DEGENERATE case — the MAKE/fabrication station is free, because "making"
 *   the candidate means simulating it.
 *
 * STATIC FIGURE (no animation): geometry computed ONCE into a draw-list,
 *   consumed by BOTH the live emitter and the poster string emitter — the
 *   JS-off floor cannot drift from the JS-on ceiling. No data beyond the
 *   station labels; nothing to source-comment (this is a schematic, not a plot).
 *
 * SUSTAINABILITY LAWS: zero deps, pure vanilla, vendored first-party;
 *   reader-side only; NEVER executed by CI.
 */
(function (root) {
  "use strict";

  var NS = root && root.DossierFigures;
  if (!NS) { if (root && root.console) root.console.error("[qc-degenloop] figures.js runtime not found — load figures.js first"); return; }
  var DossierFigures = NS;
  var r2 = DossierFigures.r2, escAttr = DossierFigures.escAttr,
      escTxt = DossierFigures.escTxt, dedupPoster = DossierFigures.dedupPoster;

  var W = 960, H = 520;
  var COL = { ink: "#3a474b", axis: "#5a6b70", grid: "#d7dee0", coral: "#c2562f", teal: "#0c8f86" };
  var R = 36;                 // station node radius
  var AH = 13, AW = 5;        // arrowhead length / half-width

  // Five stations, in clockwise ring order. dx/dy = where the 2-line description sits.
  var NODES = [
    { id: "PROPOSE",  x: 480, y: 170, col: COL.ink,   d: ["an AI drafts a candidate code:", "a small grid of 0s and 1s"],        dx: 480, dy: 228 },
    { id: "VERIFY",   x: 785, y: 258, col: COL.coral, d: ["cheap algebra grades the draft", "(n,k,d) before any simulation"],    dx: 785, dy: 302 },
    { id: "SIMULATE", x: 655, y: 428, col: COL.ink,   d: ["the full checking circuit, poisoned", "with chip-calibrated errors"], dx: 655, dy: 470 },
    { id: "SCORE",    x: 305, y: 428, col: COL.teal,  d: ["count decoder failures; compare", "to budget-matched repetition"],     dx: 305, dy: 470 },
    { id: "LEARN",    x: 175, y: 258, col: COL.ink,   d: ["autopsy every loser; the lesson", "feeds the next PROPOSE"],           dx: 175, dy: 302 }
  ];

  function compute() {
    var d = [];
    function ln(x1, y1, x2, y2, col, w, dash) { d.push({ k: "line", x1: x1, y1: y1, x2: x2, y2: y2, col: col, w: w || 1, dash: dash || "" }); }
    function tx(x, y, anchor, cls, fill, str) { d.push({ k: "text", x: x, y: y, a: anchor, cls: cls, fill: fill, s: str }); }
    function ci(x, y, r, fill, stroke, sw) { d.push({ k: "circle", x: x, y: y, r: r, fill: fill, stroke: stroke, sw: sw || 0 }); }
    function poly(pts, fill) { d.push({ k: "poly", pts: pts, fill: fill }); }

    // title + subtitle (matches the house header rhythm of the other two figures)
    tx(W / 2, 40, "middle", "lf-callout lf-scale-with-art", COL.ink, "THE DISCOVERY LOOP, RUN ON ITSELF");
    tx(W / 2, 64, "middle", "lf-tick lf-scale-with-art", COL.axis, "five stations, clockwise — the degenerate case, because here MAKE is free: making a candidate means simulating it");

    // clockwise arrows between consecutive stations (trimmed to the node rim, arrowhead at the target)
    for (var i = 0; i < NODES.length; i++) {
      var a = NODES[i], b = NODES[(i + 1) % NODES.length];
      var vx = b.x - a.x, vy = b.y - a.y, L = Math.sqrt(vx * vx + vy * vy);
      var ux = vx / L, uy = vy / L, px = -uy, py = ux;      // unit + left perpendicular
      var sx = a.x + R * ux, sy = a.y + R * uy;             // start at source rim
      var ex = b.x - R * ux, ey = b.y - R * uy;             // end at target rim
      ln(sx, sy, ex, ey, COL.grid, 1.6);
      var tipx = ex, tipy = ey;
      var b1x = ex - AH * ux + AW * px, b1y = ey - AH * uy + AW * py;
      var b2x = ex - AH * ux - AW * px, b2y = ey - AH * uy - AW * py;
      poly(r2(tipx) + "," + r2(tipy) + " " + r2(b1x) + "," + r2(b1y) + " " + r2(b2x) + "," + r2(b2y), COL.axis);
    }

    // center note: what makes this loop cheap
    tx(W / 2, 298, "middle", "lf-tick lf-scale-with-art", COL.axis, "no fabrication step to run —");
    tx(W / 2, 314, "middle", "lf-tick lf-scale-with-art", COL.axis, "the simulator is the lab");

    // station nodes: ringed circle + title inside, 2-line description outside
    NODES.forEach(function (nd) {
      ci(nd.x, nd.y, R, "#ffffff", nd.col, 2.2);
      tx(nd.x, nd.y + 4, "middle", "lf-axis lf-scale-with-art", nd.col, nd.id);
      tx(nd.dx, nd.dy, "middle", "lf-tick lf-scale-with-art", COL.ink, nd.d[0]);
      tx(nd.dx, nd.dy + 16, "middle", "lf-tick lf-scale-with-art", COL.ink, nd.d[1]);
    });

    // the two campaign events, marked on the ring
    tx(785, 214, "middle", "lf-axis lf-scale-with-art", COL.coral, "THE KILL HAPPENED HERE");
    tx(305, 506, "middle", "lf-axis lf-scale-with-art", COL.teal, "THE WIN WAS SCORED HERE");

    return { W: W, H: H, list: d,
             ariaLabel: "The five-station discovery loop drawn as a ring played clockwise: PROPOSE (an AI drafts a candidate code), VERIFY (cheap algebra grades it before any simulation), SIMULATE (the full checking circuit poisoned with chip-calibrated errors), SCORE (count decoder failures against budget-matched repetition), and LEARN (autopsy every loser to feed the next proposal). The referee's kill is marked at VERIFY and the campaign's win at SCORE; the loop is degenerate because the make step is free — making a candidate means simulating it." };
  }

  function itemStr(it) {
    if (it.k === "line") return '<line x1="' + r2(it.x1) + '" y1="' + r2(it.y1) + '" x2="' + r2(it.x2) + '" y2="' + r2(it.y2) + '" stroke="' + it.col + '" stroke-width="' + it.w + '"' + (it.dash ? ' stroke-dasharray="' + it.dash + '"' : "") + '></line>';
    if (it.k === "circle") return '<circle cx="' + r2(it.x) + '" cy="' + r2(it.y) + '" r="' + it.r + '" fill="' + it.fill + '"' + (it.stroke && it.stroke !== "none" ? ' stroke="' + it.stroke + '" stroke-width="' + it.sw + '"' : "") + '></circle>';
    if (it.k === "poly") return '<polygon points="' + it.pts + '" fill="' + it.fill + '"></polygon>';
    if (it.k === "text") return '<text class="' + it.cls + '" x="' + r2(it.x) + '" y="' + r2(it.y) + '" text-anchor="' + it.a + '" fill="' + it.fill + '">' + escTxt(it.s) + '</text>';
    return "";
  }
  function posterSVG(spec) {
    var g = compute();
    var s = '<svg viewBox="0 0 ' + g.W + " " + g.H + '" width="100%" class="lf-svg" role="img" aria-label="' + escAttr(g.ariaLabel) + '">';
    for (var i = 0; i < g.list.length; i++) s += itemStr(g.list[i]);
    s += "</svg>";
    return s;
  }
  function renderQCDegenLoop(container, spec) {
    if (!container) return;
    dedupPoster(container);
    container.insertAdjacentHTML("beforeend", posterSVG(spec));  // static: live == sealed
  }

  DossierFigures.renderQCDegenLoop = renderQCDegenLoop;
  DossierFigures.renderQCDegenLoopPosterSVG = posterSVG;
  DossierFigures.registerPoster("qc-degenloop", posterSVG);
  DossierFigures.registerRenderer("qc-degenloop", renderQCDegenLoop);
})(typeof window !== "undefined" ? window : null);
