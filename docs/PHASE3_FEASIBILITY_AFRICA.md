# Phase 3 — "to source" feasibility log (sub-Saharan Africa)

The same question as Phase 2, asked of a second region: *can we go to source with country-level
programme data, country by country?* Southeast Asia answered "yes for some", with open
structured national data at one country in nine. The access ladder built on that answer
([`ACCESS_LADDER.md`](ACCESS_LADDER.md)) makes a prediction for Africa — heavier donor
dependence should mean a lower country-side grade distribution and a much richer donor-side
layer. This log is the country-side half of the test.

**What the evidence here is, and is not.** The Southeast Asian log rests on per-country desk
research: each national system identified by name, each access route tried. This log rests on a
mechanical access probe of 62 candidate endpoints — 58 national, 4 regional, across 19
countries — run 2026-08-03, recording for each one whether the host resolves, what it returns,
where it redirects, and whether a DHIS2 API answers. A probe establishes a barrier when it hits
one, and it establishes nothing when a hostname I guessed does not exist. Rows below are marked
for which of the two they are. South Africa is the exception: it was worked through properly and
a connector is built.

| Country | National source probed | What it did | Status |
|---|---|---|---|
| **South Africa** | Thembisa model outputs (UCT), NDoH webDHIS | Thembisa: **open versioned Excel**, national + 9 provinces, 95% CIs, key populations, no login | ✅ **Connector built** (`za_thembisa`) |
| **Tanzania** | Tanzania HMIS (`dhis.moh.go.tz`), NACP, TACAIDS | HMIS answers and redirects to a DHIS2 login; TACAIDS serves an untrusted certificate | ⛔ **Gated** (login wall observed) |
| **Ethiopia** | `dhis.moh.gov.et`, EPHI | DHIS2 login wall (Amharic UI); the API returns the login app, not JSON | ⛔ **Gated** (login wall observed) |
| **Uganda** | `hmis.health.go.ug`, UAC | "Login app \| DHIS2" | ⛔ **Gated** (login wall observed) |
| **Malawi** | `dhis2.health.gov.mw`, MoH | "Malawi HMIS" login; the ministry site 403s at the edge | ⛔ **Gated** (login wall observed) |
| **Kenya** | KHIS Aggregate (`hiskenya.org`), NASCOP, NSDCC | Host alive, certificate untrusted; behind it a DHIS2 login redirect | ⛔ **Gated** (login wall observed) |
| **Nigeria** | National Data Repository (`ndr.phis3project.org.ng`), NACA, NAIIS | "Login - Nigeria National Data Repository"; NAIIS answers over plain HTTP only | ⛔ **Gated** (login wall observed) |
| **Zambia** | `hmis.moh.gov.zm`, MoH, NAC | HMIS host alive, certificate untrusted, root serves an Apache Airflow UI and no public data | ⛔ Gated |
| **Zimbabwe** | `hmis.mohcc.gov.zw`, MoHCC, NAC | Host alive, certificate untrusted, serves an "EHR" application | ⛔ Gated |
| **Mozambique** | MISAU, INS | Both certificates untrusted; INS is in maintenance | ⏳ Inconclusive |
| **Rwanda** | `hmis.moh.gov.rw`, RBC | Reachable over valid TLS, landing page is not a login, `/api/system/info.json` 404s | ⏳ **Lead** — closest thing to an open HMIS found |
| **Lesotho** | MoH | Certificate untrusted; no DHIS2 host found | ⏳ Inconclusive |
| **Eswatini** | NERCHA, gov.sz | Reachable, no data portal located | ⏳ Lead |
| **Namibia** | MHSS | Connection timeout | ⏳ Inconclusive |
| **Botswana** | MoH & Wellness | Reachable, no data portal located | ⏳ Lead |
| **Ghana** | Ghana AIDS Commission, GHS, DHIMS2 | GAC reachable; GHS over plain HTTP only; the DHIMS2 hostname does not exist | ⏳ Lead |
| **Cameroon** | CNLS, MINSANTE | Both reachable, no data feed located | ⏳ Lead |
| **DR Congo** | PNLS, MSP | PNLS 403s at the edge | ⏳ Inconclusive |
| **Côte d'Ivoire** | Ministry of Health, PNLS | Ministry 403s at the edge; the PNLS hostnames do not exist | ⏳ Inconclusive |

