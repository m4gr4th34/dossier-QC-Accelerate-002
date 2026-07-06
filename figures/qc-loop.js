/*
 * qc-loop.js — "the three rungs" render module for Open Dossier living figures
 * (Dossier QC-Accelerate-002, Chapter 2).
 *
 * WHAT THIS IS
 *   Three small-multiple loop diagrams side by side — RUNG 1 · AUTOMATION,
 *   RUNG 2 · PARTIAL LOOP, RUNG 3 · CLOSED LOOP — each a four-node cycle
 *   DECIDE -> MAKE -> MEASURE -> LEARN. Node fill marks WHO holds the station:
 *   human = ink tone, machine = teal tone. An arrow between two machine nodes runs
 *   at machine tempo (SOLID); any arrow entering or leaving a human node WAITS
 *   (DASHED, with a "waits for human" tick). The human is INSIDE the loop on rungs
 *   1-2; on rung 3 the human steps OUTSIDE, reading what the loop reports
 *   ("interprets"). All three are always visible; the buttons FOCUS one rung
 *   (others dim, never hide). A gentle pulse travels the focused loop and pauses
 *   visibly at every dashed arrow (rungs 1-2), cycling unbroken on rung 3.
 *   This is a TAXONOMY of the chapter's own framework — no measured data. [schematic]
 *
 * THE COMPOSITION LAW
 *   Every GENERAL primitive comes from the runtime (figures.js), never re-rolled:
 *     - SVG nodes -> el ; string-emit -> r2/escAttr/escTxt ; dedup -> dedupPoster ;
 *     - reduced-motion -> DossierFigures.prefersReducedMotion().
 *   The engine ships no diagram primitives, so the node/edge/glyph layer lives HERE.
 *   Geometry is computed ONCE in computeLoops(spec) and consumed by BOTH the live
 *   el() emitter AND the pure poster string emitter, so the JS-off floor can never
 *   drift from the live ceiling. Text is sized by ROLE via tier classes
 *   (lf-tick / lf-axis / lf-callout — the runtime owns the px), NEVER a raw
 *   font-size; keep both emit paths in lockstep.
 *
 *   SEAM SAFETY: the poster and geometry depend on spec + focus only, NEVER on
 *   animation time — the pulse is live-only, so pausing/gating leaves sealed bytes
 *   untouched (render_figures reports 0 rewritten).
 *
 * SUSTAINABILITY LAWS: zero deps, pure vanilla, vendored first-party; reader-side
 *   only; NEVER executed by CI (the stdlib-only verify floor stays untouched).
 */
