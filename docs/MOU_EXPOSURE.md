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
State Department release that the tracker links, extracted from the anchor markup. All 35 rows
currently resolve to a primary URL.

The upstream format has changed between versions (version 1 was comma-separated, the current
version is tab-separated, and a decorative header sits above the real one), so the parser
detects the delimiter and locates the header instead of assuming either. Datawrapper serves
the datasets as `application/octet-stream` with no character set, so the tracker decodes every
dataset as UTF-8 and never lets the HTTP library guess. On 5 October 2026 a guessed encoding
turned "Côte d'Ivoire" into "CÃ´te d'Ivoire" in the programme-areas file, and the row failed to
map to ISO3.

The programme areas come from a second KFF chart. Versions 1 to 50 of the agreements chart
(`Kj5gQ`) carry a `Program Areas` column, and versions 51 and 52 do not. KFF now publishes the
programme areas in a chart titled *USG Global Health MOU Program Areas by Country* (`IsvxV`),
with one Y or N column for each of HIV/AIDS, TB, Malaria, Polio, MCH (maternal and child
health) and GHS (global health security). The tracker reads the live version of `IsvxV` the
same way, by discovery and never by a hardcoded number, and joins the programme areas to the
agreements on ISO3. The programme areas are KFF's own coding, assigned by keyword searches of
press releases and agreement texts, and KFF notes that the coding may not capture the full
scope of an agreement. Every row records the dataset version the programme areas came from in
`programme_areas_url`. No programme area is typed in by hand.

## Columns

| Column | Notes |
|---|---|
| `country_iso3`, `country_name` | ISO3 is the join key; the name is canonicalised from it |
| `country_name_as_published` | Retains footnote markers, for example `Philippines***` |
| `agreement_date`, `agreement_date_raw` | ISO date plus the source text. Where the source gives two candidate dates, the earlier is taken and the raw text retained |
| `total_funding_usd`, `us_funding_usd`, `country_coinvestment_usd`, `coinvestment_share_pct` | Committed over the period of the agreement, which KFF gives as five years (2026 to 2030) for most agreements and three years for the agreements with Bolivia, Botswana, Panama and South Sudan. Undisclosed values are null, never zero |
| `programme_areas`, `covers_hiv` | Scope as KFF codes the scope, read from the programme-areas chart, and whether HIV falls within the scope. `covers_hiv` is True only where KFF publishes Y under HIV/AIDS and False only where KFF publishes N. Both columns are empty where KFF states no programme areas for an agreement, and an empty `covers_hiv` means unknown, never no. The file written on 3 October 2026 read version 52 of the agreements chart alone and is empty in both columns on every row |
| `programme_areas_url` | The Datawrapper dataset, with the version number, that the programme areas of the row came from |
| `source_url`, `tracker_url`, `retrieved_at` | Primary State Department release, secondary KFF tracker, retrieval date |

## Current content

Thirty-five signatories at the retrieval of 5 October 2026, every one with a primary State
Department URL. Signing dates run from 4 December 2025 to 11 September 2026 and are
**staggered**, which supports a dated treatment with an untreated comparison group. Version 36
of the programme-areas chart (data as of 11 September 2026) lists all 35 signatories, and HIV
falls within the programme areas of 32 agreements. The three agreements without HIV are the
agreements with Guatemala, Madagascar and Niger. Version 50 of the agreements chart, the last
version with a `Program Areas` column, listed 34 signatories with HIV in 31 and gave the same
coding for every country the two charts share. Vietnam signed after version 50.

Signatories by region of this project, at the retrieval of 5 October 2026:

| Region | Countries | Signatories |
|---|---|---|
| Eastern and Southern Africa (built) | 22 | 14 |
| Western and Central Africa (built) | 24 | 10 |
| Southeast Asia (built) | 9 | 3 (Cambodia, Philippines, Vietnam) |
| Latin America and the Caribbean | 23 | 6 (Panama, Dominican Republic, Guatemala, El Salvador, Honduras, Bolivia) |
| East Asia and the Pacific | 13 | 1 (Papua New Guinea) |
| Eastern Europe and Central Asia | 17 | 1 (Tajikistan) |
| South Asia | 8 | 0 |
| Middle East and North Africa | 14 | 0 |

Cambodia is the stronger Southeast Asian case. The Cambodian key-population cascade is observed
quarterly through Q1 2026, and the Cambodian agreement was signed on 2 April 2026, the first day
of Q2. The pre-signature baseline is therefore complete and measured from the national
programme itself.

Vietnam signed on 11 September 2026, so the untreated Southeast Asian comparison group is now
the six countries without an agreement at the retrieval date (Thailand, Indonesia, Laos,
Myanmar, Malaysia, Timor-Leste).

## Caveat

Committed amounts are not disbursements. They should be triangulated against
`external_hiv_oda_us` (ForeignAssistance.gov, current to 2026) and are not treated as realised
funding.
