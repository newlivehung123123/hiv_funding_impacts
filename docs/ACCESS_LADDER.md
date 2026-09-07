# Going to source: what national HIV programme data is actually reachable

*A methods note consolidating the Southeast Asia phase, written 2026-08-02.*

Adrian's question at the start of Phase 2 was whether we could realistically go to source with
country-level programme data, country by country, instead of taking every number from an
aggregator. Nine Southeast Asian countries were worked through one at a time to answer it. The
answer is yes for some and no for others, and the interesting part is that the split does not
fall where anyone expected. This note sets out the finding, the taxonomy it produced, and the
one prediction it makes that the next region can test.

The per-country evidence lives in [`PHASE2_FEASIBILITY.md`](PHASE2_FEASIBILITY.md) for Southeast
Asia, [`PHASE3_FEASIBILITY_AFRICA.md`](PHASE3_FEASIBILITY_AFRICA.md) for sub-Saharan Africa, and
[`PHASE4_FEASIBILITY_WCA.md`](PHASE4_FEASIBILITY_WCA.md) for West and Central Africa. This note
is the argument built on top of them.

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

## 4b. West and Central Africa, and the grade the ladder was missing

§4a left the region that had only been probed, not researched. Twenty-four countries were then
worked through to the Phase 2 standard; the evidence is in
[`PHASE4_FEASIBILITY_WCA.md`](PHASE4_FEASIBILITY_WCA.md). The country-side result is the
prediction's third confirmation and the strongest one: **no national source in the region reached
grade 1**. Nigeria's National Data Repository is behind a login and, since NACA's April 2026
statement directing all requests to the agency, behind a policy as well; DR Congo's VIH DATAPRO
is a registration wall over an expired strategic plan's indicators; Côte d'Ivoire's PNLS
publishes Spectrum output, which fails the Malaysia test on sight, and the ministry's open RASS
yearbook series stops at 2020.

One country-side source reaches grade 2 and passes the additive test, and it makes a point the
first three regions did not. **Cameroon's CNLS annual report** is open, born-digital, and carries
the ten regions on the ART cascade, viral-load coverage and suppression, retention, PMTCT and
testing; key populations as programme counts with linkage rates, not as modelled
prevalence; and 2024 funding broken down by donor with execution against budget. Its source line
says where all of that comes from: *2024 DHIS2 database (26/03/2025)*. Cameroon's national HIV
database is the same DHIS2 that returned a login wall in six countries in §4a — and the ministry
publishes an extract of it as a public report. So a login wall is a barrier to the *database* and
not necessarily to the *data*, which is worth re-checking in Kenya, Tanzania, Uganda, Malawi,
Ethiopia and Nigeria before any of them is written off. The grade-3 verdict in those six was
recorded against the system, and the question of what the ministry publishes out of it was never
asked.

The Cameroon file also earns a methods line. An automated read of the PDF reported it as scanned
images with no extractable tables, which would have ended the enquiry at grade 3. Opening it
showed a full text layer and every table extracting cleanly. A tool's summary of a document is
not evidence about the document.

The ladder's own logic then produced something it had not anticipated. Grade 4 was defined as
donor-side reporting, and PEPFAR was taken as the case. But half the countries in this region —
twelve of twenty-four, holding 632,800 people living with HIV — have no PEPFAR rows at all, so
the grade-4 escape hatch is shut exactly where the country-side door is shut hardest. What opens
instead is a layer the ladder had no name for: **regional publication, open and structured, by
the bodies that sit above the country**.

- **UNAIDS Naomi** publishes sub-national estimates for 15 of the region's 24 countries through
  an open JSON API on `nmviewerserver.azurewebsites.net`, with credible intervals on every value
  and area detail to level 3. Seven of those 15 are among the twelve with no PEPFAR.
- **The Global Fund Data Explorer** publishes annual programme results 2017–2024 for 22 of 24
  through an open JSON API on `data.api.theglobalfund.org`, including key-population indicators
  no aggregator carries. Ten of the twelve no-PEPFAR countries get an ART series from it.

Both are grade 1 by every criterion the ladder uses, and both were found the same way Thailand's
Data Mart was: by watching what a public dashboard asks its own backend for. Neither publisher
documents them as APIs. So the practical guidance for this region is neither of the two the
ladder had — **regional-side first in West and Central Africa** — and the grade-4 definition
should be read as *the layer above the country*, of which the bilateral donor is one case and the
multilateral funder and the estimates programme are two more.

Two cautions carry forward. Naomi's period list mixes one historical estimate with projections
dated 2026 and 2027, which is the Thembisa fitted-versus-projected problem in a new place and
would be worse here, since the projections postdate the cuts and predate knowledge of them.
And Naomi's national ART figure is the country's own programme total fed in as a constraint, so
it agrees with the Global Fund's by construction — Guinea's two figures sit 0.9% apart across a
year — which is a `derived` relationship the reconciler must not score as corroboration.

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


## 7. What a second pass changed, and the two grades the ladder was still missing

*Added 2026-08-15, after the West and Central African search was run a second time and the first
pass was judged to have stopped too early.*

The first WCA pass produced four candidates. The second produced ten country sources and five
source classes the first had not opened. Almost none of that came from searching harder in the
ordinary sense. It came from four rules being wrong, and the rules are the part worth keeping.

### 7a. The additive test is per table, not per document

Phase 2 established the Malaysia test: a source earns a connector only if it carries something
the aggregators do not. Phase 4 round one applied it to whole documents, and so ruled out every
national GAM report as redundant with the GAM submission UNAIDS already publishes.

DR Congo's 2024 PNMLS report shows why that is wrong. It names a source under each table, and
the names differ: seven tables come from the national DHIS2, four from the programme's own
annual report, the provincial PrEP table from PEPFAR, and one — Tableau LVI — from the REDES
expenditure survey. Four classifications in one document. The PEPFAR table is `derived` and must
never be counted as corroborating our PEPFAR connectors; the DHIS2 tables are the gated database
in print and are `independent`.

**A document is never redundant as a whole.** Each table's named source decides its own status.

### 7b. And it is per file inside a dataset family

The same error at a larger scale, and this one was ours rather than a country's. The pipeline
reads three files from PEPFAR Spotlight. Spotlight publishes **fifteen**, all open, all direct,
all at the same host, in the same zip convention the pipeline already parses. The class had been
marked as covered because three of its members were.

Four of the twelve unread files are additive against everything the panel holds: an
operating-unit budget series reaching back to **2004** and split by beneficiary population, a
commodities file with planned ARV and test-kit quantities, a modality file carrying
community-versus-facility case-finding and the whole attrition set (`TX_RTT`, the loss-to-follow-up
reasons, interruption by duration), and a health-workforce inventory. The single most direct
measurement of the cut's mechanism anywhere in this project — outreach testing collapsing while
facility testing holds — was sitting in a file at a host the pipeline downloads from weekly.

§6 said to check what the ingested sources are being asked to throw away. Round two extends it:
**check what else the ingested source publishes.** Enumerate the family before declaring it read.

### 7c. Grade 3.5 — published to a human, not to a machine

The ladder had grade 2 (open born-digital report) and grade 3 (gated database). Nigeria sits
between them and neither name fits.

`wallboard.nascp.gov.ng` is the national programme's dashboard, public, free, no login, refreshed
20 February 2026, carrying 1,593,757 people on ART with a state selector and PrEP, HTS, ART and
PMTCT tabs. It is more current and more granular than anything the aggregators publish for
Nigeria. Its query backend returns 403 to every scripted request even with the correct cluster
and resource key and matching Origin and Referer; the page renders correctly in a browser and
emits no data request an automated client can capture.

The data is published. It is not gated. It is simply addressed to a person with a mouse.

**Grade 3.5 is where the ladder's binary of open-versus-gated fails**, and it matters for how the
feasibility answer is phrased. Counting Nigeria as gated understates what its programme
publishes; counting it as open overstates what a contamination-safe pipeline can take. A headless
browser would reach it, at the cost of a component that breaks silently on the next
republication, and that trade is the researcher's to make rather than a default.

> **Superseded by §8b (2026-08-17).** The 403 described here is real, and the grade drawn from it
> was still wrong: the same programme publishes an open JSON API on two other hosts. Nigeria is
> grade 1. The grade 3.5 category stays in the ladder — it describes a real thing — but this is no
> longer an example of it.

### 7d. Grade 3 has a second door: open, gated by an agreement

IHME's Development Assistance for Health database, 1990–2026, released 11 June 2026, carries the
projection years that hold the 2025 cuts. It is public and free. The download sits behind a
click-through non-commercial user agreement and a login.

That is a gate, but not the same gate as a national ministry's. Nobody has to be granted
anything: a researcher accepts terms once and the file is theirs. It resolves the way the
pipeline already resolves UNAIDS AIDSinfo — a hand download into `data/raw/`, with the connector
reading the file and never the site. Accepting terms on someone's behalf is not mine to do, so
the route is recorded as manual by design and not as a limitation.

### 7e. The method that opened three hosts: read the application, not the page

Three sources looked empty and were not. Chad's statistics office returned one identical
3,239-byte shell for every path; `data.pepfar.gov` returned an identical 1,993-byte shell; IHME's
financing viewer did the same. All three are JavaScript applications, and in all three cases the
addresses were sitting in the bundle:

- fetch `/static/js/main.*.js`
- grep it for `http`, `/api`, `.zip`, `.xlsx`, `.csv`
- try the endpoints without a token — some need one and some do not

Chad's `/api/menus` answers `401 Token d'accès requis`, and `/api/publications/search?q=` answers
without any token at all, listing the health statistics yearbook series 2005–2023. PEPFAR's
bundle held fifteen hardcoded dataset paths. IHME's held the GHDx series URL that its own site
search returns 403 for.

**A shell response is not an absent source.** It is the most common false negative in this whole
exercise, and both an ordinary fetch tool and `curl` report it as a page with nothing in it.

### 7f. The layer above the country now has a domestic-money column

§5 of this note found the funder layer inside PEPFAR's own files. Round two found the layer the
panel was missing on the other side: **money that is not donor money.**

`hivfinancial.unaids.org` publishes the Global AIDS Monitoring programme-expenditure database as
one open 5.5 MB spreadsheet — 59,947 rows, 121 countries, expenditure years 2011–2024, the NASA
programme hierarchy down the rows, and down the columns a split by financing source with central
government, sub-national government, social security, **households**, private insurance,
corporations, PEPFAR and the Global Fund each in their own column.

For the panel's taxonomy it splits in two. The PEPFAR and Global Fund columns are `derived`
against connectors the project already has, and must not be read as corroborating them. The
domestic public, household and private columns are `independent` and exist in no other source
the pipeline touches. The question of who absorbs a withdrawn donor — the state, or the
patient — is answerable only from those columns.

It also replaces most of a hand-extraction programme. Round one's plan was to read national AIDS
spending assessment PDFs country by country; this file covers 18 of the 24 WCA countries, and the
PDFs stay valuable only where it has no entry (Cameroon, Congo-Brazzaville, Cabo Verde,
Guinea-Bissau, Equatorial Guinea, São Tomé) or where the report breaks spending down further than
the spreadsheet does.

### 7g. Four traps that are general, not local

Each was found by checking a figure that looked like a finding, and each would have produced a
publishable number that was wrong.

**A zero is not a measurement.** In the GAM expenditure database a zero means *not reported*.
Mali's 2024 row shows 3,184,591 USD of domestic spending and no international spending at all,
while the Global Fund's own API shows Mali holding active HIV grants disbursing across that year.
Read literally, that row says a donor left. It says a country did not fill in a column.

**Same-origin agreement is not triangulation.** Benin's GAM figure agrees with Benin's NASA
report to within 3–5%, and DR Congo's with its REDES table to within 2%. Both pairs are one
national exercise published twice. The agreement is worth having — it establishes that the
spreadsheet can stand in for the PDF, which is what removes the hand extraction — but it
corroborates the extraction and not the measurement, and the reconciliation layer must not treat
it as two sources agreeing.

**A quantity column is not unit-stable across years.** PEPFAR's commodities file gives Nigeria
*HIV-1/2, Determine, 100 Tests* at 75,757 units and 85.60 USD each in FY2024, and the same item
string at 5,965,515 units and 0.80 USD each in FY2025 — a pack one year and a single test the
next. The naive read is testing supply rising fifty-eight-fold in the year the money fell. The
per-unit price is the only thing in the file that reveals it.

**A code column can hold several vocabularies at once.** IATI transaction types come back as `D`,
`E`, `C`, `11`, `IF`, `R`, `IR` and `LR` from the same query, and 1,834 of 46,964 distinct
activity/date/value keys appear under more than one of them. A connector has to pick one
vocabulary and dedupe against the others, or it double-counts disbursements.

### 7h. What round two costs, and what it says to the next region

The first pass cost a day and produced four candidates; the second cost a day and produced
fourteen. That ratio is the finding. A first pass over an unfamiliar region measures which
sources are easy to find, and easy-to-find and additive are close to uncorrelated: the largest
country-side money source in this region is one spreadsheet three clicks from a page the project
had already used, and the sharpest service-disruption signal is a file on a host the pipeline
downloads from every week.

The instruction that produced this section — search again, and keep going until the search is
exhausted rather than until it is satisfying — is not a work-rate instruction. **A single pass
systematically under-finds, and the shortfall is not spread evenly: it lands on the sources that
are additive.** Every region after this one gets two passes, and the second one starts by
enumerating the families the first marked as covered.

---

## 8. What a third pass changed, and the traps that now live in code

*Added 2026-08-17. §7h prescribed two passes for every region. This was the third pass over the
same region, and it produced two large sources and one overturned grade, so the prescription was
still set too low.*

### 8a. The fourth search rule: searching for the topic word under-finds

Rounds one and two both keyed on HIV — the word, its French forms, DAC purpose code 13040, HIV in
a catalogue title. That is the right key for a source about HIV and a useless one for a source
carrying HIV as a handful of columns inside a collection about something else.

WHO's tuberculosis dataset holds **100 HIV-related variables across nine of its datasets**,
including the only ART-initiation series anywhere in this project — national TB programmes report
how many people started ART because they need it as a denominator for preventive-treatment
coverage. WHO's Global Health Expenditure Database carries an HIV line for every country in it.
Neither has HIV in its name. Neither was visible to any search this project ran before round
three.

The failure repeats inside a single site. Chad's statistics office serves a title-matching search
endpoint where `q=sante` returns nothing and `q=VIH` returns nothing, while ten editions of the
national health statistics yearbook sit in the catalogue under the string `SANITAIRES`.

**Enumerate a catalogue; do not search it.** And when a health collection is ruled out because it
is about something else, check its columns before believing that.

### 8b. A source graded once is not graded forever

§7c invented grade 3.5 for Nigeria on the evidence that the national wallboard's Power BI backend
returns 403 to every scripted request. That evidence was correct and the grade drawn from it was
wrong.

Nigeria's National Data Repository has an open JSON API. `ndr.nascp.gov.ng/public/GetRecencyData/`
returns state-level recency yield with numerators, denominators, age bands and a monthly
viral-load series from March 2020; `ctd.nascp.gov.ng/facilitydata/` returns all 37 states with
treatment, PLHIV estimate and coverage, dated December 2025. Plain `curl` gets HTTP 000. The same
request with HTTP/1.1, a browser user agent and `Referer: https://ndr.nascp.gov.ng/public/wallboard`
returns the data. **A `Referer` header was the whole gate.**

