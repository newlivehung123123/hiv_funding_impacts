# Policy exposure — America First bilateral global-health MOUs

`data/panel/mou_agreements.csv`, produced by `hivimpact/mou_tracker.py`, joined to
`data/panel/hiv_panel.csv` on `country_iso3`.

## Why this table exists

Adrian's brief contained two questions. The first, whether country-level programme and finance
data can be obtained at source, is answered by the panel and the Phase-2 feasibility log. The
second concerned **bilateral-arrangement opacity**: the America First Global Health Strategy
replaced multilateral USAID flows with country-to-country Memoranda of Understanding, which
makes funding harder to trace.

Every other component of this repository measures *consequences* (funding flows, treatment
counts, stockouts, service disruption). This table captures the *instrument* presumed to cause
them. In design terms the panel supplies outcome and mediator variables; this supplies the
exposure.

## Why it is a separate file and not panel rows

An MOU is an event with a precise signing date, a textual scope, and **committed** and not
disbursed amounts. The panel's grain is one row per country-indicator-year measurement.
Inserting an MOU into that structure would degrade the signing date to a calendar year, which
destroys the timing precision that gives the variable its analytical value, and would mix a
policy instrument into a measurement table. The conventional arrangement is an outcome panel
joined to a treatment table, which is what this implements.

## Source and provenance

The KFF tracker *America First MOU Bilateral Global Health Agreements* renders through
Datawrapper, which exposes the chart's underlying data at
`https://datawrapper.dwcdn.net/<chart>/<version>/dataset.csv`.

Two handling requirements follow. First, the version must be **discovered, never hardcoded**:
the unversioned chart URL returns a redirect stub naming the live version, and the version must
be taken from a regular-expression capture group because the chart identifier itself contains a
digit. Second, KFF is a **secondary** source, so every row carries `source_url`, the primary
State Department release that the tracker links, extracted from the anchor markup. All 34 rows
currently resolve to a primary URL.

The upstream format has changed between versions (version 1 was comma-separated, the current
version is tab-separated, and a decorative header sits above the real one), so the parser
detects the delimiter and locates the header instead of assuming either.

## Columns

| Column | Notes |
|---|---|
| `country_iso3`, `country_name` | ISO3 is the join key; the name is canonicalised from it |
| `country_name_as_published` | Retains footnote markers, for example `Philippines***` |
| `agreement_date`, `agreement_date_raw` | ISO date plus the source text. Where the source gives two candidate dates, the earlier is taken and the raw text retained |
| `total_funding_usd`, `us_funding_usd`, `country_coinvestment_usd`, `coinvestment_share_pct` | Committed over the 2026–2030 period. Undisclosed values are null, never zero |
| `programme_areas`, `covers_hiv` | Scope as published, and whether HIV falls within it |
| `source_url`, `tracker_url`, `retrieved_at` | Primary State Department release, secondary KFF tracker, retrieval date |

## Current content

Thirty-four signatories, of which twenty-nine include HIV. Signing dates run from 4 December
2025 to 1 July 2026 and are **staggered**, which supports a dated treatment with an untreated
comparison group.

Two signatories fall within this project's country set, and both are countries for which a
country-level to-source connector already exists with quarterly pre-signature baselines:

| Country | Signed | US funding | Co-investment | Scope |
|---|---|---|---|---|
| Cambodia | 2 April 2026 | $30.8m | $5.3m (15%) | HIV/AIDS; TB; Malaria; GHS |
| Philippines | 7 April 2026 | not disclosed | not disclosed | HIV/AIDS; TB; GHS |

Cambodia is the stronger case. Its key-population cascade is observed quarterly through Q1
2026, and the agreement was signed on 2 April 2026, the first day of Q2. The pre-signature
baseline is therefore complete and measured from the national programme itself.

The remaining seven Southeast Asian countries in the panel (Vietnam, Thailand, Indonesia, Laos,
Myanmar, Malaysia, Timor-Leste) had not signed as at the retrieval date and serve as the
untreated comparison group.

## Caveat

Committed amounts are not disbursements. They should be triangulated against
`external_hiv_oda_us` (ForeignAssistance.gov, current to 2026) and are not treated as realised
funding.
