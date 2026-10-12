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

*Corrected 2026-09-21 in §9x.* The IATI trap above is wrong. IATI's transaction types form one
codelist, in which d-portal shows codes 1 to 10 as letters and leaves 11, 12 and 13 as numbers.
Among Nigeria's HIV-sector rows, 524 of 19,525 activity, date and value keys sit under more than
one code, mostly a commitment beside a disbursement of the same amount on the same day, and no key
pairs a disbursement with an expenditure. Disbursements and expenditures are different flows and
are summed. The count of 1,834 of 46,964 keys was not reproduced.

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

### §9x. A split an aggregator makes is not the split a publisher publishes, a copied commitment is not a disbursement, and a rise in a donor series can be a change of purpose code

Work item #16 surveyed IATI, the International Aid Transparency Initiative, the standard under
which donor governments, multilateral agencies, foundations and NGOs publish records of each
organisation's own activities and transactions. The survey read the IATI records through d-portal, IATI's own open viewer,
using d-portal's query service `https://d-portal.org/q` and d-portal's XML export, on 20 and 21
September 2026. The survey wrote only to the session scratchpad, and no connector is written. The
design of connector 26, `iati`, waits on Jason's decision in section 5 item 17 of `RESUME.md`.
Money below is in US dollars by calendar year unless a US fiscal year is named, and the HIV sector
means DAC purpose code 13040, STD control including HIV/AIDS.

The first probe, on 15 August 2026, left §7g and two claim rows below saying that `sum()` in the
query service returns zero, that the transaction-type column mixes several vocabularies, and that
a connector has to pick one code or count a disbursement twice. The survey overturns the `sum()`
claim, the vocabulary claim and the double-count claim. `SUM()` works in single precision, so
Nigeria's 2024 HIV-sector disbursements come back as 395,198,700 against 395,198,777 summed row by
row. The transaction-type column holds one IATI codelist, in which d-portal shows codes 1 to 10 as
letters, 1 incoming funds (`IF`), 2 commitment (`C`), 3 disbursement (`D`), 4 expenditure (`E`), 5
interest payment (`IR`), 6 loan repayment (`LR`), 7 reimbursement (`R`), 8 purchase of equity
(`QP`), 9 sale of equity (`QS`) and 10 credit guarantee (`CG`), and leaves 11 (incoming
commitment), 12 and 13 as numbers. Among Nigeria's 20,415 HIV-sector transaction rows, 524 of
19,525 activity, date and value keys sit under more than one code. The largest overlaps are a
commitment beside a disbursement of the same amount on the same day, 288 keys, and an incoming
commitment beside incoming funds and a commitment, 181 keys, and no key pairs a disbursement with
an expenditure. The count of 1,834 of 46,964 keys in §7g was not reproduced. IATI defines a
disbursement as money passed to another organisation and an expenditure as money the publisher
spends directly. In the four sampled publishers that report both codes, three of about 66,100
expenditure rows match a disbursement row in the same activity on date and value, two at the UK's
FCDO and one at UNICEF. A connector therefore sums disbursements and expenditures, and counts no
commitment, incoming funds, interest payment or loan repayment as spending.

d-portal stores each transaction already split by country and by sector, and a read through
d-portal's activity-level country and sector tables multiplies rows. Nigeria's 2024 disbursements
read 3,168m over 24,551 rows through the activity-level join, against 395.2m over 807 rows without
the join, and 350.5m once the join's percentages are applied. d-portal's own code,
`src_dstore_db.js` lines 843 to 1039, departs from the percentages publishers publish in three
ways. Recipient-region percentages are left out of the pool, so the share an activity gives a
region is handed to the activity's countries. A country listed with no percentage is given a
weight of one, which splits the activity equally, and a negative percentage is made positive.
Sector vocabularies 1 (five-digit DAC codes) and 2 (three-digit DAC codes) are pooled and rescaled
together, so a publisher listing the three-digit code 130 beside 13040 halves the 13040 share. The
Gates Foundation shows the size of the region rule. Of the Gates Foundation's 734 HIV activities,
40 give part of the money to a region. Split by the published percentages with each regional share
left with the region, Gates disbursements come to 53.88m in 2021, 74.32m in 2022, 112.18m in 2023,
83.50m in 2024, 107.90m in 2025 and 36.37m in 2026 so far, and d-portal's split gives 55.48m,
82.37m, 130.38m, 94.43m, 119.86m and 38.73m, between three and 16 per cent higher. For 2024
d-portal gives Kenya 12.40m of Gates money against 9.39m published.

d-portal also writes a copy of every commitment as a disbursement, flagged `trans_flags=1`, for any
publisher whose commitments outnumber the publisher's disbursements and expenditures together
(`fake_trans` in `src_dstore_pg.js`). In the HIV sector the copies number 32 rows carrying 627m.
Pact (`US-EIN-13-2702768`), which publishes commitments only, holds 30 of the copied rows and
627,097,700, and Enabel, the Belgian development agency, holds two copied rows and 22,607.84. The
Pact copies read as 317.6m of disbursements in 2019 and 198.1m in 2020. Of Pact's 30 HIV
activities, 29 name USAID as the funder and one names the Global Fund, so counting the Pact copies
would count US and Global Fund commitments a second time as disbursements. Nigeria holds two of the
copied rows, 6,464,864 over all years. The Nigerian yearly totals in
[`PHASE4_FEASIBILITY_WCA.md`](PHASE4_FEASIBILITY_WCA.md) and in the claim rows were read without a
`trans_flags=0` filter, so the two Nigerian copied rows may sit inside one of the Nigerian yearly
totals. Pact also publishes one activity under a doubled identifier,
`US-EIN-US-EIN-13-2702768-P2000`. d-portal's XML export carries no copied rows. **The general
rule. A figure an aggregator has split, joined or copied is the aggregator's reading of a
publisher's record. A connector reads the publisher's own percentages and transaction codes from
the publisher's own record, and carries the aggregator's figure in `extra`, so that a reader can
see how far the aggregator's split departs from the published percentages.**

d-portal marks no HIV-sector activity as published by a secondary reporter, a publisher reporting
money another organisation manages, because `act.flags=1` returns nothing, and the XML sample
carries the `secondary-reporter` attribute only as absent or 0. The survey found no parent activity
and child activity reporting the same transactions.

Five US government publishers, US-GOV-1, 7, 10, 11 and 14, publish HIV disbursements and no
expenditures. Summed by US fiscal year over the countries that both IATI and the panel's
`foreign_assistance` series hold, the US IATI figures equal `foreign_assistance` with a median
ratio of 1.0 in every year from FY2016 to FY2024, and between 65 and 70 of the 70 to 80 shared
country-years agree within two per cent in each year. Under §9f the US IATI series is a
republication of ForeignAssistance.gov and adds no evidence about US money. FY2025 departs from
the pattern, 3,357m in IATI against 3,093m in the panel's file over 71 shared country-years, 8.5
per cent higher, with 28 of the 71 within two per cent. IATI holds 2,162m for FY2026. The panel
holds no FY2026 row, because `run_all.py` stops at `--end 2025` by default, and the docstring of
`foreign_assistance` records 613m for FY2026 in the downloaded file, a part year. The panel's copy of ForeignAssistance.gov is dated 18 July 2026, so the
likeliest reading is that the panel's copy is out of date, and a fresh download would settle
whether the FY2025 gap closes. US agencies also book HIV money to recipient codes that are not
countries, mostly 998, developing countries unspecified, 454m in 2019, 475m in 2020, 666m in 2021,
2,836m in 2022, 3,346m in 2023, 3,835m in 2024 and 2,614m in 2025. The rise from 2022 is not
surveyed.

The Global Fund publishes 1,246 HIV activities, all in US dollars, with sector vocabulary 1 only,
disbursements from 2002 to 2026 and no expenditures. The Global Fund's sector coding changed with
the grants that began in 2018. HIV grants (component H) and joint HIV and TB grants (component C)
that began from 2010 to 2016 are coded 13040 alone, and nearly every H or C grant that began in
2018 or later is split between 13040, 12110 (health policy and administrative management) and
12263 (TB control). The only H or C grants that began in 2017 and carry a split are three H grants.
d-portal's 13040 figure for the Global Fund therefore counts only part of each newer grant.

The panel's OECD CRS series for the Global Fund, donor 9OTH012, books the whole H or C grant to
HIV. The whole disbursement of H and C grants, plus the 13040 share of the Global Fund's other
grants, matches the CRS series with a median ratio of 1.0 in every year from 2012 to 2024, and
within five per cent in 95 of 98 shared country-years in 2020, 89 of 96 in 2021, 87 of 93 in 2022,
79 of 91 in 2023 and 81 of 91 in 2024. The 13040 share alone falls to between 0.52 and 0.59 of the
CRS series from 2020, and the 13040 share plus the 12110 share gives between 0.90 and 1.0. Under
§9f the Global Fund's IATI figures and the CRS series are one reporter's figures published twice.
IATI extends the Global Fund series past the CRS series. For 2025 IATI gives 1,859m of whole-grant
disbursements, of which 1,188m is the 13040 share, and for 2026 so far 723m, of which 479m is the
13040 share. Country-years in IATI with no CRS row number 10, nine, 16, 19, 26, three, six, eight,
nine and 11 over 2015 to 2024.

The CRS series appears to change classification in 2020. In the country-years where a C grant
disbursed and the CRS series holds a row, the Global Fund's whole-grant figure exceeds CRS from 2015
to 2019, 241m against 123m in 2015, 678m against 457m in 2016, 656m against 341m in 2017, 390m
against 241m in 2018 and 546m against 375m in 2019, and many C-grant countries have no CRS row at
all, 24 of 37 in 2019. From 2020 every C-grant country has a CRS row, and the C-grant countries'
whole-grant figure equals CRS, 1,302m against 1,303m in 2020. Before 2020 CRS appears to have
booked part or all of each joint HIV and TB grant under another purpose code, and the survey did
not check the other purpose codes. Over all countries the panel's CRS series rises from 1,061m in
2019 to 2,100m in 2020, while the Global Fund's whole-grant figure rises from 1,753m to 2,100m, so
692m of the CRS rise of 1,039m has no counterpart in the Global Fund's own disbursements. **The
general rule. A step in a donor series that the donor's own disbursement records do not show is a
change in how the series is classified until the donor's records show otherwise. A comparison that
crosses the step has to be made against the donor's own records, and the step has to be recorded
on the series and never read as a change in money.**

The Global Fund's reimbursement rows (type 7) are negative in every year from 2016, between 16.0m
and 82.8m a year to 2024 and 179.8m in 2025, and the survey did not establish what the
reimbursement rows record. The 13040 share of the Global Fund's multi-country and no-country grants
fell from 59.7m in 2017 to 5.3m in 2025. The 515 activities with the Global Fund's older numeric
identifiers are coded 13040 alone and carry 11,725m of disbursements. For Nigeria's H grant to the
National Agency for the Control of AIDS, NGA-H-NACA, the Global Fund's own data service and IATI
differ by 3.9 per cent, and the gap is unexplained. The Global Fund's data service,
`fetch.theglobalfund.org/v4.2/odata`, lists 32 financial indicators over 16 datasets in the entity
`AllFinancialIndicators`, among them disbursements, commitments, grant budgets, expenditure by
intervention, allocations and pledges. The panel's `global_fund` connector reads only
`AllProgrammaticIndicators` and `Geographies` from the same service, so the Global Fund's
financial datasets are unread.

The table groups HIV-sector money by the reporting organisation's declared type, in millions, with
d-portal's split and single-precision sums, over recipient codes that are countries. The
multilateral group excludes the Global Fund, and "not sampled" covers 55 publishers outside the 21
in the XML sample.

| Group | Code | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| US government | D | 3,766 | 3,330 | 3,382 | 3,667 | 3,509 | 3,966 | 3,121 |
| Global Fund | D | 1,236 | 1,442 | 1,647 | 1,544 | 1,495 | 1,470 | 1,187 |
| Multilateral (type 40) | D | 47 | 533 | 541 | 358 | 145 | 99 | −89 |
| Multilateral (type 40) | E | 106 | 127 | 318 | 390 | 414 | 292 | 293 |
| Gates Foundation (type 60) | D | 0 | 0 | 55 | 82 | 130 | 94 | 120 |
| Governments (type 10) | D | 44 | 44 | 32 | 34 | 29 | 25 | 31 |
| Governments (type 10) | E | 7 | 6 | 7 | 5 | 4 | 3 | 2 |
| Not sampled | D | 14 | 8 | 16 | 12 | 13 | 15 | 13 |
| Not sampled | E | 3 | 2 | 6 | 2 | 2 | 5 | 7 |
| Pact's copied commitments | D | 318 | 198 | 1 | 11 | 41 | 0 | 0 |

Six publishers make up the multilateral group. Counting disbursements and expenditures together,
UNAIDS spends between 55.0m and 76.3m a year, UNDP between 177.6m and 280.7m a year from 2021,
UNICEF between 30.3m and 57.2m and WHO between 1.6m and 26.8m. The Asian Development Bank disbursed
462.5m in 2020, 536.4m in 2021 and 355.3m in 2022 and shows a net negative 112.9m in 2025. The World
Bank's HIV-sector disbursements fall from 53.6m in 2020 to 1.5m or less a year from 2021 to 2024,
and reach 14.7m in 2025. Of UNDP's HIV disbursements and expenditures, 89.2 per cent, in 73 of 134
activities, sit in activities that name the Global Fund as a funder, so counting UNDP beside the
Global Fund would count the same money twice. Of the 1,554.9m that d-portal assigns the Asian
Development Bank in the HIV sector, 90.1 per cent sits under activity titles naming COVID. Titles
carrying no HIV term hold 98.1 per cent of WHO's HIV-sector money, 85.7 per cent of UNAIDS's, 75.5
per cent of the money of Germany's development ministry, BMZ (DE-1), 57.0 per cent of the Gates
Foundation's and 38.8 per cent of UNICEF's. WHO and UNAIDS titles are strategy lines such as
"Strategic Direction 1. Leadership and Advocacy". BMZ's leading titles are voluntary contributions
to the Global Fund, which is money the Global Fund's own disbursements already count. A title with
no HIV term does not make an activity unrelated to HIV, because Gates titles such as the MK-8527
prevention trial name an HIV drug without naming HIV. The largest publishers outside the sample
average 5.2m a year from 2019 to 2025, the Netherlands Enterprise Agency, followed by Norad at 3.0m,
Aidsfonds at 2.9m and UNOPS at 1.5m. Among the sampled governments, France's development agency AFD
(FR-3) averages 10.6m a year, BMZ 6.0m and Global Affairs Canada (CA-3) 4.3m. The panel's
`external_hiv_oda_total` reads CRS donor code ALLD, which `oecd_crs` describes as all official
donors, so the government and multilateral money in the table already sits inside
`external_hiv_oda_total` up to 2024. For government and multilateral publishers IATI adds a split
by publisher up to 2024 and new money only for 2025 and 2026. The Gates Foundation is a private
donor and should fall outside ALLD, and the survey did not check whether ALLD holds Gates money.
**The general rule.
A purpose code records what a publisher chose to report under the code, and a publisher can pass
on money a funder already in the panel reports. Money a publisher passes on from the Global Fund or
the US government, and money under titles that name another disease and no HIV term, has to be taken
out by the funder named and by the title, and counted in the log.**

The XML sample fetched up to 300 HIV activities from each of 21 publishers. Sida, the UK's FCDO,
UNAIDS, UNICEF and WHO reached the cap, so figures read from the XML for Sida, FCDO, UNAIDS, UNICEF
and WHO cover the first 300 activities only. The Gates Foundation was fetched in three pages, 734
activities. The group table, the title shares and the Global Fund's 1,246 activities cover every
activity.

---

### §9y. A documented endpoint can be the wrong path, a public API can be closed to every client that is not a browser, a filter documented as an array can take one value, and the same publisher can leave the same data open somewhere else

*Surveyed 23 September 2026, after Jason pointed at the ForeignAssistance.gov Data API as a
replacement for the Complete Data Set download.*

ForeignAssistance.gov publishes an OpenAPI description at `/api-docs` covering six endpoints, one
transaction-level and five aggregated. The description is accurate about the data and wrong about
the address. Every documented path begins `/data-api/`, and every one of those paths returns
nginx's 404 page. The paths that answer begin `/api/data-api/`, a prefix stated nowhere on the
site and found by trying candidates. A connector written from the documentation alone would fail
at the first request and the 404 would look like a withdrawn service.

The description's security block names an OAuth scheme whose own description says the API is
get-only public data needing no password or authentication, and whose authorisation and token
URLs point at api.example.com and test.com. The transaction endpoint carries an empty security
list. So the block is boilerplate, the documented 401 and 403 responses are unused, and no key
exists to request.

The API is nonetheless closed to the connector. Cloudflare answers 403 with the header
`cf-mitigated: challenge` to every client that is not a browser. The survey was refused with
curl, with curl carrying a current Chrome user agent, an Accept header and a Referer, and with
Python's `urllib`. The same challenge covers the bulk file at `/static/us_foreign_aid_complete.csv`.
So the manual download step in `foreign_assistance` is a consequence of the challenge and not of a
missing API, and moving the connector to the API does not remove the step. The address the
documentation gives for questions is FAgovInquiries@state.gov.

**The general rule.
A source is reachable only from the client that will do the reading. A path that answers a browser
says nothing about whether the connector can call it, and an access claim recorded from a browser
probe has to name the client that made the probe.**

The challenge closes ForeignAssistance.gov's own servers and closes nothing else. Every US
government agency publishes the same transactions as IATI XML, and the IATI Registry gives the
address of each file. USAID's 208 files, the Department of State's 207 and Health and Human
Services' 72 sit on three Amazon S3 buckets, `s3.amazonaws.com/files.explorer.devtechlab.com`,
`iati-reporting.s3.amazonaws.com` and `iati-reporting.s3.us-east-1.amazonaws.com`. Every file
probed answered curl with 200 and no challenge. The files are ForeignAssistance.gov's own output,
because the State and Health and Human Services files carry elements in the namespace
`https://foreignassistance.gov`, among them a `treasury-account` element naming the appropriation
and a `fiscal-funding-year` child.

The S3 country files reproduce one agency and fall short for the others. Nigeria HIV
disbursements, in millions of dollars, set the country file against the API for every year both
readings hold. Health and Human Services agrees closely from FY2021 to FY2025, at 75.35 against
76.19, 152.07 against 152.22, 129.99 against 130.53, 98.43 against 98.46, and 101.90 against
101.90. The Department of State agrees from FY2021 to FY2024, on sums under a quarter of a million
a year, and then parts company, at 8.82 against 23.10 for FY2025 and 46.32 against 115.13 for
FY2026. The US Agency for International Development agrees in no year at all, falling 15 to 20 per
cent short from FY2013 to FY2018 and between a half and two thirds short from FY2020, at 53.67
against 145.51 for FY2020, 63.58 against 190.08 for FY2024 and 48.71 against 148.11 for FY2025.

A country file carries the bilateral mission's money and leaves out the money a central bureau
manages, which is why the country files fall short. The API's sub-agency field shows the split.
Nigeria FY2024 under the US Agency for International Development divides into 110.75 million
managed by the Global Health bureau and 79.32 million managed by the Africa bureau. Nigeria FY2026
under the Department of State is 115.13 million managed in full by the Bureau of Global Health
Security and Diplomacy. Most of the money a central bureau manages is drawn on the Agency for
International Development HIV/AIDS Working Capital Fund, the appropriation that pays for the
centrally procured commodity supply chain.

The centrally managed money is published, and is published with a country code, in the files named
Multiple Countries. The Department of State publishes three such files holding 99.9 megabytes in
all and the US Agency for International Development publishes 34. The first 6.3 megabytes of the
Department of State's first Multiple Countries file carry 39.45 million of Nigeria FY2026 HIV
disbursements, of which 38.66 million is drawn on the HIV/AIDS Working Capital Fund, and all of
which belongs to a single activity, Global Health Supply Chain - Procurement and Supply
Management, award AID-OAA-TO-15-00007. Adding that 39.45 million to the country file's 46.32
million reaches 85.77 million of the API's 115.13 million out of 6.3 of the 99.9 megabytes the
three files hold. The two files named Worldwide, by contrast, carry no country attribution at all,
because every one of the 13,723 transactions in Worldwide-2 that names a recipient country names
code 998, countries unspecified.

Read in full, the Department of State reconciles to the cent. Adding the Department of State's
three Multiple Countries files to the Department of State's Nigeria country file, and applying the
HIV test to each transaction separately, reproduces the API in every year the S3 files cover.
Nigeria HIV disbursements in millions, S3 files and API alike, FY2012 0.624, FY2013 0.625, FY2014
0.778, FY2015 0.552, FY2016 0.762, FY2017 1.078, FY2018 1.108, FY2021 0.251, FY2022 0.141, FY2023
0.138, FY2024 0.172, FY2025 23.096 and FY2026 115.128. No year differs by a cent. FY2019 and
FY2020 hold no Department of State Nigeria HIV disbursement in either source.

Closing the last 9.016 million of FY2026 needed two corrections to the reading rule. The HIV test
has to be applied to each transaction and not to the activity holding the transaction, because one
award can carry Malaria-coded and HIV-coded transactions side by side. Award AID-OAA-TO-15-00009,
the Malaria task order of the same Global Health Supply Chain contract as the award named above,
holds 11 Nigeria disbursements across FY2025 and FY2026 worth 35.09 million, of which the two
dated 1 October 2025 and 1 February 2026 carry DAC purpose code 13040 and sum to 9,016,197
dollars, which is exactly what the API attributes to HIV for that award. The other nine
transactions carry Malaria control, code 12262. All 11 transactions carry the USG sector narrative
Malaria, so the USG vocabulary alone never finds the money.

The second correction is the code the DAC test matches. ForeignAssistance.gov's `dac_sector_code`
134 is the site's own numbering, and every record carrying 134 carries DAC purpose code 13040,
whose own first three digits are 130. So a reader testing the IATI file's vocabulary-1 code for
the prefix 134 never matches a transaction, and the correct test is equality with 13040. The
failure was silent, because the USG vocabulary narrative HIV/AIDS carries almost every HIV
transaction unaided, and the error surfaced only in the 30 Nigeria rows of 2,478 that the API
counts as HIV under the DAC code while labelling them something else under the USG sector name.

**The general rule.
A sector test belongs on the transaction that carries the money, not on the activity that holds
the transaction. A code drawn from one publisher's numbering cannot be matched by prefix against
another publisher's file. Check both by reproducing a figure the publisher states, because a test
that never fires returns a well-formed series that is short.**

The US Agency for International Development, the agency holding 54 per cent of the US HIV money in
Nigeria, reconciles from FY2019 onward and not before. Adding the agency's 34 Multiple Countries
files, 1,250.7 megabytes, to the agency's Nigeria country file reproduces the API within 173
dollars in every year from FY2020 to FY2024. Nigeria HIV disbursements, files against API in
dollars, FY2020 145,508,188 against 145,508,302, FY2021 129,396,686 against 129,396,830, FY2022
100,411,324 against 100,411,496, FY2023 101,567,522 against 101,567,666, and FY2024 190,078,323
against 190,078,496. FY2019 runs 188,905 dollars above the API, three parts in a thousand. FY2013
to FY2018 fall between 11,570 and 4,044,658 dollars short of the API, and FY2012 and every earlier
year hold nothing at all in the files, against an API series that begins at 1,090,321 dollars in
FY2001. So the S3 route carries the US Agency for International Development back to FY2019 and the
ForeignAssistance.gov API carries the same agency back to FY2001, which is a difference of 18
years that no rebuild of the connector can recover.

Five transactions have to be removed before those figures appear, and the key that removes them
safely is the whole row. The US Agency for International Development publishes five FY2026 Nigeria
HIV disbursements twice inside one file, worth 15,851,027 dollars together, each repeat carrying
the same transaction reference, the same date, the same value and the same receiver as the
original, and the API counts each payment once. Removing repeats on the transaction reference
alone, however, destroys the Department of State's reconciliation, because the Department of State
attaches one transaction reference to genuinely different transactions and the API counts every
one of them. Deduplicating the Department of State on the transaction reference alone moves FY2012
from 623,717 dollars to 551,282 and FY2018 from 1,108,121 to 950,903, and breaks five further
years. Deduplicating on the whole row, meaning the activity identifier together with the
transaction reference, the date, the value and the receiver, restores all 13 Department of State
years to the cent and still removes the 15,851,027 dollars the US Agency for International
Development repeats.

**The general rule.
A row identifier a publisher attaches to a row is not necessarily unique inside that publisher's
own files, so a deduplication key built on the identifier alone can delete money the authority
counts. Test a deduplication key by reproducing a total the authority states, on every publisher,
before applying the key to any of them.**

From FY2025 the two agencies publish the same money, and the ForeignAssistance.gov API divides
each shared award between the two agencies and does not credit one of them. Award
72062020CA00001, the Heartland Alliance key populations award, appears in the API at FY2025 as two
separate activity records, the Department of State's activity 227505 at 977,134 dollars and the US
Agency for International Development's activity 215553 at 3,651,931, while the US Agency for
International Development's own file reports the combined 4,629,063 under a single activity, two
dollars below the sum of the API's two records. Summing the publishers therefore double counts.
At FY2025 the two publishers' files total 194,159,508 dollars against the API's 171,206,047, and
at FY2026 they total 230,060,569 against 114,932,594.

