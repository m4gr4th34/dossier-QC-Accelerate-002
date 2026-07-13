/*
 * qc-ch5-posters.js — inline mount + lightbox registration for Chapter 5's
 * five poster figures (qc-wall, qc-spectrum, qc-trap, qc-board, qc-gap).
 *
 * WHAT THIS IS
 *   Chapter 5's figures are hand-baked poster SVGs authored directly in
 *   editions/index.source.html — every coordinate computed from committed
 *   records at authoring time, no live data path. figures.js runs a standard
 *   page-init hydrate: for every figure[data-figure] it calls the registered
 *   renderer with the figure host as container, and the same renderer serves
 *   the lightbox (with a fresh overlay div as container). This module
 *   registers each type with a renderer that follows the standard
 *   mount/dedup contract (see qc-campaign.js): dedupPoster removes the baked
 *   poster, then the figure's own poster markup is (re)inserted — so the page
 *   shows exactly ONE figure per slot, live == sealed byte-for-byte.
 *
 *   Because these posters are hand-baked (no compute()/posterSVG generator),
 *   the markup is CAPTURED ONCE AT LOAD — before the hydrate's dedupPoster
 *   mutates the DOM — and that captured string is what both the inline mount
 *   and the lightbox re-insert.
 *
 * WHAT THIS IS NOT
 *   No poster emitters are registered: the posters are authored in the source
 *   and sealed by the normal pipeline; Node-side rendering never calls into
 *   this module (browser-only guard below), so render-edition and the sealer
 *   are unaffected, and the JS-off floor is the baked poster untouched.
 *
 * DATA DISCIPLINE
 *   This module contains no numbers. Every figure's numbers live in its
 *   poster SVG and single-source caption in the edition source, each traced
 *   to a committed record in its [SCORED] tag.
 */
(function (root) {
  if (!root || !root.DossierFigures || !root.document) return; // browser-only
  var DF = root.DossierFigures;
  var TYPES = ["qc-wall", "qc-spectrum", "qc-trap", "qc-board", "qc-gap"];

  // Capture each type's baked poster markup ONCE, at module load — the script
  // tag sits after the figures, so they're present, and this runs before the
  // DOMContentLoaded hydrate calls dedupPoster (which would remove the baked
  // svg and leave nothing to read from the DOM).
  var POSTERS = {};
  (function capturePosters() {
    var figs = root.document.querySelectorAll("figure[data-figure]");
    for (var i = 0; i < figs.length; i++) {
      var spec;
      try { spec = JSON.parse(figs[i].getAttribute("data-figure")); }
      catch (e) { continue; }
      if (spec && TYPES.indexOf(spec.type) !== -1 && !POSTERS[spec.type]) {
        var svg = figs[i].querySelector("svg.lf-svg");
        if (svg) POSTERS[spec.type] = svg.outerHTML;
      }
    }
  })();

  TYPES.forEach(function (type) {
    DF.registerRenderer(type, function (container, spec) {
      if (!container) return;
      DF.dedupPoster(container);                    // standard contract: drop the baked poster
      if (POSTERS[type]) container.insertAdjacentHTML("beforeend", POSTERS[type]); // live == sealed
    });
  });
})(typeof window !== "undefined" ? window : null);
