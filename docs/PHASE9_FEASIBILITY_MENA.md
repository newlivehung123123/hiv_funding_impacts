# Phase 9. Feasibility log for HIV data sources in the Middle East and North Africa

The Phase 9 log records the search for HIV data sources in the 14 countries of the Middle East and North Africa (MENA) region of hivimpact/config/regions.py. The search ran on 28 October 2026 under the method of docs/PHASE4_FEASIBILITY_WCA.md and the grades of docs/ACCESS_LADDER.md, in two probe passes of the national health ministry and statistics hosts of every country and a regional pass. The working notes of the search sit in research/phase9_mena/mena_round1_notes.md, and the rulings sit in research/rulings_2026-10-15.md as R75, R76 and R77.

## The gap the search set out to fill

The panel held aggregator rows for all 14 MENA countries on 28 October 2026, from 186 rows for Palestine to 2,859 rows for Djibouti. No MENA country held a national series of notified HIV cases read from a national publisher, and the Lebanese rows held no `notified_hiv_cases` and no `new_diagnoses` row, with `art_initiations` rows from the aggregators only.

## Built, Lebanon (R75)

- Source. The Statistical Bulletins of the Lebanese Ministry of Public Health (MoPH), 2006 to 2018, served as PDF files on www.moph.gov.lb. Every bulletin from 2007 prints a table of the cases reported to the National AIDS Program (NAP) of the ministry during the year.
- Connector. lb_moph_bulletin, hivimpact/connectors/country/lebanon_moph.py, connector 76 of the registry. The connector reads the bulletins for 2007, 2009 and 2014 to 2018.
- Rows. 23 national rows. `notified_hiv_cases` for 2007 (92), 2009 (97), 2014 (109), 2015 (113), 2016 (108), 2017 (205) and 2018 (160), by sex for 2007 and 2014 to 2018, and `art_initiations` for 2014 (114), 2015 (140), 2016 (150) and 2017 (186).
- Gates. Exactly one table page in every bulletin, the stages of disease summing to the printed total, men and women summing to the printed total, and every printed percentage within 0.6 points of the count over the total.
- Not read. The 2006 bulletin is a scan, the 2008 bulletin prints no NAP table in the text layer, the bulletins for 2010, 2011 and 2013 count cases up to November, and the 2012 bulletin prints the total in glyph codes of an embedded font. The 2018 ART figure counts people started up to November, and 2018 gives no `art_initiations` row.
- Open question carried in every row. No bulletin states whether the counts cover residents of other nationalities, and the 2017 bulletin says the printed rate covers the Lebanese population only.

## Routes not carried or not reached (R76)

- Algeria. www.insp.dz, www.ons.dz and www.sante.gov.dz timed out. NOT REACHED.
- Djibouti. INSTAD, the statistics institute, serves a JavaScript application with no table in the page, and reading the interface behind the application would be a switch of tool under R16. sante.gouv.dj gave no reply to the second probe. NOT REACHED.
- Egypt. CAPMAS, the statistics agency, serves a JavaScript application of 1,421 bytes, and www.mohp.gov.eg timed out. NOT REACHED.
- Iran. amar.org.ir gave an empty reply, and icdc.behdasht.gov.ir and behdasht.gov.ir timed out. NOT REACHED.
- Iraq. moh.gov.iq returned a Cloudflare block page, BLOCKED with no workaround. COSIT, the statistics organisation, publishes no health section, NOT CARRIED.
- Jordan. www.moh.gov.jo and dosweb.dos.gov.jo timed out. NOT REACHED.
- Lebanon beyond the bulletins. The notifiable disease tables of the Epidemiological Surveillance Unit carry no HIV row, and the NAP page of the ministry holds no data file. NOT CARRIED.
- Libya. The AIDS and STI department page of the National Centre for Disease Control lists branch offices only, NOT CARRIED. bsc.ly, the Bureau of Statistics and Census, gave no reply to the second probe, NOT REACHED.
- Morocco. www.sante.gov.ma failed to connect, NOT REACHED. The statistical yearbook page of the High Commission for Planning (HCP) leads to a missing-page error, and the HCP report on the Sustainable Development Goals quotes only a cumulative count of notified cases to the end of 2014, NOT CARRIED.
- Palestine. www.pcbs.gov.ps timed out at the name lookup, and site.moh.ps and www.moh.ps gave no network address. NOT REACHED.
- Sudan. fmoh.gov.sd redirects to itself, and cbs.gov.sd timed out at the name lookup. NOT REACHED.
- Syria. cbssyr.sy now carries a parked-domain page, and www.moh.gov.sy timed out. NOT REACHED.
- Tunisia. The statistical yearbook for 2019 to 2023 of INS, the statistics institute, holds no match for HIV, VIH, sida or the Arabic words for AIDS, NOT CARRIED. www.santetunisie.rns.tn gave no network address, NOT REACHED.
- Yemen. www.mophp-ye.org returned a server error, and the Central Statistical Organisation site carries no health or yearbook link. NOT REACHED.
- Regional. rho.emro.who.int, the regional health observatory of the WHO Regional Office for the Eastern Mediterranean (EMRO), returned a missing-page error, data.unescwa.org returned HTTP 403, and the EMRO DHIS2 tool asks for an account. NOT REACHED.

## Closure (R77)

Every reachable MENA source holds a BUILT, NOT CARRIED or NOT REACHED ruling, and under R47, R60 and R66 a host which cannot be reached keeps no country open. Lebanon is read at source, and Algeria, Djibouti, Egypt, Iran, Iraq, Jordan, Libya, Morocco, Palestine, Sudan, Syria, Tunisia and Yemen are covered by the aggregators only. The region page goes live once the lb_moph_bulletin run has written the Lebanese rows to the panel.

## Downloads of 28 October 2026

| File | Source | Bytes |
|---|---|---|
| Statistical bulletins 2006 to 2018, 13 PDF files | www.moph.gov.lb | 2,932,121 to 18,555,252 per file |
| annuaire-2023avec lien.pdf, the yearbook for 2019 to 2023 | www.ins.tn | 16,233,493 |
| Home and listing pages of COSIT, INSTAD, NCDC Libya, CSO Yemen, INS Tunisia, CBS Syria and HCP Morocco | the hosts named | 969 to 1,691,570 per page |