The subtraction that removes the double count is the Department of State's whole Nigeria HIV
total, taken away from the US Agency for International Development's, and applied only in a year
where the overlap is present. FY2025 gives 171,063,912 less 23,095,596, which is 147,968,316
against the API's 148,110,451, low by 142,135 dollars. FY2026 gives 114,932,535 less 115,128,034,
which is −195,499 against the API's −195,440, low by 59 dollars, and reproduces the sign of a
negative year as well as the size. The trigger has to be evidence of the overlap and not a date,
because before FY2025 the whole of the Department of State's Nigeria HIV money is one redacted
activity, US-GOV-11-47198, that the US Agency for International Development does not publish, so
subtracting in those years would delete money that belongs to the Department of State. The
evidence that fires the trigger is a Department of State activity whose award number the US Agency
for International Development also publishes in the same fiscal year, which happens in FY2025 and
FY2026 and in no earlier year.

Matching the two agencies award by award, which would be the exact operation, cannot be done from
the IATI files alone, because two Department of State activities hide the award number the API
knows. Activity 227085 is award AID-OAA-TO-15-00004 in the API, worth 668,384 dollars at FY2025
and 17,909,684 at FY2026, and activity 227702 is award 7200AA19CA00003, worth −36,348 at FY2026,
and the Department of State's IATI identifiers for both carry the activity number alone with the
award number redacted. Matching award by award therefore leaves 668,934 dollars unsubtracted at
FY2025 and 17,873,277 at FY2026, which is far worse than subtracting the whole total. The
142,135 dollars the whole-total subtraction removes wrongly at FY2025 are the Department of
State's own small grants, 16 PEPFAR FY24 Small Grants worth 141,947 dollars together and one line
of 738, and even that account is 550 dollars out, which is the same order as the 114 to 173 dollar
differences the API shows in the years where nothing is in dispute.

**The general rule.
Where two publishers report one award, the authority may divide the award between them instead of
crediting either, so the operation that reconciles a publisher to the authority is a subtraction and
not a choice of figure. Trigger the subtraction on evidence that the overlap is present in that
year, because a rule applied to every year deletes money in the years where the two publishers
report different awards.**

A transaction with no recipient country is regional money and the country filter is right to drop
it. The US Agency for International Development's Multiple Countries files hold 905 HIV
disbursements worth 101.245 million dollars that name no recipient country at either the activity
or the transaction level, and every one of them names a recipient region instead, 511 under code
289 south of Sahara regional, 356 under code 998 countries unspecified, 19 under 789, 11 under 380
and eight under 619. No country panel can carry that money, and the API does not carry it under
Nigeria either. The country file and the Multiple Countries files do not overlap, so adding them
is safe, and across Nigeria HIV disbursements the two sets share no transaction reference and no
activity identifier, 204 identifiers in the country file against 77 in the Multiple Countries
files.

So a connector reading only the country files understates every agency except Health and Human
Services, and a connector reading every file reaches the API's figure. The corpus is far larger
than the three publishers first surveyed. The IATI Registry lists 2,116 publishers, of which 197
give their country as the United States and 21 carry an identifier beginning `US-GOV`. The four
largest are the US Agency for International Development with 208 files, the Department of State
with 207, the Department of Defense with 180 and the Department of Agriculture with 155. The
Department of Defense matters for HIV, because the API credits the department with between 1.78
and 15.20 million a year of Nigeria HIV disbursements from FY2005 to FY2023.

Measured and not estimated, the seven publishers sized on this pass hold 2,590.3 megabytes over
848 files, and adding the Millennium Challenge Corporation's 101.4 megabytes over 54 files, sized
by GET on 27 September 2026, gives 2,691.7 megabytes over 902 files for all eight publishers that
carry HIV money. Asking the host for each file's length without downloading the body gives the US Agency
for International Development 1,891.1 megabytes over 208 files, the Department of State 448.2 over
207, the Peace Corps 83.0 over 70, the Department of Defense 77.0 over 181 with one file failing to
answer, Health and Human Services 63.2 over 72, the African Development Foundation 24.3 over 48 and
the Department of Labor 3.5 over 62. The Millennium Challenge Corporation's 54 files answered none
of the 54 length requests, for the reason given below, so the 2.59 gigabytes excludes that
publisher, which the 27 September 2026 pass closed. Two thirds of the largest publisher's bytes are the files the reconciliation
showed the panel cannot do without. The US Agency for International Development's 208 files divide
into 157 country files worth 529.4 megabytes, 34 Multiple Countries files worth 1,250.7 megabytes,
12 region-coded files worth 23.8, two region-named files worth 0.1, two Worldwide files worth 72.6
and one organisation file worth 14.5. So the central bureau money is the bulk of the download and
cannot be trimmed away, and skipping the Worldwide files saves 72.6 of 1,891.1 megabytes, which is
four per cent.

A registry package title does not classify a file and the S3 filename does. The US Agency for
International Development registers country files under two-letter codes, `usaid-ng` for Nigeria,
and registers Multiple Countries files under three spellings, `usaid-multiple-1`,
`usaid-multiple-countries-16` and `usaid-multiplecountries33`. Eight more carry a bare number,
`usaid-19` through `usaid-29`, which reads as a region code beside the genuine region codes
`usaid-89` and `usaid-289` and is not one, because `usaid-19` is served as
`iati-activities-Multiple+Countries-19.xml`. Those eight hold 296.2 megabytes, so a reader that
classifies by title loses a quarter of the Multiple Countries bytes and believes it has read a
region. The Department of State, Health and Human Services and the Department of Defense instead
register country files under country names, `state-afghanistan`, with one of the Department of
State's 207 breaking that pattern as `dos-grenada`, and they name the unusable files
`state-worldwide-1` where the US Agency for International Development names the same thing
`usaid-998-1`.

**The general rule.
Classify a published file by the name the file is served under, not by the name the catalogue
entry carries. A catalogue title is written by hand, varies within one publisher, and can make one
kind of file look like another.**

Not every US publisher is on Amazon S3, and a publisher that looks wholly unreachable may be
refusing one HTTP method. The Millennium Challenge Corporation's 54 files sit on
`inventory.data.gov`, which answers every one of them 403 Forbidden to a HEAD request and 200 with
the file to a GET, so a sizing pass built on HEAD reports the publisher as entirely closed when
the publisher is entirely open. The three files probed came back as `text/xml` at 969,181, 36,990
and 1,345,456 bytes. The same domain's catalogue API, at `catalog.data.gov`, answers 404 to both
documented paths, so data.gov serves the files while refusing to list them.

**The general rule.
A host refusing HEAD has not refused the file. Before recording a publisher as unreachable, retry
with GET, because a method-level refusal and a source-level refusal look identical in a failure
count.**

The same award reaches the panel twice from FY2025. The Department of State and the US Agency for
International Development both report the Nigeria bilateral awards from FY2025 onwards, under
different IATI identifiers built on the same award number. For FY2026 the Department of State
reports six activities worth 46.32 million and the US Agency for International Development reports
the same six award numbers worth 46.52 million, with the titles rewritten, so that KP-CARE 1
Activity under the Department of State is Key Populations Care 1 under the US Agency for
International Development. Deduplication cannot key on the IATI identifier and has to key on the
award number inside the identifier. Where the two agencies report one award at two amounts, as the
two agencies do throughout FY2025, a rule is needed to choose between the two figures.

The rule is a subtraction, not a choice, and the arithmetic is visible in the API. Award
72062020CA00001, the Heartland Alliance key populations award in Nigeria, is reported by the US
Agency for International Development from March 2020 and by the Department of State from July
2025. The two copies share not one transaction identifier, and the two publishers even write dates
differently, the US Agency for International Development using quarter ends and the Department of
State using the first of the month. Nigeria HIV disbursements on that award, IATI file first and
API second, run 7,180,925 against 7,180,926 at FY2020, 8,083,628 against 8,083,629 at FY2021,
12,003,217 against 12,003,222 at FY2022, 12,013,819 against 12,013,821 at FY2023 and 7,522,939
against 7,522,944 at FY2024, all of it the US Agency for International Development alone. FY2025
gives the Department of State 977,134 in both sources and the US Agency for International
Development 4,629,063 in the file against 3,651,931 in the API. FY2026 gives the Department of
State 4,726,591 in both sources and the US Agency for International Development 4,726,587 in the
file against nothing at all in the API.

Taking the Department of State's figure away from the US Agency for International Development's,
for the same award, country and fiscal year, reproduces the API in every year. FY2025 gives
4,629,063 less 977,134, which is 3,651,929 against the API's 3,651,931, and FY2026 gives 4,726,587
less 4,726,591, which is four dollars below zero against the API's nothing. The few dollars left
over are rounding inside the file's own values. So the Department of State did not restate the
award, the Department of State took over reporting it, and the US Agency for International
Development's file still carries the months the Department of State now reports.

**The general rule.
Where two publishers report one award, test whether the second publisher's series is the first
publisher's series or the remainder of it. A duplicate that has to be dropped and an overlap that
has to be taken away look the same in a yearly total and differ in every transaction.**

The S3 route reaches back further for some agencies than for others, and how far back depends on
which of an agency's files are read. Nigeria HIV disbursements run in the US Agency for
International Development's country file from FY2013 to FY2026 without a gap, in the Health and
Human Services country file for FY2018 and FY2019 in token amounts and then FY2021 to FY2025, and
in the Department of State's country file from FY2021 to FY2026. Adding the Department of State's
three Multiple Countries files carries the Department of State back to FY2012, eight years earlier
than the country file alone. Whether the Multiple Countries files carry the US Agency for
International Development and Health and Human Services back in the same way was not measured.
The API carries the whole-of-government Nigeria HIV series from FY2001, rising from 1.09 million
at FY2001 to 249.47 million at FY2008, so the S3 files cannot supply the first decade of PEPFAR
however many of the files are downloaded.

**The general rule.
A publisher refusing one address has not refused the data. Before recording a source as closed to
machine clients, look for the same publisher's other outlets, and treat the IATI Registry as a
directory of file addresses for any government donor. An access claim naming a site is a claim
about the site, not about the data.**

Read from a browser, the API describes itself well. Each transaction carries 51 fields, including
`country_code` already in ISO3 form, the managing agency and sub-agency acronyms, the DAC sector
code and purpose name, the USG sector and category names, the transaction type, the fiscal year
and both a current and a constant amount. `page_info` carries `total_records` and `total_pages`.
Two documented behaviours are wrong. Every filter is documented as an array, and a repeated
parameter keeps the last value and discards the first, `country_code=NGA&country_code=KEN`
returning Kenya alone, while a comma list matches nothing. `per_page` is documented with a maximum
of 10,000 and is capped at 1,000.

**The general rule.
A filter documented as an array has to be tested with two values before a connector relies on it. A
query that silently answers on one of the two values returns a well-formed page and a wrong
total.**

The connector's HIV test, which admits a row when any of four columns names HIV, reproduces on the
API as the union of two queries, because one USG sector name of the 51 in use contains HIV and one
DAC sector does, code 134, and no USG category name does. The two queries disagree in both
directions, so neither alone is the panel's series. For FY2024 disbursements the USG query holds
2,564 rows and 10,223.6m, the DAC query holds 2,620 rows and 10,265.2m, 75 rows worth 62.3m carry
the USG HIV label without DAC 134 and many of those carry a COVID-19 control purpose, and 131 rows
worth 103.9m carry DAC 134 under a USG label of Malaria, Tuberculosis, Maternal and Child Health or
Direct Administrative Costs. The union is 2,695 rows.

One code in the country column is not a country. `WLD`, standing for World, holds 6,625.4m of the
FY2024 union total of 10,327.5m, and the connector drops the code because the name resolves to no
ISO3 code. The FY2026 total over all codes including World is 2,093.0m, which sits beside the
2,162m §9x records IATI holding for FY2026. So the gap §9x reported between IATI and
ForeignAssistance.gov for FY2026 was the July snapshot the panel holds and the country-only
reading, and not a disagreement between the two publishers, which strengthens the §9f judgement
that US IATI republishes ForeignAssistance.gov.

Against the July download the panel holds, the data of 31 August 2026 is higher everywhere.
Countries only, current dollars, millions, the API first and the connector's docstring second.
FY2024 3,702.1 against 3,659.4, FY2025 3,117.9 against 3,084.6, FY2026 1,012.3 against 613. FY2025
by agency, USAID 1,402.0 against 1,379.2, CDC 1,364.5 against 1,356.8, State 273.2 against 270.7,
other agencies 78.3 against 77.9. FY2026 is almost all State, 999.7 of the 1,012.3, with USAID at
2.0 and CDC at zero. Whether the differences of about one per cent at FY2024 and FY2025 are a
restatement between the July and August releases or a difference between the two-query rule and the
four-column rule was not settled, because settling it means scanning the July file, which Jason
moved out of `data/raw/foreign_assistance/` on 21 September 2026.

---

### §9ab. A rule can empty a publisher, a numeric code can belong to a published list, an accumulator can assert a measurement nobody made, a paged read can return a different subset every run, a table can be apportioned before the connector ever sees the table, a coverage finding can describe the connector instead of the publisher, a key can describe a different population than the value standing beside the key, and a joined query can serve one activity once per joined row while the reader counts every copy

*Written 30 September 2026, from the seven defects the IATI connector produced between 28 and 30
September 2026. Five of the seven were found after the connector had been written, dry-run,
approved, run and verified, and five of the seven wrote a wrong number into the panel without
raising anything. The sixth defect, the joined query counting one activity more than once, is
recorded in the claims table and in the closing lesson of this section. The seventh was found
inside the repair of the seventh row of the claims table below, when the repaired sector keys were
read back off the file the repaired run had written and stood a cent from the value, and the
seventh is recorded in that same row. All seven are now repaired in the code. Jason rebuilt the
panel on 30 September 2026, so `data/panel/hiv_panel.csv` carries the first six repairs, and the
seventh moves no money and waits for whatever run happens next for another reason. The copies at
`site/dist/downloads/` are the site build of 7 September 2026, which holds 177,594 rows from 18
sources and no `iati` row at all, so none of the seven defects has ever reached a reader of the
download page. Every figure the three repairs Jason reran were predicted to move moved by the
predicted amount to the penny, which is recorded in the claims rows below.*

*An eighth defect was found later on 30 September 2026, repaired on 1 October 2026 and is now in
the panel. A transaction stating no currency at any level the IATI standard provides used to be
written into the panel as US dollars, which decided 48 rows carrying 13,629,785.48 USD as the old
panel wrote those amounts one for one, among them 63.1 per cent of the money the Ministry for
Foreign Affairs of Finland holds in the panel. The connector now reads a currency down a four-rung
ladder and refuses the amount where no rung answers. A ninth defect was found on 1 October 2026 and
repaired the same day, being the reason the panel stated beside a missing Global Fund value, which
denied an H or C grant that the same row names on 10 of 192 rows. Jason ran `iati` at 18:09 on 1
October 2026 and the panel on disk carries both repairs, and item 30 and item 31 of RESUME.md hold
the measurements, the builds and the run records. A tenth and an eleventh defect were found on 1
October 2026 and both were repaired the same day, being a country-year the Global Fund reached by
reimbursement alone, which the connector used to drop with no row and no log line and now writes
with no value, a stated reason and a boolean key, and a publisher's reimbursement, which the
connector used to sum in whatever currency the publisher wrote and log as US dollars and now
accumulates under the currency the file states and logs one figure per currency. Neither repair
moves a figure in the panel. The eleventh needed no run and is closed. The tenth added rows to the
Global Fund series, and Jason ran `iati` a second time at 19:07 on 1 October 2026, which measured
the population at 54 country-years over 33 countries from 2007 to 2025, raised the Global Fund
series from 2,577 rows to 2,631 and left the 2,385 valued rows untouched, so both defects are now
closed. Both sit in the claims table below with the build and the run recorded on the row, and
item 37 and item 38 of RESUME.md hold the build records and the verification.*

**A de-duplication rule removed an entire publisher, and the rule looked correct on the case that
motivated the rule.** The connector's rule 17(g) excludes any activity naming the Global Fund or a
United States government agency as a role-1 funder, so that money already counted once under the
Global Fund's own series does not enter the panel a second time through a body spending the money
on the Global Fund's behalf. The rule does exactly that on the UN Development Programme, which
names the Global Fund alone on 63 of the 73 activities the rule excluded. The rule also removed the
UNAIDS Secretariat completely. The UNAIDS Secretariat filed 1,228 activities under purpose 13040,
every one of the 1,228 names 42 role-1 funders at once, and the United States is always among the
42, so the whole of UNAIDS's multi-donor core money left the panel because one of 42 contributors
is an excluded funder. Measuring the rule across every publisher found 2,140 activities excluded
and only 109 of the 2,140 naming an excluded funder alone. The rule was narrowed to exclude only
where every named role-1 funder is an excluded funder, and an activity kept under the narrower rule
carries three keys naming the pass-through funder and the money standing behind that funder, so a
reader can remove the kept money without a rerun. The narrower rule kept 2,005 activities, being
the World Health Organization 517, UNAIDS 1,228, UNICEF 250 and the UN Development Programme 10.

**The general rule.
A rule that removes records has to be measured against the publishers the rule will empty, and not
only against the case the rule was written for. Count and name what a rule removes before trusting
what the rule keeps, because a rule that deletes one publisher entirely leaves no trace in a row
count that nobody compared against the publisher's own filing.**

**A publisher's odd numeric codes turned out to be a published codelist, and looking for the list
first changed what the repair had to be.** The Swiss Agency for Development and Cooperation files
numeric recipient codes where the IATI standard requires an ISO 3166-1 alpha-2 code, and the
connector refused all eight codes and logged the money against each. The obvious repair was a
connector-local alias table justified by the French narrative sitting beside each code in the
cached file. Checking first whether the eight numbers belong to a published list showed that all
eight match the OECD DAC recipient codelist exactly, French labels included, five being countries
and three being regional or unspecified codes. So the table went into the connector as DAC
recipient codes with a citable source, the three regional codes now reach the region pool instead
of being refused, and a reader can check every entry against the codelist. A table justified by
the connector's own reading of a French narrative could not have been checked that way. The table
is keyed on the exact code string and never on the narrative, because resolving a country by name
is what once made the United Kingdom the largest recipient of American HIV aid.

**The general rule.
Before writing a private alias table for a publisher's unexpected codes, look for the published
list the codes come from. A mapping that cites a codelist can be audited by a reader, and a mapping
justified by the connector author's reading of a label cannot.**

**An accumulator with a default of zero turned the absence of a measurement into a measurement of
zero, across 424 country-years.** The Global Fund totals live in a `defaultdict(float)`, and the
branch for a grant that is not an HIV or HIV-and-tuberculosis grant adds that grant's purpose-13040
share, which is zero when the grant carries no purpose-13040 money. So a country-year in which the
Global Fund moved only malaria or tuberculosis money created a key in the accumulator and was
written into the panel as a row of value zero. A zero in a disbursement series is a statement that
the funder disbursed nothing. For Zimbabwe in 2019 the statement is false, because the OECD Creditor
Reporting System records 122,147,155 USD for that country-year and the connector had simply seen no
HIV-coded Global Fund transaction. The run carrying the defect wrote 424 such rows out of 2,148, and
OECD CRS reports 5,097,904,760 USD against 265 of the 424. The repair separates a country-year the
connector measured from a country-year the connector only saw, and writes the second with no value,
a stated reason and the grant identifiers seen. Dropping those rows instead would have removed 424
country-years and emptied the Global Fund series for nine countries, which hides a funder's presence
in a country rather than reporting a year the connector could not measure.

**The general rule.
A default of zero inside an accumulator converts every absence into a measured zero, silently and
at the moment the key is created. A series has to distinguish a measured zero from an unmeasured
country-year, and the panel's own convention of keeping the row with no value says which one the
reader is looking at.**

**A paged read of a query service returned a different subset of the same result on every run, and
the symptom was a figure that moved between two runs of unchanged code.** The connector paged
d-portal's query service on `limit` and `offset` and asked for no ordering. A relational engine
given no ORDER BY may return rows in any order, and in a different order on two executions of the
same statement, so `LIMIT n OFFSET n` is not guaranteed to continue where `LIMIT n OFFSET 0`
stopped. Two identical requests for 20,000 rows returned 20,000 rows each of which 14,680 differed.
Across two runs of identical code the Global Fund series moved by 1,387,699,426 USD, 101
country-years gained money naming grants the previous run never returned, 224 country-years lost
money, and Rwanda lost every row. The comment in the connector recorded 20,000 as a measured
per-page cap on the service. That figure was wrong, and nothing was capping the response at 20,000
except the connector asking for 20,000. A limit of 200,000 was honoured and answered in 6.3
seconds, and the largest query the connector sends, 326,852 rows, came back complete in about 40
seconds. The repair is one request per query, with a raise when the returned count equals the limit,
because a count equal to the limit is the one case where a single request loses rows without saying
so. The publisher census was being shuffled as well, at 23,327 rows against a page of 20,000, so
every run so far had chosen the connector's list of HIV publishers from a reshuffled result.

**The general rule.
A paged read that requests no ordering is not a read of the whole result, and the defect announces
itself as a figure that changes between two runs of unchanged code rather than as an error. Run the
same code twice against the same source and compare the output row by row, because no single run
and no schema check finds this class of defect.**

**The diagnosis was only possible because the service echoes the SQL the service built.** d-portal
returns a `dquery` field carrying the statement the parameters produced. The service silently drops
`groupby`, every aggregate function, `order_by`, `order`, `sort`, `sortby`, `trans_day_min`,
`trans_day_max`, `year` and `trans_year`, and honours `orderby` on that one spelling alone. A
dropped parameter changes neither the row count nor the response's error field, so a connector that
trusted `groupby` would have received ungrouped rows and summed the same money twice, and a
connector that partitioned on `trans_year` would have read the whole corpus into every partition.
The echoed statement is the only oracle that can tell an honoured parameter from an accepted and
ignored one.

**The general rule.
When a service accepts a parameter without honouring the parameter, the row count cannot detect the
loss, so the only oracle is whatever the service says about the query the service built. Record for
each parameter whether the parameter was verified honoured or verified dropped, and name the
evidence, because the next connector author will otherwise read the same documentation and make the
same assumption.**

**A table turned out to be apportioned before the connector ever saw the table, and two plausible
explanations of the same row counts were both wrong.** d-portal's `trans` table holds one row per
transaction per sector row the activity declares, each row carrying the transaction's value times
that sector's percentage, so `trans_usd` is a sector's share of a transaction and never a
transaction. The connector stored each row as `groups[(aid, trans_id)][sector] = usd`, which is the
right structure for apportioned data and the wrong operator, because an activity may declare the
same sector code twice at two different percentages and then one share overwrites the other.
`47045-MWI-C-MOH-2` declares purpose 12263 at 4 per cent, 12110 at 7 per cent, 12110 again at 1 per
cent and 13040 at 88 per cent, and 7 divided by 1 is the ratio of exactly seven that appeared on
every repeated key of that grant. Changing the assignment to an accumulation raises the Global Fund
HIV series by 3,139,231,583 USD, being 8.97 per cent, and the rise is exactly zero for every year
from 2002 to 2016 and grows from 0.3 per cent in 2017 to 26.1 per cent in 2023, because the Global
Fund changed how the Global Fund codes grant sectors in 2018. So the defect manufactured a false
downward step at 2018 in the very series the panel exists to measure.

The rerun of 30 September 2026 wrote the predicted figure in every year to the dollar, from
2,056,044,820 USD for 2017 to 764,307,152 USD for 2026, and the panel's own step down from 2017 to
2018 fell from 28.4 per cent to 20.2 per cent. The figure of 8.97 per cent nevertheless describes
only part of what the rerun changed, because 8.97 per cent compares two ways of aggregating one
complete read while the panel being replaced also carried the paged read described above, and the
panel's Global Fund series rose 81.1 per cent in all. Two defects repaired in one change give one
observed difference, and separating the two defects needs a prediction that holds for one of the two
alone, which the exact per-year match supplied.

Two explanations were proposed and falsified before the sector table gave the answer. The first
said the repeated rows were a join fanning the result out, which failed because `from=trans` and
`from=trans,act` both return 326,852 rows, so the repeats live in the `trans` table itself. The
second said d-portal holds each transaction both whole and apportioned, which failed because the
largest row on a transaction equals the sum of the other rows on only 1.0 per cent of transactions,
so no row carries a whole transaction. Row counts, ratios and totals could not separate the three
explanations. Reading the publisher's declared sector percentages from d-portal's own `sector`
table separated the three in one query.

**The general rule.
Before summing a column, establish what one row of the table is, from the source's own metadata
rather than from the shape of the numbers. Row counts, ratios and totals cannot tell an apportioned
table from a transaction table, and a connector that guesses wrong produces a total that looks
plausible and is wrong by a quarter in the years that matter most.**

**A mechanism confirmed on three examples is a hypothesis, and the corpus is what decides.** The
ratio of exactly seven held on three consecutive transactions of one grant, which is suggestive and
proves nothing about the other 113,774 transactions. Three checks across the whole corpus settled
the repair. All 2,726 Global Fund activities declare sector percentages summing to exactly 100
across 4,721 declared rows, so adding a transaction's shares reaches the transaction and does not
overshoot. All 113,777 transactions return exactly as many rows as the transaction's activity
declares sector rows, with none surplus and none short, so no returned row is a duplicate and adding
the rows cannot double count. On 113,774 of 113,774 transactions the percentages recovered from the
shares match the declared percentages. Because the repaired series now depends on the first two
facts, and because d-portal documents neither, the connector tests both on every run and logs what
the test found, warning without stopping.

**The general rule.
When a repair rests on a property of the source that the source does not document or promise, test
the property on every run and log the result. A measurement that held on the day of the diagnosis
is evidence about that day, and a connector that will run again needs the check in the code rather
than in a probe script nobody will run twice.**

