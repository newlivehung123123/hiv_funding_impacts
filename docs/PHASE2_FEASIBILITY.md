# Phase 2 — "to source" feasibility log (Southeast Asia)

The core Phase-2 question (Adrian's): *can we realistically go to source with country-level
programme data, country by country?* The honest answer is **it varies sharply** — this log
records what national HIV data is actually accessible per country, and where a connector was
built. National-data openness is itself a finding.

| Country | National source | Access | Status |
|---|---|---|---|
| **Thailand** | HIV Info Hub "Data Mart" (DDC/MOPH → NAP/NHSO) | **Open, public, structured** (JSON endpoint) | ✅ **Connector built** (`th_hivhub`) |
| **Vietnam** | VAAC (vaac.gov.vn) · HIV INFO 4.0 | Portal **down/unreachable**; surveillance **gated** | ⛔ **Aggregator-only** (no to-source feed) |
| **Philippines** | DOH Epidemiology Bureau quarterly surveillance report | **Open, born-digital PDF** with a clean regional 95-95-95 cascade annex (2025+) | ✅ **Connector built** (`ph_doh_cascade`) — national cascade (sum-of-regions) |
| **Malaysia** | data.gov.my (API) · MoH GAM Country Progress Report | Open portal = UNAIDS-derived incidence only; national report **= the GAM submission = already in UNAIDS** (redundant) | ⛔ aggregator-only (re-tested 2026-07-19) |
| **Indonesia** | SIHA (siha.kemkes.go.id) / satudata / data.go.id | SIHA times out; satudata bot-blocked; data.go.id API unresponsive | ⛔ aggregator-only |
| **Cambodia** | NCHADS "Boosted CoPCT" quarterly report | **Open, born-digital PDF tables** (ART/VCCT reports are scanned) | ✅ **Connector built** (`kh_nchads_copct`) — key-population cascade |
| **Laos** | CHAS / HIVCAM database | HIVCAM = national cascade DB (gated); public = PDF/aggregator | ⏳ lead: HIVCAM access |
| **Myanmar** | National AIDS Programme (NAP) M&E | Gated; + post-2021 political disruption | ⏳ lead: NAP access |
| **Timor-Leste** | DHIS2 case-based surveillance (2023) | New DHIS2 system (has an API); likely login-gated; tiny epidemic | ⏳ lead: check DHIS2 API |

**Reframe:** all 9 countries HAVE a national programme cascade database (NAP/HIV INFO/SIHA/MyHDW/HARP/HIVCAM/NAP-MM/DHIS2). The data exists universally; the barrier is **access**, and access comes in three grades: (1) an **open structured feed** (Thailand's Data Mart API); (2) an **open born-digital report** whose tables are deterministically extractable (Cambodia's CoPCT PDF); (3) a **gated DB** that releases only scanned PDFs or aggregator feeds (the rest). For grade-3 countries the realistic route is an **institutional data-sharing agreement** (via Adrian / PEPFAR / academic channels), not public scraping.

**Pattern (the headline finding): open structured national HIV data is the EXCEPTION in SEA,
but "to source" is realistic wherever the data is open — via more than one mechanism.**
**Three national cascades + one community layer are now built**, via three routes: Thailand
via a live JSON API (national cascade), Cambodia via born-digital PDF-table extraction (KP
cascade), Philippines via born-digital PDF-table extraction (national 95-95-95 cascade), plus
Indonesia via a community-led-monitoring API (service disruption; see addendum). This refines
the earlier "PDF = dead end" read on two axes:
  1. *Scanned* PDFs (Cambodia's own ART/VCCT reports) stay out of scope — we don't OCR — but
     *born-digital* PDFs with structured tables are fair game with integrity checks.
  2. A born-digital re-test only *helps* where the national report carries data **beyond** what
     already flows to the aggregators — sub-national, more-timely, KP-specific, or programme-flow.
     Philippines qualifies (its quarterly surveillance report ≠ its GAM submission — richer,
     regional, quarterly). **Malaysia does not**: its national report *is* the GAM Country
     Progress Report, i.e. the exact UNAIDS feed we already ingest — re-testing it born-digital
     changes nothing because the data is redundant, not because of the file format.
So "going to source" is realistic *country by country where the data is open AND additive*, not a
uniform regional method — an evidence-based, nuanced yes-for-some that answers Adrian's "is there
potential here?"

---

## Thailand — ✅ built

- **Source:** HIV Info Hub Data Mart — a queryable National AIDS Program (NAP/NHSO) KPI
  database, publicly reachable, backed by a JSON endpoint
  (`officer/dashboard/get-rdqa.php`, reverse-engineered).
- **Extracted (national, 2021–2025):** currently on ART, know-status count, virally suppressed
  count, new diagnoses (HIV+), PrEP recipients — summed across the 77 provinces.
- **Validation:** reconciles with the aggregator layer — e.g. on-ART 2023 = 441,635 (NAP) vs
  480,000 (UNAIDS); the ~8% gap is national-programme vs modelled-estimate, itself informative.
  The national source is also **more timely** (has 2025 where UNAIDS stops).
- Connector: `hivimpact/connectors/country/thailand_hivhub.py` (`source_id=th_hivhub`).

## Vietnam — ⛔ aggregator-only

- **VAAC (vaac.gov.vn):** unreachable. `ERR_CONNECTION_CLOSED` / connection refused from
  Anthropic infrastructure **and** from a browser in Bangkok *with a Vietnam VPN* — so the site
  is down/unavailable, not merely geoblocked.
- **HIV INFO 4.0:** the national case-surveillance system (CDC/PATH-built, OpenHIM/OpenSearch)
  is patient-level and **officer-gated** — not a public aggregate feed.
- **Open-data portals:** `data.gov.vn` / `dulieu.gov.vn` do not resolve; GSO has no HIV cascade.
- **Conclusion:** no accessible public structured national HIV source. Vietnam is served by the
  aggregator layer (UNAIDS / WHO / OECD) already in the panel. Revisit if VAAC comes back online
  or a public dashboard appears.

## Philippines — ✅ built (national 95-95-95 cascade, born-digital PDF)

*Originally logged as PDF-limited/aggregator-only — REOPENED and built 2026-07-19 once the
Cambodia work established that born-digital PDF-table extraction is legitimate.*

- **Source:** the DOH Epidemiology Bureau's quarterly **"HIV & AIDS Surveillance of the
  Philippines"** report (mirrored on ship.ph). It's a born-digital infographic PDF; pages 1-6
  are graphics (not usable), but the **Annex** carries a clean **"HIV Care Cascade by Region"**
  table — 18 regions × the full 95-95-95 columns (estimated PLHIV, diagnosed, on ART, VL tested,
  VL suppressed, with each stage's %). Present from the **2025** reports onward (2024 reports
  carry the national cascade only in infographic prose, which we don't parse).
- **Extracted:** estimated PLHIV → `plhiv`; diagnosed → `know_status_count`; on ART →
  `on_art_count`; VL suppressed → `viral_suppression_count`. Emitted **both per-region**
  (`admin1`=region code — 18 regions × 4 indicators) **and national** (`admin1=""`, sum of
  regions). 2025 (Q4 snapshot, national): PLHIV 252,700 · diagnosed 152,344 · on ART 97,983 ·
  suppressed 56,272. Cascade is a *snapshot* (as-of quarter end), so annual = latest quarter.
  The regional layer is a genuine **sub-national / small-area** signal no aggregator carries —
  it required adding a first-class `admin1` field to the panel schema (Thailand/Cambodia province
  data can use it too later).
- **Integrity (anti-contamination):** the annex prints BOTH counts and percentages, so for every
  region we verify the printed % against the computed one (`round(100·diagnosed/est)==Dx%`, etc.)
  and require national cascade monotonicity — if the printed % doesn't match, the column mapping
  drifted and we skip. (Analogue of Thailand's grand==male+female / Cambodia's TOTAL==zone-sum.)
- **Honest caveat:** national-here = **sum-of-regions**, which runs ~0.6–3% *below* the report's
  headline national (e.g. diagnosed 152,344 vs 153,207) because some cases are nationally
  unallocated (unknown region). The exact headline lives only in the infographic prose. Tagged as
  sum-of-regions in `extra`. Still adds value the aggregators lack: **more timely** (2025 quarterly
  vs UNAIDS' annual lag) and **sub-national-derived**.
- **Access:** auto-discovers report PDFs via the ship.ph **WordPress REST API**
  (`/wp-json/wp/v2/media?search=surveillance`), caches into `data/raw/philippines/`; local files win.
- **Time-depth caveat:** the regional annex only exists from 2025, so the series is currently thin
  (2025; grows one snapshot per year). `data.gov.ph` remains bot-blocked (405) and OHASIS (the
  national registry) still has no public dashboard/API (DOH says one is only "a priority").
- Connector: `hivimpact/connectors/country/philippines_doh.py` (`source_id=ph_doh_cascade`).

## Cambodia — ✅ built (key-population cascade, born-digital PDF)

- **Source:** NCHADS (National Center for HIV/AIDS, Dermatology and STD) publishes a quarterly
  **"Boosted CoPCT"** (Continuum of Prevention to Care and Treatment) report. It is **born-digital**
  (real text layer, not a scan) with clean province-level tables, **one page per key population**:
  Female entertainment workers (→ `sex_workers`), MSM (→ `gbmsm`), Transgender (→ `transgender`).
- **What made it viable (vs the other PDF-only countries):** NCHADS's *ART* and *VCCT* quarterly
  reports are **scanned images** (0 text chars — would need OCR, which we don't do). The *CoPCT*
  report is the exception: born-digital tables that `pdfplumber` extracts deterministically. So
  Cambodia is a build **not despite** being PDF-only but because *this specific* report is machine-
  readable. This is the case that refined the pipeline's "no PDF" rule into "no *scanned* PDF."
- **Extracted (national, 2023–2025), per key population:** reached (outreach) → tested → newly
  HIV-positive → newly enrolled on ART. Quarterly **flows**, summed to annual (`n_quarters`
  recorded so partial recent years stay visible — that's where the funding-cut signal is).
  Example (2025, MSM): reached 231,192 · tested 120,258 · positive 1,293 · ART-enrolled 1,287.
  Coverage: **2022 / 2024 / 2025 complete (4/4 quarters)**; 2026 Q1 already available; **2023
  partial (2/4)** — its Q3 report was published only as a *scanned* PDF (skipped, logged) and no
  Q4-2023 was found. Partial years are tagged `n_quarters` so a thin year is never mistaken for
  a real decline. Quarter detection also handles reports that omit the "Q" and print only a month
  range (e.g. "(Oct-Dec)" → Q4), which recovered Q4-2022.
- **Extraction integrity (anti-contamination):** the national figure is the report's own printed
  **TOTAL** row — never recomputed — guarded by a check that `TOTAL == NORTHERN ZONE + SOUTHERN
  ZONE` (the two zone subtotals), analogous to Thailand's `grand == male+female`. Columns are
  located by **header name**, not position, which proved essential: page order varies across
  quarters (some files lead with a scanned cover, Q2-2025 puts FEW on page 1, Q3-2025 leads with
  the KP-aggregate) — a fixed page/column index would silently mis-assign totals; the title/header
  approach maps every page correctly. The one born-digital artifact (stray intra-number spaces,
  `"8 23"→"823"`) is stripped deterministically; no digit is ever guessed.
- **Validation note (honest):** unlike Thailand, there is **no aggregator equivalent** for a 1:1
  numeric cross-check — UNAIDS/PEPFAR do not publish Cambodia KP *quarterly reached/tested* flows.
  That absence is itself the value of going to source. Validation is therefore (a) internal
  integrity (TOTAL == zone-sum, cascade monotonicity — both pass on all pages), and (b) loose
  order-of-magnitude plausibility vs UNAIDS KP estimates. Rows are tagged `reconcile_with` for the
  coming reconciliation layer to flag, never trust blindly.
- **Access:** the connector **auto-discovers** the quarterly CoPCT PDFs from the NCHADS
  quarterly-report category pages and caches them into `data/raw/nchads/`; any PDFs already there
  win (vetted/offline mode). So the user just runs the pipeline — same one-command experience as
  Thailand's live API.
- Connector: `hivimpact/connectors/country/cambodia_nchads.py` (`source_id=kh_nchads_copct`).

---

## Addendum — Community-Led Monitoring (CLM): scoped, one source built

**Question:** is CLM data (civil-society monitoring of service *disruption* — stockouts, clinic
access, treatment interruption) machine-readable enough to connect, and does it complement the
funding-cut-impact signal? It's in Adrian's document and is arguably the most *direct* impact
signal (KP-facing services are the first cut).

**Scoping finding:** almost all CLM output is unstructured — ITPC's Community Treatment
Observatory model is West-Africa reports/PDF, APCASO/APN+ are advocacy networks, amfAR's CLM
output is white papers, and the raw collection layer (KoboToolbox) is login-gated. **One source
is machine-readable:**

### CLM Asia — ✅ built (Indonesia sentinel; `source_type=community_led_monitoring`)

- **Source:** `data.clm-asia.org` — the amfAR TREAT Asia / ITPC "Community-Led Monitoring in
  Asia" dashboard. A public D3/billboard.js dashboard backed by an **unauthenticated JSON API**
  (reverse-engineered the same way as Thailand's Data Mart):
  `GET /api/?component=indicator_data_table&CC=AA&ind=<IND>&year=<Y>&period=Q<n>&level=FACILITY`.
- **Extracted (Indonesia, `SNU1='ID'`; India is out of SEA scope):** quarterly service-user /
  facility survey indicators, pooled to a country proportion (numerator + denominator retained):
  ARV stockout, treatment interruption, out-of-pocket payment, facility open-on-time, enough
  staff, stigma, psychosocial-support availability, knows-own-viral-load. Quarterly 2023 Q1 →
  2026 Q3; pooled to annual with `n_quarters`. Example (Indonesia 2024): ARV stockout 0.31%,
  stigma 0.0%, knows-VL 97.9%, out-of-pocket 11.7%, treatment interruption 11.9% — a healthy
  pre-cut baseline; the funding-cut signal is these moving over 2024→2026.
- **What it is / isn't:** a **sentinel** sample (a handful of Jakarta-area facilities), **not
  nationally representative** — a ground-truth *disruption* layer tagged
  `community_led_monitoring`, never a cascade. Each row's `extra.higher_is` says whether a rising
  value is good or bad. **No** aggregator cross-check (it's a distinct signal) — that's the point.
- **Not available:** the dashboard defines KP-disaggregated facility counts
  (`BQ__death_*`, `BQ__elig_treat_*` by MSM/PWID/SW/TG) but they are **unpopulated in the public
  API** (verified empty every quarter), so they are not emitted. Revisit if they populate.
- Connector: `hivimpact/connectors/clm_asia.py` (`source_id=clm_asia`), live API, self-filters
  to Indonesia. Runs with the pipeline (no download).