(function (root) {
  "use strict";

  var NS = root && root.DossierFigures;
  if (!NS) {
    if (root && root.console) {
      root.console.error("[qc-loop] figures.js runtime not found — load figures.js before qc-loop.js");
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

  function num(v, d) { return (typeof v === "number" && isFinite(v)) ? v : d; }
  function clamp(x, lo, hi) { return x < lo ? lo : x > hi ? hi : x; }

  // ----- layout + palette -----
  var W = 960, H = 380;
  var CX = [160, 480, 800], CY = 188, R = 74, RN = 20;   // panel centers, loop radius, node radius
  var DIM = "0.25";                                        // the UNFOCUSED rung dims, never hides
  var ORDER = ["DECIDE", "MAKE", "MEASURE", "LEARN"];
  var COL = {
    human: "#5a6b70", machine: "#2f6f8f", axis: "#5a6b70",
    edge: "#9aa3a6", pulse: "#c2562f", faint: "#9fb0b5"
  };
  // Per-rung: which stations a MACHINE holds (the rest are human). The load-bearing taxonomy.
  var RUNGS = [
    { rung: 1, header: "RUNG 1 · AUTOMATION",   machine: { MAKE: 1 },
      say: "Rung 1 · automation — a machine makes; humans decide, measure, and learn. The loop waits for a human at every hand-off." },
    { rung: 2, header: "RUNG 2 · PARTIAL LOOP", machine: { MAKE: 1, MEASURE: 1 },
      say: "Rung 2 · partial loop — machines make and measure; humans still decide and learn. Where quantum computing lives today." },
    { rung: 3, header: "RUNG 3 · CLOSED LOOP",  machine: { DECIDE: 1, MAKE: 1, MEASURE: 1, LEARN: 1 },
      say: "Rung 3 · closed loop — machines hold all four stations; the human steps outside to interpret. The chapter's bet." }
  ];
  var DEFAULT_RUNG = 2;

  // ===== SHARED COMPUTE ===================================================
  // computeLoops(spec) -> geometry for ALL three panels. Consumed by the live
  // el() emitter AND the pure poster string emitter -> floor == ceiling.
  function computeLoops(spec) {
    spec = spec || {};
    var panels = RUNGS.map(function (p, i) {
      var cx = CX[i];
      var pos = {
        DECIDE:  { x: cx,     y: CY - R, lx: cx,            ly: CY - R - RN - 9, anchor: "middle" },
        MAKE:    { x: cx + R, y: CY,     lx: cx + R + RN + 6, ly: CY + 4,        anchor: "start"  },
        MEASURE: { x: cx,     y: CY + R, lx: cx,            ly: CY + R + RN + 17, anchor: "middle" },
        LEARN:   { x: cx - R, y: CY,     lx: cx - R - RN - 6, ly: CY + 4,        anchor: "end"    }
      };
      var isMachine = function (k) { return !!p.machine[k]; };
      var nodes = ORDER.map(function (k) {
        return { key: k, x: pos[k].x, y: pos[k].y, owner: isMachine(k) ? "machine" : "human",
          lx: pos[k].lx, ly: pos[k].ly, anchor: pos[k].anchor };
      });
      // cyclic edges DECIDE->MAKE->MEASURE->LEARN->DECIDE, trimmed to node rims
      var edges = [];
      for (var e = 0; e < 4; e++) {
        var A = pos[ORDER[e]], B = pos[ORDER[(e + 1) % 4]];
        var dashed = !isMachine(ORDER[e]) || !isMachine(ORDER[(e + 1) % 4]);
        var dx = B.x - A.x, dy = B.y - A.y, L = Math.sqrt(dx * dx + dy * dy) || 1;
        var ux = dx / L, uy = dy / L;
        edges.push({
          x1: r2(A.x + ux * (RN + 3)), y1: r2(A.y + uy * (RN + 3)),
          x2: r2(B.x - ux * (RN + 9)), y2: r2(B.y - uy * (RN + 9)),
          dashed: dashed, mx: r2((A.x + B.x) / 2), my: r2((A.y + B.y) / 2),
          nx: r2(-uy), ny: r2(ux)   // outward perpendicular (for the waits-tick offset)
        });
      }
      // "waits for human" tick: once per diagram, at the first dashed edge (none on rung 3).
      var wait = null;
      for (var w = 0; w < edges.length; w++) {
        if (edges[w].dashed) { wait = { x: r2(edges[w].mx + edges[w].nx * 15), y: r2(edges[w].my + edges[w].ny * 15) }; break; }
      }
      // human glyph: inside the loop (rungs 1-2); OUTSIDE, reading, on rung 3.
      var allMachine = ORDER.every(isMachine);
      var glyph = allMachine
        ? { x: cx + 42, y: CY + 42, outside: true,  label: "interprets" }
        : { x: cx,      y: CY,      outside: false, label: null };
      return { rung: p.rung, header: p.header, say: p.say, cx: cx, cy: CY, nodes: nodes, edges: edges, wait: wait, glyph: glyph };
    });
    return {
      W: W, H: H, panels: panels,
      ariaLabel: "Three small-multiple loop diagrams of the decide-make-measure-learn cycle, showing who holds each station across three rungs of automation: rung one a mostly-human loop with a single machine step, rung two a partial loop where machines make and measure while humans decide and learn, and rung three a fully closed machine loop with the human moved outside the loop to interpret its results. Solid arrows run at machine tempo; dashed arrows wait for a human."
    };
  }

  function fail(container, msg) {
    if (root && root.console) root.console.error("[qc-loop] " + msg);
    if (container && container.appendChild) {
      var doc = (root && root.document) || container.ownerDocument;
      var p = doc.createElement("p"); p.className = "lf-fallback";
      p.textContent = "Figure unavailable: " + msg; container.appendChild(p);
    }
    return null;
  }

  // Live-only pressed style for the focus buttons — stated TWICE: once for the page, once scoped to
  // #lf-lightbox so it beats the runtime's own "#lf-lightbox .lf-btn" base (ID selector) in the
  // expanded view (our #lf-lightbox .lf-controls .lf-btn[...] is more specific, so it wins, no
  // !important). Reset carries no aria-pressed, so it keeps the default unfilled look. (Mirrors
  // qc-frontier's injectToggleStyle exactly — same contract, same specificity reasoning.)
  function injectToggleStyle(doc) {
    if (!doc || !doc.getElementById || doc.getElementById("qc-loop-toggle-style")) return;
    var st = doc.createElement("style");
    st.id = "qc-loop-toggle-style";
    st.textContent =
      '.lf-controls .lf-btn{border-radius:var(--r-sm,10px);}' +
      '.lf-controls .lf-btn[aria-pressed="true"]{background:#5a6b70;color:#fff;border-color:#5a6b70;}' +
      '#lf-lightbox .lf-controls .lf-btn[aria-pressed="true"]{background:#5a6b70;color:#fff;border-color:#5a6b70;}';
    (doc.head || doc.documentElement).appendChild(st);
  }

  // ===== LIVE: renderQCLoop(container, spec) =============================
  function renderQCLoop(container, spec) {
    if (!container) return fail(null, "no container");
    var doc = (root && root.document) || container.ownerDocument;
    injectToggleStyle(doc);

    if (spec == null && container.getAttribute) spec = container.getAttribute("data-figure");
    if (typeof spec === "string") { try { spec = JSON.parse(spec); } catch (e) { return fail(container, "data-figure is not valid JSON"); } }
    spec = spec || {};

    dedupPoster(container);   // RUNTIME: drop any sealed [data-poster] floor before going live

    var g = computeLoops(spec);
    var startRung = clamp(Math.round(num(spec.defaultRung, DEFAULT_RUNG)), 1, 3);

    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, width: "100%", "class": "lf-svg",
      role: "img", "aria-label": g.ariaLabel });

    // one shared arrowhead marker
    var defs = el("defs", {});
    var mk = el("marker", { id: "loop-arr", viewBox: "0 0 10 10", refX: "8", refY: "5",
      markerWidth: "7", markerHeight: "7", orient: "auto-start-reverse" });
    mk.appendChild(el("path", { d: "M0 1L9 5L0 9z", fill: COL.edge }));
    defs.appendChild(mk); svg.appendChild(defs);

    var panelGroups = [];   // one <g> per rung (for focus dimming)
    g.panels.forEach(function (P) {
      var gp = el("g", { "class": "lf-rung", "data-rung": String(P.rung) });

      // header
      var hd = el("text", { "class": "lf-callout", x: P.cx, y: 30, "text-anchor": "middle", fill: COL.axis });
      hd.textContent = P.header; gp.appendChild(hd);

      // edges (solid = machine tempo; dashed = waits for a human)
      P.edges.forEach(function (ed) {
        var ln = el("line", { x1: ed.x1, y1: ed.y1, x2: ed.x2, y2: ed.y2, stroke: COL.edge,
          "stroke-width": "1.8", "marker-end": "url(#loop-arr)" });
        if (ed.dashed) ln.setAttribute("stroke-dasharray", "5 4");
        gp.appendChild(ln);
      });

      // "waits for human" tick (once)
      if (P.wait) {
        var wt = el("text", { "class": "lf-tick", x: P.wait.x, y: P.wait.y, "text-anchor": "middle", fill: COL.pulse });
        wt.textContent = "waits for human"; gp.appendChild(wt);
      }

      // nodes + labels
      P.nodes.forEach(function (nd) {
        gp.appendChild(el("circle", { cx: nd.x, cy: nd.y, r: String(RN),
          fill: nd.owner === "machine" ? COL.machine : COL.human, stroke: "#fff", "stroke-width": "2" }));
        var lb = el("text", { "class": "lf-axis", x: nd.lx, y: nd.ly, "text-anchor": nd.anchor, fill: COL.axis });
        lb.textContent = nd.key; gp.appendChild(lb);
      });

      // human glyph (inside on 1-2; outside + "interprets" on 3)
      personGlyph(gp, P.glyph.x, P.glyph.y);
      if (P.glyph.label) {
        var il = el("text", { "class": "lf-tick", x: P.glyph.x, y: P.glyph.y + 26, "text-anchor": "middle", fill: COL.human });
        il.textContent = P.glyph.label; gp.appendChild(il);
      }

      svg.appendChild(gp);
      panelGroups.push(gp);
    });

    // legend (once, centered under the middle panel)
    var lg = el("g", { "class": "lf-legend" });
    lg.appendChild(el("circle", { cx: 402, cy: 350, r: "7", fill: COL.human, stroke: "#fff", "stroke-width": "1.5" }));
    var lh = el("text", { "class": "lf-tick", x: 414, y: 354, "text-anchor": "start", fill: COL.axis }); lh.textContent = "human"; lg.appendChild(lh);
    lg.appendChild(el("circle", { cx: 486, cy: 350, r: "7", fill: COL.machine, stroke: "#fff", "stroke-width": "1.5" }));
    var lm = el("text", { "class": "lf-tick", x: 498, y: 354, "text-anchor": "start", fill: COL.axis }); lm.textContent = "machine"; lg.appendChild(lm);
    svg.appendChild(lg);

    // the traveling pulse (live-only; focused loop; hidden under reduced motion)
    var pulse = el("circle", { cx: "0", cy: "0", r: "6", fill: COL.pulse, stroke: "#fff", "stroke-width": "1.5", opacity: "0" });
    svg.appendChild(pulse);

    // ---- controls ----
    var controls = doc.createElement("div"); controls.className = "lf-controls";
    var btns = [1, 2, 3].map(function (rn) {
      var b = doc.createElement("button");
      b.type = "button"; b.className = "lf-btn"; b.textContent = "Rung " + rn;
      controls.appendChild(b); return b;
    });
    var resetBtn = doc.createElement("button");
    resetBtn.type = "button"; resetBtn.className = "lf-btn"; resetBtn.textContent = "Reset";
    controls.appendChild(resetBtn);
    var readout = doc.createElement("span");
    readout.className = "lf-readout"; readout.setAttribute("aria-live", "polite");
    controls.appendChild(readout);

    // ---- animation state ----
    var reduced = DossierFigures.prefersReducedMotion();
    var currentRung = startRung;
    var acc = 0, last = 0, raf = 0, visible = true, playing = !reduced;

    // segments for the focused loop: each dashed edge gets a DWELL (pulse parked, "waiting for a
    // human") before its TRAVEL; solid edges are travel only. Rebuilt on focus change.
    var WAIT_UNITS = 0.75, TRAVEL_UNITS = 1.0, SPEED = 1.6;   // units/sec
    var segs = [], segTotal = 0;
    function buildSegs() {
      segs = [];
      var P = g.panels[currentRung - 1];
      P.edges.forEach(function (ed) {
        if (ed.dashed) segs.push({ dwell: true, x: ed.x1, y: ed.y1, dur: WAIT_UNITS });
        segs.push({ dwell: false, x1: ed.x1, y1: ed.y1, x2: ed.x2, y2: ed.y2, dur: TRAVEL_UNITS });
      });
      segTotal = segs.reduce(function (s, x) { return s + x.dur; }, 0) || 1;
    }
    function placePulse() {
      if (reduced || !segs.length) { pulse.setAttribute("opacity", "0"); return; }
      var ph = ((acc % segTotal) + segTotal) % segTotal, i = 0;
      while (i < segs.length && ph >= segs[i].dur) { ph -= segs[i].dur; i++; }
      var s = segs[Math.min(i, segs.length - 1)];
      var x, y;
      if (s.dwell) { x = s.x; y = s.y; }
      else { var t = clamp(ph / s.dur, 0, 1); x = s.x1 + (s.x2 - s.x1) * t; y = s.y1 + (s.y2 - s.y1) * t; }
      pulse.setAttribute("cx", r2(x)); pulse.setAttribute("cy", r2(y)); pulse.setAttribute("opacity", "1");
    }
    function frame(now) {
      raf = 0;
      if (!playing || !visible || reduced) return;         // stop re-scheduling; resume from frozen acc
      var dt = clamp((now - last) / 1000, 0, 0.05); last = now;
      acc += dt * SPEED;
      placePulse();
      raf = root.requestAnimationFrame(frame);
    }
    function start() {
      if (raf || !playing || !visible || reduced) return;
      last = (root.performance && root.performance.now) ? root.performance.now() : 0;
      raf = root.requestAnimationFrame(frame);
    }
    function stop() { if (raf) { root.cancelAnimationFrame(raf); raf = 0; } }

    function setMode(rn) {
      currentRung = clamp(Math.round(rn), 1, 3);
      panelGroups.forEach(function (gp) {
        gp.setAttribute("opacity", parseInt(gp.getAttribute("data-rung"), 10) === currentRung ? "1" : DIM);
      });
      btns.forEach(function (b, i) { b.setAttribute("aria-pressed", (i + 1) === currentRung ? "true" : "false"); });
      readout.textContent = g.panels[currentRung - 1].say;
      acc = 0; buildSegs(); placePulse();
    }
    btns.forEach(function (b, i) { b.addEventListener("click", function () { setMode(i + 1); start(); }); });
    resetBtn.addEventListener("click", function () { setMode(DEFAULT_RUNG); start(); });

    container.appendChild(svg); container.appendChild(controls);
    setMode(startRung);

    // Visibility gate: an off-screen figure must not burn frames. root:null fires on parent-scroll
    // even inside an iframe. Resume from the frozen acc on re-entry.
    if (root.IntersectionObserver) {
      var io = new root.IntersectionObserver(function (entries) {
        for (var k = 0; k < entries.length; k++) {
          visible = entries[k].isIntersecting;
          if (visible) start(); else stop();
        }
      }, { root: null });
      io.observe(svg);
    } else { start(); }

    // Handle: getState carries the focus rung (discrete-focus figure — like qc-frontier, no slider,
    // so the lightbox opens at the published start rung; Reset restores rung 2).
    var handle = {
      runtimeVersion: DossierFigures.FIGURES_RUNTIME_VERSION,
      getState: function () { return { rung: currentRung }; },
      setMode: setMode
    };
    container.__lfHandle = handle;
    return handle;

    // person glyph (head + shoulders bust) in human ink — live path helper.
    function personGlyph(parent, gx, gy) {
      parent.appendChild(el("circle", { cx: gx, cy: gy - 7, r: "6", fill: COL.human }));
      parent.appendChild(el("path", { d: "M" + r2(gx - 10) + " " + r2(gy + 11) + " a10 10 0 0 1 20 0 z", fill: COL.human }));
    }
  }

  // ===== POSTER: renderQCLoopPosterSVG(spec) ============================
  // Pure string; ALL three panels at full opacity, no pulse, no buttons — the
  // small-multiples floor. Same computeLoops + same tier classes -> floor == ceiling.
  function renderQCLoopPosterSVG(spec) {
    if (typeof spec === "string") { try { spec = JSON.parse(spec); } catch (e) { return ""; } }
    spec = spec || {};
    var g = computeLoops(spec);
    var s = '<svg viewBox="0 0 ' + W + ' ' + H + '" width="100%" class="lf-svg" role="img" aria-label="' + escAttr(g.ariaLabel) + '">';
    s += '<defs><marker id="loop-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1L9 5L0 9z" fill="' + COL.edge + '"></path></marker></defs>';

    g.panels.forEach(function (P) {
      s += '<g class="lf-rung" data-rung="' + P.rung + '">';
      s += '<text class="lf-callout" x="' + P.cx + '" y="30" text-anchor="middle" fill="' + COL.axis + '">' + escTxt(P.header) + '</text>';
      P.edges.forEach(function (ed) {
        s += '<line x1="' + ed.x1 + '" y1="' + ed.y1 + '" x2="' + ed.x2 + '" y2="' + ed.y2 + '" stroke="' + COL.edge + '" stroke-width="1.8" marker-end="url(#loop-arr)"' + (ed.dashed ? ' stroke-dasharray="5 4"' : '') + '></line>';
      });
      if (P.wait) {
        s += '<text class="lf-tick" x="' + P.wait.x + '" y="' + P.wait.y + '" text-anchor="middle" fill="' + COL.pulse + '">' + escTxt("waits for human") + '</text>';
      }
      P.nodes.forEach(function (nd) {
        s += '<circle cx="' + nd.x + '" cy="' + nd.y + '" r="' + RN + '" fill="' + (nd.owner === "machine" ? COL.machine : COL.human) + '" stroke="#fff" stroke-width="2"></circle>';
        s += '<text class="lf-axis" x="' + nd.lx + '" y="' + nd.ly + '" text-anchor="' + nd.anchor + '" fill="' + COL.axis + '">' + escTxt(nd.key) + '</text>';
      });
      s += personGlyphS(P.glyph.x, P.glyph.y);
      if (P.glyph.label) {
        s += '<text class="lf-tick" x="' + P.glyph.x + '" y="' + r2(P.glyph.y + 26) + '" text-anchor="middle" fill="' + COL.human + '">' + escTxt(P.glyph.label) + '</text>';
      }
      s += '</g>';
    });

    s += '<g class="lf-legend">';
    s += '<circle cx="402" cy="350" r="7" fill="' + COL.human + '" stroke="#fff" stroke-width="1.5"></circle>';
    s += '<text class="lf-tick" x="414" y="354" text-anchor="start" fill="' + COL.axis + '">' + escTxt("human") + '</text>';
    s += '<circle cx="486" cy="350" r="7" fill="' + COL.machine + '" stroke="#fff" stroke-width="1.5"></circle>';
    s += '<text class="lf-tick" x="498" y="354" text-anchor="start" fill="' + COL.axis + '">' + escTxt("machine") + '</text>';
    s += '</g>';
    s += '</svg>';
    return s;
  }

  function personGlyphS(gx, gy) {
    return '<circle cx="' + gx + '" cy="' + r2(gy - 7) + '" r="6" fill="' + COL.human + '"></circle>' +
      '<path d="M' + r2(gx - 10) + ' ' + r2(gy + 11) + ' a10 10 0 0 1 20 0 z" fill="' + COL.human + '"></path>';
  }

  DossierFigures.renderQCLoop = renderQCLoop;
  DossierFigures.renderQCLoopPosterSVG = renderQCLoopPosterSVG;
  DossierFigures.registerPoster("qc-loop", renderQCLoopPosterSVG);
  DossierFigures.registerRenderer("qc-loop", renderQCLoop);
})(typeof window !== "undefined" ? window : null);
