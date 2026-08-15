# Going to source: what national HIV programme data is actually reachable

*A methods note consolidating the Southeast Asia phase, written 2026-08-02.*

Adrian's question at the start of Phase 2 was whether we could realistically go to source with
country-level programme data, country by country, instead of taking every number from an
aggregator. Nine Southeast Asian countries were worked through one at a time to answer it. The
answer is yes for some and no for others, and the interesting part is that the split does not
fall where anyone expected. This note sets out the finding, the taxonomy it produced, and the
one prediction it makes that the next region can test.

The per-country evidence lives in [`PHASE2_FEASIBILITY.md`](PHASE2_FEASIBILITY.md) for Southeast
Asia and [`PHASE3_FEASIBILITY_AFRICA.md`](PHASE3_FEASIBILITY_AFRICA.md) for sub-Saharan Africa.
This note is the argument built on top of them.

---

## 1. The finding

**Every one of the nine countries has a national HIV programme database.** Thailand has the NAP
system behind the HIV Info Hub, Vietnam HIV INFO 4.0, Indonesia SIHA, Malaysia MyHDW, the
Philippines HARP, Laos HIVCAM, Cambodia the NCHADS reporting system, Myanmar the National AIDS
Programme M&E system, and Timor-Leste a DHIS2 instance stood up in 2023. Case-based
surveillance is close to universal in the region.

So the barrier is not that the data does not exist. Data existence was the hypothesis worth
ruling out first and it is ruled out. The barrier is access, and access is not binary.

## 2. The access ladder

Sorting the nine by how their data actually comes out produces four grades. The first three
came out of Southeast Asia; the fourth came out of starting on Africa and is set out in §4.

**Grade 1 — an open structured feed.** The national system exposes a queryable endpoint that
returns machine-readable values. Thailand's Data Mart is the only case in the region: a JSON
endpoint over the NAP/NHSO indicators, versioned, and stable enough to build against. One
country in nine.

**Grade 2 — an open born-digital report.** No endpoint, but the national programme publishes a
report whose tables are laid out as text and can be extracted deterministically, with integrity
checks against the row and column totals the report prints. Cambodia's quarterly Boosted CoPCT
report and the Philippine DOH quarterly surveillance report are both grade 2. Two countries in
nine.

**Grade 3 — a gated database.** The system exists and is not public. What comes out is either a
scanned PDF, which we do not OCR because an OCR error in a count is invisible and
unfalsifiable, or a feed to an aggregator we already ingest. Six countries in nine.

The grades are about the *release mechanism*, not the *file format*, and that distinction did
real work. Malaysia looks like a grade-2 candidate: the Ministry of Health publishes a national
report, born-digital, with tables. Building a connector for it would have added nothing,
because that report *is* the country's Global AIDS Monitoring submission, which is to say the
exact UNAIDS feed already in the panel. The test that matters is not "can this be parsed" but
"does this carry anything the aggregator does not" — sub-national detail, a shorter lag,
key-population breakdowns, or programme flows. The Philippine report passes that test and
Malaysia's does not.

## 3. What this says about the original question

Going to source is realistic country by country wherever the data is both open and additive. It
is not a regional method, and a project that budgeted for one connector per country and
expected them to look alike would have been wrong about seven of the nine.

The distribution is itself a result worth reporting. Open structured national HIV data is the
exception in Southeast Asia, at one country in nine, and the modal country holds a working
national cascade database that no external researcher can read. For those six the route is an
institutional data-sharing agreement through academic or PEPFAR channels, which is a different
kind of work from writing a connector and runs on a different timescale. Saying so early is more
useful than discovering it per country.

There is a second-order point for anyone reading a cross-country HIV panel. The countries whose
national data is reachable are not a random sample of the region. Thailand, Cambodia and the
Philippines are reachable partly because their programmes are comparatively well resourced and
politically stable, and Myanmar is unreachable partly because of the 2021 coup. Data access
correlates with the health-system conditions under study, so a panel assembled only from
grade-1 and grade-2 countries is selected on something close to the outcome. This is a reason
to carry the aggregator series alongside the to-source series, which the panel does, and to
report source type on every row, which the schema does.

## 4. Grade 4 — the donor side, and the prediction it makes

Southeast Asia produced three grades because all three are country-side routes: they ask what
the country publishes about itself. There is a fourth, and it became obvious only on turning to
Africa.