**A finding about a publisher's coverage was a finding about the connector, and three probes did not
catch the mistake.** Comparing the panel's two readings of the same Global Fund money gave a ratio
of the IATI reading to the OECD Creditor Reporting System reading of 0.831 for 2003 to 2010, 0.761
for 2011 to 2017 and 0.598 for 2018 to 2026, which read as a coverage collapse in what d-portal
returns, worsening steadily over time. The reading survived the falsification of two rival
explanations and was nearly written into the project's documentation as a limitation of the source.
Recomputed after the paging repair and the apportionment repair, the same three ratios are 1.009,
1.073 and 1.013, and the share of paired country-years agreeing within two per cent rose from 81, 50
and three per cent to 91, 76 and 87 per cent. Ethiopia's median ratio moved from 0.037 to 1.000,
Mozambique's from 0.186 to 1.000, South Africa's from 0.385 to 1.000 and Uganda's from 0.230 to
1.000. Nothing about d-portal or about the Global Fund's publication had changed.

**The general rule.
A comparison of two sources measures the code reading each source as well as the two sources, so no
limitation may be written about a publisher while any known defect in the reading code is
unrepaired. A worsening trend in such a comparison is evidence of a defect before it is evidence
about the publisher, because a defect in a connector is free to grow over time with the source's own
changing practice, as the Global Fund's sector-coding change of 2018 made this one grow.**

**A key stamped beside a value described a different population than the value.** The Global Fund
rows carry `extra.sector_13040_usd`, `extra.sector_12110_usd` and `extra.sector_12263_usd`, which a
reader would use to strip tuberculosis-coded money out of the HIV series, while the row's value
holds HIV and HIV-and-tuberculosis grants whole plus only the purpose-13040 share of every other
grant. The three accumulators run before the grant-letter test at
`hivimpact/connectors/iati.py:845`, so the keys describe every grant the connector saw and the value
does not. Across the series the keys sum to 53,953,975,658 USD against a value total of
38,152,946,330 USD. On the 480 rows where every named grant is an HIV or HIV-and-tuberculosis grant
the keys sum to the value exactly, 4,450,872,871 USD both, and no row anywhere carries keys summing
below the value. On the 1,905 rows naming at least one other grant the keys exceed the value by
15,801,029,329 USD, and the 192 rows carrying no value at all carry 352,219,073 USD of purpose 12263
and 48,548,052 USD of purpose 12110 beside the absent value.

**The general rule.
Test a key offered as a decomposition of a value on the rows where the key and the value are built
from different populations, and not on the rows where the two populations coincide. A key that agrees
with its value exactly on the homogeneous subset looks correct on every row a spot check is likely to
reach, and the disagreement lives in the rows a spot check is least likely to choose.**

**A query joining two tables served one activity once per joined row, and the reader summed every
copy.** The connector's XML reader asks d-portal for `from=act,sector` with `sector_code=13040`,
which joins the activity table to the sector table, so an activity declaring purpose code 13040
twice under vocabulary 1 arrives as two complete activity elements. Pass one of the reader assigns
each identifier's fingerprint set and survives a repeat. Pass two tests whether the identifier is
known and not whether the identifier has already been summed, so the activity's transactions are
added once per copy. Across the 85 cached publisher directories, 11,698 activity elements hold 71
surplus copies in three publishers, and the number of copies equals the activity's count of
vocabulary-1 13040 sector elements for 905 of UNICEF's 905 activities, 235 of `GB-CHC-285776`'s 236
and 217 of `AU-5`'s 250. Two of the three publishers reach the panel. Cambodia's bilateral row is
overstated by between 10.1 and 33.2 per cent in nine years, where the whole Australian contribution
is exactly twice the truth, and Kenya's multilateral row is overstated by 1.0 per cent in 2012, by
less in 2014 and 2015, and understated by 0.5 per cent in 2019, because the doubled transaction in
2019 is a negative expenditure. The surplus is about 3,752,076 USD against a series total of
38,152,946,330 USD, so the aggregate moves by about 0.01 per cent while nine country-years move by a
fifth to a third.

**The general rule.
A `limit` and an `offset` sent to a joined query count joined rows and not the entities the reader
believes it is counting, so a reader walking such a result must deduplicate on the entity's own
identifier and must say in its log how many copies it skipped. Two further habits follow. A
duplicate found inside a single response falsifies an unstable-paging explanation immediately,
because no reordering across pages can place two copies side by side in one response, so the
position of a duplicate is worth establishing before its cause is written down. And an aggregate
that moves by a hundredth of a per cent can still double a named country's series for a decade,
so the size of a defect has to be stated per cell as well as per series.**

---

### §9ad. A publisher can retire one aggregate indicator while publishing every disaggregation of the same measure, three publishers can lack the same measure in the same years, a coverage field can mean national within the reporting unit and not a sovereign state, and a drop counter can name a cause the code never tested

*Written 1 October 2026, from the probe that settled why the panel holds no 2025 HIV testing
result from the Global Fund. The Global Fund's 2025 annual results reached the panel for the first
time on 1 October 2026, and `hiv_tests_performed` was absent from the 2025 rows while every other
Global Fund HIV series reported 2025 at about the 2024 level. Five causes could produce the same
silence, being no row published at all, a row published at a coverage the connector declines, the
series renamed, a row published with an empty value, and the row lost inside this project's own
code. Jason ran one read-only request to the service on 1 October 2026, saved all 17,538
`Annual_Results` rows under `data/raw/global_fund/results_probe_20261001/`, and the saved rows then
answered the question offline together with three more that the connector's logs could not.*

**No 2025 HIV testing row exists at any coverage, so the silence is the publisher's.**
`Total number of HIV tests` carries 795 rows in the service, being 527 at National coverage, 243 at
Subnational coverage and 25 carrying no coverage value at all. Counting National rows the series
runs 54, 62, 68, 67, 69, 69, 72 and 66 over the eight years 2017 to 2024 and zero in 2025, and no
2025 row exists at Subnational coverage or with the coverage field empty either. Across the whole
dataset 2025 holds 2,225 rows against 2024's 2,239, so 2025 is a fully reported year for everything
except HIV testing. Exactly one name appears in 2025 that does not appear in 2024, being `TB
patients with DST result for at least Rifampicin` at 15 National rows, which measures tuberculosis
drug-susceptibility testing and could not carry a 66-country HIV series in any case, so the series
was not renamed. The volume the panel loses is 41,041,341 tests over 66 reporting countries in
2024, against 48,238,125 in 2023 and 48,525,192 in 2022.

**The disaggregations of the same measure all continue into 2025, which is what rules out a fall in
testing.** Counting National rows for 2024 and then 2025, the Global Fund's key-population HIV
testing counts run drug users 31 then 32, men who have sex with men 56 then 54, sex workers 55 then
52, transgender people 36 then 34, adolescents and youth 4 then 5, other vulnerable populations 11
then 15, and prisoners 21 then 21. Two further testing series grow, being `Individual HIV self-test
kits distributed` at 8 then 12 and `People on ART with viral load test result` at 25 then 33.
Treatment reporting is untouched, with `People on antiretroviral therapy for HIV` at 96 countries
in both years. A country that had stopped testing for HIV would not go on reporting how many sex
workers and prisoners were tested, so the Global Fund retired one aggregate indicator from the 2025
reporting year and the quantity the indicator measured did not fall to zero. The retirement is a
fact in the data. Why the Global Fund retired the indicator is not in the data, and is not asserted
here.

**Three publishers lack recent HIV testing volume while publishing treatment counts for the same
years, so the pattern belongs to the measure and not to one publisher.** The Global Fund ends
`hiv_tests_performed` after 2024. WHO's Global Health Observatory holds `hiv_tests_performed` for
129 countries in 2024 and nothing after, and `hiv_test_positivity_pct` for 127 countries in 2024
and nothing after, while reaching 2025 across 10 of the 12 series WHO's Global Health Observatory
contributes to the panel. UNAIDS AIDSinfo holds interior gaps in the same two measures, with 92 and
90 countries in 2019, nothing in 2020 and 2021, and 92 again in 2022. Any statement this project
makes about recent HIV testing volume therefore has to name the end year of each publisher's
series, and no year-to-year comparison of testing volume should cross 2024.

**A second Global Fund testing series is degrading without stopping, and no stopped-series warning
will ever fire for it.** `Number of HIV positive tests`, which the panel maps to `new_diagnoses`,
holds 22 National rows in 2023, 8 in 2024 and 2 in 2025. A reader trending `new_diagnoses` from the
Global Fund to 2025 would be reading two countries as though reading the programme. A series that
thins to a handful of reporters is as misleading as a series that stops, and is harder to see,
because the series goes on producing a number.

**The Global Fund's coverage field means national within the reporting unit and does not mean a
sovereign state.** Zanzibar is published under code `QNB` with `geographicCoverage` set to
`National`, while the service's own Geographies lookup grades Zanzibar `Subnational`. Zanzibar
accounts for one National testing row in each of the eight years the series runs, which is why the
service's National row counts stand exactly one above the panel's reporting-country counts in every
year, being 54 against 53, 62 against 61, 68 against 67, 67 against 66, 69 against 68, 69 against
68, 72 against 71 and 66 against 65. The connector declines all eight rows correctly, and the
guarantee that a panel row is a country comes from the `level == "Country"` filter on the
Geographies lookup and not from the coverage test on the result row. A connector that tested
coverage alone would have placed Zanzibar's results under a country code.

**Two of the three drop counters in the Global Fund connector name causes the code never tested.**
Replaying every exit from `fetch()` over the 17,538 saved rows accounts for every row, being 8,294
dropped for a name the connector does not map, 2,328 dropped for a coverage other than National,
127 dropped for a geography that is not a country, and 6,789 emitted. The behaviour is right at
every exit and two of the labels are wrong. Of the 2,328 rows the log calls subnational, 2,168
state `Subnational` and 160 state no coverage at all, and a row stating no coverage is a different
fact from a row stating a coverage below the national level. Of the 127 rows the log calls
unresolved, all 127 resolve to a published geography and are declined because the geography is a
region or a subnational unit, being Zanzibar at 104 rows, the Caribbean at 13, Oceania at 7 and
Western Asia at 3. Calling a declined region unresolved reads as a lookup failure and sends a
reader looking for a broken identifier. Two further exits carry no counter at all, being an
unreadable year and an unreadable numerator, and both drop zero rows of the saved dataset, so each
is a latent defect and not an active one.

**The general rule.
A series that ends is not a quantity that ended, and the two are told apart inside the publisher's
own later data and not by argument. The test that settles the question is whether the publisher
still reports the disaggregations, the neighbours and the related measures for the year the series
is missing, because a publisher reporting 2025 for everything except one indicator has retired an
indicator, while a publisher reporting nothing for 2025 has not yet published. Three habits follow.
A connector that drops a row must keep a counter for every exit it has, must name the cause the
code actually tested, and must not fold two different causes into one word, because the counter is
the only instrument available when a publisher changes shape and a counter that says subnational
when the row said nothing at all will send the next reader to the wrong question. A field named for
a level of geography describes the level within whatever unit reported, so the entity a row belongs
to has to be established from the publisher's own entity list and never from a coverage label on
the row. And a series can mislead by thinning as well as by stopping, so a count of reporting
entities belongs beside every value a reader is invited to compare across years.**

---

### §9ae. A class swept across every country finds what a country swept one at a time misses, a cross-check that agrees can be proof of duplication instead of corroboration, the panel itself can exclude half a region before any host is probed, a published correction can fail to repair the defect it was recorded as repairing, a dashboard's own headline can disagree with every decomposition the same dashboard publishes, two endpoints of one source can both publish a stock the duplicate key cannot tell apart, and a required schema field can settle a decision the data cannot

*Written 1 October 2026, from two pieces of work. Jason asked whether another round of searching
was worth running before the West and Central African country connectors were written, on the
reading that two national connectors looked thin beside the region's aggregator coverage. The
round was run and the round changed the build list from nine countries to five. The second piece
is the Nigeria National Data Repository build itself, where the connector was written against
five saved payloads and every integrity check, refusal and gate was forced offline before the
connector was handed over.*

**A class swept across every country in a region finds what three rounds of country-by-country
sweeping missed.** The UNAIDS national AIDS spending assessment index holds reports for 14 of the
region's 24 countries. Three earlier rounds, each sweeping one country at a time, had recorded
three of the 14 and had recorded nothing at all about the other 11. Sweeping the whole class in
one pass and settling the class against the panel then showed that almost none of the 14 was
additive, because the GAM expenditure workbook already on disk holds 59,947 rows and matches the
panel country for country and year for year for 18 of the 24 countries across 817 panel rows.
Counting from 2019 the entire class adds six country-years, being Cameroon 2020 and 2021, DR Congo
2019 and 2020, and Togo 2022 and 2023. One country of the 24 is a build, Cameroon, which holds
zero GAM years and eight published assessment years, so for Cameroon alone an assessment report is
the only expenditure measurement anywhere in the pipeline. The lesson is about sweep order and not
about this region. Sweeping a country at a time hides the denominator, because the question "does
this country publish something" is answerable one country at a time while the question "does this
class add anything" is not.

**A cross-check that agreed to within 3 to 5 per cent was proof of duplication and not the
corroboration it was read as.** Two of the three reports an earlier round extracted by hand were
Benin 2024 and Ghana 2022, and the panel already held Benin 2018 to 2024 unbroken and Ghana 2014 to
2023 unbroken through the GAM workbook. Agreement between a hand extraction and a panel series is
evidence that the two are the same measurement whenever the provenance allows it, and the
provenance allowed it here, because a country's assessment report is what the country's GAM return
is built from. Benin left the build list on that finding. An agreement is only corroboration once
the two figures have been shown not to share an origin, and the showing has to come before the
comparison is read.

**The panel excluded half the region before any host was probed.** The panel holds 52,840 rows
carrying a sub-national unit across 55 countries, and in this region every one of those rows comes
from two PEPFAR connectors and from nothing else. Twelve of the 24 countries already have PEPFAR
coverage at that level, so a national statistics institute could only add sub-national measurement
for the other 12, and the class was probed for 12 hosts instead of 24. Asking what the panel
already holds is cheaper than asking what a publisher serves, and the question narrows the probe
list and not the findings.

**Reading one yearbook settles a build, where reading a catalogue page does not.** Guinea's
institute serves health statistics yearbooks for 2007 to 2022, and the 2018 edition is 88 pages of
extractable text with six pages carrying HIV content. Two tables carry the build, being TB and HIV
co-infection by health district with tested counts, positivity and share on treatment, and
antenatal counselling and testing by health district with women counselled, women accepting a
test, women tested, women testing positive, and partners tested and positive, where one district
reports 9,147 first antenatal visits against 93 women testing positive. Niger's 2019 edition is 208
pages with 37 mentioning HIV, and carries TB and HIV co-infection by district and region plus
something the pipeline holds nowhere else, being a per-district reporting completeness and
promptitude rate for the HIV care form itself, which measures how complete the underlying HIV
reporting is.

**A planning document published once every five years is not a repeating structured series.** The
Gambia's bureau of statistics publishes no health statistics yearbook, and the only district HIV
figures available anywhere, running from 2.7 per cent down to 0.98 per cent, sit inside a national
strategic plan covering 2021 to 2025. The repeating-series test that an earlier region applied to
18 of its 19 countries refuses that document, and the refusal is about publication cadence and not
about the quality of the figures inside.

**A redirect to a site root is a withdrawn publication, and a republication through a data portal
is derived.** Gabon's yearbook URL answers 302 to the institute's new site root, so the published
document is gone and not moved. The institute's remaining HIV content is prevalence under
demographic indicators, republished through a commercial data portal, which grades the Gabon
figures derived against UNAIDS and not additive.

**Five countries comprehensively dark is a result and not a gap to keep searching.** Cabo Verde,
Congo-Brazzaville, Equatorial Guinea, Guinea-Bissau and São Tomé hold zero GAM years, no spending
assessment report and zero sub-national rows, so no expenditure measurement and no sub-national
measurement exists for any of the five anywhere in the pipeline. Recording the five as a finding
is what stops a later round spending a fourth sweep on them.

**The gate on Nigeria's repository is four headers and not the one header three rounds recorded.**
The endpoints answer 403 without a referer naming the wallboard page, a header declaring an
XMLHttpRequest, a JSON accept header and a browser user agent. The base connector class sets only
a user agent and an encoding header, and the class deliberately leaves 403 out of its retryable
statuses, so a missing header fails a run immediately instead of retrying into a rate limit. Three
fields of the richest payload are also JSON documents encoded as strings, each decoding to an
object whose content sits one level down, which is why an earlier survey of the same host reported
three endpoints where five exist and reported the two richest of the five as absent.

**A published correction can fail to repair the defect it was recorded as repairing.** Nigeria's
repository publishes treatment above its own state PLHIV estimate in 14 of 37 states, and an
earlier round recorded the repository's residence matrix as the fix, on the reasoning that patients
are counted where they are treated and not where they live. Recomputing every state's numerator
from residence leaves 13 of 37 states above 100 per cent and moves the worst state the wrong way,
from 158 to 165 per cent. The geography of patient counting is worth at most 18.6 percentage points
here, which is the Federal Capital Territory, and the first-order defect is the state allocation of
the national estimate. So the connector publishes the state treatment count and the state estimate
as separate flagged rows and emits no state coverage percentage, while the national coverage figure
of 87.81 per cent is emitted because the national sum is sound. A documented mechanism for a defect
has to be applied to the data before the mechanism is recorded as the answer.

**A dashboard's own national headline can disagree with every decomposition the same dashboard
publishes.** Nigeria's dashboard reports a national treatment figure of 1,791,837 against a state
sum of 1,678,165 from the same payload, 6.3 per cent lower. The state sum is emitted, because the
state, sex and age decompositions agree with one another to within 0.8 per cent while the headline
agrees with none of the three. The discarded headline travels on the emitted row together with the
reasoning, so a reader who wants the published number can find the published number and can see
why the number was not used. Three decompositions agreeing is evidence about the decompositions,
and a headline standing alone against all three is evidence about the headline.

**Two endpoints of one source can both publish a stock that the panel's duplicate key cannot tell
apart.** The project's duplicate check keys on country, sub-national unit, indicator, population,
sex, age band, year and source identifier, and the key does not include the source's own indicator
code. Nigeria's two endpoints both publish a treatment stock, at different snapshot dates, so in
any year where both snapshots fall the panel would hold two conflicting stock figures under one
source and the writer would only append a warning. The connector resolves the collision instead of
reporting it, by giving the later snapshot month ownership of the stock for that year, suppressing
the earlier snapshot's stock rows, and recording the dropped figure on the surviving national row.
Implementing the rule required loading both payloads before any row is yielded, because the
decision cannot be made from one payload alone. A warning is not a resolution, and a connector that
can see the collision is the only thing in the pipeline that can resolve it.

**A required schema field settles a decision that no amount of flagging can.** The recency endpoint
holds 220,423 recency tests, 9,617 recent infections and 3,403 confirmed by the second assay, broken
out over 34 states and eight age bands, and the figures are self-consistent, with the state block
and the age block summing to the same totals. The figures carry no date, and the panel's row type
declares the year as a required field with no default, so an undated figure cannot enter the panel
and no flag beside the row can stand in for a year that is not there. The same endpoint also holds
one block that is dated, being 76 monthly points across nine series from March 2020 to June 2026,
internally clean in all 76 months and holding five complete calendar years. That block is refused
on two other grounds, being that the measure is viral-load sample collection for recency
confirmation, which no indicator in the panel's vocabulary covers and no other source holds, and
that the yearly denominator runs 554, 1,731, 3,516, 2,012, 1,566, 237 and 1, so the collapse after
2024 cannot be told apart from reporting lag. Offering a choice between admitting a figure with a
loud flag and refusing the figure is only a real choice once the schema has been checked.

**A source that covers units another source omits bounds coverage, and the two sources are not
independent.** Nigeria's repository reports four states that the 2025 PEPFAR extract does not
report at all, holding 106,931 people on treatment between them, against a national
repository-minus-PEPFAR difference of only 71,424, so PEPFAR reports about 35,507 more than the
repository across the 33 shared states. An earlier round had graded one of the comparison sources
as independent of the repository, and the grading was wrong, because the national AIDS programme
both runs the repository and prepares the reporting that feeds the others, and the PEPFAR extract
rests on the same facility registers. Every emitted row now declares shared origin, so the
reconciliation layer reads a discrepancy as a bound on site coverage and never as triangulation.

**What the round says in general. A sweep ordered by country answers whether a country publishes
and cannot answer whether a class adds, so a class that has been left half swept is worth one pass
across every country before any connector in that class is written. An agreement between a new
extraction and a series already held is evidence of a shared origin until the origins have been
shown to differ, and the showing comes first. The panel on disk is the cheapest filter available
for a probe list, because what the panel already holds at a given grain excludes hosts without a
single request. A mechanism recorded as the fix for a defect is a hypothesis until the mechanism
has been applied to the data, and a correction that moves the worst case the wrong way is not a
fix. A publisher's own headline aggregate is one claim among several in the same payload, and
decompositions that agree with one another outrank a headline that agrees with none of them. A
duplicate warning on a key that cannot see which endpoint a row came from is not a resolution, so a
source with two endpoints publishing one quantity needs an ownership rule inside the connector. And
the schema is part of the feasibility question, because a required field with no default closes off
every option that would have needed the field to be absent.**

---

### §9af. A report's own list of tables can disagree with the report's body, a chart's axis can impersonate a table's year header and agree with it anyway, a document can license a figure about a year the document does not assess, a reclassification can account for half of an apparent 21-point fall in a spending share, a gate built for one defect can catch two of another kind, a line that carries figures must not lend its label to the line below, and money with no stated rate is a measurement property and not a formatting choice

*Written 2 October 2026, from the Cameroon build, being the region's first two-connector country.
Both connectors were written against PDFs already cached and every refusal, gate and integrity
check was forced offline before either connector was handed over. The programme connector emits 188
rows from two annual report editions and the expenditure connector emits 36 rows from two national
spending assessments. Four real parser bugs surfaced across three offline runs and an integrity
gate caught every one, which is the part of the round worth generalising.*

**A report's own list of tables can disagree with the report's own body, so a table number is a
caption and never an address.** The 2020-2021 Cameroonian spending assessment's list of tables
calls the body's Tableau 8 "Tableau 7", calls the body's Tableau 9 "Tableau 8", calls the body's
Tableau 14 "Tableau 12", and prints two different tables both numbered Tableau 9. The body then
prints Tableau 14 under a caption reading "en 2018 et 2019" above a table whose own year header
says 2020 and 2021. A parser pinned to a number would have read the wrong table, and a parser
trusting a caption's years would have filed four years of money under the wrong two. Every block is
located by caption text and every year is read from the block's own column header, which is the
same rule the Cameroonian annual reports forced for a different reason, that table numbers move
between editions and the 2023 edition's Tableau 38 is a map of trained peer mentors where the 2024
edition's Tableau 38 is the regional treatment file.

**A chart's data axis can print a year header directly above a table's own header, and the hazard
is invisible precisely when the two agree.** Printed page 41 of that assessment carries the
Graphique 9 axis line reading 2020 and then 2021, sitting above Tableau 8's own header. Taking a
page's first year header would therefore have taken Tableau 8's year order from a chart. On that
page the chart and the table happen to agree, so the defect would have produced correct output and
survived every check, until an edition printed a chart in descending order. Two findings from the
same document show that edition is not hypothetical, because Graphique 9's own data labels extract
in descending year order, reversed from the axis above them, and the two candidate orderings differ
by 231,233,448 FCFA. The rule that follows is that a later header replaces an earlier one up to the
first data row, and the rule had to be written while no observable failure existed to motivate it.

**Searching for the row that satisfies the table's arithmetic beats deciding in advance which row
is the total.** Three of the target tables print a grand total the label map cannot reach, in one
case because the line's only text is a fragment of a merged group heading reading "administrant
des", which leaves the total as an unlabelled pair of numbers with no label of its own. The parser
therefore collects every unlabelled numeric pair on the page and keeps
the one that equals the sum of the components the parser has already matched, and refuses the whole
table when no such pair exists. That refusal is what caught the second bug, where a table's
subtotal printed below the table's last labelled row and a stop-at-the-last-label rule made the
subtotal unreachable. The gate printed an empty candidate list instead of emitting a table with no
total, and the fix was to read the page to its end, which is safe exactly because the gate is
arithmetic and not positional.

**A gate built for one defect caught two bugs of a different kind, which is the strongest argument
for gating that this round produced.** A duplicate-row gate was written to refuse the case where
one indicator is assigned two different values in one parse. The gate caught, first, a two-line
label look-back that matched a bilateral subtotal as the United States row, because the two lines
above that subtotal read "Gouvernement américain" and then "Contributions", and the gate printed
20,279,515,168 against 23,486,587,409 for the same year. The gate caught, second, an unmapped child
row inheriting the label of the parent row printed above it, printing 80,596,207,345 against
5,804,405,493. Neither bug is a duplicate-row bug. Both would have emitted a single plausible
figure that no shape check could have questioned, being an integer of the right magnitude in the
right currency on a registered indicator. A gate's worth is not bounded by the failure the gate was
designed for.

**A line that carries its own figures owns its own label and lends it to nobody.** Wrapped labels
force a parser to look at the line above, and that look-back is what both label bugs exploited. The
condition that fixes it is narrow and mechanical, being that a previous line may be borrowed for a
label only when that previous line carried no figures of its own. Every wrapped label in both
documents is preceded by a label-only line, so the narrowing costs nothing, and the same condition
removes the whole class of parent-to-child label inheritance rather than the one instance that was
caught.