Regional layer: the PHIA survey programme's data manager (`phia-data.icap.columbia.edu`) is
alive, serves an untrusted certificate, and is a registration-gated request system. PHIA is the
best population survey layer in the region and it is grade 3.

---

## 1. The prediction's first half holds

Six countries return a login wall from a national health information system that is plainly
working: Tanzania, Ethiopia, Uganda, Malawi, Kenya and Nigeria. In each case the system answers,
identifies itself, and refuses. That is the same grade-3 pattern Southeast Asia produced, and it
is now observed rather than assumed for six of the largest PEPFAR countries in the world.

The DHIS2 API is worth a line of its own, because it looked like a way round. DHIS2 exposes
`/api/system/info.json`, and on an open instance that returns JSON without a session. On every
national instance probed it returned HTTP 200 with `text/html` — the login application. The API
is authenticated along with the interface. There is no side door, which is the correct design
and closes the obvious shortcut.

Against nineteen countries, exactly one country-side source is open, structured, additive and
usable: South Africa's Thembisa. One in nineteen, against Southeast Asia's one in nine. The
prediction said the African country-side distribution should be lower and it is, though the two
regions were probed to different depths and the numbers should not be read as if they were.

## 2. A barrier class Southeast Asia did not produce

Twelve of the sixty-two endpoints failed on TLS certificate verification. Retried with
verification disabled, nine of them served ordinary content:

| Host | What it actually serves |
|---|---|
| `hiskenya.org` | KHIS Aggregate, redirecting to `/dhis-web-commons/security/login.action` |
| `www.health.go.ke` | Kenya Ministry of Health |
| `tacaids.go.tz` | TACAIDS (Tanzania Commission for AIDS) |
| `www.moh.gov.zm` | Zambia Ministry of Health |
| `hmis.moh.gov.zm` | an Apache Airflow interface |
| `hmis.mohcc.gov.zw` | an "EHR" application |
| `www.misau.gov.mz` | MISAU, behind a BunkerWeb proxy |
| `www.health.gov.ls` | Lesotho Ministry of Health |
| `phia-data.icap.columbia.edu` | PHIA Data Manager |

Two more (`naiis.ng`, `www.ghanahealthservice.org`) answer over plain HTTP and fail over HTTPS.

This matters twice over. First as a measurement error: a probe that reads a TLS failure as "site
down" writes a false finding into the log, and this project already made that mistake once — the
first Africa note recorded that Kenya's national DHIS2 host "does not resolve", when in fact it
resolves, runs, and is gated. The conclusion survived; the stated reason was wrong, and a reason
that is wrong in the record is worse than a gap in it.

Second as a decision. These hosts are reachable if certificate verification is turned off. We do
not turn it off. An unverified channel means there is no way to attest that what came down the
wire is what the ministry published, and a research panel whose provenance fields say
`source_url` cannot carry rows collected that way. So they stay out, and the recorded reason is
"TLS chain not verifiable", not "unreachable". The distinction is the difference between a
technical barrier that a data-sharing agreement would not fix and one it would.

## 3. What is inconclusive, and why that is not a finding

Twelve probes failed at DNS. Most of those hostnames were my guesses at a naming convention
(`dhis2.gov.sz`, `dhis2.mhss.gov.na`, `webdhis.health.gov.za`, `dhims.ghsmis.org`). A DNS failure
on a guessed hostname is evidence about the guess. Three probes returned 403 from an edge or WAF
(DR Congo's PNLS, Côte d'Ivoire's ministry, Malawi's ministry), which says the origin declined a
request from this network and says nothing about whether data sits behind it.

Those two groups cover most of West and Central Africa in this log, which is the region's real
gap: francophone national programmes were probed thinly and deserve the per-country desk research
that Southeast Asia got before anything is claimed about them.

---

## South Africa — ✅ built

- **Source:** the Thembisa model, `https://www.thembisa.org/downloads`. Thembisa produces South
  Africa's official national and provincial HIV estimates, is run academically (Leigh Johnson
  and colleagues, UCT), and publishes versioned Excel workbooks with no registration and no bot
  blocking. Grade 1 on the ladder, and the only grade-1 country-side source found in the region.
