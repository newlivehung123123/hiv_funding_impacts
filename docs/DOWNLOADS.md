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

**Nothing to download. This connector became automatic on 27 September 2026.**

ForeignAssistance.gov answers every non-browser client with HTTP 403 and the header
`cf-mitigated: challenge`, which is why the Complete Data Set used to be fetched by hand.
Every US agency republishes the same transactions as IATI XML on Amazon S3, outside the
challenge, and the IATI Registry gives the address of every file. The connector now discovers
the 21 US government publishers in the registry and downloads their XML into
`data/raw/foreign_assistance/iati/`, cached by ETag so a rerun re-fetches only what moved.
The corpus is **2,723 MB over 2,015 files**, of which USAID is 1,746 MB and State 370 MB. The
first run is slow, and the manifest is now saved after every file fetched, so a run that is
interrupted resumes instead of starting the corpus again. The progress line reports how many
files were fetched and how many came from cache, because a rerun that reports no cache hits at
all means the manifest was not read and the whole corpus is coming down again. The run of 27
September 2026 reported one file fetched and 2,015 served from cache and finished the download
stage in 295 seconds, so a rerun on a warm cache costs about five minutes rather than the hours
the first run takes.

Two defects in the registry's own records are handled at discovery. The Department of Defence
registers one file as a link to the Amazon S3 web console instead of the file, which used to
download 1,158 bytes of console HTML that the parser then rejected. The connector now rewrites a
console link into the address of the object the console displays, and the Defence file reads as
XML. A read-only sweep of all 21 US publishers on 27 September 2026 found that resource to be
the only console link in the corpus, and the activity it holds is not HIV, so the fix removes a
parse failure and moves no figure. The Department of Transportation registers one URL under two
packages, so the connector used to ask for that file twice and never asked for the Ecuador file
at all. The repeat is now dropped, and a publisher that registers two different files under one
filename gets a warning and a second local name for the second file, so neither file is
overwritten in silence. Transportation's Ecuador file is still missing, because the registry
publishes no address for it. The rerun of 27 September 2026 proves both fixes. Discovery reported
2,020 files to read out of 2,041 registered resources, 20 Worldwide files skipped and one
duplicate registration dropped, the download reported one file fetched and 2,014 served from
cache, which with the five unchanged 403 failures accounts for all 2,020 jobs, the parse gave up
on no file as unreadable against one before, and the panel is unchanged at 209,872 rows.