**Grade 4 — donor-side programme reporting.** Where a country's own system is gated, the donor
that paid for the services may still publish them. PEPFAR's MER data is the case: quarterly,
sub-national to facility level, disaggregated by age and sex, covering 59 operating units, and
released at the grain of the individual implementing partner and the US agency funding it.

This is not a substitute for national data and must not be described as one. It measures the
PEPFAR programme footprint and not the national programme, so it undercounts wherever a country
funds services outside PEPFAR, and its coverage is a function of where PEPFAR chose to work. The
panel tags it `routine_programme_record` and every row carries a note saying so.

But for the specific question this project asks — what happened when the funding was cut — the
donor side is not a second-best source. It is the better one, because it carries the funder as
a column and the national systems do not. See §5.

The prediction the ladder makes is testable: **a region with heavier donor dependence should have
a lower country-side grade distribution and a much richer grade-4 layer.** Sub-Saharan Africa is
more PEPFAR-dependent than Southeast Asia, and the grade-4 layer is enormous there where
Southeast Asia's is thin — Kenya alone has 16,109 rows in the PEPFAR MER top-line file against
Cambodia's 2 and Thailand's 468. The country-side half is tested in §4a.

## 4a. The African country side, widened

The first version of this note stated the African pattern off three countries. That was too thin
to carry it, so the probe was widened to 62 candidate endpoints (58 national, 4 regional) across
19 countries on 2026-08-03. The per-endpoint evidence is in
[`PHASE3_FEASIBILITY_AFRICA.md`](PHASE3_FEASIBILITY_AFRICA.md). Three things came out of it.

**The first half of the prediction holds.** Six countries return a login wall from a national
health information system that is plainly working: Tanzania, Ethiopia, Uganda, Malawi, Kenya and
Nigeria. The system answers, names itself, and refuses. DHIS2's `/api/system/info.json` returned
the login application and not JSON on every national instance probed, so the API is
authenticated along with the interface and there is no side door. Against nineteen countries,
one country-side source is open, structured and additive: South Africa's Thembisa, at grade 1.
One in nineteen against Southeast Asia's one in nine — lower, as predicted, though the two
regions were probed to different depths and the ratio should not be read as if they were.

**Africa produced a barrier class Southeast Asia did not.** Twelve endpoints failed TLS
certificate verification; retried with verification off, nine served ordinary content, including
Kenya's KHIS Aggregate, Kenya's Ministry of Health, Tanzania's TACAIDS, Zambia's ministry and
HMIS, Zimbabwe's HMIS, Mozambique's MISAU, Lesotho's ministry, and the PHIA data manager. These
hosts are alive and gated, not dead. We do not disable verification to collect them: an
unverified channel gives no way to attest that what arrived is what the ministry published, and
the panel's provenance fields would then be recording something we cannot stand behind. They
stay out, and the recorded reason is "TLS chain not verifiable", which is a different problem
from a login wall and would not be fixed by a data-sharing agreement.

**One earlier claim in this note was wrong and is corrected.** It read "Kenya's national DHIS2
host does not resolve". `hiskenya.org` resolves, serves KHIS Aggregate, and redirects to
`/dhis-web-commons/security/login.action`; the original failure was certificate verification.
The conclusion — gated — was right for the wrong reason, and a wrong reason in the record is
worse than a gap in it. Malawi's ministry site returns 403 at the edge and not a server
error; its HMIS is the thing that shows a login.

So the practical guidance inverts by region, as the ladder said it would: **country-side first in
Southeast Asia, donor-side first in Africa** — with South Africa the one country where both
doors are open, and Rwanda the one national HMIS in the probe that did not immediately refuse.

## 5. Why the funder column is the whole point

The country total hides the event. US HIV funding was not withdrawn uniformly across agencies:
USAID was dismantled through 2025 while HHS/CDC continued. Both fund treatment in the same
countries, so a country total sums an arm that was cut with an arm that was not.

Kenya, people on ART, FY2024 to FY2025, from the PEPFAR MER file:

| | FY2024 | FY2025 | change |
|---|---|---|---|
| USAID-funded partners | 472,520 | 413,032 | **−12.6%** |
| HHS/CDC-funded partners | 797,595 | 844,340 | +5.9% |
| other US agencies | 66,185 | 67,080 | +1.4% |
| **country total** | 1,336,300 | 1,324,452 | −0.9% |

Zambia shows the same shape: USAID −14.7%, CDC +4.8%, total −3.9%. A reader of Kenya's country
total sees a programme holding steady to within a percent. The split shows one arm losing
roughly sixty thousand people there.

