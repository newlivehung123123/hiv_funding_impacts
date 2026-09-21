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
the geographic total is the safer one. Since 19 September 2026 `pepfar_panorama` holds every row
against the geographic file on every run and records the geographic figure on any row more than
five per cent away (§9w).

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

### 9l. The file that measures the mechanism, and the defect it found in two connectors already built

§7b said to enumerate the family before declaring a source read, and the PEPFAR Spotlight catalogue
had 12 zips nobody had opened. The first of the four §7b named as additive is
`Country_Level_Results_by_Modality_Coarse_Age_and_Sex`, 14,033 rows over 59 countries, one row per
country, indicator, coarse age, sex and modality.

Modality is how the person was reached. Every other PEPFAR series in this panel counts services
delivered. This one counts the route, and the route is the part of a programme a funding cut
removes first. Facility testing is a nurse offering a test to somebody who already walked into a
clinic, and it costs almost nothing extra once the clinic is open. Community testing is a van, a
fuel budget, an outreach team and a per-diem, and it is a line item that can be cancelled in a
week without closing anything.

The §9f test ran first, because a new file naming a quantity the panel already holds is a
hypothesis and not a finding. Summing this file's HTS_TST across modality, age and sex gives 415
overlapping country-years over 58 countries against `pepfar_panorama`, with a median ratio of
exactly 1.000000 and 349 cells inside half a per cent. HTS_TST_POS against `new_diagnoses` gives
the same 415 country-years and the same median. This file is a decomposition of a total already in
the panel, so its rows must never be read as corroboration of that total.

**The defect this exposed.** `pepfar_panorama` and `pepfar_agency` build country totals by adding
up the partners named in `Public_Partner_MER_TopLine`. This file reports the country directly.
Where PEPFAR runs a country through a REGIONAL operating unit it names very few partners, so the
partner sum is a fraction of the country figure. Thailand FY2018 publishes exactly one partner,
Bangkok Metropolitan Administration, with 1,308 tests, against 75,944 in this file. Thailand FY2019
is 1,752 against 136,227. From FY2020 Thailand publishes three partners and the two agree to
1.000000. Every country-year where the partner sum falls more than five per cent short belongs to
South and Southeast Asia Region, Central Asia Region or Central and South America Region, the sole
exception being Kenya FY2018 at 5.8 per cent. The connector therefore also emits country totals
under the same canonical ids, so the reconciliation table forms a pair and names the divergence
rather than the panel carrying a silent undercount.

Eleven country-years run the other way, this file three to 54 per cent BELOW the partner sum, worst
at Malawi FY2018 at 0.462 and Namibia FY2020 to FY2022. The shortfall is spread evenly across all
four quarters and no modality is missing, so it is neither a missing quarter nor a missing
modality. The obvious explanation, that results reported without an age breakdown are dropped
rather than filed under Unknown Age, is contradicted by Namibia, whose Unknown Age share is 28 per
cent in exactly the years it falls short. Recorded as unexplained rather than described as
understood.

**A category that arrives with the finding has to be kept out of the finding.** The modality
`Not Specified` carries no HTS_TST at all before FY2025 and 784,344 tests in Q4 FY2025, the one
quarter the community share collapses. It is confined to seven countries, Thailand, Mozambique,
Haiti, the Dominican Republic, Botswana, Jamaica and Zambia, and 727,005 of the 784,344 belongs to
Thailand alone. Thailand's own classified testing in Q4 FY2024 was 45,211 tests across both arms,
so putting the unclassified rows into either arm would have moved that arm by more than 16 times
the whole of Thailand's previous quarter. Those rows are counted into the country total, put in
neither arm, flagged in `extra.unclassified_tests`, and the seven countries are held out of the
headline. None of the countries driving the community collapse carries a single unclassified test.

**What the split shows**, Q4 FY2024 against Q4 FY2025, over the 52 countries whose modality labels
are complete. Both quarters are the fourth quarter of their fiscal year, so the comparison is 12
months apart and like for like.

| | Q4 FY2024 | Q4 FY2025 | change |
|---|---|---|---|
| community testing | 3,056,545 | 1,068,854 | -65.0% |
| facility testing | 16,021,304 | 13,517,748 | -15.6% |
| community share | 16.0% | 7.3% | |
| community positives | 51,185 | 34,825 | -32.0% |
| facility positives | 294,968 | 241,411 | -18.2% |

Community testing fell further than facility testing in 21 of the 26 countries doing more than
20,000 tests in Q4 FY2024 with both arms running, including Uganda at -93.5 per cent community
against -10.3 per cent facility and Nigeria at -83.4 against -15.8. Community positivity rose from
1.67 to 3.26 per cent while facility positivity barely moved, 1.84 to 1.79, which is what a
programme looks like when it stops going out to find people and keeps only its highest-yield
contacts.

### 9m. Two pairs of the same two sources, the same 415 cells, opposite verdicts

Running the connector put a second defect in plain view, and this one belongs to `reconcile.py`
rather than to any connector. The classifier calls a pair `derived` only when the median relative
difference is at or below one per cent AND the share of cells agreeing within two per cent is at or
above 0.90. The two conditions are joined by AND, and the second is a hard cut.

`pepfar_modality` against `pepfar_panorama` produced two pairs over the identical 415 country-years,
both with a median relative difference of exactly 0.000000 and a median ratio of exactly 1.000000.
`hiv_tests_performed` agrees within two per cent on 374 of 415 cells and is classified `derived`.
`new_diagnoses` agrees on 372 and is classified `independent`, carrying the evidence string
"separate measurement systems, divergence is informative". Two cells decide it. The very defect
§9l documents, the regional operating units, is what puts a tail of cells outside the band, so the
tail that the derived test punishes is the thing the pair was created to expose.

The problem is general, not local to the new connector. Eight of the 64 independent pairs, holding
8,567 of the 28,625 independent cells, have a median relative difference at or below one per cent,
meaning the typical cell is identical while the pair is labelled two separate measurement systems.
The clearest case is UNAIDS AIDSinfo against WHO GHO, where `hiv_tests_performed` is `derived` on
323 cells while `aids_deaths` (3,264 cells), `pmtct_arv_count` (1,515), `on_art_count` (2,030) and
`hiv_test_positivity_pct` (321) are all `independent` at a median relative difference at or below
one per cent. WHO GHO republishes UNAIDS estimates for HIV, and the reconciliation table currently
says otherwise on four indicators out of five.

The shape of those pairs is bimodal rather than noisy. `aids_deaths` has a median difference of
exactly zero and only 56 per cent of cells within two per cent, which is identical on most
country-years and far apart on the rest, the signature of one estimate republished at two vintages
and not of two instruments measuring the same world. Calling it `derived` overstates the agreement
and calling it `independent` inverts the meaning, so the honest repair is a fourth category rather
than a moved threshold. **Unfixed, and left unfixed deliberately**, because changing the rule
changes the verdict on all 94 pairs and that is a decision for Jason, not a tuning exercise to be
run after seeing which side of the line the new connector landed on.

### §9n. A file excluded for the right reason, and the sixteen years the exclusion cost

`pepfar_expenditure` reads `Public_Partner_Budgets_and_Expenditures` and its code excludes the
operating-unit budgets file by name, on the reasoning that the operating-unit file "covers the
same money at a coarser grain with no agency column, so reading both would double count". The
§9f test confirms that reasoning completely. Restricted to rows carrying an ISO3 code and with
the aggregate rows removed, the operating-unit file reproduces the panel to the dollar in every
year the two files share: FY2021 budget 5,036,285,258 in both, FY2021 expenditure 4,121,559,166
in both, FY2025 budget 4,281,549,540 in both, FY2025 expenditure 2,789,722,472 against the
panel's 2,789,722,474. Not close, identical.

What the exclusion did not notice is that the partner file begins at FY2021 and the
operating-unit file carries a budget column from 2004 and an expenditure column from 2018. A
correct decision about the overlap silently discarded 16 years of budget history and three years
of expenditure. The repair is a second connector, `pepfar_ou_budgets`, that stops where
`pepfar_expenditure` starts: budget for 2005 to 2020, expenditure for 2018 to 2020, and the five
later year columns named in its log line as left to the other connector. **The general rule.
Establishing that two files overlap settles what to do about the overlap and settles nothing
about the parts that do not overlap. Check the range before excluding the file.**

*Corrected 2026-09-19.* This section first said 17 years, counting a 2004 budget column that §9r
shows is not a year's budget. The connector reads the 2004 column, reports the 2004 column in its
log line and does not emit the 2004 column, so the budget recovered runs from 2005 to 2020.

Three aggregate layers sit on the detail and all three had to be removed. The file's 12,062 rows
are 11,919 detail rows, 71 country rows carrying `Program = Total`, 71 rows carrying
`Applied Pipeline` simultaneously in four different columns, and one footer row whose only
populated fields are `Operating Unit = Total` and the money. The footer row was found by
arithmetic rather than by inspection: after removing the country `Total` rows, the remainder came
to exactly 2.0000 times the country totals in all 30 money columns at once, and a ratio that
clean is a duplicated layer rather than an error of degree. The rebuilt country budgets are
checked against PEPFAR's own `Total` row at runtime, and they reproduce it exactly in 770 of the
773 country-years that carry a budget, the other three differing by more than a dollar and by
far less than one per cent.

### §9o. A denominator that cannot be spent, and the execution rate it corrupts

Rows whose `Record Type` is Management and Operations hold about half a billion dollars of
budget in every recent year against almost no expenditure at all, 317m of budget in 2018 and
518m against 12m in 2025. The pattern is flat across every year carrying expenditure, 2018 to
2025, so it is a property of how
PEPFAR books its own running costs rather than an artefact of any one year. Any execution rate
computed over the whole file therefore carries half a billion in its denominator that its
numerator structurally cannot contain, and understates execution by about ten points: 0.897
against 0.966 in FY2018, 0.861 against 0.939 in FY2019, 0.808 against 0.902 in FY2020, and 0.652
against 0.737 in FY2025. Both forms are carried on the row and the connector's interpretation
string says which one to read. **The general rule. Before dividing one column of a file by
another, check that every row contributing to the denominator is eligible to contribute to the
numerator.**

### §9p. The same conclusion by a second route is agreement, not corroboration

The FY2025 expenditure fall has two candidate explanations that this project cannot afford to
confuse, a reporting lag against a real stop in spending, and the file is stamped 21 January
2026, less than four months after FY2025 closed. The operating-unit file discriminates between
them without a mechanism column. A late file shrinks every programme by roughly the same
fraction. Instead the FY2025 execution rate runs 0.77 for care and treatment, 0.80 for testing,
0.66 for above-site programme support, 0.56 for programme management, 0.45 for prevention and
0.35 for surveillance and survey work. Care and treatment is the activity the January 2025
waiver covered, and it is the one that held up. An ordering that tracks which activities were
allowed to continue does not come out of a reporting lag.

`pepfar_expenditure` reaches the same conclusion from the mechanism reporting rates. That is
worth recording and it is not corroboration, because both readings come from the same
expenditure reports filed by the same staff. Two analyses of one instrument agreeing tells you
the analyses are sound, not that the instrument is.

### §9q. A country count can measure the publisher's attribution rather than the publisher's reach

The PEPFAR operating-unit file gives 14 countries a budget in 2005, 31 in 2019 and 53 in 2020.
Read as reach, the 22 countries entering in 2020 are countries PEPFAR started funding that year.
They are not. Every one of the 22 already sat under an operating unit covering several
countries, the operating unit does not change across the step, and what changes is that PEPFAR
starts writing an ISO3 on those rows. Across the same step the budget on those operating units
carrying no ISO3 falls from 79,647,757 to 8,956,546 while the budget on the same operating units
carrying one rises from 46,654,139 to 194,948,927. Thailand shows it at country level, present
2010 to 2013, absent 2014 to 2019, back with 21,141,451 in 2020, under one unchanged operating
unit throughout.

Nothing in the panel catches this. The validation harness warns when coverage falls between
years and says nothing at all when coverage rises, so a composition change that adds countries
passes silently. The cost lands on the analysis this project exists to run: an analysis
measuring the effect of a funding cut reads an absent year as a cut, and here an absent year
before 2020 means the file does not say. **The general rule. A count of units present in a
period can measure how far the publisher attributed the quantity to units that period rather
than where the publisher was working. Where that is so, an absence is not evidence of zero and a
first appearance is not a start, and the rows have to say so.**

Two corollaries came out of writing the connector that reports this.

The first is about what a rise licenses. Reporting the rise is always right, because a total
compared across the step covers two different sets of countries whatever caused it. Attributing
the rise to a re-coding is a separate claim needing separate evidence. The early rises, from 14
countries in 2005 to 28 in 2007, meet neither condition that the 2020 step meets. Of the 14
countries entering, 11 sit under their own single-country operating units, and rows with no ISO3
carry no budget at all from 2005 to 2010. A first draft of this connector attributed every rise to
re-coding and was wrong on the early rises. A second draft called the early rises genuine
expansion, and the file does not settle that either, because a file attributing no budget to
regional rows in those years cannot show whether PEPFAR was already working in the countries
entering. **Report the composition change on the count. Attribute it only where the file settles
the cause, and where the file settles nothing, say that the file settles nothing.**

The second is about how a category is defined. Regional operating units were first identified as
the ones that somewhere appear with no ISO3, which is the property that made them visible. That
definition misses South and Southeast Asia Region, which covers six countries and carries an
ISO3 on all 519 of its rows, and Thailand is one of the six. Defining a regional operating unit
as one covering more than one country flags 28 of the 55 emitted countries rather than 22.
**A category defined by the symptom that made it visible will miss the members that never showed
the symptom.**

### §9r. A column can hold an allocation rule, a category can start partway, and a repeat is not a hold

After the 2026-09-19 re-run the validator's outlier check, called directly because the
validation text stops after ten series, flagged a single series on `pepfar_ou_budgets`, Uganda in
2004. Following that one flag turned up three defects in the operating-unit file, and none of the
three is an error in any single cell.

The 2004 budget column is an allocation rule rather than a year's budget. The 2004 column holds
22 rows over 11 countries and 68,991,569 dollars, and every row sits under testing or under care
and treatment. In all 11 countries testing takes exactly 70 per cent and care and treatment
exactly 30 per cent, from Tanzania at 14,693,227 dollars down to Cote d'Ivoire at 2,709,900. A
budget planned programme by programme does not divide in the same proportion in 11 countries, so
the 2004 column carries one figure per country divided by a fixed rule. The same 11 countries
carry 783,034,013 dollars in 2005, 11.3 times the 2004 total and between 4.6 and 33.3 times by
country. Emitted as planned funding, the 2004 column put an elevenfold rise at the start of every
series the 2004 column touched. The connector now emits budget from 2005, and the log line
measures the 70 and 30 per cent split on every run rather than asserting the split. **The general
rule. Where a breakdown divides in exactly the same proportion in every unit, the breakdown holds
one number per unit and a rule, not a measurement of each part.**

Two budget categories begin in 2014. The file books nothing under Management and Operations or
under Applied Pipeline before 2014, and 295,636,956 dollars and 1,180,230,636 dollars under those
two categories in 2014. The emitted budget total rises from 3,213,039,728 dollars in 2013 to
4,780,573,818 in 2014 over the same 32 countries, and 1,475,867,592 of that rise of 1,567,534,090
comes from the two categories that start in 2014. The file does not say whether the years before
2014 carried those costs inside the programme lines, so the 2013 to 2014 comparison changes basis
as well as amount. The 244 budget rows for 2005 to 2013 now name the absent categories in
`categories_absent`, and a comparison across the step subtracts `mgmt_ops_budget` and
`applied_pipeline` from the later year first. **The general rule. When a category first appears
partway through a series, the rows before the category appears must say so, because nothing in a
total shows that the total is measured on a different basis.**