The hand-downloaded file survives as one small committed extract,
`data/raw/foreign_assistance/history_fa_gov.csv`, made once by `scripts/extract_fa_history.py`
from the copy dated 18 July 2026. The extract supplies the years the S3 files cannot: the S3
route reproduces ForeignAssistance.gov's own API exactly for State from FY2012, for Health and
Human Services from FY2012 and for USAID from FY2020, and falls short before those years.
Rebuilding the extract is only necessary if the repository ever loses it, and that is the one
case where the Complete Data Set has to be downloaded from <https://foreignassistance.gov/data>
again.

   Filters HIV (ForeignAssistance.gov's own HIV/AIDS sector name, or DAC purpose code 13040)
   and **Disbursements** only, by country-year → `external_hiv_oda_us`
   (triangulates the OECD-CRS US series).

- **Also emits the same money split by managing agency** — `external_hiv_oda_us_usaid`,
  `_hhs`, `_state`, `_other_agency`. The split is on *managing* agency (who spent it), not
  *funding* agency (whose appropriation it came from), because PEPFAR is appropriated to State
  and a funding-agency split separates nothing. The four series sum to the country total, so
  take one level or the other and never both.
- **`_hhs` replaced `_cdc` on 27 September 2026.** The CSV carried a managing sub-agency column
  and the XML carries none, so the bucket is now the whole department rather than CDC alone.
  CDC is 38.5bn USD of the department's 43.1bn. NIH and HRSA moved out of `_other_agency` and
  into `_hhs` at the same time.
- **State is its own series and matters.** State-managed HIV disbursements go from about 6m
  USD in FY2024 to 271m in FY2025, because the Bureau of Global Health Security and Diplomacy
  took over USAID's global health programmes. Reading the USAID fall without the State series
  overstates the cut in every large PEPFAR country.
- **The State series has a hole at FY2019 and FY2020, and the hole belongs to
  ForeignAssistance.gov.** State-managed HIV disbursements run at 19m to 94m USD a year from
  FY2015 to FY2018, fall to 91,332 USD across the whole world in FY2019, report nothing at all
  in FY2020, and resume at 6.5m in FY2021. The frozen extract of the Complete Data Set shows the
  same shape, one country in FY2019 and no FY2020 row anywhere, so the S3 files reproduce the
  source faithfully and the gap is not a connector fault. The panel's validator flags the gap as
  a fall from 28 reporting countries to one. **Any before-and-after comparison that uses FY2019
  or FY2020 as a State baseline is reading a hole in the source.**
- **The last fiscal year is a part year.** The publishers rewrite these files during a running
  US fiscal year and nothing in them says which year is incomplete, so the connector infers it
  and flags every row of that year with `partial_fiscal_year`. The panel holds the FY2026
  part year, because the runs of 12 October and 29 October 2026 used `--end 2026`. A run at the
  default `--end 2025` drops every FY2026 row, and the first guarded run of 29 October 2026
  stopped before the build when a run at `--end 2025` lost the FY2026 rows.
- **USAID and State publish the same awards twice from FY2025.** The USAID XML file reports
  State's transactions as well as USAID's, and ForeignAssistance.gov reports the USAID figure
  net of the State figure, so the connector subtracts the State country total from the USAID
  country total in a fiscal year where the files show both agencies publishing the same award
  number, and carries the unadjusted USAID figure in `extra`. The subtraction fired on 52
  country-years in the run of 27 September 2026, every one of them FY2025.
- **The subtraction runs whatever the sign of the State figure.** A guard skipping a negative
  State country-year was added and removed on 27 September 2026. A negative State figure looks
  like a year of recoveries rather than an award reported twice, and Papua New Guinea FY2025
  turns a raw USAID figure of minus 7,782 USD into a positive 2,487,146 once State's minus
  2,494,928 is taken away. ForeignAssistance.gov publishes 2,487,154. Skipping the subtraction
  leaves State's money in the USAID series as well as the State series, and Papua New Guinea's
  four agency series then sum to minus 2,403,586 against the API's 91,350. **The panel was
  rebuilt without the guard on 27 September 2026.** The subtraction then fired on 52
  country-years and skipped none, which is the 48 the guard had allowed plus the four the guard
  had blocked, and Indonesia, Nepal, Papua New Guinea and Vietnam now carry the figures the API
  publishes. The count of country-years disagreeing with the frozen history inside a proven
  window fell from 16 to 14 in the same run.
- **Where the S3 files and ForeignAssistance.gov disagree, the row says so.** Fourteen
  country-years inside a proven window differ from the frozen extract by more than 2 per cent,
  and three consecutive USAID years belong to Nicaragua and three consecutive Health and Human
  Services years to Trinidad and Tobago. Every row a disagreement touches now carries
  `history_disagreement` in `extra`. An agency row carries the figure read from the S3 files, the
  extract's figure, the relative gap between the two and a note saying which source is right is
  not settled, and the country total row carries the flag and names the agency buckets behind it.
  **Treat an agency series flagged this way as uncertain for that country and year.**
  `scripts/reconcile_fa_country.py` traces one of these disagreements to a file and an activity,
  reading only the cached XML and writing nothing, with Nigeria as the control and Nicaragua and
  Trinidad and Tobago as the targets.
- **The reconciliation was run on 27 September 2026 and the S3 route is broadly sound.** Of 1,367
  agency-years the connector takes from the S3 files, 1,220 agree with ForeignAssistance.gov to
  within 0.01 per cent and only 14 exceed 2 per cent. Nigeria agrees in 32 of 32 proven
  agency-years. Nicaragua's fault is USAID alone and runs FY2013 to FY2022, closing at FY2023,
  and Trinidad and Tobago's fault is Health and Human Services alone and starts at FY2021. The
  fault is not the HIV test, not the sign of a transaction and not a transaction naming several
  countries, because all three explanations were tested against the cache and ruled out. What
  fits every measurement, without being proved, is that ForeignAssistance.gov attributes to a
  named country money the IATI XML leaves in an unspecified pot, worth up to 1.03 billion dollars
  a year in USAID alone and dropped by both routes. A user should read a flagged agency series as
  likely to understate the country, and should read the country total, which the shortfall also
  moves.
- **Tuvalu's `foreign_assistance` figures were wrong in every panel built before 27 September
  2026, and the defect is fixed.** The panel used to credit Tuvalu with Health and Human Services
  HIV money in nine fiscal years from FY2013 to FY2021, the seven years FY2014 to FY2020 running
  between 5,825,511 and 12,414,715 dollars each, and 65,951,587 dollars in all. Tuvalu receives no
  United States HIV money. Health and Human Services publishes ForeignAssistance.gov's numeric
  country code 798, and the connector's fallback resolved 798 through pycountry as the UN M49
  number for Tuvalu. Moldova was affected in the same way through code 498, and the whole of
  Moldova FY2024 at 45,204 dollars and the whole of Moldova FY2022 at 308 dollars were fabricated,
  while Moldova's other years are correct. The connector no longer resolves a numeric country
  code. The rerun on 27 September 2026 removed Tuvalu's 28 `foreign_assistance` rows and Moldova's
  four rows for FY2022 and FY2024, removed nothing else and changed no surviving value, and the
  panel fell from 209,872 rows to 209,840. Tuvalu remains in the panel on the 163 rows
  `unaids_aidsinfo`, `world_bank`, `who_tme`, `who_gho` and `oecd_crs` supply, and none of those
  rows was ever affected. **Anyone holding a copy of the panel exported before 27 September 2026
  should drop Tuvalu from any analysis of `foreign_assistance` and drop Moldova FY2022 and
  FY2024, or take a fresh export.** Access ladder §9z holds the full account.
- **Sudan's `foreign_assistance` figures were short by 8,903,002 dollars over FY2012 to FY2018 in
  every panel built before 29 October 2026, and the defect is fixed.** Health and Human Services
  publishes Sudan under the code `SF`, which is the FIPS 10-4 code (Federal Information
  Processing Standard 10-4, a retired United States list of country codes) for South Africa and
  which no code list the panel consults reads as Sudan, and the connector dropped 22 HIV
  disbursements as naming no country. Two readings of the cached files place `SF` in Sudan, and
  ruling R78 adds a table to the connector which reads `SF` as Sudan for Health and Human
  Services and the State Department alone. The table stays out of `hivimpact/normalize.py`, and a
  later source using the FIPS code still reads `SF` as South Africa. The rerun of 29 October 2026
  added 13 Sudan rows, raised the Sudan totals of FY2013, FY2014 and FY2015, gave Sudan a total
  in FY2012, FY2016, FY2017 and FY2018, and took `foreign_assistance` from 6,271 rows to 6,284
  and the panel from 456,316 rows to 456,329. The rerun fetched no file. The first guarded run of
  the same day fetched two Department of Defense files from the ForeignAssistance.gov bucket on
  Amazon S3, `iati/dod/iati-activities-Gambia_The.xml` at 33,130 bytes and
  `iati/dod/iati-activities-Western_Hemisphere_Region.xml` at 7,867 bytes, and the rerun read the two
  files along with the 54 Millennium Challenge Corporation files which failed with ConnectionError
  on 12 October 2026. Five files are still refused with HTTP 403. **Anyone holding a copy of the
  panel exported before 29 October 2026 should take a fresh export before analysing Sudan.**
  Ruling R78 and access ladder §9aa hold the full account.

## 4. Global Fund — NO download needed (comes from OECD automatically)

The Global Fund publishes no country-year panel (only per-country manual profiles), and
its OData API doesn't serve filtered disbursements. So the Global Fund is pulled
programmatically as a **donor series inside the OECD connector** (donor code `9OTH012`)
→ `global_fund_hiv_disbursements`. Nothing to download; it appears whenever the OECD
connector runs. (`data/raw/global_fund/` is now unused.)

**The Global Fund now has a second, separate reading in the panel**, taken from the Global Fund's
own IATI publication by the `iati` connector and written under the same indicator with
`source_id = iati`. Section 7 below says what the second reading is for and, more importantly, what
the two readings cannot be used to do.

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

## 7. IATI d-portal — NO download needed, but read the six limitations below before using the rows

The `iati` connector reads the International Aid Transparency Initiative through d-portal's query
service at <https://d-portal.org/q>, so there is nothing to download and nothing to register for.
The connector writes two kinds of row. Bilateral donor rows come from every publisher the connector
identifies as publishing HIV money, and a Global Fund series comes from the Global Fund's own
publication and is written under `global_fund_hiv_disbursements` with `source_id = iati`. The run of
1 October 2026 put 7,062 `iati` rows in the panel across 180 countries and the years 2000 to
2026, of which 2,577 are Global Fund country-years over 128 countries, which is the same row count,
the same country count and the same year span the run of 30 September 2026 produced.

Run the connector with `--countries all --start 2000 --end 2026`. Both arguments have to be typed.
`scripts/run_all.py` defaults `--countries` to `sea` and `--end` to 2025. `iati`,
`foreign_assistance` and `ng_ndr` are among the sources reaching 2026, and a run taking the
default `--countries` or the default `--end` writes a panel which cannot be compared with the
last panel.

**What the download page holds.** The download page holds the panel published on 29 October
2026, 456,329 rows including the `iati` rows. When section 7 was first written, the
download page held the site build of 7 September 2026, 177,594 rows from 18 sources and no
`iati` row, because the `iati` connector was first run on 28 September 2026. Four of
the six limitations below describe a defect in this project's own code, being the first, the third, the fifth and the
sixth, the first, the third and the fifth repaired on 30 September 2026 and the sixth on 1 October
2026, all four before any `iati` row reached the download page.
The second and the fourth describe how the Global Fund and d-portal publish and stand whatever
this project does.

**How the written value is built, and why a stored sector percentage cannot rebuild it.** For every
publisher other than the Global Fund, the written value follows the percentages that publisher
stated in the publisher's own file, because the publisher's file is the record of what the publisher
disbursed and d-portal's split of the same transaction is one reading of that record. For the Global
Fund the written value is the sum of d-portal's sector splits, grouped on the activity identifier
and the transaction ordinal, and the sum is taken because the sector percentages stored against a
Global Fund activity do not reconstruct the published value. Two grants measured while the connector
was being built show the disagreement. On `47045-MWI-C-MOH-2`, a Malawi HIV and tuberculosis grant,
the stored percentages read 1, 4 and 88 while the splits divide the money 7, 4 and 88. On
`47045-UGA-H-MoFPED-2`, a Ugandan HIV grant, the stored percentages read 11 and 88 while the splits
divide the money 1 and 88. Anybody rebuilding a published value by dividing a split by the
percentage stored beside the split will therefore reach the wrong figure on grants of this shape.

No size is claimed here for how far the two readings stand apart across the whole panel, and the
absence is deliberate. No `iati` row carries d-portal's own split beside the written value. The
7,062 rows of the run of 30 September 2026 carry 24 distinct `extra` keys and none of the 24 holds
that figure, so measuring the disagreement across the panel would need a new key and a rerun of the
connector, or a separate read-only probe against the query service. The choice of which reading to
write does not turn on that measurement, so neither was done, and a reader wanting the comparison
has the two grant identifiers above and can query d-portal for each one directly.

**First limitation. The two Global Fund readings are not two independent observations of the same
money.** The OECD Creditor Reporting System reading comes from the Global Fund's return to the OECD
and the IATI reading comes from the Global Fund's own publication, so both readings originate with
the same organisation. Where the two readings agree, the agreement says that this project now reads
the whole of the Global Fund's publication and says nothing about whether the Global Fund's own
figures are right. Do not present the two readings as corroboration by an independent observer, and
do not average the two readings, because averaging two reports of one accounting system produces a
number neither the OECD nor the Global Fund would recognise. Across paired country-years the two
readings now stand at a ratio of 1.009 for 2003 to 2010, 1.073 for 2011 to 2017 and 1.013 for 2018
to 2026, with 91, 76 and 87 per cent of paired country-years agreeing within two per cent.
Until 30 September 2026 the reconciliation layer inferred every relationship from the numbers, and
on the first panel to hold both readings it classified this pair as `independent` and described the
pair as separate measurement systems, which is wrong for the reason just given and overstated both
the count of independent pairs and the count of independent cells. The repair is in the code and
the working panel of 30 September 2026 carries it. The copy of `reconciliation_pairs.csv` on the
download page is the build of 7 September 2026 and names no pair at all for this reading, because
that build predates the connector. The reconciliation layer now
reads a declared relationship where the provenance of two figures is known instead of inferring the
relationship from the numbers, every classified pair carries a `basis` column saying whether the
verdict was declared or inferred, and this pair is declared `derived`. On the panel of 30 September
2026 the declaration moves 2,002 cells out of the independent set, taking the independent-pair cell
count from 31,145 to 29,143 and the material divergences from 8,518 to 8,354, and moves no other
pair's verdict. The 164 cells the reconciliation layer flags as a material divergence
on this pair are places where this project's reading of one Global Fund publication differs from the
Global Fund's return to the OECD, which is worth investigating as a completeness question about this
project's own reading and is not a disagreement between two observers.

**Second limitation. Part of the Global Fund's HIV series is tuberculosis money, and the share
changes in 2018.** The Global Fund makes combined HIV-and-tuberculosis grants, which the connector
takes whole because a combined grant's HIV money cannot be separated from the grant's own
accounting. For country-years after 2018 containing such a grant, about a fifth of the money carries
the OECD purpose code for tuberculosis control, 19.2 per cent of the money against 42.9 per cent
coded to HIV and 37.9 per cent coded to health policy and administrative management. For country-
years after 2018 containing only single-disease HIV grants, 62.7 per cent is coded to HIV, 0.7 per
cent to tuberculosis and 36.6 per cent to health administration, so the health-administration share
is the Global Fund's own coding of HIV money and not money spent on something else. Before 2018 the
Global Fund coded effectively all of this money to HIV, so a jump in the tuberculosis share at 2018
is a change in the Global Fund's coding practice and not a change in what the money bought. Any
comparison spanning 2018 has to say so.

**Third limitation, temporary. Do not use the `extra.sector_*_usd` keys to decompose a Global Fund
row's value.** `extra.sector_13040_usd`, `extra.sector_12110_usd` and `extra.sector_12263_usd`
currently describe every Global Fund grant the connector saw in that country-year, while the row's
value holds HIV and HIV-and-tuberculosis grants whole plus only the HIV-coded share of every other
grant. The three keys therefore exceed the value by 15,801,029,329 USD across the series, and a
reader subtracting the tuberculosis key from the value would remove tuberculosis money the value
never contained. The percentages quoted in the second limitation above are measured on the 480 rows
where every named grant is an HIV or HIV-and-tuberculosis grant, which are the rows where the keys
do describe the value, and are sound. The repair is in the code and the working panel of 30
September 2026 carries it, and the download page holds no `iati` row, so no reader has yet met
either the keys or the defect. In the repaired panel the keys describe the money the row carries and nothing else, a
fourth key `extra.sector_other_usd` holds the part of an HIV or HIV-and-tuberculosis grant declared
under a purpose code none of the three named keys holds, and a fifth key
`extra.seen_not_counted_usd` records the non-HIV part of the grants counted at their HIV share
alone, which stands outside the value and comes to 34,721,419,439 USD across the series. The repair
changed the keys and left every value untouched, which the working panel confirms, because the
total of the Global Fund series is 38,152,946,329.59 USD before the repair and after it.

**One caveat on the repaired keys, measured, not material and repaired in turn.** Each key was
rounded to a cent on its own while the `value` column is published unrounded, so four independently
rounded keys could add to a cent away from the value they decompose. On the working panel of 30
September 2026, rounding both sides to a cent, the four keys add to the value exactly on 2,173 of
the 2,385 rows that carry a value and are one cent out on the other 212, 101 of them a cent low and
111 a cent high. No row is further out than a cent, the 212 differences come to 2.12 USD across a
series of 38,152,946,329.59 USD, and measured against the unrounded value the largest difference
anywhere is 0.0131 USD. The connector's own check compared the unrounded running totals, which is
why the run log reported a largest disagreement of 0.00 USD while the written file carried the cent.

The second repair, written on 30 September 2026, makes `extra.sector_other_usd` the residual on
every row that carries a value, written as the rounded value minus the three rounded named keys, so
the four keys add to the value to the cent. The three keys that name a purpose code are unchanged
and no value moves. `extra.sector_other_usd` is the key that absorbs the rounding because
`extra.sector_other_usd` names no purpose code and none of the percentages quoted above rests on
it. The residual is taken only where the unrounded running totals already agree with the value, so
a genuine disagreement is still reported in the run log and still visible in the file. Until the
`iati` connector is next run the working panel keeps the 212 rows, and a reader decomposing a row
from a panel built before the next run should treat the keys as correct to the cent and not to the
last digit.

**The publisher split carries the same rounding and no residual.** On the bilateral and
multilateral rows, `extra.by_publisher` gives each publisher's share of the value, rounded to a
cent one publisher at a time, so adding the publishers can reach a cent or two either side of the
value. Measured on the working panel of 30 September 2026, 439 of the 4,485 rows carrying a split
and a value do not add up, 291 bilateral and 148 multilateral, the largest difference is 0.02 USD
and the differences come to 4.41 USD. No residual is written there, because every key in that split
names a publisher and moving a cent onto one of them would state that a named publisher disbursed a
cent the publisher did not publish. The value is the figure to quote and the split is a reading of
where the value came from.

**Fourth limitation. One row of d-portal's transaction table is a sector's share of a transaction
and not a transaction.** d-portal serves one row per transaction per sector row the activity
declares, each row carrying the transaction's value times that sector's percentage. Anybody querying
d-portal directly, rather than through this connector, has to add the shares to recover a
transaction, and has to keep both shares where an activity declares the same purpose code twice.
`47045-MWI-C-MOH-2`, a Malawi HIV and tuberculosis grant, declares purpose 12263 at 4 per cent,
12110 at 7 per cent, 12110 again at 1 per cent and 13040 at 88 per cent, so one of its transactions
arrives as four rows of 28,722.43, 50,264.25, 7,180.61 and 631,893.42 USD which add to the
transaction's 718,060.70 USD. Keeping one row per purpose code silently drops the 7 per cent share
of that grant. Access ladder §9ab holds the full account and the checks the connector now runs on
every read.

**Fifth limitation, temporary. Cambodia's bilateral row and Kenya's multilateral row are overstated,
because the same join repeats whole activities and not only transaction rows.** An activity
declaring purpose code 13040 twice arrives from d-portal as two complete activity elements, and this
connector's XML reader currently sums such an activity's transactions once per copy. Across the 85
publishers whose pages are cached, 71 surplus copies were found in three publishers, and the count
of 71 is complete for the publishers whose money this panel writes. One of the three publishers is
`GB-CHC-285776`, an international NGO whose money this panel reads and never writes, so the money
reaching the panel is Australian money in Cambodia and UNICEF money in Kenya. Cambodia's
`external_hiv_bilateral_other` row is overstated by between 10.1 and 33.2 per cent in 2009, 2010,
2011, 2012, 2013, 2015, 2018, 2019 and 2020, and in those years the whole Australian contribution is
exactly twice the truth. Kenya's `external_hiv_multilateral_other` row is overstated by 1.0 per cent
in 2012 and by less in 2014 and 2015, and understated by 0.5 per cent in 2019, because the doubled
transaction in 2019 is a negative expenditure and doubling a negative amount lowers the total. The
surplus is about 3,752,076 USD against the 5,679,863,850 USD the bilateral and multilateral series
held together, which is 0.066 per cent, so no aggregate in this panel moves, and the Cambodian
bilateral series and the Kenyan multilateral series must not be quoted for the years named above
from any panel built before 30 September 2026. The Global Fund series, `oecd_crs` and every other source are
unaffected, because the defect lives in the XML path alone, and no reconciliation figure is
affected, because neither the bilateral series nor the multilateral series is reconciled against
another source. The repair is in the code and the working panel of 30 September 2026 carries it,
and the download page holds no `iati` row, so no reader has yet met the defect. The reader now refuses a
second copy of an activity it has already summed and reports on every run how many copies each
publisher's read refused, and the refusal cannot lose money, because every repeated copy found in
the cache is byte-identical to the copy already counted. In the repaired panel 13 country-years
moved and no others, `external_hiv_bilateral_other` fell by 3,545,561.71 USD across nine Cambodian
years and `external_hiv_multilateral_other` by 206,514.00 USD across four Kenyan years, both to the
penny of what the offline replay predicted, and the row count of each series is unchanged.

**Sixth limitation, repaired. 48 rows of the bilateral series hold money whose currency no publisher
stated, and the currency is inferred.** A transaction value in an IATI file can carry no currency at
all, and the standard lets the currency come from the enclosing activity or from the file instead.
Across the full cached export, 119 of the 374,789 transaction value elements carry a value date and
no currency while no enclosing activity and no file root states a default currency either, so the
currency is absent from the publisher's file and was not missed by the reader. 90 of the 119 pass
the connector's transaction-type and year filters. Until 1 October 2026 the connector wrote such an
amount into the panel as US dollars and put nothing on the row to say so. The connector now reads a
currency down four rungs, being the transaction's own currency, the enclosing activity's
`default-currency`, the file's `default-currency` and then the one currency the publisher states
across the whole file, and refuses the amount where no rung answers. In the panel of 1 October 2026,
48 rows carry a `currency_assumed` key naming the publisher, the inferred currency, the dollars
resting on the inference and the number of the publisher's own transactions the inference rests on.
Every one of the 48 names euros, 35 of the 48 rest on the Ministry for Foreign Affairs of Finland
(`FI-3`), whose cached file states euros on 68 transaction values and no second currency anywhere,
and 13 rest on Irish Aid (`XM-DAC-21-1`), whose file states euros on 217 values and no second
currency anywhere. The 48 rows hold 276,244,253.05 USD between them and 17,798,589.64 USD of that
total rests on the inference, which is 6.4 per cent. The inference decides most of what one
publisher contributes, Finland holding 8,400,141.68 USD in the panel of which 5,872,764.29 USD or
69.9 per cent rests on the inference, against Irish Aid's 34,887,224.16 USD of which 11,925,825.35
USD or 34.2 per cent does. Anybody quoting Finland's contribution should say that the currency is
this project's reading of Finland's own file and not a currency Finland stated on those
transactions. A reader who declines the inference can drop the money by reading
`extra.currency_assumed` off the row, which names the dollars resting on the inference for each
publisher separately, and a note beside the key states the inference in words. The row carries no
exchange rate, so the figure the panel held before the repair cannot be rebuilt from the row alone.
The 48 rows held 272,075,448.89 USD before the repair, of which 13,629,785.48 USD was the same
money written as dollars one for one, and the euro conversion is the whole of the difference. Two
further defects in the same connector were found on the day this limitation was written and both
were repaired the same day. A country-year the Global Fund reached by reimbursement alone used to
leave the panel with no row at all, and the connector now writes the country-year with no value, a
stated reason and the boolean key `only_reimbursements_seen`. The panel carries those rows from the
run of 1 October 2026, which added 54 of them over 33 countries from 2007 to 2025 and raised the
Global Fund series from 2,577 rows to 2,631. A reader counting Global Fund country-years should
know that 54 of the 2,631 are country-years in which every transaction the Global Fund reported was
a reimbursement, which is money returning to the Global Fund and not a disbursement, and that the
boolean key selects or excludes them without matching words inside the reason. A
publisher's reimbursement used to be summed in whatever currency the publisher wrote and logged as
US dollars, and the connector now accumulates such a reimbursement under the currency the file
states and logs one figure per currency. Neither repair changes a figure in the panel, the first
because every row the repair adds carries no value and the second because a publisher's
reimbursement reaches no row at all, and access ladder §9x holds both with the measurement on the
row.

---

After any/all of these are in place, re-run `run_all`. Each source that has its file will
switch from `0 rows` to real data, and the run summary + `data/panel/hiv_panel.validation.txt`
will show the result.
