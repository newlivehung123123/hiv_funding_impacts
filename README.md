# HIV Funding Impacts

A contamination-safe data pipeline tracking how global-health funding cuts (PEPFAR /
USAID / UNAIDS, under the *America First Global Health Strategy*) affect HIV services
across LMICs. Joint work with Adrian Smith (Oxford Population Health).

This repository is **Phase 1**: the aggregator layer.

## Principles (non-negotiable)

1. **Reliability & validity first.** Structured/authoritative feeds only. We never
   parse prose or PDFs for numbers. An honest *"not published in structured form"*
   beats a fabricated figure.
2. **No mass-LLM extraction** anywhere in the pipeline. Phase 1 needs no LLM at all —
   every source here is machine-readable.
3. **Provenance on every row** — `source_url`, `source_type`, `retrieved_at`.
4. **Triangulation, not blind trust.** Country/source data is primary; aggregators are
   a cross-check. Discrepancies are findings, not just errors.
5. **Uncertainty is a first-class field.** Every value can carry `value_lower` /
   `value_upper`. (The amfAR *Unmeasurable and Unaccountable* report shows the HIV
   "95-95-95" outcome metrics carry wide confidence intervals — a point value alone
   would misrepresent them.)

## Phases

- **Phase 1** — aggregator connectors (UNAIDS AIDSinfo, WHO GHO, OECD CRS, World Bank).
  Few, structured, near-global → the reliable panel skeleton + triangulation baseline.
  - **Phase 1.1** — filter/present the **Southeast Asia** slice first (for Adrian). Not
    a separate build: the connectors are global; `--countries sea` is just the filter.
- **Phase 2** — SEA country-level "to source" connectors (the feasibility test).
  Log: [`docs/PHASE2_FEASIBILITY.md`](docs/PHASE2_FEASIBILITY.md).
- **Phase 3** — extend region by region to all LMICs. Africa first, since that is where the
  funding cut lands hardest. Log: [`docs/PHASE3_FEASIBILITY_AFRICA.md`](docs/PHASE3_FEASIBILITY_AFRICA.md).
- **Phase 4** — West and Central Africa, the region Phase 3 probed but did not research. Half its
  countries have no PEPFAR data at all, and the sources that reach them are regional and not
  national. Log: [`docs/PHASE4_FEASIBILITY_WCA.md`](docs/PHASE4_FEASIBILITY_WCA.md).
  The methods note built on all three regions — what is reachable, and the layer above the country
  that carries the funder as a column — is [`docs/ACCESS_LADDER.md`](docs/ACCESS_LADDER.md).
- **Phase 5**, Latin America and the Caribbean. The log is
  [`docs/PHASE5_FEASIBILITY_LAC.md`](docs/PHASE5_FEASIBILITY_LAC.md). The assessment closed on
  28 October 2026 under rulings R72 to R74 of
  [`research/rulings_2026-10-15.md`](research/rulings_2026-10-15.md).
- **Phase 6**, South Asia. The working notes are in [`research/phase6_sas`](research/phase6_sas).
  The region page went live on 27 October 2026.
- **Phase 7**, East Asia and the Pacific. The working notes are in
  [`research/phase7_eap`](research/phase7_eap). The region page went live on 27 October 2026.
- **Phase 8**, Eastern Europe and Central Asia. The working notes are in
  [`research/phase8_eeca`](research/phase8_eeca). The region page went live on 27 October 2026.
- **Phase 9**, Middle East and North Africa. The log is
  [`docs/PHASE9_FEASIBILITY_MENA.md`](docs/PHASE9_FEASIBILITY_MENA.md). The assessment closed on
  28 October 2026 under rulings R75 to R77 of
  [`research/rulings_2026-10-15.md`](research/rulings_2026-10-15.md).

The site footer lists the phases in number order, with Southeast Asia under Phase 2, the phase
of the first country-level connectors, and Phase 1 as the aggregator sources for every region.

## Install

```bash
cd "15. HIV Funding Impacts"
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Run the collection  — *you run this; Claude writes the code but does not execute collection*

```bash
# 1. (UNAIDS only) export CSVs from https://aidsinfo.unaids.org/ into data/raw/unaids/,
#    one indicator per file, named by canonical id, e.g. plhiv.csv, new_infections.csv
#    (see hivimpact/connectors/unaids_aidsinfo.py for the naming convention)