Two caveats, both handled in code and carried on every row.

*The quarter.* TX_CURR is a point-in-time snapshot, so its annual value is the latest quarter
reported and not a sum. FY2025 publishes one quarter of four, which raises the obvious worry
that the two years are read off different points in the calendar. They are not — FY2025's single
quarter is Q4, the same quarter FY2024's snapshot comes from, so the comparison is twelve months
apart. That is a fact about this download and not a guarantee of the format, so both connectors
now record `snapshot_quarter` on every snapshot row and warn when consecutive years are read off
different quarters.

*Transfer.* CDC is a strong within-country control: same year, same epidemic, same indicator
definition, same reporting calendar. It does not control for a patient moving from a
USAID-funded clinic to a CDC-funded one, which subtracts from one series and adds to the other
and imitates loss exactly. Kenya's figures do not net out — USAID falls 59,488 while CDC rises
46,745 — but that is a reason to look further and not a finding by itself. Every row carries an
`interpretation` note saying so, because the divergence is evidence and not yet a conclusion.

## 5a. The same column also catches a cut that did not happen

The funder column was added to see a cut the country total hides. On the third source it was
applied to, ForeignAssistance.gov, it did the opposite job and that is the more instructive
result.

ForeignAssistance.gov carries two agency columns. **Funding agency** records which
appropriation the money came out of, and because PEPFAR is appropriated to the State
Department's Global Health Programs account it puts 102bn USD under State and separates
nothing. **Managing agency** records who spent it, and that is the column that reproduces the
USAID/CDC split: USAID 72bn against HHS 43bn, of which CDC is 38.5bn once the sub-agency column
takes out NIH and HRSA. Choosing between them is most of the work in this connector.

HIV-labelled disbursements, FY2024 to FY2025, current USD millions:

| | FY2024 | FY2025 | change |
|---|---|---|---|
| managed by USAID | 2,037.0 | 1,379.2 | **−32.3%** |
| managed by HHS/CDC | 1,510.2 | 1,356.8 | −10.2% |
| managed by the State Department | 6.4 | 270.7 | — |
| other US agencies | 105.8 | 77.9 | −26.4% |
| **country total** | 3,659.4 | 3,084.6 | −15.7% |

The State line is the finding. The Bureau of Global Health Security and Diplomacy absorbed
USAID's global health programmes in 2025, and it disbursed nothing at all before FY2025, so a
State-managed HIV series that was 6m in FY2024 and 271m in FY2025 is not new money. It is the
same programmes under a new manager. Part of what left USAID did not leave the US government.

Zimbabwe is the clean case: USAID −40.9m, State +47.6m, country total up 3.9%. Kenya USAID
−55.2m against State +16.5m; Mozambique −110.4m against +41.4m; Zambia −83.5m against +37.2m.
Read the USAID series alone and the cut is overstated in every one of them. Read the country
total alone and it disappears. Only the split shows both halves, which is why State is carried
as its own series here and is not pooled into "other agencies" the way the PEPFAR expenditure
connector pools it.

The two files disagree, and the disagreement is worth keeping. PEPFAR's own expenditure
reporting still labels its agencies USAID, HHS/CDC and a handful of State bureaux, with no
GHSD line at all through FY2025. The reclassification is invisible in PEPFAR's accounting and
visible in Washington's. Where they differ, ForeignAssistance.gov is the one recording where
the money went.

The general point is the one §6 makes about aggregation, turned round. A column dropped in
aggregation does not only hide falls. It also manufactures them, and an analysis that reported
USAID's 32% fall as the size of the 2025 cut would have been wrong in the direction that
confirms what everyone expects — which is the direction that gets published.

## 5b. What only the all-country run could show

Everything above was built and checked on the nine Southeast Asian countries. Running the same
pipeline over every country it can reach, on 2026-08-03, produced two errors that the pilot
slice was structurally incapable of showing.

The first: the United Kingdom came out as the largest recipient of US HIV aid in the world,
59.9bn USD cumulative, with North Macedonia second at 12.0bn. Neither receives any. OECD CRS
keys country recipients by ISO3 and regional aggregates — "Africa, regional", "Bilateral,
unspecified" — by mnemonics, and the connector resolved both through a name-matching function
whose last resort is `pycountry`'s fuzzy search. That search also matches *subdivision* names
and always returns its best guess, so a three-letter aggregate code that happens to spell a
district of England is answered with the United Kingdom, and one that spells a municipality of
North Macedonia is answered with North Macedonia. 344 rows carried a region's money under a
country's name.