Some years repeat the year before. In 2010 all 28 countries present in both 2009 and 2010 carry
the 2009 budget to the dollar in every programme area, and the whole change in the 2010 total,
32,775,394 dollars, belongs to the three countries entering in 2010, China, Guyana and Thailand.
The file does not say whether PEPFAR copied the 2009 plan or planned 2010 at exactly the 2009
levels. A second kind of repeat holds the total while the split moves. In 24 country-years between
2016 and 2018, five in 2016, 12 in 2017 and seven in 2018, the total repeats the year before while
the programme areas and Applied Pipeline change. Angola holds 17,700,000 dollars in every year from
2015 to 2018. Mozambique's own Total row reads 337,075,909 dollars in 2016 and in 2017, while the
budget net of Applied Pipeline falls from 330,523,501 to 310,403,040 and Applied Pipeline rises
from 6,552,407 to 26,672,869. A held total therefore does not mean held new money. The rows carry
`repeats_previous_year` naming which kind of repeat applies. **The general rule. A change of zero
is not evidence that funding was held. An exact repeat across every part of a breakdown cannot be
told apart from a copied plan, and every check that looks for jumps passes a copied year
silently.**

The runtime check that absorbs the second kind of repeat needed a tolerance of two dollars rather
than half a dollar. The rebuilt budget is detail plus Applied Pipeline, each rounded separately in
PEPFAR's file, so a country total that PEPFAR held at exactly the same figure can rebuild a dollar
apart, as Mozambique does at 337,075,908 against 337,075,909. At half a dollar the check missed
Indonesia, Ghana, Cote d'Ivoire and Mozambique.

### §9s. A zero can record who pays, a sum can arrive as an average, and a net count can hide who left

`PEPFAR_OU_Commodities_Procurements`, the third of the four files §7b named as additive, is read
by connector 22, `pepfar_commodities`. The file lists every commodity a Country Operational Plan
from COP18 to COP24 sets out to buy, one line per item with a planned budget and a planned
quantity, 8,902 lines and 5,537,274,918 dollars over the implementation years 2019 to 2025. The
connector was run into the panel twice, and the second run, on 19 September 2026, emitted 1,116
rows over 54 countries, 279 for each of four series, the like-for-like total and the ARV, rapid
test kit and laboratory categories. Every plan in the file was written before the January 2025
freeze, so the file cannot show the cut. The file shows the trend going into 2025. Over the 23
countries with a plan in both 2019 and 2025, planned ARV procurement falls from 506.7m dollars to
220.2m and the like-for-like total from 861.8m to 542.3m. The file cannot separate fewer people
supplied from a cheaper regimen or from another funder taking over the purchase.

A budget of zero beside a stated quantity records where the cost sits. In 2019 every one of the
40 condom lines carries a budget of zero against 422.7 million condoms over 14 countries,
103,662,024 of the condoms for Zambia. Seven later country-years in 2021 and 2022 also list
condoms at a budget of zero, which makes 21 country-years and 462,389,641 condoms planned with no
money attached. Lesotho 2024 lists 907,443 laboratory units, 1,510 rapid test kit units and
30,200 male circumcision units, every line at a budget of zero, between a like-for-like total of
5.94m dollars in 2023 and 5.80m in 2025. Read as spending, each zero would show a supply
collapsing in a year when the plan lists the goods. A plan can list goods whose cost another plan
or another funder carries, so a zero budget beside a quantity says who pays and says nothing
about what was bought. Condoms enter no indicator, and Lesotho 2024 is withheld from every series
and named in the log. **The general rule. A budget of zero beside a stated quantity is a
statement about who pays, not a measurement of zero, and an analysis of funding cuts has to be
kept from reading the zero as a cut.**

A figure in a second file can be aggregated with the wrong function. The partner file,
`Public_Partner_Budgets_and_Expenditures`, carries a `Condoms: Commodities` column, and the
column agrees with the commodities file's condom category to within half of one per cent in 103
of the 118 country-years both files fill. The partner file and the commodities file disagree in
15 country-years, all in 2021 or 2022, and the partner file carries the smaller figure in all 15
disagreements. In eight of the 15 disagreements the partner figure is the condom total divided by
the number of condom lines. Cote d'Ivoire 2022 has three condom lines summing to 749,967 dollars
in the commodities file, and the partner file gives 249,989. Seven disagreements fit no rule
either file settles, the Democratic Republic of the Congo 2021, Lesotho 2022, Sierra Leone 2021,
Eswatini 2022, Ukraine 2022, Zambia 2021 and Zimbabwe 2021. A mean written where a sum belongs
does not look like an error. The mean looks like a smaller plan, and a comparison of the partner
file with the commodities file would report PEPFAR's own publications disagreeing about money
when one publication has averaged. The panel does not read the partner file's condom column, so
no indicator is affected through the condom column.

The averaging does not reach the partner file's `Total Planned Funding`, which the panel reads as
`pepfar_planned_funding`. The test was run offline on 19 September 2026. In all eight averaged
country-years the partner file books the condom money on a single GHSC-PSM row under PREV,
Condom & Lubricant Programming, and the row's `Total Planned Funding` is at least the full condom
total in the commodities file. Cote d'Ivoire 2022 carries 750,000 dollars of planned funding on
the row whose condom column reads 249,989, against a condom total of 749,967 in the commodities
file. None of the 145 partner rows carrying condom commodities shows a condom figure larger than
the row's own `Total Planned Funding`. The partner file's `Total Planned Funding` also equals the
budget in `PEPFAR_OU_Budgets_and_Program_Expenditures`, summed over the OU file's detail rows, to
within two dollars in all 277 country-years from 2021 to 2025, the eight averaged country-years
included, once the Peace Corps rows described in §9t are placed in the countries the rows name.
The partner file and the OU file are both PEPFAR publications and may be built from one
database, so the agreement rules out an error made in writing the partner file and cannot rule
out an error in a database behind both files. The two files split each country's total across
programme areas differently, so the agreement holds for the country-year total and cannot be
tested programme by programme. The partner file's 14 other cross-cutting columns, among them
`Food and Nutrition: Commodities`, `Human Resources for Health` and `Construction`, cannot be
tested for averaging, because no file on disk lists those amounts line by line. The panel reads none of the 14 columns. **The general
rule. When two files disagree on the same quantity and one file is always smaller, divide the
larger figure by the number of lines behind the larger figure before looking for any other cause.
An average found in one column of a file has to be looked for in every column the panel reads
from the same file.**

The quantity column changes unit across the whole file, not in Nigeria alone. §7g records
Nigeria's Determine test kit at 85.60 dollars a unit in FY2024 and 0.80 in FY2025 under an
identical item string. Across the whole file, 260 of the 1,694 pairs of the same item in the same
country in consecutive years change price per unit more than tenfold, including 161 of 630
laboratory pairs, 66 of 272 rapid test kit pairs and two of 329 ARV pairs. A quantity series
would record changes of unit as changes of supply, so the connector emits budget only and counts
the jumps on every run. The description in §7b of a file carrying planned ARV and test-kit
quantities stands for what the file holds and is withdrawn for what the panel can use.

A category the plan does not list is a zero, and a country-year the file does not hold is not.
The connector's first run left a hole wherever a plan carried a like-for-like total and no line
in a category. The validator read the holes as countries leaving, and flagged ARV at 32 reporting
countries in 2023 against 26 in 2024, laboratory at 37 in 2021 against 29 in 2022 and rapid test
kits at 42 in 2021 against 33 in 2022. None of the flagged countries left the file. A procurement
plan lists what the plan buys, so a plan with a total and no ARV line plans to buy no ARVs, and
the file settles the zero. Mali 2024 carries 489,495 dollars of essential medicines, laboratory
goods and rapid test kits and no ARV line, between about 29,000 dollars of ARVs in 2023 and about
98,000 in 2025. The second run writes the zero, marked `category_not_in_plan`, on 84 ARV rows, 65
laboratory rows and 31 rapid test kit rows, and all three validator flags are gone. A country-year
the file does not hold, or holds only as a withheld plan, still carries no row, because nothing in
the file says what a missing plan contained. A zero ARV plan can also mean another funder buys the
country's ARVs, and the file does not name the other funder. **The general rule. Whether an empty
cell is zero or unknown depends on what the file lists. A file that lists what a plan buys
settles a zero inside a plan that exists and settles nothing about a plan the file does not
hold.**

A net count of countries can hide the countries that left. The like-for-like total covers 44
countries in 2023 and 43 in 2024, a fall of one country. Underneath the fall of one, Guatemala,
Honduras, Panama and El Salvador leave, Lesotho is withheld, and Colombia, Peru, Senegal and
South Sudan return from gaps. The validator's reporting-drop check compares net counts against a
threshold of 15 per cent (`REPORTER_DROP_SHARE` in `hivimpact/writers.py`), so a year in which
countries return as fast as other countries leave passes silently. Guatemala, Honduras, Panama
and El Salvador all sit under the Central and South America Region. In 2024 the Central and
South America Region carries no line for any of the four Central American countries and one line
naming `Western Hemisphere Region (pre-FY24)` in place of a country, 436,870 dollars of PrEP
tablets. The file does not settle whether PEPFAR stopped planning commodities for the four
Central American countries or began planning the countries' commodities at regional level. The
connector now names every entry and every exit on every run, and the series of 12 countries end
before 2025 in the current file. Where a country's series ends in the year before the country's
operating unit carries a line naming a region, the country's rows say so in `coverage_warning`.
The rises in the count in 2020 and 2021 repeat §9q, with 15 of the 16 countries entering in 2020
sitting under a regional operating unit that first appears in the file in 2020. **The general
rule. A count of units compared year on year measures net change. Entries and exits have to be
listed by name, because a year in which units return as fast as other units leave shows no change
at all.**

Two rules from §9r held again. The file books In-Country Logistics and Quality Assurance from
2023 and Procurement Management from 2024, and together with the 2019 `Not Specified` lines the
cost categories hold 223,952,936 dollars, 4.04 per cent of the file. Every indicator excludes the
cost categories, and the total row carries the amounts in `cost_categories`. PrEP enters the ARV
category in 2020 at 2.9m dollars, so ARV rows carry `prep_budget`, and ARV rows before 2020 name
the absent minor category in `categories_absent`.

### §9t. A code column can contradict the name written beside the code

The partner file, `Public_Partner_Budgets_and_Expenditures`, carries an `ISO3` column and a
`Country` column on every row. On 106 rows the `ISO3` column reads USA while the `Country` column
names one of 13 countries in which PEPFAR works, Botswana, Cameroon, Eswatini, Kenya, Lesotho,
Malawi, Mozambique, Namibia, South Africa, Tanzania, Uganda, Ukraine and Zambia. Every one of the
106 rows belongs to a Peace Corps mechanism named Management and Operations (Funding Agency `PC`),
and every one of the 106 rows falls in the implementation years 2022 to 2025. The 106 rows hold
101,663,836 dollars of planned funding and 30,336,352 dollars of expenditure. No row in the
partner file names the United States in the `Country` column. The Peace Corps rows of 2021 carry
the code of the country each row names, and so do the Peace Corps rows booked to `All for OU` in
later years, which hold the Peace Corps expenditure of 2025 and Lesotho's Peace Corps plan for
2024 and 2025. The test of the condom averaging in §9s found the mislabel on 19 September 2026.

Until 19 September 2026 `pepfar_expenditure` took a partner row's country from the `ISO3` column
alone, so the panel held four rows for the United States in each of `pepfar_planned_funding`,
`pepfar_planned_funding_other_agency`, `pepfar_expenditure` and `pepfar_expenditure_other_agency`,
one row for each year from 2022 to 2025, and the 13 countries' series for the same years lacked the
Peace Corps money. Over the 50 affected country-years the missing money is a median 0.85 per cent
of a country's corrected planned funding and at most 6.04 per cent, in Botswana 2022, and at most
4.12 per cent of corrected expenditure, in Botswana 2024. The other-agency series, which holds
every agency other than USAID and HHS/CDC, loses far more. The missing money is a median 19.2 per
cent of a country's corrected other-agency planned funding and 75.2 per cent in Botswana 2024.
The panel read other-agency expenditure of zero in Botswana 2024, Namibia 2023 and Namibia 2024,
where the Peace Corps spent 1,675,092, 528,167 and 646,038 dollars. The mislabel starts in
2022, so a country's other-agency series fell between 2021 and 2022 partly because the Peace
Corps money left the country's rows. Botswana's other-agency planned funding read 6,943,294
dollars in 2021 and 2,564,110 in 2022 in the panel, a fall of 63 per cent, and 6,279,181 in 2022
with the Peace Corps money restored, a fall of 9.6 per cent. The mechanism counts on the affected
rows left out the Peace Corps mechanism, which the United States rows counted instead, 13
mechanisms in 2022 and 2023 and 12 in 2024 and 2025.

`PEPFAR_OU_Budgets_and_Program_Expenditures` places the Peace Corps money in the 13 countries, and
settles which column is wrong. Keyed on the partner file's `Country` column, the partner file's
planned funding equals the OU file's budget to within two dollars in all 277 country-years from
2021 to 2025, and the partner file's expenditure equals the OU file's expenditure to within two
dollars in 271 of 278 country-years and to within four dollars in all 278. Keyed on the `ISO3`
column, as the panel was keyed before the fix, planned funding agrees in 227 of 281 country-years and
expenditure in 238 of 281. The same key moves one figure in connector 22's check against the
partner file (§9s). Keyed on `Country`, the full commodity plan is 15.8 to 17.9 per cent of
planned funding by year, against 15.9 to 17.9 keyed on `ISO3`, and the highest share stays 0.408,
in the Democratic Republic of the Congo in 2023.

The fix was made on 19 September 2026. `pepfar_expenditure` and connector 22's check now take a
partner row's country from the `Country` column wherever `Country` and `ISO3` name different
countries, and the log of every run counts the rows and dollars moved and names the countries.
Jason's run of the same day at 11:25 removed the 16 United States rows and raised the planned
funding of 50 country-years by 101,663,836 dollars and the expenditure of 37 country-years by
30,336,352 dollars. No value fell, and the 181,039 rows of every other source are unchanged.
Botswana's other-agency planned funding now reads 6,279,181 dollars in 2022, and the other-agency
expenditure of Botswana 2024, Namibia 2023 and Namibia 2024 now reads 1,675,092, 528,167 and
646,038 dollars. The reporting rate changed on 100 expenditure rows of the 13 countries. Six
other-agency rows lost the completeness warning (Botswana 2023 and 2024, Mozambique 2022,
Eswatini 2022, Ukraine 2022 and South Africa 2023), and five other-agency rows of 2025 gained the
warning (Mozambique, Malawi, Eswatini, Uganda and Zambia), for the reason §9u gives. **The general
rule. A file that gives a code and a name for the same unit can let the code and the name
disagree, and a connector keyed on the code alone moves money between countries without any
warning. Where a file carries both columns, the connector has to derive the code from the name as
well and name every row on which the two columns disagree.**

