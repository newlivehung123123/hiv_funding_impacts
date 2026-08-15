/* Region rack and small interface bits.

   Every slat expands when it is pointed at, including the regions that are still
   greyed out. A greyed slat opens to the countries in scope for that region and
   says plainly that no figures are published for it yet. The rack collapses again
   when the pointer leaves it.

   A published region's slat is an anchor: the whole panel is the link to its page,
   so a click anywhere on it navigates and none of the picking below applies. The
   greyed slats have nowhere to go, so clicking one picks it instead. A picked slat
   changes colour and stays open after the pointer has gone, so a region can be read
   at leisure or compared against the one beside it. Clicking it again lets it go, as
   does Escape. */
(function () {
  'use strict';

  var rack = document.querySelector('[data-rack]');
  if (rack) {
    var slats = Array.prototype.slice.call(rack.querySelectorAll('.slat'));
    var touch = window.matchMedia('(hover: none)').matches;
    var shut;

    function picked() {
      for (var i = 0; i < slats.length; i++) {
        if (slats[i].classList.contains('is-picked')) return slats[i];
      }
      return null;
    }

    /* a link is not a disclosure widget, so only the button slats carry the state */
    function isLink(s) { return s.tagName === 'A'; }

    function show(s, on) {
      s.classList.toggle('is-open', on);
      if (!isLink(s)) s.setAttribute('aria-expanded', on ? 'true' : 'false');
    }

    function open(el) {
      clearTimeout(shut);
      slats.forEach(function (s) { show(s, s === el); });
    }
    function closeAll() {
      var keep = picked();
      slats.forEach(function (s) { show(s, s === keep); });
    }
    function pick(el) {
      var on = !el.classList.contains('is-picked');
      slats.forEach(function (s) {
        var me = s === el && on;
        s.classList.toggle('is-picked', me);
        if (!isLink(s)) s.setAttribute('aria-pressed', me ? 'true' : 'false');
      });
      open(el);
    }

    slats.forEach(function (s) {
      if (!isLink(s)) {
        s.setAttribute('aria-expanded', 'false');
        s.setAttribute('aria-pressed', 'false');
      }
      s.addEventListener('mouseenter', function () { if (!touch) open(s); });
      s.addEventListener('focus', function () { open(s); });

      /* An anchor slat goes to its page on click and on Enter, and the browser does
         both by itself, so the picking below is only wired up for the others.

         A screen with no pointer is the exception. On a pointer device the slat has
         already opened under the pointer before anyone clicks it, so the reader has
         seen the countries in it and leaves for the region's page having chosen to.
         A finger has no hover: the first touch is the click, and the page changes
         under a reader who never saw what was in the slat. So on a touch screen the
         first tap opens it and a second one follows the link, which is how the slats
         with nowhere to go already behave. */
      if (isLink(s)) {
        if (touch) {
          s.addEventListener('click', function (ev) {
            if (s.classList.contains('is-open')) return;
            ev.preventDefault();
            open(s);
          });
        }
        return;
      }

      s.addEventListener('click', function () { pick(s); });
      /* a div is not a button, so the keyboard has to be wired by hand */
      s.addEventListener('keydown', function (ev) {
        if (ev.target !== s) return;
        if (ev.key === 'Enter' || ev.key === ' ' || ev.key === 'Spacebar') {
          ev.preventDefault();
          pick(s);
        }
      });
    });

    rack.addEventListener('mouseleave', function () {
      if (touch) return;
      shut = setTimeout(closeAll, 140);
    });
    rack.addEventListener('mouseenter', function () { clearTimeout(shut); });
    rack.addEventListener('keydown', function (ev) {
      if (ev.key !== 'Escape') return;
      slats.forEach(function (s) {
        s.classList.remove('is-picked');
        if (!isLink(s)) s.setAttribute('aria-pressed', 'false');
      });
      closeAll();
      if (document.activeElement) document.activeElement.blur();
    });
  }

  /* narrow-screen navigation */
  var tog = document.querySelector('[data-navtoggle]');
  var nav = document.querySelector('[data-nav]');
  if (tog && nav) {
    tog.addEventListener('click', function () {
      var on = nav.classList.toggle('is-open');
      tog.setAttribute('aria-expanded', on ? 'true' : 'false');
      tog.textContent = on ? 'Close' : 'Menu';
    });
  }

  /* The masthead draws in once the page is scrolled and opens back out at the top.
     The two thresholds are deliberately apart: a single one makes the bar flicker
     when the reader stops with the page a few pixels down. */
  var head = document.querySelector('[data-masthead]');
  if (head) {
    var drawn = false, queued = false;

    function measure() {
      queued = false;
      var y = window.pageYOffset || document.documentElement.scrollTop;
      if (!drawn && y > 26) { drawn = true; head.classList.add('is-drawn'); }
      else if (drawn && y < 8) { drawn = false; head.classList.remove('is-drawn'); }
    }
    window.addEventListener('scroll', function () {
      if (queued) return;
      queued = true;
      window.requestAnimationFrame(measure);
    }, { passive: true });
    measure();
  }

  /* Regions in the masthead. It opens on hover on a pointer device and on click
     everywhere, so it works the same from the keyboard and on a phone, where the
     list unfolds under the button instead of hanging off it. */
  var grp = document.querySelector('[data-navgrp]');
  if (grp) {
    var btn = grp.querySelector('[data-navbtn]');
    var fine = window.matchMedia('(hover: hover)').matches;
    var away;

    function menu(on) {
      clearTimeout(away);
      grp.classList.toggle('is-open', on);
      btn.setAttribute('aria-expanded', on ? 'true' : 'false');
    }

    btn.addEventListener('click', function () {
      menu(!grp.classList.contains('is-open'));
    });
    if (fine) {
      grp.addEventListener('mouseenter', function () { menu(true); });
      grp.addEventListener('mouseleave', function () {
        away = setTimeout(function () { menu(false); }, 120);
      });
    }
    grp.addEventListener('keydown', function (ev) {
      if (ev.key !== 'Escape') return;
      menu(false);
      btn.focus();
    });
    /* tabbing out of the list closes it; clicking elsewhere on the page does too */
    grp.addEventListener('focusout', function (ev) {
      if (!grp.contains(ev.relatedTarget)) menu(false);
    });
    document.addEventListener('click', function (ev) {
      if (!grp.contains(ev.target)) menu(false);
    });
  }
})();
