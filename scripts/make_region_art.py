#!/usr/bin/env python3
"""
Draw a map of each region: one SVG showing the countries that region covers picked
out against their neighbours. Boundaries come from Natural Earth, which is in the
public domain, so the files can be redistributed with the site.

    python3 scripts/make_region_art.py                 # uses the cached boundaries
    python3 scripts/make_region_art.py --fetch         # downloads them first

The download is the only part that touches the network, and it is off by default.

Nothing on the site draws these at the moment. The rack used to show a map over the
photograph behind each region and the two competed, so the maps came out and the
photographs stayed. The script is kept because the maps are cheap to regenerate and
would suit a region page, where there is room for a map to be looked at and not just
read through. Run it and the eight SVGs reappear in site/static/img/regions.

Source: Natural Earth 1:50m Admin 0 countries, via the natural-earth-vector
repository. Licence: public domain (https://www.naturalearthdata.com/about/terms-of-use/).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hivimpact.config.regions import REGIONS  # noqa: E402

NE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
# 1:110m carries the whole world at a weight the page can afford. It leaves out the
# smaller island states, so 1:50m is used to fill those in and nothing else.
SCALES = ("110m", "50m")
REF = ROOT / "data" / "reference"
OUT = ROOT / "site" / "static" / "img" / "regions"

# the drawing is cropped to this shape before the stylesheet crops it again
W, H = 900.0, 620.0
PAD = 0.30          # share of the region's own extent left as margin
MIN_AREA = 14.0     # drop islands smaller than this many square units once drawn
THIN = 1.5          # drop points closer together than this, measured after projection


# ── boundaries ────────────────────────────────────────────────────────────────
def load(fetch: bool) -> list:
    """
    One feature per country: the 1:110m outline where there is one, the 1:50m
    outline for the island states 1:110m omits.
    """
    sets = {}
    for scale in SCALES:
        name = f"ne_{scale}_admin_0_countries.geojson"
        path = REF / name
        if fetch or not path.exists():
            import urllib.request
            REF.mkdir(parents=True, exist_ok=True)
            print(f"fetching {NE + name}")
            with urllib.request.urlopen(NE + name, timeout=120) as r:
                path.write_bytes(r.read())
            print(f"  cached -> {path.relative_to(ROOT)} ({path.stat().st_size/1e6:.1f} MB)")
        sets[scale] = json.loads(path.read_text())["features"]

    feats, seen = [], set()
    for scale in SCALES:
        for f in sets[scale]:
            iso = iso_of(f["properties"])
            if not iso or iso in seen:
                continue
            seen.add(iso)
            feats.append(f)
    return feats


def iso_of(props: dict) -> str:
    for k in ("ISO_A3", "ISO_A3_EH", "ADM0_A3"):
        v = props.get(k)
        if v and v != "-99":
            return v
    return ""


def rings(geom: dict) -> list:
    """Outer rings only. Holes are invisible at this opacity and cost bytes."""
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    if geom["type"] == "MultiPolygon":
        return [p[0] for p in geom["coordinates"]]
    return []


# ── framing ───────────────────────────────────────────────────────────────────
def frame_for(shapes: list) -> tuple:
    """
    A window on the world in degrees, sized to the region and shaped like the slot
    it is drawn into. Regions that straddle the antimeridian are measured on a
    0-360 longitude line so the Pacific does not come out inside out.
    """
    lons = [x for ring in shapes for x, _ in ring]
    wrap = max(lons) > 150 and min(lons) < -150
    if wrap:
        shapes = [[(x + 360 if x < 0 else x, y) for x, y in ring] for ring in shapes]
        lons = [x for ring in shapes for x, _ in ring]
    lats = [y for ring in shapes for _, y in ring]

    x0, x1, y0, y1 = min(lons), max(lons), min(lats), max(lats)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    k = math.cos(math.radians(max(-70, min(70, cy))))     # degrees of longitude are shorter away from the equator

    # widen or heighten whichever side is short until the window matches the slot
    half_w = max((x1 - x0) / 2 * (1 + PAD), 1e-6)
    half_h = max((y1 - y0) / 2 * (1 + PAD), 1e-6)
    if (half_w * k) / half_h < W / H:
        half_w = half_h * (W / H) / k
    else:
        half_h = half_w * k * (H / W)
    return cx - half_w, cx + half_w, cy - half_h, cy + half_h, k, wrap


def path_for(ring: list, fr: tuple) -> str:
    """One projected ring as an SVG path, thinned to whole pixels."""
    x0, x1, y0, y1, _k, wrap = fr
    sx, sy = W / (x1 - x0), H / (y1 - y0)
    pts, area, px, py = [], 0.0, None, None
    for lon, lat in ring:
        if wrap and lon < 0:
            lon += 360
        x = (lon - x0) * sx
        y = H - (lat - y0) * sy
        if px is not None:
            area += px * y - x * py
            if abs(x - px) < THIN and abs(y - py) < THIN:
                continue
        pts.append(f"{x:.1f} {y:.1f}")
        px, py = x, y
    if len(pts) < 3 or abs(area) / 2 < MIN_AREA:
        return ""
    return "M" + "L".join(pts) + "Z"


def visible(ring: list, fr: tuple) -> bool:
    x0, x1, y0, y1, _k, wrap = fr
    for lon, lat in ring:
        if wrap and lon < 0:
            lon += 360
        if x0 <= lon <= x1 and y0 <= lat <= y1:
            return True
    return False


# ── drawing ───────────────────────────────────────────────────────────────────
def draw(region: dict, feats: list) -> str:
    want = set(region["iso3"])
    mine = [f for f in feats if iso_of(f["properties"]) in want]
    if not mine:
        raise SystemExit(f"no boundaries matched {region['slug']}")

    fr = frame_for([r for f in mine for r in rings(f["geometry"])])
    near, own = [], []
    for f in feats:
        for ring in rings(f["geometry"]):
            if not visible(ring, fr):
                continue
            d = path_for(ring, fr)
            if d:
                (own if iso_of(f["properties"]) in want else near).append(d)

    # Everything is drawn in grey. The stylesheet blends it into whichever colour
    # the slat is carrying, so only the lightness of each layer matters here.
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" '
        f'width="{W:.0f}" height="{H:.0f}" role="img" '
        f'aria-label="{region["name"]} and the countries around it">\n'
        f'<title>{region["name"]}</title>\n'
        f'<desc>Country boundaries from Natural Earth, 1:50m, public domain.</desc>\n'
        f'<g fill="#4a4a4a" stroke="#5e5e5e" stroke-width="0.6" '
        f'stroke-linejoin="round">\n<path d="{"".join(near)}"/>\n</g>\n'
        f'<g fill="#e8e8e8" stroke="#ffffff" stroke-width="0.9" '
        f'stroke-linejoin="round">\n<path d="{"".join(own)}"/>\n</g>\n'
        f'</svg>\n'
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fetch", action="store_true",
                    help="download the Natural Earth boundaries before drawing")
    args = ap.parse_args()

    feats = load(args.fetch)
    OUT.mkdir(parents=True, exist_ok=True)
    for r in REGIONS:
        svg = draw(r, feats)
        p = OUT / f"{r['slug']}.svg"
        p.write_text(svg)
        print(f"  {p.name:38s} {p.stat().st_size/1024:6.1f} KB")


if __name__ == "__main__":
    main()