A grade attaches to a route and not to an institution. Nigeria had one closed route and three open
ones, and the log recorded the institution as closed on the strength of the first. Any source
graded 3 or higher on a single probe is re-probed on the next pass, and the re-probe enumerates
the host's other paths before it repeats the one that failed.

### 8c. Four more traps, and this time three of them have code

§7g listed four traps as things to watch for. Round three found four more, and built a check for
three of them, which is the part worth generalising: a trap described in a document protects
whoever reads the document, and a trap in `validate()` protects everyone who runs the pipeline.

**A unit error is a discontinuity; growth is continuous.** Gabon's entire 2024 TB/HIV expenditure
row is CFA francs filed into columns the dictionary declares to be US dollars — 325,375,873
against that country's own median of 9,836, a factor of 33,000. There is no currency field to
check against. The connector emits it exactly as published, because a connector records what the
source said and validation says what it means, and `writers._unit_outliers` catches it. The
discriminator matters more than the threshold: most large jumps in these money columns are real
variation on budgets of a few thousand dollars, so the check tests for a break in an otherwise
stable series and not for a big ratio.

**A fall in reporters is not a fall in the thing measured.** `writers._reporter_drops` names every
series where the reporting country set shrinks sharply between two years, so that nobody totals
two years of a changed panel and reads the difference as a change in the world.

**A censoring floor is not a measurement.** UNAIDS censors small figures for display — `<100`,
`<500`, `<0.1`, `>98` — across 66,291 cells, and whoever strips the sign is left holding the
threshold as though it were data. Ukraine's HIV expenditure reads **100 US dollars for 2018**,
sitting between 108,000,000 in 2017 and 100,000,000 in 2019. The AIDSinfo connector can repair its
own share because the CSVs still carry the `<`; the WHO and World Bank APIs return the floored
number with the notation already gone, so for those two the check is the only defence there is.
`writers._floor_values` names all twelve affected groups across three connectors.

The same notation means different things in different instruments, and that distinction cannot be
automated away: in the epidemiological files `<100` is a real small epidemic (37 countries are
censored end to end), and in the money file it is a country that did not report. WHO GHO confirms
the first from outside — Maldives is `<100` in AIDSinfo for its whole series and 2, 3, 5, 6, 8
people in GHO.

**The catalogue name is not the indicator, and no check will catch that one.** GHO code
`HIV_0000000020` is catalogued as *Estimated number of pregnant women living with HIV* and returns
69, 67, 64, 63, 56, 61 for Nigeria. It is PMTCT coverage as a percentage: 36,701 of 53,000 is 69.2
in 2020, and 26,566 of 47,000 is 56.5 in 2024, both of which the code returns rounded. Loaded on
the strength of its name it would have entered the panel as a headcount, in units of `count`, at
roughly a thousandth of the true value — and **no range check, no outlier check and no bounds
check would have found it**, because 56 to 69 is an unremarkable number for a count to be. The
only thing that catches this class is reading the values against a second source before mapping
the code.

This indicts the auto-resolution path in our own GHO connector, which resolves codes by matching
catalogue names. That path now logs a warning telling the reader to verify before trusting it, and
the fourteen mapped series are pinned by code. Related, and the reason the name cannot be trusted
even to be unique: `HIV_0000000015` and `HIV_0000000016` carry identical catalogue names, and 15
returns an empty array.

### 8d. One detector, two readings, and only one of them is a unit error

Run over the whole panel, `_unit_outliers` flagged 247 rows under the single label *possible
currency/unit mismatch*. Split by direction, it is 17 rows above their series and 230 below, and
those are not the same finding. Above is the currency error the check was written for. Below is
almost never a unit problem: South Africa's 2021 TB/HIV figures are 42 and 37 against a normal six
figures, which is a reporting collapse in the second COVID year.

The check now reports the two directions separately. What makes this more than tidier wording is
where the low side lands: 42 of those 230 rows are UNAIDS HIV expenditure at exactly 100 US
dollars, which `_floor_values` independently names as a censoring floor two warnings later. **Two
checks built for different faults converging on the same rows is the strongest evidence either of
them offers**, and neither would have produced it while the low side was mislabelled as a currency
mismatch.

### 8e. What round three says about when to stop

Round one produced four candidates, round two fourteen, round three two large sources and a grade
overturned on the region's largest epidemic. The returns are falling, which is the expected shape,
but they have not fallen to nothing and the third pass reached the only flow measurement in the
whole panel.

The stopping rule that comes out of this is not a number of passes. **Stop when a pass produces
only sources you already know how to classify.** Rounds two and three each ended by changing a
rule about what counts as a source — per-table in round two, per-column in round three — and a
pass that changes the rule is a pass that was worth running. Round four's key, if there is one,
is columns inside sources already ingested: §7b asked what else the source publishes, and round
three's version asks what else the file already downloaded contains.

---

## 9. What a fourth pass changed, starting with a source three rounds had written off

*Added 2026-09-05.*

### 9a. A block page is a version number, not a decision about us

Round three recorded the Global Fund's documented API host as edge-blocked: `fetch.theglobalfund.org`
answered every request with an Azure Front Door page reading "The request is blocked." on an HTTP
403, including the bare root, which is what a network-level ban looks like. The connector registry
carried the conclusion drawn from that, which was that the Global Fund had no country-level feed and
would enter the panel only as an OECD CRS donor code.

Both readings were wrong, and the fourth pass overturned them by opening the host in a browser and
reading `data-service.theglobalfund.org/api`, which lists the live versions. **Versions 2 and 3.3
are retired.** Every path the earlier documentation gives sits under a retired version, and a
retired version and a closed door return the identical page, down to the bare root. The first
request to `/v4.2/odata/` succeeded from the same machine, on the same network, with plain `curl`
and no headers at all.

§8b said a grade attaches to a route and not to an institution. This adds the sharper form. **A
grade attaches to a route at a version, and a 403 that covers the whole host is evidence about the
path, not about the requester.** Read the service's own version list before concluding anything from
a block page, and treat any source whose refusal was uniform across every path as a source that has
not actually been probed.

### 9b. What the Global Fund publishes that nothing else in the panel does

`AllProgrammaticIndicators` filtered to `programmaticDataSet eq 'Annual_Results'` is 15,313 rows of
country by year by indicator, grant-reported, in a single response with no `nextLink`. Annual_Results
is not an HIV dataset. It carries 69 indicator names covering the institution's whole portfolio,
of which 20 map to canonical indicators and 49 are named in the connector as deliberately unmapped,
26 of those because they are malaria, drug-resistant TB or health-systems lines.

The run of 2026-09-05 emitted **4,797 rows over nine canonical indicators**, leaving out 2,034
subnational rows and 80 rows whose geography is not a country.

The one that matters is *People newly diagnosed with HIV initiated on ART*, a count of people who
started treatment in a year, arriving through grant reporting that has no connection to the UNAIDS
estimate WHO and the World Bank republish. **The national series is much smaller than the raw row
count suggests, and the filters are why.** 114 rows carry the indicator across 40 country codes and
the years 2017 to 2024. After dropping subnational rows and multicountry geographies, 93 rows
survive, across 33 countries, and the series starts in 2021 rather than 2017. Every row before 2021
is subnational or regional, so the Global Fund began reporting this indicator nationally only in
2021. Reporting countries then rise, 17 in 2021 to 32 in 2024, which is the opposite direction from
`new_diagnoses` in the same dataset and means the two series cannot be read the same way.

The panel's only other initiation series is `hiv_reg_new2` from WHO's tuberculosis dataset (§8a),
so for the countries the two share this is a second independent instrument on the project's central
indicator. The Global Fund also supplies a second reading of `tbhiv_on_art`, 592 rows against WHO
TME's `newrel_art`.

### 9c. Two traps, and one of them defeats every check we have

**`$expand` empties an OData result instead of failing.** Asking for `$expand=geography` on
`AllProgrammaticIndicators` returns HTTP 200 with an empty value array. The same query without the
expand returns rows. A connector written the obvious way therefore reports a source with nothing in
it, and every downstream check agrees, because zero rows is a perfectly well-formed answer. The
diagnostic that found it was running `$top=1` twice, once with the expand and once without, and
comparing the counts. **When a source returns no rows, re-request it with each query option removed
in turn before recording the source as empty.** The connector joins on `recordId` instead, which for
this dataset is a Geography id.

**A partial row wearing a country's code.** 21 of those 114 ART-initiation rows are marked
`Subnational` and carry a country-level geography exactly like the national ones. South Africa's
2022 subnational row is 1,531 people, against a national figure in the hundreds of thousands. This
is the same class as the GHO catalogue-name error in §8c and it is worse. Nothing in the country
code, the year or the value marks the row as partial, and no range check can catch it, because
1,531 is an ordinary number for a small country's annual initiations and the row does not even have
to be small. `geographicCoverage` is the only field that separates the two, and a connector that
does not read that field mixes one grant's catchment into a national series silently. Only
`National` rows are emitted, and the subnational count is logged rather than dropped in silence.

Two related shapes in the same service. 63 of the 300 geographies are `Multicountry`, so a regional
grant's results would otherwise land on whichever country its code resolved to, and only
`level == "Country"` geographies are accepted. And the Global Fund now enters the panel twice, as
service results here and as money through the OECD CRS donor code `9OTH012`, which are different
quantities from the same institution and must not be totalled together.

### 9d. What the two instruments say when both are asked the same question

The Global Fund connector makes `art_initiations` the first indicator in this panel carried by two
independent instruments, so the run of 2026-09-05 was the first chance to ask whether they agree.
The whole panel at that point was 144,318 rows over 226 countries and 17 sources.

