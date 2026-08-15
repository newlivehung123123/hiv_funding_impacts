/* Chart or table, and the download panel.

   Both views of a figure are already in the page — the chart drawn at build time, the table
   written out beneath it — so switching is a matter of which one is hidden. Nothing is
   fetched, nothing is redrawn, and a figure switched to its table and back is in exactly the
   state it started in. The two files behind the download button were also written at build
   time, so the button is an ordinary link and not an assembly job done in the browser.

   The markup carries the state: a figure's data-view says which of the two it is showing, and
   the CSS follows that attribute. The state is read off the DOM and not held here, so there
   is one answer to what a figure is showing and not two that can disagree. */
(function () {
  'use strict';

  /* ---- chart or table --------------------------------------------------------------- */

  function show(fig, view) {
    if (fig.getAttribute('data-view') === view) return;
    fig.setAttribute('data-view', view);
    // the attribute is the whole of the state. The stylesheet reads it and hides the other
    // view, which also takes that view out of the tab order and out of what a screen reader
    // walks, so there is nothing further to keep in step here
    fig.querySelectorAll('[data-view-to]').forEach(function (b) {
      var on = b.getAttribute('data-view-to') === view;
      b.classList.toggle('is-on', on);
      b.setAttribute('aria-selected', on ? 'true' : 'false');
    });
  }

  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-view-to]');
    if (!b) return;
    var fig = b.closest('[data-figure]');
    if (fig) show(fig, b.getAttribute('data-view-to'));
  });

  // left and right move between the two tabs, which is how a tablist is expected to behave
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
    var b = e.target.closest && e.target.closest('[data-view-to]');
    if (!b) return;
    var tabs = [].slice.call(b.parentNode.querySelectorAll('[data-view-to]'));
    var next = tabs[(tabs.indexOf(b) + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length];
    next.focus();
    next.click();
    e.preventDefault();
  });

  /* ---- the download panel ----------------------------------------------------------- */

  var dlg = document.querySelector('[data-dlg]');
  var opener = null;

  function fill(btn) {
    // the file counts its rows the long way and the table on screen counts them the wide way,
    // so the two numbers differ and this one says which of them it is
    dlg.querySelector('[data-dlg-sub]').textContent =
      btn.getAttribute('data-dl-title') + ' · ' +
      btn.getAttribute('data-dl-rows') + ' rows in the file';

    var csv = dlg.querySelector('[data-dlg-csv]');
    csv.href = btn.getAttribute('data-dl-csv');
    dlg.querySelector('[data-dlg-csv-size]').textContent = btn.getAttribute('data-dl-csv-size') || '';
    // a figure of years has a row per year and series; a figure of categories has one per
    // category, and saying the wrong one would misdescribe the file before it is opened
    dlg.querySelector('[data-dlg-shape]').textContent =
      btn.getAttribute('data-dl-shape') + ' Plain text, opens anywhere.';

    // the spreadsheet is only offered when the build produced one
    var xlsx = dlg.querySelector('[data-dlg-xlsx]');
    var href = btn.getAttribute('data-dl-xlsx');
    xlsx.hidden = !href;
    if (href) {
      xlsx.href = href;
      dlg.querySelector('[data-dlg-xlsx-size]').textContent =
        btn.getAttribute('data-dl-xlsx-size') || '';
    }
  }

  function open(btn) {
    opener = btn;
    fill(btn);
    dlg.hidden = false;
    document.body.classList.add('is-locked');
    var first = dlg.querySelector('[data-dlg-csv]');
    if (first) first.focus();
  }

  function close() {
    dlg.hidden = true;
    document.body.classList.remove('is-locked');
    // back to the button that opened it, so a keyboard is not returned to the top of the page
    if (opener) opener.focus();
    opener = null;
  }

  if (dlg) {
    document.addEventListener('click', function (e) {
      var btn = e.target.closest && e.target.closest('[data-dl-open]');
      // the link would otherwise fetch the CSV on its own, which is what it is there to do
      // when there is no scripting to open the panel instead
      if (btn) { e.preventDefault(); open(btn); return; }
      if (e.target.closest && e.target.closest('[data-dlg-close]')) close();
      // choosing a file is the end of the errand the panel was opened for
      if (e.target.closest && e.target.closest('.dlg__opt')) setTimeout(close, 120);
    });

    document.addEventListener('keydown', function (e) {
      if (dlg.hidden) return;
      if (e.key === 'Escape') { close(); return; }
      if (e.key !== 'Tab') return;
      // while it is open the panel is the whole of the page, so focus stays inside it
      var f = [].slice.call(dlg.querySelectorAll('a[href],button')).filter(function (el) {
        return !el.hidden && el.offsetParent !== null;
      });
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { last.focus(); e.preventDefault(); }
      else if (!e.shiftKey && document.activeElement === last) { first.focus(); e.preventDefault(); }
    });
  }

  /* ---- the chart, full screen on a phone -------------------------------------------- */

  /* One of these to a page, filled from whichever figure was tapped. What goes into it is a
     copy of the drawing already on the page, so the enlarged figure is the figure the reader
     was looking at and cannot have been built from anything else. */

  var cv = document.querySelector('[data-cview]');
  // The same condition the stylesheet draws the control under, because a control that is
  // drawn and does nothing is worse than one that was never drawn, and a drawing that opens
  // where no control said it would is worse again. A finger, on a screen no wider than a
  // handset held on its side; a desktop window dragged narrow is neither of those.
  var offer = window.matchMedia('(pointer:coarse) and (max-width:1000px)');
  var cvFrom = null;

  function empty(el) { while (el.firstChild) el.removeChild(el.firstChild); }

  function cvFill(fig) {
    var svg = fig.querySelector('.figure__chart svg.chart');
    if (!svg) return false;

    var stage = cv.querySelector('[data-cview-stage]');
    empty(stage);
    var clone = svg.cloneNode(true);
    // the copy arrives showing whatever the original was showing, and what it should show
    // is nothing until a point is asked for
    var tip = clone.querySelector('.tip');
    if (tip) tip.classList.remove('is-on');
    stage.appendChild(clone);
    // a copy carries the drawing and not the listeners on it, so the targets are wired again
    // here, by the same function that wired the original
    if (typeof window.chartReadout === 'function') window.chartReadout(clone);

    var t = fig.querySelector('.figure__t');
    var s = fig.querySelector('.figure__src');
    cv.querySelector('[data-cview-t]').textContent = t ? t.textContent.trim() : '';
    cv.querySelector('[data-cview-s]').textContent = s ? s.textContent.trim() : '';

    var box = cv.querySelector('[data-cview-legend]');
    empty(box);
    var leg = fig.querySelector('.legend-inline');
    if (leg) box.appendChild(leg.cloneNode(true));

    // a bar chart has no points on a line to aim at, so it is not offered a readout it
    // has not got
    cv.querySelector('[data-cview-hint]').textContent =
      clone.querySelector('.hit') ? 'Tap a point for its value' : '';
    return true;
  }

  function cvOpen(fig) {
    if (!cvFill(fig)) return;
    cvFrom = fig.querySelector('.cvbtn');
    cv.hidden = false;
    document.body.classList.add('is-locked');
    var x = cv.querySelector('.cview__x');
    if (x) x.focus();
  }

  function cvClose() {
    cv.hidden = true;
    document.body.classList.remove('is-locked');
    // the copy is thrown away with the view. Left in place it would be a second chart in the
    // document answering to the same styling as the one on the page
    empty(cv.querySelector('[data-cview-stage]'));
    if (cvFrom) cvFrom.focus();
    cvFrom = null;
  }

  if (cv) {
    document.addEventListener('click', function (e) {
      if (!e.target.closest) return;
      if (e.target.closest('[data-cview-close]')) { cvClose(); return; }
      // above phone width the figure is already the size it was drawn for, and the page is
      // the better place to read it from
      if (!offer.matches) return;
      var panel = e.target.closest('[data-cview-open]');
      if (!panel) return;
      var fig = panel.closest('[data-figure]');
      // the table was legible to begin with and was never the thing being fixed here; the
      // figure's own attribute says which of the two it is showing
      if (!fig || fig.getAttribute('data-view') !== 'chart') return;
      cvOpen(fig);
    });

    document.addEventListener('keydown', function (e) {
      if (cv.hidden) return;
      if (e.key === 'Escape') { cvClose(); return; }
      // while it is open it is the whole of the screen, so the tab key stays in it
      if (e.key === 'Tab') { cv.querySelector('.cview__x').focus(); e.preventDefault(); }
    });

    // A window dragged wide used to be able to leave a reader holding a full-screen copy of
    // something already legible on the page behind it, and there was a listener here to shut
    // it. Nothing opens this on a desktop now, so the case it watched for cannot arise, and a
    // handset that turns is a width change this must sit still through.
  }
}());
