# MENA assessment notes, started 28 October 2026 (30 per cent weekly at start, pause at 36)

LAC handed over: S/push_lac.zsh (three commands, zsh -n ok, guards tested, pe_cdc_sala in CONNECTORS, 75 connectors). Photograph request sent for 64 countries (41 open plus 23 LAC).
Panel rows (aggregators) for every MENA country: DJI 2859, DZA 2595, EGY 2778, IRN 517, IRQ 831, JOR 908, LBN 1325, LBY 2492, MAR 1586, PSE 186, SDN 2780, SYR 1455, TUN 2846, YEM 2654.

## Probes of 28 October 2026 (curl, Safari user agent, 15 to 25 s)
- LBN MoPH www.moph.gov.lb 200. ESU notifiable disease tables (by caza, month, age, sex, Esu_currentyear/*.htm) carry no HIV row (gonorrhoea, syphilis only). NAP page /en/Pages/2/1313/aids has no data file. Statistical Bulletins 2006 to 2018 at /en/DynamicPages/page_download_file/<id> (2018 id 2896, 2017 id 2537). Downloaded S/dl_lb1/STATISTICALBULLETIN2018.pdf 3,020,952 bytes sha ccbc0f67a187, 68 pages. Table D.1 p44 (printed 42), NAP source: 160 incident cases 2018, HIV 106, AIDS 33, not specified 21, males 151, females 9, age groups, mode, ART new to November 168, cumulative 1,479. Graph D.6 2013-2018 totals 109 108 113 119 150? 160? (graph text order unclear). National only.
- IRQ moh.gov.iq 403 Cloudflare "Sorry, you have been blocked" -> BLOCKED. COSIT cosit.gov.iq/ar/ 200 (statistical summaries, household survey 2024).
- JOR www.moh.gov.jo and dosweb.dos.gov.jo connect timed out 15 s -> NOT REACHED.
- MAR www.sante.gov.ma failed to connect (port 443, 8 s) -> NOT REACHED. HCP www.hcp.ma 200.
- IRN amar.org.ir empty reply, icdc.behdasht.gov.ir and behdasht.gov.ir timed out -> NOT REACHED.
- PSE www.pcbs.gov.ps resolve timed out, site.moh.ps and www.moh.ps no DNS -> NOT REACHED.
- EGY CAPMAS 200 but JavaScript app (1,421 bytes), www.mohp.gov.eg timed out.
- TUN www.ins.tn 200, www.santetunisie.rns.tn no DNS.
- DZA www.insp.dz, www.ons.dz, www.sante.gov.dz timed out -> NOT REACHED.
- DJI instad.dj 200 (4,309 bytes), sante.gouv.dj 200 (news pages).
- LBY ncdc.org.ly 200 (Ar), bsc.ly 200 (WordPress).
- SDN fmoh.gov.sd 302 to itself, cbs.gov.sd resolve timed out.
- SYR cbssyr.sy 200, www.moh.gov.sy timed out.
- YEM www.mophp-ye.org 500 WordPress error, www.cso-yemen.com 200.
- Regional: rho.emro.who.int 404 at root, data.unescwa.org 403.

## LBN bulletins (downloaded 28 Oct, S/dl_lb1/b<year>.bin, ids 2006 424, 2007 425, 2008 426, 2009 427, 2010 420, 2011 1159, 2012 429, 2013 1000, 2014 1611, 2015 1871, 2016 2000, 2017 2537, 2018 2896)
Sizes and sha256 prefix: 2006 2,932,121 b23525b829b4; 2007 5,425,747 a1f0c75f995d; 2008 18,555,252 5a74744ab661; 2009 5,183,649 de7449fd893b; 2010 4,882,899 f8583e627e2d; 2011 3,460,946 c7a91697a7d5; 2012 854,691 796646478871; 2013 3,881,030 acd78b711e6e; 2014 4,489,248 c447bb00bf18; 2015 4,307,091 194a831771c9; 2016 3,751,074 8e6a5f32c3f2; 2017 3,024,802 14e64ca6b248; 2018 3,020,952 ccbc0f67a187.
Table D.1 (NAP) values: 2009 97 (74 HIV + 23 AIDS, "during 2009", sex in per cent only); 2010 93 "up to November"; 2011 109 "up to November"; 2012 total in cid glyph codes (unreadable); 2013 119 "up to November" (M 105 F 14); 2014 109 (M 100 F 9, stages 42+38+29); 2015 113 (97, 16); 2016 108 (100, 8); 2017 205 (193, 12, stages 123+56+26); 2018 160 (151, 9, stages 106+33+21). ART new 2014 114, 2015 140, 2016 150, 2017 186; 2018 168 "until November"; cumulative ever 764, 841, 980, 1304, 1479. 2006-2008 no table page found by the filter.
Panel LBN has no notified_hiv_cases and no new_diagnoses (55 indicators, art_initiations present).
Plan: connector lb_moph_bulletin, notified_hiv_cases national 2009, 2014-2018, by sex 2014-2018 (gate M+F = total, stages sum = total), art_initiations 2014-2017. Partial years and 2012 NOT CARRIED.

## Lebanon connector BUILT (28 Oct, 31 per cent weekly)
- hivimpact/connectors/country/lebanon_moph.py, source_id lb_moph_bulletin, registered in country/__init__.py (CONNECTORS 76).
- Offline test on S/lb_raw (symlinks to S/dl_lb1) with network blocked: 23 rows, validate []. notified_hiv_cases all 2007, 2009, 2014-2018, male and female 2007 and 2014-2018, art_initiations 2014-2017.
- 2009 contents page carries the caption without "Table of Contents" text, fixed by requiring Male or Males on the table page.
- Negative test, 2013 file named as 2014: fingerprint WARNING and refused, 0 rows.
- Run command S/push_lbn.zsh, zsh -n ok, DNS guard ok, panel guard tested on S/guardlb (0 rows exit 1, 23 rows exit 0), host answered 200 with 5,425,747 bytes for id 425.
- NEXT: MENA probes COSIT, CSO Yemen, INSTAD, Djibouti MoH, NCDC Libya, BSC, INS Tunisia, CBS Syria, HCP Morocco, CAPMAS. Then SOURCE_META, rulings R75 onward, doc, regions.py.

## MENA probes, second pass (28 Oct, 32 per cent weekly)
- IRQ COSIT cosit.gov.iq/ar/ 200 (162,297 bytes): menu has agriculture, industry, trade, population, living conditions, environment, prices, human development, welfare, displaced, surveys. No health section, no statistical abstract link. Health statistics belong to MoH (moh.gov.iq Cloudflare block). -> NOT CARRIED (no HIV table at COSIT), MoH BLOCKED.
- MAR HCP www.hcp.ma/downloads/Annuaire-statistique-du-Maroc_t11878.html redirects to www.wmaker.net/404.html (969 bytes). Web search found the HCP SDG report (odd.hcp.ma/attachment/636506) quoting MoH cumulative notified cases to end 2014 (10,017), cumulative only. sante.gov.ma failed to connect. -> NOT REACHED (MoH), HCP NOT CARRIED (cumulative quote of MoH figures, no annual series).
- TUN INS: /publication lists Annuaire statistique de la Tunisie 1995-2001 to 2019-2023. Downloaded S/dl_tn1/annuaire_2019_2023.pdf (annuaire-2023avec%20lien.pdf, 16,233,493 bytes, sha 45ee5d23797e, 332 pages, text layer present, health chapter infrastructure and reproductive health). No match for sida, VIH, HIV or the Arabic AIDS words. -> NOT CARRIED (no HIV table). santetunisie.rns.tn no DNS -> NOT REACHED.
- SYR cbssyr.sy now a parked domain (43,757 bytes, northwavepoint ad script, no content). -> NOT REACHED. moh.gov.sy timed out.
- LBY NCDC ncdc.org.ly/Ar/ 200 (1.69 MB). Tag 7 (AIDS and STI control department) page lists only branch offices, no report. -> NOT CARRIED (no HIV table found). BSC not probed further.
- DJI INSTAD instad.dj is a Nuxt JavaScript application (4,308 bytes, no links in the HTML). Reading the API behind the app would be a tool switch (R16). -> NOT REACHED. sante.gouv.dj answered 200, not searched.
- YEM CSO www.cso-yemen.com 200 (113,612 bytes, 54 links), no health or yearbook link. mophp-ye.org WordPress 500. -> NOT REACHED.
- EGY CAPMAS JavaScript application of 1,421 bytes (R16), mohp.gov.eg timed out. -> NOT REACHED.
- Downloads this pass: S/dl_tn1/annuaire_2019_2023.pdf 16,233,493 bytes from www.ins.tn. Pages (html) in S/dl_mena1, S/dl_mena3, S/dl_tn1.
- NEXT: rulings R75 (LBN BUILT), R76 (MENA routes NOT CARRIED, NOT REACHED, BLOCKED), R77 (MENA closure: LBN at source, 13 aggregator-only). Then SOURCE_META lb_moph_bulletin, docs/PHASE9_FEASIBILITY_MENA.md (phase number check), regions.py, site copy. Pause at 36 per cent.

## Rulings written (28 Oct, 32 per cent weekly)
- R75 (LBN BUILT), R76 (MENA routes), R77 (MENA closure, LBN at source, 13 aggregator-only) appended to research/rulings_2026-10-15.md, lines 814 to 847. Next ruling R78.
- Second probe of sante.gouv.dj and bsc.ly gave no reply (curl 000), recorded in R76.
- NEXT: SOURCE_META lb_moph_bulletin in build_site.py, docs/PHASE?_FEASIBILITY_MENA.md (check phase numbering in regions.py), regions.py MENA LIVE with phase and note, site copy (AT_SOURCE LBN, COUNTRY_COPY LBN, REGION_COPY MENA, FEASIBILITY_LATER MENA rows), home.html and about.html counts, then a tested build and deploy command for Jason (S/push_mena.zsh). Pause at 36 per cent.

## Site work done (28 Oct, 33 per cent weekly)
- build_site.py patched by S/tools_whohts/patch_mena.py (SOURCE_META lb_moph_bulletin, AT_SOURCE LBN, COUNTRY_COPY LBN, FEASIBILITY_LATER MENA with 14 rows, REGION_COPY MENA), py_compile ok, no new line over 99 characters, prose clean.
- regions.py MENA LIVE, Phase 9, note "Lebanon is read at source." README Phase 9 line, home.html region list (all eight published), about.html 42 connectors and MENA assessment closed.
- docs/PHASE9_FEASIBILITY_MENA.md written, notes copied to research/phase9_mena/mena_round1_notes.md.
- S/push_lac_mena.zsh replaces S/push_lac.zsh and S/push_lbn.zsh (the LAC build check for "Seven regions published" would now fail). Four commands. zsh -n ok, DNS guards ok, panel guard tested on four scratch panels, footer and kicker rendered offline with the real region list ("Phase 9 &nbsp;·&nbsp; Eight regions published").
