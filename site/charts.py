"""
Hand-drawn SVG figures.

There is no charting library here on purpose. Every library ships a house style — its own
axis furniture, its own default palette, its own idea of how much ink a gridline deserves —
and overriding all of it costs more than drawing the marks directly. These functions emit
plain SVG that inherits the site's stylesheet, so a figure looks like the page it sits on.

Conventions that the rest of the build relies on:
  * a point from an incomplete reporting period is drawn as an open rust ring, never as a
    filled dot, so a partial year cannot be read as a fall;
  * confidence bounds, where a source publishes them, are drawn as a band behind the line;
  * the y axis starts at zero for money and counts, and at the data for percentages.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence

# stroke colours, in the order series are handed in
STROKE_HEX = ["#C9A464", "#C8D3E0", "#4E6688", "#E6CE9C", "#7B90AC", "#0B3F74"]


# --- number formatting -------------------------------------------------------------------
def fmt_value(v: float, unit: str) -> str:
    """A figure as it would be written in a sentence."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "—"
    if unit == "USD":
        a = abs(v)
        if a >= 1e9:
            return f"${v/1e9:,.2f}bn"
        if a >= 1e6:
            return f"${v/1e6:,.1f}m"
        if a >= 1e3:
            return f"${v/1e3:,.0f}k"
        return f"${v:,.0f}"
    if unit == "percent":
        return f"{v:,.1f}%"
    return f"{v:,.0f}"


def fmt_tick(v: float, unit: str) -> str:
    """Shorter still, for an axis."""
    if unit == "USD":
        a = abs(v)
        if a >= 1e9:
            return f"${v/1e9:g}bn"
        if a >= 1e6:
            return f"${v/1e6:g}m"
        if a >= 1e3:
            return f"${v/1e3:g}k"
        return f"${v:g}"
    if unit == "percent":
        return f"{v:g}%"
    a = abs(v)
    if a >= 1e6:
        return f"{v/1e6:g}m"
    if a >= 1e3:
        return f"{v/1e3:g}k"
    return f"{v:g}"


def nice_ticks(lo: float, hi: float, n: int = 4) -> List[float]:
    if hi <= lo:
        hi = lo + 1
    raw = (hi - lo) / n
    mag = 10 ** math.floor(math.log10(raw)) if raw > 0 else 1
    for m in (1, 2, 2.5, 5, 10):
        if raw / mag <= m:
            step = m * mag
            break
    else:
        step = 10 * mag
    start = math.floor(lo / step) * step
    out, v = [], start
    while v <= hi + step * 1e-9:
        out.append(round(v, 10))
        v += step
    return out


