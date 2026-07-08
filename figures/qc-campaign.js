/*
 * qc-campaign.js — "the campaign arc" render module for Open Dossier living
 * figures (Dossier QC-Accelerate-002, Chapter 4, Fig 2).
 *
 * WHAT THIS IS
 *   What Chapter 4 actually did, in one glance: FOUR bets frozen in public
 *   before the search ran (hollow diamonds, prior percentages attached),
 *   resolved the same day against the frozen criteria (filled green = hit,
 *   filled coral = miss — the fill states Chapter 3's scoreboard promised).
 *   Under the P2/P3 rows, the referee's story: the mechanical verifier killed
 *   the proposer's first family before any Monte-Carlo, and the repair became
 *   the winner. On the right rail, the chapter's THREE forward bets as hollow
 *   diamonds — the next edition's fills. Along the bottom, nine dots: the
 *   error ledger E1-E9, every mistake caught, credited, and published.
 *
 * HARD DATA DISCIPLINE
 *   Every percentage, verdict, and criterion below is a LITERAL with a source
 *   comment naming its committed record (PREREG_search1.md resolution log and
 *   avenues.json cards @ commits cac735c / ef505c5). No measured data beyond
 *   the resolved verdicts; the forward bets are FORECAST cards, hollow by the
 *   house convention.
 *
 * STATIC FIGURE (no animation): geometry computed ONCE into a draw-list,
 *   consumed by BOTH the live el()-free emitter and the poster string emitter
 *   — floor == ceiling by construction.
 *
 * SUSTAINABILITY LAWS: zero deps, pure vanilla, vendored first-party;
 *   reader-side only; NEVER executed by CI.
 */
