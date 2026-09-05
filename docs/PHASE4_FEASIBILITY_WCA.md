# Phase 4 — "to source" feasibility log (West and Central Africa)

The Phase 3 log ended by naming its own gap: *"francophone national programmes were probed
thinly and deserve the per-country desk research that Southeast Asia got before anything is
claimed about them"* ([`PHASE3_FEASIBILITY_AFRICA.md`](PHASE3_FEASIBILITY_AFRICA.md) §3). This
log is that research. It rests on per-country desk work, the Phase 2 method — each national
system identified by name, each access route tried, each candidate put to the Malaysia test —
and not on the mechanical endpoint probe that produced the Phase 3 table.

> **Read [round two](#round-two--a-second-pass-and-what-it-overturns) at the end of this log
> before acting on anything above it.** Everything down to "What this changes" is the first
> pass, kept as written so the record shows what was believed when. A second pass on 2026-08-15
> overturned two of its conclusions — that Cameroon is the region's only country-side candidate,
> and that seven countries need no individual probe — and opened five source classes the first
> pass never looked at, including the one that turned out to carry the region's domestic money.

The region matters more than its share of attention so far. Twenty-four countries, 5,031,800
people living with HIV in the panel's latest year, and **half of them have no PEPFAR data at
all**. Nigeria, DR Congo, Cameroon and Côte d'Ivoire carry 70% of the regional burden between
them; the other 632,800 people live in the twelve countries where the donor-side layer that
rescued Eastern and Southern Africa does not exist.

**The headline finding is that the region's gap is mostly filled from above, not from below.** No
national programme *database* in West or Central Africa was found open, which is the outcome the
access ladder predicted and the fourth region in a row to produce it. One national *report* is
open and additive, Cameroon's, and it is the region's only country-side connector candidate.
[**Overturned by round two** — nine countries publish one, and DR Congo publishes part of one.]
What carries the rest are two *regional* sources that turned out to be open, structured and
additive, and that between them reach further into this region than any set of national
connectors would have:

| Layer | Source | Access | WCA coverage |
|---|---|---|---|
| Sub-national estimates | **UNAIDS Naomi viewer** — undocumented public JSON API | **Grade 1**, no login, uncertainty bounds on every value | **15 of 24 countries**, including 7 of the 12 with no PEPFAR |
| Programme results and money | **Global Fund Data Explorer** — public JSON API | **Grade 1**, no login, annual series 2017–2024 | **22 of 24 countries**; an ART series for 10 of the 12 with no PEPFAR |
| Survey measurement | **DHS Program** API (already connected) | **Grade 1**, sub-national breakdown available and not yet used | **18 of 24** have a survey with HIV testing |
| Population survey | **PHIA** data manager | Grade 3, registration-gated request | CIPHIA and CAMPHIA only |

Both regional APIs were found the same way Thailand's Data Mart was: by watching what the public
dashboard asks its own backend for. Neither is documented as an API by its publisher.

---

## The country side, country by country

| Country | National source | Access | Status |
|---|---|---|---|
| **Nigeria** | National Data Repository (`ndr.phis3project.org.ng`) · NACA HIV & AIDS Data Ecosystem · NAIIS 2018 | NDR login wall (Phase 3); the Data Ecosystem has no public address; NACA's stated policy is formal data request | ⛔ **Gated**, and gated by policy as well as by login |
| **DR Congo** | VIH DATAPRO (`vihdatapro.app`, PNMLS) · PNMLS library · PNLS | Database behind a registration wall; library open but its HIV content is the GAM submission | ⛔ **Gated**; one additive open item (EDS-RDC III 2023–2024) |
| **Cameroon** | CNLS (`cnls.cm`) annual reports · MINSANTE | Open born-digital report PDFs, 2024 the most recent, English and French, no login | ✅ **Grade 2, passes the additive test** — the region's one connector candidate |
| **Côte d'Ivoire** | PNLS (`pnlsci.com`) Spectrum profiles · DIIS (`snisdiis.com`) RASS yearbooks | Both open; the PNLS profile is Spectrum output, the RASS series stops at 2020 | ⏳ **Grade 2, stale** |
| **Ghana** | Ghana AIDS Commission · GHS · DHIMS2 | GAC reachable, GHS over plain HTTP only, DHIMS2 hostname does not exist (Phase 3) | ⏳ Lead |
| **Senegal, Benin, Burkina Faso, Mali, Togo, Liberia, Sierra Leone** | national AIDS programmes | Not individually probed; all covered by the regional layer | ⏳ **Superseded** — probed in round two; five of the seven publish something |
| **The twelve with no PEPFAR** | see below | No national feed found for any | ⛔ Regional layer only |

Nothing here reaches grade 1, and one thing reaches grade 2. Against Southeast Asia's one
country-side connector in nine and sub-Saharan Africa's one in nineteen, West and Central Africa
offers one in twenty-four, and it is a report and not a feed. That distribution is a finding
about the region and not a failure of the search, and it is why the two regional sources
below carry most of the weight.

---

## 1. UNAIDS Naomi — sub-national estimates, grade 1

`https://naomi-spectrum.unaids.org/` is the public viewer for Naomi, the Bayesian small-area
model UNAIDS and Imperial College run with countries during the annual estimates round. It opens
with no login, and it offers a "Download all data" link to
`https://resources.spectrumweb.org/Naomi/Naomi 2026.zip`.

The zip is not the useful part. The viewer is driven by an undocumented JSON API on
`nmviewerserver.azurewebsites.net`, open, CORS-enabled and self-describing:

```
/api/v1/countries                          32 countries, each with its ISO3
/api/v1/options?country=NER                indicators, age groups, periods, sexes, area levels
/api/v1/boundaries?country=NER             the area hierarchy
/api/v1/areas?country=NER&indicator=art_current&ageGroup=Y015_999
             &period=2025-4&sex=both&areaLevel=2
```

Because `options` is per country, a connector never has to hardcode what a country publishes; it
reads it. What comes back from `areas` is a nested area tree carrying `lower`, `mean` and `upper`
on every node, with stable area codes (`NER_1_1JT`) and parent links. The bounds map onto the
schema's `value_lower` and `value_upper` exactly as Thembisa's did.

**What it carries: 25 indicators, 33 age groups, three sexes, area levels 0 to 3.** Population,
prevalence, PLHIV, ART coverage, ART number split between residents and attendees, PLHIV not on
ART, the awareness cascade, incidence, new infections, and a nine-indicator ANC block down to ART
initiations at ANC. Cameroon publishes to area level 3; Nigeria to level 2, which is its 37
states; Chad reports 23 provinces at level 1.

**Coverage.** Of 32 countries, **15 are in West and Central Africa**: Burkina Faso, Cameroon,
Chad, Congo, Gabon, Gambia, Ghana, Guinea, Guinea-Bissau, Liberia, Mali, Niger, Nigeria, Sierra
Leone and Togo. **Seven of those are among the twelve WCA countries with no PEPFAR data**
(Guinea, Congo, Chad, Gabon, Guinea-Bissau, Niger, Gambia), which is the single most valuable
fact in this log. Absent: Benin, Cabo Verde, Central African Republic, DR Congo, Côte d'Ivoire,
Equatorial Guinea, Mauritania, São Tomé and Príncipe, Senegal. Absence from the viewer is not
absence of Naomi — Côte d'Ivoire's own 2025 epidemiological profile names Naomi-Spectrum among
its sources — so the 32 are the countries that agreed to publish, not the countries that model.

**It is a cross-section, not a series, and this is the limitation that decides how it is used.**
Every country offers the same shape of period list: one historical point, then December 2025,
then September 2026 and September 2027. Malawi and South Africa each carry a second historical
point and a fourth projection. So a country typically has **two estimate years**, and the older
one is usually far back: Burkina Faso 2010, Guinea-Bissau 2010, Niger 2012, Gambia 2013, Mali
2013.

That older year is not arbitrary. In twelve of the fifteen WCA countries it lands on the year of
that country's last national HIV survey — Guinea 2018 against GN2018DHS, Sierra Leone 2019
against SL2019DHS, Nigeria 2018 against NAIIS, Chad 2015 against TD2014DHS, and so on. Naomi is
anchored to the last time somebody drew blood, which is worth stating plainly in any write-up
that uses it. Cameroon (2024), Congo (2022) and Guinea-Bissau (2010) are the three that do not
line up with a DHS, and each is anchored to some other national survey.

**The September 2026 and September 2027 points are projections and must not be emitted as
observations.** This is the Thembisa lesson arriving in a new costume: the viewer presents them
in the same period dropdown as the estimates, they carry future dates, and they were produced
under assumptions that predate the cuts this project is trying to measure. A study of what a
funding cut did in 2026 that reads a pre-cut model's 2026 projection as evidence about 2026 has
measured nothing. A connector emits the estimate periods and drops the projections, or tags them
so hard they cannot be mistaken.

**Two more things a connector has to handle honestly.**

*The national ART number is not an estimate.* Level-0 `art_current` comes back at values that are
round to the unit — Nigeria 1,510,000.00005, Niger 19,821.0000, Guinea 98,069.0000, Chad
82,674.0000 — because the national ART total is a programme figure fed into the model as a
constraint. The modelled part is the split across areas. Rows at level 0 therefore stand in a
`derived` relationship to the country's own programme reporting and must not be counted as
corroborating it. The reconciliation layer already drops sub-national rows from comparison
(`reconcile.py:66`), so the risk sits entirely at level 0.

*Some intervals are degenerate.* Niger's PLHIV at 15+ for December 2025 is 28,413 with bounds of
1,000 and 244,496, and its ART lower bound comes back as 1.1e-21. Cameroon, Nigeria, Guinea and
Chad all return tight, sane intervals over the same call. Niger's width is real — a very low
prevalence anchored to a 2012 survey — and the answer is a per-country data-quality flag, not
dropping the source. A near-zero lower bound should be recorded as what it is, which is the model
declining to rule out zero.

## 2. Global Fund Data Explorer — programme results and money, grade 1

`https://data.theglobalfund.org/` is the Data Explorer, and it too is a front end over an open
JSON API, `data.api.theglobalfund.org`, with no login:

```
/results/cycles?geographies=GIN            the years available
/results/stats?geographies=GIN&cycle=2024  headline results
/results/table/GIN/2024                    the full indicator table
/disbursements/line-chart/activityAreaGroup/Standard%20View?geographies=GIN
/expenditures/heatmap/principalRecipientType,principalRecipientSubType,principalRecipient/...
/budgets/sankey/...  ·  /allocations/radial/GIN  ·  /funding-requests/GIN
```

A caveat on how this was found: the Global Fund's *documented* API host,
`fetch.theglobalfund.org`, answers this network with an Azure Front Door "The request is blocked"
page. By the standard Phase 3 set, an edge block establishes nothing about what sits behind it,
so the documented API stays open as a question. The Data Explorer's own backend is reachable and
is what the coverage below rests on.

**Why this is the answer to the no-PEPFAR twelve.** Guinea has zero PEPFAR rows in the panel. Its
2024 results table carries people on ART (98,998), people on ART with a viral load result
(44,855), early infant diagnosis, HIV-positive pregnant women on ART, and key-population
indicators the aggregators do not publish at all: men who have sex with men reached with
prevention (10,780), HIV tests among sex workers (20,446), HIV tests among MSM (9,711), plus
people who use drugs reached. That is a programme cascade with a KP layer, in a country the
donor-side panel currently cannot see.

The series is annual and continuous. Chad's people-on-ART runs 51,866 (2017) → 69,379 (2019) →
83,792 (2021) → 69,159 (2023) → 76,828 (2024); Niger 18,425 → 20,427 → 24,292 → 22,109 → 21,139;
Central African Republic 33,021 → 47,032 → 56,123 → 63,560 → 66,851. Eight years, 2017 to 2024,
which is the panel's own shape.

All 24 WCA countries were then checked one at a time against `/results/table/{ISO3}/2024`:
**22 of the 24 return a people-on-ART indicator.** The two that do not are Gabon, which returns a
results table with no HIV ART line because its HIV programme is domestically financed and the
Global Fund covers TB and malaria there, and Equatorial Guinea, which returns an empty table.
Across the twelve countries with no PEPFAR data, that leaves ten with an ART series.

**One number to be careful with.** Naomi's Guinea national ART figure for December 2025 is 98,069;
the Global Fund's for 2024 is 98,998. Two sources a year apart, 0.9% apart, in a growing ART
cohort. The likely explanation is that both trace back to the same national programme report,
which would make them `derived` and not corroboration. That is a hypothesis this log records
and not a finding, and it is exactly the pattern `reconcile.py` exists to catch. It should be
checked before either source is used to validate the other.

## 3. DHS — the survey layer, already connected and under-used

The DHS connector (`hivimpact/connectors/dhs.py`) already reads
`api.dhsprogram.com`, which is open and needs no key. Two things about it turned up here.

**Eighteen of the twenty-four WCA countries have a survey with HIV biomarker testing**, from the
`surveyCharacteristicIds=23` endpoint: Benin, Burkina Faso, Cameroon, Chad, Congo, DR Congo, Côte
d'Ivoire, Gabon, Gambia, Ghana, Guinea, Liberia, Mali, Niger, São Tomé, Senegal, Sierra Leone,
Togo. The six without are Cabo Verde, Central African Republic, Equatorial Guinea, Guinea-Bissau,
Mauritania and Nigeria — Nigeria because its HIV survey is NAIIS, run outside the DHS programme.
Timeliness is the constraint: only DR Congo 2023, Gabon 2019, Sierra Leone 2019, Cameroon 2018,
Guinea 2018 and Senegal 2017 are recent, and everything else stops at 2014 or earlier. The DHS
layer is a pre-period baseline and the thing Naomi is calibrated to, not a post-cut measurement.

**The API serves sub-national breakdowns and the connector does not ask for them.** Adding
`&breakdown=subnational` returns region-level prevalence with the region name in
`CharacteristicLabel`, which the schema's `admin1` field already accommodates. This is the
cheapest sub-national gain available anywhere in this log.

**A defect found and fixed.** `to_iso3("Congo Democratic Republic")` returned `None`, so every DHS
row for DR Congo was being dropped silently — including CD2023, the most recent HIV-testing survey
in the region, in the region's second-largest epidemic. The DHS Program spells DRC that way and
the overrides table held four other spellings but not this one. Fixed at
`hivimpact/normalize.py:48`. Checking the full DHS country list against the mapping leaves one
other unmapped name, "Nigeria (Ondo State)", which is a state-only survey and correctly excluded,
though it is excluded silently and not by decision.

## 4. PHIA — grade 3, and thinner here than in the east

PHIA covers this region at two countries, CIPHIA (Côte d'Ivoire) and CAMPHIA (Cameroon), against
near-complete coverage of Eastern and Southern Africa. Access is unchanged from Phase 3: the data
manager at `phia-data.icap.columbia.edu` is a registration-gated request system serving an
untrusted certificate. Grade 3, a data-request route, and for this region a small one.

---

## Nigeria — ⛔ gated by policy as well as by login

Nigeria is 2,000,000 of the region's 5,031,800 people living with HIV and has 1,510 sub-national
rows in the panel from `pepfar_snu` across 37 states, so the donor side is deep. The country side
is shut, and the Phase 3 login wall at the National Data Repository is now the smaller half of
the reason.

- **The NACA HIV & AIDS Data Ecosystem**, launched 29 January 2025, is exactly what this project
  would want: NACA-run, Global Fund-funded, built by DURE Technologies, hosted in Nigeria,
  consolidating NDR, NHMIS and eNNRIMS behind one interface, searchable by state, LGA, month,
  quarter and year. No public address for it could be found, and NACA's launch material does not
  give one.
- **NACA's stated policy closes the question.** In April 2026, responding to state-by-state HIV
  figures circulating from the NDR dashboard, NACA said only authorised government health
  institutions should generate and release HIV data, and directed anyone else to submit a formal
  request to the agency. The same statement is a warning worth carrying into the write-up: NACA
  said the circulating figures reflected HIV positivity from routine facility testing and were
  not a measure of prevalence or incidence. Test positivity read as prevalence is a mistake this
  panel could make on its own.
- **What is open** is NAIIS 2018 and the quarterly factsheets on `naca.gov.ng`. NAIIS gives
  state-level prevalence at one point in time and is already the anchor for Nigeria's Naomi
  estimates.
- **Route:** an institutional data-sharing agreement, the same conclusion as the other six gated
  countries, with the difference that here there is a named agency and a stated request process
  to address it to.

## DR Congo — ⛔ gated database, open library, one additive item

DR Congo is 610,000 people living with HIV, the second-largest epidemic in the region, and the
one large WCA country absent from Naomi.

- **VIH DATAPRO** (`vihdatapro.app`) is the PNMLS multisectoral database, presented under the
  Presidency, and it opens on *Se Connecter* and *Créer un compte*. Registration wall, grade 3.
  Its stated scope is the national HIV response indicators of the 2020–2023 strategic plan, which
  is a plan period that has ended while the current plan runs to 2027.
- **The PNMLS virtual library** (`documentation.pnmls.cd`) is open with no login and reasonably
  well organised. Its HIV holdings are dominated by GAM country progress reports (2017, 2020),
  which are the UNAIDS submission and therefore already in the panel — the Malaysia test, failed
  for the usual reason. The PNLS annual reports it holds stop around 2017.
- **The one additive open item is EDS-RDC III 2023–2024**, the third DHS, published 2024 by the
  Institut National de la Statistique, held in the library and also in the DHS API as CD2023. With
  the alias fix above it now enters the panel; with `breakdown=subnational` it would enter with
  province detail.
- PNLS's own site still returns 403 at the edge, as in Phase 3, and that still establishes nothing.

## Cameroon — ✅ grade 2, and the only country-side source in the region that passes

Cameroon is 510,000 people living with HIV. It is also the deepest Naomi country in the region,
publishing at area levels 0 through 3. It did not need to be: its own national committee publishes
more than Naomi does.

- **Source:** the CNLS annual report, `https://cnls.cm/catdocument/rapports-annuels/`. Open, no
  login, no bot blocking, English and French editions of the same document. The 2024 report is
  123 pages and was published in June 2025. Earlier editions on the same page run 2023 and 2016;
  the entry labelled 2021 is the 2021–2023 strategic plan and not a report.
- **Born-digital, and the check matters.** A first automated read of the file called it scanned
  images. It is not. Every table extracts as text with `pypdf`, including the numbers, so the
  grade-2 requirement — deterministic extraction with no OCR — is met. That an automated reader
  said otherwise is the argument for opening the file instead of trusting a summary of it.
- **What it carries beyond the aggregators**, which is the test that decides whether a connector
  is worth writing:
  - **The ten regions, on the programme cascade.** Table 38 splits the active ART file by region,
    sex and children (Centre 115,372, Littoral 70,051, Adamawa 25,723, against a national 449,290
    at 31 December 2024). Table 42 gives viral-load coverage *and* suppression by region, and the
    spread is the point — coverage runs from 43.3% in Adamawa to 91.5% in the Far North against a
    national 68.7%. Table 40 gives 12-month retention by region. Table 41 gives the
    community-dispensation cohort by region and quarter. Tables 14, 16, 19, 21, 23, 27, 28, 30, 32
    and 33 add condom distribution, testing and positivity, self-testing, PMTCT, EID and infant
    prophylaxis at the same level. No aggregator in this panel publishes anything below Cameroon's
    national total.
  - **Key populations as programme counts, not estimates.** Table 18 gives, for female sex
    workers, men who have sex with men, transgender people and people who inject drugs, the number
    screened, the number positive, the positivity rate and the linkage-to-ART rate: 91,188 FSW
    screened with 3.3% positivity and 99.6% linked, 38,899 MSM at 4.3% and 92.9%, 1,191 TG at 8.5%,
    4,493 PWID at 3.9% and 82.1%. UNAIDS publishes modelled KP prevalence. This is what the
    programme actually did, with the linkage step attached.
  - **Money by donor, and budget against execution.** Table 46 breaks 2024 funding down by source
    in CFA francs: Global Fund 35.17bn, government counterpart funds 6.48bn, the national
    investment budget 2.87bn, NACC-CDC/PEPFAR 916m, WHO 265m, UNICEF 125m. Tables 47 to 49 then
    give execution against budget — Global Fund 66.87% executed, counterpart funds 14.74%, with
    the reasons stated. That is the recipient side of the disbursement question, and it is the one
    thing no donor-side file in this panel can carry: ForeignAssistance.gov and the Global Fund
    both record money leaving, and this records how much of it was spent and on what.
  - **Timeliness.** 2024 programme data from a DHIS2 extract dated 26 March 2025, published in
    June 2025.
- **The catch, and it is the usual one.** The report's *denominators* are EPP-Spectrum output —
  the 510,000 PLHIV figure and every coverage percentage built on it. Those are `derived` from the
  same UNAIDS estimate already in the panel and must not be treated as a second measurement of it.
  The numerators are the independent part: the active file, the viral-load counts, the testing
  counts and the money all come from Cameroon's own systems. A connector takes the counts and
  recomputes any ratio it needs, and does not ingest the published coverage rates.
- **What it also proves.** Cameroon's national HIV database is DHIS2, and DHIS2 is the system that
  returned a login wall in six countries in the Phase 3 probe. The report is that database's
  public face. Where a ministry publishes its own DHIS2 extract as a report, the login wall stops
  being the end of the question, and that is worth checking in the six gated countries before any
  of them is written off.
- **Connector shape:** grade 2, one PDF per year, region-level rows tagged
  `routine_programme_record` with `admin1` set, plus a small set of national KP and finance rows.
  Two years of regional tables exist so far (2023 and 2024), which is thin for a trend and lands
  either side of nothing yet. The 2025 edition, when it appears, is the first Cameroonian
  regional read of the post-cut year.

## Côte d'Ivoire — ⏳ open, born-digital, and stale or redundant

Côte d'Ivoire is 410,000 people living with HIV and has 1,264 sub-national rows from `pepfar_snu`
across 32 units, so the donor side is strong. Two open country-side sources, neither of which
passes cleanly:

- **PNLS** (`pnlsci.com`) publishes an epidemiological profile as a born-digital PDF, 2024 and
  2025 editions, at `/donnees/donnees-de-routine/`. It is Spectrum output, which is what UNAIDS
  publishes, so it fails the Malaysia test on its face. The profile's own source list names
  Naomi-Spectrum for sub-national estimates, which says Côte d'Ivoire produces Naomi estimates it
  does not publish through the viewer. Whether the profile prints those estimates as tables is the
  open grade-2 question and is not settled here.
- **DIIS** (`snisdiis.com`), the ministry's health information directorate, publishes the RASS
  annual health situation report and the statistical yearbook openly, with no login, back to 2007.
  The series stops at RASS 2020. A five-year-old yearbook cannot speak to a 2025 funding cut, so
  this is grade 2 and stale, and it becomes interesting the moment RASS 2021 onward appears.

## The twelve with no PEPFAR — ⛔ country side, ✅ regional layer

Cabo Verde, Central African Republic, Chad, Congo, Equatorial Guinea, Gabon, Gambia, Guinea,
Guinea-Bissau, Mauritania, Niger and São Tomé and Príncipe hold 632,800 people living with HIV
between them and have no PEPFAR rows in the panel at all. Before this log they had only the
modelled aggregator layer, which is to say UNAIDS, WHO and the World Bank republishing one
Spectrum output three times. The regional sources change that:

| | Naomi | Global Fund ART series | DHS with HIV testing |
|---|---|---|---|
| Chad, Congo, Gambia, Guinea, Guinea-Bissau, Niger | ✅ | ✅ (all but Guinea-Bissau's series unverified beyond 2017) | ✅ except Guinea-Bissau |
| Gabon | ✅ | ⛔ no HIV indicator (TB and malaria only) | ✅ |
| Cabo Verde, Central African Republic, Mauritania, São Tomé | ⛔ | ✅ | ✅ São Tomé only |
| Equatorial Guinea | ⛔ | ⛔ no Global Fund results | ⛔ |

**Equatorial Guinea is the one country in the region this log leaves dark.** No Naomi, no Global
Fund, no DHS with HIV testing, no PEPFAR, and no PLHIV value in the panel's latest year. São Tomé
also has no PLHIV value in the latest year despite having both a Global Fund ART series and a 2008
DHS, which is a gap in the aggregator layer and not in this region's sources.

---

## What this changes

**First, what these four sources are not.** Three of the four candidates below are not country
connectors, and the distinction decides how they are ranked and how their rows must be tagged.
Naomi is a UNAIDS product — the small-area model that feeds the UNAIDS estimates — so it stands
`derived` against `unaids_aidsinfo` and adds geography, not a second measurement. The Global Fund
is donor-side reporting, grade 4, the same class as PEPFAR, and `subset` for the same reason:
it measures the Global Fund footprint and not the national programme. DHS is an existing
connector needing one query parameter. Only Cameroon is a country going to source.
[**Overturned by round two.** Nine are, plus DR Congo table by table, and the region's domestic
money is published for 18 of 24 in a single open spreadsheet.]

That matters because the country layer is incomplete by construction — it always is, in every
region, which is why the panel carries an aggregator layer alongside it. A region where
twenty-three of twenty-four national databases are shut is not an argument for building something
other than country connectors. It is a map of where the institutional-agreement work has to go,
and it makes the one open country source more valuable, not less.

1. **Cameroon CNLS.** Grade 2, born-digital, ten regions on the ART cascade, viral-load coverage
   and suppression, retention, a key-population cascade with linkage rates, and 2024 funding by
   donor with execution against budget. The only source in this region that is a country speaking
   about itself, which is what Adrian asked. Its counts are `independent`; its published coverage
   percentages are not, since the denominators are EPP-Spectrum, so the connector takes the
   numerators and recomputes any ratio it needs.
2. **Global Fund connector.** Fills a real hole in the *donor* layer: twelve WCA countries have no
   donor-side data of any kind, and this is the funder in them. Annual 2017–2024, ART for 22 of
   24, key-population indicators no aggregator publishes, plus disbursements and expenditure on
   the same API. Tagged `subset`, like PEPFAR.
3. **DHS sub-national breakdown.** One query parameter on a connector that already exists, and it
   puts region-level survey prevalence into `admin1` for 18 WCA countries. `independent`, and the
   only independent measurement of the four. The DRC alias fix has already been made.
4. **Naomi connector.** Sub-national to level 3 for 15 WCA countries with bounds on every value,
   and worth 17 more countries elsewhere. Ranked last on purpose: it is a UNAIDS model output
   entering a panel that already carries UNAIDS, WHO and the World Bank republishing one Spectrum
   run, so it must be tagged `derived` against `unaids_aidsinfo` or it will make the
   reconciliation layer look better corroborated than it is. Must also drop the September 2026 and
   2027 projections, flag level-0 ART as a programme figure and not an estimate, and carry a
   per-country flag for degenerate intervals.

The honest summary for Adrian is that "can we go to source?" gets a fourth answer, and it is the
hardest of the four. In West and Central Africa the national database is shut in twenty-three
countries out of twenty-four, so the going-to-source work here is mostly institutional and
mostly slow. Two things soften it. The regional and donor layers reach further into this region
than into any other, which keeps the countries visible while the agreements are negotiated. And
in Cameroon the ministry publishes the contents of its own gated database as a report — the one
route through a login wall that needs an agreement with nobody, and the first thing to check in
the six countries Phase 3 wrote off on the strength of a login screen.

---

# Round two — a second pass, and what it overturns

Round one of this log stopped at four candidates. That was too early. This section records a
second pass made afterwards, and it does two things: it overturns two of round one's
conclusions, and it opens five source classes the first pass never looked at.

The two overturned conclusions, stated plainly:

1. Round one called Cameroon *"the region's only country-side connector candidate"*. Nine WCA
   countries publish an open, born-digital, additive national source, and DR Congo publishes a
   tenth in part.
2. Round one recorded seven countries as *"not individually probed … all covered by the regional
   layer"*. They have now been probed, and five of the seven publish something usable.

Neither correction came from a cleverer search engine. Both came from dropping an assumption:
that a country either has an open database or has nothing.

## The rule that was wrong: the additive test is per table, not per document

Round one applied the Malaysia test to whole documents. A country's published GAM *report* was
treated as redundant with its GAM *submission*, since UNAIDS already publishes the submission's
values through AIDSinfo.

That is wrong, and DR Congo is the case. The PNMLS GAM 2024 report (83 pages, open at
`pnmls.cd/documentation/`) names a source under each table, and the names differ:

- seven tables sourced **"Données DHIS2"** — the gated national database, published as a table
- four tables sourced **"Rapport PNLS 2023"** — the programme's own annual report
- province-level PrEP sourced to **PEPFAR** — `derived`, and must be tagged so
- **Tableau LVI**, the REDES money table: institutional HIV spending 2018–2021 by financing
  source, by intervention and by beneficiary population. International share rises 70% → 74%
  (167,861,131 USD in 2021); the total runs 149.6m → 227.8m USD

One document, four classifications. The rule that follows is that **each table's named source
decides its own status**, and a document is never redundant as a whole.

## The national statistics yearbook — the class round one never opened

Ministries of health in francophone Africa publish an *annuaire des statistiques sanitaires*:
a several-hundred-page volume of routine service tables, district by district and often facility
by facility, built from the country's gated DHIS2. It is the gated database, printed.

**Chad** is the find. `inseed.ssn-tchad.td` serves a JavaScript application that returns one
identical 3,239-byte shell for every path, so both a fetch tool and `curl` saw nothing there.
Downloading the application bundle and grepping it for endpoints produced
`https://inseed.ssn-tchad.td/api`. The menu endpoint answers `401 Token d'accès requis`;
`/api/publications/search?q=` needs no token and lists the yearbook series 2005–2023.

The 2023 edition (286 pages, July 2024) carries:

- **Tableau 306** — the ART cohort by province, with stock at 31/12/22, new inclusions,
  transfers in, and stock at 31/12/23 (N'Djamena 24,228 → 26,027; Logone occidental 6,528 →
  6,969; Lac 5,195 → 5,752)
- **Tableau 322** — PMTCT by province
- TB/HIV with ARV coverage, 2011–2023

Nothing in the aggregator layer publishes a provincial ART cohort with its flows. This passes
the additive test without argument.

## NASA / REDES — the national AIDS spending assessment

Indexed at `unaids.org/en/dataanalysis/knowyourresponse/nasacountryreports`. A country-run
expenditure survey giving total HIV spending by financing source, by intervention, by
beneficiary population and by financing agent. Three verified by reading the PDFs:

- **Benin 2024** (published March 2025): 9,292,143,634 FCFA in 2024 against 11,952,301,720 in
  2023. Central government 31%, households 6%, bilateral USAID 1,580,353,218 (17%), Global Fund
  3,868,068,978 (42%, down by more than half from 7,463,926,165), UN 3%. Financing agents
  include Family Health International at 14.7% and Plan International at 12.4%. Ten-year series,
  2015–2024.
- **Togo 2023**: 25,184,643,343 FCFA, 85.58% international. Global Fund 13,887,628,233; the US
  government through PEPFAR and USAID 5,471,99x,xxx; domestic 3,631,867,244 against
  3,126,562,557 in 2022.
- **Ghana 2022**: public 41%, private 16%, international 43%, reported in USD for 2021 and 2022.

**The classification rule comes from Ghana's own methods section.** Its international line is
built from Global Fund principal-recipient ledgers and the PEPFAR expenditure report, so that
line is `derived` against our own donor connectors and must not be counted as corroboration of
them. The domestic public, household and private lines are independent and exist nowhere else
in the panel.

One warning for the extraction: Benin's executive summary contains transcription errors that
its own figure tables do not. Take the tables, never the prose.

## The UNAIDS GAM programme-expenditure database — the same class, machine-readable, in one file

This is the largest single find of round two, and it was three clicks from a page the project
had already used.

`https://hivfinancial.unaids.org/GARPR16-GAM2025ProgrammeExpenditures-20250903.xlsx` — 5.5 MB,
open, no login, published 3 September 2025.

- **59,947 rows, 121 countries**, reporting cycles GARPR 2016 through GAM 2025, expenditure
  years **2011–2024**
- Rows are the NASA programme hierarchy (`1 Treatment, care and support`, `1.1 HIV testing and
  counselling`, `1.2 Antiretroviral treatment`, `1.2.1 Adult antiretroviral therapy`, …)
- Columns split every figure by financing source: **domestic public** (central, sub-national,
  development banks, social security), **domestic private** (insurance, **households**,
  corporations, non-profits), and **external** with **PEPFAR and the Global Fund as their own
  named columns**, plus other bilateral, other multilateral and development banks

**18 of the 24 WCA countries appear.** Eight have expenditure year 2024: Benin, Burkina Faso,
CAR, Guinea, Gambia, Mali, Chad, Togo. Six are absent altogether — Cameroon, Congo-Brazzaville,
Cabo Verde, Guinea-Bissau, Equatorial Guinea, São Tomé — which is where the country NASA PDFs
keep their value.

Two cross-checks were run against documents already extracted by hand:

| Country-year | From the PDF | From the GAM file | Gap |
|---|---|---|---|
| Benin 2024, total | 9,292,143,634 FCFA ≈ 15.2–15.5m USD | 14,757,867 USD | 3–5%, inside the exchange rate |
| DR Congo 2021, total | 227.8m USD | 223,877,209 USD | under 2% |
| DR Congo 2021, international | 167,861,131 USD | 163,912,882 USD | under 3% |

**These agreements are not triangulation.** The GAM submission and the NASA report are prepared
by the same national body from the same exercise, so they are one measurement published twice.
What the agreement establishes is extraction fidelity — that the spreadsheet can stand in for
the PDF — and that is worth having, since it removes hand extraction for 18 of 24 countries.

**The trap in this file is the zero.** A blank or zero means *not reported*, never *not spent*.
Mali 2024 reports 3,184,591 USD, all domestic, and zero international — while the Global Fund
API shows Mali holding active HIV grants disbursing through 2024. Gambia 2024 reports 33,054 USD
in total. Chad reports 21.7m USD of international money as a lump with no donor split. Any
connector over this file has to treat zeros as missing and cross-check every donor line against
the donor's own reporting before reading an absence as a fact.

**What it is, in the panel's terms:** the PEPFAR and Global Fund columns are `derived` against
our own connectors for those two funders. The domestic public, household and other private
columns are `independent` and have no other source anywhere in the pipeline. And the timing is
worth being clear about — expenditure year 2024, reported September 2025, is the **baseline the
cut will be measured against**. The cut year itself appears in the GAM 2026 cycle.

## PEPFAR Spotlight — the pipeline reads three files out of fifteen

`data.pepfar.gov` serves the same one-shell-for-every-path application as Chad's statistics
office, so the same method applies: pull `/static/js/main.*.js` and read the dataset section out
of the bundle. Fifteen zip files sit under `https://data.pepfar.gov/media/`, all open, all
direct, no login. Every one returns 200. The partner MER files were refreshed on 5 August 2026;
the rest on 18 June 2026.

The pipeline currently reads three: `Enhanced_Geographical_Analysis` (`pepfar_snu`),
`Public_Partner_Budgets_and_Expenditures` (`pepfar_expenditure`) and `Public_Partner_MER_TopLine`
(`pepfar_panorama` and `pepfar_agency`). The other twelve were never opened. Four of them
matter.

**`PEPFAR_OU_Budgets_and_Program_Expenditures`** — budget by operating unit back to **2004** and
expenditure 2018–2025, against the partner file's FY2021 start, and split by `Program`,
`Sub Program` and `Beneficiary` (Key Pops, OVC, Pregnant & Breastfeeding Women, Priority Pops,
Females, Males). Twelve WCA countries. It answers which population lost money, over a twenty-one
year baseline the partner file cannot reach.

| | 2023 budget | 2023 spent | 2024 budget | 2024 spent | 2025 budget | 2025 spent |
|---|---|---|---|---|---|---|
| Nigeria | 804,150,000 | 696,723,649 | 793,667,000 | 603,103,517 | 673,011,082 | 525,811,614 |
| Côte d'Ivoire | 210,546,000 | 168,163,544 | 240,736,314 | 194,873,024 | 212,800,000 | 137,178,260 |
| Cameroon | 160,882,000 | 135,313,191 | 209,242,000 | 134,837,162 | 165,000,000 | 114,341,666 |
| DR Congo | 225,450,000 | 173,601,610 | 245,889,500 | 185,435,941 | 210,000,000 | 147,162,836 |

**`PEPFAR_OU_Commodities_Procurements`** — planned commodity budget **and planned quantity**, by
COP planning cycle, FY2019–2025, 55 countries, classified to named items. This is the physical
supply line: ARVs, rapid test kits, laboratory reagents, condoms, TB drugs.

The finding in it, for Nigeria: the COP24/FY2025 plan carries
*Dolutegravir/Lamivudine/Tenofovir DF 50/300/300 mg Tablet, 90 Tablets* — first-line adult
therapy, and the single largest ARV line the year before at 2,550,449 bottles and 31,153,224 USD
— **as a line item with a quantity of zero and a budget of zero**. The row is present and
zeroed, not absent. Adult ARV procurement overall falls 4,667,649 → 863,629 units and paediatric
415,605 → 141,880.

That is a statement about *PEPFAR's planned procurement*, and it is not the same as a statement
about ARV availability in Nigeria. The Global Fund also procures there, and so does the
government. The Global Fund API can test exactly that, which makes this one of the few places
in the panel where a claim and its check sit on two independent feeds.

**The quantity column changes unit between years without changing the item string.** Nigeria's
*HIV-1/2, Determine, 100 Tests* is 75,757 units at 6,484,799 USD in FY2024 — 85.60 USD each, a
pack of 100 — and 5,965,515 units at 4,772,412 USD in FY2025 — 0.80 USD each, a single test.
Same name, same country, different unit, and the naive read is a fifty-eight-fold rise in
testing supply in the year the money fell. Quantities are usable per item with the unit
recovered from the implied price, never summed across items or across years without that check.

**`Country_Level_Results_by_Modality_Coarse_Age_and_Sex`** — MER results by **testing modality**
(28 values: Index, IndexMod, Mobile, HomeMod, SNS, VCT, PMTCT ANC, TB clinic, inpatient, and so
on), 59 countries, FY2018–FY2025, and it carries the attrition indicators the top-line file does
not: `TX_RTT`, `TX_ML_died`, `TX_ML_refused_stopped`, `TX_ML_transferred_out`, interruption
split by duration, and multi-month dispensing.

Grouping the modality codes by PEPFAR's own convention — the `Mod` suffix and the `Active`/`SNS`
codes are community delivery, everything else is facility — gives new positives found, Q4 FY2024
against Q4 FY2025:

| | facility | | community | |
|---|---|---|---|---|
| Nigeria | 17,720 → 16,907 | −4.6% | 12,903 → 10,953 | **−15.1%** |
| Côte d'Ivoire | 3,857 → 3,726 | −3.4% | 1,455 → 970 | **−33.3%** |
| Cameroon | 5,847 → 5,261 | −10.0% | 518 → 0 | **−100%** |
| DR Congo | 4,929 → 4,328 | −12.2% | 1,186 → 569 | **−52.0%** |
| Mali | 1,108 → 1,066 | −3.8% | 506 → 289 | **−42.9%** |
| Burkina Faso | 796 → 852 | +7.0% | 271 → 36 | **−86.7%** |
| Liberia | 768 → 1,237 | +61.1% | 182 → 0 | **−100%** |
| Togo | 525 → 569 | +8.4% | 463 → 329 | −28.9% |

Ten of the twelve WCA countries with PEPFAR data show community case-finding falling harder
than facility case-finding, and two go to zero. Benin is the exception, off a base of 49.
Senegal rises on both. This is the mechanism, and no other source in the panel can show it: the
outreach that finds people outside a clinic is discretionary, partner-delivered, and it goes
first.

The same file, Nigeria, Q4 to Q4: **`PrEP_NEW` 75,736 → 1,508**, a 98% fall. `TX_RTT` — people
brought back onto treatment after interrupting — halves, 60,059 → 29,528, while `TX_CURR` rises
by 63,009. Interruptions of six months or more also fall, 27,756 → 17,467, and that reading is
ambiguous in a way that has to be stated: fewer people interrupting and fewer people being
traced and classified as interrupted look identical in this file. Both are consistent with less
outreach; they are not separable here.

**`HRH_Inventory_Public_Dataset`** — PEPFAR-funded health workers by cadre, with annual spend,
head count and full-time equivalents, 57 countries. FY2025 only, so it is an establishment
snapshot and not a trend.

**One hard limit on everything above.** Spotlight's own front page says FY2025 publishes Q4
results alone, and the files bear it out — FY2025 Q1, Q2 and Q3 are empty columns. The
within-year path of the cut is not published. Every FY2025 comparison in this project is
therefore a Q4-against-Q4 comparison, and no FY2025 annual total exists for a cumulative
indicator. The year the reporting mattered most is the year the reporting got thinner.

## IATI through d-portal — the donor side, current to this month

`api.iatistandard.org` wants a key and `api.iatiregistry.org` no longer resolves, but
`d-portal.org/q` answers open JSON with no key at all.

Querying transactions on DAC sector **13040** (STD control including HIV/AIDS):

- **26 publishers** report HIV activity in Nigeria alone, including USAID, State, HHS, DoD, the
  Global Fund, the Gates Foundation, FCDO, UNICEF, WHO, **UNAIDS itself** (`XM-DAC-41110`), and
  NGOs — CHAI, Pact, Frontlineaids, Aidsfonds
- Transactions carry an exact date. The most recent HIV disbursement in the WCA set is dated
  **15 August 2026** — today. Most countries run to late July 2026.

HIV disbursements, USD, four largest WCA epidemics:

| | 2023 | 2024 | 2025 | 2026 (part) |
|---|---|---|---|---|
| Nigeria | 338,179,984 | 395,198,777 | 330,726,636 | 172,923,392 |
| DR Congo | 114,679,204 | 164,832,544 | 104,605,204 | 26,104,072 |
| Côte d'Ivoire | 104,229,555 | 118,518,766 | 90,938,739 | 33,119,646 |
| Cameroon | 118,396,239 | 133,340,801 | 112,635,543 | 26,784,267 |

It passes the additive test against both donor sources the panel already has. OECD CRS runs
twelve to eighteen months behind; this is current to the month. ForeignAssistance.gov covers the
US government; this covers the Gates Foundation, FCDO, AFD, the Italian agency, UNAIDS and a
dozen NGOs that no other feed in the panel reaches.

**Two traps, both confirmed rather than assumed.** The transaction-type column mixes eight
vocabularies — `D`, `E`, `C`, `11`, `IF`, `R`, `IR`, `LR` — and 1,834 of 46,964 distinct
activity/date/value keys appear under more than one of them, so summing without picking a single
code double-counts. And `sum()` in the query API silently returns zero: aggregation has to be
done locally over raw rows.

## UNICEF SDMX — checked, and mostly a republication

`sdmx.data.unicef.org/ws/public/sdmxapi/rest/` is open and undocumented-friendly; the `HIV_AIDS`
dataflow returns 139,446 rows as CSV in one request. Its dimensions include `WEALTH_QUINTILE`
and `RESIDENCE`, which no other source in the panel carries.

It does not earn a connector on the strength of that. Of 26,242 WCA rows, **21,460 are sourced
"UNAIDS 2025 estimates"** and a further 1,270 to Global AIDS Monitoring — `derived` and `subset`
against connectors the panel already has. What is additive is the survey slice: 3,512 rows from
MICS and DHS, on knowledge, testing, stigma and condom use, broken by wealth quintile and by
urban/rural.

MICS reaches six WCA countries that have no recent DHS in this dataflow — CAR, DR Congo,
Congo-Brazzaville, Guinea-Bissau, São Tomé and Togo — and that is the case for taking it. The
case against taking it for *this* project is timing: the most recent MICS anywhere in the WCA
slice is 2019, and the most recent DHS is Ghana 2022. It is a pre-cut equity baseline, not a
measurement of the cut. Worth having as a stratifier; worth nobody's time as an impact signal.

## IHME's DAH database — real, and behind a user agreement

The Financing Global Health viewer is another application shell, and its bundle points at GHDx.
The series page lists **Development Assistance for Health Database 1990–2026, released 11 June
2026** — DAH by health focus area, source and channel, with the projection years that carry the
2025 cuts.

The download route runs through `ghdx.healthdata.org/download-access/login` under a
free-of-charge non-commercial user agreement. The data is real and the terms permit our use, but
somebody has to accept those terms and log in, and that is the researcher's to do, not mine.
This is the same shape as the UNAIDS AIDSinfo CSVs the pipeline already handles: a hand download
dropped into `data/raw/`, with the connector reading the file and not the site. Recorded as
grade 3, with a working manual route.

## Nigeria — published to a human, not to a machine

`wallboard.nascp.gov.ng` renders a Power BI dashboard from the national programme, **last
refreshed 20 February 2026**, with year buttons for 2023, 2024 and 2025, a month selector, a
State dropdown, and tabs for PrEP, HTS, ART and PMTCT. It reads 9,343 newly initiated,
**1,593,757 on ART**, 994,370 with a viral-load result, 953,709 suppressed, 95.9% suppression,
and a PMTCT row of 528,955 tested, 649 positive, 1,663 known positive, 591 newly started and
1,648 already on ART.

The publish-to-web query backend returns 403 to scripted requests on
`modelsAndExploration`, `explore/…/exploration` and `conceptualschema`, with the correct cluster
and resource key and matching Origin and Referer. The dashboard renders correctly in a browser;
clicks inside the embedded frame did not register and no data requests were captured.

This is a grade the ladder did not have. The data is public, current, sub-national and free —
and reachable only by a human with a mouse. A connector would need a headless browser, which is
outside this pipeline's contamination-safe design and would break the first time the dashboard
is republished. **Grade 3.5: published to a human, not to a machine.** Recorded, not built.

> **Overturned by round three (2026-08-17).** The wallboard backend still returns 403. The
> National Data Repository behind it serves an open JSON API on two other hosts, and a `Referer`
> header is the whole gate. Nigeria is grade 1; see *Nigeria — the round's largest overturn*
> below.

## Negative findings, so nobody researches them twice

- **Togo's 2023 yearbook** exists and no route reaches it. `sante.gouv.tg` redirects to
  `sante-assurances.gouv.tg` and returns `text/html` for the `.pdf` path; the PNLS site returns
  500; the Internet Archive capture is truncated. The Togo NASA 2023 report partly compensates.
- **The Internet Archive caps stored PDFs at 5 MiB.** A truncated capture keeps `%PDF` and its
  page objects but loses the cross-reference trailer, so `pypdf` cannot open it. A Wayback PDF
  of exactly 5,242,880 bytes is a truncation, not a file.
- **WHO AFRO's `aho.afro.who.int` is gone** — 404 at every path including the root. Only the
  Azure blob container behind it survives, and listing is disabled, so it answers exact blob
  names and nothing else. A 404 on a guessed filename there is not evidence of absence.
- **Côte d'Ivoire remains closed.** The PNLS publishes Spectrum profiles; the RASS series still
  stops at 2020.
- **The Global Fund API carries no PU/DRs.** Its documents entity holds 2,283 items in nine
  types — funding requests, concept notes, country profiles — all qualitative.
- **No NASA report exists** for Cabo Verde, CAR, Congo, Equatorial Guinea, Gabon, Gambia, Guinea,
  Guinea-Bissau or Senegal.
- **Chad's old Joomla URLs are dead**; the API route above is the only one that works.

## What round two changes

Round one's ranked list stands, and four things join it.

5. **The UNAIDS GAM expenditure workbook.** One file, one request, 121 countries, expenditure by
   programme area split by financing source with households and domestic public broken out.
   It is the cheapest connector in the whole project and it fills the panel's largest hole —
   the money that is not donor money. Build it first.
6. **The four unread PEPFAR Spotlight files.** No new access work at all: the same host, the same
   format, the same zip convention the pipeline already parses. Commodities is the physical
   supply line, the OU file is a twenty-one-year budget baseline split by beneficiary
   population, modality is the community-outreach mechanism, and the attrition indicators are
   the harm measure Adrian's question actually asks for.
7. **IATI through d-portal.** The donor side, current to this month, covering the foundations,
   the NGOs and the non-US bilaterals that neither CRS nor ForeignAssistance.gov reaches.
8. **The country layer, ten sources deep instead of one.** Cameroon, Senegal, Guinea, Gambia,
   Burkina Faso, Niger, Mali, Benin and Chad, plus DR Congo table by table.

And one thing to say to Adrian that round one could not. The answer to *"can we go to source?"*
in this region is no longer "in one country out of twenty-four". Twenty-three national databases
are still shut. But nine of those countries print the contents of the database as a report, one
prints part of it, and the money that the shut databases would not have carried anyway is
published for eighteen of them in a single spreadsheet. The going-to-source work here is still
mostly institutional. It is much less of it than round one thought.

---

# Round three — the datasets that never say "HIV"

*Added 2026-08-17, after a third pass. Round two closed by saying that every region gets two
passes. Three is the honest number, and this round says why.*

Round three found two large sources, overturned the grade this log gave Nigeria, and widened a
connector the pipeline already had to twice its coverage. None of it came from looking harder in
the ordinary sense. It came from one habit that all of the previous searching shared.

## The rule that was wrong: every earlier round searched for the word HIV

Round one searched national AIDS programmes. Round two searched the source classes round one had
never opened. Both keyed on HIV: the word, its French forms *VIH* and *SIDA*, DAC purpose code
13040, and catalogue entries with HIV in the title. That is the right key for a source about HIV.
It is the wrong key for a source that carries HIV as a handful of columns inside a collection
about something else, and such a source stays invisible at three separate points — the search
that never runs, the catalogue query that returns nothing, and the judgment that a tuberculosis
dataset is about tuberculosis.

**Search the general health collections for whatever HIV columns they happen to carry.** Two of
them hold measurements that exist nowhere else in the panel.

The same failure happens inside a single site. Chad's statistics office serves a search endpoint
that matches on title text: `q=sante` returns nothing and `q=VIH` returns nothing, while ten
health statistics yearbooks sit in the catalogue under the string `SANITAIRES`. Querying a
catalogue with the topic word under-finds its contents.

## WHO TME — a tuberculosis dataset carrying the panel's only treatment flow

`https://extranet.who.int/tme/generateCSV.asp?ds={dataset}`, open, no key, no login. The
dictionary is itself one of the datasets: 698 variables across 19 collections, of which **100 are
HIV-related, spread over nine datasets**.

The valuable columns are not TB measurements. National tuberculosis programmes report the total
number of people on ART (`hiv_all`) and the number who started ART in the last 12 months
(`hiv_reg_new2`), because they need those denominators to compute TB preventive treatment
coverage. That is a reporting channel separate from both UNAIDS GAM and WHO GHO.

- **It is independent, not a republication.** `hiv_all` against the panel's UNAIDS on-ART series,
  180 shared country-years: within one per cent in 32 per cent of them, **more than a tenth apart
  in 28 per cent**, median gap 2.2 per cent.
- **It carries the flow the panel never had.** The panel is almost entirely stocks, and a stock is
  the wrong instrument for a funding cut, because people already on treatment stay on it for a
  while after the money stops. `hiv_reg_new2` is ART initiations: 998 rows, 2013–2024, 153
  countries, and **all 24 WCA countries**. DR Congo runs 107,468 (2020), 96,516, 97,177, 83,436,
  **65,651 (2024)** with no gap in the series. Cameroon 75,954 (2021) to 38,059 (2024); Côte
  d'Ivoire 40,703 (2020), 32,114 (2022), 26,765 (2024).
- **Read those trajectories only where consecutive years are present.** The series is ragged.
  Guinea reports 61,197 in 2020 and 7,884 in 2024 with nothing in between, and that is a reporting
  gap wearing the shape of a collapse. DR Congo is the one WCA country reporting every year.
- **`hiv_new` is the same measurement under a second name** — identical in 94 per cent of the 235
  country-years carrying both. It is mapped as a gap-filler only, adding exactly 39 country-years,
  with the column it came from stamped on every row.
- **The cut is in the file, measured directly.** Expected USAID funding to national TB programmes
  totals 134,747,052 USD in 2018, climbs to 235,509,731 in 2024, and falls to **98,701,987 in
  2025**, with the count of countries expecting anything falling from 31 to 23. The budget file
  reaches 2025; the expenditure file stops at 2024, so the cut appears first as a plan and not yet
  as an outturn.
- **The TB funding columns are exposure, not HIV money.** `cf_tot_usaid` and its siblings are the
  whole TB programme's budget. They are mapped under `tb_funding_*` ids and anything totalling HIV
  financing has to exclude every one of them.

The connector emits 23,705 rows over 20 mapped columns, 215 countries, 2000–2025, no duplicate
panel keys. It does not join the pre-2015 cascade columns to the post-2015 ones: `hivtest` and its
siblings counted all TB patients and were retired in 2014, `newrel_hivtest` counts new and relapse
cases only, and mapping both onto one id would put a definition change in the middle of every
series and read as a jump in 2015.

## WHO GHED — the domestic money, for every country

`https://apps.who.int/nha/database/Home/IndicatorsDownload/en`, one 38.9 MB workbook, open.
Global Health Expenditure Database, and its disease split carries HIV. It occupies the same cell
as the UNAIDS GAM expenditure workbook found in round two and has to be classified against it
carefully: it is **independent**, not derived, because it is built from national health accounts
and not from the GAM submission.

Two things to handle when it is built (task #20). `dis11` splits into `_gghed`, `_ext` and
`_pvtd` — government, external and private — which is the same donor-versus-domestic question §7f
of the ladder identified, answered by a second instrument. And `dis11_usd` is in **millions** of
US dollars while everything around it is not, which is trap one waiting to happen.

## WHO GHO — the catalogue was one seventh read

The GHO catalogue holds 3,089 indicators, of which 62 are HIV-related. The pipeline mapped seven.
It now maps 14 series, and the assessment decided each candidate on its values and not on its
name.

- **Reported ART (`HIV_0000000009`) is not the modelled series republished.** Against the panel's
  UNAIDS figures, 2,030 shared country-years: identical in one per cent, within one per cent in 52
  per cent, more than a tenth apart in 13 per cent. It also reaches **1,766 country-years the panel
  held no ART figure for at all**, 170 of them 2023 or later.
- **It un-censors UNAIDS from outside.** Maldives is `<100` in AIDSinfo for its whole series and
  2, 3, 5, 6, 8, 10, 12 people in GHO. That is external confirmation of what the censoring fix
  assumed: the suppressed epidemiological cells are small true numbers and not missing data.
- **Testing volume and positivity are instruments the panel did not have.** 936 rows, 143
  countries, 2022–2024, 19 of the 24 WCA countries. Nigeria performed 12,390,356 tests in 2022 at
  2.38 per cent positivity all ages, 2.17 among women 15+, 3.31 among men 15+, 0.92 under 15.
- **The testing splits partition the total.** Women 15+, men 15+ and under-15 sum to the all-ages
  figure exactly in 82 per cent of country-years, so the same rule the agency split already has
  applies here: one level or the other, never both.
- **Dropped, each on evidence:** testing facilities (2014 only), condoms distributed (empty
  response), prison diagnoses (no WCA country), and the whole TB/HIV block, which is WHO TME
  republished and belongs to the TME connector.

Two live defects surfaced while widening it, both of which would have corrupted the panel
silently: the age dimension was being discarded, and the sex map knew `BTSX` while these series
return `SEX_BTSX`. The original seven series carry no sex dimension, so the map had never once
been exercised in production.

## Nigeria — the round's largest overturn

Round two graded Nigeria **3.5, published to a human and not to a machine**, on the evidence that
the Power BI wallboard's query backend returns 403 to every scripted request. That grade was
wrong, and it was wrong in the direction that matters: it understated what the national programme
publishes.

The National Data Repository has an **open JSON API**. Three endpoints answer:
`ndr.nascp.gov.ng/public/GetRecencyData/` (state-level recency yield with numerators,
denominators, age bands and RITA, plus a monthly viral-load series from March 2020),
`ctd.nascp.gov.ng/facilitydata/` (all 37 states with `txcurr`, `pl_estimate` and `tx_coverage`,
dated December 2025), and `ndr.nascp.gov.ng/public/surveillance-report` (28 monthly national
reports).

**A `Referer` header is the whole gate.** Plain `curl` returns HTTP 000; the same request with
`--http1.1`, a browser user agent, `Referer: https://ndr.nascp.gov.ng/public/wallboard` and
`X-Requested-With: XMLHttpRequest` returns the data. This is the round-two method — read the
application and not the page — applied to a host that round two had already judged and closed.
**A source graded once is not graded forever**, and the 403 that produced grade 3.5 was one path
into a system with three open ones.

National treatment stands at **1,672,219 on treatment against 1,904,364 PLHIV**, 87.8 per cent,
December 2025. GHO's reported ART for Nigeria 2025 is 1,550,000: about eight per cent apart, two
instruments that do not share an origin, so `reconcile.py` has to classify them independent.

The state table carries a trap of its own, and the source ships the fix. State TX_CURR exceeds
the state PLHIV estimate in several states — **Bauchi 158 per cent, Adamawa 121, Benue 115** —
because patients are counted where they are treated and not where they live. The residence matrix
(`txcurr_res_state`, `txcurr_res_outof_state`) is what corrects it. A state coverage figure
computed without it is wrong, and the connector either loads the matrix or refuses to publish a
state coverage number. Task #23.

## Negative findings, so nobody researches them twice

- **WAHO** (`waho.dhis2.org`), the West African Health Organisation's regional DHIS2, is the sixth
  gated DHIS2 in this project. All five unauthenticated probes redirect 302 to the login page.
- **WHO AFRO is confirmed dead, not merely moved.** `aho.afro.who.int` returns 404 at every path.
  The African Health Observatory's country atlases survive as 2022 PDFs, and those republish GHO
  and UNAIDS figures the pipeline already holds. The class is closed.
- **Chad's INSEED is alive and round two was right about it.** The catalogue holds 135
  publications in 15 series, including ten editions of the health statistics yearbook, most
  recently `ANNUAIRE-STATISTIQUES-SANITAIRES-2023`. It is the searching that misleads, not the
  site: see the note on `q=sante` above.

## What round three changes

Round two's ranked list stands unchanged. Three things join it, and one moves.

9.  **WHO TME**, built. The only ART flow measurement in the panel, an independent ART stock, and
    a direct USAID budget series that already shows the 2025 fall.
10. **WHO GHED** (task #20). The second independent instrument on domestic HIV spending.
11. **Nigeria NDR** (task #23). Moved out of grade 3.5 and into grade 1: an open API, state-level,
    current to December 2025, for the largest epidemic in the region.

And the thing to say to Adrian that round two could not. The answer to *"can we go to source?"*
for Nigeria is now yes, by machine, at state level. That is the country this log opened by
recording as the hardest in the region.
