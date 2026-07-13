/*
 * qc-ch5-posters.js — lightbox registration for Chapter 5's five poster
 * figures (qc-wall, qc-spectrum, qc-trap, qc-board, qc-gap).
 *
 * WHAT THIS IS
 *   Chapter 5's figures are hand-baked poster SVGs authored directly in
 *   editions/index.source.html — every coordinate computed from committed
 *   records at authoring time, no live data path. figures.js (0.8.0+) only
 *   wires the lightbox expand trigger for types with a registered renderer,
 *   so without this module the posters stand but cannot be expanded. This
 *   module registers each type with a renderer that clones the figure's own
 *   published poster into the lightbox: live == sealed, byte-for-byte — the
 *   same contract qc-campaign.js states for its static render.
 *
 * WHAT THIS IS NOT
 *   No poster emitters are registered: the posters are authored in the
 *   source and sealed by the normal pipeline; Node-side rendering never
 *   calls into this module (browser-only guard below), so render-edition
 *   and the sealer are unaffected.
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

  function findPosterSVG(type) {
    var figs = root.document.querySelectorAll("figure[data-figure]");
    for (var i = 0; i < figs.length; i++) {
      var spec;
      try { spec = JSON.parse(figs[i].getAttribute("data-figure")); }
      catch (e) { continue; }
      if (spec && spec.type === type) {
        var svg = figs[i].querySelector("svg.lf-svg");
        if (svg) return svg.outerHTML;
      }
    }
    return null;
  }

  TYPES.forEach(function (type) {
    DF.registerRenderer(type, function (container, spec) {
      var svg = findPosterSVG(type);
      if (svg) container.insertAdjacentHTML("beforeend", svg); // live == sealed
    });
  });
})(typeof window !== "undefined" ? window : null);