(function (root) {
  "use strict";

  var NS = root && root.DossierFigures;
  if (!NS) { if (root && root.console) root.console.error("[qc-campaign] figures.js runtime not found — load figures.js first"); return; }
  var DossierFigures = NS;
  var r2 = DossierFigures.r2, escAttr = DossierFigures.escAttr,
      escTxt = DossierFigures.escTxt, dedupPoster = DossierFigures.dedupPoster;

  var W = 960, H = 520;
  var COL = { hit: "#0c8f86", miss: "#c2562f", ink: "#3a474b", axis: "#5a6b70", grid: "#d7dee0" };
  var LX = 205, RX = 560, FX = 865;          // frozen column, resolved column, forward rail
  var ROWS = [150, 228, 306, 384];

  // ---- DATA (literals; source comments name the committed record) ----
  var BETS = [
    { name: "the Day-1 headline survives circuit level", prior: "35%",   // [PREREG P1; resolved FALSE @ 6616004]
      hit: false, outcome: "FALSE — lost by five orders of magnitude" },
    { name: "a searched code beats repetition 2x",       prior: "55%",   // [PREREG P2; resolved TRUE @ 47eba87]
      hit: true,  outcome: "TRUE — [24,4,12] wins ~4x; survived 3 re-checks" },
    { name: "an LLM-layer seed makes the podium",        prior: "40%",   // [PREREG P3; resolved TRUE @ cac735c]
      hit: true,  outcome: "TRUE — the winner itself, born from the kill" },
    { name: "match the frontier overhead at weight 4",   prior: "20%",   // [PREREG P4; resolved FALSE @ cac735c]
      hit: false, outcome: "FALSE — the stretch was a stretch" }
  ];
  var FWD = [
    { y: 185, pct: "30%", l1: "low-weight codes reach", l2: "the frontier overhead", when: "by end 2027" },   // [avenues card: Forward: low-weight...]
    { y: 268, pct: "55%", l1: "the field crosses",      l2: "the noise seam",        when: "by mid 2027" },   // [avenues card: Forward: the field crosses...]
    { y: 351, pct: "25%", l1: "an outer cat code",      l2: "on real hardware",      when: "by end 2028" }    // [avenues card: Forward: a multi-logical...]
  ];

  function compute() {
    var d = [];
    function ln(x1, y1, x2, y2, col, w, dash) { d.push({ k: "line", x1: x1, y1: y1, x2: x2, y2: y2, col: col, w: w || 1, dash: dash || "" }); }
    function tx(x, y, anchor, cls, fill, str) { d.push({ k: "text", x: x, y: y, a: anchor, cls: cls, fill: fill, s: str }); }
    function di(x, y, r, fill, stroke) { d.push({ k: "diamond", x: x, y: y, r: r, fill: fill, stroke: stroke }); }
    function ci(x, y, r, fill) { d.push({ k: "circle", x: x, y: y, r: r, fill: fill }); }

    tx(W / 2, 40, "middle", "lf-callout lf-scale-with-art", COL.ink, "FOUR PUBLIC BETS, TWO HITS, TWO MISSES");
    tx(W / 2, 64, "middle", "lf-tick lf-scale-with-art", COL.axis, "read left to right: each bet starts hollow with its pre-registered probability, and ends filled — green if it came true, coral if it did not");

    // column headers
    tx(LX, 108, "middle", "lf-axis lf-scale-with-art", COL.ink, "FROZEN 2026-07-07");
    tx(LX, 126, "middle", "lf-tick lf-scale-with-art", COL.axis, "before the search ran");
    tx(RX, 108, "middle", "lf-axis lf-scale-with-art", COL.ink, "RESOLVED — SAME DAY");
    tx(RX, 126, "middle", "lf-tick lf-scale-with-art", COL.axis, "hollow diamond -> filled: green hit, coral miss");
    tx(FX, 108, "middle", "lf-axis lf-scale-with-art", COL.ink, "NEXT BETS");
    tx(FX, 126, "middle", "lf-tick lf-scale-with-art", COL.axis, "hollow until scored");
    ln(770, 92, 770, 440, COL.grid, 1);

    BETS.forEach(function (b, i) {
      var y = ROWS[i], col = b.hit ? COL.hit : COL.miss;
      di(LX - 150, y, 9, "#ffffff", COL.ink);                                   // frozen: hollow
      tx(LX - 150, y - 16, "middle", "lf-tick lf-scale-with-art", COL.ink, b.prior);
      tx(LX - 128, y + 4, "start", "lf-tick lf-scale-with-art", COL.ink, b.name);
      ln(LX + 205, y, RX - 132, y, COL.grid, 1.4);
      d.push({ k: "arrow", x: RX - 132, y: y, col: COL.axis });
      di(RX - 108, y, 9, col, col);                                             // resolved: filled
      tx(RX - 88, y + 4, "start", "lf-tick lf-scale-with-art", col, b.outcome);
    });

    // the referee story, its own line below the rows
    tx(390, 432, "middle", "lf-tick lf-scale-with-art", COL.axis,
       "the verifier killed the first proposed family before any Monte-Carlo — the repair became the winner");

    // forward rail (hollow, the next edition's fills)
    FWD.forEach(function (f) {
      di(FX - 62, f.y, 8, "#ffffff", COL.ink);
      tx(FX - 62, f.y - 15, "middle", "lf-tick lf-scale-with-art", COL.ink, f.pct);
      tx(FX - 46, f.y - 2, "start", "lf-tick lf-scale-with-art", COL.ink, f.l1);
      tx(FX - 46, f.y + 13, "start", "lf-tick lf-scale-with-art", COL.ink, f.l2);
      tx(FX - 46, f.y + 29, "start", "lf-tick lf-scale-with-art", COL.axis, f.when);
    });

    // ledger strip: E1-E9
    var ly = 470, lx0 = 190;
    for (var i = 0; i < 9; i++) ci(lx0 + i * 26, ly, 5, COL.ink);               // [ledger E1-E9, NOTEBOOK @ cac735c]
    tx(lx0 + 9 * 26 + 8, ly + 4, "start", "lf-tick lf-scale-with-art", COL.ink,
       "E1-E9: nine of the machinery's own errors — caught, credited, published.");
    tx(lx0 - 12, ly + 4, "end", "lf-tick lf-scale-with-art", COL.axis, "the error ledger:");

    return { W: W, H: H, list: d,
             ariaLabel: "Chapter 4's campaign arc: four bets frozen before the search (35, 55, 40, 20 percent), resolved the same day — two hits, two misses — with the referee's kill-then-repair story, three hollow forward bets, and the nine-entry error ledger." };
  }

  function itemStr(it) {
    if (it.k === "line") return '<line x1="' + r2(it.x1) + '" y1="' + r2(it.y1) + '" x2="' + r2(it.x2) + '" y2="' + r2(it.y2) + '" stroke="' + it.col + '" stroke-width="' + it.w + '"' + (it.dash ? ' stroke-dasharray="' + it.dash + '"' : "") + '></line>';
    if (it.k === "circle") return '<circle cx="' + r2(it.x) + '" cy="' + r2(it.y) + '" r="' + it.r + '" fill="' + it.fill + '"></circle>';
    if (it.k === "diamond") {
      var p = r2(it.x) + "," + r2(it.y - it.r) + " " + r2(it.x + it.r) + "," + r2(it.y) + " " + r2(it.x) + "," + r2(it.y + it.r) + " " + r2(it.x - it.r) + "," + r2(it.y);
      return '<polygon points="' + p + '" fill="' + it.fill + '" stroke="' + it.stroke + '" stroke-width="1.6"></polygon>';
    }
    if (it.k === "arrow") {
      var p2 = r2(it.x) + "," + r2(it.y - 5) + " " + r2(it.x + 10) + "," + r2(it.y) + " " + r2(it.x) + "," + r2(it.y + 5);
      return '<polygon points="' + p2 + '" fill="' + it.col + '"></polygon>';
    }
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
  function renderQCCampaign(container, spec) {
    if (!container) return;
    dedupPoster(container);
    container.insertAdjacentHTML("beforeend", posterSVG(spec));  // static: live == sealed
  }

  DossierFigures.renderQCCampaign = renderQCCampaign;
  DossierFigures.renderQCCampaignPosterSVG = posterSVG;
  DossierFigures.registerPoster("qc-campaign", posterSVG);
  DossierFigures.registerRenderer("qc-campaign", renderQCCampaign);
})(typeof window !== "undefined" ? window : null);