### §9u. A reporting rate counted by mechanism cannot see money booked to no mechanism

The partner file writes `All for OU` in `Mechanism Code` for money booked to a whole operating
unit and not to a mechanism. The partner file holds 506 `All for OU` rows under 12 funding
agencies, which form 490 agency-country-years. In 375 of the 490 agency-country-years the
`All for OU` line carries budget and no expenditure, in 72 the line carries both, and in 43 the
line carries expenditure and no budget, 20,644,073 dollars in all. `pepfar_expenditure` counts a
mechanism as reporting when the mechanism holds a budget and files expenditure, so an `All for OU`
line with expenditure and no budget enters no reporting rate. Wherever an agency's `All for OU`
line carries expenditure and no budget, the same agency also holds a mechanism with a budget and
no expenditure in the same country-year, and the budgeted mechanism reads as silent although the
agency reported spending in the country-year. The 43 unbudgeted `All for OU` lines belong to USAID
(18), the Peace Corps (13), HHS/CDC (five), State/AF (five), HHS/HRSA (one) and the Department of
Defense (one). The connector pools the Peace Corps, the Department of Defense and the State
Department in the other-agency series, so the 43 unbudgeted `All for OU` lines fall in 42 agency
series-years, because Mozambique in 2025 has an unbudgeted line for both the Peace Corps and
State/AF.

The Peace Corps in 2025 is the largest case. From 2022 to 2024 the Peace Corps booked most of the
agency's spending on the Management and Operations mechanism, 7,435,672, 10,556,066 and
12,344,614 dollars by year, against 1,031,930 and 800,010 dollars on `All for OU` lines in 2022
and 2024. In 2025 the Management and Operations rows carry 24,292,139 dollars of planned funding
and no expenditure, and the Peace Corps spending of 12 countries, 11,544,602 dollars, sits on
`All for OU` lines with no budget, led by Zambia (2,462,597 dollars) and Botswana (2,019,855).
Lesotho's Peace Corps `All for OU` line carries a budget of 976,618 dollars in both 2024 and 2025,
so Lesotho's Peace Corps spending enters the reporting rate. The partner file does not say why the
Peace Corps spending of 2025 moved off the Management and Operations mechanism. Of the 43
unbudgeted `All for OU` lines, 18 fall in 2025 and carry 12,500,610 dollars, and the two unbudgeted
USAID lines of 2025 carry 144,659 dollars, in South Africa (138,485) and Senegal (6,174).

The Peace Corps `All for OU` booking of 2025 did not show in the country rows until the fix of
§9t. Before the fix, the silent Management and Operations mechanisms of 2025 sat on the United
States rows, where the other-agency reporting rate read 1.00 in 2024 and 0.00 in 2025. Placing the
Peace Corps rows by `Country` moved the silent Management and Operations mechanisms into the 13
countries, and the other-agency rows of Mozambique, Malawi, Eswatini, Uganda and Zambia for 2025
gained a completeness warning. The partner file does not say which mechanism an `All for OU` line
belongs to, so the connector changes no reporting rate. Every
expenditure row carries the unbudgeted `All for OU` spending of the row's agency series and
country-year in `ou_level_unbudgeted_expenditure`, above zero on 79 of the 970 expenditure rows.
Where the unbudgeted `All for OU` spending sits beside a silent mechanism, the completeness
warning names the amount and calls the reporting rate a lower bound, on 33 of the 214 warnings.
Jason's run of 19 September 2026 at 11:25 left every value and every reporting rate as the offline
dry run without the new field had predicted.

How far the `All for OU` booking can move a warning was tested under the reading that each
unbudgeted `All for OU` line holds the spending of one silent mechanism of the same agency. The
test credits one silent mechanism for each unbudgeted line and compares the credited rate of a
year with the uncredited rate of the year before, which gives the smallest fall the file allows
under the one-mechanism reading. Under the one-mechanism reading 11 of the 33 lower-bound warnings
would not fire, among them all five warnings that the Peace Corps fix added. Mozambique's
other-agency rate reads three of eight mechanisms in 2024 and two of eight in 2025, and four of
eight in 2025 once the Peace Corps line and the State/AF line are each credited. Under the same
reading 22 of the 33 lower-bound warnings still fire, among them South Africa's USAID series, 29
of 36 mechanisms reporting in 2024 and seven of 34 in 2025, eight of 34 with the South African
line credited, and Senegal's USAID series, three of six in 2024 and one of six in 2025, two of six
with the Senegalese line credited. The `All for OU` booking therefore does not explain the fall in
USAID reporting in 2025. The partner file does not say how many mechanisms an `All for OU` line
holds, so the 11 cleared warnings describe one plausible reading and not a bound. **The general
rule. A completeness measure counted over reporting
units cannot see money a file books outside the reporting units. Where a file has a placeholder
unit, the connector has to carry the money on the placeholder beside every completeness figure,
and has to call the completeness figure a lower bound wherever the placeholder's money sits
beside a silent unit.**

### §9v. A headcount split across rows can count one person twice, and a country with one row is not a country with no staff

`HRH_Inventory_Public_Dataset`, the fourth of the four files §7b named as additive, is read by
connector 23, `pepfar_hrh`. The file is PEPFAR's human resources for health inventory, in which
PEPFAR's implementing partners report the staff whose pay PEPFAR funds, one row for each
combination of operating unit, country, staff category, cadre, programme area, sub-programme and
interaction type. The file holds 2,974 rows over 33 operating units and 57 names in the `Country`
column, with 1,223,427,353 dollars of spend, 274,456 in the `Individual Count` column and
175,844.14 full-time equivalents. §7b called the file a health-workforce inventory. The inventory
lists PEPFAR-funded staff only and does not describe a country's national health workforce. The
connector emits three series for each country, `pepfar_hrh_spend`, the spend summed over the
country's rows, `pepfar_hrh_fte`, the full-time equivalents summed over the country's rows, and
`pepfar_hrh_fte_service_delivery`, the full-time equivalents on the rows whose `Interaction Type`
is `Service Delivery`. The service-delivery series is part of `pepfar_hrh_fte` and must never be
added to `pepfar_hrh_fte`. No other source in the panel counts PEPFAR-funded staff. Every row
carries fiscal year 2025, which runs from October 2024 to September 2025 and contains the freeze
of January 2025. A file holding one year cannot show a change, and the inventory cannot separate
staff paid before the freeze from staff paid after the freeze, so `pepfar_hrh_spend`,
`pepfar_hrh_fte` and `pepfar_hrh_fte_service_delivery` give the level of PEPFAR-funded staffing in
the year of the cut.

The file sorts staff into clinical health workers, ancillary health workers and other staff, and
classifies a post by the employment terms of the PEPFAR-funded position and not by the worker's
qualification, so a qualified nurse employed as a manager counts as other staff (Financial
Classifications Reference Guide of 16 April 2025, page 65). Other staff hold 63.9 per cent of the
spend, clinical health workers 22.7 per cent and ancillary health workers 13.4 per cent. Counted
in full-time equivalents, ancillary health workers come first with 82,262, against 47,634 for
other staff and 45,948 for clinical health workers. A full-time equivalent costs 16,416 dollars
among other staff, 6,046 dollars among clinical health workers and 1,990 dollars among ancillary
health workers. The same number of posts cut among other staff therefore lowers
`pepfar_hrh_spend` about eight times as much as the same number of posts cut among ancillary
health workers, while `pepfar_hrh_fte` falls by the same amount. Rows marked `Service Delivery`
hold 36.2 per cent of the spend and 128,306 of the 175,844.14 full-time equivalents. Every row
under Above Site Programs (ASP) and Program Management (PM) is marked `Non Service Delivery`, and
so are 1,730 of the 1,756 rows of other staff.

The `Individual Count` column cannot be summed into a count of people. The file splits every
country's staff by cadre, programme area, sub-programme and interaction type, and the guide refers
the rules of the inventory to an HRH Inventory Handbook that is not on disk (page 66), so nothing
on disk says whether a person whose time is split between two programme areas appears on two rows.
On every row the full-time equivalents are at most the row's `Individual Count`, and the ratio of
full-time equivalents to `Individual Count` has a median of 0.664 and a tenth percentile of 0.11.
A person split over several rows would produce low ratios, and so would part-time staff, and the
file cannot tell a split person from a part-time worker. A sum of full-time equivalents is right
in either case. A sum of `Individual Count` is right only if no person sits on two rows. The
headcount therefore rides in `extra.individual_count`, with a warning in
`extra.individual_count_warning`, and enters no series. **The general rule. A count of people
split across several dimensions adds up to a count of people only if the file guarantees that no
person sits on two rows. Where the file does not say, the connector has to emit the measure that
adds correctly either way and keep the count out of every series.**

Ukraine's inventory is one row, `IM Program Management` under other staff, with 766,678.95 dollars
of spend, 11 in the `Individual Count` column and 0.21 full-time equivalents. The partner file,
`Public_Partner_Budgets_and_Expenditures`, records 40,722,026 dollars of PEPFAR expenditure in
Ukraine in 2025, so Ukraine's inventory holds 1.9 per cent of Ukraine's expenditure. Among the
other 54 countries the lowest share is Nigeria's at 27.5 per cent, followed by the Democratic
Republic of the Congo at 28.9 per cent and Rwanda at 31.3 per cent. Emitted, Ukraine's rows would
read as PEPFAR paying almost no staff in Ukraine, when the file lists a single row of programme
managers. The connector withholds a country-year from every series when the country's inventory
spend falls below 10 per cent of the partner file's `Total Expenditure` for the same country and
year, and the log names every withheld country-year with the share, as Lesotho 2024 is withheld
from the commodity series in §9s. Any threshold from two to 27 per cent withholds Ukraine alone in
the current file. A rule withholding every country with no `Service Delivery` row would have been
the wrong rule. Cambodia's inventory carries 13 rows and 73.14 full-time equivalents, every one of the
13 rows other staff under ASP and PM, and Cambodia's inventory spend is 54.9 per cent of Cambodia's
expenditure. An inventory that lists staff and lists no service-delivery staff settles the zero,
so Cambodia's service-delivery series is emitted as zero and marked
`extra.no_service_delivery_rows`. **The general rule. Whether a record is too thin to read has to
be judged against an outside measure of the same country's activity, and not against the kinds of
row the record lacks, because a country can lack a kind of row for a reason the record itself
shows.**

The file carries 40 rows that name no country. Under the Central Asia Region, 31 rows write
`Central Asia Region` in the `Country` column, and nine rows write `Data not provided at this
geographic level`, one under the Central and South America Region, five under West Africa Region
1 and three under West Africa Region 2. The 40 rows hold 738,825 dollars, 282 in the `Individual
Count` column and 73.64 full-time equivalents, and are dropped and counted in the log, as the
regional rows of §9q and §9s are dropped, and not spread over a region's countries. Seven operating
units cover more than one country in the file, the Caribbean Region, the Central Asia Region, the
Central and South America Region, the Pacific Region, the South and Southeast Asia Region, West
Africa Region 1 and West Africa Region 2, holding 788 rows and 74,572,975 dollars with the 40
dropped rows included. The 29 countries under the seven regional operating units carry
`extra.funded_through_regional_ou`, and the 19 of the 29 countries that sit under an operating
unit with a dropped row carry an `extra.coverage_warning` that the country's figures may be a
floor, because the staff on the dropped rows may work in the country.

Every country-year's inventory spend is compared with the partner file's `Total Expenditure`, with
partner rows placed by the `Country` column as §9t requires. Over the 54 countries emitted,
inventory spend is a median 51.5 per cent of PEPFAR expenditure and 44.4 per cent overall,
highest in Jamaica at 76.2 per cent and lowest in Nigeria at 27.5 per cent. No country's inventory
spend exceeds the country's expenditure, and every country with PEPFAR expenditure in the partner
file for 2025 has rows in the inventory, Ukraine aside. The partner file and the inventory come
from the same implementing partners, so comparing inventory spend with `Total Expenditure` can
catch an inventory larger than the country's whole expenditure and cannot confirm the inventory's
figures. The partner
file's `Human Resources for Health` column looks like the same quantity and is a different
quantity. The guide defines Human Resources for Health as a programme area for above-site work to
strengthen the health workforce, such as pre-service training and national workforce planning
(pages 50 and 51). Over the partner rows placed in a country, the `Human Resources for Health`
column totals 19,829,631 dollars in 2025 and is filled for 39 of the 54 countries emitted, and a
country's inventory spend is a median 40 times the column's value for the same country. Compared
with the inventory, the column would read as partners reporting a fortieth of the staff pay the
inventory lists. The connector logs the ratio on every run and never compares the column with the
inventory. **The general rule. A column named after a quantity can hold a programme area of the
same name. Before columns sharing a name are compared, the classification guide has to be read for
what each column measures.**

The file carries 30 rows with no full-time equivalents and 23,580 dollars of spend, and eight rows
with more than 500,000 dollars per full-time equivalent, 1,179,430 dollars in all, with no more
than 0.38 full-time equivalents on any one row. Ukraine's single row is among the rows above
500,000 dollars per full-time equivalent. The rows are kept, because a small fraction of a post
can carry a stipend or a contract the file does not break down, and the log counts the rows with no
full-time equivalents and the rows above 500,000 dollars per full-time equivalent on every run.

The offline dry run of 19 September 2026 emitted 162 rows over 54 countries, 54 in each series,
with 1,221,921,849 dollars of spend (99.88 per cent of the file), 175,770.29 full-time equivalents
and 128,250.50 service-delivery full-time equivalents. Merged into the panel of 184,089 rows, the
162 rows give 184,251, the validator's 142 warnings are unchanged, and the reconciliation stays at
95 pairs, none involving `pepfar_hrh`, because no other source counts PEPFAR-funded staff.
`scripts/audit_coverage.py` now counts seven of the 15 Spotlight files as read. Jason's run of the
same day wrote the 162 rows into the panel. Checked offline, the 162 rows on disk match the dry run
in every column, the 184,089 rows of the other sources match `hiv_panel.prev.csv` in every column,
and the validator and the reconciliation give the same counts as the dry run.

### §9w. A split of a total already read is refused in writing, a zero that means two things is not emitted, and an absence has to be checked in every file

Work item #15 required every one of the 15 PEPFAR Spotlight zips in `data/raw/pepfar/` to be read
or refused in writing, and seven had been read by the end of §9v. The last eight zips were held
against two series the panel already holds, the national totals of the geographic file
(`Enhanced_Geographical_Analysis`, read by `pepfar_snu`), which removes people whom two partners
both report, and the partner-summed totals of `pepfar_panorama`, which do not remove them. The
comparison is the §9f test, under which a file whose totals equal a series already in the panel is
a split of that series and never corroboration of that series. Six of the eight zips are refused,
`Voluntary_Male_Medical_Circumcisions_Results_by_Operating_Unit` is read by connector 24,
`pepfar_vmmc`, and `Partner_Performance` waits on a design that Jason has not yet approved.
`scripts/audit_coverage.py` now reports eight of the 15 files read, six declared out of scope with
the reason printed beside each file, and `Partner_Performance` as the one file unexamined.