**A published residual can be located rather than bounded, and locating it is what licenses taking
the components from a different table.** The assessment's revenue table discloses that its parts
fall about 0.2 per cent short of its own total. Bounding that residual would have meant accepting a
0.2 per cent error on every donor component. Locating it showed the whole residual sits inside one
line, because that line falls short of two other lines by exactly the amount by which the revenue
table's two children fall short of their parent, being 152,234,707 FCFA in 2020 and 84,910,026 FCFA
in 2021. So that one line is refused as a donor total and the donor components come from a second
table that ties exactly at all three of its nesting levels. A disclosed residual is a lead and not a
limit.

**A document can license a figure about a year the document does not assess, and the licence has to
be a tested identity and not a plausible provenance.** The 2016-2017 assessment prints no split
between domestic public and domestic private money. The later report carries a historical page that
does. Taking two numbers for 2016 and 2017 off a report assessing 2020 and 2021 is exactly the kind
of borrowing that puts a wrong number into a panel while leaving the output looking complete, so the
borrowing was gated three ways. The historical page's domestic public and private rows sum to the
earlier assessment's own residual to the franc in both years, being 5,609,831,158 for 2016 and
10,839,249,471 for 2017. The same page's bilateral row equals the earlier assessment's bilateral
subtotal exactly in both years. And a reversed year read is ruled out numerically, because reading
the columns the other way round would put one year's bilateral figure 2,881,313,043 FCFA away from
the figure the other document prints. All three had to hold before either number was emitted, and
the two borrowed rows are the only figures in the connector that come from a document not assessing
their year.

**A reclassification accounts for about half of an apparent 21-point fall in a spending share, which
matters more here than in most projects because this panel exists to measure cuts.** The earlier
assessment reports prevention at 27.5 and 21.3 per cent of national HIV spending. The later
assessment reports prevention at 6.1 and 6.1 per cent. Half of that fall is definitional, because
the earlier assessment's prevention pool includes voluntary counselling and testing, which the
earlier assessment's own prose names as the largest component of that pool, while the later
assessment reports counselling and testing as a separate category at 10.8 and 9.9 per cent. Adding
the two later categories gives 16.9 and 16.0 per cent against 27.5 and 21.3, so the apparent fall of
21.4 points from 2016 to 2020 and 15.2 points from 2017 to 2021 becomes 10.6 and 5.3 points once
the reclassification is undone, and the published categories cannot say whether those 10.6 and 5.3
points are a cut or a further reclassification inside the two pools. The prevention series is refused outright and the
rest of the intervention classification is refused with it. Treatment is emitted, because both
assessments carry one treatment line covering the same activities, and in the later assessment two
different tables print a treatment total and the two printed totals are equal to the franc in both
years, so the treatment series has two readings and not one. Any series
spanning two classification regimes needs the regimes compared before the series is published, and a
category name that is identical across two documents is not evidence that the category is.

**Every printed percentage is refused, because one document can print three different values for
one quantity and agree with the recomputation at none of them.** The later assessment prints its
2021 international share as 94.1 per cent in one table, 94.0 per cent in another and 94.1 per cent
in the narrative, against 94.1244 per cent recomputed from the levels the same document prints. The
same document prints the 2021 domestic public share as 4.0 per cent in one place and 4.6 per cent in
another where its own numerator and denominator give 4.4316 per cent. One whole table is refused on
that basis, being a key-indicators table whose shares reproduce against no consistent denominator.
The levels are taken, every share is recomputed from levels, and both the numerator and the
denominator travel on the recomputed row so a reader can check the arithmetic without the document.

**Money with no stated conversion rate is a measurement property and not a formatting choice.**
Every figure in both assessments is printed in CFA francs, neither document prints a dollar
equivalent, and neither states a rate. Fetching a rate is data collection and inventing one puts an
untraceable constant inside a parser, where no reader can see it and no later correction can reach
it. The connector therefore emits local-currency levels with the currency named on every row, plus
one currency-free share, and the registry carries a local-currency unit beside its dollar, count and
percentage units. The conversion, when it is wanted, belongs in the panel as a second published
series so that a dollar figure is the quotient of two series a reader can check, and the panel's
site formatter needed no change because an unrecognised unit already renders as a plain grouped
number. The same question arrives again at the next country in the same currency zone, so the
decision is recorded rather than taken inside one parser.

**Nine pages were dumped and read by hand before either parser was written, and five of the
structural hazards above were visible in that dump and invisible without it.** The hazards were a
header led by a stub column, years printed with thousands separators so that a year cell and a money
cell share a shape, a chart axis above a table header, a grand total on an all-numeric line below
two label lines, and a parent row carrying figures directly above an unmapped child. None of the
five would have been recalled from the survey, because the survey characterised documents and did
not read tables. Reading the pages first cost one dump script and removed five classes of silent
error, and the comparison worth keeping is that the four bugs which did survive into code were all
caught by gates, while a hazard not anticipated at all would have had no gate to catch it.

