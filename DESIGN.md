# Design (living document)

This is the "load-bearing walls" spec — the parts expensive to change later, locked on
paper, while connectors are built iteratively against real data. Revise as the data
teaches us (coverage, resolution, what's actually available at source can only be
learned by touching the sources).

## 1. The panel (data model)

Long format, **one row per `(country, indicator, population_group, sex, age_group, year, source)`**
(section 4 of Adrian's indicator document, extended). Columns — see `hivimpact/schema.py`:

| field | purpose |
|---|---|
| `country_iso3`, `country_name` | ISO3 is the join key |
| `indicator_id` | canonical id (see `config/indicators.py`) |
| `population_group`, `sex`, `age_group` | stratification; `population_group` carries key populations (§2) |
| `year`, `value` | `value` may be `None` (source reported nothing) — kept, not dropped |
| `value_lower`, `value_upper` | **uncertainty bounds** — first-class, not optional |
| `unit`, `numerator`, `denominator` | keep num/denom so coverage stays interpretable after cuts |
| `source_id`, `source_type`, `source_url`, `source_indicator_code`, `retrieved_at` | provenance on every row |
| `extra` | JSON blob for source-specific provenance |

## 2. Source-type taxonomy (§4 of the document)

`modelled_estimate` · `routine_programme_record` · `survey` · `expenditure_account` ·
`community_led_monitoring`.

Triangulation is **source-type aware**: a `routine_programme` count diverging from a
`modelled_estimate` means something different from two modelled estimates disagreeing.
Some agreement is *circular* (the aggregator estimate is modelled from the country data),
which is exactly why we store the type, not just the number.

## 3. Connector contract

Every source implements `BaseConnector.fetch(countries, start_year, end_year) -> Iterator[PanelRow]`
and must:
- read only structured/authoritative data (API, SDMX, or official CSV/XLS export);
- **never** interpret prose or parse a PDF for a number;
- **never** fabricate/impute a value for a gap — yield nothing, so the absence is visible;
- stamp provenance via `make_row(...)`.

## 4. Phase-1 sources

| source | access method (confirmed) | role | source_type |
|---|---|---|---|
| World Bank | JSON API `api.worldbank.org/v2` | denominators (population) + HIV prevalence* | modelled_estimate |
| WHO GHO | OData `ghoapi.azureedge.net/api` | HIV epi + cascade estimates (carry Low/High) | modelled_estimate |
| UNAIDS AIDSinfo | official CSV/XLS export (no clean API) | epi, cascade, finance, key populations | mixed |
| OECD CRS | SDMX `sdmx.oecd.org/public/rest`, purpose 13040 | external HIV financing (total + US) | expenditure_account |

\* World Bank HIV series are UNAIDS-derived → a triangulation *duplicate*, not an
independent check. Tagged as such; never treat as a cross-check on UNAIDS.

## 5. Southeast Asia set (Phase 1.1)

THA, VNM, IDN, PHL, MMR, KHM, LAO, MYS, PNG, TLS (LMICs; Singapore/Brunei excluded).
Thailand first — strongest surveillance, best triangulation test, home base. Adjust in
`config/countries.py`.

## 6. What this pipeline can and cannot do (from Adrian's 3 concerns + the amfAR report)

Adrian's concerns — (a) switchover to unreliable metrics, (b) absence of population
stratification, (c) lack of public reporting — are **all valid** and split into:

- **Engineering CAN**: ingest heterogeneous/historical structured sources; preserve
  still-public PEPFAR/DATIM historical data (time-sensitive — build early); structure
  the *gaps* (data-sufficiency framework); compute metric-coherence checks; track
  publication status as data.
- **Engineering CANNOT**: make an incoherent metric coherent; impute missing
  key-population stratification (= contamination); connect to unpublished/confidential
  data.

So the pipeline's job is to **measure and expose** these problems, not solve them — an
automated, all-country version of amfAR's manual 7-country analysis: anchor on the
stable historical MER/95-95-95 baseline, ingest the degraded new data, and surface the
divergence as findings. Honest scope consequence: going forward this may be more a
**transparency/accountability watchdog** than a live service-outcome measurement,
because the source is going dark.

## 7. Open items / next

- [ ] Lock exact WHO GHO indicator codes (run the catalogue dump).
- [ ] Confirm one real UNAIDS AIDSinfo export shape; extend `FILE_INDICATOR_MAP`.
- [ ] Confirm OECD CRS dataflow/version, recipient code scheme, disbursements measure.
- [ ] Add key-population indicators (UNAIDS GAM 1.3A–D families) as `population_group` rows.
- [ ] Add historical **PEPFAR MER / DATIM** connector (baseline + archival urgency).
- [ ] Reconciliation layer: country-vs-aggregator, source-type-aware, materiality-gated,
      discrepancy-as-finding.
- [ ] Data-sufficiency threshold: which country×indicator×year cells qualify for display.
