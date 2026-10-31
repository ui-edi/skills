/*!
 * Drehbuch engine v1.0 (MIT) – github.com/ui-edi/skills
 * Turns scroll into a timeline. Reads data-db-* attributes from your own markup,
 * never builds DOM. Inline this file into the page (one self-contained HTML file).
 *
 * Attributes
 *   data-db="act"                 an act: gets --p (0..1) while it scrolls through the viewport
 *   data-db-cue="0.2-0.6"         child of an act: class "on" + --c (0..1) inside that range of --p
 *   data-db-speed="-0.2"          parallax: moves at a different rate than the scroll (px per px)
 *   data-db-pan                   child track of an act: slides sideways as --p goes 0..1
 *   data-db-scrub                 <video> inside an act: playhead follows --p (muted, no audio)
 *   data-db-in                    fades/slides in once when it enters the viewport
 *   data-db-count="1234"          counts up to a REAL number when it enters the viewport
 *   data-db-words                 splits text into words (span.w with --i) for kinetic type
 *
 * JS hook for the bespoke signature move:
 *   Drehbuch.on(element, p => { ... })   called every frame the act's --p changes
 */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement, win = window;
  var reduced = win.matchMedia && win.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduced) root.classList.add("db-reduced");
  root.classList.add("db-js");

  var acts = [], parallax = [], hooks = [], vh = 0, ticking = false;
  var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };

  function splitWords(el) {
    if (el.dataset.dbSplit) return;
    var words = el.textContent.trim().split(/\s+/);
    el.setAttribute("aria-label", el.textContent.trim());
    el.textContent = "";
    words.forEach(function (w, i) {
      var s = doc.createElement("span");
      s.className = "w"; s.setAttribute("aria-hidden", "true");
      s.style.setProperty("--i", i);
      s.textContent = w;
      el.appendChild(s);
      if (i < words.length - 1) el.appendChild(doc.createTextNode(" "));
    });
    el.dataset.dbSplit = "1";
  }

  function parseRange(s) {
    var m = String(s || "0-1").split("-").map(parseFloat);
    return [isNaN(m[0]) ? 0 : m[0], isNaN(m[1]) ? 1 : m[1]];
  }

  function measure() {
    vh = win.innerHeight;
    acts.forEach(function (a) {
      var r = a.el.getBoundingClientRect();
      a.top = r.top + win.scrollY;
      a.h = a.el.offsetHeight;
      if (a.pan) a.panMax = Math.max(0, a.pan.scrollWidth - a.pan.parentElement.clientWidth);
    });
  }

  function update() {
    ticking = false;
    var y = win.scrollY;
    acts.forEach(function (a) {
      // p = 0 when the act's top reaches the top of the viewport,
      // p = 1 when its bottom reaches the bottom of the viewport.
      var span = Math.max(1, a.h - vh);
      var p = clamp((y - a.top) / span, 0, 1);
      if (reduced) p = a.h > vh * 1.2 ? p : 1;
      if (Math.abs(p - a.p) < 0.0005 && a.done) return;
      a.p = p; a.done = true;
      a.el.style.setProperty("--p", p.toFixed(4));
      a.cues.forEach(function (c) {
        var on = p >= c.r[0] && p <= c.r[1] || (c.hold && p > c.r[1]);
        var local = clamp((p - c.r[0]) / Math.max(0.0001, c.r[1] - c.r[0]), 0, 1);
        c.el.style.setProperty("--c", local.toFixed(4));
        if (on !== c.on) { c.on = on; c.el.classList.toggle("on", on); }
      });
      if (a.pan && !reduced) a.pan.style.transform = "translate3d(" + (-p * a.panMax).toFixed(1) + "px,0,0)";
      if (a.video && a.video.duration) a.target = p * (a.video.duration - 0.05);
      hooks.forEach(function (h) { if (h.el === a.el) h.fn(p); });
    });
    if (!reduced) parallax.forEach(function (o) {
      var r = o.el.parentElement.getBoundingClientRect();
      var offset = (r.top + r.height / 2 - vh / 2) * o.speed;
      o.el.style.transform = "translate3d(0," + offset.toFixed(1) + "px,0)";
    });
  }

  // Video playhead is eased toward its target so scrubbing stays smooth.
  function scrubLoop() {
    acts.forEach(function (a) {
      if (!a.video || a.target == null) return;
      var v = a.video, d = a.target - v.currentTime;
      if (Math.abs(d) > 0.01 && !v.seeking) v.currentTime = v.currentTime + d * 0.25;
    });
    win.requestAnimationFrame(scrubLoop);
  }

  function request() { if (!ticking) { ticking = true; win.requestAnimationFrame(update); } }

  function init() {
    doc.querySelectorAll("[data-db-words]").forEach(splitWords);
    doc.querySelectorAll('[data-db="act"]').forEach(function (el) {
      var a = { el: el, p: -1, done: false, cues: [] };
      el.querySelectorAll("[data-db-cue]").forEach(function (c) {
        a.cues.push({ el: c, r: parseRange(c.dataset.dbCue), on: false, hold: c.hasAttribute("data-db-hold") });
      });
      a.pan = el.querySelector("[data-db-pan]");
      a.video = el.querySelector("video[data-db-scrub]");
      if (a.video) { a.video.muted = true; a.video.pause(); a.video.removeAttribute("autoplay"); }
      acts.push(a);
    });
    doc.querySelectorAll("[data-db-speed]").forEach(function (el) {
      parallax.push({ el: el, speed: parseFloat(el.dataset.dbSpeed) || 0 });
    });

    var io = "IntersectionObserver" in win ? new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target;
        el.classList.add("on");
        if (el.hasAttribute("data-db-count")) countUp(el);
        io.unobserve(el);
      });
    }, { rootMargin: "0px 0px -12% 0px" }) : null;
    doc.querySelectorAll("[data-db-in],[data-db-count]").forEach(function (el) {
      if (io && !reduced) io.observe(el);
      else { el.classList.add("on"); if (el.hasAttribute("data-db-count")) el.textContent = fmt(el, +el.dataset.dbCount); }
    });

    measure(); update();
    win.addEventListener("scroll", request, { passive: true });
    win.addEventListener("resize", function () { measure(); request(); });
    win.addEventListener("load", function () { measure(); request(); });
    if (acts.some(function (a) { return a.video; })) scrubLoop();
  }

  function fmt(el, n) {
    var loc = el.dataset.dbLocale || doc.documentElement.lang || "en";
    return Math.round(n).toLocaleString(loc);
  }
  function countUp(el) {
    var to = +el.dataset.dbCount, t0 = performance.now(), dur = 1400;
    (function step(t) {
      var k = clamp((t - t0) / dur, 0, 1), e = 1 - Math.pow(1 - k, 3);
      el.textContent = fmt(el, to * e);
      if (k < 1) win.requestAnimationFrame(step);
    })(t0);
  }

  win.Drehbuch = {
    on: function (el, fn) { hooks.push({ el: el, fn: fn }); request(); },
    refresh: function () { measure(); request(); },
    reduced: reduced
  };
  if (doc.readyState === "loading") doc.addEventListener("DOMContentLoaded", init); else init();
})();
