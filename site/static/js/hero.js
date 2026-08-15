/* Live hero plot.
   Cycles through real series from the panel. Each one is drawn left to right, held,
   then wiped for the next. The caption names the series and its source, so the
   background is readable as data and not decoration.

   Data is written into window.__HERO__ by the build. If it is missing, the hero
   stays empty instead of inventing a shape. */
(function () {
  'use strict';

  var host = document.getElementById('hero-plot');
  var capName = document.getElementById('hero-cap-name');
  var capMeta = document.getElementById('hero-cap-meta');
  if (!host || !window.__HERO__ || !window.__HERO__.length) return;

  var SERIES = window.__HERO__;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var cv = document.createElement('canvas');
  cv.setAttribute('aria-hidden', 'true');
  cv.style.width = '100%';
  cv.style.height = '100%';
  cv.style.display = 'block';
  host.appendChild(cv);
  var ctx = cv.getContext('2d');

  var W = 0, H = 0, dpr = 1, copyR = 0;

  /* Right-hand edge of the headline and deck, measured off the page instead of
     guessed, so the plot can start clear of the copy at any width. Both blocks are
     capped (16ch and 56ch), so the box edge is the text edge. */
  function measureCopy() {
    var hb = host.getBoundingClientRect();
    var r = 0;
    var sel = ['.kicker', 'h1', '.hero__deck'];
    for (var i = 0; i < sel.length; i++) {
      var el = document.querySelector('.hero__in ' + sel[i]);
      if (el) r = Math.max(r, el.getBoundingClientRect().right - hb.left);
    }
    return r;
  }

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = host.clientWidth;
    H = host.clientHeight;
    cv.width = Math.round(W * dpr);
    cv.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    copyR = measureCopy();
  }
  resize();
  var rt;
  window.addEventListener('resize', function () {
    clearTimeout(rt);
    rt = setTimeout(function () { resize(); if (reduced) still(); }, 160);
  });
  /* the web fonts land after this runs, and they move the copy edge */
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(function () { resize(); if (reduced) still(); });
  }

  /* geometry ------------------------------------------------------------- */
  function pad() {
    /* On a wide screen the trace starts to the right of the copy. Below that there is
       no room for both, so it runs the full width and the stylesheet damps it. */
    var wide = W >= 1000 && copyR > 0;
    return {
      l: wide ? Math.min(W * 0.58, copyR + 54) : Math.max(56, W * 0.055),
      r: Math.max(56, W * 0.055),
      t: Math.max(70, H * 0.22),
      b: Math.max(58, H * 0.16)
    };
  }

  function project(s) {
    var p = pad(), pts = s.points;
    var xs = pts.map(function (d) { return d[0]; });
    var ys = pts.map(function (d) { return d[1]; });
    var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs);
    var y0 = Math.min.apply(null, ys), y1 = Math.max.apply(null, ys);
    if (x1 === x0) x1 = x0 + 1;
    var span = y1 - y0;
    if (span <= 0) { y0 -= 1; y1 += 1; span = y1 - y0; }
    y0 -= span * 0.18; y1 += span * 0.18;
    var iw = W - p.l - p.r, ih = H - p.t - p.b;
    return pts.map(function (d, i) {
      return {
        x: p.l + (d[0] - x0) / (x1 - x0) * iw,
        y: p.t + ih - (d[1] - y0) / (y1 - y0) * ih,
        flag: s.flags && s.flags[i]
      };
    });
  }

  /* a monotone-ish cubic through the points, so the trace reads as an instrument
     trace and not a polyline */
  function stroke(P, upto) {
    if (P.length < 2) return null;
    ctx.beginPath();
    ctx.moveTo(P[0].x, P[0].y);
    var last = P[0];
    var n = P.length - 1;
    var end = upto * n;
    for (var i = 1; i <= n; i++) {
      var a = P[i - 1], b = P[i];
      var t = Math.min(1, Math.max(0, end - (i - 1)));
      if (t <= 0) break;
      var bx = a.x + (b.x - a.x) * t, by = a.y + (b.y - a.y) * t;
      var c1x = a.x + (b.x - a.x) * 0.42, c2x = b.x - (b.x - a.x) * 0.42;
      if (t < 1) { c1x = a.x + (bx - a.x) * 0.42; c2x = bx - (bx - a.x) * 0.42; }
      ctx.bezierCurveTo(c1x, a.y, c2x, by, bx, by);
      last = { x: bx, y: by };
    }
    ctx.stroke();
    return last;
  }

  function grid(alpha) {
    var p = pad();
    ctx.save();
    ctx.strokeStyle = 'rgba(123,144,172,' + (0.085 * alpha).toFixed(4) + ')';
    ctx.lineWidth = 1;
    for (var i = 0; i <= 4; i++) {
      var y = Math.round(p.t + (H - p.t - p.b) * (i / 4)) + 0.5;
      ctx.beginPath(); ctx.moveTo(p.l, y); ctx.lineTo(W - p.r, y); ctx.stroke();
    }
    ctx.restore();
  }

  function axisYears(s, alpha) {
    var p = pad(), pts = s.points;
    var xs = pts.map(function (d) { return d[0]; });
    var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs);
    if (x1 === x0) return;
    ctx.save();
    ctx.font = '9px "IBM Plex Mono","SF Mono",ui-monospace,Menlo,monospace';
    ctx.fillStyle = 'rgba(123,144,172,' + (0.5 * alpha).toFixed(3) + ')';
    ctx.textAlign = 'center';
    var step = Math.max(1, Math.round((x1 - x0) / 6));
    for (var y = x0; y <= x1; y += step) {
      var x = p.l + (y - x0) / (x1 - x0) * (W - p.l - p.r);
      ctx.fillText(String(y), x, H - p.b + 20);
      ctx.fillRect(Math.round(x) + 0.5, H - p.b + 2, 1, 5);
    }
    ctx.restore();
  }

  function marks(P, upto, alpha) {
    var n = P.length - 1;
    for (var i = 0; i < P.length; i++) {
      if (i / n > upto) break;
      var d = P[i];
      if (d.flag) {
        ctx.save();
        ctx.strokeStyle = 'rgba(196,98,63,' + (0.85 * alpha).toFixed(3) + ')';
        ctx.lineWidth = 1.4;
        ctx.beginPath(); ctx.arc(d.x, d.y, 4.2, 0, Math.PI * 2); ctx.stroke();
        ctx.restore();
      } else {
        ctx.fillStyle = 'rgba(201,164,100,' + (0.5 * alpha).toFixed(3) + ')';
        ctx.beginPath(); ctx.arc(d.x, d.y, 1.7, 0, Math.PI * 2); ctx.fill();
      }
    }
  }

  function trace(s, upto, alpha) {
    var P = project(s);
    ctx.save();
    ctx.lineJoin = 'round'; ctx.lineCap = 'round';

    /* soft halo under the trace */
    ctx.strokeStyle = 'rgba(201,164,100,' + (0.10 * alpha).toFixed(3) + ')';
    ctx.lineWidth = 7;
    stroke(P, upto);

    ctx.strokeStyle = 'rgba(201,164,100,' + (0.72 * alpha).toFixed(3) + ')';
    ctx.lineWidth = 1.6;
    var head = stroke(P, upto);

    marks(P, upto, alpha);

    if (head && upto < 1 && alpha > 0.9) {
      var g = ctx.createRadialGradient(head.x, head.y, 0, head.x, head.y, 16);
      g.addColorStop(0, 'rgba(230,206,156,.85)');
      g.addColorStop(1, 'rgba(230,206,156,0)');
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(head.x, head.y, 16, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = 'rgba(245,248,252,.95)';
      ctx.beginPath(); ctx.arc(head.x, head.y, 2.2, 0, Math.PI * 2); ctx.fill();
    }
    ctx.restore();
  }

  function caption(s) {
    if (capName) capName.textContent = s.label;
    if (capMeta) capMeta.textContent = s.meta;
  }

  /* static fallback ------------------------------------------------------ */
  function still() {
    ctx.clearRect(0, 0, W, H);
    grid(1);
    axisYears(SERIES[0], 1);
    trace(SERIES[0], 1, 1);
    caption(SERIES[0]);
  }

  if (reduced) { still(); return; }

  /* cycle ---------------------------------------------------------------- */
  var DRAW = 3400, HOLD = 3200, OUT = 900;
  var idx = 0, t0 = null, phase = 'draw';
  var running = true;

  function ease(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }

  caption(SERIES[0]);

  function frame(ts) {
    if (!running) return;
    if (t0 === null) t0 = ts;
    var e = ts - t0;
    ctx.clearRect(0, 0, W, H);

    var s = SERIES[idx];
    if (phase === 'draw') {
      var u = Math.min(1, e / DRAW);
      grid(Math.min(1, e / 700));
      axisYears(s, Math.min(1, e / 900));
      trace(s, ease(u), 1);
      if (u >= 1) { phase = 'hold'; t0 = ts; }
    } else if (phase === 'hold') {
      grid(1); axisYears(s, 1); trace(s, 1, 1);
      if (e >= HOLD) { phase = 'out'; t0 = ts; }
    } else {
      var a = 1 - Math.min(1, e / OUT);
      grid(a); axisYears(s, a); trace(s, 1, a);
      if (a <= 0) {
        idx = (idx + 1) % SERIES.length;
        phase = 'draw'; t0 = ts;
        caption(SERIES[idx]);
      }
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  /* stop the loop when the hero is off screen */
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && !running) {
          running = true; t0 = null; requestAnimationFrame(frame);
        } else if (!en.isIntersecting) {
          running = false;
        }
      });
    }, { threshold: 0 }).observe(host);
  }
})();