# 2. (optional) dump the WHO HIV indicator catalogue to lock exact codes
python scripts/list_who_hiv_indicators.py

# 3. build the Southeast Asia slice (Phase 1.1)
python scripts/run_all.py --countries sea --start 2000 --end 2025 --verbose

# or the full global panel
python scripts/run_all.py --countries all
```

Output: `data/panel/hiv_panel.{csv,parquet,sqlite}` + a `.validation.txt` report.

## Confirm-on-first-run (honest unknowns)

These are the few places that need a real run to lock down. The connectors are built to
make confirmation easy (they log what they used) instead of hiding a guessed constant:

- **WHO GHO** — the connector auto-resolves HIV indicator codes by name from the live
  catalogue and logs each resolution. Review `docs/who_hiv_indicators.csv` and lock
  exact `{canonical: who_code}` codes.
- **UNAIDS AIDSinfo** — CSV export column layouts vary a little by indicator. If a file
  doesn't parse, adjust `FILE_INDICATOR_MAP` / column detection in the connector.
- **OECD CRS** — confirm the dataflow id/version, the recipient code scheme (ISO3 vs
  numeric), and the gross-disbursements measure label (all logged on first run).

## Publish the site

The site is static. `build_site.py` renders it into `site/dist`, and `deploy.py` copies that
folder to the web host over FTP with TLS, sending every file and removing anything on the
server that is no longer part of the build.

```bash
python3 scripts/build_site.py && python3 scripts/deploy.py
```

The FTP password is read from the macOS keychain, so it is stored once by hand and is never
written into this repository. Set it in hPanel first (Files, FTP Accounts, Change FTP password —
not the Hostinger account password), then hand it over once:

```bash
python3 scripts/deploy.py --set-password
```

That asks for it once, tries it against the server, and stores it only if the server accepts it.
A password that will not work is reported there and then.

`python3 scripts/deploy.py --check` reads the live site and changes nothing. It confirms that
the CSV files are served as `text/csv`, that the SQLite and Parquet files are served as binary,
that the old `index.html` addresses redirect to the short ones, and that every page returns 200.
The publish step runs the same check when it finishes.

The host answers from several edge servers, each holding its own copy of a file. A copy taken
before the `.htaccess` reached the server goes on calling a `.csv` plain text, so a browser saves
it as `.txt`, and which edge server answers a given reader is chance. The fault therefore appears
in a share of the requests and looks fixed when it is not. Two things guard against it:

- Each line of the check is asked eight times and every answer has to be right. A line reading
  `right 6 of 8 times` is a stale copy, not a passing site.
- The download links on the Data page carry a stamp taken from the contents of the file, so a
  changed file is fetched at an address no edge server has seen. The stamp is not part of the
  saved filename, which comes from the path.

If the check reports a mixed result, flush the edge copies in hPanel under Performance, CDN,
**Flush cache**, then run it again.

Do not publish by uploading a zip through the browser file manager. That route leaves out
`site/dist/.htaccess`, which carries the file types and the redirect, and it does so without
reporting anything: the pages still work, but every download arrives named `.txt`.

## Layout

```
hivimpact/
  schema.py            # PanelRow + SourceType (the one data model)
  connector_base.py    # BaseConnector contract (HTTP hygiene, provenance)
  normalize.py         # country name/code -> ISO3
  writers.py           # panel -> CSV/Parquet/SQLite + validation
  config/
    countries.py       # SEA set + country-set resolver
    indicators.py      # canonical indicator registry
  connectors/
    world_bank.py  who_gho.py  unaids_aidsinfo.py  oecd_crs.py
scripts/
  run_all.py                    # assemble the panel  (you run)
  list_who_hiv_indicators.py    # dump WHO catalogue   (you run)
  build_site.py                 # panel -> the static site in site/dist
  deploy.py                     # site/dist -> the web host, over FTP with TLS
site/
  templates/  static/  charts.py    # the site's source
  dist/                             # the built site, including .htaccess
DESIGN.md              # the living design doc
```

See `DESIGN.md` for the schema, source-type taxonomy, and the reasoning behind each
decision.
