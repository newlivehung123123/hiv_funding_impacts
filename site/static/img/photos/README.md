# Photographs

One photograph sits behind each segment on the site: the eight regions on the home page
rack, the six data categories, the six downloads, the three source relationships on the
reconciliation page, and the nine Southeast Asian countries.

These are the published copies. They are small WebP files written by
`scripts/make_photos.py` from the full-size originals in `assets/photos/`, which are
kept out of `site/static` so they are never served. Replace an original, run the script,
and the build picks the new copy up on its next run.

## How the build finds them

A file is looked up by the slug of the segment it belongs to:

    region-southeast-asia.webp        the rack on the home page
    domain-financing.webp             the data categories
    country-tha.webp                  the country cards, by ISO3
    rel-derived.webp                  the reconciliation cards
    panel-csv.webp                    the downloads

Every backdrop is optional by design. A segment with no file of its own is drawn on
plain metal, so photographs can be added or replaced one at a time without touching the
templates. The lookup is `photo()` in `scripts/build_site.py`.

## How they are prepared

The originals are bright: a white building against a clear sky, a market under lights.
Light text cannot be read over that however the stylesheet is arranged, so the
highlights are rolled off when the copy is written instead of covered up afterwards.
Everything above a threshold is compressed towards a ceiling, which takes the glare out
while leaving the detail and the shadows alone, and it puts every photograph in the same
tonal range so one setting in the stylesheet suits all of them. The thresholds are
`KNEE`, `CEIL` and `FLOOR` at the top of `scripts/make_photos.py`.

On the page each picture is part-desaturated, drawn at low opacity and carries its own
gradient wash, so it gives shape and tone, not detail. That is why the copies are
small: at the size and opacity they are drawn, a larger file buys nothing.

The rack used to draw a Natural Earth map over the photograph as well. The two competed
and the maps came out. `scripts/make_region_art.py` still generates them offline if a
region page ever wants one, where there is room for a map to be looked at and not just
read through.

## Before filing a photograph

Check what the picture actually shows, not what the download was called. One of these
was captioned for the wrong continent, which on a public academic page is a credibility
problem and not a cosmetic one.

## Source and licence

None of these files carry EXIF author or copyright fields, so the record has to be kept
by hand. Fill this in before the site is published.

| file | subject | source | licence | attribution required |
|---|---|---|---|---|
| `region-southeast-asia` | | | | |
| `region-south-asia` | | | | |
| `region-east-asia-and-the-pacific` | | | | |
| `region-eastern-and-southern-africa` | | | | |
| `region-western-and-central-africa` | | | | |
| `region-latin-america-and-the-caribbean` | | | | |
| `region-middle-east-and-north-africa` | | | | |
| `region-eastern-europe-and-central-asia` | | | | |
| `domain-financing` | | | | |
| `domain-cascade` | | | | |
| `domain-epi` | | | | |
| `domain-prevention` | | | | |
| `domain-service_access` | | | | |
| `domain-denominator` | | | | |
| `country-tha` | | | | |
| `country-vnm` | | | | |
| `country-idn` | | | | |
| `country-phl` | | | | |
| `country-mmr` | | | | |
| `country-khm` | | | | |
| `country-lao` | | | | |
| `country-mys` | | | | |
| `country-tls` | | | | |
| `rel-derived` | | | | |
| `rel-subset` | | | | |
| `rel-independent` | | | | |
| `panel-csv` | | | | |
| `panel-parquet` | | | | |
| `panel-sqlite` | | | | |
| `panel-recon-pairs` | | | | |
| `panel-recon-cells` | | | | |
| `panel-mou` | | | | |