**They agree, and they are not copies of one another.** WHO TME and the Global Fund both report
national ART initiations for 75 country-years across 29 countries. The two figures are within 1 per
cent of each other in 24 per cent of those country-years, within 10 per cent in 63 per cent, and
more than 25 per cent apart in 24 per cent, with a median gap of 3.5 per cent. `tbhiv_on_art` is
carried by both for 571 country-years across 87 countries, agreeing within 1 per cent in 37 per
cent, within 10 per cent in 70 per cent, more than 25 per cent apart in 15 per cent, median gap 2.8
per cent. Two instruments that agreed exactly would be one instrument published twice, which is what
§4b found for GAM against the national NASA reports. A quarter of country-years a quarter apart is
the signature of two organisations counting the same patients through different reporting chains,
the health ministry's TB register in one case and the grant's own results framework in the other.

**Comparing the two requires matching the age group as well as the country and year.** WHO TME
publishes `tbhiv_on_art` for all ages and for children under 15 as separate rows, 226 of the latter.
A comparison keyed on country and year alone silently sets a national all-ages figure from one
instrument against a paediatric figure from the other, and reports the disagreement as a measurement
difference. Matching on age group moves the median gap from 6.1 per cent to 2.8 per cent.

**Both instruments show ART initiations falling into 2024.** On the 88 countries where WHO TME
reports both 2023 and 2024, 46 fell and the total dropped 14.4 per cent. On the 21 countries where
the Global Fund reports both years, 14 fell and the total dropped 29.6 per cent. Of the 45
consecutive-year changes both instruments can see, 33 agree on the direction and 12 do not. The two
totals are not comparable to each other, because the Global Fund's 21 countries are a different and
much smaller set, but each is computed on countries reporting both of its own years, which is what
the reporter-drop warning in §5 exists to enforce.

**A validation detector can be confidently wrong in a way the panel cannot show.** The same run
raised three new censoring-floor warnings on WHO TME, at the value 1, and all three were false. The
check dropped zeros before looking for the most repeated value, which leaves the smallest printable
count as the mode of any small-count series: `tbhiv_deaths` reads 461 zeros, 315 ones, 179 twos and
98 threes, which is a small-count distribution and not a threshold with nothing below it. A series
that contains zeros has already published the smallest value there is, so nothing under its mode was
suppressed, and zeros now count towards the series even though they can never be the candidate
value. Over the panel the separation is total, with all 12 genuine floors carrying no zeros at all
and the three WHO TME columns between a tenth and a quarter zeros. One plausible alternative was
measured and rejected: the repeated value's count against the count of the next value up separates
nothing, because UNAIDS `new_infections` is a genuine floor at 2.74 times the next value and WHO GHO
at 2.08, against 2.2 for `tbhiv_on_art`, which is not censored.

**The same run confirmed two earlier fixes in the data rather than in the code.** UNAIDS
`hiv_expenditure_total` now stands at 961 rows with none reading exactly 100 US dollars, against 42
such rows and a 273-row floor warning before the censoring fix. The DHS connector now returns nine
rows for the Democratic Republic of the Congo across 2007, 2013 and 2023, where the country name
mismatch had returned none.

**A run warning can be a fault the code already answered.** `data.clm-asia.org/api/` returned HTTP
500 on every fetch for the 2023 first quarter across all eight indicators, which reads like a source
going down and is not. That server raises an unhandled `KeyError` and serves a Django debug page for
any request it cannot satisfy, including a quarter with almost nothing in it, and the connector has
recorded that behaviour and capped its retries since July 2026. The sentinel produced 23 rows over
2023 to 2025 on all eight indicators in the same run. The general point is that a source which
answers a bad request with a 500 rather than an empty result makes its own logs unreadable, so the
run log has to be checked against what the connector actually wrote before a warning is believed.

### 9e. The cheapest source in the ladder was the one already on disk

Four Global Fund indicators were held out of the connector on 2026-09-05 on the stated grounds that
TB preventive services for people in HIV care are published by nobody else, so mapping them would
create a series with no second instrument. That reasoning was sound and the premise was false.
UNAIDS AIDSinfo publishes the proportion counterpart of three of them, and those exports were
already sitting in `data/raw/unaids/` where a previous download had put them.

The connector reads any CSV in that directory and classifies it by matching substrings of the
filename against a list of 11 core indicators. A file the list does not name is counted as skipped
and passed over in silence. Seven `TB and HIV` exports had been skipped that way on every run, and
they hold about 14,100 country-year cells across 193 countries: TB and HIV treatment co-management
for 168 countries over 2000 to 2024, incident TB cases in people living with HIV for 192, TB-related
deaths for 191, and the three TB preventive therapy proportions the Global Fund counts publish the
other side of.

**The general rule this adds to §8b. A source graded once is not graded forever, and neither is a
source already ingested.** The ladder's grades describe what an organisation publishes, and every
grade in this document was assigned by probing a remote host. Nothing in the ladder describes how
much of what arrived was ever read. A connector that names the files it wants and skips the rest
will report a healthy run, a rising row count and no warning at all, while sitting on material it
never opened. **Count what a connector skipped, not only what it mapped, and read that number as
often as the row count.** For this connector the number is 114 of 146 files still unread, reducing
to 111 distinct indicator names, among them condom and needle distribution volumes, opioid agonist
therapy coverage, male circumcisions performed, procured self-test kits, early infant diagnosis,
late HIV diagnosis and prevention-programme coverage for each key population. Several of those are
commodity and service volumes of exactly the kind this project argues move first.

### 9f. Three of the seven files turned out to be a republication, and the test says which

The seven TB and HIV exports were mapped on the expectation that all seven would add a second
instrument. The run of 2026-09-05 wrote them into the panel and the exact-agreement test, the same
test that exposed UNAIDS GAM as a republication of the national NASA reports, was applied to each.
The seven do not behave alike, and mapping them was still right, because the test can only be run on
data that has been ingested.

**Two are WHO republished.** On `tbhiv_deaths`, 4,302 country-years overlap WHO TME. 3,941 carry an
identical non-zero figure, 315 are zero in both files, and 46 differ. On `tbhiv_incidence`, of the
1,815 overlapping country-years where UNAIDS prints an uncensored number, 97.5 per cent are identical
and 99.0 per cent agree within one per cent. Two organisations do not independently model 3,941
national TB death counts and land on the same integer. The benchmark for what genuine independence
looks like is in the same panel: Global Fund and WHO TME both count ART initiations, agree exactly in
8 per cent of country-years, and differ by a median of 3.5 per cent.

**The incidence export is worse than redundant.** UNAIDS covers 497 country-years WHO TME lacks, and
every one of the 497 is a censored `<100` bound. Where the two overlap UNAIDS censors 2,934 cells
that WHO TME publishes as numbers. The export adds no point estimate anywhere in the panel. The
deaths export is uncensored and its 432 extra country-years are usable, so it stays for coverage.

**The three proportions are a genuine second instrument, but not of the series they were mapped
against.** The expectation written into `indicators.py` was that the Global Fund count of TPT
initiations divided by `art_initiations` would reproduce the UNAIDS newly-enrolled proportion.
Tested on 181 country-years it reproduces it within one percentage point in 41, misses by a median of
11.5 points, and exceeds 100 per cent in 32, Eswatini 2024 reaching 3,093 per cent on 194,482 courses
against 6,288 new enrolments. The Global Fund counts everyone on ART who started a course, not the
new enrolments. Against the right denominator the identity holds: the Global Fund count over
`on_art_count` reproduces the *currently* enrolled proportion within one percentage point in 48 of
111 country-years, within five in 76, and never exceeds 100 per cent.

**The general rule this adds to §9d. Two sources naming the same quantity are a hypothesis about
which two series pair, not a fact, and the arithmetic decides it.** Both errors here were errors of
pairing rather than of ingestion, both were invisible until the rows were in the panel, and both were
caught by dividing one series by another and reading the answer against 100 per cent. **An identity
that a pairing implies is a test the pairing has to pass. Run it before writing the pairing into a
note.**

### 9g. The audit §9e asked for, and the indicator it found unread

§9e ended by asking for a number that no run produces, the count of what each connector skipped.
[`scripts/audit_coverage.py`](../scripts/audit_coverage.py) now produces it. The audit reads only
local files, fetches nothing, and is meant to be run whenever the panel is rebuilt.

Connectors fail three different ways, so the audit measures three different things. A **directory
reader** is handed a folder and opens the files whose names it recognises, so the audit lists the
files it did not open. A **wide file picker** opens one file holding many indicator codes and keeps
the codes named in a dictionary, so the audit lists the codes nobody has looked at. A **pull by name
connector** asks a remote interface for a fixed list of series and cannot skip anything, because it
never sees the catalogue, so the audit can only report the size of the request and leave checking
the catalogue as a manual job. Those five connectors ask for 14, 8, 3, 3 and 2 named series
respectively, against catalogues running to hundreds or thousands of codes.

The audit found the AIDSinfo case §9e already describes, 32 of 146 exports read. It found 3 of 15
PEPFAR archives read, the 12 unopened ones including the health workforce inventory, commodity
procurements, partner performance and both site-level files. It found four Global Fund CSVs on disk
that no connector reads, because the Global Fund connector reads the OData API instead, which is
the same disease with a different cause, material downloaded and never decided about. And it found
the case that matters.

**`pepfar_panorama` was reading 2 of the 71 MER indicators inside the one file it opens, and one of
the 69 it ignored was `TX_NEW`, the count of people newly started on antiretroviral therapy.** That
is the indicator this project exists to measure, the one §1 argues almost nobody publishes, sitting
in a file that had been on disk since July 2026 and was opened on every single run. `TX_NEW` carries
the same coverage as the `TX_CURR` series the connector already read, 57 countries over fiscal years
2018 to 2025, so the fix was one dictionary entry per connector.

Before the entry was written the pairing was tested, per §9f. PEPFAR measures a programme footprint
rather than a country, so a PEPFAR figure above the WHO TME national total would mean the pairing
was wrong. Across the 266 overlapping country-years PEPFAR sits at or below the national total in 86
per cent and takes a median share of 0.74, which is the shape a funder's share should have. Fifteen
country-years exceed 1.25, led by Mali 2020 at 5.19 and Uganda 2019 at 1.98, and PEPFAR's October to
September fiscal year against WHO's calendar year accounts for part of that. `TX_NEW` also covers 88
country-years across 38 countries where WHO TME publishes no initiation figure at all, and splitting
it by funding agency gives `art_initiations_usaid` against `art_initiations_cdc`, which is the
within-country comparison in its sharpest form. A treatment cohort falls slowly after a cut because
people already enrolled keep collecting refills. Enrolment stops the week the clinic stops testing.

`HTS_TST` and `PrEP_NEW` were mapped in the same pass. Sixty-six MER codes remain unmapped, among
them `TX_ML` and `TX_RTT`, which count people who left treatment and people who returned to it.
Both measure care disruption directly and neither has a canonical indicator yet, so both were left
as a decision to make rather than taken quietly. `TX_ML` equals the sum of its own seven sub-codes
to within one per cent, so mapping the total alone is correct and mapping the parts as well would
double count.

**The general rule this adds to §9e. A connector must report what it discarded, in the same log line
it reports what it used.** `global_fund` already does this, naming 24 series, declaring 45 out of
scope, and tallying anything matching neither at run time, so a new indicator appearing in the API
is reported instead of dropped. Every PEPFAR connector now logs the files it did not read. **An
unread file is not a loss, it is a decision nobody has made yet, and the fix is to record the
decision where the connector lives so the next audit reports a choice instead of a gap.**

### 9h. The 114 unread AIDSinfo exports, decided one by one

The audit in §9g reported `unaids_aidsinfo` reading 32 of 146 exports. Every one of the remaining
114 has now been opened, counted and either mapped or declared out of scope with a reason. The
connector reads 51, declares 95, and leaves nothing undecided.

Nineteen exports were mapped. Four of them land on canonicals another source already fills, so each
was measured against the series already in the panel before the mapping was written, per §9f.
`hiv_tests_performed` agrees with WHO GHO exactly in 100 per cent of 323 overlapping country-years.
That is not corroboration, that is UNAIDS reprinting the GHO series, and the mapping exists only for
the 92 country-years GHO does not carry. `hiv_test_positivity_pct` agrees exactly in 22.5 per cent
and within one percentage point in 65.1 per cent, which is the same instrument at finer precision
because UNAIDS prints two decimals where GHO rounds. `pmtct_arv_count` agrees exactly in 76.7 per
cent of 1,515 overlaps. Only `pregnant_women_hiv` behaves like a second instrument, agreeing exactly
in 17.4 per cent of 759 overlaps with a median gap of 6.8 per cent, close to the Global Fund against
WHO TME benchmark of 8 per cent exact and a 3.5 per cent median gap.