The pilot could not have caught this: a nine-country query names its recipients, so no
aggregate is ever returned. Nor did the validator catch it on its own terms — the duplicate
check fired only because a real GBR row already existed for the same year and the collision
showed. An aggregate that had landed on a country with no CRS row of its own would have passed
validation in silence and been read as that country's aid.

The second is a gap, not a contamination. ForeignAssistance.gov calls Myanmar "Burma
(Myanmar)", which matched nothing, so the US self-reported series had no Myanmar in it at all —
for one of the nine pilot countries, through every SEA run. The file holds 111.8m USD of US HIV
disbursements to Myanmar across 2006–2025, and none of it reached the panel; the OECD series
carried its 59 Myanmar rows the whole time, so what the panel showed was one source reporting
US aid to Myanmar and the other reporting none, which reads as a disagreement between sources
instead of an unmatched string. China, at 69.0m across 2003–2018, was missing the same way.

Both have the same shape: a country identifier that resolves to the wrong thing, or to nothing,
without anything failing. Codes now resolve strictly — a code is a country only if it *is* an
ISO3 country, and skipped codes are counted and named in the log — and the fuzzy pass on names
now has to find the matched country's own name inside the query before it is believed. The
spellings that only worked by fuzzy luck (Russia, Brunei, Curaçao, Kosovo) are written down
instead, and Curaçao is no longer filed under the Netherlands, nor Kosovo under Serbia.

The re-run on 2026-08-03 confirmed the fix and immediately earned the log line twice over. OECD
CRS skipped 60 distinct aggregate codes across the three donor series, and exactly one entry in
that list was a real recipient: `XKV`, which is how CRS codes Kosovo and which the World Bank
codes `XKX`. Left alone, the same place would have sat in the panel as two countries. And the
list itself showed the third instance of the error, in a connector nobody had suspected: World
Bank aggregates carry three-letter alphabetic codes of their own — `WLD` is the world, `SSA`
Sub-Saharan Africa, `LDC` the least-developed countries — and that connector was testing the
*shape* of the code instead of asking whether it was a country. 44 of them had entered the
panel as countries, the world's own population among them, which is why the run reported 267
countries covered. The same strict resolution now runs there.

The lesson generalises past this pipeline: every aggregator publishes totals in the same column
as its units, and the identifier is the only thing separating them. Any code that is not
confirmed to be a country has to be refused and named, because an aggregate admitted as a
country does not fail — it publishes.

## 5c. What only the sub-national layer could show

PEPFAR's Enhanced Geographical Analysis file goes three levels below the country, quarterly,
2016–2025. No aggregator in this pipeline publishes anything below the country, so this is the
only place a cut can be watched land unevenly inside one — 26 countries with real sub-national
detail, Kenya's 47 counties, Nigeria's 37 states, Vietnam's 34 provinces. The file covers 61
countries, and 35 of them publish a single "sub-national unit" that is the country itself.
Those are dropped: they are national figures wearing a province's label. Two of the 61 are
easy to lose — Bahamas and Belize sit under regional operating units ("Caribbean Region",
"Central and South America Region") with the ISO3 column blank, and are recoverable only from
the country name.

Building it exposed an error in the two national connectors that had been in the published
panel since July. TX_CURR is a snapshot, so its annual value is the latest reported quarter and
never a sum — but "latest reported quarter" was being applied to each partner separately and
the results added together. That produces a total belonging to no date. Nigeria's provinces
showed it first: 33 states reached Q4 of FY2024 and two stopped at Q3, and reading each at its
own last quarter gave 1,577,095 against a national 1,537,786.

The national version of the same error is larger, because at country level the unit that stops
reporting is a funding mechanism and a mechanism that stops usually has not stopped operating —
it has changed hands. Zimbabwe FY2024: UNIVERSITY OF WASHINGTON reported Q1 (539,106 on ART)
and then handed mechanism 70465 to Zim - TTECH, which reported Q2–Q4. Both were counted, and
Zimbabwe's `on_art_count` came out at 1,753,641 against a Q4 figure of 1,214,535 — 44% too
high, by exactly the size of the transferred cohort. The published series read 1,215,211 →
1,753,641 → 1,211,326 across FY2023–25, a spike and a collapse where the programme was flat.