- **What it carries beyond the aggregators** — the test that decides whether a connector is
  worth writing:
  - **Nine provinces.** UNAIDS and WHO carry South Africa as a single national number. This is
    the sub-national layer for the largest epidemic in the panel.
  - **95% confidence intervals on every indicator**, published as their own rows, which map
    straight onto the schema's `value_lower` / `value_upper`.
  - **Key populations** as modelled series: sex workers, cis-gender MSM, transgender women and
    PWID, with prevalence, ART coverage, diagnosis and viral suppression.
- **Extracted:** 12 canonical indicators, 10 geographies (national plus 9 provinces), 14,150
  rows at the pipeline's default 2000–2025 window (17,650 from 1990), every row carrying 95%
  bounds except one derived series that says why it does not.
- **Estimates against projections.** The workbook publishes to 2035, and the years past the fit
  are extrapolations. Which years those are is encoded in the font colour, not in a cutoff:
  black is fitted to data, grey is projection. The boundary is per indicator, because it tracks
  the last year of data feeding that series — AIDS deaths are fitted to 2018 (the last
  vital-registration year), population to 2011 (the last census), the treatment cascade to 2025.
  The connector reads the colour and emits only the black years. This is not a nicety. A study of
  what a funding cut did in 2025 must not read a model's pre-cut extrapolation of 2025 as
  evidence about 2025, and any year-based rule would have let some of them through.
- **Provinces do not sum to the national figure**, because the national model is calibrated
  independently of the provincial ones. Measured on the panel: PLHIV 2022 national 7,652,160
  against 7,686,812 for the nine provinces (+0.45%), on-ART 2022 −0.63%. Every row carries the
  warning, and anything aggregating this source takes the national rows or the province rows and
  never both.
- **Validation:** values and bounds checked cell by cell against the workbook across sheets and
  indicators, and cross-checked against the aggregator layer already in the panel — PLHIV 2022
  +0.7% against UNAIDS, prevalence 15–49 −1.8%, ART coverage −1.8%. New infections 2021 sits
  15.4% below UNAIDS, which is a real difference between Thembisa and Spectrum and not a defect;
  it is the kind of divergence the reconciliation layer exists to surface.
- **Tagged `modelled_estimate`, not `routine_programme_record`.** South Africa's national source
  is a model, so its rows must not be compared with programme counts as though they were the
  same kind of number.
- Connector: `hivimpact/connectors/country/south_africa_thembisa.py` (`source_id=za_thembisa`).
  Auto-discovers the newest `ProvOutputs` workbook, caches into `data/raw/thembisa/`, and uses a
  local copy when one is present.

## Kenya, Tanzania, Uganda, Malawi, Ethiopia, Nigeria — ⛔ gated

All six run a national health information system that answers and requires a session. The route
to these is an institutional data-sharing agreement, the same conclusion Southeast Asia reached
for its six grade-3 countries, and the same different-timescale work.

For the specific question this project asks, that is less costly here than it sounds, because
these are exactly the countries where the donor-side layer is deepest. Kenya alone has 16,109
rows in the PEPFAR MER top-line file against Cambodia's 2. The country-side door is shut and the
donor-side door is wide open, which is the inversion the ladder predicted.

## Rwanda — ⏳ lead

`hmis.moh.gov.rw` answers over valid TLS with a "Welcome to MoH HMIS" page and no login redirect,
and its `/api/system/info.json` returns 404, so it is either not DHIS2 or not DHIS2 at that path.
It is the only national HMIS in the probe that did not immediately refuse. Worth a proper look
before the francophone desk research.

## Untested leads worth naming

- **NASCOP and NSDCC (Kenya)** both serve reachable public sites. Whether either publishes a
  born-digital report that carries more than Kenya's GAM submission is the grade-2 question, and
  it has not been asked yet. The Malaysia lesson applies: the test is not whether a report can be
  parsed, it is whether it carries anything the aggregator does not.
- **PHIA** (Population-based HIV Impact Assessments) covers most of the high-burden countries
  here with the best survey data in the region, released through a registration-gated data
  manager. Grade 3, and a data-request route rather than a connector.