Six new canonicals cover the vertical transmission chain either side of `pmtct_coverage_pct`, plus
two prevention commodities. The chain matters because a country can hold PMTCT coverage steady while
antenatal testing collapses, since coverage is computed among women already known to have HIV.
`anc_hiv_testing_pct` falling while `pmtct_coverage_pct` holds is the signature of a programme
shrinking its own denominator. `circumcisions_performed` is the most cancellable service in the
panel, a one-off surgical procedure delivered in campaigns that PEPFAR largely paid for, and the 15
countries reporting it are close to the whole global programme rather than a sample of it.

Two key-population canonicals were added, and the reason is a denominator. PEPFAR reports how many
men who have sex with men its partners reached. Only UNAIDS says how many there are to reach.
`kp_size_estimate` supplies that figure for 552 country-population pairs across five key
populations, and `kp_prevention_coverage_pct` supplies the baseline a cut starts from for 156. Both
carry a single value stamped 2024, which is when UNAIDS last compiled the figure rather than when the
survey behind it ran, so both rows carry `extra["most_recent"]` and neither can show a change.

The 95 declared exports fall into groups. Thirty-six are age bands of `plhiv`, `new_infections` or
`aids_deaths` across 183 to 184 countries and 35 years, roughly 173,000 cells, and the panel has no
`age_group` column. Twenty-nine are single-point 2024 key-population snapshots measuring stigma,
violence, condom use, syphilis and viral hepatitis, which are outcomes of a different research
question. Eight are quantities the panel can already compute, such as an incidence rate per 1,000
that is `new_infections` over population. The rest are single-year or near-empty service counts,
including procured self-test kits, which covers 48 countries for 2019 alone.

Two declared exports are the largest body of unread material left in this source and they are held
back for a reason that is not technical. `Progress towards 95-95-95 targets` and `Testing and
treatment cascade` use a two-row header, the first row naming the year and the second naming the
indicator, which the parser in `unaids_aidsinfo` cannot read. The All-ages pair alone holds 3,532 and
3,660 values across 176 and 185 countries from 2015 onwards. Writing a second parser is a small job.
Deciding what the numbers are is not. The first bar of each cascade repeats `know_status_pct`, which
the panel holds. The second and third bars are conditional percentages, the share on treatment among
those who know their status and the share suppressed among those on treatment, and a conditional
percentage is a different quantity from the unconditional `art_coverage_pct` and
`community_viral_suppression_pct` already in the panel. Whether the conditional form earns three
more canonicals is a question about the analysis, not about the parser.

**What §9g asked for, applied.** `unaids_aidsinfo` now holds a `DECLARED_UNMAPPED` list pairing a
filename substring with the reason the file stays out, `scripts/audit_coverage.py` subtracts declared
files before reporting a gap, and the connector logs three numbers rather than two, read against
declared against awaiting a decision. An export in the third number raises a warning naming the file,
because an export in the third number is the only kind that needs anyone's attention.

### 9i. The 66 unread PEPFAR indicator codes, and the ten canonicals already waiting for them

Closing the AIDSinfo gap left the audit reporting `pepfar_panorama` at 5 of 71 MER codes mapped and
`pepfar_agency` at 3 of 71, with nothing declared and everything else unexamined. The §9g rule had
been applied to PEPFAR at the level of files, where the connector now names the archives it does not
open, and not at the level of indicators inside the one archive it does.

The expected job was to write 66 reasons for leaving 66 codes alone. Checking the codes against the
canonical registry before writing any of them changed that. Ten of the largest already had a name in
the panel, put there by UNAIDS, WHO and the Global Fund, with no PEPFAR measurement under it. Six
could be paired on arithmetic alone and are now read.

| MER code | canonical | what the pairing test showed |
|---|---|---|
| `TX_PVLS` | `viral_suppression_count` | 393 of 399 country-years are ones no other source in the panel covers |
| `TB_PREV` | `tpt_completions` | 250 of 252 country-years are new |
| `TB_STAT` | `tb_patients_hiv_tested` | median 0.58 of the WHO TME national figure over 201 overlaps, at or below it in 96% |
| `TB_STAT_POS` | `tb_patients_hiv_positive` | median 0.77 over 197 overlaps, below in 93% |
| `PMTCT_ART` | `pmtct_arv_count` | median 0.75 to 0.81 against three separate national sources, below each in 91 to 93% |
| `VMMC_CIRC` | `circumcisions_performed` | median 0.91 over 98 overlaps |

Exact agreement with the national series is 0.0% for five of the six and 1.0% for `VMMC_CIRC`, so
none of them is a national series reprinted under a PEPFAR label, and every one sits at or below the
national total in the large majority of country-years, which is the shape a programme footprint has
to have. Applying §9f before writing the mappings, rather than after, is what these numbers are.

**The one that would have been silently wrong.** `TX_PVLS` summed across its quarters reaches a
median of 2.32 times `TX_CURR` and exceeds the treatment cohort in 70% of country-years, which
cannot happen, because a person with a suppressed viral load result is a person on treatment. The
code restates a rolling twelve months every quarter rather than adding a new period to it. Read at
the latest quarter the median is 0.71 and the excess appears in 1%. Nothing in the file says which
of the two collapses is right, and nothing in a clean run would have said the wrong one was wrong.

**A second collapse the file does not announce.** `TB_PREV` and `KP_PREV` publish at Q2 and Q4 only,
in 204 of 258 and 304 of 362 country-years, so two quarters is a complete year for them. The
partial-year warning would otherwise have fired on every row of `tpt_completions` in the panel, and
a warning that fires on everything is a warning nobody reads.

**The refusal worth recording.** `KP_PREV` looks ready to map and is not. Summing its two half-years
gives a median of 0.58 of the Global Fund national figure over 142 overlapping country-years, and
taking the later half alone gives 0.29. Both readings are defensible, they differ by a factor of
two, and PEPFAR's definition rather than this panel's arithmetic has to settle which. `TB_PREV` is
mapped despite the same reporting pattern because completing a course of preventive therapy is an
event and events add, while being reached is a status and the same person is reached in both halves
of a year as a matter of course.

**What the other 60 are.** Twenty-seven are a part of a code already read or of one left for a
decision, and the parts were measured rather than assumed: `HTS_TST_POS` and `HTS_TST_NEG` sum to
`HTS_TST` in 99% of 415 country-years, the `TX_CURR` dispensing legs sum to `TX_CURR` in 71% of 304
and never exceed it, and the three `HTS_INDEX` outcome legs sum to their parent in only 33% of 332,
so the parent and the parts there are not the same population. Sixteen need a canonical definition
written before a dictionary entry means anything, `TX_ML`, `TX_RTT`, `TX_NET_NEW`, `TB_ART` and
`PrEP_CURR` among them. Fourteen sit outside HIV testing and treatment, being cervical cancer
screening, post-violence care and services for orphans and vulnerable children. Three pair with a
canonical that is a percentage, and reading them needs the Denominator rows the connector currently
filters out, which is a change to how the file is read rather than an entry in a dictionary.

`pepfar_agency` still splits three indicators and now says why. Each added indicator becomes three
series needing three canonical definitions, and the three chosen are the ones a cut moves first. The
strongest candidate for a fourth is `TX_PVLS`, since a USAID arm losing viral suppression while the
CDC arm holds would be the clearest harm this panel could show.

Both connectors now log read against declared against awaiting a decision, and the audit reports 0
unexamined for each.

### 9j. How many quarters make a year, asked of the release instead of assumed

Reading six more MER codes brought in the reporting patterns of six more indicators, and the rule
deciding whether a year was complete could not hold them. That rule counted to four, with a
hardcoded exemption for the two codes §9i had found publishing twice a year. Reporting frequency
turned out to be a property of the indicator **and the year** rather than of the indicator alone.

| MER code | quarterly | at Q2 and Q4 |
|---|---|---|
| `TB_STAT`, `TB_STAT_POS` | FY2019 onwards | FY2018 |
| `PrEP_NEW` | FY2018, and FY2021 onwards | FY2019 and FY2020 |
| `TB_PREV`, `KP_PREV` | never | throughout |

No fixed list can hold a pattern that changes twice within one code. Counting to four put a
partial-year warning on 93 operating-unit-years whose totals are complete, and a warning that fires
on complete data is worse than no warning, because the rows it fires on are indistinguishable from
the rows where a service really stopped. The connector now derives the cadence, taking the modal set
of reported quarters over every country reporting that indicator in that year, and a country is
short only against what its own indicator-year actually publishes.

**Fewer quarters has two causes and they want opposite comparisons.** A year can report fewer
quarters because the release stopped early, which is FY2025 carrying Q4 alone, or because PEPFAR
changed how often the indicator reports. The two look identical in the quarter count and lead to
contradictory advice. Under a truncated release the annual totals are not comparable and the shared
quarters are. Under a change of frequency the annual totals **are** comparable and the shared
quarters are not, because a semi-annual report covers six months and a quarterly one covers three,
so comparing Q2 with Q2 across the change puts six months against three.

Two measurements in the file settle which reading is right, and they were run because assuming
either one would have been invisible in a clean run.

| test | full-year ratio | like-quarter ratio |
|---|---|---|
| `TB_STAT` FY2018 (Q2, Q4) against FY2019 (quarterly) | 0.99 | 0.53 |
| `TB_STAT_POS`, same change | 0.96 | 0.49 |
| `PrEP_NEW` FY2018 (quarterly) against FY2019 (Q2, Q4) | 3.10 | 6.05 |

`TB_STAT` is a service that neither grew nor shrank across that year, so the full-year ratio of 0.99
is the true one and the like-quarter 0.53 is an artefact of comparing 12 months with six. `PrEP_NEW`
grew steeply and no single ratio means anything on its own, but both of its ratios carry the same
growth, so the factor between them does mean something. That factor is 1.95. Had a semi-annual
report covered three months, the two ratios would have agreed.

So a semi-annual figure covers six months, a two-quarter semi-annual year is a whole year, and the
partial-year warning fires only when the newest year in the download publishes fewer quarters than
the year before it, or when one country falls short of what its own indicator-year publishes. Across
the TopLine file the warning count falls from 381 operating-unit-years to 288, and the 93 it stops
firing on are exactly the four indicator-years above. Every FY2025 cumulative row still carries it.

**What the rows now carry.** Every cumulative row keeps its four quarterly values in `extra`, so a
like-quarter comparison can be rebuilt from the panel without returning to the archive. Rows either
side of a truncated release carry `like_quarter_comparison` with its ratio, and rows either side of
a frequency change carry `cadence_change`, which states that the annual totals are the comparison
and a quarter-by-quarter reading is not. The FY2025 rows carry 228 of the 275 like-quarter
comparisons in the file.

`circumcisions_performed` has no FY2025 row at all. `VMMC_CIRC` reports `0000` for all 14 countries
in the Q4 release, so the panel carries silence rather than a zero, which is the right behaviour and
worth knowing before anyone reads the gap as a finding.

The general rule, alongside §9f and §9g. **A connector must not assume the shape of a period from
the shape of the file it happens to hold.** How many parts make a whole is a property of the release
and has to be read off the release, and where two readings of the same missing data give opposite
advice, the arithmetic that separates them has to be run before either is written down.

### 9k. The one source that asks the country who paid, and the four traps inside it

Every financing series in the panel before this one was a donor's account of the donor's own money.
The OECD Creditor Reporting System holds what donors reported disbursing, ForeignAssistance.gov
holds Washington's account of Washington's money, and the PEPFAR expenditure file holds PEPFAR's
account of PEPFAR's. Nothing asked the country. The UNAIDS Global AIDS Monitoring expenditure
database does, and it is the only near-global source that does: 59,947 rows, 121 countries, 541
country-years, expenditure years 2011 to 2024, of which 41 country-years carry 2024, the last year
before the cuts.

**The pairing test decided which canonical each donor column takes, and the column name did not.**
GAM's PEPFAR column against PEPFAR's own expenditure gives n=72, a median ratio of 0.995 and 35
country-years within 10%. The same column against `external_hiv_oda_us` gives n=205, a median of
1.031 and 54 within 10%. The wider overlap is coverage rather than agreement, so the column pairs
with PEPFAR's own account, at 49% of country-years within 10% against 26%. GAM's GlobalFund column
against the OECD CRS Global Fund series gives n=326, median 0.806, 47 within 10%. Both are emitted
under the donor's canonical, so the reconciliation layer classifies the comparison rather than the
panel holding two series that never meet. GAM's International column keeps a canonical of its own,
because every external dollar a country received and what OECD members reported as aid under purpose
code 13040 are differently scoped quantities, not two measurements of one.