61 of 821 country-years were affected, every one of them a snapshot indicator and every one of
them inflated. The correction is exact in a way worth stating: for all 821 country-years and
all 1,408 agency-years, the change equals the total the absent mechanisms last reported, to the
person. Nothing else moved, and the cumulative indicators are untouched, since summing quarters
and summing partners commute.

The fix is one quarter per country-indicator-year, the latest any unit reaches, with every unit
read at that quarter. A unit absent from it is left out of the year and its last figure is
recorded in `extra.partners_absent` instead of being carried forward. That matters for what the
panel is for: a partner that stops reporting is the event this project is trying to see, and it
should look like an absence, not like a programme still running.

Two things generalise. The first is that a snapshot has to be collapsed once, at the level it
will be read at, and never collapsed per part and then added — the parts are dated
independently. The second is that the unit of reporting was not what it looked like. Keying the
partner detail by partner name missed a third of the affected rows, because 530 partner names
in this download run more than one mechanism inside a single country-indicator-year; the
mechanism code is the identity, and a handover is invisible without it.

### What the two downloads still disagree about

The correction can be checked against a file it never touches. The partner file and the
geographic file are separate downloads with separate structures, and after the fix they agree
within 2% on 195 of 208 shared country-years, up from 165 before it. Five are still more than
10% apart: Namibia 2019–22 and Vietnam 2019–20.

Namibia is the one worth reading. The partner file puts 298,637 people on ART in FY2022; the
geographic file says 200,190 and UNAIDS' national estimate is 190,000. Two CDC mechanisms
report the country — the Ministry of Health and Social Services at 199,165, and University of
Washington at 96,537. The Ministry's figure is the national programme, and the second sits on
top of it, which is how a country ends up with 57% more people on treatment than it has. The
geographic file has no mechanism column at all: it is one row per district, so a patient two
mechanisms both support is still counted once. Nothing inside the partner file separates an
overlapping mechanism from an additional one, so this cannot be corrected from that file alone
— it only becomes visible by holding the two downloads against each other. Where they disagree,
the geographic total is the safer one.

Vietnam runs the other way, and is not the same problem. The partner file is around half the
UNAIDS national total in every year, which is what partial coverage looks like: PEPFAR supports
a minority of the Vietnamese programme, most of which is carried domestically.

## 6. What this cost, and what it means for the next region

The Southeast Asian phase produced four connectors from nine countries and took the bulk of
Phase 2. Grade 4 for Africa needed no new download and no new source: the funding-agency and
partner columns were already present in the MER file the pipeline had been reading since July,
and the existing connector summed them away to reach a country total. Recovering them was one
new connector over a file already on disk.

The lesson generalises past this project. Before going looking for a new source, check what the
sources already ingested are being asked for and what they are being asked to throw away. The
aggregation step is where information goes missing, and it goes missing silently.

---

## Status of the claims here