def _esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# --- line chart --------------------------------------------------------------------------
def line_chart(series: Sequence[Dict],
               unit: str = "count",
               width: int = 1180,
               height: int = 330,
               zero_base: Optional[bool] = None,
               show_last: bool = True) -> str:
    """
    series: [{"label": str, "points": [(year, value), ...],
              "flags": [bool, ...] (optional),
              "band":  [(year, lo, hi), ...] (optional)}]
    """
    series = [s for s in series if s.get("points")]
    if not series:
        return ""
    if zero_base is None:
        zero_base = unit in ("USD", "count")

    pl, pr, pt, pb = 74, 26, 18, 36
    iw, ih = width - pl - pr, height - pt - pb

    xs = [p[0] for s in series for p in s["points"]]
    ys = [p[1] for s in series for p in s["points"]]
    for s in series:
        for b in s.get("band") or []:
            ys.extend([b[1], b[2]])
    x0, x1 = min(xs), max(xs)
    if x1 == x0:
        x0, x1 = x0 - 1, x1 + 1
    y_lo, y_hi = min(ys), max(ys)
    if zero_base:
        y_lo = min(0.0, y_lo)
    span = (y_hi - y_lo) or (abs(y_hi) or 1.0)
    y_hi += span * 0.10
    if not zero_base:
        y_lo -= span * 0.10

    ticks = nice_ticks(y_lo, y_hi, 4)
    y_lo, y_hi = min(y_lo, ticks[0]), max(y_hi, ticks[-1])

    def X(v):
        return pl + (v - x0) / (x1 - x0) * iw

    def Y(v):
        return pt + ih - (v - y_lo) / (y_hi - y_lo) * ih

    # the kind of chart is named on the element because the three kinds label their x axis
    # differently — years here, a sentence long each on the other two — and the full-screen
    # view on a phone can only enlarge the labels as far as the longest of them allows
    out = [f'<svg class="chart chart--line" viewBox="0 0 {width} {height}" '
           f'preserveAspectRatio="xMidYMid meet" role="img">']

    for t in ticks:
        y = round(Y(t), 1)
        out.append(f'<line class="gridline" x1="{pl}" y1="{y}" x2="{pl+iw}" y2="{y}"/>')
        out.append(f'<text class="tick" x="{pl-10}" y="{y+3.4}" text-anchor="end">'
                   f'{_esc(fmt_tick(t, unit))}</text>')

    step = max(1, int(round((x1 - x0) / 8)))
    yr = x0
    while yr <= x1:
        x = round(X(yr), 1)
        out.append(f'<text class="tick" x="{x}" y="{pt+ih+20}" text-anchor="middle">{yr}</text>')
        yr += step
    out.append(f'<line class="axis" x1="{pl}" y1="{pt+ih}" x2="{pl+iw}" y2="{pt+ih}"/>')

    for i, s in enumerate(series):
        col = STROKE_HEX[i % len(STROKE_HEX)]
        band = s.get("band")
        if band:
            up = " ".join(f"{X(b[0]):.1f},{Y(b[2]):.1f}" for b in band)
            dn = " ".join(f"{X(b[0]):.1f},{Y(b[1]):.1f}" for b in reversed(band))
            out.append(f'<polygon class="band" points="{up} {dn}"/>')

        # The line, its dots and its end label are one object, so they are grouped: anything
        # applied to a series is applied once, to the group. The band stays outside it, being
        # a backdrop to the series and not part of it.
        out.append('<g class="ser">')
        pts = s["points"]
        # The line is only drawn between years that sit next to each other. Where a year is
        # absent from the series the line stops and starts again on the far side of the hole,
        # so that a missing year is never bridged by a segment that looks like a measurement.
        # A year left on its own between two holes keeps its dot and has no line at all.
        gap = min((pts[k + 1][0] - pts[k][0] for k in range(len(pts) - 1)), default=1) or 1
        d = " ".join(("M" if k == 0 or (p[0] - pts[k - 1][0]) > gap else "L")
                     + f"{X(p[0]):.1f} {Y(p[1]):.1f}"
                     for k, p in enumerate(pts))
        dash = ' stroke-dasharray="4 3"' if s.get("dashed") else ""
        out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.9" '
                   f'stroke-linejoin="round" stroke-linecap="round"{dash}/>')

        flags = s.get("flags") or [False] * len(pts)
        for k, p in enumerate(pts):
            cx, cy = X(p[0]), Y(p[1])
            if flags[k]:
                out.append(f'<circle class="dot--flag" cx="{cx:.1f}" cy="{cy:.1f}" r="4.6"/>')
            else:
                out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.4" fill="{col}"/>')

        if show_last and pts:
            lx, ly = X(pts[-1][0]), Y(pts[-1][1])
            anchor = "end" if lx > pl + iw - 70 else "start"
            dx = -8 if anchor == "end" else 8
            out.append(f'<text class="val" x="{lx+dx:.1f}" y="{ly-9:.1f}" '
                       f'text-anchor="{anchor}" fill="{col}">'
                       f'{_esc(fmt_value(pts[-1][1], unit))}</text>')
        out.append('</g>')

    # A target over every point, so that pointing anywhere near one reads its value out.
    # These are drawn last and are invisible: a transparent fill still takes the pointer,
    # whereas no fill at all would let it through. The radius is half the gap between
    # points, so the whole line is covered without one point stealing its neighbour's.
    n_pts = max(len(s["points"]) for s in series)
    reach = min(20.0, max(7.0, iw / max(1, n_pts - 1) / 2)) if n_pts > 1 else 14.0
    for i, s in enumerate(series):
        col = STROKE_HEX[i % len(STROKE_HEX)]
        for p in s["points"]:
            out.append(f'<circle class="hit" cx="{X(p[0]):.1f}" cy="{Y(p[1]):.1f}" '
                       f'r="{reach:.1f}" data-v="{_esc(fmt_value(p[1], unit))}" '
                       f'data-k="{_esc(str(s.get("label") or ""))}" data-x="{p[0]}" '
                       f'data-c="{col}"/>')

    # The readout itself, empty until something is pointed at. It is sized and moved by
    # site/static/js/chart.js, which measures the text instead of guessing at it.
    out.append('<g class="tip" aria-hidden="true">'
               '<rect class="tip__bg" rx="3"/>'
               '<text class="tip__k"></text>'
               '<text class="tip__v"></text>'
               '</g>')

    out.append("</svg>")
    return "".join(out)