**The grand total is a republication and is emitted anyway.** `TOTAL GRAND` against AIDSinfo's
country-reported expenditure gives n=469, median 1.0000, 420 within 1%, and the residual is
AIDSinfo rounding to two significant figures. Withholding it would hide a `derived` verdict the
reconciliation layer should reach from the data.

**A zero is not a measurement, and here that costs something real.** In this database a blank and a
zero both mean the country did not report. On the grand-total row the Households column is blank 13
times and zero 375 times against 153 positive values, and PEPFAR is blank 14 times and zero 313
times against 214. Neither is emitted, which means a programme defunded to nothing cannot be told
apart from a programme nobody filed a return for. That is a limitation of the source and not a
choice the connector can undo.

**Programme numbers are not stable and labels are.** Line `3.11` is "Cash transfers to girls
(high-prevalence countries)" from GAM 2017 to GAM 2023 and "Prevention programmes for vulnerable and
accessible populations (excluding HIV testing)" from GAM 2024, and `3.12` moves from vulnerable
populations to post-exposure prophylaxis at the same cycle. A map keyed on the number would splice
cash transfers to girls onto a vulnerable-populations series at the 2024 boundary this project
exists to measure. The map is keyed on the label text.

**Two classification schemes, and the reporting cycle does not tell them apart.** The pre-2016
scheme writes a full stop after the digit, `4. Universal access to treatment`, and the modern one
does not, `4 Gender programmes`. 31 country-years use the old scheme, 484 the modern one, 26 report
a grand total with no programme breakdown at all, and none mixes the two. Both GARPR 2016 and GAM
2017 contain old-scheme returns, so the cycle is not the discriminator and the label is. The old
scheme is declared out of scope for programme series: "8. Synergies with development sectors" spans
four modern lines and the modern gender, children, social-protection and community lines have no old
counterpart, so a mapped series would begin in 2016 with a definitional break wearing the appearance
of a change in spending. The cost is nil, because every old-scheme country-year lies in expenditure
years 2011 to 2015. Those country-years still contribute their financing split, which does not
depend on the classification.

**Two partitions that do not nest.** The ten modern top-level lines sum to `Total for key HIV
programmes` for 461 of 467 country-years at a median ratio of 1.00000, and to the grand total for
only 389 of 477, because the grand total also holds other essential programmes. Nothing may add a
programme series to a financing series. Nor may anything derive one financing series by subtracting
others: public plus private plus international equals the total for 532 of 540 country-years, the
six international columns sum to International for 423 of 469, the four public columns sum to
TotalPublic for 425 of 495, and the four private columns for 226 of 250.

**The country code is not always ISO3.** Kazakhstan is filed as `KZK` in all 102 of its rows for
expenditure year 2018, so a connector trusting `CountryID` loses Kazakhstan silently, while "Gambia
(Republic of The)" defeats name resolution and its `GMB` code is fine. Code first, name second, and
any disagreement logged. The 121 country-code pairs resolve to 120 countries, and the missing one is
Kazakhstan appearing under two codes rather than a country dropped.

The audit reports 17 of 299 programme labels read, 282 declared out of scope and none unexamined.
The 282 are 252 dotted sub-lines that are parts of lines already read, 11 country-written free-text
lines in Russian, Spanish and French, the 8 old-scheme lines, 4 lines a country filed under other
essential programmes that repeat within a single country-year, 3 pre-2016 other-essential lines, 2
aggregates and 2 residual buckets. A top-level line the map has never seen returns no reason on
purpose, so an eleventh programme line in a future cycle surfaces as undecided instead of being
filed away as free text nobody looks at.

**What the panel gained, measured after the run of 7 September 2026.** Three pairs formed and the
reconciliation layer classified all three from the arithmetic. AIDSinfo against GAM on
`hiv_expenditure_total` is `derived` over 469 cells at a median relative difference of 0.13%, which
is the republication finding recovered without being told. PEPFAR against GAM on
`pepfar_expenditure` is `independent` over 72 cells at 11.8%, and OECD CRS against GAM on
`global_fund_hiv_disbursements` is `independent` over 326 cells at 40.4%. The second and third are
the first pairs in this panel where a donor's account of the donor's own money faces an account
written by the country receiving it, so a difference between the two sides carries information
instead of being an error in one of them.

