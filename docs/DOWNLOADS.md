# One-time source downloads (the file-based connectors)

Four sources are download-then-ingest (no clean live API), so they stay empty until you
drop their source file in the right folder. This is your collection step. After placing
the files, run:

```
python scripts/run_all.py --countries sea --verbose
```

General notes:
- Only **UNAIDS filenames matter** (the file stem selects the indicator). For the other
  three, just drop the file in the folder as-is (any name).
- Every connector **auto-detects its columns and logs what it picked** — if a column
  isn't found, the run log tells us the exact one-line tweak. So exact column names and
  minor format changes are fine.
- I can't create accounts or accept site terms for you (a couple of these may prompt a
  free registration) — that part is yours.

---

## 1. UNAIDS AIDSinfo → `data/raw/unaids/`   (the backbone)

1. Open <https://aidsinfo.unaids.org/>.
2. Pick an indicator from the indicator selector, set geography (your countries or All)
   and the year range.
3. Export the data table as **CSV** (download/export icon on the data view). A wide
   layout — countries × years — is fine; the connector also handles long.
4. Save **one file per indicator, named by canonical id** (the stem is the mapping key):

   | Save as | AIDSinfo indicator |
   |---|---|
   | `plhiv.csv` | People living with HIV — all ages |
   | `new_infections.csv` | New HIV infections — all ages |
   | `aids_deaths.csv` | AIDS-related deaths |
   | `know_status_pct.csv` | % of PLHIV who know their status |
   | `art_coverage_pct.csv` | % of PLHIV on ART |
   | `viral_suppression_pct.csv` | % (on ART) virally suppressed |
   | `domestic_hiv_spend.csv` | Domestic public HIV spending (Finance) |

   (Add/rename to match `FILE_INDICATOR_MAP` in `unaids_aidsinfo.py` — extend it freely.)

## 2. PEPFAR Panorama → `data/raw/pepfar/`   (programme baseline; archival)

1. Open <https://data.pepfar.gov/datasets>.
2. Under the **MER** structured datasets, download an **Operating-Unit-level** MER dataset
   for the fiscal years you want (e.g. "MER Structured Dataset OU x IM").
   *May require a free PEPFAR Panorama account — you'd register.*
3. **Unzip** it → a large tab-delimited **`.txt`**.
4. Move the `.txt` into `data/raw/pepfar/`.

   Keeps `TX_CURR` → `on_art_count` and `HTS_TST_POS` → `new_diagnoses` (Total Numerator).
   Tagged *PEPFAR footprint, not national totals*.

## 3. ForeignAssistance.gov → `data/raw/foreign_assistance/`   (US self-reported)

1. Open <https://foreignassistance.gov/data>.
2. Download the **Complete Data Set** (full disaggregated data) as **CSV** (large file).
3. Save into `data/raw/foreign_assistance/`.

   Filters HIV category + **Disbursements**, by country-year → `external_hiv_oda_us`
   (triangulates the OECD-CRS US series).

- **Also emits the same money split by managing agency** — `external_hiv_oda_us_usaid`,
  `_cdc`, `_state`, `_other_agency` — from the file already downloaded. Nothing extra to
  fetch. The split is on *managing* agency (who spent it), not *funding* agency (whose
  appropriation it came from), because PEPFAR is appropriated to State and a funding-agency
  split separates nothing. The four series sum to the country total, so take one level or the
  other and never both.
- **State is its own series and matters.** State-managed HIV disbursements go from about 6m
  USD in FY2024 to 271m in FY2025, because the Bureau of Global Health Security and Diplomacy
  took over USAID's global health programmes. Reading the USAID fall without it overstates the
  cut in every large PEPFAR country.
- **The last fiscal year in the file is a part year.** The download is a snapshot taken during
  a running US fiscal year and says nothing about being incomplete, so the connector infers it
  and flags every row of that year with `partial_fiscal_year`. In the current file that is
  FY2026, at 18% of a normal year. The default `--end 2025` keeps it out of the panel anyway.
- The file is 3.7 GB and 56 columns; the connector reads the nine it needs and takes about
  20 seconds.

## 4. Global Fund — NO download needed (comes from OECD automatically)

The Global Fund publishes no country-year panel (only per-country manual profiles), and
its OData API doesn't serve filtered disbursements. So the Global Fund is pulled
programmatically as a **donor series inside the OECD connector** (donor code `9OTH012`)
→ `global_fund_hiv_disbursements`. Nothing to download; it appears whenever the OECD
connector runs. (`data/raw/global_fund/` is now unused.)

## 5. Cambodia NCHADS CoPCT — NO download needed (auto-discovered), optional vetting

The Cambodia country connector (`kh_nchads_copct`) **auto-discovers** the quarterly "Boosted
CoPCT" PDFs from the NCHADS quarterly-report category pages and caches them into
`data/raw/nchads/` on its own — so, like Thailand's live API, you just run the pipeline.

- **To vet or run offline:** drop any CoPCT PDFs into `data/raw/nchads/` yourself and they
  take precedence (the connector reads local files first, then discovers). Source pages:
  <https://www.nchads.gov.kh/category/quarterly-report-2025-en/> (swap the year).
- **Only the born-digital *CoPCT* report is used** — NCHADS's *ART* and *VCCT* quarterly
  reports are scanned images and are deliberately ignored (we don't OCR).
- Emits a **key-population** cascade (sex workers / MSM / transgender): reached → tested →
  HIV-positive → newly on ART, quarterly flows summed to annual. Tagged national programme
  figures (the report's printed TOTAL row, integrity-checked against the zone subtotals).

## 6. South Africa Thembisa — NO download needed (auto-discovered), optional vetting

The South Africa country connector (`za_thembisa`) reads the Thembisa model's provincial
output workbook. It finds the newest version on <https://www.thembisa.org/downloads> by
itself, follows the download interstitial to the actual file, and caches it into
`data/raw/thembisa/`. No registration, no terms to accept, so just run the pipeline.

- **To vet or run offline:** drop a `ProvOutput*.xlsx` into `data/raw/thembisa/` yourself and
  it takes precedence (local file first, then discovery). The current cache is
  `ProvOutputs5_0.xlsx`, v5.0.
- **The workbook is the *provincial* outputs file**, not the age-specific one. It carries the
  national sheet plus nine provinces, each indicator as a Mean / 95% LL / 95% UL triple.
- **Only years the model fits to data are ingested.** Thembisa publishes to 2035 and marks
  extrapolated years in grey font; the connector reads the font colour and drops them. The
  cutoff is per indicator, so there is no year to configure.
- Tagged `modelled_estimate`, because Thembisa is a model and not a facility reporting system.
  Provincial rows do not sum to the national row by design — take one level or the other.

---

After any/all of these are in place, re-run `run_all`. Each source that has its file will
switch from `0 rows` to real data, and the run summary + `data/panel/hiv_panel.validation.txt`
will show the result.
