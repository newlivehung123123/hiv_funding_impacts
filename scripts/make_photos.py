#!/usr/bin/env python3
"""
Prepare the photographs shown behind the panels and cards on the site.

The originals live in assets/photos, one per segment, named after the slug the build
looks them up by. They are full-size downloads and are deliberately kept out of
site/static so they are never published. This script writes a small WebP copy of each
one into site/static/img/photos, which is what the site actually serves.

    python3 scripts/make_photos.py

Nothing here touches the network. Replace an original and run it again to update the
site copy; the build picks the new file up on its next run.

The slug carries a prefix saying what the photograph is for, because that decides how
it is cropped and how large a copy is worth keeping:

    region-*     the eight regions on the home page rack
    domain-*     the six data categories
    country-*    the countries of every live region, by ISO3
    rel-*        the three source relationships on the reconciliation page
    panel-*      the six files on the downloads page

The photographs are shown desaturated, at low opacity and behind a gradient wash, so
they carry shape and tone, not detail. That is why the copies are small: at the
size and opacity they are drawn, a larger file buys nothing.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "photos"
OUT = ROOT / "site" / "static" / "img" / "photos"

QUALITY = 70

# A slat on the home page opens to about 1100 pixels across and three times as wide as
# it is tall. A card or a tile is a third of that and much closer to square. Cropping
# to something near the shape it will be drawn at means the browser throws away less,
# so the subject survives; sizing to what it will be drawn at keeps the files honest.
SHAPE = {"region": (1280, 2.1)}
SHAPE_DEFAULT = (900, 1.5)

# Some of these pictures are bright — a white building against a clear sky, a market
# under lights — and light text cannot be read over them however the stylesheet is
# arranged. The picture is not covered over; instead the highlights are rolled off here,
# so everything above KNEE is compressed towards CEIL, which takes the glare out while
# leaving the detail and the shadows alone. Every segment then arrives in the same
# tonal range, so one setting in the stylesheet suits all of them.
KNEE = 0.42         # where the shoulder starts
CEIL = 0.62         # the brightest anything is allowed to become
FLOOR = 0.03        # a little lift, so the darkest pictures do not go to pure black


def shoulder() -> list[int]:
    lut = []
    slope = (CEIL - KNEE) / (1 - KNEE)
    for v in range(256):
        x = v / 255
        y = x if x < KNEE else KNEE + (x - KNEE) * slope
        lut.append(round(255 * (FLOOR + y * (1 - FLOOR))))
    return lut


# Where the eye should land after the stylesheet crops the picture to its panel. 0.5 is
# the middle of the frame; smaller keeps the top. Only the pictures whose subject sits
# high or low in the frame need one.
FOCUS = {
    "region-eastern-europe-and-central-asia": 0.38,   # the dome
    "region-latin-america-and-the-caribbean": 0.40,   # the child's face and hat
    "region-eastern-and-southern-africa": 0.42,       # the headdress
    "region-east-asia-and-the-pacific": 0.44,         # the pavilion roof
}


def prepare(path: Path) -> tuple[Path, int]:
    slug = path.stem
    width, aspect = SHAPE.get(slug.split("-", 1)[0], SHAPE_DEFAULT)

    # Some cameras store the pixels sideways and record the turn in an EXIF tag, which the
    # WebP copy would not carry, so the turn is applied here.
    im = ImageOps.exif_transpose(Image.open(path))
    if im.mode != "RGB":
        im = im.convert("RGB")

    w, h = im.size
    keep = min(h, int(round(w / aspect)))
    if keep < h:
        top = int(round((h - keep) * FOCUS.get(slug, 0.5)))
        im = im.crop((0, top, w, top + keep))

    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)

    im = im.point(shoulder() * 3)

    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f"{slug}.webp"
    im.save(dest, "WEBP", quality=QUALITY, method=6)
    return dest, dest.stat().st_size


def main() -> None:
    originals = sorted(p for p in SRC.iterdir()
                       if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    if not originals:
        sys.exit(f"no photographs in {SRC.relative_to(ROOT)}")

    total = 0
    for path in originals:
        dest, size = prepare(path)
        total += size
        print(f"  {dest.name:42s} {size/1024:6.1f} KB")
    print(f"  {len(originals)} photographs{'':27s} {total/1024:6.1f} KB total")


if __name__ == "__main__":
    main()