The PEPFAR pair agrees on the centre and disagrees case by case. Median ratio 1.005 over 30
countries and expenditure years 2021 to 2024, 35 of 72 country-years within 10%, 26 where PEPFAR
reports more and 11 where the country does, direction consistency 0.58. Neither side is
systematically larger, so no constant correction exists. The extreme divergences are one-sided,
Sierra Leone 2022 at 4.57m against 37k and Burkina Faso 2024 at 8.24m against 503k, and both sit in
small programmes, but programme size explains little across the whole set, with a Spearman
correlation of -0.187 between size and the ratio. The natural explanation, that a national AIDS
spending assessment cannot see PEPFAR money spent through regional or centrally procured channels,
has not been tested here and must not be written up as though it had been.

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
| No WCA national source reaches grade 1 | Per-country desk research, [`PHASE4_FEASIBILITY_WCA.md`](PHASE4_FEASIBILITY_WCA.md): NGA login wall plus a stated formal-request policy, COD registration wall, CIV Spectrum output and a RASS series ending 2020 |
| Cameroon's CNLS report is grade 2 and additive | 2024 report opened 2026-08-15: born-digital, all tables extract as text, 123 pages. Ten regions on the ART cascade (Table 38, active file 449,290 national), VL coverage 43.3–91.5% by region against 68.7% national (Table 42), 12-month retention by region (Table 40), KP programme counts with linkage rates (Table 18), 2024 funding by donor with execution rates (Tables 46–49) |
| A DHIS2 login wall is not proof the data is unpublished | Cameroon's report sources every regional table to "2024 DHIS2 database (26/03/2025)" — the same system class that refused six countries in the §4a probe |
| Half of WCA has no PEPFAR data at all | Panel of 2026-08-04: 12 of 24 WCA countries carry 0 `pepfar_*` rows (CPV, CAF, TCD, COG, GNQ, GAB, GMB, GIN, GNB, MRT, NER, STP), holding 632,800 PLHIV in the latest year |
| Naomi is an open API, not just a viewer | `nmviewerserver.azurewebsites.net/api/v1/{countries,options,boundaries,areas}`, no auth, CORS-open, enumerated 2026-08-15: 32 countries, 15 in WCA, 25 indicators, area levels 0–3, `lower`/`mean`/`upper` on every value |
| Naomi is a cross-section, not a series | Period list read for all 32: one historical estimate, then 2025-4, then 2026-3 and 2027-3 as projections (MWI and ZAF add one each). The historical year matches the country's last national HIV survey in 12 of the 15 WCA countries |
| Naomi's national ART figure is not independent | Level-0 `art_current` returns unit-round means (NGA 1,510,000, GIN 98,069, TCD 82,674, NER 19,821); GIN's sits 0.9% from the Global Fund's 2024 figure a year earlier |
| Global Fund results are an open API | `data.api.theglobalfund.org/results/{cycles,stats,table}`, no auth, read 2026-08-15: annual 2017–2024 for 22 of 24 WCA countries, ART series for 10 of the 12 with no PEPFAR; GAB has results but no HIV indicator, GNQ none at all |
| ~~The Global Fund's documented API host is edge-blocked~~ — overturned 2026-09-05, see below | `fetch.theglobalfund.org` returns an Azure Front Door "The request is blocked" page from this network; the Data Explorer backend serving the same data answers normally |
| The block was two retired API versions, not an edge ban | `data-service.theglobalfund.org/api` lists V4.2, V4.1 and V4.0 as live, read 2026-09-05. Every path under `/v2/` and `/v3.3/` returns the block page including the bare root; `/v4.2/odata/` returns data to plain `curl` with no headers, from the same machine and network |
| The Global Fund publishes ART initiations by country and year | `AllProgrammaticIndicators?$filter=programmaticDataSet eq 'Annual_Results'`, run 2026-09-05: 15,313 rows in one response with no `nextLink`, 69 indicator names, 4,797 rows emitted over 9 canonical indicators. *People newly diagnosed with HIV initiated on ART* has 114 rows across 40 country codes 2017–2024 raw, and **93 rows across 33 countries 2021–2024** after the national and country-geography filters |
| The Global Fund's national ART-initiation series starts in 2021 | Every row for 2017–2020 is subnational or multicountry; reporting countries run 17 (2021), 22, 22, 32 (2024) |
| Ethiopia's 2017 testing row is a different quantity from the rest of its series | `hiv_tests_performed`, run 2026-09-05: 7,919,182 (2017) against 293,850, 397,355, 253,245, 295,374, 277,057, 394,488, 337,643 for 2018–2024. A 27-fold break in an otherwise flat series, the shape §8c describes. India's 48.8m and Tanzania's 14.4m are large and continuous, so the check is the break and not the size. Emitted as published, flagged by `writers._unit_outliers` |
| Its `new_diagnoses` series moves the opposite way | `writers._reporter_drops` on the same run: reporting countries 22 (2023) → 8 (2024). Grant reporting arriving late, not diagnoses collapsing |
| `$expand` empties this OData result rather than failing | `$top=1` returns 1 row; `$top=1&$expand=geography` returns HTTP 200 with an empty value array. Joined on `recordId` instead, verified against `/Geographies?$filter=id eq …` resolving to CPV / Cabo Verde |
| A Global Fund row can be subnational and still carry a country geography | 21 of the 114 ART-initiation rows are `geographicCoverage: Subnational`; ZAF 2022 reads 1,531 people. 63 of the 300 geographies are `Multicountry`. Only National rows on Country geographies are emitted |
| The four Global Fund CSVs already in `data/raw/` cannot reach the panel | Read 2026-09-05: `annual-results.csv` 66 rows with no country column, `expenditures.csv` 251 rows with neither country nor year, `funding-requests.csv` 901 rows with a geography and no money, `pledges-and-contributions.csv` 158 rows on the donor side only |
| DHS covers WCA far better than it was being used | `surveyCharacteristicIds=23`: 18 of 24 WCA countries have a survey with HIV biomarkers; the API serves `breakdown=subnational` and the connector never asks for it |
| Every DHS row for DR Congo was being dropped | `to_iso3("Congo Democratic Republic")` returned `None` — the DHS Program's own spelling, absent from `_OVERRIDES` while four others were present. Fixed at `hivimpact/normalize.py:48`; all 92 DHS country names re-resolved, one still unmapped ("Nigeria (Ondo State)", correctly) |
| The additive test has to be applied per table | DR Congo PNMLS GAM 2024 report, read 2026-08-15: 7 tables sourced "Données DHIS2", 4 to the PNLS 2023 report, provincial PrEP to PEPFAR, Tableau LVI to REDES — four classifications in one document |
| PEPFAR Spotlight publishes 15 datasets and the pipeline reads 3 | Dataset paths taken from `data.pepfar.gov/static/js/main.9f74f1e6.js` 2026-08-15; all 15 return 200 unauthenticated from `data.pepfar.gov/media/`; connectors read `Enhanced_Geographical_Analysis`, `Public_Partner_Budgets_and_Expenditures`, `Public_Partner_MER_TopLine` |
| Four of the unread files are additive | `PEPFAR_OU_Budgets_and_Program_Expenditures` (budget from 2004, by Program/Sub Program/Beneficiary, against the partner file's FY2021 start), `PEPFAR_OU_Commodities_Procurements` (planned ARV/RTK quantity and budget, COP18–COP24), `Country_Level_Results_by_Modality_Coarse_Age_and_Sex` (28 modalities, `TX_RTT`, loss-to-follow-up reasons), `HRH_Inventory_Public_Dataset` (FY2025 workforce) |
| Community case-finding falls harder than facility case-finding | `Country_Level_Results_by_Modality`, Q4 FY2024 → Q4 FY2025, modalities grouped by PEPFAR's own `Mod`/`Active`/`SNS` convention: 10 of 12 WCA countries with PEPFAR data; NGA −15.1% vs −4.6%, CIV −33.3% vs −3.4%, CMR −100% vs −10.0%, COD −52.0% vs −12.2%, BFA −86.7% vs +7.0% |
| Nigeria's PEPFAR first-line ARV line is zeroed, not missing | COP24/FY2025 carries *DTG/3TC/TDF 50/300/300 mg, 90 Tablets* as a present row at quantity 0 and budget 0, against 2,550,449 units and 31,153,224 USD in COP23/FY2024; adult ARV 4,667,649 → 863,629 units overall |
| A commodity quantity column changes unit between years | NGA *HIV-1/2, Determine, 100 Tests*: 75,757 units at 6,484,799 USD (85.60 each, a pack) in FY2024; 5,965,515 units at 4,772,412 USD (0.80 each, a test) in FY2025 — identical item string |
| FY2025 publishes Q4 only | Spotlight's own front page, and confirmed in the files: FY2025 Q1–Q3 columns are empty in every MER download, so no FY2025 annual total exists for a cumulative indicator |
| UNAIDS publishes GAM programme expenditure as one open file | `hivfinancial.unaids.org/GARPR16-GAM2025ProgrammeExpenditures-20250903.xlsx`, 5,497,605 bytes, no auth, read 2026-08-15: 59,947 rows, 121 countries, cycles GARPR 2016–GAM 2025, expenditure years 2011–2024, 18 of 24 WCA countries, 8 with 2024 |
| It carries domestic and household money nothing else in the panel has | Columns 5–14: central and sub-national government, development banks, social security, private insurance, **households**, corporations, non-profits; columns 15–21 split external by PEPFAR, Global Fund and other |
| Its zeros mean "not reported" | MLI 2024: 3,184,591 USD domestic, 0 international, while `data.api.theglobalfund.org` shows active disbursing HIV grants in Mali that year. GMB 2024 totals 33,054 USD; TCD reports 21.7m USD international with no donor split |
| GAM and the national NASA reports agree, and that is not triangulation | BEN 2024: 14,757,867 USD against 9,292,143,634 FCFA in the NASA report (3–5% apart, inside the exchange rate). COD 2021: 223,877,209 / 163,912,882 USD against 227.8m / 167,861,131 in Tableau LVI (under 3%). Both pairs are one national exercise published twice — fidelity, not corroboration |
| IATI is open through d-portal and is current to this month | `d-portal.org/q?from=act,trans`, sector 13040, no key, read 2026-08-15: 26 publishers reporting HIV activity in Nigeria including UNAIDS itself, Gates, FCDO and NGOs; latest WCA disbursement dated 2026-08-15, against OECD CRS running 12–18 months behind |
| Its transaction-type column mixes vocabularies | `D`, `E`, `C`, `11`, `IF`, `R`, `IR`, `LR` returned by the same query; 1,834 of 46,964 distinct activity/date/value keys appear under more than one code |
| `sum()` in the d-portal query API returns zero silently | Every aggregate query returned 0 or null; the same rows pulled raw and summed in Python give NGA HIV disbursements 395,198,777 (2024) → 330,726,636 (2025) |
| UNICEF SDMX is mostly a republication | `HIV_AIDS` dataflow, 139,446 rows, read 2026-08-15: of 26,242 WCA rows, 21,460 are sourced "UNAIDS 2025 estimates" and 1,270 to Global AIDS Monitoring; the additive slice is 3,512 MICS/DHS rows with `WEALTH_QUINTILE` and `RESIDENCE`, latest MICS 2019 and latest DHS 2022 |
| IHME DAH is open but behind a user agreement | GHDx record `ihme-data/dah-1990-2026-20260611`, released 2026-06-11, 1990–2026; downloads route through `ghdx.healthdata.org/download-access/login` under a free non-commercial user agreement — a manual drop into `data/raw/`, the same pattern as the UNAIDS AIDSinfo CSVs |
| Nigeria's national dashboard is public and unreachable by machine | `wallboard.nascp.gov.ng`, refreshed 2026-02-20: 1,593,757 on ART, 953,709 suppressed, state selector, PrEP/HTS/ART/PMTCT tabs. `modelsAndExploration`, `explore/…/exploration` and `conceptualschema` all return 403 to scripted requests with the correct cluster and resource key and matching Origin and Referer; renders correctly in a browser |
| Chad publishes its DHIS2 contents as a yearbook | `inseed.ssn-tchad.td` serves one 3,239-byte shell for every path; endpoint recovered from its JS bundle. `/api/menus` returns `401 Token d'accès requis`, `/api/publications/search?q=` returns the series 2005–2023. The 2023 edition (286 pages, July 2024) carries Tableau 306, the ART cohort by province with stock, inclusions and transfers |
| A shell response is not an absent source | Three hosts returned an identical short page for every path — `inseed.ssn-tchad.td` (3,239 bytes), `data.pepfar.gov` (1,993 bytes) and IHME's FGH viewer — and in all three the real addresses were hardcoded in `/static/js/main.*.js` |
| Ghana's NASA international line is derived from donor ledgers | Stated in the report's own methods section: built from Global Fund principal-recipient records and the PEPFAR expenditure report. Its domestic public, household and private lines are independent |
| Togo's 2023 yearbook is unrecoverable by any route tried | `sante.gouv.tg` redirects to `sante-assurances.gouv.tg` and returns `text/html` for the `.pdf` path; the PNLS site returns 500; the Wayback capture is exactly 5,242,880 bytes — the archive's 5 MiB cap, which keeps `%PDF` and the page objects but loses the trailer, so `pypdf` cannot open it |
| WHO AFRO's data portal is gone | `aho.afro.who.int` returns 404 at every path including the root; only the Azure blob container behind it answers, with listing disabled, so it serves exact blob names and a 404 there is not evidence of absence |
| The Global Fund API carries no PU/DRs | Documents entity read 2026-08-15: 2,283 items in nine types — funding requests, concept notes, country profiles — all qualitative |
| WHO's TB dataset carries 100 HIV variables | `extranet.who.int/tme/generateCSV.asp?ds=dictionary`, read 2026-08-17: 698 variables across 19 datasets, 100 of them HIV-related across 9 — 30 in Notification, 23 in Outcomes, 21 in Estimates, 8 in non-routine HIV surveillance |
| TME's ART totals are an independent channel, not a republication | `hiv_all` against the panel's UNAIDS on-ART series, 180 shared country-years: within 1% in 32%, more than 10% apart in 28%, median gap 2.2% |
| TME carries ART initiations for all 24 WCA countries | `hiv_reg_new2`: 998 rows, 2013–2024, 153 countries, 24 of 24 in WCA. COD 107,468 (2020), 96,516, 97,177, 83,436, 65,651 (2024) with no missing year; CMR 75,954 (2021) → 38,059 (2024); CIV 40,703 (2020) → 26,765 (2024) |
| The initiation series is ragged and must be read only on consecutive years | GIN reports 61,197 (2020) and 7,884 (2024) with nothing between; of the 24 WCA countries only COD reports every year 2019–2024 |
| `hiv_new` is the same variable under a second name | Identical in 94% of the 235 country-years carrying both; mapped as a gap-filler that adds exactly 39 country-years, with the source column stamped per row |
| Expected USAID funding to national TB programmes falls 58% in 2025 | TME budget file: 134,747,052 USD (2018) → 235,509,731 (2024) → 98,701,987 (2025); countries expecting anything 31 → 23. The budget file reaches 2025, the expenditure file stops at 2024 |
| The TB funding columns are exposure and not HIV money | `cf_tot_usaid` and siblings are whole-TB-programme totals; mapped under `tb_funding_*` and excluded from any HIV financing total |
| Gabon's 2024 expenditure row is CFA francs in USD columns | `exp_tbhiv` 325,375,873 against that country's own median of 9,836 (33,000×); `rcvd_tot_gf` 731,795,829. Emitted as published; caught by `writers._unit_outliers` |
| The TME connector emits a clean panel slice | 23,705 rows over 20 mapped columns, 215 countries, 2000–2025, 0 duplicate panel keys; 19 offline controls pass |
| GHO's reported ART is not the modelled series republished | `HIV_0000000009` against the panel's UNAIDS figures, 2,030 shared country-years: 1% identical, 52% within 1%, 13% more than 10% apart. It also reaches 1,766 country-years the panel held no ART figure for, 170 of them 2023 or later |
| GHO un-censors UNAIDS from outside | Maldives is `<100` throughout AIDSinfo; GHO reports 2, 3, 5, 6, 8 people for 2010–2014, rising to 39 in 2025 |
| GHO carries testing volume and positivity, which the panel did not have | `HIV_0000000027` and `HIV_POSITIVITY`: 936 rows, 143 countries, 2022–2024, 19 of 24 WCA. NGA 2022: 12,390,356 tests at 2.38% all ages, 2.17 women 15+, 3.31 men 15+, 0.92 under 15 |
| The testing splits partition the all-ages total | Women 15+, men 15+ and under-15 sum to the all-ages figure exactly in 82% of country-years — the same one-level-or-the-other rule as the PEPFAR agency split |
| A GHO catalogue name can be wrong about its own indicator | `HIV_0000000020`, catalogued *Estimated number of pregnant women living with HIV*, returns 69, 67, 64, 63, 56, 61 for Nigeria. It is PMTCT coverage: 36,701/53,000 = 69.2% (2020) and 26,566/47,000 = 56.5% (2024), the numerator from `HIV_0000000016` and the denominator from `HIV_0000000021`. Not mapped |
| Two GHO codes share one catalogue name and one of them is empty | `HIV_0000000015` and `HIV_0000000016` carry identical names; 15 returns `{"value":[]}` |
| The GHO connector was discarding the age dimension and could not read its own sex codes | These series return `SEX_BTSX`/`AGEGROUP_YEARSALL`; the map knew only bare `BTSX`. All 19,400 `who_gho` rows in the 2026-08-15 panel are `sex='all'`, so the original seven series carry no sex dimension and the map had never been exercised |
| Nigeria's National Data Repository is an open JSON API | Three endpoints confirmed 2026-08-17: `ndr.nascp.gov.ng/public/GetRecencyData/`, `ctd.nascp.gov.ng/facilitydata/`, `ndr.nascp.gov.ng/public/surveillance-report`. Plain `curl` returns HTTP 000; HTTP/1.1 with a browser UA and `Referer: …/public/wallboard` returns the data |
| Nigeria's national treatment figure, December 2025 | 1,672,219 on treatment against 1,904,364 PLHIV, 87.8%, all 37 states. The endpoint takes no parameters, so it is a snapshot with no history and re-runs are new snapshots |
| NDR and GHO are independent instruments for Nigeria | 1,672,219 (NDR, Dec 2025) against 1,550,000 (GHO reported ART, 2025) — about 8% apart, no shared origin |
| State treatment exceeds state PLHIV in several Nigerian states | Bauchi 158%, Adamawa 121%, Benue 115%: patients are counted where treated, not where resident. The source ships the correction as `txcurr_res_state` / `txcurr_res_outof_state`; a state coverage figure computed without it is wrong |
| UNAIDS censoring floors reach 66,291 cells | `<100`, `<500`, `<0.1`, `>98` in the AIDSinfo CSVs. UKR `hiv_expenditure_total` reads 100 USD for 2018, between 108,000,000 (2017) and 100,000,000 (2019). `_floor_values` names 12 affected groups across 3 connectors in the 2026-08-15 panel |
| The unit check has two readings and only one is a unit error | 2026-08-15 panel: 247 rows flagged, 17 above their series and 230 below. 42 of the low side are `hiv_expenditure_total` at exactly 100 USD, which `_floor_values` independently names as a censoring floor; ZAF 2021 TB/HIV reads 42 and 37 against a normal six figures |
| WAHO is the sixth gated DHIS2 | `waho.dhis2.org`, probed 2026-08-17: all five unauthenticated paths redirect 302 to the login page |
| WHO AFRO's observatory is dead, and its atlases are republications | `aho.afro.who.int` 404 at every path; the surviving country atlases are 2022 PDFs carrying GHO and UNAIDS figures the panel already holds |
| Chad's INSEED publishes ten health statistics yearbooks, and its search hides them | Catalogue enumerated 2026-08-17: 135 publications in 15 series, including `ANNUAIRE-STATISTIQUES-SANITAIRES-2023` (published 2024). `q=sante` returns 0 and `q=VIH` returns 0; the endpoint matches title text and the titles read `SANITAIRES` |
| WHO GHED carries an HIV line and is independent of GAM | `apps.who.int/nha/database/Home/IndicatorsDownload/en`, 38.9 MB, open. Built from national health accounts, not from the GAM submission. `dis11` splits into `_gghed`/`_ext`/`_pvtd`. Release read from the Version sheet: 12 December 2025 |
| Every `dis11` money variable is in millions, not `dis11_usd` alone | Corrects the second half of the row above, which claimed `dis11_usd` was in millions "while its neighbours are not". The codebook marks all eight `Millions`. Three checks agree: printed `dis11_che` equals `dis11 / che * 100` to the sixth decimal on all 359 country-years (ZMB 2019, 13,225.51 / 20,290.29 = 65.181457 against a printed 65.181458); `dis11_usd / dis11_usd_pc` implies populations of 109,821 to 223,150,896, median 15,895,315; the resulting totals sit alongside GAM's for the same country-years |
| GHED's HIV line is HIV **and** other STDs, so it is not a second reading of the GAM series | `dis11` is "HIV/AIDS and Other Sexually Transmitted Diseases". Against GAM over the country-years both cover: total, 138 country-years / 44 countries, median ratio 1.14, 48 differing by 2× or more; government, 134 / 43, median 1.22, 68 differing by 2× or more; external, 129 / 39, median 1.002 with GHED larger in 65 of 129. Coinciding centres with coin-flip direction is not agreement. Mapped to seven `hiv_std_*` canonicals of its own |
| The three GHED financing components are a true partition, unlike GAM's | Government plus external plus private equals the printed total on 328 of 328 country-years, median ratio 1.000000. GAM's printed parts fail to close on about a tenth. Every row carries `extra.partition_level` = `total` / `component` / `share` so nothing sums the two levels |
| A zero means opposite things in GAM and in GHED, and the file decides which | GAM leaves an unfilled line at zero, so no zero is emitted there. GHED's seven zero component cells all sit in accounts whose remaining parts still close on the printed total (CRI 2020 and MKD 2019–2020 external, UZB 2016–2018 and HTI 2016 private), so each is an entry in a closed account and is emitted. Blank is how GHED says nothing is known |
| GHED's HIV line stops before the event this project measures | The workbook runs to 2024; the HIV line covers 359 country-years over 60 countries, 2013–2023. Countries per year: 20, 29, 32, 46, 47, 51, 51, 32, 26, 15, 10. The last year present is not the current position, and this source cannot see the 2025 cuts at all |
| HIV is a large fraction of the whole health system in the countries at issue | `dis11_che` reaches 65.2% in ZMB 2019, and 46 country-years exceed 20%, every one in Eastern or Southern Africa (ZMB, MWI, MOZ, ZWE, UGA, TZA, SWZ, BWA, KEN). A cut to HIV in these places is a cut to a large fraction of health spending, which is what makes the share an exposure measure rather than a descriptive one |
| WHO publishes whether each GHED figure was documented or estimated, and the panel carries it | Metadata sheet, 32,664 rows, as text like "2013 - 2018: Documented; 2019: Estimated". All 59 country records for `dis11` parse, labelling 340 of the 359 country-years: 303 documented, 35 estimated, 2 partially documented. The private component is filed for 57 countries rather than 59, which leaves 43 of 1,381 money rows unlabelled. Carried as `extra.data_type`, because an estimation method read as a funding cut is the failure mode |
| The GHED download carries no version in its filename | `Content-Disposition: attachment; filename=GHED_data.XLSX` for every release, unlike the GAM workbook whose filename carries its publication date. A cached copy cannot be told from a current one by name, so the connector reads the release off the Version sheet, logs it every run and writes it into every row. Deleting the cached file is how a new release is taken |
| `run_all.py` defaults to the Southeast Asia slice, so a global connector run without `--countries all` silently returns a region | The GHED run of 7 September 2026 was launched as `--sources who_ghed` alone and landed 125 rows over KHM, MMR and PHL, against the 2,430 rows over 60 countries the workbook holds. Nothing in the log says the scope was narrowed, because the connector reports what it found inside the filter it was given. Every other aggregator in the panel is global (world_bank 216 countries, who_tme 215, who_gho 194, unaids_aidsinfo 193, oecd_crs 153, foreign_assistance 124, unaids_gam_expenditure 120, global_fund 107), so a two-figure country count on an aggregator is the tell |
| The Philippines 2019 HIV line is 26 times its own series and reaches the panel unflagged | `dis11` reads 65,907.48 million pesos for 2019 against 1,122.41 in 2018 and 5,430.60 in 2020, so `dis11_usd` reads 1,272,448,707 USD between 21,313,702 and 109,434,836. The anomaly is in the source's own national-currency figure, not in the conversion, and `dis11_che` carries it too at 8.10% against 0.16 and 0.59, so WHO's published share is computed from the same number. WHO labels the year **Documented**, so the metadata does not warn either. Emitted as published, following the Gabon precedent |
| `writers._unit_outliers` cannot see an outlier that is large enough to set its own reference | The Philippines series has 10 rows with a log10 median of 7.684 and a MAD of 0.563, above `SCALE_STABLE_MAD` (0.5), so the series is skipped whole as having no stable scale to depart from. Even without that gate the row survives, because the threshold is `max(log10 25 = 1.398, 4 × 0.563 = 2.252)` and the departure is 1.421. Both tests fail for one reason: a 26× spike inside a series that genuinely climbs an order of magnitude inflates the spread being used to judge it. The check is behaving as designed and the design has a blind spot for short, steeply growing money series |
| The reconciliation table can never test whether GHED is a republication of an existing series | `hivimpact/reconcile.py` compares two sources only where both report the same `indicator_id`, and the seven `hiv_std_*` canonicals belong to `who_ghed` alone, so no pair can form at any scope. The 87 pairs from the global run of 7 September 2026 name `who_ghed` in none of them, and an empty result produced by construction is not evidence. The test has to be made by hand against `hiv_expenditure_total`, which is HIV alone. On the 164 overlapping country-years across 49 countries the ratio has a median of 1.141 and a middle half of 0.854 to 1.760, GHED is larger on 102 of 164, and only 4 pairs agree within 2% (29 within 10%). A republication would sit at 1.000 throughout, so the separate canonicals stand. Containment does not hold either, and should not, because the national health accounts count HIV and STD spending flowing through the health system while GAM counts the AIDS programme. The tails belong to the UNAIDS side, not to GHED: MDG 2019 reaches 2,647 because UNAIDS records 3,900 USD of total HIV spending that year against 12,000,000 in 2017, and AFG 2017 reaches 274 on a UNAIDS figure of 45,000 USD |
| GHED's three flagged rows are small components inside accounts that close, not unit errors | `writers._unit_outliers` flags exactly three `who_ghed` rows out of 2,430, all on the low side: ARM 2021 external 198.50 USD, ARM 2021 external share 0.0013% (the same figure said twice) and BEN 2013 private 35,135 USD. Both country-years close on their printed total at a ratio of 1.000000, so a tiny component is what the account contains. 60 of the 1,381 money rows sit below 100,000 USD and 12 below 10,000, so small components are ordinary in the national health accounts rather than a symptom. The flag is worth reading as a prompt to check closure, not as a defect |
| The GHED connector accounts for all 4,120 columns with none undecided | Verified offline 2026-09-07 against the cached workbook: 7 read, 4,113 with a written reason (3,372 health-system aggregates, 649 other disease categories, 47 `dis12` tuberculosis, 16 constant 2023 prices, 8 per capita, 5 identifiers, 5 GDP or government-spending denominators, 4 national currency, 4 purchasing-power parity, 3 recoverable component shares), 0 awaiting a decision. A future `dis11` variable matching no rule returns `None` and surfaces as undecided rather than being filed away |
| ART initiations now have two independent instruments, and they agree without matching | WHO TME against the Global Fund, 75 country-years over 29 countries: within 1% in 24%, within 10% in 63%, more than 25% apart in 24%, median gap 3.5%. `tbhiv_on_art`: 571 country-years, 87 countries, 37% within 1%, 70% within 10%, median gap 2.8% |
| Comparing two instruments needs the age group matched, not just country and year | WHO TME publishes `tbhiv_on_art` for all ages and for under-15s as separate rows, 226 of the latter. Keying on country and year alone sets a national figure against a paediatric one and moves the median gap from 2.8% to 6.1% |
| Both instruments show ART initiations falling into 2024 | WHO TME, 88 countries reporting both 2023 and 2024: 46 fell, total −14.4%. Global Fund, 21 countries: 14 fell, total −29.6%. Of 45 consecutive-year changes both can see, 33 agree on direction and 12 do not |
| The censoring-floor check fired on three WHO TME columns that are not censored | `tbhiv_deaths` reads 461 zeros, 315 ones, 179 twos, 98 threes. Dropping zeros before taking the mode leaves the smallest printable count as the mode of any small-count series. Fixed by counting zeros towards the series: 12 genuine floors carry none, the three WHO TME columns are a tenth to a quarter zeros |
| A spike against the next value up does not separate a floor from a small count | UNAIDS `new_infections` is a genuine floor at 2.74 times the count at 200 and WHO GHO at 2.08, against 2.2 for `tbhiv_on_art`, which is not censored. Any threshold keeping the real floors admits the false ones |
| The UNAIDS censoring and DHS country-name fixes are confirmed in the data | `hiv_expenditure_total` 961 rows with none at exactly 100 USD, against 42 and a 273-row floor warning before. DHS returns 9 rows for COD across 2007, 2013 and 2023, where the name mismatch returned none |
| The community-led monitoring sentinel's HTTP 500s are the documented empty-quarter behaviour, not an outage | Every 2023-Q1 fetch across all eight indicators returned 500 on 2026-09-05, as the connector has recorded since July 2026. The server raises an unhandled `KeyError` and serves a Django debug page (`/home/brian/CLM_DB/interface/api.py`, line 256) for any request it cannot satisfy. The same run wrote 23 rows over 2023–2025 on all eight indicators |
| The TB preventive services the Global Fund counts are not a single-source series | UNAIDS AIDSinfo publishes the proportion counterpart of all three, in `data/raw/unaids/`: newly enrolled started on TPT (131 countries, 2013–2024), currently enrolled started on TPT (106, 2017–2024), completed a course of TPT (58, 2019–2024) |
| A connector can report a clean run while skipping most of what it was given | `unaids_aidsinfo` classifies by filename substring against 11 core names and counts the rest as skipped. 114 of 146 exports were never read, reducing to 111 distinct indicator names |
| Seven of those unread exports are TB and HIV, and hold about 14,100 cells | Co-management of TB and HIV treatment (168 countries, 2000–2024, 2,536 cells), incident TB cases in PLHIV (192, 4,749), TB-related deaths in PLHIV (191, 4,734), plus the three TPT proportions and TB disease at enrolment |
| UNAIDS censors 62% of the incident-TB series and none of the TB-deaths series | `Incident TB cases in people living with HIV`: 2,934 of 4,749 cells are `<100`. `TB-related deaths among people living with HIV`: no censoring at all and 714 zeros, which is the shape the corrected floor detector has to leave alone |
| The run of 2026-09-05 landed all nine new canonicals | Panel 159,063 rows. `unaids_aidsinfo` mapped 32 files against 25 before, 39,451 rows. Global Fund: `tpt_initiations` 341, `plhiv_tb_screened` 272, `tpt_completions` 8, `tbhiv_on_cpt` 3. UNAIDS: `tbhiv_comanagement_pct` 2,536, `plhiv_new_tb_diagnosed_pct` 971, `tpt_initiation_new_pct` 709, `tpt_initiation_current_pct` 294, `tpt_completion_pct` 128 |
| The UNAIDS TB/HIV burden exports are WHO republished, not a second instrument | `tbhiv_deaths`: of 4,302 overlapping country-years, 3,941 identical non-zero, 315 zero in both, 46 differ. `tbhiv_incidence`: of the 1,815 uncensored overlaps, 97.5% identical, 99.0% within 1%. Against ART initiations, where the two instruments are genuinely independent, exact agreement is 8% |
| The UNAIDS incident-TB export adds no point estimate anywhere | All 497 of its country-years beyond WHO TME are censored `<100` bounds, and it censors 2,934 cells WHO TME publishes as numbers. The deaths export is uncensored, so its 432 extra country-years are kept |
| The Global Fund TPT count pairs with the currently-enrolled proportion, not the newly-enrolled one | Over `art_initiations`: within 1pp in 41 of 181 country-years, median gap 11.5pp, above 100% in 32, SWZ 2024 at 3,093% on 194,482 courses against 6,288 new enrolments. Over `on_art_count`: within 1pp in 48 of 111, within 5pp in 76, never above 100% |
| The censoring check was labelling reporting ceilings as floors | AIDSinfo censors at both ends and `>98` is a ceiling. 148 WHO GHO `viral_suppression_pct` rows and 141 UNAIDS `pmtct_coverage_pct` rows sit at exactly 98, which is the largest value either series contains. The three cases separate on where the repeated value sits: series minimum, series maximum, or neither, the last being UNAIDS stacking `<100` and `<500` in one file |
| `pepfar_panorama` was reading 2 of the 71 MER indicators in the file it opens | `Public_Partner_MER_TopLine.zip`, counted 2026-09-05 by [`scripts/audit_coverage.py`](../scripts/audit_coverage.py). The 69 unread codes included `TX_NEW`, `HTS_TST`, `PrEP_NEW`, `TX_ML` and `TX_RTT` |
| PEPFAR `TX_NEW` is `art_initiations` measured by the funder being cut | 1,894 valued rows, 57 countries, FY2018–2025, one row per mechanism, `Total Numerator` only, no age or sex disaggregate to double count |
| MER quarters are independent periods, not a running total | FY2024 `TX_NEW` reads Q1 390,160 / Q2 414,358 / Q3 383,029 / Q4 464,878, so the annual value is the sum. `TX_CURR` rises within each year, so it stays a snapshot at the latest quarter |
| PEPFAR `TX_NEW` is a share of the WHO TME national total, not a rival estimate | 266 overlapping country-years: PEPFAR at or below the national total in 86%, median share 0.74, quartiles 0.38 and 0.98. Fifteen exceed 1.25, led by MLI 2020 at 5.19 and UGA 2019 at 1.98; PEPFAR's Oct–Sep fiscal year against WHO's calendar year explains part |
| `TX_NEW` adds 88 country-years WHO TME does not cover | 38 countries, 2018–2024, where `who_tme` publishes no `art_initiations` figure |
| `TX_ML` is the exact sum of its seven sub-codes | 312 country-years, agreement within 1% in 100%, so mapping the total alone is correct and mapping the parts as well would double count |
| Three of 15 PEPFAR archives are read, and four Global Fund CSVs are read by nobody | Unopened: health workforce inventory, commodity procurements, partner performance, both site-level files, both age/sex cascade files, OU budgets, OU-by-fine-age-sex, modality results, VMMC. The Global Fund connector reads the OData API, so `data/raw/global_fund` is downloaded and unattached |
| The province and national PrEP series are different grains, not duplicates | `pepfar_snu` sets `admin1` on 100% of its 2,096 `prep_recipients` rows; `pepfar_panorama` writes the national total with `admin1` empty, the same separation `on_art_count` already has |
| Every one of the 146 AIDSinfo exports is now mapped or declared | `scripts/audit_coverage.py` reports 51 read, 95 declared out of scope with a reason, 0 unexamined. Before this pass the same script reported 32 read and 114 unexamined |
| UNAIDS `HIV tests (volume)` is WHO GHO reprinted, not a second measurement | 323 overlapping country-years, exact agreement in 100.0%. Mapped only for the 92 country-years GHO does not carry, and never to be counted as corroboration |
| UNAIDS `Pregnant women needing ARV for PMTCT` is a genuinely independent second measurement | 759 overlaps against WHO GHO, exact in 17.4%, median gap 6.8%, against the Global Fund–WHO TME independence benchmark of 8% exact and 3.5% median gap |
| `pmtct_arv_count` and `hiv_test_positivity_pct` are largely republications | 1,515 overlaps at 76.7% exact with a median gap of 0.0%, and 289 overlaps at 22.5% exact with 65.1% within one percentage point, UNAIDS printing two decimals where GHO rounds |
| The key-population exports are single points, not series | All 37 carry one column, `Most recent data as of 2024`. The two mapped supply a denominator (552 values) and a baseline (156 values), and the rows carry `extra["most_recent"]` so no analysis reads the 2024 stamp as a 2024 measurement |
| The two-row-header cascade files are the largest unread body left in AIDSinfo | `Progress towards 95-95-95` and `Testing and treatment cascade`, All-ages pair holding 3,532 and 3,660 values across 176 and 185 countries from 2015. Held back because the conditional bars need a decision, not because the parser is hard |
| Six of the 66 unread MER codes had a canonical already waiting in the registry | `TX_PVLS`, `TB_PREV`, `TB_STAT`, `TB_STAT_POS`, `PMTCT_ART`, `VMMC_CIRC`. Exact agreement with the national series is 0.0% for five and 1.0% for `VMMC_CIRC`, median share 0.58 to 0.91, at or below the national total in 82–96% |
| `TX_PVLS` is a rolling twelve-month snapshot, not a sum of quarters | Summed it reaches a median of 2.32 times `TX_CURR` and exceeds the treatment cohort in 70% of 399 country-years. Read at the latest quarter, median 0.71 and excess in 1% |
| `TB_PREV` and `KP_PREV` are semi-annual, so two quarters is a complete year | Q2 and Q4 in 204 of 258 and 304 of 362 country-years. Without the exception the partial-year warning fires on every `tpt_completions` row |
| `KP_PREV` cannot be collapsed on arithmetic | Summing the half-years gives a median of 0.58 of the Global Fund national figure over 142 overlaps, taking the later half gives 0.29. A factor of two between two defensible readings |
| Every one of the 71 MER codes is now mapped or declared | `scripts/audit_coverage.py` reports `pepfar_panorama` 11 read, 60 declared, 0 unexamined, and `pepfar_agency` 3 read, 68 declared, 0 unexamined. Before this pass the same script reported 5 and 3 read with 66 and 68 unexamined |
| Reporting frequency changes within a code, so no fixed list can hold it | `TB_STAT` and `TB_STAT_POS` at Q2 and Q4 in FY2018 and quarterly after, `PrEP_NEW` quarterly in FY2018, at Q2 and Q4 in FY2019 and FY2020, quarterly from FY2021 |
| A semi-annual PEPFAR figure covers six months, so a two-quarter year is whole | `TB_STAT` across its FY2019 change gives a full-year ratio of 0.99 against a like-quarter 0.53, and `TB_STAT_POS` 0.96 against 0.49. `PrEP_NEW` across its FY2019 change gives 3.10 and 6.05, a factor of 1.95, which growth cannot produce because both ratios carry it |
| Deriving the cadence removes 93 false partial-year warnings and keeps every true one | Replayed over `Public_Partner_MER_TopLine` Total Numerator rows: 381 operating-unit-years flagged under the fixed count, 288 under the derived cadence, the 93 difference being `PrEP_NEW` FY2019 and FY2020 and `TB_STAT` and `TB_STAT_POS` FY2018. All 33 FY2025 `TX_NEW` operating units still flagged |
| `circumcisions_performed` is absent from FY2025 rather than zero | `VMMC_CIRC` reports `0000` for all 14 countries in the Q4 release, so no row is emitted |
| The GAM expenditure database is the only near-global source that asks the country who paid | `hivfinancial.unaids.org`, one workbook, 59,947 rows, 121 country codes resolving to 120 countries, 541 country-years, expenditure years 2011–2024, 41 of them 2024. Cycles GARPR 2016 to GAM 2025, and UNAIDS has already kept the latest return where a country reported one year twice: every country-year appears in exactly one cycle |
| GAM's PEPFAR column pairs with PEPFAR's own account, and the arithmetic said so | Against `pepfar_expenditure` n=72, median 0.995, 35 within 10% (49%). Against `external_hiv_oda_us` n=205, median 1.031, 54 within 10% (26%). GAM's GlobalFund against OECD CRS n=326, median 0.806, 47 within 10% |
| GAM's grand total is AIDSinfo's country-reported expenditure republished | n=469, median ratio 1.0000, 420 within 1%, the residual being AIDSinfo rounding to two significant figures. Emitted anyway so the reconciliation layer reaches the `derived` verdict from the data |
| GAM programme numbers move between cycles and the labels do not | `3.11` is "Cash transfers to girls (high-prevalence countries)" from GAM 2017 to GAM 2023 and "Prevention programmes for vulnerable and accessible populations (excluding HIV testing)" from GAM 2024; `3.12` moves from vulnerable populations to post-exposure prophylaxis at the same cycle |
| Two GAM classification schemes, separated by the label and not by the cycle | The old scheme writes `4. Universal access to treatment` and the modern one `4 Gender programmes`. 31 country-years old, 484 modern, 26 with no breakdown, none mixed. GARPR 2016 holds 23 old-scheme country-years and GAM 2017 holds 8. Every old-scheme country-year is in expenditure years 2011–2015 |
| The ten GAM programme lines partition key programmes, not the grand total | Sum to `Total for key HIV programmes` in 461 of 467 country-years, median 1.00000; to the grand total in 389 of 477. The grid is complete: exactly one of each of the ten in all 484 modern country-years, no duplicates |
| No GAM financing series may be derived by subtracting others | Public + private + international equals the total in 532 of 540 country-years, the six international columns sum to International in 423 of 469, the four public columns to TotalPublic in 425 of 495, the four private to TotalPrivate in 226 of 250 |
| A GAM zero is indistinguishable from a GAM blank, and both mean not reported | On the grand-total row Households is blank 13 times and zero 375 against 153 positive, PEPFAR blank 14 and zero 313 against 214, TotalPrivate blank 11 and zero 278 against 252. 3,499 cells dropped on this rule across the file |
| GAM files Kazakhstan under a code that is not ISO3 | `KZK` on all 102 of its expenditure-year-2018 rows, while "Gambia (Republic of The)" defeats name resolution and its `GMB` code does not. Code first and name second resolves all 121 pairs with no disagreement |
| Every one of the 299 GAM programme labels is now mapped or declared | `scripts/audit_coverage.py` reports 17 read, 282 declared out of scope, 0 unexamined: 252 dotted sub-lines, 11 free-text lines, 8 old-scheme lines, 4 lines filed under other essential programmes that repeat within a country-year, 3 pre-2016 other-essential lines, 2 aggregates, 2 residual buckets |
| The reconciliation layer reaches the republication verdict on its own | Run of 7 September 2026. `hiv_expenditure_total` AIDSinfo against GAM, 469 cells, median relative difference 0.13%, agreement within 2% on 96% of cells, classified `derived`, evidence "same underlying estimate, not corroboration" |
| The panel now holds two independent accounts of PEPFAR money and two of Global Fund money | Same run. `pepfar_expenditure` PEPFAR against GAM, 72 cells, median relative difference 11.8%, classified `independent`. `global_fund_hiv_disbursements` OECD CRS against GAM, 326 cells, median relative difference 40.4%, classified `independent` |
| Donor and recipient agree on the central tendency of PEPFAR money and disagree country by country | 72 country-years, 30 countries, expenditure years 2021 to 2024, median ratio 1.005, 35 within 10%, 26 where PEPFAR reports more and 11 where the country does, direction consistency 0.58 |
| Programme size does not explain the PEPFAR divergence | Smallest quartile by PEPFAR-reported size has median ratio 1.19 and 8 of 18 within 10% against 11 of 18 in the largest, but the Spearman correlation of size with the ratio is -0.187. Sierra Leone 2022 is 4.57m against 37k and Burkina Faso 2024 is 8.24m against 503k, so the tail is one-sided while the body is not |
| The GAM rows raise 44 validation warnings and none is a defect | All 44 lines in `data/panel/hiv_panel.validation.txt` naming `unaids_gam_expenditure` are `reporting countries` lines, which record voluntary participation changing between years. No GAM series tripped a scale, percent-range or censoring-floor warning |
| The site was publishing reconciliation verdicts from a panel that no longer existed | `reconciliation_pairs.csv` and `reconciliation_cells.csv` were dated 20 July 2026 against a panel of 7 September 2026, because `run_all.py` never called `reconcile.run()` and no script wrapper existed. `run_all.py` now regenerates them after writing the panel, and `build_site.py` warns before building when the tables are the older file |
| Six pairs in the panel are one source reprinting another | Regenerated tables give 87 source pairs, 61 independent, 11 subset, nine insufficient and six derived. The six are `hiv_expenditure_total` (AIDSinfo and GAM, 469 cells), `hiv_prevalence_15_49` (AIDSinfo and World Bank, 3,693), `tbhiv_deaths` (AIDSinfo and WHO TME, 4,302), `hiv_tests_performed` (AIDSinfo and WHO GHO, 323) and `know_status_pct` twice (Thembisa against AIDSinfo, 16, and against WHO GHO, 11). None may be counted as corroboration |
| Four money indicators in the panel double if summed across their sources | `external_hiv_oda_us` has 3,194 rows sharing a country-year with a second source, `hiv_expenditure_total` 938, `global_fund_hiv_disbursements` 652 and `pepfar_expenditure` 144. The data page now states the count on every affected indicator, 30 of the 33 multi-source indicators in all |