Summed over age, sex and facility, four of the refused files reproduce the geographic file's
national totals for TX_CURR, TX_NEW, HTS_TST and HTS_TST_POS. `Operating_Unit_by_Fine_Age_and_Sex`
equals the geographic file exactly in 1,466 of 1,466 country-indicator-years,
`Site_Performance_2021_plus` in 1,080 of 1,080, `Site_Performance_2016-2020` in 903 of 934, and
`Clinical_Cascade_Results_by_Coarse_Age_and_Sex` in 1,756 of 2,012, with every mismatch in FY2016
to FY2018. `Clinical_Cascade_Results_by_Fine_Age_and_Sex` carries the coarse Cascade file's totals
in finer age bands, and the fine bands are defined differently in different years.
`Public_Partner_MER_AgeSex` is the age and sex split of `Public_Partner_MER_TopLine`, the partner
file `pepfar_panorama` reads, and equals `pepfar_panorama` in 401 of 406 TX_CURR country-years and
in 415 of 415 HTS_TST_POS country-years. The eight codes that `Public_Partner_MER_AgeSex` carries
and TopLine lacks are codes for orphans and vulnerable children, which `pepfar_panorama` already
declares outside the HIV cascade. None of the six refused files holds a country-indicator-year that
the geographic file lacks. The Cascade files and the 2016 to 2020 site file do hold about 93
country-years per code that the panel lacks at the national level, most of them in FY2016 and
FY2017 before `pepfar_panorama` begins, and the geographic file holds the same country-years, so a
national PEPFAR series for FY2016 and FY2017 would be read from the geographic file and not from a
split of the geographic file. **The general rule. A file whose totals equal a series already in the
panel adds a breakdown of that series and no evidence about that series. A refusal of such a file
has to name the series matched and the count of cells that match, so that the refusal can be
checked and reversed without repeating the comparison.**

`Site_Performance_2021_plus` carries one finding that the refusal does not discard. Named
facilities reporting TX_CURR at the fourth quarter number 24,260 in FY2023, 27,098 in FY2024 and
27,359 in FY2025. Between FY2024 and FY2025, 779 facilities stopped reporting, against 492 between
FY2023 and FY2024. Myanmar's count of reporting facilities fell 55 per cent, from 33 to 15, India's
38 per cent, Haiti's 30 per cent, Nepal's 28 per cent, Thailand's 28 per cent and Burundi's 18 per
cent. The site file cannot tell a facility that stopped treating people from a facility handed to
the national government, which then reports outside PEPFAR, so the count of facilities that stopped
reporting is recorded here and enters no series.

`pepfar_vmmc`, connector 24, reads the circumcision file, a table of 17 rows, one for each
country, with a column for every PEPFAR fiscal year from 2010 to 2024, a column pooling 2007 to
2009 and a total. On the download of 2026-07-18, dated 29 May 2025 inside the zip, the total equals
the sum of the other columns in all 17 rows, and the connector repeats the check on every run. From
FY2018 onwards `pepfar_panorama` already emits `circumcisions_performed` from the partner file. The
circumcision file and `pepfar_panorama` agree within half of one per cent in 92 of the 101
country-years both carry, and the other nine country-years lie between 0.952 of
`pepfar_panorama`'s value (Zambia 2018) and 1.030 (Kenya 2018), which also shows that the years in
the circumcision file are PEPFAR fiscal years. For 2016 and 2017 the circumcision file equals the
geographic file exactly in 27 of the 28 country-years, Uganda 2017 standing at 732,527 against
734,492, so the circumcision file is a deduplicated series and carries none of the partner
overcount described below. The connector emits FY2010 to FY2017 only, 108 rows over 14 countries
and 14,939,124 circumcisions, and leaves the 101 later cells to `pepfar_panorama`. The pooled column
holds 73,118 circumcisions in six countries (Kenya 45,657, South Africa 18,100, Botswana 5,180,
Eswatini 3,802, Tanzania 262 and Namibia 117) and is read, counted in the log and never emitted,
because dividing a three-year figure by three would invent a path the file does not contain.

The circumcision file writes 0 both for a country with no programme and for a running programme
that reported nothing. Nigeria, Burundi and Sierra Leone carry 0 in every year from 2010 to 2017,
and the three countries report 22 procedures between them after 2019. Namibia carries 0 in 2013
between 6,121 in 2012 and 785 in 2014, and Botswana carries 0 in 2011 between 534 in 2010 and 8,590
in 2012. A 0 in the panel would read as a measured stop to a programme. The connector emits cells
above 0 only, names every 0 left out in the log, and marks every Namibian and Botswanan row with
`extra.zero_years_not_emitted`. **The general rule. A value that a file writes both for no
programme and for no report is not a count of services. The connector has to leave such a value
out of the series, name every omitted cell, and mark the neighbouring rows, so that a gap in the
series is not read as a fall in services.**

Connector 24 adds attribution and almost no coverage. `unaids_aidsinfo` carries the national
circumcision count under the same indicator for every one of the 108 country-years, and gives 0 for
Lesotho 2011, where the circumcision file gives 199. PEPFAR's figure is at or below the national
figure in 85 of the other 107 country-years, with a median ratio of 0.831. Four country-years sit
more than 25 per cent above the national figure, Malawi 2013 at 1.65 times, Eswatini 2012 at 1.45
times, Tanzania 2015 at 1.39 times and Namibia 2012 at 1.26 times. A PEPFAR fiscal year begins
three months before the calendar year of the same number and could move a campaign into the next
year, but neither file can confirm that explanation, so the four country-years are recorded and not
explained. With `pepfar_panorama`, the panel now holds PEPFAR's own circumcision series from FY2010
to FY2024, and the PEPFAR series divided by the UNAIDS series gives the share of each country's
circumcisions that PEPFAR supported, which is the share a cut to PEPFAR puts at risk. The PEPFAR
series and the UNAIDS series must never be added together.

§5 judged the geographic file the safer national total wherever the geographic file and the partner
file disagree, after Namibia's partner-file TX_CURR of 298,637 in FY2022 was set against 200,190 in
the geographic file. The comparison was made for the §5 correction and was not repeated on later
runs. `pepfar_panorama` now compares every row the connector emits with the geographic file's
national figure for the same country, code and year, a snapshot at the quarter the row was read at
and a flow as the sum of the quarters. A row more than five per cent away keeps the partner value
and carries the geographic value, the ratio and the direction in `extra.geographic_total_differs`.
Values are never replaced. The count of rows above the geographic file falls from 335 past half of
one per cent to 222 past two per cent and 157 past five per cent, and five per cent is the
tolerance. The dry run of 19 September 2026 checked 3,338 rows over 11 codes from FY2018 to FY2025,
found 3,101 rows within five per cent and 2,892 within half of one per cent, and flagged 157 rows
above the geographic file and 79 below.

The 157 rows above the geographic file belong to 19 countries, Namibia 33, Kazakhstan 19,
Tajikistan 18, Laos 16, Kyrgyzstan 11, Lesotho, Malawi and Vietnam 10 each, and 11 other countries
with six rows or fewer, and reach 2.17 times the geographic figure. Kazakhstan's TX_CURR is exactly
twice the geographic figure in every year from FY2021 to FY2025, because two mechanisms report the
same patients, mechanisms 81234 and 85713 at 5,234 each in FY2023. Namibia reaches 1.56 times on
TX_NEW in FY2022. The `pepfar_agency` rows split the same partner totals by funding agency and carry
the same excess, and the note on every flagged row of TX_CURR, TX_NEW or HTS_TST_POS says that the
`pepfar_agency` rows carry the same excess. The 79 rows below the geographic file belong to 13
countries, Thailand 12, Colombia 10, Guatemala nine, Honduras and Panama eight each, and eight other
countries, and 69 of the 79 rows fall in FY2018 and FY2019, the years in which §9l found PEPFAR's
regional operating units naming few partners. The lowest is Panama's TX_CURR in FY2018, 31 against
11,932, and Thailand's HTS_TST in FY2018 stands at 1,308 against 75,944. The note on a row below the
geographic file calls the row a floor for the PEPFAR programme and warns that a fall against
another year may be missing reporting and not missing services.

The survey of 19 September 2026 first reported that the rows below the geographic file already
carried a discontinuity or `partners_absent` flag, and the survey was wrong. On the panel of 5
September 2026, 56 of the 80 rows more than five per cent below carried no warning of any kind in
`extra`, 15 carried `partial_year`, six carried a discontinuity flag, two carried `partners_absent`
and one carried only a snapshot-quarter mismatch. The change Jason approved flags rows above the
geographic file, and the rows below are flagged as well because the 56 unflagged rows would
otherwise read as measured falls. Dropping the flag on rows below is a one-line change if Jason
prefers the approved scope. The 80th row, Laos TX_PVLS in FY2019, is read at the first quarter, and
at the first quarter the geographic file gives the same 534, so the check passes the row. **The
general rule. A comparison that decides which of two totals is safer protects a later reader only
if the comparison runs inside the connector on every run and leaves the answer on the row.**

The claim row of 4 August 2026 that PEPFAR has no agency × province anywhere was wrong.
`Partner_Performance` names the funding agency of every partner in every priority sub-national unit
(PSNU), the unit at which PEPFAR plans a country's programme, for every quarter from FY2018 to
FY2025. The file carries 1,188 PSNUs over 61 countries, four of the PSNUs in Bahamas and Belize,
which carry no ISO3 code. Of the 59 countries with an ISO3 code, 15 have one PSNU covering the whole
country and 44 have more than one, 1,169 PSNUs in all. The PSNU sits at the geographic file's first
sub-national level in 17 of the 44 countries, at the second level in 22 and at the third level in
four, and Mali's PSNU names match no level of the geographic file until accents such as the one in
`Ségou` are normalised. Among the 26 countries for which `pepfar_snu` emits provinces, the PSNU
names equal `pepfar_snu`'s province names in 17 countries and sit lower, at district level, in
nine, among them Uganda with 146 PSNUs against 10 provinces and Zambia with 116 against 10. The
PSNU sits one level below `pepfar_snu`'s province in eight of the nine and two levels below in
Malawi, where 28 PSNUs fall under four provinces. The claim of 4 August named every geographic and partner file as checked and said that the
partner files stop at the country, and `Partner_Performance` does not stop at the country. **The
general rule. A claim that a publisher lacks a split is a claim about every file the publisher
releases. Before such a claim is written down, every file in the catalogue has to be opened and
every column read, and the claim has to name the files checked.**

`Partner_Performance` adds every partner's count without removing the people two partners both
report, and agrees with `pepfar_panorama` within half of one per cent in 389 of 406 TX_CURR
country-years. Held against the geographic file province by province for FY2024, the partner sum
lies within five per cent in 390 of 399 provinces on TX_CURR, 385 of 401 on TX_NEW and 387 of 394
on HTS_TST_POS, with a median ratio of 1.000 and no province more than five per cent below. The
provinces above lie in Kyrgyzstan, Kazakhstan, Tajikistan, Namibia, India, Haiti and Botswana. In
FY2024, 116 provinces report TX_CURR through USAID-funded partners alone, 167 through CDC-funded
partners alone and 116 through a mix of agencies. In 15 countries, among them Kenya, Mozambique,
Nigeria, South Africa, Tanzania, Uganda, Zambia and Zimbabwe, the USAID share of TX_CURR runs from
under 20 per cent in one province to over 80 per cent in another. No national series can show that
spread, which is the variation within a country in exposure to the closure of USAID.

Jason approved connector 25 on 20 September 2026, and `pepfar_agency_snu` emits the three
`pepfar_agency` codes with the agency suffix at admin1 for FY2018 to FY2025. Connector 25 places
each PSNU in the province `pepfar_snu` writes, through the geographic file's own SNU1, SNU2 and
SNU3 columns, and three rules settle every placement. A PSNU whose folded name equals the
country's own name never places, because such a unit is a national figure wearing a province's
label. Every PSNU in one country resolves at a single level of the hierarchy, the level most of
that country's PSNUs match, and no single PSNU falls through to a lower level when the country's
chosen level fails to match that PSNU. A PSNU resolving to a province that `pepfar_snu` does not
name is not emitted by connector 25 either, so the two connectors write the same province names.
Accents are folded before any name is matched, so Mali's `Ségou` places and Mali no longer waits
on accent normalisation. The release cadence is voted on the country's own rows before any PSNU is
placed, through `pepfar_panorama`'s `release_cadence`, so a province and the country that province
sits in cannot disagree about which years are short. Five PSNUs are named `Data reported above
PSNU Level`, one each in Burkina Faso, the Democratic Republic of the Congo, Liberia, Senegal and
Sierra Leone. Only the Congolese heading carries any of the three codes, 43 in all, which
connector 25 logs and leaves out of the panel. The 15 countries whose PSNU is the whole country
are refused and stay covered nationally by `pepfar_agency`. Targets, including the FY2025 targets
set before the freeze, are read and never emitted as values, and since 21 September 2026 every
row carries its agency's target in `extra`, as the section on targets below sets out.

TX_CURR is a snapshot and not a sum, so connector 25 settles one quarter for each
country-indicator-year, the latest quarter any partner in any province of that country reports, and
applies that one quarter to every province and every agency in the country alike. A province-agency
series that reported earlier in the year and not in the settled quarter is absent from that year and
is not carried forward, which the run logs country by country, 41 province-agency series over 22
country-indicator-years, Vietnam FY2019 the largest with 14 series. **The general rule. When one
figure is a snapshot, every part of a partition has to be read at the same date, because parts read
at different dates do not add up to the whole and the disagreement looks like a measured change.**

The survey also found a gap in `pepfar_snu`. The connector skipped the 35 countries whose only SNU1
is the country's own name, treating such a unit as a national total wearing a province's label. The
claim row of 4 August 2026 gives 35 countries, and the connector's docstring gave 33 until 20
September, because Bahamas and Belize carry no ISO3 code in the geographic file and a count grouped
on the ISO3 column leaves both out, while the connector resolves both from the `Country` column. The
survey of 19 September made the same omission. In all 35 countries every row carrying a value names
an SNU2, and the units are provinces, departments, states or districts. Thailand names 17 provinces,
Guatemala 19 departments, Myanmar 14 states and regions, Laos six provinces, Cambodia six, the
Philippines five and Indonesia four, so six of the nine Southeast Asian countries of
[`PHASE2_FEASIBILITY.md`](PHASE2_FEASIBILITY.md) had PEPFAR provinces the panel did not hold.

