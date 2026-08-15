/* The readout on a line chart.

   Every point on a line carries an invisible target. Pointing at one shows the year, the
   series it belongs to and the value read off the y axis, so a figure can be read at any
   point on the line and not only at the end of it.

   Everything here is done in the chart's own viewBox units. The SVG scales with the
   column it sits in, so working in user space means the readout scales with the rest of
   the chart and there is no screen-to-chart conversion to get wrong. The box is sized
   from the measured text and not from a guess at how wide a number will be. */
(function () {
  'use strict';

  /* The box round the readout is built in the chart's own units, from numbers that suit the
     size the type is set at when the figure is drawn in the page. BASE_K is that size, and
     it is here so the rest can be measured against it. */
  var PAD_X = 7, PAD_Y = 6, LEAD = 13, GAP = 14, BASE_K = 8.5;

  function ns(el, name) { return el.querySelector(name); }

  function setup(svg) {
    var tip = svg.querySelector('.tip');
    var hits = svg.querySelectorAll('.hit');
    if (!tip || !hits.length) return;

    var bg = ns(tip, '.tip__bg');
    var key = ns(tip, '.tip__k');
    var val = ns(tip, '.tip__v');
    var box = svg.viewBox.baseVal;

    function hide() { tip.classList.remove('is-on'); }

    function show(hit) {
      var cx = parseFloat(hit.getAttribute('cx'));
      var cy = parseFloat(hit.getAttribute('cy'));
      var label = hit.getAttribute('data-k');
      var year = hit.getAttribute('data-x');

      key.textContent = label ? label + '  ·  ' + year : year;
      val.textContent = hit.getAttribute('data-v');
      val.setAttribute('fill', hit.getAttribute('data-c'));

      /* the box has to be on the page before it can be measured */
      tip.classList.add('is-on');

      /* The same drawing is used twice: once in the page and once, larger, in the full-screen
         view on a phone, where the stylesheet sets the readout in bigger type to go with it.
         The padding and the space between the two lines are taken up in the same proportion,
         or the value would be set on top of the label it belongs to. Drawn in the page this
         works out at one and the box is exactly what it was. */
      var k = (parseFloat(getComputedStyle(key).fontSize) || BASE_K) / BASE_K;
      var padX = PAD_X * k, padY = PAD_Y * k;

      key.setAttribute('x', padX);
      key.setAttribute('y', padY + 8 * k);
      val.setAttribute('x', padX);
      val.setAttribute('y', padY + (8 + LEAD) * k);

      var w = Math.max(key.getBBox().width, val.getBBox().width) + padX * 2;
      var h = (PAD_Y * 2 + 8 + LEAD + 2) * k;
      bg.setAttribute('width', w);
      bg.setAttribute('height', h);

      /* above the point by preference, below it when there is no room, and never
         hanging off either side of the figure */
      var x = Math.min(Math.max(cx - w / 2, 2), box.width - w - 2);
      var y = cy - GAP * k - h;
      if (y < 2) y = cy + GAP * k;

      tip.setAttribute('transform', 'translate(' + x.toFixed(1) + ',' + y.toFixed(1) + ')');
    }

    for (var i = 0; i < hits.length; i++) {
      hits[i].addEventListener('pointerover', function (ev) { show(ev.currentTarget); });
      hits[i].addEventListener('pointerdown', function (ev) { show(ev.currentTarget); });
    }
    svg.addEventListener('pointerleave', hide);
  }

  var charts = document.querySelectorAll('svg.chart');
  for (var i = 0; i < charts.length; i++) setup(charts[i]);

  /* A chart copied into the full-screen view on a phone is a copy of the drawing and not
     of the listeners on it, so the copy arrives with targets that answer to nothing. This
     is how the copy gets its readout. It is the same function the page ran on its own
     charts, so the enlarged figure behaves as the small one does and there is no second
     implementation to keep in step. */
  window.chartReadout = setup;
})();