**What the round says in general. A table number, a caption's stated years and a chart's axis are
each a claim a document makes about itself, so a parser locates a block by caption text, reads the
years from the block's own header, and lets a later header replace an earlier one, because the
version of this defect that produces correct output is the version that survives. A grand total is
found by searching for the row that satisfies the table's own arithmetic, never by position, and a
table with no such row is refused whole. A gate written for one defect is worth more than the
defect it was written for, because the two label bugs this round produced were caught by a
duplicate-row gate and would otherwise have emitted one plausible figure each. A disclosed residual
is a lead to be located and not an error bar to be accepted. A figure borrowed from a document that
does not cover the year needs an identity that ties to the franc, a second independent tie, and a
numerical refutation of the wrong column order, all three before the figure is emitted. A category
name shared by two documents is not a shared category, and a series spanning two classification
regimes is refused until the regimes have been compared. Every printed rate is refused and
recomputed from levels, with the numerator and the denominator carried on the row. Money in a
currency the document does not convert stays in that currency, and the conversion becomes a second
panel series instead of a constant inside a parser. And the pages are read by hand before the parser
is written, because a hazard nobody anticipated has no gate waiting for it.**

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
| ~~Its transaction-type column mixes vocabularies~~, corrected 2026-09-21 in §9x | ~~`D`, `E`, `C`, `11`, `IF`, `R`, `IR`, `LR` returned by the same query; 1,834 of 46,964 distinct activity/date/value keys appear under more than one code~~. The codes are one IATI codelist. The count of 1,834 of 46,964 keys was not reproduced. Nigeria's HIV-sector rows give 524 of 19,525 activity, date and value keys under more than one code, and no key pairs a disbursement with an expenditure |
| ~~`sum()` in the d-portal query API returns zero silently~~, corrected 2026-09-21 in §9x | `SUM()` works in single precision. Read on 20 and 21 September 2026, NGA HIV-sector disbursements come back as 338,180,200 (2023), 395,198,700 (2024), 330,811,580 (2025) and 230,015,260 (2026 so far), against 395,198,777 summed row by row for 2024. The 2025 total read 330,726,636 on 15 August 2026, so a closed year can still change. The four totals were read without a `trans_flags=0` filter and may include the two Nigerian rows d-portal copied from commitments, 6,464,864 over all years |
| d-portal's country split departs from the percentages publishers publish | d-portal's `src_dstore_db.js`, lines 843 to 1039, leaves recipient-region percentages out of the pool, gives a country with no percentage a weight of one, makes a negative percentage positive and pools sector vocabularies 1 and 2. Gates Foundation disbursements split by d-portal run between three and 16 per cent above the published split in every year from 2021 to 2026, 94.43m against 83.50m in 2024, and Kenya's 2024 Gates money reads 12.40m against 9.39m. *Surveyed 2026-09-21* (§9x) |
| Money read through d-portal's activity-level join is multiplied | NGA 2024 disbursements read 3,168m over 24,551 rows through the join to the activity-level country and sector tables, 395.2m over 807 rows without the join and 350.5m once the join's percentages are applied. *Surveyed 2026-09-21* (§9x) |
| Disbursements and expenditures are distinct flows and are summed | In the four sampled publishers that report both codes, three of about 66,100 expenditure rows match a disbursement row in the same activity on date and value, two at FCDO and one at UNICEF. WHO 0 of 52,413 and the World Bank trust funds 0 of 32. *Surveyed 2026-09-21* (§9x) |
| d-portal invents disbursements by copying commitments | Rows flagged `trans_flags=1` (`fake_trans` in `src_dstore_pg.js`) number 32 in the HIV sector and carry 627m. Pact (`US-EIN-13-2702768`) holds 30 rows and 627,097,700, read as 317.6m of disbursements in 2019 and 198.1m in 2020, and 29 of Pact's 30 HIV activities name USAID as the funder. Enabel holds two rows and 22,607.84. The XML export carries no copied rows. *Surveyed 2026-09-21* (§9x) |
| No HIV-sector activity comes from a secondary reporter, and no parent activity repeats a child activity's transactions | `act.flags=1` returns nothing, and the `secondary-reporter` attribute is absent or 0 in all 21 sampled publishers. *Surveyed 2026-09-21* (§9x) |
| US government IATI is a republication of ForeignAssistance.gov | By US fiscal year over shared country-years, median ratio 1.0 in every year from FY2016 to FY2024, with 65 to 70 of 70 to 80 country-years within two per cent in each year. *Surveyed 2026-09-21* (§9x) |
| The panel's copy of ForeignAssistance.gov is probably out of date | The copy is dated 18 July 2026. FY2025 reads 3,357m in IATI against 3,093m in the copy over 71 shared country-years, 8.5 per cent higher, with 28 of the 71 within two per cent, and IATI holds 2,162m for FY2026, where the connector's docstring records 613m in the copy. A fresh download would settle the FY2025 gap. *Surveyed 2026-09-21* (§9x) |
| The Global Fund recoded HIV and joint HIV and TB grants from the grants that began in 2018 | H and C grants that began from 2010 to 2016 are coded 13040 alone. Nearly every H or C grant that began in 2018 or later is split between 13040, 12110 and 12263, and the only split grants that began in 2017 are three H grants. *Surveyed 2026-09-21* (§9x) |
| The Global Fund's whole-grant IATI figure equals the CRS series, donor 9OTH012 | Whole H and C grants plus the 13040 share of other grants give a median ratio of 1.0 to CRS in every year from 2012 to 2024, within five per cent in 95 of 98 shared country-years in 2020 and 81 of 91 in 2024. The 13040 share alone gives 0.52 to 0.59 of CRS from 2020, and the 13040 and 12110 shares together 0.90 to 1.0. One reporter published twice under §9f. *Surveyed 2026-09-21* (§9x) |
| The CRS series for the Global Fund appears to change classification in 2020 | Where a C grant disbursed and CRS holds a row, the Global Fund's whole-grant figure exceeds CRS in every year from 2015 to 2019, 546m against 375m in 2019, and 24 of 37 C-grant countries have no CRS row in 2019. In 2020 the C-grant countries read 1,302m in IATI against 1,303m in CRS. Over all countries CRS rises from 1,061m to 2,100m between 2019 and 2020 and IATI from 1,753m to 2,100m, so 692m of the CRS rise of 1,039m has no counterpart. The CRS series' other purpose codes were not checked. *Surveyed 2026-09-21* (§9x) |
| Most of UNDP's HIV-sector money is Global Fund money | 89.2 per cent of UNDP's HIV disbursements and expenditures sit in 73 of 134 activities that name the Global Fund as a funder. *Surveyed 2026-09-21* (§9x) |
| Most of the Asian Development Bank's HIV-sector money is COVID money | 90.1 per cent of the 1,554.9m that d-portal assigns the bank in the HIV sector sits under activity titles naming COVID. *Surveyed 2026-09-21* (§9x) |
| Much HIV-sector money sits under titles with no HIV term | WHO 98.1 per cent, UNAIDS 85.7, BMZ (DE-1) 75.5, the Gates Foundation 57.0 and UNICEF 38.8. WHO and UNAIDS titles are strategy lines, and BMZ's leading titles are voluntary contributions to the Global Fund. Gates titles such as the MK-8527 prevention trial name an HIV drug without naming HIV, so a title test alone cannot exclude an activity. *Surveyed 2026-09-21* (§9x) |
| The Global Fund's financial datasets are unread | `AllFinancialIndicators` on `fetch.theglobalfund.org/v4.2/odata` lists 32 financial indicators over 16 datasets, among them disbursements, commitments, grant budgets and expenditure by intervention. The `global_fund` connector reads only `AllProgrammaticIndicators` and `Geographies`. *Surveyed 2026-09-21* (§9x) |
| The Global Fund's IATI XML export cannot be read whole, because d-portal repeats every transaction of a grant inside every activity of that grant | 573,710 bytes an activity over 1,246 activities, about 715 MB, measured over the export d-portal serves at `/q.xml`. The repetition is the same behaviour item 28 found later in the activity-level join, where d-portal serves one complete copy of an activity per joined row. The `iati` connector therefore reads the Global Fund from the query service at `/q` and not from the export, which is the departure RESUME.md item 19 accepted, and `extra.read_from` on all 2,577 Global Fund rows of the panel of 30 September 2026 records the route taken. Three further measurements say the departure skips no allocation decision, being that 42 of 48 sampled Global Fund activities name one country at 100 per cent and no region while the other six name a region and no country, that the Global Fund publishes in US dollars only, and that the Global Fund publishes in sector vocabulary 1 only, so neither a currency conversion nor a vocabulary filter can change a Global Fund figure. *Surveyed 2026-09-21, route confirmed in the panel 2026-09-30* (§9x) |
| An IATI transaction amount is the `<value>` element's own text and never an attribute | Over the 114 cached publisher pages the run of 28 September 2026 left on disk, all 374,789 transaction `<value>` elements carry the amount as element text and not one carries an attribute named `value`. All 374,789 carry a `value-date` attribute and 374,670 carry a `currency` attribute, so `<value currency="USD" value-date="2024-02-22">3371462</value>` is the shape to expect. Reading an attribute named `value` returns nothing at all and reports a publisher filing thousands of disbursements as a publisher with no HIV money, which is what the first draft of the `iati` connector did across its whole sample, and which survived a test because every rejection path in the transaction loop was a bare `continue` with no counter. Every rejection path now carries a counter and the per-publisher log line names each one. *Surveyed 2026-09-21, remeasured over the full cache 2026-09-30* (§9x) |
| A recipient element can carry a percentage and no code, which is money whose destination the publisher did not state | Over the full cached export, 74 activities of 11,698 carry a recipient element with a percentage and no code, 67 of them UNICEF's (`XM-DAC-41122`) and seven the Swiss Agency for Development and Cooperation's (`CH-4`). Each of UNICEF's 67 carries two such elements, one `recipient-country` and one `recipient-region`, both at 100 per cent and neither coded, and the connector's own `_geography` returns no country share at all on any of the 67, so nothing in those activities names a country. Put through `_geography` and `_sector_share`, the unnamed share carries 123,724,334.67 USD of UNICEF HIV-sector money over 2012 to 2026 across 2,046 transactions, and 1,266,281 CHF of Swiss money over 2013 to 2016, six of the seven Swiss activities also naming a coded country so that the Swiss unnamed share is a part of each transaction and not the whole. Against the 693,702,825 USD of UNICEF money the panel writes, the unnamed money is 15.1 per cent of the UNICEF HIV money the connector reads and it reaches no country row. The uncoded element stays inside the percentage pool deliberately, because dropping the element would hand its share to whichever country was named beside it, and a country gaining money no publisher ever assigned to it is worse than writing nothing. The `_geography` docstring said 34 such activities, which was the count over one page a publisher, and the count over the full cache is 67 at UNICEF and seven at the Swiss agency. *Surveyed 2026-09-21, measured over the full cache 2026-09-30* (§9x) |
| A transaction can state no currency at any level the IATI standard provides, and this connector then writes the amount as US dollars without saying so | Over the full cached export, 119 of the 374,789 transaction `<value>` elements carry a `value-date` and no `currency`, and no enclosing activity and no `iati-activities` root element states a `default-currency` either, so the currency is absent from the publisher's file and was not missed by the reader. `_to_usd` returns the value unchanged when the currency string is empty, so those amounts enter the panel as dollars and no key on the row records the assumption. 90 of the 119 pass the connector's transaction-type and year filters, being 47 at Finland, 38 at Irish Aid, four at Plan International USA and one at the Indigo Trust, the survey's first count of 83 having applied a sector filter the connector does not apply and a recount from the cache on 1 October 2026 correcting the figure to 90, and 48 panel rows carry 13,629,785.48 USD written this way, being the Ministry for Foreign Affairs of Finland (`FI-3`) with 4,324,764.00 USD over 35 rows from 2002 to 2010, and Irish Aid (`XM-DAC-21-1`) with 9,305,021.48 USD over 13 rows in 2013 and 2015. Both publishers state EUR on the rest of their HIV transactions and state no second currency anywhere, 68 values stating EUR against 75 stating nothing at Finland and 217 against 38 at Irish Aid when counted over every transaction value in each publisher's cached file, so treating the amount as dollars is unlikely to be right for either. The money affected is 63.1 per cent of the 6,852,141.39 USD Finland holds in the panel and 28.8 per cent of the 32,266,420.29 USD Irish Aid holds. Two further publishers file uncurrencied HIV transactions and write nothing into the panel, Plan International USA (`US-IRS-13-5661832`, 36,724,252.14 over Benin 2014 and Benin 2015) because an international NGO belongs to no written series, and the Indigo Trust (`GB-CHC-1075920`, 5,774.91 on South Africa 2018) because the foundation series is held behind `_WRITE_FOUNDATION = False`. The Indigo Trust states a currency on no transaction value anywhere in the Indigo Trust's cached file, so no single currency exists to infer there and the amount is refused. Plan International USA states US dollars on one of five transaction values, which this row first reported as no currency at all, and a remeasurement over every value element in the cached file on 1 October 2026 corrected the count. Two panel figures reproduce exactly from the cache, Finland's Uganda 2010 row at 676,335.00 USD and Irish Aid's Uganda 2013 row at 6,500,000.00 USD, so the reading is the panel's own arithmetic. **Repaired, run and verified on 1 October 2026.** Jason approved the inference with a refusal as the fallback, and `_to_usd` now refuses a blank currency instead of returning the amount unchanged, so the one line that caused the defect can no longer produce dollars. The connector reads a currency down a four-rung ladder, being the transaction's own `currency`, the enclosing activity's `default-currency`, the file's `default-currency` and then the one currency the publisher states across the whole file, and refuses the amount where no rung answers. The two default-currency rungs change no figure in today's cache, because zero of the 119 affected transactions sit under an activity or a file stating a default currency, and the two rungs guard against an inference overriding a stated currency in a later export. Every row holding money that rests on the fourth rung carries a `currency_assumed` key naming the publisher, the inferred currency, the dollars resting on the inference and the number of the publisher's own transactions the inference rests on, and the per-publisher log line gained a refusal counter naming all four rungs. Checked offline against the cache with every exchange rate stubbed at 1.0, so that only a changed decision can move a figure, the repaired code reproduces the figures the old code wrote on every affected row, Finland showing zero moved country-years and 35 flagged rows holding 4,324,764.00 USD, Irish Aid zero moved and 13 flagged rows holding 9,305,021.48 USD, and the total 13,629,785.48 USD over 48 rows, while the controls `AU-5`, `SE-0`, `GB-GOV-1` and `CA-3` move nothing and flag nothing. A second check ran the real `fetch()` over both publishers and wrote 165 rows, 48 carrying `currency_assumed`, none drawing inferred money from two publishers, the largest being Uganda 2013 at 6,500,000.00 from Irish Aid. Jason ran `iati` at 18:09 on 1 October 2026 and the panel on disk now carries the repair. 48 rows carry `currency_assumed`, being 35 naming `FI-3` and 13 naming `XM-DAC-21-1` and none naming any third publisher, every one of the 48 names EUR with the evidence counts 68 at Finland and 217 at Irish Aid, and the 48 rows moved from 272,075,448.89 USD to 276,244,253.05 USD, so the inferred money stands at 17,798,589.64 USD against the 13,629,785.48 USD the same money carried when every rate was stubbed at 1.0, which is the euro rate doing the work and nothing else. No row appeared and no row vanished, the two `iati` series holding 4,485 rows on each side of the run, and the only other real move in those series is Central African Republic 2026 rising 2,093.83 USD on `FR-6`'s money in the live partial year, the other 490 differing values moving 0.0000148 USD between them, which is the order a float sum is accumulated in. The refusal counter fired once, on the Indigo Trust, refusing 16,985.02 as the file wrote the amount, which is the whole transaction of which the 5,774.91 above is the purpose-13040 share at 34 per cent. The run also exposed a labelling defect, now repaired, the refused amount having been accumulated into the connector's `money` dictionary whose every label the log prints with a `USD` suffix, so the one figure whose currency nobody stated was printed as "16985.02 USD", and the connector now holds the refused total apart and prints the total with no currency suffix. RESUME.md section 5c item 30 holds the build record and the run record. *Surveyed 2026-09-30, approved and built 2026-10-01, run and verified 2026-10-01* (§9x) |
| The reason the panel stated for a missing Global Fund value denied a grant that the same row names | A country-year in which the `iati` connector measured no Global Fund HIV money is written with no value and a stated reason, and 192 rows of the panel of 30 September 2026 carried the one reason the connector had, which reads that none of the transactions was an H or C grant or carried purpose code 13040. On 10 of the 192 that sentence is false, because the row's own `grant_identifiers` names an H or a C grant. The cause is that the connector adds the activity identifier to the country-year's grant set before the reimbursement branch abandons the transaction, so a country-year whose only transaction belonging to an H or C grant was a reimbursement lists the grant while never entering `whole_grant_years`. The 10 rows are Botswana 2012, China 2014, Côte d'Ivoire 2009, Colombia 2010, Guinea 2006, Indonesia 2007, Peru 2015, Romania 2011, Romania 2013 and Suriname 2016, holding -10,503,815.34 USD of reimbursements between them. The absent value is the right answer on all 10, because a reimbursement is money returning to the Global Fund and not a disbursement, and none of the 10 carries an OECD Creditor Reporting System figure that contradicts the absence, so what was wrong was only what the panel said about the absence. A second defect sat in the same place, the key `grants_seen_but_not_hiv_coded` being written as the identical list the row already carries under `grant_identifiers` while the key's name asserts something the list does not satisfy, identical on all 192 rows with none differing. **Repaired, run and verified on 1 October 2026.** The connector now chooses between two stated reasons on the row's own grant list, the duplicated key is gone, and the unmeasured log line counts the two reasons apart instead of asserting the non-HIV cause for every unmeasured country-year. Checked by driving the real `_global_fund` with synthetic rows beside the module as it stood before the repair, a country-year holding one malaria grant's disbursement carries the non-HIV reason on both modules, a country-year holding an H grant's reimbursement beside a TB grant's disbursement carries the non-HIV reason on the old module and the reimbursement reason on the new one, and a country-year holding an H grant's disbursement carries its value and `whole_grant_basis` true on both. No value moves on any row. Jason ran `iati` at 18:09 on 1 October 2026 and the panel on disk now carries the repair, the 2,577 Global Fund rows standing at 2,577 on each side of the run with 2,385 valued and 192 unvalued on each side, the 192 now splitting 182 non-HIV and 10 reimbursement with the 10 being exactly the 10 named above, `grants_seen_but_not_hiv_coded` standing on all 192 rows before the run and on none after, the series total unchanged to the cent at 38,152,946,329.59 USD, and no country-year moving between carrying a value and carrying none. RESUME.md section 5c item 31 holds the build record and the run record. *Audited, approved and built 2026-10-01, run and verified 2026-10-01* (§9x) |
| A country-year the Global Fund reached by reimbursement alone is dropped from the panel with no row and no log line | The writing loop of the Global Fund branch reads `for (iso3, year) in sorted(totals)`, and the reimbursement branch adds the grant to `grants` and the money to `reimbursed` before abandoning the transaction, so a country-year in which every Global Fund transaction is a reimbursement creates no key in `totals`. The connector writes no row for that country-year, states no reason and prints no counter, and the reimbursement money the connector accumulated is never read again. The 10 rows above are visible only because each of the 10 also holds a transaction of some grant that is not an H or C grant, and that branch runs `totals[key] += 0.0` through a `defaultdict`, which creates the key. RESUME.md item 24 set this connector's convention, namely that a country-year the connector saw without measuring any HIV money is kept with no value and a stated reason because dropping the country-year hides the Global Fund's presence in a country, and `hivimpact/schema.py` line 60 states the same convention for the panel, so a country-year reached by reimbursement alone is the one case the code still drops. The population cannot be counted offline, because a dropped country-year leaves no trace in the panel and the Global Fund rows come from d-portal's query service, which this connector never caches, so the count comes with the next `iati` run once a counter exists to print it. Found by driving the real `_global_fund` with a synthetic country-year holding one H grant reimbursement and nothing else, which both the repaired and the unrepaired module write nowhere. Jason's run of 18:09 on 1 October 2026 carried items 30 and 31 without this one built, and comparing the panel that run wrote against `hiv_panel.prev.csv` found no Global Fund country-year present on one side and absent on the other, which is the invisibility this row describes rather than evidence that the population is empty. **Repaired, checked offline, run and closed on 1 October 2026, the repair having missed the run of 18:09 and ridden a second run at 19:07.** The writing loop now reads `for (iso3, year) in sorted(grants)`, and `grants` holds every country-year the connector saw because `grants[key].add(aid)` runs above the reimbursement branch, so the keys of `grants` are the union of the keys of `totals` and the keys of `reimbursed` by construction. A country-year reached by reimbursement alone is written with no value, the grant list, the reimbursement total, a reason naming the case and a boolean key `only_reimbursements_seen`, which stands on every row of the series so that the case can be selected or excluded without matching words inside the reason. The run log splits the unmeasured count three ways instead of two and the three counts add to the unmeasured total. `latest` is taken over `grants` for the same reason the loop is, which is the one way the repair could have moved a row already in the panel, and it cannot move one on today's corpus, because the `iati` Global Fund series ends at 2026, 98 of the 102 rows in 2026 carry a value and the year filter refuses anything past `--end`, so the maximum year over `grants` equals the maximum over `totals`. Checked by driving the real `_global_fund` with six synthetic country-years, where the loop over `totals` wrote three rows and the loop over `grants` wrote six, the three added rows carrying no value, the boolean and the new reason, while a country-year holding an H grant reimbursement beside a malaria disbursement kept the item 31 reason and a country-year holding only non-HIV money kept the item 24 reason. Jason's run of 19:07 on 1 October 2026 measured the population the dropped rows left no trace of, at 54 country-years over 33 countries from 2007 to 2025, led by Equatorial Guinea with five years, North Korea with four, and Myanmar, Yemen and Gabon with three each. The Global Fund series moved from 2,577 rows to 2,631, the valued rows stayed at 2,385, the unvalued rows moved from 192 to 246, and the run log split the 246 into 182, 10 and 54, which add to 246. Verified against the panel and against `hiv_panel.prev.csv` after the run, all 54 added rows carry no value, `only_reimbursements_seen` stands on all 2,631 rows and is True on 54, every one of the 2,577 keys present before the run is present after with none lost and none duplicated, no value moved, and no `partial_year` flag moved, the same 102 rows carrying the flag before and after and every one of the 102 a 2026 row, which is the prediction this row recorded before the run. 182 of the 2,577 pre-existing rows differ in the last bits of their stored value, largest absolute difference 0.0000002086 USD and largest relative difference 1.311e-15, which is summation-order noise from d-portal serving an activity's transactions in a different order between the two runs and not an effect of the repair, because `value` is a direct read of a per-key accumulator holding no cross-row state. RESUME.md section 5c item 37 holds the build record and the verification. *Found 2026-10-01, approved, built, run and closed 2026-10-01* (§9x) |
| A publisher's reimbursement is summed in whatever currency the publisher wrote and logged as US dollars | `hivimpact/connectors/iati.py:1513` is the publisher reimbursement branch and reads `money["reimbursements (carried in extra, never subtracted)"] += raw`, where `raw` is the number as the publisher's file wrote the number. The branch stands above the four-rung currency ladder the row for item 30 describes, so the branch runs before any currency is resolved, and the per-publisher money log prints every label in that dictionary with a `USD` suffix. A publisher filing reimbursements in euros and another filing in dollars would be added together and the sum printed as dollars, which is the assumption item 30 removed from `_to_usd` surviving in the one branch that reads `raw` before the ladder. A second defect sits in the same branch, in the label and not the arithmetic, the counter reading "reimbursement, carried in extra" while nothing is carried into any publisher row's `extra`, the wording having been borrowed from the Global Fund branch at `hivimpact/connectors/iati.py:1014`, which does carry `reimbursements_usd` onto a row and whose total is genuinely in dollars because d-portal's query service serves the Global Fund amounts already converted. Nothing in the panel is wrong today and the defect is latent. Counting every transaction in every cached publisher file offline, the cache holds 374,789 transactions and none of type 7, the types present being 214,366 of type 4, 67,474 of type 3, 43,150 of type 2, 26,401 of type 11, 20,830 of type 1, 1,952 of type 5 and 616 of type 6, so no publisher reaches the branch, neither the counter nor the money label appears for any publisher in the run of 1 October 2026, and neither defect showed itself in five runs. A publisher adding a reimbursement to a later export is what turns the defect live, and the Global Fund already files reimbursements, so the shape is one IATI publishers do use. Found while repairing the log label the item 30 run exposed, which is the same assumption in a neighbouring branch. **Repaired, checked offline and closed on 1 October 2026, and no run was needed, because the branch writes nothing onto a row and feeds nothing into a value.** The branch stays above the currency ladder, where a reimbursement on this path is logged and reaches no row, so nothing below the branch has work to do on it. The money is now held in a dictionary keyed on currency, apart from `money` and for the same reason item 30 holds its refused total apart, and the currency is read from the transaction, then from the activity's `default-currency`, then from the file's `default-currency`, which are the three rungs of that ladder that read the file and never infer. The fourth rung is deliberately not consulted, because that rung is an inference and this branch measures nothing, and an amount no part of the file states a currency for is logged as what it is. The log prints one line per currency, with the currency named and no suffix added, the counter now reads "reimbursement, read and written nowhere", and the false money label is gone. Checked by driving the real `_publisher_rows` with synthetic XML stating one currency on a transaction, one on an activity default, one on a file default and none anywhere, which logged four figures across the two files under `EUR`, `SEK`, `GBP` and a line naming no currency, printed no `USD` suffix on any of them, and left the publisher's ordinary disbursement in the panel bucket unchanged. The defect stays latent, because no publisher in the cache files a transaction of type 7, and Jason's `iati` run of 19:07 on 1 October 2026 confirms the latency on live data, having read all 94 publishers filing under purpose 13040 and printed no reimbursement line for any of them. RESUME.md section 5c item 38 holds the build record. *Found 2026-10-01, approved, built, checked offline and closed 2026-10-01* (§9x) |
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
| FA.gov's documented API paths all return 404, and the working prefix is undocumented | Every `/data-api/…` path in the OpenAPI description answers with nginx's 404 page. `/api/data-api/complete-data.json` answers with JSON, found by trying candidate prefixes. *Surveyed 2026-09-23* (§9y) |
| The FA.gov API needs no key, and its OAuth block is boilerplate | The security scheme describes itself as get-only public data needing no authentication and points its authorisation and token URLs at api.example.com and test.com. The transaction endpoint carries an empty security list. *Surveyed 2026-09-23* (§9y) |
| Neither the FA.gov API nor the FA.gov bulk CSV can be fetched by the connector | 403 with `cf-mitigated: challenge` to curl, to curl carrying a current Chrome user agent with Accept and Referer headers, and to Python's `urllib`, on `/api/data-api/complete-data.json` and on `/static/us_foreign_aid_complete.csv`. Both answer a browser on the same machine. *Surveyed 2026-09-23* (§9y) |
| FA.gov filters documented as arrays take one value, and `per_page` caps below its documented maximum | `country_code=NGA&country_code=KEN&fiscal_year=2024` returns 1,706 records all Kenyan, which is Kenya's own count, and `country_code=NGA,KEN` returns none. `per_page=10000` is answered with `per_page` 1,000 in `page_info`. *Surveyed 2026-09-23* (§9y) |
| The connector's four-column HIV rule reproduces on the API as the union of two queries | One USG sector name of 51 contains HIV and one DAC sector does, code 134, and no USG category name does. FY2024 disbursements, USG query 2,564 rows and 10,223.6m, DAC query 2,620 rows and 10,265.2m, 75 rows and 62.3m in the USG query alone with COVID-19 control among their purposes, 131 rows and 103.9m in the DAC query alone under USG labels of Malaria, Tuberculosis, Maternal and Child Health and Direct Administrative Costs, union 2,695 rows and 10,327.5m. *Surveyed 2026-09-23* (§9y) |
| FA.gov's World row is two thirds of the FY2024 HIV total, and the panel never holds it | `WLD` holds 6,625.4m of the FY2024 union total of 10,327.5m and resolves to no ISO3 code. The FY2026 total over all codes is 2,093.0m against the 2,162m IATI holds, so the FY2026 gap §9x reported was the July snapshot and the country-only reading. *Surveyed 2026-09-23* (§9y) |
| The data of 31 August 2026 is above the July file the panel holds in every year | Countries only, current dollars, millions, API against the connector's docstring. FY2024 3,702.1 against 3,659.4, FY2025 3,117.9 against 3,084.6, FY2026 1,012.3 against 613. FY2025 by agency, USAID 1,402.0 against 1,379.2, CDC 1,364.5 against 1,356.8, State 273.2 against 270.7, other 78.3 against 77.9. FY2026 State 999.7, USAID 2.0, CDC 0. Restatement and rule difference are not separated, which needs a scan of the July file. *Surveyed 2026-09-23* (§9y) |
| Every US agency publishes ForeignAssistance.gov's own data as IATI XML on Amazon S3, outside the Cloudflare challenge | The IATI Registry lists 2,116 publishers, of which 21 carry an identifier beginning `US-GOV`. The four largest are the US Agency for International Development with 208 packages, the Department of State with 207, the Department of Defense with 180 and the Department of Agriculture with 155. The files sit on `s3.amazonaws.com/files.explorer.devtechlab.com`, `iati-reporting.s3.amazonaws.com` and `iati-reporting.s3.us-east-1.amazonaws.com`, and every file probed answered curl with 200 and no challenge. The State and Health and Human Services files carry elements in the namespace `https://foreignassistance.gov`, among them `treasury-account` with a `fiscal-funding-year` child, which names ForeignAssistance.gov as the generator. **A claim recorded on 23 September 2026 of 487 files across three agencies counted only the three publishers then searched and is not the size of the corpus.** *Surveyed 2026-09-23, corrected 2026-09-26* (§9y) |
| The S3 country file reproduces the FA.gov API's figures for Health and Human Services | Nigeria, Health and Human Services as reporting organisation, HIV disbursements in millions by US fiscal year derived from the transaction date, S3 file first and API `HHS/CDC` second. FY2021 75.35 against 76.19, FY2022 152.07 against 152.22, FY2023 129.99 against 130.53, FY2024 98.43 against 98.46, FY2025 101.90 against 101.90. The differences are at or below 1.1 per cent and are not yet separated into fiscal-year derivation and content. **The agreement holds for Health and Human Services alone. The heading of this row on 23 September 2026 read that the S3 files reproduce the API's figures, which the next two rows show is false for the other two agencies.** *Surveyed 2026-09-23, corrected 2026-09-26* (§9y) |
| The S3 country files understate the US Agency for International Development in every year and the Department of State from FY2025 | Nigeria HIV disbursements in millions, country file against API. The US Agency for International Development, FY2020 53.67 against 145.51, FY2024 63.58 against 190.08, FY2025 48.71 against 148.11, and no year of the 14 agrees. The Department of State, FY2021 to FY2024 agree on sums under 0.25 a year, then FY2025 8.82 against 23.10 and FY2026 46.32 against 115.13. *Surveyed 2026-09-26* (§9y) |
| The shortfall is the money a central bureau manages, and the Multiple Countries files hold it with a country code | The API's sub-agency field splits Nigeria FY2024 under the US Agency for International Development into 110.75 million managed by the Global Health bureau and 79.32 million managed by the Africa bureau, and splits Nigeria FY2026 under the Department of State into 115.13 million managed in full by the Bureau of Global Health Security and Diplomacy. The first 6.3 megabytes of the Department of State's Multiple Countries-1 file carry 39.45 million of Nigeria FY2026 HIV disbursements, 38.66 million of it drawn on the Agency for International Development HIV/AIDS Working Capital Fund, all of it in one activity, Global Health Supply Chain - Procurement and Supply Management, award `AID-OAA-TO-15-00007`. The Department of State publishes three Multiple Countries files holding 99.9 megabytes and the US Agency for International Development publishes 34. *Surveyed 2026-09-26* (§9y) |
| The files named Worldwide carry no country attribution and cannot be split | The Department of State's Worldwide-2 file holds 5,127 activities and no `recipient-country` element at activity level, and every one of the 13,723 transactions that names a recipient country names code 998, countries unspecified. Worldwide-1 holds no Nigeria-coded transaction either. *Surveyed 2026-09-26* (§9y) |
| The Department of State and the US Agency for International Development both report the same award from FY2025, under different identifiers | Nigeria FY2026 HIV disbursements, the Department of State 46.32 million over six activities and the US Agency for International Development 46.52 million over the same six award numbers. The identifiers differ, `US-GOV-11-72062020CA00001-227505` against `US-GOV-1-72062020CA00001`, and so do the titles, KP-CARE 1 Activity against Key Populations Care 1. No FY2024 or earlier award is shared. In FY2025 the eight shared awards carry 8.68 million on the Department of State's side and 39.18 million on the US Agency for International Development's. So deduplication has to key on the award number inside the identifier, and a rule is needed for a shared award reported at two amounts. *Surveyed 2026-09-26* (§9y) |
| HIV is about six per cent of the US corpus, and eight of the 21 US publishers carry all of it | HIV disbursements are 52,360 of the API's 823,061 disbursement records and 2,695 of the 47,365 records of FY2024. Over FY2001 to FY2026 the union rule gives 133.11 billion dollars by managing agency, USAID 72.09 and 54.2 per cent, HHS 43.23 and 32.5 per cent, STATE 15.30 and 11.5 per cent, DOD 2.14 and 1.6 per cent, the Peace Corps 0.296, the Millennium Challenge Corporation 0.023, the Department of Labor 0.021 and the African Development Foundation 0.003. The first four are 99.75 per cent and the other 13 US publishers have disbursed no HIV money in 26 years. *Surveyed 2026-09-26* (§9y) |
| Two encodings in the IATI Registry's own URLs break a naive fetcher | Eighteen of the 34 USAID Multiple Countries URLs answer 403 when the `+` in the stored path is sent literally, because the `+` stands for a space, and Python's `urllib` refuses a URL carrying a literal space outright. Both forms have to be decoded with `unquote_plus` and re-quoted before the fetch. Transaction elements also appear both as `<transaction>` and as `<transaction ref="...">`, so a reader matching the bare tag silently finds none in the Multiple Countries files. *Surveyed 2026-09-26* (§9y) |
| The S3 files carry every field the FA.gov connector now derives from text columns | A transaction holds `transaction-type` code 3 for a disbursement, `transaction-date`, `value` in US dollars, `recipient-country` as a two-letter code, `sector` vocabulary 99 whose narrative is the USG sector name, among them HIV/AIDS, and `sector` vocabulary 1 whose code is the DAC purpose code, among them 13040. The reporting organisation reference gives the managing agency, `US-GOV-14` being Health and Human Services. *Surveyed 2026-09-23* (§9y) |
| The S3 window reaches the current fiscal year, starts in a different year for each agency, and starts earlier once an agency's Multiple Countries files are added | Nigeria HIV disbursements run in the US Agency for International Development's country file from FY2013 to FY2026 without a gap, in the Health and Human Services country file for FY2018 and FY2019 in token amounts and then FY2021 to FY2025, and in the Department of State's country file from FY2021 to FY2026. The Department of State's three Multiple Countries files carry the same agency back to FY2012, eight years earlier than the Department of State's country file alone. The US Agency for International Development's 34 Multiple Countries files do not move that agency's start year, which stays at FY2013 with no Nigeria HIV disbursement in FY2012 or any earlier year, and the agency's files reproduce the API only from FY2019, falling between 11,570 and 4,044,658 dollars short in each year from FY2013 to FY2018. Health and Human Services was not tested beyond the country file. The API carries the whole-of-government Nigeria HIV series from FY2001, rising from 1.09 million at FY2001 to 249.47 million at FY2008, so the S3 files cannot supply the first decade of PEPFAR. **This row replaces a claim recorded on 23 September 2026 that the S3 route covers FY2021 onwards and no earlier year, which generalised from the Health and Human Services file alone and understated the US Agency for International Development by eight years. The Department of State window of FY2021 to FY2026 recorded on 26 September 2026 was the country file alone.** *Surveyed 2026-09-23, corrected 2026-09-26* (§9y) |
| Reading every file of one agency and testing each transaction reproduces the API to the cent | The Department of State's Nigeria country file plus the Department of State's three Multiple Countries files give Nigeria HIV disbursements in millions of FY2012 0.624, FY2013 0.625, FY2014 0.778, FY2015 0.552, FY2016 0.762, FY2017 1.078, FY2018 1.108, FY2021 0.251, FY2022 0.141, FY2023 0.138, FY2024 0.172, FY2025 23.096 and FY2026 115.128, and the API gives the same 13 figures. FY2019 and FY2020 hold no Department of State Nigeria HIV disbursement in either source. The US Agency for International Development's Nigeria country file plus that agency's 34 Multiple Countries files reproduce the API within 173 dollars at FY2020 to FY2024, on totals of 100 to 190 million, and within 550 dollars at FY2025 and 59 at FY2026 once the Department of State's overlapping total is subtracted. *Surveyed 2026-09-26, extended 2026-09-27* (§9y) |
| Deduplicating on a publisher's own transaction reference deletes money the API counts, and only a whole-row key is safe | The US Agency for International Development publishes five FY2026 Nigeria HIV disbursements twice over, 15,851,027 dollars, each repeat identical to the original in reference, date, value and receiver and sitting in the same file as the original, four pairs worth 15,649,184 dollars in `iati-activities-Multiple_Countries-34.xml` and the fifth pair worth 201,843 dollars in `iati-activities-Nigeria.xml`, and the API counts each payment once. The Department of State, by contrast, attaches one transaction reference to genuinely different transactions, and removing repeats by reference alone moves the Department of State's FY2012 figure from 623,717 dollars to 551,282, FY2015 from 551,901 to 360,890 and FY2018 from 1,108,121 to 950,903, breaking seven of the 13 reconciled years. A key of activity identifier with reference, date, value and receiver together keeps all 13 Department of State years exact and still removes the 15,851,027 dollars. *Surveyed 2026-09-27* (§9y) |
| A US HIV transaction with no recipient country is regional money, and the country panel cannot carry it | The US Agency for International Development's 34 Multiple Countries files hold 905 HIV disbursements worth 101.245 million dollars that name no recipient country at either the activity or the transaction level, and every one names a recipient region instead, 511 under code 289 south of Sahara regional, 356 under code 998 countries unspecified, 19 under 789, 11 under 380 and eight under 619. The API does not carry that money under Nigeria either. *Surveyed 2026-09-27* (§9y) |
| A publisher's country file and Multiple Countries files do not overlap, so adding them is safe | Across the US Agency for International Development's Nigeria HIV disbursements the two sets share no transaction reference and no activity identifier, 204 activity identifiers in the country file against 77 in the Multiple Countries files. *Surveyed 2026-09-27* (§9y) |
| Health and Human Services very nearly reconciles from the country file alone, which no other agency does | The Health and Human Services Nigeria country file gives Nigeria HIV disbursements of 101,896,712 dollars at FY2025, the API's figure to the cent, and falls short by 27,038 dollars at FY2024, 542,722 at FY2023, 148,765 at FY2022 and 839,734 at FY2021. The same file holds only 5,054,679 dollars at FY2018, 662,394 at FY2019 and nothing at FY2020, against API figures of 120.86, 98.21 and 119.42 million, so the agency's usable window on the country file alone is FY2021 to FY2025. The residual and the missing years are untested against the agency's Multiple Countries files, which cost 63.2 megabytes in all across 72 files. *Surveyed 2026-09-27* (§9y) |
| One award can carry Malaria-coded and HIV-coded transactions side by side, so the sector test belongs on the transaction | Award `AID-OAA-TO-15-00009`, the Malaria task order of the Global Health Supply Chain contract, holds 11 Nigeria disbursements across FY2025 and FY2026 worth 35.09 million in the Department of State's Multiple Countries-2 file. The two dated 1 October 2025 and 1 February 2026 carry DAC purpose code 13040 and sum to 9,016,197 dollars, which is what the API attributes to HIV for that award, and the other nine carry Malaria control, code 12262. All 11 carry the USG sector narrative Malaria. *Surveyed 2026-09-26* (§9y) |
| ForeignAssistance.gov's DAC sector code 134 is the site's own numbering, and the code the IATI files carry is the purpose code 13040 | Every Nigeria disbursement record answering `dac_sector_code=134` carries `dac_purpose_code` 13040 and no other, and 13040 begins 130 under the DAC's own numbering. So a reader testing an IATI `sector vocabulary="1"` code for the prefix 134 matches nothing, and the test has to be equality with 13040. The failure is silent because the USG vocabulary narrative HIV/AIDS carries almost every HIV transaction unaided, and it showed in only 30 of the 2,478 Nigeria HIV records, which the API counts as HIV under the DAC code while labelling them Malaria, Tuberculosis, Maternal and Child Health or Direct Administrative Costs under the USG sector name. *Surveyed 2026-09-26* (§9y) |
| The eight HIV-carrying publishers hold 2.59 gigabytes over 902 files, and two thirds of the largest publisher's bytes are the files the panel cannot do without | Content lengths taken without downloading the bodies. The US Agency for International Development 1,891.1 megabytes over 208 files, the Department of State 448.2 over 207, the Peace Corps 83.0 over 70, the Department of Defense 77.0 over 181 with one file failing to answer, Health and Human Services 63.2 over 72, the African Development Foundation 24.3 over 48, the Department of Labor 3.5 over 62, and the Millennium Challenge Corporation's 54 files unsized. The US Agency for International Development's 208 divide into 157 country files worth 529.4 megabytes, 34 Multiple Countries files worth 1,250.7, 12 region-coded files worth 23.8, two region-named worth 0.1, two Worldwide worth 72.6 and one organisation file worth 14.5. Skipping the Worldwide files saves four per cent of that publisher's bytes. *Surveyed 2026-09-26* (§9y) |
| Where two US agencies report one award, the API takes the Department of State's figure away from the US Agency for International Development's and does not choose between the two | Award 72062020CA00001 in Nigeria, HIV disbursements in dollars, IATI file against API. FY2020 to FY2024 the US Agency for International Development alone, 7,180,925 against 7,180,926, 8,083,628 against 8,083,629, 12,003,217 against 12,003,222, 12,013,819 against 12,013,821, 7,522,939 against 7,522,944. FY2025 the Department of State 977,134 in both and the US Agency for International Development 4,629,063 in the file against 3,651,931 in the API, and 4,629,063 less 977,134 is 3,651,929. FY2026 the Department of State 4,726,591 in both and the US Agency for International Development 4,726,587 in the file against nothing in the API, and 4,726,587 less 4,726,591 is four dollars below zero. The two copies share no transaction identifier and use different date conventions, quarter ends against the first of the month. The API holds the shared award as two separate activity records, the Department of State's 227505 and the US Agency for International Development's 215553 at FY2025. *Surveyed 2026-09-26* (§9y) |
| The subtraction that removes the overlap is the Department of State's whole total, and the trigger has to be evidence of the overlap and not a date | Taking the Department of State's whole Nigeria HIV total away from the US Agency for International Development's gives 147,968,316 dollars at FY2025 against the API's 148,110,451, low by 142,135, and −195,499 at FY2026 against the API's −195,440, low by 59, reproducing the sign of a negative year as well as the size. Applied before FY2025 the same subtraction would delete money that belongs to the Department of State, because the whole of that agency's pre-transition Nigeria HIV money is one redacted activity, `US-GOV-11-47198`, that the US Agency for International Development does not publish. The evidence that fires the trigger is a Department of State activity whose award number the US Agency for International Development also publishes in the same fiscal year, which happens in FY2025 and FY2026 and in no earlier year. *Surveyed 2026-09-27* (§9y) |
| Matching the two agencies award by award is impossible from the IATI files alone, because the Department of State redacts award numbers the API publishes | Department of State activity 227085 is award `AID-OAA-TO-15-00004` in the API, worth 668,384 dollars at FY2025 and 17,909,684 at FY2026, and activity 227702 is award `7200AA19CA00003`, worth −36,348 at FY2026, and the IATI identifiers `US-GOV-11-227085` and `US-GOV-11-227702` carry the activity number alone. Matching award by award therefore leaves 668,934 dollars unsubtracted at FY2025 and 17,873,277 at FY2026, against 142,135 and 59 for the whole-total subtraction. The API's own `activity_project_number` field supplies the redacted award numbers, so the gap is in the IATI file and not in the publisher's records. *Surveyed 2026-09-27* (§9y) |
| A transaction's `ref` is a per-publisher hash and cannot match an overlap across publishers | The Department of State's nine Nigeria disbursements on award 72062020CA00001 carry refs such as `01452CEC32A3` and the US Agency for International Development's 67 carry refs such as `9A8D9D1E4C75`, and none of the nine appears among the 67. *Surveyed 2026-09-26* (§9y) |
| The API carries negative disbursements, so a year's total can be below zero | Nigeria FY2026 HIV disbursements managed by the US Agency for International Development are minus 0.195 million, against 148.11 million at FY2025. *Surveyed 2026-09-26* (§9y) |
| The Millennium Challenge Corporation publishes on data.gov, not on S3, and data.gov refuses HEAD while serving GET | All 54 of the publisher's files carry `inventory.data.gov` URLs. Each answers 403 Forbidden to HEAD and 200 with the file to GET, the three probed returning `text/xml` at 969,181, 36,990 and 1,345,456 bytes. So a sizing pass built on HEAD records the publisher as entirely closed when the publisher is entirely open. The same domain's catalogue API at `catalog.data.gov` answers 404 to both documented paths. *Surveyed 2026-09-26* (§9y) |
| A registry package title does not classify a file, and within one publisher the same kind of file carries four different titles | The US Agency for International Development registers country files under two-letter codes, `usaid-ng`, and Multiple Countries files as `usaid-multiple-1`, `usaid-multiple-countries-16`, `usaid-multiplecountries33` and, for eight of the 34, as a bare number from `usaid-19` to `usaid-29` that sits beside the genuine region codes `usaid-89` and `usaid-289`. `usaid-19` is served as `iati-activities-Multiple+Countries-19.xml`, and those eight hold 296.2 of the 1,250.7 megabytes. The Department of State, Health and Human Services and the Department of Defense register country files under country names, `state-afghanistan`, one of the Department of State's 207 breaking the pattern as `dos-grenada`, and name the unusable files `state-worldwide-1` where the US Agency for International Development names the same thing `usaid-998-1`. *Surveyed 2026-09-26* (§9y) |
| An IATI country file carries only its own recipient country, so the files a country reconciliation must read are the country file, the Multiple Countries files and nothing else | Eight of the US Agency for International Development's other country files, Cameroon, Ghana, Kenya, Mozambique, South Africa, Tanzania, Uganda and Zambia, together holding 5,814 activities, contain zero Nigeria HIV disbursements. That publisher's 14 region files, two Worldwide files and one organisation file also contain zero, and the organisation file carries no activity at all, its root element being `iati-organisations`. So a connector reconciling one country reads that country's file plus every Multiple Countries file, and can skip the other 156 country files, the region files, the Worldwide files and the organisation file without losing a dollar. The US Agency for International Development's 208 files are 157 country, 34 Multiple Countries, 14 region, two Worldwide and one organisation. *Surveyed 2026-09-27* (§9y) |
| Health and Human Services publishes exactly one Multiple Countries file, and that one file is the difference between a broken and an exact reconciliation | Reading only the Nigeria country file leaves Health and Human Services short by 27,038 to 839,734 dollars at FY2021 to FY2024 and almost empty at FY2018 to FY2020. Adding `iati-activities-Multiple Countries.xml`, 34.32 megabytes, reproduces the API to the dollar in all 14 years from FY2012 to FY2025. The country file and the Multiple Countries file keep 573 and 87 transactions across 34 and 11 activities and share no activity identifier, so the two are added without deduplication between them. *Surveyed 2026-09-27* (§9y) |
| The US Agency for International Development's IATI files carry a smaller figure than the API before FY2020, and no unread file and no parsing rule accounts for the difference | Every file of that publisher that could hold Nigeria money was read, 156 other country files ruled out by the partition rule above, all 34 Multiple Countries files, all 14 region files, both Worldwide files and the organisation file, and the shortfall stands. Four candidate causes were tested and all four fail. Falling back to activity-level `recipient-country` and `sector` changes no figure, because all 4,896 kept transactions carry both elements on the transaction. No kept transaction carries a `currency` attribute. Every kept transaction carries exactly two `sector` elements and no `sector` or `recipient-country` element anywhere carries a `percentage`, so the API is not apportioning a value the file reports whole. The selection rule is sound, because it reproduces FY2020 to FY2024 within 173 dollars. The FY2013 shortfall of 4,044,658 dollars splits into 2,213,871 of operating and administrative money and 1,830,787 of programme money, and the operating half is visibly a different booking of the same spending, the API carrying 2,302,058 dollars under "Administrative Costs" where the files carry 33,477 and 1,732,034 under "Administrative Costs (ICASS)" where the files carry nothing, while the files carry 1,225,023 under "USAID Travel and Transportation" where the API carries 244,903. *Surveyed 2026-09-27* (§9y) |
| Neither award number nor activity title joins the FA.gov API to the IATI files for older years | At FY2013 the API reports 42 award numbers for Nigeria HIV disbursements managed by the US Agency for International Development and the files report 82 activity identifiers, because the API groups small payments under operating-unit codes such as `3.1.1`, `(none)` and `redacted ID` while the files give each payment voucher its own identifier such as `720201351529`. Titles drift too, the API carrying 70,659,156 dollars under "Strengthening Integrated Delivery of HIV/AIDS Services (SIDHAS)" against 70,659,155 in the files under "Strengthen Integrated Delivery of HIV/AIDS Services (SIDHAS)". Where a title does match the two sources differ by one to five dollars on about a dozen awards, which is rounding to whole dollars. So a reconciliation between the two sources can be checked at the year level and not at the award level. *Surveyed 2026-09-27* (§9y) |
| The FA.gov Data API returns its records under the key `data` and not `rows`, and honours `per_page` only between 10 and 1,000 | A response body is `{"data":[...],"page_info":{"current_page","per_page","total_pages","total_records"}}`. Reading `rows` returns undefined and yields an empty result that looks like a successful query with no matches, which is the most dangerous failure shape the API offers. `per_page=5` is silently raised to 10 and `per_page=5000` silently lowered to 1,000, in both cases with the effective value reported back in `page_info.per_page`, so a client must read the echoed value and not assume the requested one. *Surveyed 2026-09-27* (§9y) |
| The whole US corpus is three gigabytes, so excluding the publishers that carry no HIV money saves a tenth of the download | The 13 US publishers that have never disbursed a dollar of HIV money hold 306.8 megabytes over 1,138 files, and the eight that have hold 2,691.7 megabytes over 902 files, so all 21 US publishers together are 2,998.5 megabytes over 2,040 files. Excluding the 13 saves 10.2 per cent of the bytes. Largest of the 13 are the Department of the Treasury at 79.6 megabytes, the Department of the Interior at 35.2 and the Inter-American Foundation at 26.6, and smallest is the International Development Finance Corporation at 0.3. The 13 average 0.27 megabytes a file against 2.98 for the eight, so reading the 13 costs request count and not bytes. The Millennium Challenge Corporation's 54 files, 101.4 megabytes, are inside the 2,691.7 and were sized on this pass by GET after HEAD was refused, which closes the one publisher the 26 September sizing could not measure. *Surveyed 2026-09-27* (§9y) |
| A quarter of the registry's US resource URLs carry literal spaces, and a standard client rejects such a URL before it contacts the host | 274 of the 1,139 resource URLs the IATI Registry gives for the 13 US publishers without HIV money carry unencoded spaces, for example `https://iati-reporting.s3.amazonaws.com/department_of_agriculture/xml/iati-activities-Antigua and Barbuda.xml`. Python's `urllib` raises `InvalidURL` on such a URL and never makes a request, so a sizing pass built on the registry URL as published reported all 274 files as unreachable when 272 of the 274 are open. Percent-encoding the path with `urllib.parse.quote` fetches all 272. **A plain `quote` is not the right encoder, corrected 2026-09-27.** Registry paths also carry literal plus signs, 63 of these same 1,139 URLs and at least three of the US Agency for International Development's, and `quote` turns a plus into `%2B`, which Amazon S3 answers 403 because S3 reads a plus in a key as a space. The encoder that fetches both classes is `urllib.parse.quote(path, safe='/+')`, which leaves the plus and encodes the space. `iati-activities-Caribbean+Region.xml`, `iati-activities-Eastern+and+Central+Africa+Regio.xml` and the joint State and USAID organisation file all answer 403 under a plain `quote` and 200 under the corrected one. A connector has to encode the path of every registry URL before use, has to keep the plus out of the encoding, and has to distinguish a client-side rejection from a closed file, because a client-side rejection looks identical to a refusal in a log. *Surveyed 2026-09-27* (§9y) |
| The registry publishes URLs that no encoding repairs, and publishes one file twice under two packages | Two of the 1,139 resource URLs still answer 403 after the path is percent-encoded. The Department of the Interior's `iati-activities- Middle+East+and+regional.xml` carries a stray space after the hyphen and plus signs where sibling URLs from the same publisher carry spaces, and the Department of Justice's `iati-activities-chinarepublicoftaiwan` carries no `.xml` extension. Two Department of Transportation packages publish one identical resource URL, so 1,139 registered resources are 1,138 distinct files. A connector has to log a bad URL and carry on. Neither the Department of the Interior nor the Department of Justice carries HIV money, so no panel value turns on either file. *Surveyed 2026-09-27* (§9y) |
| Registry package counts move between surveys and disagree with the packages the registry returns | The 21 US publishers register 2,038 packages on 27 September 2026 against the 2,138 counted on 26 September 2026, and this survey cannot tell whether the registry changed or the earlier count was taken on a different basis. Within one survey `package_search` returns more packages than `package_count` advertises, 126 against 125 for the Department of the Interior and 121 against 120 for the Department of Justice. A connector cannot treat `package_count` as the number of files to expect and has to page `package_search` until the returned result count is reached. *Surveyed 2026-09-27* (§9y) |
| USAID's S3 files are a month older than the other agencies' and some are empty | USAID files answer Last-Modified 3 August 2026, State 5 September 2026 and Health and Human Services 4 September 2026. USAID Grenada is 0 bytes. The FA.gov site states data last updated 31 August 2026. *Surveyed 2026-09-23* (§9y) |
| Throughput from S3 to this machine varies by more than two orders of magnitude between fetches | Single fetches of whole files ran at 4,175,629 bytes a second for a 23.1 megabyte State file and 4,116,015 for a 16.3 megabyte USAID file, and a fetch of a 40.9 megabyte State file started minutes later held about 21,000 bytes a second over six and a half minutes. Nothing in the survey explains the difference, so a run has to be written to tolerate the slow case and a download budget cannot be set from a single measurement. A sequential download of the US Agency for International Development's 34 Multiple Countries files, 1,250.7 megabytes with one fetch running at a time and no competition from this machine, ran at a median of 3.33 megabytes a second with a minimum of 0.15 and a maximum of 6.87, and the seven fetches below one megabyte a second fell at positions 1, 7, 8, 12, 14, 17 and 20 of the 34. So the slow case is not a cold first connection and recurs throughout a run. **This row replaces a claim recorded on 23 September 2026 of 3,893 bytes a second, which was measured while several of the survey's own parallel fetches were competing for the same link and is wrong by three orders of magnitude.** *Surveyed 2026-09-23, corrected 2026-09-26, extended 2026-09-27* (§9y) |
| data.gov's catalogue API is unreachable, so a data.gov mirror of the FA.gov file stays unchecked | `catalog.data.gov/api/3/action/package_search` and `catalog.data.gov/api/action/package_search` both answer 404 with the body `{"detail":{},"message":"Not Found"}`. *Surveyed 2026-09-23* (§9y) |
| The IATI files carry no managing sub-agency, so the route change costs the panel its CDC series | `hhs_nigeria.xml` names Health and Human Services three times and never names CDC. `reporting-org ref` is `US-GOV-14`, and `participating-org` roles 2 and 3 both give `US-GOV-14` with the narrative "Department of Health and Human Services". The only CDC string anywhere in the file is inside the ForeignAssistance.gov-namespace `treasury-account` element, code `75x0943`, narrative "Centers for Disease Control, Disease Control, Research, and Training", which names the appropriation the money came from and is therefore the funding basis the connector rejects on principle, PEPFAR being appropriated to the Department of State. The hand-downloaded CSV carries a "Managing Sub-agency or Bureau Acronym" column and the XML carries no equivalent, so the S3 route supports managing agency at department level only. `external_hiv_oda_us_cdc` therefore becomes `external_hiv_oda_us_hhs` and NIH and HRSA move out of `external_hiv_oda_us_other_agency`. CDC is 38.5 billion dollars of the department's 43.1 billion, so the replacement series is close to the old one and is not the same measurement. *Surveyed 2026-09-27* (§9y) |
| The one unreadable file in the corpus is not malformed XML at all, because the IATI Registry hands out an AWS console page in place of the file | The full corpus run of 27 September 2026 hit `iati-activities-Africa_North_of_Sahara.xml` with `mismatched tag: line 2, column 45`, so `ET.iterparse` abandoned the file and whatever the file reports is absent from the totals. The warning named the file and not the publisher, and several US publishers use the same regional file names, so the log gave no way to tell which agency's money went missing. `_parse_file` now takes the publisher slug and names it, and the parse summary counts unreadable files. The rerun the same day printed `dod/iati-activities-Africa_North_of_Sahara.xml`, so the owner is Defense. The cause is the registry and not the publication. The registry gives that one resource the URL `https://us-east-1.console.aws.amazon.com/s3/object/iati-reporting?region=us-east-1&prefix=department_of_defense/xml/iati-activities-Africa+North+of+Sahara.xml`, which is the S3 console web page and not the object, so the connector downloaded 1,158 bytes of HTML beginning `<!DOCTYPE html>` and a redirect script. The manifest record for that file is also the only one of 2,015 carrying no ETag. The real file exists and a HEAD on `https://iati-reporting.s3.us-east-1.amazonaws.com/department_of_defense/xml/iati-activities-Africa%20North%20of%20Sahara.xml` answers 200, last modified 4 September 2026, so rewriting a console URL to the object URL would recover the file. Defense sits in `external_hiv_oda_us_other_agency`, which takes the frozen extract of the Complete Data Set in every year because `PROVEN_WINDOW` holds no entry for that bucket, so the unreadable file costs the panel nothing today and would matter only if Defense were ever brought inside a proven window. **The rewrite was built on 27 September 2026.** `object_url` turns a console link whose path reads `/s3/object/<bucket>` into `https://<bucket>.s3.<region>.amazonaws.com/<key>`, taking the bucket from the path and the key and the region from the query string, and returns every other URL untouched, including a console link to a folder listing, which uses `/s3/buckets/<bucket>` and names no single object. A query string reads a plus sign as a space, so the key comes back with real spaces and `encode_url` quotes those spaces as %20, which is the form the HEAD above proved. The cache filename does not move, because `_cache_path` replaces a space and a plus alike with an underscore, so the rewritten address overwrites the console HTML already sitting at `dod/iati-activities-Africa_North_of_Sahara.xml` instead of opening a second file beside it. A GET on the rewritten address answers 200 with content type `application/xml`, an ETag of `"e72dc3c1d0ff653c14b1fcaf2595caf2"` and 5,162 bytes that parse into one activity, `US-GOV-7-314363`, holding one disbursement of 97,297 USD dated 3 April 2020 against country code 189. `_is_hiv` rejects that disbursement, so recovering the file removes the corpus's one parse failure and adds no money to any series. A read-only sweep of all 21 US publishers the same day found this resource to be the only console link among 2,041 registered resources. The rerun the same day proves the rewrite in the panel, reporting one file fetched, which is the rewritten Defense address, and giving up on zero files not readable as XML against one before the fix, with the panel unchanged at 209,872 rows because the recovered file carries no HIV money. *Surveyed 2026-09-27* (§9y) |
| Five US publishers have not rewritten their IATI files since March 2022, and none of the five carries HIV money | The full corpus run of 27 September 2026 read Last-Modified on every file. USAID and the Department of State answered 25 June 2026, the Millennium Challenge Corporation 13 May 2026 and most others 24 June 2026, but Homeland Security, Commerce, Justice, Transportation and the Federal Trade Commission all answered 29 March 2022. A publisher that stops reporting still serves its files, so a date is the only symptom, and the cost is nothing today only because none of the five has ever disbursed HIV money. *Surveyed 2026-09-27* (§9y) |
| The whole US corpus is 2,723 megabytes over 2,015 files once the Worldwide files are skipped | The 21 US government publishers registered 2,041 resources on 27 September 2026, of which 20 are named Worldwide and skipped. Five of the remaining 2,021 fail to download, all five the 403 files no encoding repairs. A sixth, `dol/iati-activities-Paraguay.xml`, failed on the first run with a connection error and downloaded on the rerun the same day, so a single failed download is not evidence that a file is unreachable. The remaining 2,016 downloads land in 2,015 files, because two Transportation resources carry the same URL and so resolve to one filename, which is the registry defect recorded in the row below. Discovery drops that duplicate registration from 27 September 2026, so the count of downloads and the count of files agree from the next run onwards, and a read-only sweep the same day produced 2,020 jobs out of 2,041 resources after skipping 20 Worldwide files and dropping the one repeat. On disk USAID is 1,746 megabytes, the Department of State 370, the Millennium Challenge Corporation 98, the Peace Corps 78, Defense 74, Treasury 60 and Health and Human Services 58. The earlier figure of 2,691.7 megabytes covered only the eight publishers that carry HIV money. *Surveyed 2026-09-27* (§9y) |
| ForeignAssistance.gov subtracts the State figure from the USAID figure whatever the sign, and a guard that skipped a negative State figure broke the country total | The USAID XML file reports State's transactions as well as USAID's, so the API's USAID figure equals the USAID file's raw total less the State file's total. A guard added on 27 September 2026 skipped that subtraction where the State country-year netted below zero, on the reasoning that a negative State figure is a year of recoveries and not an award reported twice. The frozen extract of the Complete Data Set shows the reasoning is wrong. Papua New Guinea FY2025 gives raw USAID minus 7,782 less State minus 2,494,928 for 2,487,146 against the API's 2,487,154, Nepal 6,972,368 against 6,972,374 and Indonesia 6,639,936 against 6,639,952, all three within 16 dollars. Skipping the subtraction leaves State's money in the USAID series as well as the State series and moves the country total by the whole State amount, and Papua New Guinea's four agency series sum to minus 2,403,586 with the guard against the API's 91,350. The guard was removed the same day, together with a floor at zero that had fired on none of the 48 adjusted country-years. Two of the four affected country-years, Indonesia and Vietnam, stayed inside the 2 per cent history tolerance and never appeared in the disagreement warning, so the tolerance does not catch a fault of this size. *Surveyed 2026-09-27* (§9y) |
| S3 honours a conditional GET on these files, and a rerun that reports no cache hits means the manifest was not read | A conditional GET on `dfc/iati-activities-Egypt.xml` carrying the stored ETag `"48ef61cd8b9cb44f52d9c997fa824974"` answered 304 with the same ETag, so the ETag cache works against this bucket. The rerun of 27 September 2026 nonetheless re-fetched all 2,015 files, every manifest record reading `fetched` and every file rewritten, and why the first run's manifest was not on disk at the start of the rerun is not established. A reporting defect hid the re-download, because a cached record is built from the previous run's record and keeps that record's `bytes` field, so the progress line counted a cache hit as a fetch and printed the same 2,833 megabytes either way. The counter now counts only fetched files and prints the cached count alongside. The third run the same day settles the question. That run reported `1 fetched for 0 MB at 0.0 MB/s, 2015 served from cache` and finished the download stage in 295 seconds, so the ETag cache works end to end and the corrected counter shows it. The one file counted as fetched is the Department of Defense console page, the only manifest record of 2,015 carrying no ETag, which cannot send a conditional request and so is re-downloaded on every run at 1,158 bytes, printing as 0 MB. The cached count of 2,015 exceeds the 2,014 remaining files because both Transportation jobs for the Uruguay URL read the same manifest record and both count as cache hits. Both causes of that arithmetic were removed later the same day. The console link is now rewritten to the object address, which returns a real ETag, so the Defense file joins the conditional cache after one more download and stops being re-fetched every run, and the duplicate Transportation registration is dropped at discovery, so no file is counted as a cache hit twice. The fourth run the same day confirms both removals, reporting `1 fetched for 0 MB at 0.0 MB/s, 2014 served from cache` over 301 seconds. One fetch plus 2,014 cache hits plus the five unchanged 403 failures account for all 2,020 jobs exactly, so no file is counted as a cache hit twice, and the one fetch is the Defense file taking its first real ETag, which should leave the fetched count at zero on the run after. *Surveyed 2026-09-27* (§9y) |
| The IATI Registry misdirects two US resources, and the connector cannot tell a repeated filename from a repeated file | The Department of Transportation registers 102 resources, of which the package `dot-ecuador` and the package `dot-uruguay` both give the URL `https://iati-reporting.s3.amazonaws.com/department_of_transportation/xml/iati-activities-Uruguay.xml`, so 101 jobs after the Worldwide skip produce 99 files and Transportation's Ecuador file is never requested. The Ecuador file exists, and a HEAD on the predictable object URL answers 200, last modified 4 September 2026, so the loss is the registry's entry and not the publication. Corpus-wide arithmetic shows this is the only collision, because 2,021 jobs less five failures give 2,016 successes against 2,015 files on disk. The connector builds `jobs` from the resource list with no check that a publisher has claimed a filename twice, so two resources with different URLs and one basename would overwrite each other silently and the count would still look right. Transportation carries no HIV money, so nothing in the panel moves, and the defect is recorded because a collision inside USAID, State or Health and Human Services would cost real money without a warning. **The check was built on 27 September 2026 and separates the two cases a repeated filename can mean.** A second resource carrying the same filename and the same URL is a duplicate registration, which the Transportation Uruguay package is, and discovery drops the repeat and counts it, so the job list stops asking for one file twice and the cached count stops exceeding the number of files. A second resource carrying the same filename and a different URL is two files fighting over one cache path, and discovery logs a warning naming the publisher, the filename and both URLs, then stores the second under a name made distinct by eight characters of the digest of its URL, so both files are read, neither is lost and a rerun still serves both from cache. A read-only sweep of all 21 US publishers the same day found one duplicate registration and no genuine collision across 2,041 registered resources, so the warning guards against a defect that no publisher commits today. Discovery now yields 2,020 jobs, which is 2,041 registered resources less 20 Worldwide files and less the one repeat, and the rerun of 27 September 2026 turned those 2,020 jobs into 2,015 files because five fail with 403. The gap between 2,020 and 2,015 is those five failures and not growth in the registry, which held 2,041 resources before the fix and 2,041 after. Transportation's Ecuador file stays missing, because the registry never gives its address and guessing an address the registry does not publish is not something the connector should do. *Surveyed 2026-09-27* (§9y) |
| The S3 route reproduces ForeignAssistance.gov in Nigeria and does not generalise to every country | Inside the windows the Nigeria reconciliation proved, 14 country-years still differ from the frozen extract of the Complete Data Set by more than 2 per cent, and two of the 14 are runs of consecutive years rather than single-year noise. Trinidad and Tobago's Health and Human Services figure is short in all five years FY2021 to FY2025 by 243,021, 869,625, 522,051, 790,746 and 1,113,132 dollars, and FY2022 changes sign, minus 197,947 on S3 against 671,678 in the extract. Nicaragua's USAID figure is short in FY2020, FY2021 and FY2022 by 1,007,067, 398,932 and 659,280 dollars. The other six are single years, the largest Uganda FY2024 USAID at 3,434,752 dollars high, then Ethiopia FY2020, Ukraine FY2020, Mali FY2020, Jordan FY2020 and Djibouti FY2023. `PROVEN_WINDOW` was measured on Nigeria alone and these two clusters are the evidence that one country does not settle it. **Two answers were built on 27 September 2026.** Every panel row a disagreement touches now carries the disagreement, because a log line is read once by whoever ran the connector and the panel is read later by Adrian and by anyone who takes the CSV. The agency row carries `history_disagreement`, the figure read from the S3 files, the extract's figure, the relative gap between the two and a note saying which of the two sources is right is not settled. The country total row carries the same flag and names the agency buckets behind it, because the total is the four buckets added up and a reader who takes only the total would otherwise never see the warning. Second, `scripts/reconcile_fa_country.py` reads one country out of the cached XML using the connector's own sector test, country resolution, fiscal year, deduplication key and State subtraction, and prints that figure beside the extract's for every fiscal year and agency, then breaks every disagreeing agency-year down by file and by activity so a difference can be traced to a publisher's own record. The script writes nothing and needs no network, because the frozen extract is ForeignAssistance.gov's own output and comparing against the extract compares against the API without sending a request to a site that refuses Python. Nigeria is the control and Nicaragua and Trinidad and Tobago are the targets, which is the first test of the agency buckets against a country that is not Nigeria. What the extract cannot settle is whether ForeignAssistance.gov has restated any of these figures since the extract was taken on 18 July 2026, and answering that needs the Data API read in a browser. **Jason ran all three reconciliations on 27 September 2026 and the answer is in.** Nigeria agrees in 32 of 32 proven agency-years out of 5,636 kept disbursements with no duplicate dropped, and the script found no bucket-year to break down, so the script reproduces by a second route the answer the Nigeria reconciliation had already reached. Nicaragua's fault is USAID alone, with every Health and Human Services year from FY2012 to FY2025 agreeing to the dollar, and the USAID shortfall runs FY2013 to FY2022 and closes at FY2023, where the whole remaining difference is 6 dollars, 8 dollars and 3 dollars in the last three years. Nicaragua's worst two years are FY2018 at minus 47.8 per cent and FY2019 at minus 77.5 per cent and both sit outside the USAID window, so neither reached the disagreement log, which means the 14 understate the departure because the warning can only fire where the connector already trusts the S3 figure. Trinidad and Tobago's fault is Health and Human Services alone, with both USAID years agreeing exactly, and every Trinidad and Tobago disbursement Health and Human Services publishes comes from the single file `hhs/iati-activities-Multiple_Countries.xml`, because Health and Human Services publishes no Trinidad and Tobago country file. Trinidad and Tobago agrees exactly in FY2020 at 310,859 dollars and then falls short in all five years after. **Three explanations were tested against the cache and all three are ruled out.** Removing the HIV test altogether still leaves Trinidad and Tobago short in FY2022 to FY2025, and a scan of every HIV-mentioning sector label in the corpus found no variant an exact-equality test could miss, so the fault is not the HIV test. Splitting into positive and negative disbursements leaves the positives alone short in every year from FY2021, so the fault is not the sign. No transaction anywhere in the corpus names more than one country. **What fits every measurement, without being proved, is that ForeignAssistance.gov attributes to a named country money the XML leaves in an unspecified pot.** USAID books between 220,847,404 and 1,030,501,650 dollars of HIV disbursements a year to `recipient-region` code 998 with no recipient country, and Health and Human Services books between 24,925,243 and 289,837,018 dollars a year to `recipient-country` code 998. Both the connector and `extract_fa_history.py` drop both pots, and the Complete Data Set behind the extract carries ForeignAssistance.gov's own benefiting-country attribution for the same money. The shape of the panel fits, because the countries that disagree are small ones served through regional awards while countries with large dedicated bilateral programmes agree closely. Proving the explanation needs ForeignAssistance.gov's activity-level detail read in a browser, because the frozen extract is aggregated to country, fiscal year and agency. Why Nicaragua's gap closes at FY2023 is not explained, and the unspecified pot is still 685,799,286 dollars in FY2023, so the pot does not empty when the gap closes. **The exposure across the whole panel was measured and the route is broadly sound.** Of 1,367 agency-years the connector takes from the S3 files, 1,220 agree with the extract to within 0.01 per cent, 27 fall between 0.01 and 0.2 per cent, 12 between 0.2 and 0.5 per cent, 23 between 0.5 and 2 per cent, and 14 exceed 2 per cent. The band between 0.5 and 2 per cent is almost entirely large PEPFAR countries, Uganda, Tanzania, South Africa, Ethiopia and the Democratic Republic of the Congo among them, at the size a restatement would produce. *Surveyed 2026-09-27, reconciled 2026-09-27* (§9y) |
| The panel credits Tuvalu with United States HIV money, because a fallback between two country-code systems reads ForeignAssistance.gov's numeric country codes as UN M49 numbers | Measuring the exposure at §9y turned up 71 agency-years where the S3 files carry money the frozen extract has no row for at all, and seven of the largest belong to Tuvalu, a Pacific state of about 11,000 people. Tuvalu carries Health and Human Services HIV money in nine fiscal years from FY2013 to FY2021, and the seven years FY2014 to FY2020 run between 5,825,511 and 12,414,715 dollars each, with FY2013 at 53,291 dollars and FY2021 at 34,975. Tuvalu receives no United States HIV money and ForeignAssistance.gov reports none. The cause was line 764 of `hivimpact/connectors/foreign_assistance.py`, which read `iso3 = code_to_iso3(codes[0]) or to_iso3(codes[0])`. Health and Human Services publishes `recipient-country code="798"`, a numeric code from ForeignAssistance.gov's own country list. `code_to_iso3` does not recognise 798 and returns nothing, and the fallback to `to_iso3` resolves 798 through pycountry, where 798 is the UN M49 numeric code for Tuvalu. The fallback exists so that an alphabetic code or a country name `code_to_iso3` does not hold still resolves, and on a numeric code the fallback silently reinterprets the code under a different code system. The corpus holds 244 distinct recipient-country codes, 22 of them numeric, and exactly two of the 22 collide with a UN M49 number, 798 becoming Tuvalu and 498 becoming Moldova. The other 20 numeric codes, among them 998, 1000, 1031 and the regional codes ending in 89, resolve to nothing and are correctly dropped. The contamination is 65,363,976 dollars into Tuvalu `hhs` over 51 transactions, 577,611 into Tuvalu `other_agency` over 10 transactions, 10,000 into Tuvalu `state`, and 45,204 plus 308 into Moldova, so 65,997,099 dollars in all. Every Tuvalu figure in the panel is fabricated, and of the Moldova money the S3 files supply, 119,794 dollars in FY2014, FY2016 and FY2017 carry the alphabetic code `MD` while the whole of FY2024 at 45,204 dollars and the whole of FY2022 at 308 dollars are fabricated. The defect is confined to the one connector, because `world_bank` and `oecd_crs` call `code_to_iso3` with no fallback, `unaids_gam_expenditure` and `who_ghed` pass a code to `code_to_iso3` and a name to `to_iso3`, and `extract_fa_history.py` falls back on the country name and not on the country code, which is why the frozen extract has no Tuvalu row and is right. Jason approved the fix on 27 September 2026 and the fix is written. The fallback now lives in a module-level function `resolve_country`, which tries `code_to_iso3` first, returns nothing when the code is all digits, and falls back to `to_iso3` only for a code that is not all digits, so an unrecognised numeric code joins 998 in the no-country bucket. A dropped numeric code is counted under a new `numeric_code` counter and a new log line names every all-digit code the run dropped with the number of transactions each code carried, so a publisher moving to a new numbering is visible and not silent. `scripts/reconcile_fa_country.py` and `scripts/check_fa_dedup.py` call the same helper instead of copying the line. An offline check returns nothing for 798, 498, 998, 289, 789, 380, 619 and 1000, and still returns `MDA` for `MD` and `TUV` for `TV`, so a publisher that ever reports real Tuvalu money under the alphabetic code would keep the money. Jason reran the connector the same day and the fix is in the panel. The log line named 798 (62 transactions) and 498 (3) among 13 all-digit codes carrying 2,559 dropped transactions in all, the connector emitted 5,994 rows over 125 countries against 6,026 over 126 before, and the panel fell from 209,872 rows to 209,840. A row-by-row comparison against the previous panel shows 32 rows removed, no row added and no surviving row changed in value, the 32 being Tuvalu's 28 `foreign_assistance` rows and Moldova's four rows for FY2022 and FY2024. Tuvalu stays in the panel on the 163 rows `unaids_aidsinfo`, `world_bank`, `who_tme`, `who_gho` and `oecd_crs` supply, and Moldova keeps 12 `foreign_assistance` rows worth 2,622,795 dollars. *Surveyed and fixed 2026-09-27* (§9z) |
| The panel under-counts Sudan, because Health and Human Services publishes Sudan under the country code `SF`, which is neither an ISO code nor anything pycountry holds | Sizing what the numeric-code fix at §9z left behind found that the run of 27 September 2026 dropped 2,583 transactions as naming no country, of which 2,559 carried an all-digit code, leaving 24 HIV disbursements dropped on a code that is not all digits. A read-only scan of the cached corpus found exactly three codes that are not all digits and that `resolve_country` cannot resolve, being `XK`, `SF` and `YU`. `XK` is the user-assigned code for Kosovo, appears 13,344 times across 15 agencies, led by the US Agency for International Development on 8,478 and the Department of State on 3,549, and carries the narrative `Kosovo` in 376 appearances, yet `XK` carries no HIV money at all, zero transactions and zero dollars, because every Kosovo activity fails the connector's HIV test. The panel already holds Kosovo as `XKX`. `YU` is withdrawn Yugoslavia, appears three times, all from the Department of Defense, and carries two HIV disbursements worth 25,639 dollars in 2012 and 2014, and because `YU` covers territory that is now six countries the code cannot be assigned and dropping the money is correct. `SF` carries the rest, being 22 HIV disbursements worth 8,903,002 dollars, every one published by Health and Human Services, running 4,495,465 dollars in 2012, 2,454,887 in 2013, 978,399 in 2014, 276,045 in 2015, 253,107 in 2016, 227,852 in 2017 and 217,247 in 2018. Every one of the 22 carries treasury account `19x1030`, the Department of State Global HIV/AIDs Initiative, and sector `13040`, STD control including HIV/AIDS, so the money is PEPFAR money. Two independent readings identify `SF` as Sudan. Health and Human Services orders the recipient-country blocks inside an activity alphabetically by country name, and activity `US-GOV-14-43311` runs `ZA`, `ZW`, `SS`, `SD`, `SZ`, `TJ` where the PEPFAR activity `US-GOV-14-47141` runs `ZA`, `ZW`, `SS`, `SF`, `SZ`, `TJ`, so `SF` occupies the slot `SD` occupies in the sibling activity, between South Sudan and Swaziland, which alphabetically is Sudan. Separately, `state/iati-activities-Sudan.xml` holds only `SD` and `SF`, and activity `US-GOV-11-SSJTIP21GR3024-89567`, titled Identifying and Protecting VoTs in Sudan, codes all 12 of its transactions `SF` and none `SD`. South Africa and South Sudan were both tested and ruled out, because the same Health and Human Services file already uses `ZA` 870 times and `SS` 488 times. The frozen extract cannot arbitrate, because `data/raw/foreign_assistance/history_fa_gov.csv` holds no `SDN` row at all, the same way the frozen extract holds no Kosovo row. The panel already holds Sudan on eight `foreign_assistance` rows covering 2013, 2014, 2015 and 2019, so accepting `SF` would change four existing Sudan values and add the years 2012, 2016, 2017 and 2018, and would add no country. The under-count predates the fix at §9z and is not a regression, because all three codes are alphabetic and took the same route before that fix as after. The fix is designed and not written and awaits Jason's decision, and the design is a connector-local alias map holding the single entry `SF` to `SDN`, consulted inside `resolve_country` after `code_to_iso3` and before the `to_iso3` fallback, kept out of `hivimpact/normalize.py` because `SF` is the FIPS code for South Africa and a global alias would mislabel South African money the moment another source uses the FIPS list, together with a second log line naming every dropped code that is not all digits. *Surveyed 2026-09-27* (§9aa) |
| Rule 17(g) removed the UNAIDS Secretariat from the panel completely, because one of the 42 funders the UNAIDS Secretariat names is an excluded funder | The connector's rule 17(g) excluded any activity naming the Global Fund or a United States government agency as a role-1 funder, so that money already counted under the Global Fund's own series does not enter the panel a second time through a body spending the money on the Global Fund's behalf. The UN Development Programme is the publisher rule 17(g) was written for, and the UN Development Programme names the Global Fund alone on 63 of the 73 UN Development Programme activities rule 17(g) excluded. The UNAIDS Secretariat filed 1,228 activities under purpose 13040, every one of the 1,228 names 42 role-1 funders at once, and the United States sits among the 42 every time, so the whole of the UNAIDS Secretariat's multi-donor core money left the panel on one contributor out of 42. Measuring rule 17(g) across every publisher found 2,140 activities excluded and only 109 of the 2,140 naming an excluded funder alone. The narrowed rule excludes an activity only where every named role-1 funder is an excluded funder, and the run of 29 September 2026 kept 2,005 activities under the narrowed rule, being the World Health Organization 517, the UNAIDS Secretariat 1,228, UNICEF 250 and the UN Development Programme 10, with the connector logging `_PASSTHROUGH_MODE` as `sole`. The UNAIDS Secretariat moved from nothing to 1,228 activities and 4,696 transactions. Every activity kept under the narrowed rule carries three keys naming the pass-through funder and the money standing behind the pass-through funder, so a reader can remove the kept money without a rerun. *Surveyed 2026-09-30* (§9ab) |
| The Swiss Agency for Development and Cooperation's numeric recipient codes are OECD DAC recipient codes and not a private encoding, and looking for the published list changed what the repair had to be | The Swiss Agency for Development and Cooperation files numeric recipient codes where the IATI standard requires an ISO 3166-1 alpha-2 code, and the connector refused all eight codes and logged the money standing behind each of the eight. All eight numbers match the OECD DAC recipient codelist exactly, French labels included, five of the eight being countries and three being regional or unspecified codes. The eight codes therefore entered the connector as DAC recipient codes with a citable source, the three regional codes now reach the region pool instead of being refused, and a reader can check every entry against the codelist, which a table justified by the connector author's reading of the French narrative could not have allowed. The table is keyed on the exact code string and never on the French narrative sitting beside the code, because resolving a country by name is what once made the United Kingdom the largest recipient of American HIV aid at 59.9 billion USD. *Surveyed 2026-09-30* (§9ab) |
| The Global Fund accumulator's default of zero wrote 424 country-years into the panel as a disbursement of zero where the connector had measured nothing | The Global Fund totals live in a `defaultdict(float)`, and the branch for a grant that is not an HIV or HIV-and-tuberculosis grant adds that grant's purpose-13040 share, which is zero when the grant carries no purpose-13040 money, so a country-year in which the Global Fund moved only malaria or tuberculosis money created a key in the accumulator and reached the panel as a row of value zero. A zero in a disbursement series states that the funder disbursed nothing, and for Zimbabwe in 2019 the statement is false, because the OECD Creditor Reporting System records 122,147,155 USD for Zimbabwe in 2019 and the connector had seen no HIV-coded Global Fund transaction. The run carrying the defect wrote 424 zero-valued rows out of 2,148, and OECD CRS reports 5,097,904,760 USD against 265 of the 424. Dropping the 424 rows instead would have emptied the Global Fund series for nine countries, which hides a funder's presence in a country instead of reporting a year the connector could not measure, so the repair keeps the row with no value, a stated reason and the grant identifiers seen, which `hivimpact/schema.py:60` provides for. The run of 29 September 2026 wrote 449 valueless country-years out of 2,140, with 4,450,922,895 USD of OECD CRS money standing against the 449 and no zero-valued Global Fund row anywhere in the panel. The rerun of 30 September 2026, carrying the paging repair and the apportionment repair recorded in the rows below, wrote 192 valueless country-years out of 2,577, and the OECD Creditor Reporting System holds no row at all for any of the 192, so every valueless country-year that the other reading of the same money could contradict has gone. 323 country-years moved from valueless to measured, carrying 4,992,006,610 USD, and Zimbabwe in 2019, the country-year the defect was found on, reads 122,147,153.25 USD against the OECD Creditor Reporting System's 122,147,155.00 USD. *Surveyed 2026-09-30* (§9ab) |
| A paged read of d-portal's query service returned a different subset of the same result on every run, and moved the Global Fund series by 1,387,699,426 USD between two runs of unchanged code | The connector paged d-portal's query service on `limit` and `offset` and asked for no ordering, and a relational engine given no ORDER BY may return rows in any order and in a different order on two executions of the same statement, so `LIMIT n OFFSET n` is not guaranteed to continue where `LIMIT n OFFSET 0` stopped. Two identical requests for 20,000 rows returned 20,000 rows each, of which 14,680 differed. Across two runs of identical code the Global Fund series moved by 1,387,699,426 USD, 101 country-years gained money naming grants the previous run never returned, 224 country-years lost money, and Rwanda lost every row. The connector's own comment recorded 20,000 as a measured per-page cap on the query service, and the recorded figure is wrong, because a limit of 200,000 was honoured and answered in 6.3 seconds and the largest query the connector sends, 326,852 rows, came back complete in about 40 seconds, so nothing was capping the response at 20,000 except the connector asking for 20,000. The publisher census was being shuffled as well, at 23,327 rows against a page of 20,000, so every run up to 29 September 2026 chose the connector's list of HIV publishers from a reshuffled result. The repair sends one request per query and raises when the returned count equals the limit, because a count equal to the limit is the one case where a single request loses rows without saying so. The rerun of 30 September 2026 measured what the paged read had been losing. The Global Fund series rose from 21,066,498,719 USD to 38,152,946,330 USD, a rise of 81.1 per cent, and because the apportionment repair recorded below changes no year before 2017, the rise of 63.54 per cent across 2000 to 2016 is the paging repair alone. Measured against a complete read carrying the old assignment, which totals 35,013,714,747 USD, the paged read had been losing 13,947,216,028 USD, about 40 per cent of the Global Fund series, on the one draw the run of 29 September 2026 happened to make. A shuffled paged read is therefore not a small loss around the edge of a series but can cost two fifths of the money, and the loss is invisible to any check that does not hold a complete read beside the paged one. *Surveyed 2026-09-30* (§9ab) |
| d-portal echoes the SQL d-portal built, and the echoed statement is the only oracle that separates an honoured parameter from an accepted and ignored one | d-portal returns a `dquery` field carrying the statement the parameters produced. The query service silently drops `groupby`, every aggregate function, `order_by`, `order`, `sort`, `sortby`, `trans_day_min`, `trans_day_max`, `year` and `trans_year`, and honours `orderby` on that one spelling alone at a cost of about 24 seconds on the largest query the connector sends. A dropped parameter changes neither the row count nor the response's error field, so a connector trusting `groupby` would have received ungrouped rows and summed the same money twice, and a connector partitioning on `trans_year` would have read the whole corpus into every partition. The parameters verified honoured are `orderby`, `trans_day_gteq`, `trans_day_lteq`, `trans_day_gt`, `trans_day_lt`, `aid`, `trans_country` and `trans_sector`, and `country_code` is honoured but adds `JOIN country USING (aid)` to the statement and so must not be used to partition a transaction query. *Surveyed 2026-09-30* (§9ab) |
| d-portal's `trans` table is apportioned before the connector ever reads the table, and the connector discarded one sector share of every transaction whose activity declares a purpose code twice | d-portal's `trans` table holds one row per transaction per sector row the activity declares, each row carrying the transaction's value times that sector's percentage, so `trans_usd` is a sector's share of a transaction and never a transaction. The connector stored each row as `groups[(aid, trans_id)][sector] = usd`, which is the right structure for apportioned data and the wrong operator, because an activity may declare the same purpose code twice at two different percentages and then one share overwrites the other. `47045-MWI-C-MOH-2` declares purpose 12263 at 4 per cent, 12110 at 7 per cent, 12110 again at 1 per cent and 13040 at 88 per cent, the four percentages sum to 100, and 7 divided by 1 is the ratio of exactly seven that appeared on every repeated key of that grant. Two explanations were falsified before the sector table answered the question, the first holding that a join fanned the result out, which failed because `from=trans` and `from=trans,act` both return 326,852 rows, and the second holding that d-portal serves each transaction both whole and apportioned, which failed because the largest row on a transaction equals the sum of the other rows on only 1.0 per cent of transactions. Accumulating instead of assigning raises the Global Fund HIV corpus from 35,013,714,747 USD to 38,152,946,330 USD, a rise of 3,139,231,583 USD or 8.97 per cent, and the rise is exactly zero for every year from 2002 to 2016 and runs from 0.3 per cent in 2017 to 26.1 per cent in 2023, because the Global Fund changed how the Global Fund codes grant sectors in 2018. The defect therefore manufactured a false downward step at 2018, the current series falling 28.7 per cent from 2017 to 2018 where the repaired series falls 20.2 per cent. An offline dry run on 30 September 2026 put the four real apportioned rows of `47045-MWI-C-MOH-2` through the repaired code and got a panel value of 718,060.70 USD, the whole transaction to the penny, with `extra.sector_12110_usd` at 57,444.86 USD holding both declared 12110 shares, against 667,796.45 USD under the old assignment, a loss of 50,264.25 USD which is exactly the 7 per cent share, because the 1 per cent row arrived last. The rerun of 30 September 2026 matched the per-year prediction to the dollar, the panel's Global Fund series equalling the predicted corpus figure in every year from 2,056,044,820 USD for 2017 to 764,307,152 USD for 2026 and 38,152,946,330 USD in total, and the panel's step down from 2017 to 2018 fell from 28.4 per cent to 20.2 per cent, which is the repaired prediction. The rise of 8.97 per cent is not what the panel moved by and must not be quoted as the size of the change, because 8.97 per cent compares two assignments over one complete read while the panel of 29 September 2026 also carried the paged read of the row above, and the panel rose 81.1 per cent. *Surveyed 2026-09-30* (§9ab) |
| The repaired Global Fund series rests on two properties d-portal does not document, both held across the whole corpus, and the connector now tests both on every run | All 2,726 Global Fund activities declare sector percentages summing to exactly 100 across 4,721 declared sector rows, and 820 of the 2,726 declare a purpose code more than once, so adding a transaction's shares reaches the transaction and does not overshoot. All 113,777 transactions return exactly as many rows as the transaction's activity declares sector rows, with none surplus and none short, so no returned row is a duplicate and adding the rows cannot double count. On 113,774 of 113,774 transactions the percentages recovered from the shares match the declared percentages. 10 activities declare a purpose code twice at the same percentage, every one of the 10 on purpose 12110, and the 10 same-percentage declarations account for the 1,494 repeated keys standing in a ratio of exactly 1.0, so adding both rows of a ratio-1.0 pair is correct and invents none of the 25,040,420.73 USD standing behind the 1,494 keys. Because d-portal promises neither property, `_check_apportionment` reads the declared sector table on every run, counts the transactions matching, short and surplus, warns when an activity's declared percentages miss 100 by more than 0.5 and warns when a transaction returns more rows than the activity declares, and the run continues on a warning, because a run that reaches the panel with a warning against the run is worth more than a run that raises and leaves nothing to inspect. *Surveyed 2026-09-30* (§9ab) |
| A coverage finding that survived three probes turned out to describe the connector and not the publisher, because every figure in the finding was measured on a series the connector itself had damaged | Comparing the panel's two readings of the same Global Fund money, the IATI reading against the OECD Creditor Reporting System reading, on country-years where both readings exist, gave a ratio of 0.831 for 2003 to 2010, 0.761 for 2011 to 2017 and 0.598 for 2018 to 2026, with the share of country-years agreeing within two per cent falling from 81 to 50 to three per cent. The falling ratios read as a coverage collapse in what d-portal returns for the Global Fund, worsening steadily over time, and the reading survived the falsification of two rival explanations, namely that the Global Fund had consolidated single-disease grants into multi-component grants and that the connector's grant-letter test could not parse one identifier shape. Recomputed after the paging repair and the apportionment repair, the same three ratios are 1.009, 1.073 and 1.013 and the shares agreeing within two per cent are 91, 76 and 87 per cent, Ethiopia's median ratio moving from 0.037 to 1.000, Mozambique's from 0.186 to 1.000, South Africa's from 0.385 to 1.000 and Uganda's from 0.230 to 1.000. A comparison of two sources measures the code reading each source as well as the two sources, so a coverage limitation may not be written about a publisher while any known defect in the reading code is unrepaired, and the agreement now reached is a completeness check and not corroboration by an independent observer, because both readings originate with the Global Fund, the OECD reading through the Global Fund's return to the OECD and the IATI reading through the Global Fund's own publication. *Surveyed 2026-09-30* (§9ab) |
| A key stamped beside a value described a different population than the value, and the key summed to the value exactly on the rows where the two populations coincide | The Global Fund rows carry `extra.sector_13040_usd`, `extra.sector_12110_usd` and `extra.sector_12263_usd`, which a reader would use to strip tuberculosis-coded money out of the HIV series, while the row's value holds HIV and HIV-and-tuberculosis grants whole plus only the purpose-13040 share of every other grant. The three accumulators run before the grant-letter test at `hivimpact/connectors/iati.py:845`, so the three keys describe every grant the connector saw in that country-year and the value does not. Across the series the three keys sum to 53,953,975,658 USD against a value total of 38,152,946,330 USD. On the 480 rows where every named grant is an HIV or HIV-and-tuberculosis grant the keys sum to the value exactly, 4,450,872,871 USD both, and no row anywhere carries keys summing below the value, so every check run on the homogeneous rows agrees. On the 1,905 rows naming at least one other grant the keys exceed the value by 15,801,029,329 USD, on 1,745 of the 1,905, and the 192 rows carrying no value at all carry 352,219,073 USD of purpose 12263 and 48,548,052 USD of purpose 12110 beside the absent value. A key offered as a decomposition of a value must therefore be tested on the rows where the key and the value are expected to disagree, because a key that agrees on the subset where the two populations coincide looks correct on every row a spot check is likely to reach. **Jason rebuilt the panel on 30 September 2026 and the repair holds.** The four sector keys add to the value on all 2,385 rows that carry a value, the connector's own check of the unrounded running totals reports a largest disagreement of 0.00 USD, `seen_not_counted_usd` comes to 34,721,419,439 USD across the series, the 192 rows carrying no value are still 192, and the series total is 38,152,946,329.59 USD before the repair and after it, so the keys moved and no value did. Read back off the written file, with both sides rounded to a cent, the four keys are one cent out on 212 of the 2,385 rows and exact on the other 2,173, no row is further out than a cent, and the 212 differences come to 2.12 USD, because each key is rounded to a cent on its own while the value is written unrounded, which is a property of the published keys and not of the accumulators. **That second defect was approved and repaired the same day.** `sector_other_usd` is now the residual on every row that carries a value, written as the rounded value minus the three rounded named keys, so the four keys add to the value to the cent while no key naming a purpose code and no value moves. The residual is taken only where the unrounded accumulators already agree with the value, because a residual written unconditionally would define the invariant to be true and bury a real accounting defect inside the key that is meant to be checked, and the run now logs both counts, the accumulators against the value and the written keys against the written value. A check that tests the arithmetic inside a run says nothing about the file the run wrote, so a decomposition offered to a reader has to be tested as the reader will read it, on the written figures and not on the running totals. *Surveyed, repaired twice and rerun once 2026-09-30* (§9ab) |
| d-portal served one activity once per joined sector row, and the reader's second pass counted every copy, doubling one country's bilateral series for nine years while the series total moved by a hundredth of a per cent | The connector's XML reader asks d-portal for `from=act,sector` with `sector_code=13040`, which joins the activity table to the sector table, so `limit` and `offset` count joined rows and an activity declaring purpose code 13040 twice under vocabulary 1 arrives as two complete activity elements. Pass one of the reader writes `fingerprints[ident] = prints` by assignment and survives a repeat. Pass two tests `ident not in fingerprints` at `hivimpact/connectors/iati.py:1179`, which asks whether the identifier is known and not whether the identifier has already been summed, so lines 1288 to 1291 add the activity's money once per copy. A read-only scan of the 85 cached publisher directories found 11,698 activity elements holding 71 surplus copies in three publishers, and the number of copies equals the activity's count of vocabulary-1 13040 sector elements for 905 of UNICEF's 905 activities, 235 of `GB-CHC-285776`'s 236 and 217 of `AU-5`'s 250, which is the mechanism. `GB-CHC-285776` holds 64 of the 71 and is an international NGO, organisation type 21, which belongs to none of the three series, so `_publisher_rows` returns before pass one and no figure moves. Replaying the connector's own `_publisher_rows` offline against the cached pages, with `_request` patched to raise on any call, reproduces the panel's own `by_publisher` figure for Kenya 2012 exactly at 2,592,117.09 USD and gives 2,398,386.09 USD with repeated identifiers removed, so the defect is verified in the panel then on disk and not inferred. Kenya's multilateral row is overstated by 193,731.00 USD in 2012, by 12,783.00 USD in 2014 and in 2015, and understated by 12,783.00 USD in 2019, because the doubled transaction in 2019 is a negative expenditure and doubling a negative amount lowers the total. All six repeated Australian activities are Cambodian, and Cambodia's bilateral row is overstated by between 10.1 and 33.2 per cent in 2009, 2010, 2011, 2012, 2013, 2015, 2018, 2019 and 2020, where the surplus is exactly 50.00 per cent of the Australian contribution in every one of the nine years, so the whole Australian contribution to Cambodia in those years is twice the truth. The surplus is about 3,752,076 USD against the 5,679,863,850 USD the bilateral and multilateral series held together before the repair, which is 0.066 per cent, and not against the Global Fund series total, which the defect never touched. All 71 repeated copies are byte-identical to the copy already served, so deduplicating on the identifier cannot lose money, and the repair needs no publisher XML refetched because the bytes on disk are correct and the duplication is in the reading. Neither `external_hiv_bilateral_other` nor `external_hiv_multilateral_other` appears in the reconciliation pair or cell files, so no divergence was flagged on either series. The duplication is deterministic and is not the unstable paged read recorded above, because the repeated UNICEF activity sits at child indices 281 and 282 of one page, adjacent and inside a single response, which no reordering across pages can produce. **Jason rebuilt the panel on 30 September 2026 and the repair holds.** Exactly 13 country-years moved and no others, `external_hiv_bilateral_other` fell by 3,545,561.71 USD across the nine Cambodian years and `external_hiv_multilateral_other` by 206,514.00 USD across the four Kenyan years, both to the penny of the offline replay, Kenya 2019 rose by 12,783.00 USD as the negative expenditure predicted, and the row count of each series is unchanged. One claim in the survey above was wrong and is corrected here. A read-only scan of all 85 cached publisher directories finds no repeat anywhere straddling two pages, so the set of summed identifiers was justified by a case the cache does not contain. The set still belongs outside the page loop, because the query permits a repeat to straddle a page, and what a page boundary was measured to do is the opposite of a repeat, namely serve an activity once whose second join row fell past the limit. *Surveyed and rerun 2026-09-30* (§9ab) |
| A classifier that reads a relationship off the numbers cannot tell two publications of one accounting record from two measurements, and called the Global Fund's own two returns independent evidence of a disagreement with itself | `hivimpact/reconcile.py` sorted every pair of sources reporting the same country, indicator and year into derived, subset or independent by three numeric tests, with independent as the final else, on the stated principle that a classification inferred from the data can be audited where a hardcoded classification cannot. The principle is right about auditing and wrong about what the numbers hold. The Global Fund publishes the same disbursements to the IATI registry and to the OECD Creditor Reporting System as reporter 9OTH012, so the `iati` and `oecd_crs` figures for `global_fund_hiv_disbursements` are one accounting record published twice, but the two readings date money differently, by transaction date against reporting year, and the IATI reading counts the whole value of an HIV or HIV-and-tuberculosis grant where the OECD return carries the HIV purpose code alone. Those two treatments put the pair outside the derived band and outside the subset test, so the pair fell through to independent and 2,002 cells were counted as independent evidence, of which 164 were flagged as material divergences between one reporter and itself. No numeric threshold could have saved the classification, because provenance is not a property of the numbers. The repair declares the relationship where the provenance is known and infers it only where the provenance is not known. A module-level map holds the pair, the verdict and the reason in prose, `classify_pairs` reads a declared verdict before applying any threshold, and every classified pair carries a `basis` column reading declared or inferred so a reader can tell one from the other without opening the module. Run over the panel of 30 September 2026 the declaration moves that one pair from independent to derived and moves no other pair, taking the independent-pair cells from 31,145 to 29,143 and the material divergences from 8,518 to 8,354. Only what is known goes in the map. The two `unaids_gam_expenditure` pairs look independent and have not been established as independent, so no entry claims either way and both keep an inferred verdict. **Jason rebuilt the panel on 30 September 2026 and the run reproduced every predicted figure.** The reconciliation summary reads 29,143 independent-pair cells, 8,354 material divergences, 67 independent pairs and one pair whose relationship was declared and not inferred, and `data/panel/reconciliation_pairs.csv` carries the `basis` column with 97 inferred rows and one declared. *Surveyed, repaired and rerun 2026-09-30* (§9ac) |
| The Global Fund retired `Total number of HIV tests` from the 2025 reporting year, and the quantity the indicator measured did not fall to zero | One read-only request to `AllProgrammaticIndicators` on 2026-10-01 returned 17,538 `Annual_Results` rows, saved under `data/raw/global_fund/results_probe_20261001/`. `Total number of HIV tests` carries 795 rows, 527 National, 243 Subnational and 25 with no coverage value, running 54, 62, 68, 67, 69, 69, 72 and 66 National rows over 2017 to 2024 and zero in 2025 at every coverage. The dataset holds 2,225 rows for 2025 against 2,239 for 2024, so 2025 is a fully reported year. Exactly one name appears in 2025 and not in 2024, `TB patients with DST result for at least Rifampicin` at 15 National rows, which is tuberculosis drug-susceptibility testing, so the series was not renamed. Every disaggregation of the same measure continues into 2025, with key-population testing counts running drug users 31 then 32, men who have sex with men 56 then 54, sex workers 55 then 52, transgender people 36 then 34, adolescents 4 then 5, other vulnerable populations 11 then 15 and prisoners 21 then 21, while `Individual HIV self-test kits distributed` grows 8 to 12, `People on ART with viral load test result` grows 25 to 33 and `People on antiretroviral therapy for HIV` holds 96 countries in both years. The panel therefore ends `hiv_tests_performed` for the Global Fund at 2024, where 66 countries reported 41,041,341 tests, against 48,238,125 in 2023 and 48,525,192 in 2022. Why the indicator was retired is not in the data and is not asserted. *Probed 2026-10-01* (§9ad) |
| Three publishers lack recent HIV testing volume while publishing treatment counts for the same years, so no year-to-year comparison of testing volume may cross 2024 | The Global Fund ends `hiv_tests_performed` after 2024. WHO's Global Health Observatory holds `hiv_tests_performed` for 129 countries in 2024 and nothing after and `hiv_test_positivity_pct` for 127 countries in 2024 and nothing after, while reaching 2025 across 10 of the 12 series it contributes to the panel. UNAIDS AIDSinfo holds interior gaps in the same two measures, 92 and 90 countries in 2019, nothing in 2020 and 2021, and 92 again in 2022. A second Global Fund testing series thins without stopping, `Number of HIV positive tests` mapping to `new_diagnoses` at 22 National rows in 2023, 8 in 2024 and 2 in 2025, so no stopped-series warning will ever fire for it and a reader trending the series to 2025 reads two countries as the programme. *Measured 2026-10-01* (§9ad) |
| The Global Fund's `geographicCoverage` field means national within the reporting unit and not a sovereign state, and the guarantee that a panel row is a country comes from the geography level and not from the coverage test | Zanzibar is published under code `QNB` with `geographicCoverage` set to `National` while the service's Geographies lookup grades Zanzibar `Subnational`, and Zanzibar carries one National testing row in each of the eight years the series runs. The service's National row counts therefore stand exactly one above the panel's reporting-country counts in every year, 54 against 53, 62 against 61, 68 against 67, 67 against 66, 69 against 68, 69 against 68, 72 against 71 and 66 against 65. `geographies()` keeps only geographies graded `Country`, so all eight Zanzibar rows are declined correctly, and a connector testing coverage alone would have placed Zanzibar's results under a country code. *Measured 2026-10-01* (§9ad) |
| The UNAIDS spending-assessment index holds reports for 14 of the region's 24 countries, where three rounds of country-by-country sweeping had found three | The index was read as a class on 30 September 2026 instead of one country at a time, and the 11 countries the earlier rounds said nothing about are the measure of what a country-ordered sweep hides. A sweep ordered by country answers whether a country publishes and cannot answer whether a class adds, because the denominator of the class is never in view. *Swept 2026-09-30* (§9ae) |
| Almost none of those 14 reports is additive, because the GAM expenditure workbook already on disk holds the same countries and years | The workbook holds 59,947 rows over 121 countries, and 18 of the region's 24 countries match the panel country for country and year for year across 817 panel rows. Counting from 2019 the whole class adds six country-years, being Cameroon 2020 and 2021, DR Congo 2019 and 2020, and Togo 2022 and 2023. *Settled against the panel 2026-09-30* (§9ae) |
| One country of the 24 is a build in that class, and the reason is an absence and not a publication | Cameroon holds zero GAM expenditure years and eight published assessment years, so for Cameroon alone an assessment report is the only expenditure measurement anywhere in the pipeline. The other 13 publishers in the class are publishing what the panel already reads through UNAIDS. *Settled 2026-09-30* (§9ae) |
| An agreement of 3 to 5 per cent between a hand extraction and a panel series was proof of duplication, and Benin left the build list on it | Two of the three reports an earlier round extracted by hand were Benin 2024 and Ghana 2022, and the panel already held Benin 2018 to 2024 unbroken and Ghana 2014 to 2023 unbroken through GAM. A country's assessment report is what that country's GAM return is built from, so the provenance permits the two figures to be one measurement and the agreement is fidelity. An agreement is corroboration only after the two figures have been shown not to share an origin, and the showing comes before the comparison is read. *Settled 2026-09-30* (§9ae) |
| Half the region was excluded from the probe list by the panel itself, before any host was contacted | The panel holds 52,840 rows carrying a sub-national unit over 55 countries, and in this region every one of those rows comes from two PEPFAR connectors and from nothing else. Twelve of the 24 countries already have PEPFAR coverage at that grain, so a national statistics institute could only add sub-national measurement for the other 12, and 12 hosts were probed instead of 24. *Measured on the panel 2026-09-30* (§9ae) |
| Guinea's institute publishes health statistics yearbooks that carry two extractable HIV tables, and the 2018 edition settles the build | `stat-guinee.org` serves yearbooks for 2007 to 2022, and the 2018 edition is 88 pages of extractable text with six pages carrying HIV content. Tableau 4.2 gives TB and HIV co-infection by health district with tested counts, positivity and share on treatment, and Tableau 4.19 gives antenatal counselling and testing by health district with women counselled, women accepting a test, women tested, women testing positive, and partners tested and positive, where one district reports 9,147 first antenatal visits against 93 women testing positive. *Read 2026-09-30* (§9ae) |
| Niger's 2019 yearbook carries a measurement the pipeline holds nowhere else, being the completeness of the HIV reporting itself | `stat-niger.org` serves a 208-page 2019 edition with 37 pages mentioning HIV. Tableau 99 gives TB and HIV co-infection by district and region, and Tableaux 58 and 59 give a per-district reporting completeness and promptitude rate for the HIV care form, which measures how complete the underlying HIV reporting is and not how many patients there are. *Read 2026-09-30* (§9ae) |
| The Gambia publishes no repeating HIV series, and the only district figures available sit inside a five-year planning document | The bureau of statistics publishes no health statistics yearbook, and district HIV prevalence running from 2.7 per cent down to 0.98 per cent appears only in a national strategic plan covering 2021 to 2025. The repeating-series test an earlier region applied to 18 of its 19 countries refuses the document on publication cadence and not on the quality of the figures inside. *Refused 2026-09-30* (§9ae) |
| Gabon's yearbook is withdrawn and not relocated, and the institute's remaining HIV content is derived | The yearbook URL answers 302 to the institute's new site root, so the document is gone and not relocated. The institute's remaining HIV content is prevalence under demographic indicators, republished through a commercial data portal, which grades the Gabon figures derived against UNAIDS. *Probed 2026-09-30* (§9ae) |
| Five of the region's 24 countries publish nothing a machine can read, and recording the five is what stops a fourth sweep | Cabo Verde, Congo-Brazzaville, Equatorial Guinea, Guinea-Bissau and São Tomé hold zero GAM expenditure years, no spending assessment report and zero sub-national rows, so no expenditure measurement and no sub-national measurement exists for any of the five anywhere in the pipeline. Comprehensively dark is a result and not a gap to keep searching. *Settled 2026-09-30* (§9ae) |
| Nigeria's repository serves five endpoints and the gate is four headers, where three survey rounds recorded three endpoints and one header | The endpoints answer 403 without a referer naming the wallboard page, a header declaring an XMLHttpRequest, a JSON accept header and a browser user agent. `BaseConnector.RETRYABLE_STATUS` deliberately excludes 403, so a missing header fails a run at once instead of retrying into a rate limit. Three fields of the richest payload are JSON documents encoded as strings, each decoding to an object whose content sits one level down, which is why earlier surveys of the same host reported the two richest endpoints as absent. *Built against five saved payloads 2026-10-01* (§9ae) |
| A published residence matrix does not repair the defect the matrix was recorded as repairing, and moves the worst Nigerian state the wrong way | The repository publishes treatment above its own state PLHIV estimate in 14 of 37 states, and an earlier round recorded the repository's `txcurr_res_state` matrix as the fix, on the reasoning that patients are counted where treated and not where resident. Recomputing every state's numerator from residence leaves 13 of 37 states above 100 per cent and moves the worst state from 158 to 165 per cent. The geography of counting is worth at most 18.6 percentage points here, which is the Federal Capital Territory, and the first-order defect is the state allocation of the national estimate. The connector therefore publishes the state treatment count and the state estimate as separate flagged rows, emits no state coverage percentage, and emits the national figure of 87.81 per cent because the national sum is sound. A documented mechanism is a hypothesis until the mechanism has been applied to the data. *Measured offline 2026-10-01* (§9ae) |
| Nigeria's dashboard publishes a national treatment headline that disagrees with every decomposition in the same payload | The headline reads 1,791,837 against a state sum of 1,678,165 from the same payload, 6.3 per cent lower, while the state, sex and age decompositions agree with one another to within 0.8 per cent. The state sum is emitted and the headline travels on the emitted row with the reasoning, so a reader who wants the published number can find the number and see why the number was not used. Three decompositions agreeing is evidence about the decompositions, and a headline standing alone against all three is evidence about the headline. *Measured offline 2026-10-01* (§9ae) |
| Two endpoints of one source both publish a treatment stock, and the panel's duplicate check cannot tell the two apart | `hivimpact/writers.py` keys duplicates on country, sub-national unit, indicator, population group, sex, age band, year and source identifier, and the key does not include the source's own indicator code, so in a year where both Nigerian snapshots fall the panel would hold two conflicting stock figures under one source and the writer would only append a warning. The connector resolves the collision instead, giving the later snapshot month ownership of the stock for that year, suppressing the earlier snapshot's stock rows and recording the dropped figure on the surviving national row, which required loading both payloads before any row is yielded because the decision cannot be made from one payload alone. A warning is not a resolution. *Built 2026-10-01* (§9ae) |
| A required schema field settled the recency question that no amount of flagging could | The recency endpoint holds 220,423 recency tests, 9,617 recent infections and 3,403 confirmed by the second assay over 34 states and eight age bands, self-consistent in that the state block and the age block sum to the same totals, and carrying no date. `PanelRow.year` at `hivimpact/schema.py:59` is a required int with no default, so an undated figure cannot enter the panel at all and no flag beside the row can stand in for a year that is not there. Offering a choice between admitting a figure with a loud flag and refusing the figure is a real choice only once the schema has been read. *Settled 2026-10-01* (§9ae) |
| One block of that same endpoint is fully dated and internally clean, so the refusal had to be re-argued on grounds the schema does not supply | `vl10.vl_month` holds 76 monthly points over nine named series from March 2020 to June 2026, the three percentages sum to 100 in all 76 months, the three denominators are identical in all 76 and the three numerators sum to the denominator in all 76, and the months per calendar year run 10, 12, 12, 12, 12, 12 and 6, giving five complete calendar years from 2021 to 2025. The block is refused on two other grounds, being that the measure is viral-load sample collection for recency confirmation, which no indicator in `CANONICAL_INDICATORS` covers and no other source in the panel holds, so admitting the block means a new specification with no reconciliation partner, and that the yearly denominator runs 554, 1,731, 3,516, 2,012, 1,566, 237 and 1 with the available-result share falling from 61.9 per cent in 2024 to 21.5 per cent in 2025, which cannot be told apart from reporting lag inside the payload. Three survey rounds missed the block entirely. *Measured offline 2026-10-01* (§9ae) |
| Nigeria's repository reports four states PEPFAR does not report at all, and the two sources are not independent | The four states hold 106,931 people on treatment between them, against a national repository-minus-PEPFAR difference of only 71,424, so PEPFAR reports about 35,507 more than the repository across the 33 shared states. An earlier round graded one comparison source independent of the repository and the grading was wrong, because the national AIDS programme both runs the repository and prepares the reporting that feeds the others, and the PEPFAR extract rests on the same facility registers. Every emitted row declares shared origin, so the reconciliation layer reads a discrepancy as a bound on site coverage and never as triangulation. *Measured offline 2026-10-01* (§9ae) |
| The connector emits 159 rows at the stated window and 77 at the default window, with no error either way | `scripts/run_all.py` defaults `--end` to 2025 while the dashboard snapshot is October 2026, so a run launched without `--end 2026` emits 77 rows instead of 159 and drops every dashboard row silently. The 159 are 77 from `ctd.nascp.gov.ng/facilitydata/` and 82 from the dashboard, taking the panel from 218,083 rows to 218,242, and the per-state suppression figures run 91.63 to 99.62 per cent. Verified three times offline against the saved payloads, twice after the docstring was rewritten. `scripts/build_site.py:458` returns nothing below three points, so this source produces no site line chart until three annual runs have accumulated. *Dry-run offline 2026-10-01* (§9ae) |
| Two of the three drop counters in the Global Fund connector name causes the code never tested, and two further exits carry no counter at all | Replaying every exit from `fetch()` over the 17,538 saved rows accounts for every row, 8,294 dropped for an unmapped name, 2,328 for a coverage other than National, 127 for a geography that is not a country and 6,789 emitted. The behaviour is right at every exit and two labels are wrong. Of the 2,328 the log calls subnational, 2,168 state `Subnational` and 160 state no coverage at all. Of the 127 the log calls unresolved, all 127 resolve to a published geography and are declined for being a region or a subnational unit, Zanzibar at 104 rows, the Caribbean at 13, Oceania at 7 and Western Asia at 3. The unreadable-year and unreadable-numerator exits carry no counter and drop zero rows of the saved dataset, so each is latent and not active. No row reaches the panel carrying a Global Fund aggregate code and the panel holds zero rows coded `QMZ`, `QPA`, `QRB`, `QUA`, `QSF`, `MCC` or `QNB`. **Jason approved the repair on 1 October 2026 and the repair was built and checked offline the same day.** The connector now keeps seven counters, being an unmapped indicator name, a coverage below National, a coverage stated nowhere, a geography the service does not grade Country, a country outside the requested list, an unreadable year and no usable value, and the log line states the rows read so a reader can close the arithmetic against the counts. One further uncounted exit was found during the build itself, being the restriction to the countries a run asks for, which the first draft of the log line would have absorbed silently into the out-of-range residual whenever a run named countries, and that exit now carries a counter of its own. The offline check serves the connector from the saved probe files with `_request` patched to raise, emits 6,789 rows, which is identical to the replay made before the edit, and reports 8,294 unmapped names, 2,168 coverages below National, 160 coverages stated nowhere, 127 geographies the service does not grade Country, no country off the list, no year out of range, no unreadable year and no unusable value, which add to 17,538 exactly. A three-country run emits 180 rows and counts 6,609 off the list with the out-of-range residual at zero, and a 2020 to 2022 window emits 2,280 rows and counts 4,509 out of range, so both counters move only on the rows each counter names. No filter and no emitted value changed, so the panel on disk is unaffected and no rerun is needed. *Audited, approved and built 2026-10-01* (§9ad) |
| A report's own list of tables disagrees with the report's own body in four places, and the body then prints a stale caption above a correct year header | In Cameroon's 2020-2021 national AIDS spending assessment the list's Tableau 7 is the body's Tableau 8, the list's Tableau 8 is the body's Tableau 9, the list's Tableau 12 is the body's Tableau 14, and the list prints two different tables both numbered Tableau 9. The body's Tableau 14 carries a caption reading "en 2018 et 2019" above a table whose own year header says 2020 and 2021. Every block in `cm_nasa` is located by caption text and every year is read from the block's own header. The same rule was already forced on the annual reports for a different reason, that the 2023 edition's Tableau 38 is a map of trained peer mentors where the 2024 edition's Tableau 38 is the regional treatment file. *Read offline 2026-10-02* (§9af) |
| A chart axis prints a year header directly above a table's own header, and on that page the two agree, so the defect would have produced correct output | Printed page 41 of the same assessment carries the Graphique 9 axis reading 2020 and then 2021 above Tableau 8's header, so a first-header rule would take Tableau 8's year order from a chart. Graphique 9's own data labels extract in descending year order, reversed from that axis, and the two candidate orderings differ by 231,233,448 FCFA, so a descending chart is not hypothetical. A later header now replaces an earlier one up to the first data row, a rule written with no observable failure to motivate it. *Read offline 2026-10-02* (§9af) |
| A duplicate-row gate written for one defect caught two label-matching bugs of a different kind, each of which would have emitted one plausible figure | A two-line label look-back matched a bilateral subtotal as the United States row, because the two lines above that subtotal read "Gouvernement américain" and then "Contributions", and the gate printed 20,279,515,168 against 23,486,587,409 for 2016. An unmapped child row inherited the label of the parent printed above it, and the gate printed 80,596,207,345 against 5,804,405,493. Four real parser bugs surfaced across three offline runs and a gate caught all four. The look-back is now conditioned on the previous line carrying no figures of its own, and every wrapped label in both documents is preceded by a label-only line, so the narrowing costs nothing. *Dry-run offline 2026-10-02* (§9af) |
| A reclassification accounts for about half of an apparent 21-point fall in the prevention share, and the surviving half cannot be separated from the published categories alone | Cameroon's 2016-2017 assessment reports prevention at 27.5 and 21.3 per cent of national HIV spending and its own prose names voluntary counselling and testing as the largest component of that pool. The 2020-2021 assessment reports prevention at 6.1 and 6.1 per cent and counselling and testing separately at 10.8 and 9.9 per cent, which add to 16.9 and 16.0 per cent. So the apparent fall is 21.4 points from 2016 to 2020 and 15.2 points from 2017 to 2021, of which reclassification accounts for 10.8 and 9.9 points, leaving 10.6 and 5.3 points that the published categories cannot attribute either way. The prevention series is refused and the rest of the intervention classification with it. Treatment is emitted, because both assessments carry one treatment line over the same activities and the later assessment prints a treatment total in two tables that agree to the franc in both years. *Read offline 2026-10-02* (§9af) |
| One document prints three different values for one quantity and agrees with the recomputation at none of them, so every printed rate is refused | The 2020-2021 assessment prints the 2021 international share as 94.1 per cent in one table, 94.0 per cent in another and 94.1 per cent in the narrative, against 94.1244 per cent recomputed from the levels the same document prints, and prints the 2021 domestic public share as 4.0 per cent in one place and 4.6 per cent in another where its own numerator and denominator give 4.4316 per cent. A whole key-indicators table is refused, because its 2020 public share of 4.1 per cent reproduces only against the intervention subtotal while its private and external shares reproduce against neither denominator. Both connectors recompute every share from levels and carry the numerator and the denominator on the row. *Read offline 2026-10-02* (§9af) |
| Two figures were taken from a document that does not assess their year, and three independent ties had to hold before either figure was emitted | Cameroon's 2016-2017 assessment prints no split between domestic public and domestic private money and the 2020-2021 report's historical page does. That page's public and private rows sum to the earlier assessment's own residual to the franc in both years, being 5,609,831,158 for 2016 and 10,839,249,471 for 2017, the same page's bilateral row equals the earlier assessment's bilateral subtotal exactly in both years, and reading the year columns the other way round would put one bilateral figure 2,881,313,043 FCFA away from the figure the other document prints. The same page's UN-system rows, other-international rows, 2017 Global Fund row and 2014, 2015, 2018 and 2019 columns are all refused, the Global Fund row because it prints 29,844,975,030 FCFA against the assessment's own 31,704,143,887 FCFA while the row's 2016 figure ties exactly. *Verified offline 2026-10-02* (§9af) |
| A disclosed residual of about 0.2 per cent was located inside one line instead of accepted as an error bar on every donor component | The revenue table's line REV.07.01.02 falls short of FE.03.02 plus FE.03.03 by exactly 152,234,707 FCFA in 2020 and 84,910,026 FCFA in 2021, which is exactly the amount by which REV.07.01.01 plus REV.07.01.02 falls short of REV.07. So the whole residual sits in that one line, the line is refused as a donor total, and the donor components come from Tableau 8, which ties exactly at all three of its nesting levels in both years. Twelve gates hold the 36 emitted rows up, including three tables agreeing on the national total to the franc. *Verified offline 2026-10-02* (§9af) |
| Money a document states in no convertible currency stays in that currency, and the conversion becomes a second panel series instead of a constant inside a parser | Every figure in both Cameroonian assessments is printed in CFA francs, neither prints a dollar equivalent and neither states a rate, so `cm_nasa` emits local-currency levels with `extra.currency` reading XAF on all 32 money rows plus one currency-free recomputed share, and `CANONICAL_INDICATORS` carries a fourth unit beside its dollar, count and percentage units at 138 indicators. `site/charts.py` already renders an unrecognised unit as a plain grouped number, so the site needed no change. The recommendation on the record is to add the World Bank's `PA.NUS.FCRF` to `world_bank.py`, which changes an existing connector's output for every country and is therefore the researcher's call. Chad is in the same currency zone, so the same question arrives again inside item 17. *Decided offline 2026-10-02* (§9af) |
| The regional alias map the probe round flagged is resolved inside the connector, and the ten names match the comparison source exactly | `cm_cnls` resolves "Extrême-Nord", "Extrême-nord", "Far-north", a line-wrapped "Extreme-" and "Nord" and the other variants to one spelling at parse time and keeps the document's own spelling in `extra["admin1_source_label"]`. Checked against the panel on disk, `pepfar_snu` holds exactly ten Cameroonian sub-national values and the connector's ten match all ten with nothing unmatched on either side, so the regional treatment rows reconcile against PEPFAR with no alias step downstream. The connector emits 188 rows from two editions, 88 for 2023 and 100 for 2024, and carries the one known arithmetic defect on the row instead of absorbing it, the 2023 viral-load tested column summing to 203,135 against a printed 203,134 with both emitted as printed and the one-person gap recorded on the national row. *Dry-run offline and checked against the panel 2026-10-02* (§9af) |