Jason approved reading SNU2 on 20 September 2026, and `pepfar_snu` now reads two levels. A country
is read at SNU2 where two or more of its SNU2 units carry a value on the six MER codes the connector
reads, which admits 29 countries and 203 units. Bahamas names New Providence Island alone, Barbados
names Saint Michael Parish alone, Colombia's only named unit is Antioquia beside `_Colombia
Aggregated PSNU`, which holds 99.88 per cent of Colombia's total, Peru's whole programme sits on
`_Peru Aggregated PSNU`, and Guyana and Trinidad and Tobago reach two units only on indicators the
connector does not read. The same two-unit test is applied a second time per indicator-year and
drops a further 100 country-indicator-years out of 5,446, each one a year where the country named
several units on its other indicators and one unit there, Papua New Guinea 43, Indonesia 15,
Suriname 11, China seven, Ghana six and ten countries with fewer than five each. Every emitted row
now carries `extra.unit_level`, which says whether the row was read at SNU1 or at SNU2.

Recounted 20 September 2026. The figure of 239 units over 31 countries, recorded on 19 September and
recounted the next day, counts every one of the 35 indicators in the geographic file, and 203 units
over 29 countries is the count over the six codes `pepfar_snu` reads. The survey of 19 September
first gave 238 units over 30 countries, because that count took SNU2 names from every row and so
counted Roraima in Brazil and Nickerie District in Suriname, which carry no value, and missed
Belize's three districts. The claim row below is corrected to 203 over 29.

The offline dry run of 20 September 2026 emitted 27,328 rows over 591 units in 55 countries, against
14,517 rows over 388 units in 26 countries before the change. The 14,517 rows already in the panel
came back with every column unchanged, `extra` included, apart from the new `unit_level` key every
row now carries. The release cadence vote is taken before any country moves from SNU1 to SNU2 for
that reason, since regrouping a country's rows would otherwise move a partial-year flag on a
province of a country that already had provinces. Of the 12,811 new rows, 6,216 are the 203 SNU2
units and 6,595 are TX_NEW and HTS_TST at SNU1 in the 26 countries. The emitted SNU2 units reproduce
the geographic file's own national figure exactly in all 1,047 country-code-years they cover, none
above it and none below, and the 100 country-code-years that the per-indicator-year test drops are
exactly the 100 the comparison cannot be made for. The validator gains one message, a fall in the
countries reporting `prep_recipients` from 48 in FY2024 to 32 in FY2025, and the reconciliation is
unchanged at 96 pairs with nothing added, lost or reclassified.

The offline dry run of connector 25 on 20 September 2026 emitted 12,705 rows over 455 provinces in
43 countries in 12 seconds, FY2018 to FY2025, with no null value, no negative value and no duplicate
key. The rows divide into `new_diagnoses_usaid` 2,295, `new_diagnoses_cdc` 2,157,
`art_initiations_cdc` 2,124, `on_art_count_cdc` 2,105, `art_initiations_usaid` 1,744,
`on_art_count_usaid` 1,737 and 543 rows under the pooled other-agency suffix. Counted by agency
instead of by code, the rows are 6,386 CDC, 5,776 USAID and 543 other.
11,483 rows name a province `pepfar_snu` reads at SNU1 and
1,222 name a province `pepfar_snu` reads at SNU2, 1,550 rows carry a partial-year flag, and the
settled snapshot quarter is the fourth in 3,958 rows, the third in 36 and the second in one. The
partner file names 58 countries on the three codes, and Bahamas, Belize and Cambodia are not among
the 58, because the PSNUs those three countries name carry no value on TX_CURR, TX_NEW or
HTS_TST_POS in any year.

1,015 PSNUs carry a value on the three codes, 999 place in a province and 16 do not. The PSNUs that
do not place are the single PSNU of each of the 15 refused countries, Barbados, Colombia, Guatemala,
Guyana, Honduras, Jamaica, Laos, Nicaragua, Panama, Peru, the Philippines, El Salvador, Suriname,
Thailand and Trinidad and Tobago, together with the Democratic Republic of the Congo's `Data
reported above PSNU Level` heading. Placement settles at SNU1 in 17 countries, at SNU2 in 22 and at
SNU3 in four, Brazil, Indonesia, Malawi and Sierra Leone, and finds no level in the 15 refused
countries. Of the 527,123,747 the partner file carries on the three codes, 99.02 per cent is placed
and 0.98 per cent falls in the refused countries and the Congo's heading.

In FY2024 connector 25 covers 406 provinces over 42 countries, against the 487 provinces over 50
countries `pepfar_snu` emits for FY2024, so the FY2024 figures of 339 provinces over 26 countries
and 399 provinces over 41 countries, both written before `pepfar_snu` read SNU2, are superseded. The
nine countries `pepfar_snu` holds in FY2024 and connector 25 refuses are Guatemala, Honduras,
Jamaica, Laos, Nicaragua, Panama, the Philippines, El Salvador and Thailand, 82 provinces in all.
One province runs the other way. Papua New Guinea names one PSNU in the partner file, National
Capital District, which is a real district and not the country's own name, so the district places
and carries 24 rows. `pepfar_snu` emits Papua New Guinea in FY2016 and FY2017 only and drops the
later years through the two-unit test above. Papua New Guinea is the only country where connector 25
emits a single province, and the 189,816 the National Capital District rows carry over three codes
and eight years are the whole PEPFAR programme in the country, which is what a footprint row means
and not a provincial share of a national total.

Three checks run on every run of connector 25. The emitted provinces reproduce the partner file's
own national figure in 5,860 of 7,593 country-code-agency-year-quarter cells, exceed that figure
in none and fall short in 1,733, and every cell falling short lies in one of the 15 refused
countries or in the Congo's heading. Against `pepfar_snu`'s deduplicated provinces, over 9,060
province-code-years the two connectors agree within one part in a thousand in 8,282, connector 25
stands above `pepfar_snu` in 777 and below in one, Lualaba in the Democratic Republic of the Congo
on HTS_TST_POS in FY2020 at a ratio of 0.994. Standing above is what a partner sum does, because a
patient two partners both report is counted twice, and the largest ratio anywhere is 2.167. 54 of
the 777 province-code-years sit at exactly two, in Kazakhstan from FY2021 to FY2025, Kyrgyzstan
from FY2021 to FY2024, Tajikistan from FY2021 to FY2023 and in FY2025, Namibia in FY2020 and
FY2022 and Vietnam from FY2018 to FY2020. The claim
row recording Kazakhstan's doubled TX_CURR left open whether any other country doubles, and
Kyrgyzstan, Tajikistan, Namibia and Vietnam double in the same way, province by province.

The third check holds connector 25 against `Public_Partner_MER_TopLine`, the file `pepfar_panorama`
and `pepfar_agency` read. At the country-code-agency-year-quarter grain 7,320 cells agree, 85
disagree, no cell exists in TopLine and not in `Partner_Performance`, and 188 cells exist in
`Partner_Performance` and not in TopLine, carrying 518,523. TopLine is the lower figure in all 85
cells that disagree. The 273 cells fall in four years, 129 in FY2018, 114 in FY2019, 18 in FY2021
and 12 in FY2022, and no cell from FY2020 or from FY2023 on differs, so the years the funding cuts
fall in are untouched. The deduplicated geographic file sides with `Partner_Performance` wherever
the geographic file holds the same country-year, Panama's FY2018 treatment cohort being 31 in
TopLine, 11,956 in `Partner_Performance` and 11,932 in the geographic file. The short file is
TopLine.

Recounted 21 September 2026. The TopLine shortfalls first recorded here, Kenya 283,804, Thailand
223,636, Panama 66,155, Jamaica 61,969, El Salvador 51,873, Guatemala 47,070, Uganda 45,949 and
Honduras 31,849, are wrong. Those figures added TX_CURR's four quarters together, which counts
the same patients up to four times, and added the shortfalls of different years together as well.
Read the way the panel reads TX_CURR, at the one quarter each country-year is read at, the
shortfall in people on treatment is 49,973 in Kenya in FY2018, 42,393 in Thailand in FY2019 and
25,780 in FY2018, 13,625 in Panama in FY2019 and 11,925 in FY2018, 12,531 in Guatemala in FY2018
and 8,438 in FY2019, 10,985 in Uganda in FY2021, 10,938 in El Salvador in FY2019, 9,512 in Jamaica
in FY2018 and 5,032 in FY2019, 6,429 in Trinidad and Tobago in FY2018, and 6,005 in Honduras in
FY2019, with eight smaller country-years below 2,500. On new diagnoses and initiations 51
agency-years fall short, the largest Kenya's USAID HTS_TST_POS in FY2018 at 10,402. Connector 25
now logs the shortfall country-year by country-year, and never adds TX_CURR across quarters or
across years.

Jason left the decision on correcting TopLine to rigour on 21 September 2026, and the TopLine
values stay as TopLine publishes them. Replacing a value with another file's figure would leave a
reader unable to say which file a number came from, and would mix two releases of PEPFAR's
partner data in one series. Every `pepfar_panorama` and `pepfar_agency` row whose annual value
differs from `Partner_Performance` by more than 0.5 carries the `Partner_Performance` figure
beside its own in `extra.partner_file_differs`, with the difference, the ratio and a note saying
the TopLine value is a floor. The threshold is 0.5 and not the geographic check's five per cent,
because the two files add the same partners together and should agree exactly. The offline dry
run of 21 September 2026 flags 62 `pepfar_panorama` rows and 26 `pepfar_agency` rows, all in
FY2018, FY2019, FY2021 and FY2022, and `Partner_Performance` is the higher figure in every one of
the 88 rows. 47 of the 62 `pepfar_panorama` rows already carried `geographic_total_differs`, and
the other 15 rows would carry no warning without the new check, Kenya's FY2018 treatment cohort
among them at 1,030,790 against 1,080,763. Where TopLine has no row for an agency that
`Partner_Performance` reports, the other agencies' `pepfar_agency` rows for the same country,
indicator and year carry `agency_missing_from_topline`, 47 rows over 43 country-indicator-years.
Five country-indicator-years are in `Partner_Performance` with nothing in TopLine for any agency,
Barbados, Suriname and Trinidad and Tobago on TX_CURR in FY2018 and El Salvador on TX_CURR and
TX_NEW in FY2019, and those five have no row in the panel to carry a flag, so both connectors log
the five by name on every run. The dry run leaves every key and every value of both connectors
unchanged, 3,338 `pepfar_panorama` rows and 2,077 `pepfar_agency` rows, and adds keys to `extra`
only. **The general rule. A connector that finds a defect in another file leaves the other file's
values alone and puts the disagreeing figure on the row the defect touches, because a warning
that sits only in a run log is a warning no reader of the panel ever sees.**

USAID and CDC work the same province in about a third of the province-indicator-years the partner
file carries. Both agencies appear in 3,190 of 9,099 province-indicator-years, 35.1 per cent, in
261 of the 455 provinces over 28 countries, and 481 of the 1,331 province-indicator series change
which agencies report them at least once, 36.1 per cent. The change of FY2025 is not a change like
the others.
USAID stops reporting in 151 province-indicator-years in FY2025 against nine in FY2024, and on
TX_CURR alone USAID leaves 47 provinces in ten countries that held 1,953,646 USAID patients in
FY2024. The count of 44 provinces first recorded here left out three provinces in which no agency
reports TX_CURR in FY2025 at all, so PEPFAR's record of the cohort in those three provinces ends.
Region 7 in the Dominican Republic held 1,144 patients in FY2024, and Maharashtra and Telangana in
India held 102,745 and 66,403, with USAID holding 62,009 of the Maharashtra cohort and the whole
Telangana cohort. `pepfar_snu` also ends in Region 7, Maharashtra and Telangana in FY2025. No
FY2025 row exists in the three provinces to carry a warning, so the run log is the only record of
the three provinces, and the panel cannot say whether those patients stayed in care after PEPFAR
stopped counting them. In the other 44 provinces, over nine countries, USAID held 1,824,090
patients in FY2024, and almost all of those patients stay in PEPFAR's count under another agency.
The all-agency total in the same 44 provinces falls three per cent between FY2024 and FY2025, the
median province keeps the whole cohort USAID had been reporting, and 27 of the 44 provinces keep
more than 90 per cent of that cohort. The earlier wording, that the 1,824,090 patients did not
leave care, claimed more than a count of PEPFAR's reporting can show, and the ladder now says
only that the patients stayed in PEPFAR's count. Gauteng is the clearest case, USAID reporting
537,283 on TX_CURR in FY2024 and nothing in FY2025 while CDC goes from 681,535 to 1,166,174.
Every row whose province does not have the same agencies as the year
before carries `extra.agencies_here`, which names the agencies reporting in both years and the value
each arriving or departing agency carried, 1,878 rows in all. **The general rule. When one agency
hands a province to another, one series ends and another grows by about the same amount, and a
reader holding either series alone sees a collapse or a surge that never happened. The row has to
carry the names of the other agencies in the same province, because the warning has to be where the
reader is looking.**

Targets (decided 21 September 2026). The partner file carries the target PEPFAR set for every
agency, province, indicator and year in the country operational plan, which is agreed before the
fiscal year begins. Jason left the decision on emitting targets to rigour, and a target is never
emitted as a value, because a target is a plan and the panel holds measurements. Every row whose
agency held a target carries the target in `extra.fy_target`, and where the result covers the
whole year the row also carries `result_to_target`. For TX_CURR a whole year means the Q4 snapshot,
and for a flow a whole year means a year with every quarter the release publishes and no
truncation. In the offline dry run of 21 September 2026, 11,979 of connector 25's 12,705 rows
carry a target and 10,686 of the 11,979 rows carry the ratio, the main exception being 921 FY2025
flow rows, because the release publishes part of FY2025 only. In `pepfar_agency` 2,030 of 2,077
rows carry a target and 1,813 carry the ratio. Both connectors take the target from
`Partner_Performance` and not from TopLine, because TopLine's own target column is short of
`Partner_Performance` in 124 cells. A row whose province lost an agency also carries the departing
agency's target for the year in `agencies_here.left_target`.

The targets answer a question the results cannot, which is whether an agency's exit from a
province was in the plan. USAID left 47 provinces on TX_CURR in FY2025 and still held an FY2025
target in 46 of the 47 provinces, 2,338,910 patients in total against the 1,953,646 USAID held in
the 47 provinces in FY2024. The one province without a USAID target is South West Ethiopia, where
USAID held 48 patients. Earlier exits look different. In FY2020 USAID left 43 provinces and CDC
left ten, and neither agency held a target in any province the agency left. In FY2019 CDC held a
target in one of the 17 provinces CDC left and USAID in two of the 20 provinces USAID left, and in
FY2021 USAID held a target in two of the 21 provinces USAID left. So the FY2025 exits were not in
the plan when the FY2025 targets were set, and the exits of FY2019 to FY2021 almost all were. The
run log gives the count for every agency and year in which an agency left five or more provinces
on TX_CURR.

Nationally the same pattern holds. On the `pepfar_agency` rows carrying both a result and a
target, USAID's TX_CURR result-to-target ratio sits between 0.81 and 0.94 in FY2021 to FY2024 and
falls to 0.65 in FY2025, while CDC's sits between 0.99 and 1.03 and rises to 1.17. USAID's FY2025
TX_CURR target on those rows, 8,179,443, is seven per cent below the FY2024 target, while USAID's
FY2025 result, 5,328,202, is 28 per cent below the FY2024 result. In Kenya in FY2025 USAID reports
413,032 against a target of 471,741 and CDC reports 844,340 against 825,326. Where an agency held
a target and reported nothing in either PEPFAR file, the other agencies' rows carry
`agency_held_target_without_result`, which in FY2025 names USAID in India with a target of 195,559,
in Namibia with 6,274 and in Colombia with 2,465. The targets do not prove that the patients USAID
stopped reporting moved to CDC, and where USAID's series falls and CDC's series rises by a similar
amount, a transfer of patients still has to be ruled out before the fall is called a loss of
patients. What the targets do show is that the size of
USAID's FY2025 fall was not planned when the FY2025 targets were agreed.

The offline dry run of 20 September 2026 emitted 108 `pepfar_vmmc` rows over 14 countries, with
14,939,124 circumcisions, and Jason's run of the same day wrote the 108 rows into the panel.
Merged into the panel of 184,251 rows, the 108 rows give 184,359. The
validator's warning messages stay at 142, and the warning on rows far below the scale of their own
series rises from 345 rows to 346 with Lesotho 2011, 199 circumcisions in the first year of Lesotho's programme against 6,971 in
2012, which is kept as published. The reconciliation rises from 95 pairs to 96, the new pair being
`pepfar_vmmc` against `unaids_aidsinfo` over 108 cells with a median ratio of 0.831, classed as
independent measurement. The `pepfar_panorama` dry run of 19 September gave the flag counts above.

The dry run found that the panel of 5 September 2026 still holds the `pepfar_panorama`,
`pepfar_snu` and `pepfar_agency` rows written before the fix of 7 September (§9j), because none of
the three connectors has run since the fix. Run again on the files on disk, the three connectors
give the same 3,338, 14,517 and 2,077 rows with no value changed, and differ from the panel only in
`extra`. The new `extra` clears 101 partial-year warnings from `pepfar_panorama` rows
(`prep_recipients` FY2019 and FY2020, `tb_patients_hiv_positive` and `tb_patients_hiv_tested`
FY2018) and 379 from `pepfar_snu` rows (`prep_recipients` FY2016, FY2017, FY2019 and FY2020),
every one a year that the cadence derived under §9j reads as complete, and adds no partial-year
warning. 14 of the 101 cleared `pepfar_panorama` rows, all `prep_recipients` in FY2019 or FY2020,
gain a discontinuity flag instead, because the connector raises no discontinuity flag on a row
already marked partial. Every row of an indicator summed over the year gains the quarterly values of
§9j, 2,533 `pepfar_panorama` rows, 5,379 `pepfar_snu` rows and 1,412 `pepfar_agency` rows, while the
rows of TX_CURR and TX_PVLS, which are read at a single quarter, gain none. 439 `pepfar_panorama`
rows, 984 `pepfar_snu` rows and 231 `pepfar_agency` rows gain a like-quarter comparison. The validator and the reconciliation give the
same results with the three connectors run again as with `pepfar_vmmc` alone. §9j's claim row
that deriving the cadence removes 93 false partial-year warnings describes the connectors, and the
panel matches that claim row now that the four connectors have run together.

Jason ran `pepfar_vmmc`, `pepfar_panorama`, `pepfar_snu` and `pepfar_agency` together at 13:54 on
20 September 2026, and the run printed every line the dry run printed. The panel holds 184,359
rows, 108 keys added and no key lost, and the 164,319 rows of the other 20 sources match the panel
as it stood before the run in every column. On the 19,932 rows that the panel before the run and
the panel after the run share, no column outside `extra` and the retrieval stamp differs, so the
run changed no value. 10,129 rows carry a changed `extra`, 480 of the 10,129 losing a false
partial-year warning, and 236 `pepfar_panorama` rows carry `geographic_total_differs`, 157 above
the geographic file and 79 below. The rows of the four connectors match the dry run's rows in
every column, `extra` included, 20,040 rows on each side. The validator gives 142 messages with
346 rows far below the scale of their own series, one more than before the run, and the
reconciliation gives 96 pairs with no pair lost and no column changed on the 95 pairs that were
there before the run.

The offline dry run of 21 September 2026 ran connector 25, `pepfar_agency` and `pepfar_panorama`
with the TopLine check and the targets in place, on the files on disk, and compared the rows of
each connector with the rows the same connector holds in the panel. Connector 25 gives 12,705
rows, `pepfar_agency` 2,077 and `pepfar_panorama` 3,338, and for `pepfar_agency` and
`pepfar_panorama` no key is added or lost, no value changes and no column outside `extra` differs
except the retrieval stamp. The only keys `extra` gains are `partner_file_differs`, `fy_target`,
`agency_missing_from_topline` and `agency_held_target_without_result`, and no key already in
`extra` changes. Because `pepfar_agency` and `pepfar_panorama` now carry new keys in `extra`, the
next run has to include both connectors, together with `pepfar_snu` and connector 25, as
`python3 scripts/run_all.py --sources pepfar_panorama,pepfar_agency,pepfar_snu,pepfar_agency_snu
--countries all -v`. The panel that run writes should hold 209,875 rows, the 184,359 of the run of
20 September plus 12,811 new `pepfar_snu` rows and 12,705 connector 25 rows, with no key lost.

Jason ran that command at 08:14 UTC on 21 September 2026, and the run reproduced the dry run.
The panel holds 209,875 rows. Joined on the panel's full row key, no key is lost and the only
keys added are the 12,811 `pepfar_snu` keys and the 12,705 connector 25 keys. On the 184,359 keys
that the panel before the run and the panel after the run share, no value changed and no column
outside `extra` differs except the retrieval stamp, and the 164,427 rows of the other 21 sources
carry the same `extra`, compared as parsed JSON. The rows of connector 25, `pepfar_agency` and
`pepfar_panorama` equal the dry run's rows in every value and every `extra` field. The validator
gives 144 messages against 142 before the run. The two new messages are falls in the number of
reporting countries, `prep_recipients` in `pepfar_snu` from 48 in FY2024 to 32 in FY2025 and
`new_diagnoses_other_agency` in connector 25 from nine in FY2021 to six in FY2022. Rows flagged
as far below scale rise from 346 to 411, and all 65 new rows belong to `pepfar_snu` or connector
25. The validator also flags two new rows as far above scale, Udon Thani's FY2025 test count in
`pepfar_snu` and CDC's FY2025 treatment cohort in Mpumalanga, 543,298, in the province USAID left
with 566,088 patients in FY2024. The flag on the Mpumalanga row marks the handover and not a unit
error. The reconciliation gives 96 pairs, and no pair involves `pepfar_snu` or connector 25,
because the reconciliation compares national cells only.

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
| Summing over modality and over ragged SNU depth does not double-count | Checked before any row was emitted, recounted 2026-09-20 at the level the connector emits. Blank modality is how FY2016 and FY2017 reported (78,545,152 and 87,552,680, named modalities zero) and named modalities are how FY2018 onward reports (blank zero), the two overlapping in 26 unit-years of 8,796, all FY2025 and all DOM or MOZ, worth 26,920 against 20,000,990 and 0.0038% of the two codes' total. On ragged depth, 1,160 unit-indicator-quarter cells carry a value on both the SNU3-named and the SNU3-blank side, 537 at SNU1 and 623 at SNU2, and the two sides are equal in five, each holding one named SNU3 unit at 3, 5, 7, 62 and 71. Elsewhere the blank side runs 0.002 to 221 times the named sum, so the blank rows are residuals and not totals |
| ~~0 SNU2 groups carry a value on both the SNU3-named and SNU3-blank side~~, corrected 2026-09-20 in the row above | The count of 2026-08-04 is wrong. 1,160 cells carry a value on both sides. The conclusion it supported still stands, because five of the 1,160 are equal and all five are one small number beside another |
| ~~PEPFAR has no agency × province anywhere~~, corrected 2026-09-19 in §9w | ~~Every geographic and partner file in the catalogue checked 2026-08-04: agency appears only in the partner files, which stop at the country~~. `Partner_Performance` names the funding agency of every partner in 1,188 priority sub-national units over 61 countries, FY2018 to FY2025 |
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
| PEPFAR Spotlight publishes 15 datasets and the pipeline reads 3 | Dataset paths taken from `data.pepfar.gov/static/js/main.9f74f1e6.js` 2026-08-15; all 15 return 200 unauthenticated from `data.pepfar.gov/media/`; connectors read `Enhanced_Geographical_Analysis`, `Public_Partner_Budgets_and_Expenditures`, `Public_Partner_MER_TopLine`. *Seven read as of 2026-09-19*, the four additive files added by `pepfar_modality`, `pepfar_ou_budgets`, `pepfar_commodities` and `pepfar_hrh` (§9v) |
| Four of the unread files are additive | `PEPFAR_OU_Budgets_and_Program_Expenditures` (budget from 2004, by Program/Sub Program/Beneficiary, against the partner file's FY2021 start), `PEPFAR_OU_Commodities_Procurements` (planned budget by commodity item, COP18 to COP24, with a quantity column that changes unit between years, so the budget alone is usable. *Corrected 2026-09-19* from "planned ARV/RTK quantity and budget", §9s), `Country_Level_Results_by_Modality_Coarse_Age_and_Sex` (28 modalities, `TX_RTT`, loss-to-follow-up reasons), `HRH_Inventory_Public_Dataset` (FY2025 workforce, meaning the spend, full-time equivalents and headcount of PEPFAR-funded staff by category, cadre, programme and interaction type, one year only and not the national health workforce. *Read 2026-09-19* by `pepfar_hrh`, §9v) |
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
| PEPFAR's modality file is a decomposition of a total the panel already held | Run of 7 September 2026. Summing HTS_TST across modality, age and sex gives 415 country-years over 58 countries against `pepfar_panorama`, median ratio exactly 1.000000, 349 inside 0.5%; HTS_TST_POS against `new_diagnoses` the same 415 and the same median. The reconciler reached `derived` on the testing pair unprompted |
| The partner sum undercounts the country in regional operating units | Thailand FY2018 names one partner, Bangkok Metropolitan Administration, 1,308 tests against 75,944 in the country-level file; FY2019 1,752 against 136,227; from FY2020 three partners and agreement to 1.000000. Every country-year more than 5% short belongs to South and Southeast Asia Region, Central Asia Region or Central and South America Region, except Kenya FY2018 at 5.8% |
| Eleven country-years run the other way and are unexplained | This file 3–54% BELOW the partner sum, worst MWI 2018 (0.462) and NAM 2020–22 (0.675–0.744). Shortfall even across all four quarters, no modality absent. The age hypothesis was tested and refuted: Namibia's Unknown Age share is 28–30% in exactly the years it falls short |
| A modality that appears only in the year the answer changes is excluded from the answer | `Not Specified` carries 0 HTS_TST before FY2025 and 784,344 in Q4 FY2025, in seven countries (THA, MOZ, HTI, DOM, BWA, JAM, ZMB), 727,005 of it Thailand. Thailand's classified testing in Q4 FY2024 was 45,211 across both arms. Counted into the total, put in neither arm, flagged in `extra.unclassified_tests`, and all seven held out of the headline |
| Community testing fell four times as far as facility testing | Q4 FY2024 → Q4 FY2025 over the 52 clean countries: community 3,056,545 → 1,068,854 (-65.0%), facility 16,021,304 → 13,517,748 (-15.6%), share 16.0% → 7.3%. Community fell further in 21 of the 26 countries over 20,000 tests a quarter with both arms running, UGA -93.5 against -10.3, NGA -83.4 against -15.8 |
| Outreach was cut before the clinic, and yield rose as it went | Community positives 51,185 → 34,825 (-32.0%) against facility 294,968 → 241,411 (-18.2%); community positivity 1.67% → 3.26% while facility positivity moved 1.84% → 1.79% |
| The reconciler splits identical pairs on a two-cell margin | Same run. `pepfar_modality` against `pepfar_panorama`, identical 415 cells, both at median relative difference 0.000000 and median ratio 1.000000: `hiv_tests_performed` agrees within 2% on 374 cells and is `derived`, `new_diagnoses` agrees on 372 and is `independent`. The `derived` test needs 374 |
| Eight independent pairs are identical on the typical cell | 8 of 65 independent pairs, holding 8,567 of 28,671 independent cells (panel of 2026-09-19, which added the 46-cell `pepfar_ou_budgets` against `gam` pair at 7.2%; 8 of 64 and 28,625 before it), have a median relative difference at or below 1%. AIDSinfo against WHO GHO is `derived` on `hiv_tests_performed` (323 cells) and `independent` on `aids_deaths` (3,264), `pmtct_arv_count` (1,515), `on_art_count` (2,030) and `hiv_test_positivity_pct` (321), all at or below 1%. **Unfixed pending a decision** |
| The OU budgets file and the partner file are the same money | Restricted to ISO3 rows with the three aggregate layers removed: FY2021 budget 5,036,285,258 in both, FY2021 expenditure 4,121,559,166 in both, FY2025 budget 4,281,549,540 in both, FY2025 expenditure 2,789,722,472 against the panel's 2,789,722,474. `pepfar_ou_budgets` therefore emits nothing after 2020 |
| ~~Excluding that file cost the panel seventeen years~~ — corrected 2026-09-19, see below | Counted the 2004 budget column, 68,991,569 over 11 countries, as a year's budget. §9r shows the 2004 column is one figure per country split 70/30 by a fixed rule. 611 rows, 496 budget and 115 expenditure, was the count with the 2004 column emitted |
| Excluding that file cost the panel sixteen years | `Public_Partner_Budgets_and_Expenditures` starts at FY2021. The OU file carries budget from 2005 (1,069,544,078 over 14 countries) to 2020 (4,657,232,673 over 53) and expenditure from 2018. 600 rows recovered, 485 budget and 115 expenditure, over 55 countries. Run into the panel 2026-09-19, taking the panel from 183,000 to 182,989; the 11 rows removed are exactly the 2004 budget rows and no other value moved |
| The file carries three aggregate layers, not one | 12,062 rows = 11,919 detail + 71 `Program = Total` + 71 `Applied Pipeline` + 1 footer row whose only populated fields are `Operating Unit = Total` and the money. The footer was found by arithmetic: the remainder after removing the country totals came to exactly 2.0000× those totals in all 30 money columns at once |
| The rebuilt budgets reproduce PEPFAR's own totals | Detail plus Applied Pipeline against the `Program = Total` row: exact in 770 of 773 country-years carrying a budget, the other three differing by more than a dollar and far less than 1%. Checked at runtime at 0.5%, so a future download that breaks it says so |
| Management and Operations corrupts every execution rate | About 0.5bn of budget a year against almost no expenditure, flat across all years: 317m in 2018, 518m against 12m in 2025. Including it understates execution by ~10 points — 0.897 vs 0.966 (FY2018), 0.861 vs 0.939 (FY2019), 0.808 vs 0.902 (FY2020), 0.652 vs 0.737 (FY2025). Both forms carried on the row |
| The FY2025 fall is not a reporting lag, on this file's own evidence | File stamped 21 Jan 2026, under four months after FY2025 closed. A lag shrinks every programme alike; instead execution runs C&T 0.77, HTS 0.80, ASP 0.66, PM 0.56, PREV 0.45, SE 0.35. Care and treatment is what the January 2025 waiver covered. Agrees with `pepfar_expenditure`'s mechanism-reporting result, but from the same expenditure reports, so agreement and not corroboration |
| ~~455 regional rows hold 10,255,130 USD, 0.22% of 2024~~ — corrected 2026-09-08, see below | The figure was measured in 2024, a year `pepfar_ou_budgets` does not emit, and the regional share is not flat across the file. The connector reported a discard for a period it never reports |
| 463 regional rows have no country to go to | Caribbean, Central Asia, Central and South America, Pacific, two West Africa regions, `Invalid`, plus retired labels such as `Asia Region (pre-FY24)`. Over 2005–2020, the years the connector emits, they hold 623,079,124 USD of budget against the 57,308,862,383 emitted (1.08% of the dropped and emitted budget together) and 120,451,355 USD of expenditure over 2018–2020 against 11,712,716,512 (1.02%). Of the discarded budget, 39,714,294 sits under `Invalid` and 81,305,868 is Applied Pipeline on eight rows an earlier version of the drop branch skipped without counting. Dropped and counted in the log line, never spread across a region's countries |
| The count of countries in a year measures attribution, not where PEPFAR worked | Countries carrying a budget go 31 in 2019 → 53 in 2020. All 22 entrants already sit under an operating unit covering several countries, and the operating unit does not change across the step. Across the same step the budget on those units carrying no ISO3 falls 79,647,757 → 8,956,546 while the budget on the same units carrying one rises 46,654,139 → 194,948,927. 20 of the 22 had never appeared in any earlier year |
| Regional is a property of the file, not of the name | Defining regional as "an operating unit that somewhere appears with no ISO3" misses South and Southeast Asia Region, which covers six countries and carries an ISO3 on all 519 of its rows. Defining it as "covers more than one country" flags 28 of the 55 emitted countries instead of 22, Thailand among them |
| Three countries have a hole in the middle of the series | THA present 2010–2013, absent 2014–2019, 21,141,451 in 2020, one unchanged operating unit throughout; GUY present 2010–2016, absent 2017–2019, back 2020; MMR missing 2015 alone. Named on every row of the country in `extra.series_gap_years`; the 28 regional countries also carry `extra.funded_through_regional_ou` and `extra.coverage_warning` |
| Not every rise in the country count is an attribution change | 14 (2005) → 19 → 28 (2007). Of the 14 countries entering, 11 sit under their own single-country operating units, and rows with no ISO3 carry no budget from 2005 to 2010. Of the three one-year rises of a quarter or more in the emitted years, only 2019→2020 has most entrants already regional AND a falling regional share (1.70% → 0.19%). The runtime log reports all three and attributes only that one. The file does not say what caused the early rises. *Corrected 2026-09-19* from "PEPFAR expanded genuinely 11 (2004) → 28 (2007)", which counted the 2004 allocation column and made a causal claim the file does not settle |
| The 2004 budget column is an allocation rule, not a year's budget | 22 rows, 11 countries, 68,991,569 USD, only testing and care and treatment. Testing takes exactly 70% and care and treatment 30% in all 11, TZA 14,693,227 down to CIV 2,709,900. The same 11 carry 783,034,013 in 2005, 11.3× (4.6× to 33.3× by country). Found by following the validator's only outlier flag on the source, UGA 2004. Read, logged with the split measured on every run, not emitted |
| Management and Operations and Applied Pipeline begin in 2014 | Nothing under either before 2014; 295,636,956 and 1,180,230,636 over the emitted countries in 2014. The budget total goes 3,213,039,728 (2013) → 4,780,573,818 (2014) over the same 32 countries, and 1,475,867,592 of the 1,567,534,090 rise is the two categories. The 244 budget rows for 2005–2013 carry `categories_absent` |
| A repeated budget is not a held budget | 2010 repeats 2009 to the dollar in every programme area in all 28 countries present in both years; the 2010 total rises 32,775,394, all of it CHN, GUY and THA entering. 24 further country-years in 2016–2018 (5, 12, 7) hold the total while the split moves: AGO at 17,700,000 from 2015 to 2018, MOZ's Total row 337,075,909 in 2016 and 2017 while budget net of pipeline falls 330,523,501 → 310,403,040. Tolerance two dollars, because detail and pipeline round separately. Carried in `repeats_previous_year` with the kind named |
| The commodities file is read into the panel, budget only | The run of 2026-09-19 emitted 1,116 rows over 54 countries, 279 each for `pepfar_commodity_budget`, `pepfar_arv_budget`, `pepfar_rtk_budget` and `pepfar_lab_budget`. Used 7,736 of 8,902 lines and 5,243,853,783 of 5,537,274,918 USD (94.70%). Discarded cost categories 4.04%, condoms 1.25%, one line with no ISO3 0.01%, and 25 withheld lines carrying no money. Panel 182,989 to 184,105 over two runs, the 182,989 rows of every other source identical, reconciliation unchanged at 95 pairs, no row of the source flagged by `writers._unit_outliers` (384 flags before and after) |
| Planned ARV procurement was falling before the freeze | COP24, the plan for 2025, was written in 2024, so no figure shows the 2025 cut. Over the 23 countries planned in both 2019 and 2025, ARV 506.7m to 220.2m and the like-for-like total 861.8m to 542.3m. Over the 34 countries planned in both 2020 and 2025, ARV 487.9m to 223.6m and the total 827.8m to 549.5m. The file cannot separate price, volume and a second funder taking over the purchase |
| A budget of zero beside a quantity records who pays | All 40 condom lines in 2019 carry zero against 422.7 million condoms over 14 countries (ZMB 103,662,024). 21 country-years and 462,389,641 condoms at zero budget in all, 14 in 2019, five in 2021 and two in 2022. LSO 2024 lists 907,443 laboratory, 1,510 RTK and 30,200 VMMC units at zero, between totals of 5.94m (2023) and 5.80m (2025), and is withheld from every series (§9s) |
| The partner file averages condom lines where the sum belongs | `Condoms: Commodities` agrees with the commodities file within 0.5% in 103 of 118 country-years. 15 disagreements, all 2021 or 2022, the partner file smaller in all 15. Eight equal the sum divided by the number of condom lines (CIV 2022, 749,967 against 249,989). Seven fit no rule (COD 2021, LSO 2022, SLE 2021, SWZ 2022, UKR 2022, ZMB 2021, ZWE 2021). Five country-years carry condoms in the commodities file only. The panel reads no condom column. *Tested 2026-09-19*, the averaging does not reach `Total Planned Funding`. Each of the eight country-years books the condoms on one GHSC-PSM PREV row whose planned funding is at least the full condom sum (CIV 2022, 750,000 against 749,967), no one of the 145 condom rows exceeds the row's planned funding, and partner planned funding equals the OU file's budget within 2 USD in all 277 country-years 2021 to 2025 once the Peace Corps rows are placed by `Country` (§9t). Two PEPFAR publications agreeing, not two instruments. The 14 other cross-cutting columns are untestable and unread |
| The commodity quantity column changes unit across the file, not in Nigeria alone | 260 of 1,694 pairs of the same item in the same country in consecutive years change price per unit more than tenfold (Laboratory 161 of 630, RTKs 66 of 272, Essential Meds 17 of 261, VMMC 14 of 146, ARV 2 of 329, TB 0 of 56). Quantities are not emitted, and the count is logged on every run |
| Four cost categories are booked in some years only | In-Country Logistics from 2023 (42.6m, 41.5m, 46.7m), Quality Assurance from 2023 (8.3m, 7.3m, 6.0m), Procurement Management from 2024 (32.2m, 37.2m), `Not Specified` in 2019 only (2.2m). 794 lines, 223,952,936 USD, 4.04% of the file. Excluded from every indicator and carried in `cost_categories` on the total row |
| A category the plan does not list is zero, and the first run's three drop flags were the missing zeros | The 936-row first run was flagged on `pepfar_arv_budget` 32 (2023) to 26 (2024), `pepfar_lab_budget` 37 (2021) to 29 (2022) and `pepfar_rtk_budget` 42 (2021) to 33 (2022), all plans with a total and no line in the category. The second run writes zeros marked `category_not_in_plan`, ARV 84, Laboratory 65 and RTKs 31, and no commodity series is flagged. MLI 2024 carries 489,495 USD and no ARV line. A country-year absent or withheld still carries no row |
| A net country count hid four exits | Like-for-like total 44 countries (2023) to 43 (2024). GTM, HND, PAN and SLV leave and LSO is withheld, while COL, PER, SEN and SSD return from gaps. `writers._reporter_drops` compares net counts against `REPORTER_DROP_SHARE` = 0.15, so nothing fired. In 2024 the Central and South America Region carries one line naming `Western Hemisphere Region (pre-FY24)`, 436,870 USD of PrEP tablets. The series of 12 countries end before 2025. The four Central American countries carry the regional sentence in `coverage_warning`, 60 rows |
| The 2020 rise in the commodity country count is regional plans entering the file | 23 countries (2019) to 38 (2020), 15 of the 16 entering under a regional operating unit and no regional operating unit in the file for 2019. 38 to 47 in 2021, ten of the 12 entering regional. Seven regional operating units cover 29 countries. The §9q pattern in a second PEPFAR file |
| The full commodity plan sits between 15.8% and 17.9% of planned funding | All categories against the partner file's `Total Planned Funding`, 228 country-years over 2021 to 2025, by year 17.9%, 16.3%, 17.6%, 16.3% and 15.8%. Highest share 0.408 in COD 2023, and no commodity plan exceeds the country's planned funding. Partner rows placed by `Country` wherever `Country` and `ISO3` disagree, as `pepfar_expenditure` places the rows. *Corrected 2026-09-19* from 15.9% to 17.9% (17.9%, 16.4%, 17.7%, 16.4% and 15.9%), which was keyed on `ISO3` alone (§9t) |
| Exact duplicate commodity lines are kept | 326 lines, 22,420,358 USD, 0.40% of the file and 1.51% in 2020. UGA 2020 holds one Roche viral-load line of 4,064,808 USD twice. The file has no mechanism column to separate two mechanisms planning the same purchase from a line entered twice. Carried in `duplicate_lines` and `duplicate_usd` |
| The partner file labels 106 Peace Corps rows USA | Funding Agency `PC`, mechanism Management and Operations, `ISO3` USA and `Country` naming BWA, CMR, SWZ, KEN, LSO, MWI, MOZ, NAM, ZAF, TZA, UGA, UKR or ZMB. 28 rows in 2022, 30 in 2023, 25 in 2024 and 23 in 2025, none in 2021. 101,663,836 USD planned and 30,336,352 spent. No partner row names the United States in `Country`. Found 2026-09-19 by the averaging test of §9s |
| The panel carries the Peace Corps money under the United States | Four USA rows each of `pepfar_planned_funding`, `pepfar_planned_funding_other_agency`, `pepfar_expenditure` and `pepfar_expenditure_other_agency`, 2022 to 2025, equal to the mislabelled rows by year (planned 27,687,491, 25,330,412, 24,353,794 and 24,292,139). USA `mechanisms_budgeted` 13, 13, 12 and 12, the Peace Corps mechanisms. *Fixed 2026-09-19*. The run of 11:25 removed the 16 USA rows and raised planned funding in 50 country-years by 101,663,836 USD and expenditure in 37 by 30,336,352, in the total and the other-agency series alike, with no value lowered. The 181,039 rows of every other source and the 1,116 commodity rows are identical, the validator's 142 warnings are unchanged word for word, and the reconciliation stays at 95 pairs. The log names the rows moved on every run |
| The mislabel was small in country totals and large in the other-agency series | 50 affected country-years before the fix. Missing share of corrected planned funding median 0.85%, largest 6.04% (BWA 2022), of corrected expenditure largest 4.12% (BWA 2024). Missing share of corrected other-agency planned funding median 19.2%, largest 75.2% (BWA 2024). Other-agency expenditure read zero in BWA 2024, NAM 2023 and NAM 2024 and now reads the Peace Corps spending of 1,675,092, 528,167 and 646,038 USD |
| The 2021 to 2022 fall in the other-agency series was partly the mislabel | Peace Corps rows carry the right code in 2021 (40 of 40). BWA other-agency planned funding 6,943,294 (2021) and 2,564,110 (2022) before the fix, a fall of 63%, and 6,279,181 in 2022 in the panel since the fix, a fall of 9.6% |
| The OU file settles which partner column is wrong | Keyed on `Country`, partner planned funding equals the budget of `PEPFAR_OU_Budgets_and_Program_Expenditures` (detail rows) within 2 USD in 277 of 277 country-years 2021 to 2025, and expenditure within 2 USD in 271 of 278 and within 4 USD in 278 of 278. Keyed on `ISO3`, 227 of 281 and 238 of 281. The two files split totals across programme areas differently, so the agreement holds at country-year only |
| The partner file books spending on `All for OU` lines with no budget | 506 `All for OU` rows under 12 agencies, 490 agency-country-years. 375 carry budget only, 72 budget and spending, and 43 spending only, 20,644,073 USD. Spending-only lines by agency USAID 18, PC 13, HHS/CDC five, State/AF five, HHS/HRSA one and DOD one, and 18 spending-only lines in 2025 (12,500,610 USD). Every spending-only line sits beside a budgeted mechanism of the same agency that filed no expenditure. The spending-only lines fall in 42 agency series-years, because MOZ 2025 pools PC and State/AF in the other-agency series (§9u) |
| The Peace Corps moved the 2025 spending off the Management and Operations mechanism | Management and Operations spending 7,435,672 (2022), 10,556,066 (2023), 12,344,614 (2024) and 0 (2025) against 24,292,139 USD planned in 2025. PC `All for OU` 2025 976,618 planned (LSO alone) and 12,385,194 spent, 11,544,602 USD of the PC spending on lines with no budget in 12 countries (ZMB 2,462,597, BWA 2,019,855). The partner file does not say why the PC spending moved (§9u) |
| The five warnings the Peace Corps fix added come from the `All for OU` booking | MOZ, MWI, SWZ, UGA and ZMB other-agency 2025. Crediting each spending-only `All for OU` line to one silent mechanism of the same agency, against the uncredited rate of the year before, clears 11 of the 33 lower-bound warnings, the five added warnings among the cleared (MOZ 3/8 in 2024, 2/8 in 2025, 4/8 credited). 22 lower-bound warnings still fire, among them ZAF USAID 2025 (29/36 to 7/34, 8/34 credited) and SEN USAID 2025 (3/6 to 1/6, 2/6 credited), so the booking does not explain the USAID fall of 2025. One mechanism per line is a reading, not a bound (§9u) |
| The `All for OU` booking is marked and not corrected | `ou_level_unbudgeted_expenditure` on all 970 expenditure rows, above zero on 79. The lower-bound sentence on 33 of 214 completeness warnings. No value and no reporting rate changed, checked row by row against the dry run without the field. *Written and run 2026-09-19* (§9u) |
| The staff inventory is read into the panel, fiscal year 2025 only | The run of 2026-09-19 emitted 162 rows over 54 countries, 54 each for `pepfar_hrh_spend`, `pepfar_hrh_fte` and `pepfar_hrh_fte_service_delivery`. Used 2,933 of 2,974 rows and 1,221,921,849 of 1,223,427,353 USD (99.88%), 175,770.29 FTE and 128,250.50 service-delivery FTE. Panel 184,089 to 184,251, the validator's 142 warnings and the reconciliation's 95 pairs unchanged, no pair involving `pepfar_hrh`. The 162 rows on disk match the offline dry run in every column, and the 184,089 rows of the other sources match `hiv_panel.prev.csv` in every column (§9v) |
| The inventory's headcount may count one person twice | `Individual Count` sums to 274,456 against 175,844.14 FTE. FTE per head median 0.664, tenth percentile 0.11, no row with more FTE than heads. The guide refers the inventory's rules to an HRH Inventory Handbook not on disk (page 66). Carried in `extra.individual_count` with a warning and in no series (§9v) |
| Spend and FTE weight the staff categories differently | Other staff 63.9% of spend and 47,634 FTE, clinical 22.7% and 45,948, ancillary 13.4% and 82,262. Spend per FTE 16,416 USD for other staff, 6,046 for clinical and 1,990 for ancillary. A post is classified by the employment terms of the position and not by qualification (guide page 65) |
| Ukraine's inventory is one row and is withheld | `IM Program Management`, other staff, 766,678.95 USD, 11 in `Individual Count`, 0.21 FTE, against 40,722,026 USD of 2025 expenditure in the partner file, a share of 0.019. Next lowest NGA 0.275, COD 0.289 and RWA 0.313. Withheld below 0.10, and any threshold from 0.02 to 0.27 withholds UKR alone (§9v) |
| A country with no service-delivery row is not an incomplete inventory | KHM 2025, 13 rows and 73.14 FTE, every row other staff under ASP or PM, inventory spend 54.9% of the country's expenditure. The service-delivery series is emitted as zero with `no_service_delivery_rows` |
| Forty inventory rows name no country | 31 rows `Central Asia Region` (656,618 USD, 72.88 FTE) and nine `Data not provided at this geographic level`, one under CSA, five under WAR1 and three under WAR2. 738,825 USD, 282 in `Individual Count` and 73.64 FTE in all, dropped and counted. Seven regional operating units hold 788 rows and 74,572,975 USD. 29 countries carry `funded_through_regional_ou`, and 19 of the 29 carry a `coverage_warning` |
| Inventory spend is about half of PEPFAR expenditure | Against the partner file's `Total Expenditure`, partner rows placed by `Country` (§9t), over 54 countries the median share is 0.515 and the overall share 0.444, highest JAM 0.762 and lowest NGA 0.275. No country above 1, and every country with 2025 expenditure has inventory rows, withheld UKR aside |
| The partner file's `Human Resources for Health` column is not staff pay | The guide defines the programme area as above-site work to strengthen the health workforce, pre-service training and national workforce planning among the examples (pages 50 and 51). The column totals 19,829,631 USD in 2025 over placed rows and is filled for 39 of the 54 countries, and inventory spend is a median 40 times the column. Logged and never compared with the inventory (§9v) |
| Inventory rows with no FTE, and rows above 500,000 USD per FTE, are kept | 30 rows with no FTE and 23,580 USD. Eight rows above 500,000 USD per FTE, 1,179,430 USD in all and at most 0.38 FTE on a row, UKR's single row among the rows above 500,000 USD per FTE. Counted in the log on every run |
| Four Spotlight files are the geographic file split by age, sex or facility | Summed to the country, exact against `Enhanced_Geographical_Analysis` in 1,466 of 1,466 country-indicator-years (`Operating_Unit_by_Fine_Age_and_Sex`), 1,080 of 1,080 (`Site_Performance_2021_plus`), 903 of 934 (`Site_Performance_2016-2020`) and 1,756 of 2,012 (coarse Cascade, every mismatch FY2016 to FY2018), for TX_CURR, TX_NEW, HTS_TST and HTS_TST_POS. 0 country-indicator-years in any of the four files that the geographic file lacks |
| `Public_Partner_MER_AgeSex` is TopLine split by age and sex | Equal to `pepfar_panorama` in 401 of 406 TX_CURR and 415 of 415 HTS_TST_POS country-years. The eight codes TopLine lacks are orphan and vulnerable children codes |
| Facilities reporting TX_CURR stopped faster in FY2025 | Named facilities with TX_CURR above 0 at Q4 in `Site_Performance_2021_plus`: 24,260 (FY2023), 27,098 (FY2024), 27,359 (FY2025). 779 stopped between FY2024 and FY2025 against 492 a year earlier. MMR 33 to 15, IND 130 to 81, HTI 162 to 114, NPL 53 to 38, THA 29 to 21, BDI 426 to 349. Recorded, not emitted |
| The circumcision file's years are PEPFAR fiscal years, and the file is deduplicated | Against `pepfar_panorama` FY2018 to FY2024, 92 of 101 within 0.5%, the other nine from 0.952 (ZMB 2018) to 1.030 (KEN 2018). Against the geographic file FY2016 and FY2017, exact in 27 of 28, UGA 2017 732,527 against 734,492 |
| `pepfar_vmmc` emits FY2010 to FY2017 only | Run of 2026-09-20: 108 rows over 14 countries, 14,939,124 circumcisions. The pooled 2007 to 2009 column, 73,118 in six countries, and 101 cells after FY2017 are read and not emitted. *Written and run 2026-09-20* (§9w) |
| A 0 in the circumcision file is not emitted | NGA, BDI and SLE 0 in every year 2010 to 2017 and 22 procedures after 2019. NAM 2013 0 between 6,121 and 785, BWA 2011 0 between 534 and 8,590 |
| PEPFAR's circumcisions are mostly a share of the national count | Against `unaids_aidsinfo`, all 108 country-years shared, LSO 2011 UNAIDS 0 against 199. At or below the national figure in 85 of 107, median 0.831. Above 1.25 in four, MWI 2013 1.65, SWZ 2012 1.45, TZA 2015 1.39, NAM 2012 1.26, unexplained |
| `pepfar_panorama` flags rows away from the geographic file | Dry run of 2026-09-19: 3,338 rows checked, 3,101 within 5%, 157 above (NAM 33, KAZ 19, TJK 18, LAO 16, ...) and 79 below (THA 12, COL 10, GTM 9, ...), 69 of the 79 in FY2018 and FY2019. The run of 2026-09-20 wrote 236 rows carrying `geographic_total_differs` into the panel, the same 157 above and 79 below |
| Kazakhstan's partner-summed TX_CURR is exactly double | Ratio 2.000 against the geographic file FY2021 to FY2025. Mechanisms 81234 and 85713 each report 5,234 in FY2023. Connector 25 finds the same doubling province by province in five countries, KAZ FY2021 to FY2025, KGZ FY2021 to FY2024, TJK FY2021 to FY2023 and FY2025, NAM in FY2020 and FY2022 and VNM FY2018 to FY2020, 54 province-code-years at a ratio of exactly two (§9w) |
| Most rows below the geographic file carried no warning | Panel of 2026-09-05: 56 of 80 rows more than 5% below had no warning in `extra`, 15 `partial_year`, six discontinuity, two `partners_absent`, one snapshot-quarter mismatch only. Corrects the survey note of 2026-09-19 |
| `Partner_Performance` carries agency by priority sub-national unit | 1,188 PSNUs over 61 countries, 44 of the 59 with ISO3 having more than one PSNU. Among `pepfar_snu`'s 26 countries, same names in 17 and district level in nine. Connector 25 recounts the placement over the three codes it reads: 1,015 PSNUs carry a value, 999 place and 16 do not, and the level settles at SNU1 in 17 countries, SNU2 in 22, SNU3 in four (BRA, IDN, MWI, SLE) and nowhere in the 15 refused. MLI places once accents are folded, so the survey's note that MLI matched no level is superseded (§9w) |
| Partner_Performance province sums match the geographic file | FY2024, within 5% in 390 of 399 provinces (TX_CURR), 385 of 401 (TX_NEW), 387 of 394 (HTS_TST_POS), median 1.000, none below. 1,123 PSNUs placed in one province, none in two |
| Exposure to the USAID closure varies inside countries | FY2024 TX_CURR, 399 provinces over 41 countries: 116 USAID alone, 167 CDC alone, 116 mixed. 15 countries with provinces from under 20% to over 80% USAID |
| Connector 25 writes PEPFAR's agency split at the province | Dry run of 2026-09-20: 12,705 rows over 455 provinces in 43 countries, FY2018 to FY2025, in 12 seconds. CDC 6,386 rows, USAID 5,776, other agency 543. 11,483 rows at an SNU1 province and 1,222 at an SNU2 province, 1,550 partial-year rows, snapshot quarter Q4 on 3,958 rows, Q3 on 36 and Q2 on one. No null, no negative, no duplicate key. FY2024 406 provinces over 42 countries, against `pepfar_snu`'s 487 over 50, which supersedes the earlier 339 over 26 and 399 over 41. *Built and dry-run 2026-09-20, run by Jason 2026-09-21* (§9w) |
| Connector 25 refuses 15 countries and one heading | BRB, COL, GTM, GUY, HND, JAM, LAO, NIC, PAN, PER, PHL, SLV, SUR, THA and TTO name one PSNU, the country itself, and COD's `Data reported above PSNU Level` carries 43. 99.02% of the file's 527,123,747 on the three codes is placed. BHS, BLZ and KHM name a PSNU and carry no value on the three codes in any year, so the file's 58 valued countries give 43 emitted |
| The province sums reproduce the partner file's own national figure | 5,860 of 7,593 country-code-agency-year-quarter cells exact, 0 above, 1,733 short, every short cell in a refused country or COD's heading. Against `pepfar_snu`'s deduplicated provinces over 9,060 province-code-years: 8,282 within 0.1%, 777 above, one below (COD Lualaba HTS_TST_POS FY2020, 0.994), largest ratio 2.167 |
| `Public_Partner_MER_TopLine` is short in FY2018, FY2019, FY2021 and FY2022, so two connectors understate 20 countries in those years | Against `Partner_Performance` at the country-code-agency-year-quarter grain: 7,320 cells agree, 85 disagree with TopLine lower in all 85, 0 in TopLine only, 188 in `Partner_Performance` only carrying 518,523. The 273 cells fall 129 in FY2018, 114 in FY2019, 18 in FY2021, 12 in FY2022, none in FY2020 or from FY2023 on. TX_CURR shortfall read at the snapshot quarter, by country-year: KEN FY2018 49,973, THA FY2019 42,393, THA FY2018 25,780, PAN FY2019 13,625, GTM FY2018 12,531, PAN FY2018 11,925, UGA FY2021 10,985, SLV FY2019 10,938, JAM FY2018 9,512, 12 more below 9,000. 74 agency-years over 20 countries fall short, 51 of the 74 on new diagnoses and initiations, the largest KEN HTS_TST_POS USAID FY2018 10,402. The earlier figures (KEN 283,804 and seven more) summed TX_CURR over quarters and years and are withdrawn. *Recounted 2026-09-21* (§9w) |
| USAID stopped reporting in 47 TX_CURR provinces in FY2025, and in 44 of the 47 the patients stayed in PEPFAR's count | 151 province-indicator-years lose USAID in FY2025 against nine in FY2024. On TX_CURR, 47 provinces in ten countries held 1,953,646 USAID patients in FY2024. In three of the 47 no agency reports TX_CURR in FY2025, DOM Region 7 (1,144), IND Maharashtra (102,745, USAID 62,009) and IND Telangana (66,403, all USAID), and `pepfar_snu` ends in the same three. In the other 44, over nine countries, USAID held 1,824,090, the all-agency total falls 3.0%, median province keeps the whole departed cohort, 27 of 44 keep over 90%. Gauteng USAID 537,283 to none, CDC 681,535 to 1,166,174. `extra.agencies_here` on 1,878 rows. The earlier row said 44 provinces and that the patients did not leave care, which PEPFAR's count cannot show. *Corrected 2026-09-21* (§9w) |
| TopLine values are kept, and the `Partner_Performance` figure sits on the row | Decided 2026-09-21. `extra.partner_file_differs` (value, difference, ratio, note) where the annual value differs by more than 0.5, on 62 `pepfar_panorama` rows, 47 already carrying `geographic_total_differs`, and 26 `pepfar_agency` rows, all FY2018, FY2019, FY2021 or FY2022, `Partner_Performance` higher in all 88. `agency_missing_from_topline` on 47 `pepfar_agency` rows over 43 country-indicator-years. BRB, SUR, TTO TX_CURR FY2018 and SLV TX_CURR and TX_NEW FY2019 have no TopLine row for any agency and are logged by name. No key and no value changes in either connector. *Dry-run and run by Jason 2026-09-21* (§9w) |
| Targets travel in `extra`, never as values | Decided 2026-09-21. `extra.fy_target` (value, result_to_target, note), the ratio only for a Q4 TX_CURR snapshot or a flow year with every published quarter and no truncation. In connector 25 11,979 of 12,705 rows carry a target, 10,686 the ratio, 921 FY2025 flow rows a target with no ratio. In `pepfar_agency` 2,030 of 2,077 carry a target, 1,813 with the ratio, `agency_held_target_without_result` on 25 rows. Targets from `Partner_Performance`, because TopLine's target column is short in 124 cells. *Dry-run and run by Jason 2026-09-21* (§9w) |
| USAID's FY2025 exits were not in the FY2025 plan | USAID held an FY2025 TX_CURR target in 46 of the 47 provinces USAID left, 2,338,910 against 1,953,646 held in FY2024, the exception South West Ethiopia (48). Earlier exits carried almost no target, FY2019 CDC one of 17 and USAID two of 20, FY2020 USAID none of 43 and CDC none of ten, FY2021 USAID two of 21. National USAID TX_CURR result to target 0.81 to 0.94 in FY2021 to FY2024 and 0.65 in FY2025, CDC 0.99 to 1.03 then 1.17. USAID's FY2025 target 7% below FY2024, result 28% below. Does not by itself rule out transfer to CDC (§9w) |
| One province connector 25 emits is one `pepfar_snu` drops that year | PNG names one PSNU in the partner file, National Capital District, which is a district and not the country's name, so the district places and carries 24 rows over 189,816. `pepfar_snu` emits PNG in FY2016 and FY2017 only, the later years dropped by its own two-unit test. PNG is the only country where connector 25 emits a single province |
| `pepfar_snu` reads 29 countries at SNU2 and 26 at SNU1 | 35 countries with one SNU1, BHS and BLZ resolved from `Country` because the file gives them no ISO3. In all 35 every valued row names an SNU2. Over the six MER codes the connector reads, 29 name two or more real SNU2 units carrying a value, 203 in all (GTM 19, THA 17, MMR 14, HND 12, SLV 12, PAN 12, GHA 10, NIC 10, LAO 6, KHM 6, PHL 5, IDN 4, BLZ 3). BHS, BRB, COL, GUY, PER and TTO have no provincial split to read. *Built and dry-run 2026-09-20, run by Jason 2026-09-21* (§9w) |
| ~~`pepfar_snu` skips 31 countries that publish provinces at SNU2, 239 units~~, corrected 2026-09-20 | 239 units over 31 countries counts all 35 indicators in the file, and 203 over 29 is the count over the six the connector reads. GUY and TTO reach two units only on indicators it does not read. An earlier count of 238 over 30 counted SNU2 names on rows with no value and missed BLZ |
| The panel carried partial-year warnings the fix of 7 September removed, until the run of 20 September | Panel of 2026-09-05, rows retrieved before §9j. Dry run of 2026-09-20 on the files on disk: same rows and values for `pepfar_panorama` (3,338), `pepfar_snu` (14,517) and `pepfar_agency` (2,077). Partial-year warnings cleared on 101 `pepfar_panorama` rows and 379 `pepfar_snu` rows, none added, 14 cleared `prep_recipients` rows gaining a discontinuity flag. Like-quarter comparisons added on 439, 984 and 231 rows. The run of 2026-09-20 wrote every cleared warning and every quarterly value into the panel |
| Reading SNU2 and adding TX_NEW and HTS_TST changes no row the panel already holds | Dry run of 2026-09-20. 27,328 rows over 591 units in 55 countries, against 14,517 over 388 in 26. All 14,517 keys kept, none lost, no value changed and no `extra` changed beyond the new `unit_level` key. 6,595 new rows are TX_NEW and HTS_TST at SNU1, 6,216 are the 203 SNU2 units. The emitted SNU2 units reproduce the geographic file's own national figure exactly in all 1,047 country-code-years, none above and none below. Validator 142 to 143 messages, reconciliation unchanged at 96 pairs |
| The run of 20 September changed no value outside the 108 new rows | Panel 184,251 to 184,359, 108 keys added and no key lost. The 164,319 rows of the other 20 sources identical to `hiv_panel.prev.csv` in every column. On the 19,932 rows shared by the panel before the run and the panel after the run, no column outside `extra` and the retrieval stamp differs. 10,129 rows carry a changed `extra`. The four connectors' rows match the dry run's rows in every column, `extra` included. Validator 142 messages, 346 rows far below the scale of their own series. Reconciliation 96 pairs, no pair lost, no column changed on the 95 earlier pairs |