| Claim | Basis |
|---|---|
| All 9 SEA countries have a national cascade database | Per-country desk research, [`PHASE2_FEASIBILITY.md`](PHASE2_FEASIBILITY.md) |
| Grade distribution 1 / 2 / 6 | Same; each access attempt logged with date and outcome |
| Malaysia's national report = its GAM submission | Re-tested 2026-07-19 |
| Kenya / Zambia agency divergence | `Public_Partner_MER_TopLine`, computed 2026-08-02 |
| FY2025 snapshot is Q4 | Checked per country and agency before the divergence was reported |
| Agency series partition the country total | 72 country-indicator-years checked, 0 mismatches |
| FA.gov: managing agency is the separating column, funding agency is not | Both columns totalled over the full file; funding agency puts 102bn under State |
| FA.gov State-managed HIV disbursements 6.4m (FY2024) → 270.7m (FY2025) | Computed 2026-08-03; sub-agency column attributes essentially all of it to GHSD |
| The four FA.gov agency series partition the US country total | All 1,886 country-years checked, 0 mismatches; totals unchanged from before the split |
| OECD CRS aggregates were resolving to GBR and MKD | Panel of 2026-08-03: 272 GBR rows and 104 MKD rows from `oecd_crs`, 344 flagged as duplicates; GBR 59.9bn cumulative on a series it receives nothing from |
| The fuzzy pass matches subdivisions, not just countries | Enumerated: 47 two-letter and 313 three-letter strings resolve to GBR, 6 and 61 to MKD, none of them country codes |
| The mapping fix changes nothing that was already right | All 249 ISO country names (plus official and common variants), 194 UNAIDS labels, 33 PEPFAR operating units, 34 MOU labels and 253 FA.gov labels re-resolved: 0 changes except the four that were wrong |
| FA.gov had no Myanmar and no China | Its labels are "Burma (Myanmar)" and "China (P.R.C.)"; 0 rows for either in the 2026-08-03 panel, against 111.8m USD (2006–2025) and 69.0m USD (2003–2018) of HIV disbursements in the file itself |
| 44 World Bank aggregates were in the panel as countries | Panel of 2026-08-03: `WLD`, `SSA`, `LDC`, `EUU` and 40 others, 1,745 rows, all from `world_bank`; 267 "countries covered", of which 223 are countries |
| Kosovo is coded `XKV` by OECD CRS and `XKX` by the World Bank | The re-run's skipped-code log: `XKV(16)` in two of three CRS series, the only real recipient among 60 refused codes |
| Strict resolution refuses aggregates and keeps countries | All 249 ISO3 codes pass through unchanged; all 60 CRS and all 44 World Bank aggregate codes refused |
| PEPFAR publishes admin1 detail for 26 countries | `Enhanced_Geographical_Analysis`, run 2026-08-04: 61 countries, 35 of which publish only a country-wide "SNU"; 388 real units, 14,517 rows emitted |
| Two countries carry no ISO3 in that file | Bahamas and Belize appear under "Caribbean Region" and "Central and South America Region" with `ISO3` blank; 31 rows, recoverable only from the country name |
| Summing over modality and over ragged SNU depth does not double-count | Checked before any row was emitted: blank modality is how 2016–17 reported (named modalities zero) and named modalities are how 2018+ reports (blank zero), the two overlapping in 49 unit-years of 2025 worth 0.13% of the total; and 0 SNU2 groups carry a value on both the SNU3-named and SNU3-blank side |
| PEPFAR has no agency × province anywhere | Every geographic and partner file in the catalogue checked 2026-08-04: agency appears only in the partner files, which stop at the country |
| The snapshot indicators were inflated by mixed-quarter summation | 61 of 821 country-years in the panel of 2026-08-03, all `on_art_count`, all inflated; ZWE FY2024 1,753,641 against a Q4 figure of 1,214,535 |
| The correction removes exactly the mechanisms that stopped reporting | All 821 country-years and all 1,408 agency-years: old − new equals the absent mechanisms' last reported total, worst gap 0 |
| The agency series still partition the country total after the fix | All 821 country-years re-checked, 0 mismatches |
| The reporting unit is the mechanism, not the partner | 530 partner names run more than one mechanism inside a country-indicator-year; keying the detail by name left 21 of the 61 changed rows unexplained |
| The fix moves the two downloads into agreement | Partner file against geographic file, 208 shared country-years: within 2% on 195, up from 165; more than 10% apart on 5, down from 26 |
| Namibia's partner-file total double-counts a supported cohort | FY2022: partner file 298,637, geographic file 200,190, UNAIDS 190,000; two CDC mechanisms report the country, MoHSS at 199,165 and University of Washington at 96,537 |
| Vietnam's gap is coverage, not double counting | Partner file is 45–59% of the UNAIDS national total across 2019–24, short in the same direction every year |
| Six sub-national viral-suppression ratios exceed 100% | TZA Singida 2018 109.2%, VNM Binh Duong 2017 108.4%, DOM Region 1 2022 106.6%, BWA Southern 2017 105.4%, NAM Oshana 2017 104.1%, TZA Dodoma 2018 103.5%; kept as published, flagged in `extra.data_quality_flag`, not clipped |
| PEPFAR's provincial totals sit under Thembisa's everywhere in South Africa | 90 province-years, 2016–2025: 84.4–91.7% of the modelled provincial ART total by year, 0 of 90 above 100% |
| African country-side portals gated | Probed 2026-08-03: 62 endpoints, 19 countries. Login wall observed at 6 (KEN, TZA, UGA, MWI, ETH, NGA); 12 TLS-unverifiable; 15 inconclusive (guessed hostname or edge 403) |
| One open country-side source in Africa | South Africa (Thembisa), connector built and value-checked against the workbook |
| Provinces do not sum to South Africa's national total | Stated in the workbook's Notes sheet; measured on the panel (PLHIV 2022 +0.45%, on-ART 2022 −0.63%) |
| West and Central Africa | **Not established.** Probed thinly; needs the desk research Southeast Asia got |