# --- bar chart ---------------------------------------------------------------------------
def bar_chart(points: Sequence, unit: str = "count", flags: Optional[Sequence[bool]] = None,
              width: int = 1180, height: int = 300) -> str:
    if not points:
        return ""
    pl, pr, pt, pb = 74, 26, 22, 36
    iw, ih = width - pl - pr, height - pt - pb
    flags = list(flags or [False] * len(points))

    ys = [p[1] for p in points]
    ticks = nice_ticks(min(0.0, min(ys)), max(ys) * 1.12, 4)
    y_lo, y_hi = ticks[0], ticks[-1]

    def Y(v):
        return pt + ih - (v - y_lo) / (y_hi - y_lo) * ih

    n = len(points)
    slot = iw / n
    bw = min(46.0, slot * 0.62)

    out = [f'<svg class="chart chart--bar" viewBox="0 0 {width} {height}" '
           f'preserveAspectRatio="xMidYMid meet" role="img">']
    for t in ticks:
        y = round(Y(t), 1)
        out.append(f'<line class="gridline" x1="{pl}" y1="{y}" x2="{pl+iw}" y2="{y}"/>')
        out.append(f'<text class="tick" x="{pl-10}" y="{y+3.4}" text-anchor="end">'
                   f'{_esc(fmt_tick(t, unit))}</text>')
    for i, (lab, v) in enumerate(points):
        cx = pl + slot * (i + 0.5)
        y = Y(v)
        cls = "bar--flag" if flags[i] else "bar"
        out.append(f'<rect class="{cls}" x="{cx-bw/2:.1f}" y="{y:.1f}" width="{bw:.1f}" '
                   f'height="{max(0.0, Y(0)-y):.1f}"/>')
        out.append(f'<text class="tick" x="{cx:.1f}" y="{pt+ih+20}" text-anchor="middle">'
                   f'{_esc(lab)}</text>')
        out.append(f'<text class="val" x="{cx:.1f}" y="{y-7:.1f}" text-anchor="middle">'
                   f'{_esc(fmt_value(v, unit))}</text>')
    out.append(f'<line class="axis" x1="{pl}" y1="{pt+ih}" x2="{pl+iw}" y2="{pt+ih}"/>')
    out.append("</svg>")
    return "".join(out)


# --- cascade -----------------------------------------------------------------------------
def cascade_chart(stages: Sequence[Dict], width: int = 1180, height: int = 300) -> str:
    """stages: [{"label": str, "value": float, "pct": str|None}] — the 95-95-95 staircase."""
    stages = [s for s in stages if s.get("value")]
    if not stages:
        return ""
    pl, pr, pt, pb = 24, 24, 34, 52
    iw, ih = width - pl - pr, height - pt - pb
    top = max(s["value"] for s in stages)
    n = len(stages)
    slot = iw / n
    bw = min(160.0, slot * 0.66)

    out = [f'<svg class="chart chart--cascade" viewBox="0 0 {width} {height}" '
           f'preserveAspectRatio="xMidYMid meet" role="img">']
    for i, s in enumerate(stages):
        h = ih * (s["value"] / top)
        cx = pl + slot * (i + 0.5)
        y = pt + ih - h
        cls = "cascade--hl" if i == 0 else "cascade"
        out.append(f'<rect class="{cls}" x="{cx-bw/2:.1f}" y="{y:.1f}" '
                   f'width="{bw:.1f}" height="{h:.1f}"/>')
        out.append(f'<text class="val" x="{cx:.1f}" y="{y-11:.1f}" text-anchor="middle">'
                   f'{_esc(fmt_value(s["value"], "count"))}</text>')
        out.append(f'<text class="lbl" x="{cx:.1f}" y="{pt+ih+20}" text-anchor="middle">'
                   f'{_esc(s["label"])}</text>')
        if s.get("pct"):
            out.append(f'<text class="tick" x="{cx:.1f}" y="{pt+ih+37}" text-anchor="middle">'
                       f'{_esc(s["pct"])}</text>')
    out.append(f'<line class="axis" x1="{pl}" y1="{pt+ih}" x2="{pl+iw}" y2="{pt+ih}"/>')
    out.append("</svg>")
    return "".join(out)


# --- sparkline (tiles) -------------------------------------------------------------------
def sparkline(values: Sequence[float], width: int = 300, height: int = 72) -> tuple:
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return "", ""
    lo, hi = min(vals), max(vals)
    if hi == lo:
        hi = lo + 1
    n = len(vals) - 1
    pts = [(width * i / n, height - 8 - (v - lo) / (hi - lo) * (height - 20))
           for i, v in enumerate(vals)]
    line = " ".join(("M" if i == 0 else "L") + f"{x:.1f} {y:.1f}" for i, (x, y) in enumerate(pts))
    fill = line + f" L{width} {height} L0 {height} Z"
    return line, fill
