# Segment photographs — originals

The full-size downloads, one per segment on the site, named after the slug the build
looks the file up by. They live here instead of under `site/static` so that only the
small copies are published.

`scripts/make_photos.py` reads this directory and writes `site/static/img/photos/`,
which is what the site serves. Replace a file here and run the script again to update
it; the build picks the new copy up on its next run.

The prefix on the slug says what the photograph is for, and decides how the copy is
cropped and how large it is worth keeping:

| prefix     | segment                                                   | count |
|------------|-----------------------------------------------------------|-------|
| `region-`  | the eight regions on the home page rack                    | 8     |
| `domain-`  | the six data categories on the home page                   | 6     |
| `country-` | the nine Southeast Asian countries, by ISO3                | 9     |
| `rel-`     | the three source relationships on the reconciliation page  | 3     |
| `panel-`   | the six files on the downloads page                        | 6     |

Keep the originals. They are not regenerable, and the crop, size and tone curve applied
to the published copies are all lossy.

The source and licence of each photograph belong in the table in
`site/static/img/photos/README.md`.
