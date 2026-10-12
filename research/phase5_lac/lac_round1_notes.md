# LAC round one notes (working file, scratchpad only)

## Panel facts
- new_diagnoses in panel for LAC = PEPFAR modality/panorama programme counts + Global Fund programme counts only.
  BRA 2024 PEPFAR 1,156 vs PAHO national 39,216. HTI 2021 GF 14,954, PEPFAR 14,983, PAHO 13,940.
  PRY only GF 2021-23 (572, 676, 620) vs PAHO 1,318, 1,519, 1,651.
- No national surveillance new-diagnosis series in panel for any LAC country.

## PAHO Interactive HIV Data Dashboard (key 972060bb..., model 3093636, refreshed 2026-10-01)
- Nuevos diagnosticos = PAHO Core Indicator 93/94/95 (count), country surveillance, 1995/2008-2025.
  data_source_type varies by year (Public Health Surveillance, Disease specific register, Administrative registry).
  COL = Cuenta de Alto Costo register. BRA 2018-19 = SINAN notification, 2024 preliminary=2.
  ANOMALY: HTI rows 2018-2024 carry data_provider_specific "Ministry of Health of Guyana. NAPS" (mislabel in PAHO table).
  Counts HTI 19,041 (2018) ... 13,554 (2024); GUY 772 ... 528. Different, so mislabel is in the provider string only.
- Personas en TAR = GAM republication (2025 equals WHO GHO exactly; BRA 2022-24 revised upward vs GHO).
- DTG table: ART by line and on DTG by line, age 10+ and <10, 2020-2025, 31 countries. Additive (no regimen indicator).
- PrEP table: 2019-2025 by country name. Not yet compared.

## PAHO Core Indicators (one model 3091957 behind four reports, refreshed 2026-10-04)
- Reports: CI Dashboard-Latest data EN (8d6e4cfa), Indicator profile (e0b51f56), Country profile (e2167348), Country comparison (0bcf5404).
- Indicators_Data_2022 holds all values. database_status 1 share, 2 input, 3 review, 4 reference only, 5 discontinued.
- 84-86 HIV mortality age-adjusted, 87-89 crude rate: "Rates calculated by PAHO/WHO" from WHO Global Health Estimates
  2000-2021 (modelled) / UN WPP 2024. NOT vital registration. All 23 LAC 2000-2021, n=22 each. NEGATIVE: modelled.
- 1076 ART proportion: source "UNAIDS/WHO". NEGATIVE: duplicate of UNAIDS.
- 93-96 new diagnoses (count; total, F, M, unknown), status 2 (input for calculation), data_collection_process "DHIS2".
- 98-101 new diagnoses rate and sex ratio: EIH calculation on country data (derived from 93 / population).
- 1208/1209 SDG 3.3.1 variants, status 6 (not in status table).
- Zip: paho-core-indicators-2026-20261001.zip, 5.5 MB, 157 MB CSV. Not downloaded. Power BI route reads the same table.

## PAHO PrEP table vs panel
- Matches UNAIDS AIDSinfo after rounding: MEX 2023 14,380 vs 14,000; MEX 2024 30,707 vs 31,000; HTI 2024 33,375 vs 33,000;
  ARG 2023 3,927 vs 3,900; COL 2024 9,660 vs 11,000 (differs); GTM 2022 7,469 vs 16,000 (differs); BRA 2024 158,994 vs 170,000.
- = GAM country report, unrounded, plus 2025. Mostly duplicate; additive only as 2025 and exact values. Country names only, no ISO3.
  28 countries incl. Chile, Uruguay, small Caribbean states.

## WHO Mortality Database (registered deaths, ICD-10 by country VR)
- API: https://apps.who.int/data/mortality/api/EN/facts/query?queryJson=<base64>. Indicator CG0090 = HIV/AIDS.
  Filters Indicator, Country, AgeGroup (Age_all); divisionFactors Year (values must exist, 2025 breaks it), Sex ("0" all, 1 M, 2 F, 9 unk).
  Other endpoints: dimensions/years, dimensions/countries-with-regions, facts/country-indicator-metadata?queryJson=...&indicatorCode=CG0090.
  Fact "Number" (also rate per 100 000 and % of deaths). Age groups also 5-year (ageGroupType=2).
- Coverage, all ages both sexes: ARG 1997-2023 (1,102), BLZ 1997-2022 (71), BRA 1996-2022 (11,133), COL 1997-2023 (2,232),
  CRI 1997-2022 (165), CUB 2000-2021 (406), DOM 1996-2018 (707), ECU 1997-2022 (586), SLV 1997-2018 (169), GTM 2000-2023 (190),
  GUY 1991-2020 (103), JAM 2000-2014 n=13 (595), MEX 1998-2022 (4,828), NIC 2005-2022 (169), PAN 1998-2022 (378),
  PRY 2000-2021 (275), PER 1999-2022 (1,221), SUR 1995-2014 (96), TTO 1999-2020 (156), VEN 1996-2016 (2,496).
  NONE: BOL, HTI, HND.
- Panel has no registered deaths; aids_deaths is modelled (UNAIDS, WHO GHO). Registered differs: MEX 2022 4,828 vs UNAIDS 4,100,
  WHO 5,200; COL 2023 2,232 vs 3,100; GUY 2020 103 vs 200; CUB 2021 406 vs 500. ADDITIVE, needs a new indicator id.
- Never used anywhere in the repo (grep: no "mortality database", no "vital regist").
- Data quality: MDB publishes usability/completeness per country (not yet read).

## Colombia datos.gov.co (Socrata), enumerated by category "Salud y Protección Social" (1,338 items)
- 4hyg-wa9d "Datos de Vigilancia en Salud Pública de Colombia" (INS SIVIGILA, updated 2024-10-17).
  Columns cod_eve, nombre_evento, semana, ano, cod_dpto_o, cod_mun_o, departamento_ocurrencia, municipio_ocurrencia, conteo.
  Event 850 "VIH/SIDA/MORTALIDAD POR SIDA", 2008-2022, 59,233 rows, by department and municipality of occurrence, weekly.
  National sums: 2008 6,110; 2010 7,009; 2015 10,357; 2018 14,474; 2019 17,346; 2020 13,605; 2021 17,876; 2022 19,183.
  2022 has 33 departments plus EXTERIOR (417, abroad). Bogotá 3,915; Antioquia 2,825; Valle 2,297.
  Event 850 merges HIV, AIDS and AIDS death notifications in one count (status at notification).
  ADDITIVE at admin1: COL has zero admin1 rows in the panel. Open API, grade 1.
- qvnt-2igj SIVIGILA 2019 (17,346) and fhc4-jjti DA-SIVIGILA 2021 (17,876) equal 4hyg-wa9d exactly. NEGATIVE: duplicates.
  84d4-vfax (2017) and xd2n-cu8j (2018) assumed the same series, not separately checked.
- 4e4i-ua65 "Indicadores mortalidad y morbilidad" 2005-2020: 30 indicators, none on HIV (maternal, child, fertility). NEGATIVE.
- 4k9h-8qiu RIPS (MinSalud, updated 2022-06-09): departamento, municipio, a_o, tipoatencion, diagnostico (ICD-10), numeroatenciones.
  2009-2021, 38M rows. B20-B24 rows exist (consultations, hospitalisations, procedures). Counts of service contacts, not people.
  numeroatenciones stored as text, aggregation on HIV codes times out on the server. Candidate only, weak measure.
- n4m7-xpyz "VIH - SIDA" = federated link to MEData (Medellín city) sivigila_vih.csv. Municipal, NEGATIVE for admin1.
- q4jm-feyz, 3e4s-myku = Bogotá only (one admin1 unit already inside 4hyg-wa9d). NEGATIVE as separate sources.
- i5t3-2ui7 "Recursos del Sistema General Giros" 2015-2021: transfers for the uninsured poor, no HIV line. NEGATIVE.

## Brazil
Panel position: BRA admin1 = pepfar_snu (173 rows) + pepfar_agency_snu (75), five states only, 2020-2025, PEPFAR sites only.
No BRA admin1 AIDS cases, deaths, whole-programme ART or suppression.

- dadosabertos.saude.gov.br (Ministry of Health open-data portal, Next.js over CKAN): 140 datasets ENUMERATED (page data
  /_next/data/{buildId}/dataset.json?page=N). Relevant: sim (SIM mortality microdata), ripsa-* (RIPSA indicator sets), siops.
  * RIPSA morbidity dimension 1 (incidence of communicable diseases): 14 diseases, NO AIDS or HIV indicator. NEGATIVE.
  * RIPSA mortality dimension 6: one indicator, all infectious and parasitic diseases together. NEGATIVE (not HIV-specific).
  * SIM: yearly CSV zips 1979-2024 on S3 (s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SIM/csv/Mortalidade_Geral_YYYY_csv.zip),
    record level, ICD-10 cause, state and municipality of residence. Grade 1 but each year a large file. API endpoint
    /vigilancia-e-meio-ambiente/sistema-de-informacao-sobre-mortalidade takes only limit/offset, no cause filter.
  * apidadosabertos.saude.gov.br swagger (/static/swagger.json): 109 paths, none for SINAN HIV/AIDS, SICLOM or SISCEL.
- indicadores.aids.gov.br ("Indicadores e dados básicos do HIV e aids nos municípios brasileiros", DATHI, the
  Department of HIV, AIDS, TB, Viral Hepatitis and STIs). POST municipios.php {id:02} lists 27 states; POST tabela.php
  {id2:<IBGE state code>} returns 20 HTML tables. planilha.php?id2= gives a spreadsheet. "Planilha de todos os municípios"
  = documentos/indicadoresAids.xls.
  São Paulo (35): AIDS cases 1980-2012 then yearly 2013-2024 (2023 6,490; 2024 3,055 partial), detection rate 2013-2023,
  HIV in pregnant women 2013-2024, exposed children 2015-2024, AIDS deaths 2000-2023 from SIM (2023 1,764), crude and
  standardised mortality rate, early deaths 2020-2023, by sex, race, schooling, exposure category.
  ADDITIVE for 27 states (cases and registered deaths). Open, no login. Grade 1 (HTML table per request).
- gov.br/aids Painel Integrado de Monitoramento do Cuidado do HIV e da Aids: file Banco_PIMC_2025.zip
  (http://mediacenter.aids.gov.br/Transparencia_Ativa/Banco_PIMC_2025.zip, 110,490,953 bytes, modified 2026-07-06).
  Two parquet files plus a PDF dictionary. PVHA_ano.parquet = last record per person per year 2016-2025 (SINAN notification,
  ART dispensing in SICLOM, viral load or CD4 in SISCEL). PVHA_prim.parquet = first record per person 1980-2025.
  Municipality and service with fewer than 50 people grouped. Place = service location, not residence.
  ADDITIVE: whole-programme ART and suppression for all 27 states. NOT DOWNLOADED, needs Jason's permission.
- Painel PrEP file Dados_PrEP_transparencia.zip (http://mediacenter.aids.gov.br/prep/..., 30,023,348 bytes, 2026-05-07).
  PrEP dispensing by state, municipality, service, monthly. ADDITIVE at admin1 (panel prep_recipients for BRA = PEPFAR 5 states).
- Painel PEP file Banco_PowerBI_PEP_22012025.xlsx (45,450,161 bytes, 2025-01-21). PEP dispensing by state and year.
  No PEP indicator in panel. Lower priority.
- HTTPS to mediacenter.aids.gov.br returns nothing; plain HTTP works. Sizes read from response headers only.
- indicadoresclinicos.aids.gov.br (DATHI clinical-monitoring indicators). POST tabela.php {id2:<IBGE state code>} returns
  33 HTML tables, 2009-2022 (14 yearly columns), each split by sex and age, last row "PVHA geral" (all PVHA).
  Headings: late diagnosis and advanced disease and latent TB indication; ART within one month of first CD4; median days
  first CD4 to ART; PVHA linked (vinculadas); PVHA on ART (em TARV); PVHA starting ART; CD4 at ART start; viral
  suppression; sustained suppression; adherence and loss to follow-up; retention (three years only).
  São Paulo (35) 2022: linked 190,616; on ART 168,532; started ART 11,137; suppressed 115,312 of 127,305 tested (91%);
  sufficient adherence 142,647 of 185,206 dispensed (77%); loss to follow-up 9%.
  ADDITIVE for 27 states (whole-programme ART, suppression, linkage). Open HTML, grade 1. Ends 2022; 2023 onward only in
  Banco_PIMC_2025.zip. Site JS also calls buscaCpf.php and resistencia/ (login routes), ignored.
- Federal budget lines for HIV, 2000-2026, from the orcamento.dados.gov.br SPARQL endpoint (open, no login). Full record
  under "CLASS SWEEP. Brazil federal budget lines for HIV (6 October 2026)" below. National federal lines ADDITIVE as a
  separate federal-execution indicator for 2000-2016 and 2025-2026, DUPLICATE in concept of GAM domestic_hiv_spend for
  2017-2024. Federal HIV transfers by state ADDITIVE at admin1 for 2003-2026 (27 federative units). Viral hepatitis enters
  the transfer title from 2014 and tuberculosis from 2025, so the scope of the transfer series changes in 2014 and in 2025.
  The titles of action 4370 (the national HIV medicines and care line) and of every transfer line also name other sexually transmitted
  infections, so the federal figures cover more than HIV. GRADE 1.

## Mexico
Panel position: MEX has zero admin1 rows. National on_art_count WHO GHO 2025 287,747 (all institutions); aids_deaths modelled
only; domestic spend only GAM 2013 and 2015 (no 2014).

- datos.gob.mx (CKAN, /api/3/action/*, datastore_search works, datastore_search_sql disabled). 189 organisations
  ENUMERATED. Health publishers: censida (6 packages), secretaria_salud (9), imss (3), imss_bienestar (12), issste (44),
  cnegsr (7, cancer only), insp (1, plan only). q=VIH returns only the six CENSIDA packages.
  * CENSIDA "Personas activas en sistema con Tratamiento Antirretroviral" 2022 (May-Dec), 2023, 2024, 2025 (12 months each),
    2026 (Jan-Mar so far; plan promised monthly to August, so publication lags). Datastore active. Rows = state x dispensing
    unit (CAPASITS, hospital, warehouse) x ARV product, fields consumo_arv_mensual and numero_pacientes.
    Dec 2025: 8,584 rows, 232 units, 32 states plus seven national institutes; sum numero_pacientes 175,443.
    numero_pacientes counts patients per product, so a multi-product regimen counts one person more than once
    (BIC/FTC/TAF 119,890; DTG/3TC 21,854; FTC/TDF 11,520; DRV/c 9,480; DTG 6,595). A person count needs a rule (count
    complete regimens and third agents, skip backbones and boosters). Covers the Secretaría de Salud system (uninsured)
    only, not IMSS, ISSSTE, PEMEX or the armed forces. National WHO figure 287,747 covers all.
    ADDITIVE at admin1 (MEX zero admin1) with a measurement caveat. Grade 1 (datastore API).
  * secretaria_salud registro_defunciones: record-level registered deaths 1998-2023 (one resource per registration year),
    datastore active, fields ENT_RESID, CAUSA_DEF (ICD-10, 4 characters), ANIO_OCUR etc.
    Filter CAUSA_DEF in B200..B24X on the 2022 resource: 4,847 records, 4,828 occurred in 2022 = WHO MDB 2022 (4,828)
    exactly. So the national total DUPLICATES the WHO MDB; the state split (ENT_RESID, 32 states plus 99 unknown) is
    ADDITIVE. Grade 1 (datastore filters, no download).
  * Other secretaria_salud packages (vaccines, births, pregnancy consultations, family planning, nutrition, chronic disease):
    no HIV. NEGATIVE.
  * imss deteccion_padecimientos_delegacion (13 resources, all datastore active). Resource "SIDA"
    41956511-ed2b-4ada-9a72-893e5877f5dd: 735 rows, fields delegacion, ano, detecciones. Years 2002, 2003, 2005-2023
    (2004 absent; 2008-2016 labelled "2008***" etc., footnote not given). 35 IMSS delegations (D.F. Norte/Sur, México
    Oriente/Poniente, Veracruz Norte/Sur split). Yearly sums: 2002 715,185; 2006 18,887; 2019 142,569; 2020 79,256;
    2023 93,377. Screening detections by one insurer (IMSS), definition undocumented, level shifts of 40-fold.
    WEAK candidate for hiv_tests_performed (IMSS share only, delegations need mapping to states). Grade 1.
    Verified 5 Oct 2026: numero_pacientes product totals above re-read from the Dec 2025 resource by clave_medicamento
    (6203 BIC/FTC/TAF, 7026 DTG/3TC, 4396.01 FTC/TDF succinate, 6098 DRV/c, 6010 DTG). FTC/TDF may include PrEP
    dispensing, so a person rule should not count FTC/TDF as a regimen on its own.
  * issste: all 44 package titles read. Finance, pensions, housing, medicine supply, hospital discharges
    (datos_egresos_hospitalarios, not a panel indicator). No HIV series. NEGATIVE.
  * secretaria_hacienda: 54 packages. "Asignación y Ejecución del PEF" 2003-2026 = Estadísticas Oportunas concepts by
    ramo, no programme key; q VIH, SIDA, P016 all 0. NEGATIVE for an HIV budget line.
- DGE Anuario de Morbilidad 1984-2025 (epidemiologia.salud.gob.mx/anuario/html/): SUIVE notified new cases. One PDF per
  disease per year by age group and state: ../{year}/incidencia/enfermedad_grupo_edad_entidad_federativa/{code}.pdf.
  Codes 192 "Infección por VIH" (recent years), 059 "Infección asintomática por VIH" / "Seropositivos a VIH" and 067
  "Síndrome de inmunodeficiencia adquirida" (earlier years). 2024/192.pdf 282,257 bytes; 2025/192.pdf 278,266 bytes
  (modified 2026-09-01). Not opened. ADDITIVE at admin1 if the table holds counts. Grade 2 (PDF tables).
- CENSIDA gob.mx documents (320 items enumerated):
  * "Epidemiología Registro Nacional de Casos de VIH y sida": 45 quarterly PDFs (Informe Histórico VIH DVEET), cierre 2012
    to Día Mundial 2025. National case register by state. Grade 2. Overlaps the yearbook and PAHO new-diagnosis series.
  * "Boletín de Atención Integral de Personas con VIH": 45 quarterly PDFs, 2015 to September 2026 (Secretaría de Salud
    cascade). Grade 2.
  * MEGAS 2012-2013 and 2014-2015: panel GAM expenditure 2013-2015 likely the same. Probable duplicate.
- transparenciapresupuestaria.gob.mx and nptp.hacienda.gob.mx (programme P016 "Prevención y atención de VIH/SIDA y otras
  ITS"): neither site reachable on 5 October 2026 (browser and curl both failed). Retry in round two.

## Argentina
Panel position: ARG has zero admin1 rows. No new_diagnoses, no registered deaths. Domestic spend only GAM 2014-2016.
on_art_count from who_gho and unaids_aidsinfo (national).

- datos.gob.ar (Andino/CKAN). 45 publishers ENUMERATED. Ministerio de Salud 63 packages, all titles read. Health datastore
  lives on datos.salud.gob.ar (17 publishers, 64 packages), not on datos.gob.ar (datastore_search there says Not Found).
  * notificacion-de-casos-de-vih (Dirección de Respuesta al VIH): SNVS 2.0 notified HIV cases. Resource 747d2078
    (casos_prov_vih_2014-2023): 750 rows, fields id_sexo, sexo, id_jurisdiccion, jurisdiccion, anio, casos_vih (the
    two jurisdiction field names are swapped: "jurisdiccion" holds the INDEC code, "id_jurisdiccion" the name; names lose
    accents, e.g. "Crdoba"). 24 jurisdictions plus ARG national, three sexes, 2014-2023.
    National both sexes: 2014 6,654; 2017 5,218; 2019 6,311; 2020 3,991; 2021 5,772; 2022 6,168; 2023 6,588.
    Province sum is 37 (2020) to 243 (2015) lower than the national row (cases with unknown residence). Traced from the
    in-page sumProv output, 2014 6,444; 2015 6,504; 2020 3,954; 2023 6,448.
    PAHO indicator 93 (Public Health Surveillance) for ARG DIFFERS: 2014 6,053; 2019 3,937; 2020 2,996; 2022 6,073;
    2023 7,141; 2024 6,692; 2025 7,229. Two national vintages that do not agree. The province split is ADDITIVE either way.
    Newer files (not in datastore) added 20 Jan 2026: notificacion-de-casos-de-vih.csv 26,579 bytes,
    notificacion-de-casos-de-vih-segun-edad.csv 11,043 bytes (probably add 2024). Not downloaded. Grade 1.
  * tasas-de-vih-por-100-mil-habitantes: rates from the same counts. Derived, NEGATIVE as a separate source.
  * porcentaje-de-diagnosticos-tardios-de-vih: % late diagnosis by jurisdiction, 2010-2019, 2012-2022 (new definition
    from 2022, PDF "definicion-diagnostico-tardio"), 2022-2023 (datastore), 2023-2024 CSV 31,015 bytes (20 Jan 2026).
    Panel has late_hiv_diagnosis_pct from UNAIDS 2015-2020 national only. ADDITIVE at admin1 and for 2021-2024. Grade 1.
  * defunciones-ocurridas-y-registradas (DEIS): deaths by year x province of residence x ICD-10 3-character cause x sex x
    age group, 2005-2022 (resource ccf688f4, 825,814 rows) and 2023 (e71b36a0). Datastore filters work.
    B20-B24 sums: 2005 1,307; 2010 1,337; 2015 1,553; 2019 1,265; 2020 1,139; 2021 1,260; 2022 1,174; 2023 1,102.
    2023 = WHO MDB 2023 (1,102) exactly, so the national series DUPLICATES the MDB. Province split (24 plus 98 abroad and
    99 unknown) ADDITIVE. 2024 file defuncion2024.csv (16 Mar 2026, size not given) not in datastore. Grade 1.
  * metodos-anticonceptivos-e-insumos-distribuidos-por-el-pnssyr: four quarterly files of 2021 only, by jurisdiction.
    Condoms possibly among the supplies (not opened). Single year, WEAK.
  * Remaining Ministerio de Salud packages (vaccines, COVID, births, professionals, SUMAR, SSS insurers, INCUCAI, cancer
    registries, essential medicines Remediar): no HIV. NEGATIVE.
- Budget, Subsecretaría de Presupuesto (33 packages, 1995-2025 yearly). Programme 22 of servicio 310 (Ministerio de
  Salud) "Respuesta al VIH, Infecciones de Transmision Sexual, Hepatitis Virales, Tuberculosis y Lepra", activity 41
  "Asistencia, Prevencion, Vigilancia e Investigacion en VIH e Infecciones de Transmision Sexual" (resource 971a8df0,
  d-apertura-programatica-2024, 1,750 rows). Packages presupuesto-de-la-administracion-publica-nacional-1995 to -2025. Files per year: credito-anual/mensual/diario zips (credito
  vigente, devengado, pagado by programme, activity, object of expenditure, source of funds), ejecucion-fisica-trimestre-N
  (physical targets and outputs by programme). Datastore copies are truncated previews (credito-diario 1,000 rows; physical
  table 250 rows with no health rows). So the route is the zip files: grade 1 file download, size unknown because
  dgsiaf-repo.mecon.gob.ar does not answer curl from this machine. ADDITIVE: domestic_hiv_spend national 1995-2025 at
  activity level (HIV and STI separable from TB and hepatitis from activity 41). Physical outputs may hold people on ARV.
- presupuestoabierto.gob.ar (the API listed as package api-de-presupuesto-abierto): browser and curl both refused, 5 Oct 2026.
  Access terms not read.
- Boletín sobre el VIH y las ITS en la Argentina: N° 40 (Dec 2023, 19.3 MB PDF) newest listed on
  argentina.gob.ar/salud/vih-its/boletines-vih-its-hepatitis-virales-y-tuberculosis. Grade 2. Contents not read (no PDF opened).
  Synthesis PDF 3.6 MB. Hepatitis bulletins N° 6 and N° 7, TB bulletins N° 7 and N° 8 on the same page.

## Peru
Panel position: PER 1,239 rows, zero admin1 rows. new_diagnoses only pepfar_modality and pepfar_panorama 2021-2025 (five
rows each). domestic_hiv_spend only unaids_gam_expenditure 2020 and 2022-2024 (four rows, no 2021). aids_deaths modelled only (UNAIDS 2000-2024,
WHO GHO 2000-2025). PAHO indicator 93 for PER: 2018 8,134; 2019 10,546; 2020 6,261; 2021 8,809 (Public Health
Surveillance); 2022 9,960; 2023 10,346; 2024 9,636; 2025 9,037 (Disease specific register).

- CDC Peru Sala VIH (Centro Nacional de Epidemiología, Prevención y Control de Enfermedades, MINSA). www.dge.gob.pe/vih
  redirects to app7.dge.gob.pe/maps/sala_vih/ and then to the Shiny app app7.dge.gob.pe/maps2/shiny_vih_web/.
  * Tab "Tabla: Casos y Tasa de incidencia" (reactable ten-tab07-table): notified HIV cases and AIDS cases for 25
    departments x 2019-2026 (2026 partial), cases or rate. Read 5 Oct 2026.
    Department sums equal the national series exactly every year: VIH 2019 9,884; 2020 5,795; 2021 8,476; 2022 10,101;
    2023 10,334; 2024 9,633; 2025 9,038; 2026 4,606. sida 2019 1,687; 2020 905; 2021 1,268; 2022 1,553; 2023 1,624;
    2024 1,428; 2025 1,431; 2026 732.
    Examples: LIMA VIH 2019 4,840, 2025 3,564; LORETO 2019 738, 2025 448; AMAZONAS 2019 230, 2025 515.
  * Against PAHO indicator 93: 2023 10,334 vs 10,346; 2024 9,633 vs 9,636; 2025 9,038 vs 9,037; 2022 10,101 vs 9,960;
    2019 9,884 vs 10,546; 2020 5,795 vs 6,261. Close from 2023, not equal. National series near-DUPLICATE of PAHO.
    Department split ADDITIVE (PER zero admin1). AIDS case count by department also new.
  * Other tabs: national trend by sex, age group x sex (2021-2025 quinquennium), transmission route, Estimaciones VIH 2024
    (Spectrum, probable duplicate of UNAIDS). Department, province and district selectors exist (selectize
    ten-fdepa/fprov/fdist), Loreto gives eight provinces and Maynas 11 districts, but the selectors changed only the
    table's Total row in this test, so a province table was not confirmed.
  * Route: data travels over the Shiny SockJS websocket, no data file in the network log. "Descargar" buttons serve
    session-bound URLs (session/<id>/download/ten-tab07-download). Grade 3.5 (published to a human, ACCESS_LADDER §7c).
    Not downloaded.
- datosabiertos.gob.pe (DKAN). package_list 4,419 names, group_list 402 publishers, ENUMERATED by name regex.
  package_show works (result is an array). package_search and organization_list 404, both datastore endpoints 500,
  so file-only. Regex over group names found no health publisher name.
  * MINSA SINADEF deaths (información-de-fallecidos-del-sistema-informático-nacional-de-defunciones-sinadef-ministerio):
    data at drive.minsa.gob.pe/s/PigmdwnCGEdyqos/download, changed 15 Sep 2026, size not given; dictionary
    Diccionario_Datos_SINADEF.xlsx 10.4 KB. Record-level deaths with causes. curl HEAD returned 403 and the share page
    returned a Cloudflare block ("Sorry, you have been blocked", 5 Oct 2026). Not bypassed. WHO MDB already holds PER
    1999-2022 (2022 1,221), so a national total would likely DUPLICATE the MDB; the department split would be ADDITIVE.
  * MIMP "mujeres-y-hombres-con-síndrome-de-inmunodeficiencia-adquirida-sida-por-grupos-de-edad": c_6_3.xlsx 496.61 KB.
    Probable national duplicate. Not opened.
  * GORE Tacna ITS report ITS_2025.csv 196.13 KB. One region, one year. WEAK.
  * GORE San Martín "Dataset Vigilancia Epidemiológica en la Región San Martín" CSV 34.75 MB. One region. WEAK.
  * CENARES (national procurement centre for strategic health supplies): distribution CSV Dataset_CD1.csv 12.03 MB and
    2024 budget CSV Presupuesto1.csv 2.98 MB, both changed 15 Jun 2026. ARV content not read. Candidate.
  * MINSA family planning DAT files of 2017 (Metodo 8.62 MB, Anticoncepcion 112.91 KB, Consejeria 5.21 MB). Old. WEAK.
  * CDC "vigilancia-epidemiológica-de-*" packages: dengue, Carrión, leishmaniosis, malaria, IRA, EDA, zoonoses. NEGATIVE.
  * "defunciones" package belongs to the Miraflores municipality. NEGATIVE.
- MEF budget (datosabiertos.mef.gob.pe, Angular front end over POST /Rest/... with Token = localStorage uuid).
  * presupuesto-y-ejecucion-de-gasto: "Información de 2009 al 2026 del Gasto del Gobierno Nacional, Gobiernos Regionales y
    Gobiernos Locales, proveniente de la Consulta Amigable". One CSV per year. Columns include PROGRAMA_PPTO(_NOMBRE),
    PRODUCTO_PROYECTO, ACTIVIDAD_ACCION_OBRA, DEPARTAMENTO_META, FUENTE_FINANCIAMIENTO, MONTO_PIA, MONTO_PIM,
    MONTO_DEVENGADO, MONTO_GIRADO. 2009 has 5,709,181 rows, 2024 has 11,191,489. Sizes from HEAD: 2012-Gasto.csv
    6,776,006,081 bytes; 2024-Gasto.csv 10,237,853,250; 2025-Gasto-Mensual.csv 10,497,728,811; Gastos_Diccionario.csv 5,819.
    Budget programme 0016 TBC-VIH/SIDA is the HIV target (programme name not yet read from a row).
    ADDITIVE domestic_hiv_spend by department of target and product, 2009-2026. Grade 1 by file, impractical by size.
  * Server filter getRecursoDetalleVistaData with PROGRAMA_PPTO = 0016 aborted at 42-44 s on 2024 and on 2009 (5.7M rows).
    Unfiltered 2024 page returned in 11 s. Filtered dump api.datosabiertos.mef.gob.pe/DatosAbiertos/v1/dump?id=...&filters=
    returns 401 Unauthorized to HEAD.
  * presupuesto-y-ejecucion-de-gasto-devengado-sectores: 275 resources, sectors 03 to 40, no regional or local government
    sector. Sector 11 (Salud) 2012-2026: 2024 file 677,178 rows, 659,937,762 bytes; 2012 file 479,307,020 bytes. The view
    API returned zero rows for this resource even unfiltered, so the view is not loaded. National health sector only,
    regional health directorates missing. PARTIAL.
  * presupuesto-y-ejecucion-de-gasto-devengado-trimestral: 2024 51,489 rows, 7,705,879 bytes, but columns stop at FUNCION
    (no PROGRAMA_PPTO). NEGATIVE for HIV.
  * comparacion-de-presupuesto-ejecucion-gasto 2022-2026: 8,468,325 rows, 8,978,982,720 bytes. Same size problem.
  * distribucion-geografica-del-gasto (4,035 rows) and clasificacion-funcional-del-gasto (24,136 rows): by pliego and
    function, no programme. NEGATIVE.
  * presupuesto-y-ejecucion-de-gasto-devengado-mensual 2012-2026 and presupuesto-y-ejecucin-de-gasto-2004-2008 not sized.
- Consulta Amigable (apps5.mineco.gob.pe/transparencia/Navegador): Imperva "Access denied, Error 16", re-checked 5 Oct 2026
  15:57 UTC. Not bypassed. Retry in round two from another network is Jason's call.
- Not yet checked: SIS atenciones zips (2017 to 2025, 33-167 MB each, diagnosis content unknown), ENDES HIV-testing
  questions (INEI 1986-2025), CDC weekly bulletin PDFs.

## Dominican Republic (datos.gob.do, CKAN, enumerated 6 October 2026)
- Panel position. DOM 2,054 rows, 497 admin1 rows (all PEPFAR SNU or agency SNU). new_diagnoses PEPFAR only 2016-2025.
  hiv_tests_performed national only UNAIDS/WHO 2022-2024 and GF 2019-2024. on_art_count UNAIDS 2010-2024, WHO 2000-2025.
  domestic_hiv_spend GAM 2013-2024 (12 rows). aids_deaths modelled only. No national surveillance diagnoses.
- Catalogue: package_list 1,059 names. organization_list enumerated; health-related orgs read with organization_show.
- CONAVIHSIDA (national HIV council) org, five packages, all files hosted on www.conavihsida.gob.do (Joomla), quarterly:
  1. PVVIH incorporados a servicios de atencion y tratamiento, 2018 to April-June 2025 (CSV, ODS, XLSX). Enrolments in care and ART.
  2. Poblacion clave con prueba de VIH con pre y pos consejeria, 2022 to April-June 2025.
  3. Poblacion general con prueba de VIH, 2018-2024.
  4. Embarazadas con prueba de VIH, 2018-2024 (CSV 2018-2022).
  5. Directorio servicios atencion integral VIH, 2023 (facility list).
  Route: HEAD on four download URLs returned 403 (curl), and the site page returned a Cloudflare "Performing security
  verification" challenge in the browser pane on 6 October 2026. Not bypassed. Columns unknown (no datastore).
  Additive test: national tests 2018-2021 and enrolments 2018-2025 are not in panel from a national source (panel tests start 2022,
  initiations are PEPFAR and WHO TME only). LIKELY ADDITIVE if national; province split unknown. Grade 3.5 (human route only).
- Maternity hospital (Hospital Universitario Maternidad Nuestra Senora de la Altagracia) "vih-positivos" 2025 to May: single hospital,
  host returns 403 behind Cloudflare. WEAK, one facility.
- SeNaSa (public insurer, subsidised regime) "diagnosticos-regimen-subsidiado", 2015-2026, bimonthly, ICD-10 chapter and group by
  region and province, users and value authorised (per CKAN notes). Files on arssenasa.gob.do, HEAD 200:
  Diagnostico-Regimen-Subsidiado-SeNaSa-2015-2019.csv 167,293,437 bytes; Diagnosticos-Regimen-Subsidiado-SeNaSa-2020-2025.csv
  173,700,167 bytes; Diagnosticos-Regimen-Subsidiado-febrero-2025-octubre-2025.csv 28,123,027 bytes. Later 2025-2026 files not sized.
  HIV would sit in the B20-B24 group if groups are ICD-10 blocks (not verified without the file). Insured users with an HIV-coded
  diagnosis and authorised value by province. ADDITIVE in kind (no claims-based measure in panel) but partial (one insurer,
  subsidised regime only). Grade 1 by file.
- DIGEPRES (budget office) digepres.gob.do/gastos: "Ejecucion presupuestaria" pivot files, xlsx, site sizes
  2025-2026 62.1 MB (HEAD 96,983,764 bytes), 2024 51.9 MB (54,498,540), 2022-2023 87.7 MB (94,100,383), 2020-2021 75.2 MB
  (78,893,689), 2014-2019 10.9 MB (11,450,371), 2008-2013 13.4 MB (14,117,740). Programme columns NOT verified (needs download).
  Institutional annual 1990-2025 xlsx 277,963 bytes (too coarse for an HIV line unless CONAVIHSIDA is a unit).
  Desempeno presupuestario reports: 95 links, all PDF (grade 2). Site search "VIH" returns one 2022 news item only.
- transparenciafiscal.gob.do: Cloudflare "Sorry, you have been blocked" on 6 October 2026. Not bypassed.
- Other packages scanned by name (vih, sida, epidemi, mortalidad, defuncion, vigilancia): none from DIGEPI or vital statistics.

## Guatemala (6 October 2026)
- Panel position. GTM 1,830 rows, 591 admin1 (PEPFAR SNU). new_diagnoses PEPFAR only 2016-2025. domestic_hiv_spend GAM
  2011-2013, 2016-2021 and 2023-2024 (11 rows, no 2014, 2015 or 2022). aids_deaths UNAIDS only 2000-2024. WHO MDB has GTM registered deaths 2000-2023 (190 in 2023).
- datos.gob.gt (CKAN): Cloudflare "Performing security verification" on the API URL in the browser pane, did not clear
  after 8 seconds. Not bypassed. Catalogue NOT enumerated. Retry with the pane visible in round two.
- INE vital statistics (www.ine.gob.gt/vitales, tab "Bases de datos" loads an iframe publicaciones4.php?c=118&t=24):
  Radware bot manager CAPTCHA page (validate.perfdrive.com), page timestamp 5 October 2026 16:25 UTC. Not solved.
  Death microdata would add department-level registered HIV deaths if the files carry ICD-10 and department. BLOCKED.
- MINFIN www.minfin.gob.gt/ejecucion-presupuestaria: execution and liquidation reports 2008-2026, all PDF (2008-2012 also
  HTML index pages). Grade 2. Clasificadores tematicos: per-entity PDF reports, no HIV classifier seen. Portal de Presupuesto
  Abierto (tallerdepresupuestoabierto.minfin.gob.gt): Cloudflare challenge, not bypassed. SICOIN needs a login.
- MSPAS epidemiology (epidemiologia.mspas.gob.gt): "Vigilancia Epidemiologica del VIH" item links to sala situacional
  category 12-vih, which returns "You have no rights to access this category" (Phoca Download). Grade 3 (gated).
- SIGSA datos de salud (sigsa.mspas.gob.gt/datos-de-salud): 13 topics (population, births, malnutrition, chronic disease,
  family planning, leading morbidity, consultations, vectors, maternal-child, IRA/ETA, supplementation, vaccination, COVID).
  No HIV topic. NEGATIVE.

## Ecuador (6 October 2026)
- Panel position. ECU 1,024 rows, 0 admin1. new_diagnoses none. aids_deaths modelled only (unaids_aidsinfo 2000-2024,
  who_gho 2000-2025). hiv_tests_performed GF 2020-2024, UNAIDS 2019-2023, WHO 2022-2024. domestic_hiv_spend GAM 2017-2022
  (6 rows). art_initiations WHO TME 2016-2024. WHO MDB holds ECU registered deaths 1997-2022 (586 in 2022).
- datosabiertos.gob.ec (national catalogue): 403 Forbidden on the CKAN API and on the HTML search, 6 October 2026.
  aplicaciones3.ecuadorencifras.gob.ec (BIINEC open-data bank and sbi-war historical bank) also 403 in the browser pane.
  Likely a geographic or IP block on some gob.ec hosts. NOT enumerated. Retry in round two.
- INEC Registro Estadistico de Defunciones Generales (www.ecuadorencifras.gob.ec/defunciones-generales/): 89,547 deaths
  registered in 2024 (page text). Annual files under documentos/web-inec/Poblacion_y_Demografia/Defunciones_Generales/2024/,
  HEAD 200 on 6 October 2026:
  2.%20Datos_abiertos_EDG_2024.zip 6,653,571 bytes (Last-Modified 30 Sep 2025); 1.Base_de_datos_EDG_2024_SPSS.zip 5,205,510;
  Tabulados_y_series_EDG_2024_VF.xlsx 11,289,628; Diccionario_de_variables_EDG_2024.xlsx 197,224. Also R zip, fichas,
  syntax, methodology PDF. Earlier years on the same pattern (2019 under Defunciones_Generales_2019/, 2018 under
  Nacimientos_Defunciones/2018/).
  Cause and province variables NOT verified (the dictionary xlsx needs a download). If the microdata carry ICD-10 cause and
  province of residence, the files add province-level registered HIV deaths and the years 2023 and 2024, which the MDB
  lacks. LIKELY ADDITIVE. Grade 1 by file.
  Tableau Public workbook "Registro estadistico de defunciones generales" (INEC, last updated 27 Nov 2022, 12 sheets incl.
  "Lista resumen de causas"): deaths registered in year t+1 by the Becker short list of leading causes, filters sex,
  natural region, year, age group, plus a province map selector; ICD-10 causes from 1997 (ICD-9 in 1990-1996).
  Mini-site Sitios/Defunciones: residence-based, Becker short list, 2019 provisional. Whether the Becker list keeps HIV as
  its own line is NOT verified on these pages. Grade 3.5 (Tableau, human route).
- INEC Camas y Egresos Hospitalarios 2024: datos_abiertos_camas_egresos_hospitalarios_2024.zip 43,161,161 bytes (HEAD 200,
  Last-Modified 4 Jul 2025). Hospital discharges; HIV-coded discharges by province would be a new kind of measure
  (hospitalisations), not in panel. WEAK relevance. Grade 1 by file. Variables not verified.
- MSP (Ministerio de Salud Publica) HIV reports, found by web search on 6 October 2026, all PDF on www.salud.gob.ec:
  INFORME-ANUAL-DE-VIH-2021_MSP.pdf and -2022 (wp-content/uploads/2024/04/), informe_envih_2023.pdf and
  informe_envih_2024.pdf (2025/09/), 2024_informe_envih_final.pdf (2025/11/); key-population prevalence studies 2021
  (HSH, TS). HEAD requests to www.salud.gob.ec timed out at 30 seconds each, so no sizes.
  Search-engine snippets (NOT verified, PDFs not opened) describe new HIV cases by province from PRAS (the ministry's
  care-registration platform) for 2024. Would add a national surveillance new_diagnoses series and a province split,
  neither in panel. LIKELY ADDITIVE. Grade 2 (PDF).

## Costa Rica (6 October 2026)
- Panel position. CRI 934 rows, 0 admin1. new_diagnoses none. aids_deaths modelled only (UNAIDS 2000-2024, WHO GHO
  2000-2025). hiv_tests_performed GF 2022-2023, UNAIDS 2022, WHO 2022-2024. domestic_hiv_spend GAM 2014, 2018, 2019, 2020,
  2022, 2023, 2024 (7 rows; 2015-2017 and 2021 missing). art_initiations WHO TME 2016-2020. WHO MDB holds CRI 1997-2022
  (165 in 2022).
- INEC Costa Rica microdata catalogue (NADA, sistemas.inec.cr/pad5; API /index.php/api/catalog/search and
  /api/catalog/{idno}/variables answer without login). Death studies: CRI-DEF-2002 to CRI-DEF-2010 and CRI-DEFU-2011-2013
  (data_na, metadata only), CRI-DEFU-2014-2016, CRI-DEFU-2017-2019, CRI-DEFU-2017-2021, CRI-DEFU-2022-2024 (access type
  "public"). Variables VERIFIED from the API for 2017-2021 and 2022-2024: causamuer (ICD-10 underlying cause code),
  des_causa, provincia and pc (province and canton of residence), provocu, sexo, edads, edadsrec, anodef, regsalud.
  The get-microdata page redirects to a login and registration form, and /api/resources returns ACCESS-DENIED.
  Would add province and canton registered HIV deaths (B20-B24) and the years 2023 and 2024 that the MDB lacks.
  LIKELY ADDITIVE. Grade 3 (free registration, then file). Annual Estadisticas Vitales reports on admin.inec.cr are PDF.
- Ministerio de Salud press release, 30 November 2023 (HTML, read): preliminary Direccion de Vigilancia de la Salud data to
  10 November 2023 give 816 HIV-AIDS cases (685 men, 130 women), San Jose 259, Alajuela 119, Heredia 78; 857 cases in 2022
  (732 men, 123 women). National notified cases are not in panel. Press releases are a grade 2.5 route at best (HTML text,
  one year at a time, preliminary).
- Ministerio de Salud document library (Joomla, enumerated folder by folder):
  Analisis de Situacion Salud folder (39 items): "Situacion VIH y sida. Costa Rica 2002-2017" xls, listed 285 KB, served as
  DVS_situacion_VIH_sida_cr_2017.xls (HEAD 200, no content-length, Last-Modified 29 Nov 2019). Content not verified.
  LIKELY ADDITIVE for 2002-2017 notified cases. Grade 1 by file. Perfil epidemiologico 2024 and 2025 (PDF 1.53 MB, 1.71 MB).
  Boletines de morbilidad (mandatory-notification diseases) 2012-2015 and mortality bulletins 2012-2015, PDF and rar. Old.
  Consulta de bases de datos folder: empty. No HIV item in the mortality spreadsheets folder (cancer and infant only).
- MEGAS (Medicion del Gasto en Sida, the UNAIDS national AIDS spending assessment) reports, Ministerio de Salud folder
  economia-de-la-salud/megas/informes-2: PDF for 2016 (5.78 MB), 2018 (3.92), 2019 (3.47), 2020 (5.40), 2021 (2.44),
  2022 (3.58), 2023 (1.83). The 2016 and 2021 reports would fill years the GAM rows lack, if each report year is the
  spending year. The other years would DUPLICATE or cross-check GAM. Grade 2.
- National open-data host www.datosabiertos.go.cr: HTTP 522 (Cloudflare origin timeout). datosabiertos.presidencia.go.cr: no
  response within 25 seconds. NOT enumerated.

## Paraguay (6 October 2026)
- Panel position. PRY 1,087 rows, 0 admin1. new_diagnoses GF 2021-2023 only. aids_deaths modelled only (UNAIDS
  2000-2024, WHO GHO 2000-2025). hiv_tests_performed GF 2019-2024, UNAIDS 2019-2024, WHO 2022-2024. domestic_hiv_spend GAM
  2018-2020 and 2022 (4 rows, no 2021). art_initiations GF 2021-2025, WHO TME 2013-2024. WHO MDB holds PRY 2000-2021 (275 in 2021).
- REACH FAILURE. On 6 October 2026 the gov.py names mspbs.gov.py, www.mspbs.gov.py, portal.mspbs.gov.py, datos.gov.py,
  www.datos.gov.py, ine.gov.py and www.ine.gov.py did not resolve (local resolver "nodename nor servname"; 8.8.8.8 timed out
  or returned SERVFAIL; browser ERR_NAME_NOT_RESOLVED). www.mef.gov.py (Cloudflare) resolves and loads.
  datos.hacienda.gov.py (MEF open data): curl 403, browser Cloudflare "Performing security verification". Not bypassed.
  NOTHING in Paraguay enumerated. Retry every route in round two.
- Routes identified by web search only (not opened, to retry):
  1. datos.gov.py CKAN packages "Estadisticas Vitales del Paraguay 2019 - Defunciones", "... 2020 - DEFUNCIONES",
     "... 2021 - DEFUNCIONES" (resources such as deaths by department of registration and of residence). Whether a cause
     table carries HIV is unknown.
  2. DIGIES (Direccion General de Informacion Estrategica en Salud, the ministry's statistics office, which runs the
     vital-statistics subsystem SSIEV) open-data page digies.mspbs.gov.py/datos-abiertos/. Cause-of-death databases by
     department are described in search snippets, unverified.
  3. PRONASIDA (the national HIV programme) annual "Informe epidemiologico de VIH" PDFs, e.g.
     www.mspbs.gov.py/dependencias/pronasida/adjunto/4ee285-BoletinepidemiolgicodeVIH2024.pdf. Snippets mention new
     diagnoses by department for 2024 (unverified). Would add a national surveillance new_diagnoses series and a department
     split. LIKELY ADDITIVE. Grade 2.
  4. MEF datos.hacienda.gov.py budget execution data (behind Cloudflare). PRONASIDA programme lines unknown.

## Panel position, remaining 13 countries (national rows, read 6 October 2026)
(In the list below "MDB" gives the years held by the external WHO Mortality Database. The panel holds no MDB rows.)
- BOL 937 rows, 0 admin1. new_diagnoses none. aids_deaths UNAIDS/WHO modelled. tests GF 2023-2024, UNAIDS 2022-2024, WHO
  2022-2024. domestic spend none. art_initiations WHO TME 2015-2023 (3). MDB none.
- HND 1,884, 469 admin1 (pepfar_snu). new_diagnoses GF 2022-2025, PEPFAR 2018-2025. spend GAM 2020-2024 (5). MDB none.
- SLV 1,940, 480 admin1. new_diagnoses GF 2022-2025, PEPFAR 2018-2025. spend GAM 2015 and 2017-2024 (9, no 2016). MDB 1997-2018.
- PAN 1,600, 386 admin1. new_diagnoses PEPFAR 2018-2025. spend GAM 2018 and 2020-2024 (6, no 2019). MDB 1998-2022.
- NIC 973, 192 admin1. new_diagnoses PEPFAR 2018-2025. aids_deaths NONE. spend none. MDB 2005-2022.
- JAM 1,375, 232 admin1. new_diagnoses PEPFAR 2018-2025. aids_deaths NONE. spend GAM 2013-2014 (2). MDB 2000-2014 (13 yrs).
- TTO 669, 0 admin1. new_diagnoses PEPFAR 2018-2025. aids_deaths NONE. spend GAM 2020 (1). MDB 1999-2020.
- GUY 1,280, 0 admin1. new_diagnoses PEPFAR 2018-2022. spend none. MDB 1991-2020.
- SUR 954, 8 admin1. new_diagnoses PEPFAR 2018-2019. spend none. MDB 1995-2014.
- BLZ 894, 3 admin1. new_diagnoses none. spend GAM 2021-2023 (3). MDB 1997-2022.
- HTI 2,627, 1,108 admin1 (pepfar_snu, pepfar_agency_snu). new_diagnoses GF 2021-2023, PEPFAR 2018-2025. spend GAM
  2014-2016 (3). MDB none.
- CUB 961, 0 admin1. new_diagnoses none. spend none. MDB 2000-2021.
- VEN 920, 0 admin1. new_diagnoses none. tests UNAIDS 2023-2024, WHO 2022-2024 only. spend GAM 2016-2019 (4). MDB 1996-2016.

## Bolivia (6 October 2026)
Panel position. 937 rows, zero admin1. No new_diagnoses, no domestic_hiv_spend. aids_deaths modelled only (unaids 2000-2024, who_gho 2000-2025). hiv_expenditure_total unaids 2012-2022 (three rows). hiv_tests_performed GF 2023-2024, UNAIDS 2022-2024, WHO 2022-2024. No MDB. DHS source holds hiv_prevalence_15_49 only, across all countries (252 rows).

REACH. datos.gob.bo 403 (nginx), browser and curl, including /api/3/action/package_search. snis.minsalud.gob.bo and www.minsalud.gob.bo no answer within 20 s. www.economiayfinanzas.gob.bo no answer within 25 s. www.ine.gob.bo 200.

INE Bolivia web tables (read as HTML, 6 Oct 2026).
- censos-salud. Census 2012 and 2024 tables only (care seeking, insurance, birth attendance). No HIV. NEGATIVE.
- estadisticas-sociales/mortalidad. Census 2024 declared deaths by department, sex, age, plus COVID-19 deaths. No cause list. NEGATIVE for HIV.
- registros-administrativos-sociales (SERECI civil registry). Deaths by year of registration, department, sex, age, 2010-2024. No cause. NEGATIVE for HIV.
- registros-administrativos-salud (MSyD admin). 16 tables 1997-2024 (facilities, beds, consultations, prenatal, vaccines, PAP). No HIV table. NEGATIVE.
- Search snippet (UNVERIFIED, lostiempos 3 Jan 2025): SERECI registered 58,588 deaths 1 Jan-26 Dec 2024. WHO FCTC annex snippet (UNVERIFIED): 2022 mortality database corrected with IRIS coding. Neither gives an open cause-of-death file.

INE ANDA (NADA catalogue anda.ine.gob.bo). Enumerated all 120 studies via /index.php/api/catalog/search?ps=100&page=1..2. No death-registration study. Health studies: DHS 1989, 1994, 1998, 2003, 2008 (remote), EDSA 2016 (public), EDSA 2023 (id 119, BOL-INE-EDSA-2023, public, 3,437 variables, changed 20 Oct 2025).
- EDSA 2023 data dictionary read (F31 EDSA2023_Mujer, F36 EDSA2023_Hombre). Women Section IX and men Section VII cover HIV/AIDS and STIs. Women's file has "¿alguna vez se ha realizado una prueba del VIH?", "¿La Última vez que se hizo una prueba de VIH recogió sus resultados?", knowledge, attitude and stigma items.
- get-microdata redirects to login ("Para acceder a los archivos de datos de acceso público ... ingrese su correo electrónico y contraseña o regístrese"). GRADE 3.
- Additive test. Panel has no survey "ever tested" indicator. EDSA 2023 would be a NEW indicator (self-reported ever tested, by department), not an addition to an existing series. Record as candidate new indicator, not additive.

MSyD and departmental surveillance (search snippets, UNVERIFIED).
- minsalud.gob.bo news: 46,442 cases registered since 1984, about 30,000 PLHIV, 20,687 on ART. Santa Cruz 45.4%, La Paz 21.5%, Cochabamba 19.3%.
- Weekly bulletin SE 27/2024 (minsalud jdownloads id 857): 1,630 HIV/AIDS cases to week 27 of 2024, 131 in AIDS phase.
- SEDES Cochabamba: 694 confirmed cases in 2024. SEDES La Paz: 734 cases in 2024.
- SEDES La Paz ITS/VIH bulletin PDF: https://www.sedeslapaz.gob.bo/wp-content/uploads/2024/10/Boletin-EpidemiolA%C2%B3gico-Programa-ITS-VIH.pdf, HEAD 200, 4,079,636 bytes, Last-Modified 3 Oct 2024. Not opened.
- Assessment. Department-level new_diagnoses would be ADDITIVE (panel holds none for BOL). The national series lives in SNIS-VE bulletins on hosts that did not answer. GRADE 2 where reachable, otherwise REACH FAILURE.

Spend.
- MEGAS 2010-2012 PDF on UNAIDS: https://www.unaids.org/sites/default/files/documents/bolivia_2010-2012_es.pdf, HEAD 200, 2,262,569 bytes, Last-Modified 18 Feb 2025. Snippet (UNVERIFIED): total Bs 71.019 m (2010), 96.788 m (2011), 81.780 m (2012), USD 10.045 m, 13.847 m, 11.767 m. Panel hiv_expenditure_total starts 2012, so 2010 and 2011 LIKELY ADDITIVE. GRADE 2.
- Snippet (UNVERIFIED) of a 2005 MEGAS covering La Paz, Cochabamba and Santa Cruz only (study done 2008).
- MEFP budget (SIGEP) not reached. Retry in round two.

Round-two retry list adds: datos.gob.bo, snis.minsalud.gob.bo, minsalud.gob.bo, economiayfinanzas.gob.bo.

## Panama (6 October 2026)
Panel position. 1,600 rows, 386 admin1. aids_deaths modelled only. WHO MDB (external, not in the panel) holds PAN registered deaths 1998-2022. domestic_hiv_spend GAM 2018 and 2020-2024 (six rows, no 2019). hiv_expenditure_total UNAIDS 2012-2024 (eight rows). new_diagnoses and hiv_tests_performed from PEPFAR SNU 2016-2025 (64 and 65 rows), modality and panorama 2018-2025. on_art GF 2017-2021.

REACH. www.datosabiertos.gob.pa (CKAN) 200. www.inec.gob.pa timed out at 40 s on http and https, DNS 190.34.178.25, browser navigation failed. REACH FAILURE. www.minsa.gob.pa 200, site search /search/node returns "Acceso denegado" (menu pages readable). www.mef.gob.pa 200.

datosabiertos.gob.pa CKAN, organisations enumerated. INEC 195 packages, CSS (Caja de Seguro Social, the social-security health insurer) 688, MEF 71, CGR (Contraloria) 156, MINSA 0, Gorgas institute 0. Portal search "vih" 1 hit (CSS), "sida" 0, "defunciones" 17, "mortalidad" 3.
- INEC deaths by age group, cause and sex, 2021. Package inec-hechos-vitales-defunciones-en-la-republica-por-grupo-de-edad-segun-causa-y-sexo-ano-2021, ICD-10 list, metadata 19 Jul 2023. XLS 252,416 bytes, CSV 136,951 bytes, PDF 613,962 bytes. Not in datastore, so not read.
- INEC deaths by province and comarca, cause and sex, 2021. Package hechosvitalesdefunciones-provinciaycomarca. XLS 140,288 bytes, CSV 23,162 bytes (https://www.datosabiertos.gob.pa/dataset/9667bad9-9ddf-4d52-a7c1-ef854d600cd2/resource/b8eb7e2a-8175-4d60-a3bc-24b53394b4b6/download/inec-hechos-vitales-defunciones-causa-sexo-y-provincia.csv), PDF 388,372 bytes. Not in datastore. Only 2021 on CKAN. Whether HIV (B20-B24) has its own line is NOT VERIFIED. If HIV has its own line, POSSIBLY ADDITIVE at admin1 for one year (the external WHO MDB is national only). GRADE 1.
- INEC "Natalidad y Mortalidad en la Republica anos 1952-2019". Totals only. NEGATIVE.
- CSS ITS statistics 2019 to Oct 2023. Package css-estadistica-de-infecciones-de-transmision-sexual-2019-a-oct-2023, datastore resource 190be1b3-c924-414c-a5d7-ebfa3943a570, read as JSON. Row "INFECCION POR EL VIRUS DE INMUNODEFICIENCIA HUMANA (VIH)": 2019 634, 2020 356, 2021 546, 2022 585, 2023 (to Oct) 362. Social-security sector only, unit (cases or attentions) not stated. WEAK, partial sector. GRADE 1.
- MEF "Informe del Presupuesto del Estado" 2017-2026, by institution. 2024 datastore resource (109148a5-...) 1,073 rows, zero "VIH" hits. NEGATIVE for an HIV budget line. CSS and CGR budget execution sets are institution level. NEGATIVE.

MINSA epidemiology page (/informacion-salud/epidemiologia), read as HTML. Files on minsa.b-cdn.net redirect (301) to minsa.gob.pa.
- "Boletin de VIH-SIDA - Noviembre 2025", .../publicacion-general/boletin_de_vih_sida_noviembre_2025.pdf, HEAD 200, 1,598,618 bytes, Last-Modified 27 Nov 2025. Not opened.
- "Boletin de Vigilancia Epidemiologica de VIH 2022", .../publicacion-general/nota_no.962de3196dgsp.pdf, HEAD 200, 492,203 bytes, Last-Modified 2 Nov 2023. Not opened.
- "Situacion Epidemiologica Nacional" consolidated PDF (20012026). Size not taken (HEAD followed only to 301).
- MINSA statistical yearbooks 1999-2018 (PDF), e.g. .../publicacion-general/boletin_-_2018.pdf, HEAD 200, 2,254,112 bytes, Last-Modified 29 Jun 2020. Not opened.
- CONAVIH page. "Vigilancia epidemiologica del VIH/SIDA Region Ngabe Bugle 2001-2015" PDF. Size not taken.
- Search snippets (UNVERIFIED), source named as Departamento de Epidemiologia, Vigilancia de ITS/VIH/SIDA, MINSA. 1,974 new cases in 2023, 2,104 in 2022. 2023 by health region: Panama Metro 599, Comarca Ngabe Bugle 255, Panama Oeste 230, San Miguelito 191, Chiriqui 160, Herrera 24, Los Santos 22, Kuna Yala 16, Darien 15. To Nov 2024: 1,536 cases (1,240 HIV, 296 AIDS), Metro 426, Ngabe Bugle 258, Panama Oeste 211.
- Assessment. National surveillance new_diagnoses by health region would be ADDITIVE (panel holds only PEPFAR programme counts for PAN). GRADE 2 (PDF bulletins).

Spend.
- MEGAS 2023 PDF, https://www.minsa.gob.pa/sites/default/files/programas/informe_de_medicion_del_gasto_en_vih_2023.pdf, HEAD 200, 4,409,621 bytes, Last-Modified 27 Sep 2024. Probably duplicates GAM 2018 and 2020-2024 unless the report carries a financing-source or programme breakdown. NOT ADDITIVE unless a breakdown is found. GRADE 2.

Round-two retry list adds: www.inec.gob.pa.

## El Salvador (6 October 2026)
Panel position (national, all-sex, all-age rows). 1,940 rows, 480 admin1. domestic_hiv_spend GAM 2015 and 2017-2024 (nine rows, no 2016). hiv_expenditure_total unaids_aidsinfo 2012-2024 (11), GAM 2015-2024 (9). new_diagnoses GF 2022-2025, pepfar_modality and pepfar_panorama 2018-2025. aids_deaths modelled 2000-2025. on_art NONE at national level. hiv_tests_performed GF 2017-2024, PEPFAR 2018-2025, UNAIDS 2019-2024, WHO 2022-2024. WHO MDB (external, not in the panel) holds SLV registered deaths 1997-2018.

REACH.
- onec.bcr.gob.sv (ONEC, the statistics office that replaced DIGESTYC under the central bank in November 2022). curl 200, browser "Request Rejected" (F5 web application firewall) on the root and on /metadatos/index.php/api/catalog/search. BLOCKED. Search result names a NADA catalogue with "Defunciones Generales 2014" (catalog 2, data dictionary F2). Not reached.
- www.digestyc.gob.sv no answer. datos.gob.sv and www.datos.gob.sv no answer. estadisticas.salud.gob.sv no answer.
- simmow.salud.gob.sv (MINSAL morbidity and mortality system) and sumeve.salud.gob.sv (SUMEVE, the official HIV monitoring and surveillance system) curl 403, browser Cloudflare "Sorry, you have been blocked". BLOCKED.
- www.transparencia.gob.sv curl 403, browser Cloudflare challenge. BLOCKED.
- www.salud.gob.sv. curl 522, browser loads. WordPress REST API returns 401 ("Only authenticated users can access the REST API"). Site search returns no results. /descargas/ page readable.
- www.transparenciafiscal.gob.sv 200.

MINSAL /descargas/ (WP Download Manager table, 245 packages, read as HTML). Categories and counts: Informes-VIH 7, Memorias de Labores 20, Boletines Informativos de Indicadores 10 (1999-2008), Boletines de Indicadores del Sistema Nacional de Salud 11 (2009 to 2019-2020), Boletines Epidemiologicos 2021, 2022, 2023 (52 each, weekly), Causas Frecuentes y Principales 2020 (3), Rendiciones de Cuentas 17, POI 10, TB unit 6.
- "Informe Nacional Situacion del VIH en El Salvador" 2018 (informe-nacional-situacion-de-VIH-en-el-salvador-2018_v3.pdf, 3,022,860 bytes, Last-Modified 1 Dec 2020), 2019 version 2 (..._2019_v2.pdf, 2,262,567 bytes, 13 Aug 2021), 2020 (..._2020_v1.pdf, 3,004,257 bytes, 10 Sep 2021). Base path https://www.salud.gob.sv/wp-content/uploads/download-manager-files/. Sizes from in-page HEAD (curl gets 522). Not opened. Presentation versions for 2018, 2019, 2020 also listed. No report after 2020 on the page.
- "Impacto de la pandemia de la COVID-19 en las actividades de diagnostico del VIH 2020". HEAD 522.
- "Diez Primeras causas mas frecuentes de Mortalidad Ano 2020" (Causas_mas_Frecuentes_de_Mortalidad_2020.pdf, 618,816 bytes). Top ten hospital causes only. Probably NEGATIVE for HIV.
- Memorias de Labores 2004-2005 to 2023-2024 (annual reports). May carry HIV programme counts. Not opened.
- Assessment. MINSAL national HIV reports (SUMEVE data) carry new diagnoses by department, LIKELY ADDITIVE as a national surveillance new_diagnoses series and a department split, for years before 2018 and as a source distinct from PEPFAR. GRADE 2. Coverage ends 2020 on the MINSAL site.

MCP-ES site (mcpelsalvador.org.sv, the Global Fund Country Coordinating Mechanism for El Salvador). WordPress media API open, listed by search term (megas, gasto, vih, informe).
- MEGAS (Medicion del Gasto en Sida, the national AIDS spending assessment) PDFs, all HEAD 200, none opened.
  MEGAS-2010.pdf 4,785,507 bytes. MEGAS-2012.pdf 2,741,711. MEGAS-2013-2014.pdf 16,500,164. MEGAS-VIH-2014.pdf 2,469,346. MEGAS-2015.pdf 3,044,029. Anexo_26_MEGAS-preliminar-2016.pdf 969,751. Informe-Medicion-de-Gastos-en-Sida-El-Salvador-2018.pdf 7,719,814. 121020-MEGAS-2019.pdf 4,516,324. MEGAS-2022-FINAL-VAOXXII-IMP.pdf 2,307,848. MEGAS-2023-FINALXXIII.pdf 3,380,841. MEGAS5.pdf 19,644,381 (year unknown). Also a 2025 results deck (Resultados-MEGAS-2025-para-MCP-28052026-1.pptx) and ESTIMACIONESGAM-Y-MEGAS.pptx (2026).
  Search snippet (UNVERIFIED) says MINSAL reports MEGAS from 2005 to 2014.
  Additive test. Panel domestic_hiv_spend starts 2015 and lacks 2016, so domestic (public) spend for 2010-2014 from MEGAS 2010, 2012 and 2013-2014 is LIKELY ADDITIVE, and the preliminary MEGAS 2016 (Anexo_26) would fill the 2016 gap. Financing-source split may also add for 2012-2014 where the panel holds totals only. GRADE 2.
- Global Fund funding-request annexes on the MCP-ES media API (slv_mcp_media_Panorama.json, slv_mcp_media_fundingrequest.json, slv_mcp_media_Tabla-de-datos.json, HEADs in slv_flt_heads.txt). None opened. Re-read on 6 October 2026, when the media API answered a full browser user agent and returned a Mod_Security 406 page to the short user agent "Mozilla/5.0".
  - SLV_VIH_Panorama-Financiamiento20240426_fundingrequest.xlsx, 652,759 bytes, Last-Modified 6 May 2024. The TB funding landscape table 06.SLV_TB_fundingrequest_fundinglandscape_table_aa_TB_04_29_2024.xlsx has the identical size of 652,759 bytes, so the file named for HIV may be a copy of the TB table or of the blank template (NOT VERIFIED).
  - 20240508_fundingrequest_fundinglandscape_table_aa_VIH_GF_4.30pm.xlsx, 1,654,228 bytes, Last-Modified 25 June 2024. Probably the final HIV funding landscape table for the 2024 request (NOT VERIFIED).
  - HIV funding landscape drafts for the 2021 request. 5.-Panorama-Financiamiento.xlsx 186,155 and 5.-Panorama-Financiamiento-1.xlsx 191,441 (uploaded July 2020), 5.-Panorama-Financiamiento24nov.xlsx 193,907 (November 2020), Panorama-Financiamiento-SLV-H-MOH-08022021vr.5pm.xlsx 197,205 (February 2021).
  - Essential data tables. SLV_VIH_Tabla-de-datos-esenciales.xlsx at 250,771 (May 2024) and at 254,258 (June 2024).
  - CLASS NOTE. A Global Fund funding request is expected to carry a funding landscape table with domestic HIV spending by year, past and committed (NOT VERIFIED for any package). The class sweep of Global Fund funding-request documents below covers the 23 LAC countries.
- Programme and finance indicator reports, e.g. Indicadores-Programaticos-VIH-MINSAL_S3.pdf (585,889 bytes, 6 Oct 2023), Indicadores-Financieros-VIH-y-TB-MINSAL_S3.pdf. Grant reporting, overlaps the GF connector. Probably NOT ADDITIVE.
- Prevalence study decks 2023-2024 (01-PPT-Estudio-de-Prevalencia-VIH-2023-2024.pdf, PPT-Estudio-de-Prevalencia-VIH_2024-vf.pdf) and Informe-Final-VICITS-2025.pdf (VICITS, the sentinel STI and HIV surveillance clinics for key populations). Key-population prevalence. NEW INDICATOR, not additive.
- Anexo-Datos-Epidemiologicos-VIH-El-Salvador-2025-2026.pptx (29 Sep 2026). Recent epidemiological deck. Not opened.

Search snippets (UNVERIFIED).
- 946 new HIV cases in 2023 (MINSAL figure reported May 2024). San Salvador 349, La Libertad 141, Sonsonate 78, Santa Ana 78, San Miguel 71. Source observadsdr.org (Observatorio de Derechos Sexuales y Derechos Reproductivos, a civil-society observatory), PDF https://observadsdr.org/wp-content/uploads/2024/12/vih-a-2023.pdf.
- 1,167 new cases January 2024 to April 2025 (resumenlatinoamericano.org, 29 Aug 2025).
- HIV mortality rate stable at 2 per 100,000 between 2022 and 2024 (snippet attached to the ONEC search).

Budget.
- transparenciafiscal.gob.sv Datos Abiertos. "Ejecucion del gasto por clasificacion presupuestaria" 2007-2026 and "por clasificacion economica" 2007-2026, as zips (downloads/zip/700-DINAFI-DA-{year}-CPG.zip) with xlsx dictionaries. curl and in-page HEAD both redirect to the portal index. The portal page shows an image-selection challenge ("selecciona las imagenes relacionadas con") on download. Not attempted. HUMAN-ONLY ROUTE, GRADE 3.5. Whether MINSAL budget lines name HIV is unknown. Search found no HIV work line in the budget law.

Death registration (sec 9ae class). The external WHO MDB holds SLV 1997-2018 and the panel holds no registered deaths. ONEC microdata (2014 named) blocked, MINSAL SIMMOW blocked. No open cause-of-death file reached. NEGATIVE in round one, retry in round two.

Round-two retry list adds: onec.bcr.gob.sv (and /metadatos), digestyc.gob.sv, datos.gob.sv, estadisticas.salud.gob.sv, simmow.salud.gob.sv, sumeve.salud.gob.sv, transparencia.gob.sv.

## CLASS SWEEP. UNAIDS NASA country report library, LAC entries (6 October 2026)
Page unaids.org/en/dataanalysis/knowyourresponse/nasacountryreports, read as HTML (71,552 bytes, 201 PDF links in all). WCA treated this library as one source (PHASE4 sec "NASA / REDES") and set the classification rule. The domestic public, household and private lines are independent. The international line is derived from donor ledgers and does not corroborate the donor connectors.
LAC entries, 47 PDF links, all HEAD 200 (Jamaica 2013-2015 appears twice at the same size, so 46 distinct reports). HEAD status, bytes and Last-Modified are kept in scratchpad lac_nasa_heads.txt. None opened.
By country, report years, against panel domestic_hiv_spend coverage.
- ARG 2006-2009. Panel domestic 2014-2016. ADDITIVE for 2006-2009.
- BLZ 2008-2009, 2021-2022. Panel domestic 2021-2023. ADDITIVE for 2008-2009.
- BOL 2010-2012 (2,262,569 bytes, same file size as the Bolivia entry above). Panel domestic NONE. ADDITIVE.
- COL 2022. Panel domestic 2022 only. Probably duplicate, check the split.
- CRI 2006, 2010. Panel domestic 2014, 2018-2020, 2022-2024. ADDITIVE for 2006 and 2010.
- DOM 2008, 2012. Panel domestic 2013-2024. ADDITIVE. Also fundacionplenitud.org hosts DOM MEGAS 2012 (Informe-Final-MEGAS-2012.pdf 3,154,668 bytes) and MEGAS 2012 with a 2009-2011 time series (Informe-MEGAS-2012-y-Serie-de-Tiempo-2009-2011.pdf 6,550,321 bytes).
- ECU 2005-2007. Panel domestic 2017-2022. ADDITIVE.
- SLV 2005, 2006, 2008, 2010, 2015. Panel domestic 2015, 2017-2024 (no 2016). ADDITIVE for 2005-2010, adds to the MCP-ES MEGAS list.
- GTM 2005-2006, 2009-2010, 2013, 2014, 2015, 2016-2018, 2019-2020. Panel domestic 2011-2013, 2016-2021, 2023-2024 (no 2014, 2015 or 2022). ADDITIVE for 2005-2010, 2014 and 2015. Corrected 6 October 2026 after a year-by-year panel read. The first draft gave the panel range as 2011-2024 and missed the 2014 and 2015 gap.
- HTI 2009-2011, 2016. Panel domestic 2014-2016. ADDITIVE for 2009-2011.
- HND 2006, 2009, 2012, 2013-2014, 2016. Panel domestic 2020-2024. ADDITIVE for 2006-2016.
- JAM 2011-2012, 2013-2015, 2015-2017. Panel domestic 2013-2014. ADDITIVE for 2011-2012 and 2015-2017.
- MEX 2003-2005, 2006-2007, 2008-2009, 2010-2011. Panel domestic 2013 and 2015 (no 2014). ADDITIVE for 2003-2011.
- NIC 2009-2010, 2012. Panel domestic NONE, hiv_expenditure_total 2015-2022 only. ADDITIVE.
- PAN 2004-2006, 2006, 2010. Panel domestic 2018, 2020-2024 (no 2019). ADDITIVE.
- PER 2010. Panel domestic 2020, 2022-2024 (no 2021). ADDITIVE.
- TTO 2002-2006. Panel domestic 2020. ADDITIVE.
- URY 2006, 2007, 2008. Panel domestic NONE. ADDITIVE.
No entry for BRA, CHL, CUB, GUY, PRY, SUR, VEN, BHS, BRB.
Assessment. ONE SOURCE, 17 LAC countries, mostly pre-2012 domestic spending that the panel lacks. GRADE 2 (open PDF, tables read by hand). The panel's spending layer starts in 2011 to 2020 by country, so the library is the only open domestic series for the 2000s.

## Honduras (6 October 2026)
Panel position. 1,884 rows, 469 admin1. domestic_hiv_spend GAM 2020-2024 (five rows). hiv_expenditure_total unaids_aidsinfo 2012-2024 (11). new_diagnoses GF 2022-2025, PEPFAR 2018-2025. on_art_count GF, PEPFAR, UNAIDS, WHO. aids_deaths modelled only. The external WHO MDB holds no Honduras rows.

REACH. ine.gob.hn 200 (WordPress, REST media open). www.salud.gob.hn 200 (new static site). sshome.salud.gob.hn (old SESAL Joomla site with a VIH category, named in search results) no answer from curl. www.sefin.gob.hn 200. datos.gob.hn no answer. portalunico.iaip.gob.hn (transparency portal) 403 to curl. mcp-honduras.hn 406 to curl, loads in the browser, WP REST media 401.

INE Honduras.
- Hechos vitales page lists births 2010-2016 and adolescent mothers only. Media search "defunc" returns nothing. No death publication. NEGATIVE.
- Yearbook health tables 4.1.1 to 4.1.13 (2018-2024). Titles cover attendances, hospital activity, discharges and general hospital mortality rate, establishments. No HIV table by title. NEGATIVE.
- Bases de datos page lists household surveys and ENDESA 2019 (BasesdatosENDESA2019.zip, the Demographic and Health Survey, MICS-style). HIV knowledge and testing questions only. Record for the MICS/DHS class, not additive to panel indicators.
- "17-VIH-y-comportamiento-sexual.pdf" (ENDESA chapter). Same class.

SESAL (Secretaria de Salud).
- New site documents come from a JSON API, /api/unidad/{id}/archivos. Read for units 1-60. 18 documents in all (unit 3 Vigilancia de la Salud has five arbovirus bulletins 2026, unit 40 has surgical waiting-list bulletins). No HIV document. NEGATIVE.
- Old site sshome.salud.gob.hn unreachable from curl. Retry in the browser in round two.
- Search snippets (UNVERIFIED). 918 new HIV cases in the first ten months of 2023, 42,249 cumulative cases 1985 to December 2023 (26,361 advanced infection, 15,888 asymptomatic). Cumulative by department Cortes 15,090, Francisco Morazan 8,598, Atlantida 4,350, Yoro 2,558, Colon 2,142 (swissinfo.ch, elpais.hn). asonapvsidah.org (ASONAPVSIDAH, the national association of people living with HIV) posts "Informe Estadistico de la Epidemia de VIH en Honduras periodo 1985 - Junio 2023", the SESAL statistical report. Departmental new diagnoses would be ADDITIVE (panel holds PEPFAR and GF counts only). GRADE 2 if the SESAL report files are reachable.

MCP Honduras (mcp-honduras.hn, the Global Fund CCM). Shared Files plugin, documents at /shared-files/{id}/.
- Estudios page lists 13 studies. "Estudio Mortalidad Hospitalaria VIH Final.pdf" (id 2159, 2,046,393 bytes) on HIV in-hospital mortality. "Informe Estimacion PC HND 2024.pdf" (id 4465, 2,402,567 bytes), the 2024 key-population size estimate. Stigma index studies, PrEP, drug resistance. NEW INDICATORS, not additive.
- No MEGAS, funding landscape table or essential data table found on Estudios, Informes or Monitoreo pages. Biblioteca menu has no further pages.
- MEGAS for Honduras is on unaids.org instead (see class sweep). NASA_Honduras_2013-2014_es.pdf 2,359,616 bytes, NASA_Honduras_2016_es.pdf 1,841,131 bytes, honduras_2012_es.pdf 2,369,469, honduras_2009_es.pdf 1,167,084, nasa_honduras_06_es.pdf 615,436. Search snippet (UNVERIFIED) MEGAS 2016 national health spending L. 13,557,860,959 with HIV spending L. 744,469,596 (5.49%).
- Observatorio de Derechos Humanos (odh.sedh.gob.hn, a government human rights observatory) has a "Personas con VIH/SIDA" page. Legal references only in the HTML. NEGATIVE in round one.
- ASONAPVSIDAH (asonapvsidah.org, Wix site, blog feed /blog-feed.xml readable). Posts SESAL figures twice a year. "VIH en Honduras: Panorama epidemiologico 2025" (10 Sep 2026) cites the SESAL Unidad de Vigilancia de la Salud "Boletin Epidemiologico de VIH en Honduras 2025", epidemiological weeks 1-53. Secondary text (UNVERIFIED against SESAL). 1,191 cases notified in 2025, 866 men and 325 women, 854 asymptomatic and 337 advanced infection, 44,620 cumulative 1985-2025. Earlier posts cover 1985 to June 2023 and 1985 to December 2023. No file attached to any post. The SESAL bulletin itself was not found on any reachable host. Annual national new_diagnoses by sex from SESAL would be ADDITIVE (a national surveillance series distinct from PEPFAR and GF). GRADE 2 once a SESAL file is found, otherwise secondary only.

Budget (SEFIN, Secretaria de Finanzas).
- Datos abiertos. Monthly execution 2010 to September 2026 and annual formulation 2019, 2023-2026, each as xlsx, csv and json at piep.sefin.gob.hn/odata/egames/{yyyymm} and /odata/faega/{yyyy}00. piep.sefin.gob.hn fails TLS certificate check in curl (exit 60), not fetched.
- JSON schema (jsonschema.txt, read) lists fields Gestion, Mes, Nivel_de_Administracion, Institucion, Fuente_de_Financiamiento, Grupo_de_Gasto, Objeto_de_Gasto, Aprobado, Vigente and execution amounts. No programme or activity field, so no HIV line can exist in these files. NEGATIVE for an HIV budget line. GRADE 1 route, not HIV-specific.

Death registration (sec 9ae class). INE publishes no death tables. The external WHO MDB holds no Honduras rows and the panel holds no registered deaths. NEGATIVE.

Round-two retry list adds: sshome.salud.gob.hn (old SESAL site, curl and browser both failed), piep.sefin.gob.hn (in-page HEAD), portalunico.iaip.gob.hn portal 418 (SESAL transparency documents).

## Nicaragua (6 October 2026)
Panel position. 973 rows, 192 admin1, all admin1 rows from pepfar_snu for 10 departments (Atlántico Norte, Atlántico Sur, Boaco, Chinandega, Chontales, León, Managua, Masaya, Rivas, Río San Juan). Admin1 indicators art_initiations, hiv_tests_performed, new_diagnoses, on_art_count, viral_suppression_count, viral_suppression_pct. No domestic_hiv_spend. hiv_expenditure_total 2015-2022. No aids_deaths, plhiv or new_infections rows. National new_diagnoses PEPFAR only (pepfar_modality 2018 239, 2023 1,206, 2024 953). on_art_count global_fund 2017-2025 and pepfar_panorama 2018-2025. hiv_tests_performed global_fund 2018-2024, PEPFAR 2018-2025, unaids_aidsinfo 2019 and 2022-2024. kp_tested global_fund 2018-2025 by group. anc_hiv_testing_pct unaids_aidsinfo (percentages only). The external WHO MDB holds NIC 2005-2022 (169 HIV deaths in 2022).

REACH. www.inide.gob.ni 200 (behind Cloudflare). www.minsa.gob.ni and mapasalud.minsa.gob.ni no answer from curl or the browser, so both were read through Wayback archived copies (a reading route). www.hacienda.gob.ni 200 (WordPress, REST media redirects to HTML). ccmnicaragua.org does not resolve. The CCM site is mcp.org.ni (found by web search), 200, WP REST media open.

INIDE (Instituto Nacional de Información de Desarrollo, the statistics office).
- Compendios de Estadísticas Vitales, 10 editions 2011-13 to 2022-23. Anuarios Estadísticos, 19 editions 2005-2023. 29 PDF URLs in scratchpad ni_inide_urls.txt, all HEAD 200. Size not given by HEAD (Cloudflare gzip, even with Accept-Encoding identity). None opened.
- Search snippet (UNVERIFIED). The Compendio holds civil-registry deaths by department and cause, including codes B20-B24 (HIV disease). If the HIV line exists, the Compendios add a department split and 2023 beyond the MDB national series. ADDITIVE if confirmed. Download candidate. GRADE 2.
- ENDESA 2011/12 (Encuesta Nicaragüense de Demografía y Salud) .sav files listed open on the bases de datos page. Record for the MICS/DHS class, not additive to panel indicators.

MINSA Mapa Nacional de la Salud (mapasalud.minsa.gob.ni, the health ministry indicator map).
- Wayback CDX for the host, 11,362 lines (scratchpad ni_mapasalud_cdx.txt). Archived pages for the national page, 19 SILAIS pages (SILAIS, Sistemas Locales de Atención Integral en Salud, are the departmental health districts) and municipal pages. Latest SILAIS captures 2024 for six SILAIS, 2023 for four, 2022 for nine. Municipal and sector PDF maps (2017 uploads, about 270,000 to 1,480,000 bytes each) hold facility maps, not HIV tables.
- National page (archived 2024 capture, read as HTML) has a "Situación VIH en los últimos 5 años" table, source "Sistema de información de Vigilancia Epidemiológica", years 2017-2023, 11 indicators per year.
  - Casos nuevos 1,033 (2017), 1,102, 1,118, 953, 938, 1,129, 1,155 (2023).
  - Personas en TAR 4,320, 4,991, 5,696, 5,775, 6,015, 6,567, 7,204.
  - Fallecidos por causas relacionadas al VIH 244, 235, 225, 185, 182, 165, 126.
  - Pruebas de VIH realizadas 150,538, 183,484, 196,400, 219,033, 178,671, 183,847, 310,461.
  - Pruebas de VIH a embarazadas 147,974, 156,063, 130,522, 133,659, 124,034, 124,416, 114,568.
  - Embarazadas captadas con VIH 111, 134, 143, 105, 114, 145, 102.
  - Pruebas de VIH a población clave (HSH, trans, trabajo sexual) 18,378, 15,080, 18,278, 31,191, 28,941, 30,877, 23,639.
  - Niñez con VIH, syphilis tests (out of scope).
- Additive test against the national panel rows.
  - on_art_count. MINSA equals global_fund exactly for 2017, 2018, 2019 and 2023, and differs by 1 to 71 in 2020-2022 (GF 5,846, 6,016, 6,581). DUPLICATE.
  - new_diagnoses. Panel holds PEPFAR counts only (191 to 1,206). MINSA national surveillance series 2017-2023 ADDITIVE.
  - HIV-related deaths 2017-2023. Panel holds no aids_deaths rows. The external WHO MDB 2022 figure is 169 registered deaths against MINSA 165 for 2022, so the two series are close but not identical. ADDITIVE (surveillance deaths, a different count from registered deaths).
  - hiv_tests_performed. MINSA 196,400 for 2019 against unaids_aidsinfo 439,584 and global_fund 39,274. The MINSA figure matches no panel source, so the definitions differ. ADDITIVE as a separate series, definition to settle before use.
  - Key-population tests. MINSA 15,080 to 31,191 against global_fund kp_tested totals 33,923 to 66,219. No match. ADDITIVE as a separate series.
  - Tests in pregnancy and pregnant women diagnosed. Panel holds anc_hiv_testing_pct only, no counts. ADDITIVE.
  - SILAIS split. 19 SILAIS against 10 PEPFAR departments. ADDITIVE for the nine departments with no panel admin1 rows. The Masaya 2024 capture (scratchpad ni_mapa_masaya_2024.html) carries the same table for SILAIS Masaya (2017, 44 new cases, 260 on ART). The other 18 SILAIS pages are not yet checked.
  - Cause-of-death top-15 tables list HIV only when HIV ranks (for example Masaya 2019, 18 deaths). Partial.
- Search snippet (UNVERIFIED). The map went a year without updates.
- Assessment. GRADE 2 through the archive route (HTML tables, readable without downloads). The live route is unreachable. Retry in round two.

MINSA main site (www.minsa.gob.ni, Wayback CDX 177,082 lines, scratchpad ni_minsa_cdx.txt).
- Old /bns/sida/doc/ files. analisisITSVIHSIDA2002.pdf (852,197 bytes), analisisITSVIHSIDA2004.pdf (1,468,516), Estadisticas_VIH_2007.ppt (8,755,153), BOLETIN 2004 1er trimestre (86,158). Pre-2008 surveillance analyses. ADDITIVE for years before the panel's PEPFAR and GF series. Download candidates (archived copies).
- 2010 /bns/sida/doc/ files are posters and leaflets (AFICHE, BISAGRA, FOT-VIH). NEGATIVE.
- Weekly epidemiological bulletins (Boletin SE nn yyyy) archived under /sites/default/files/. 52 for 2021, 51 for 2022, 52 for 2023, 15 for 2024, about 260,000 to 570,000 bytes each. Whether HIV appears in the bulletin tables is NOT VERIFIED. Candidate only.
- 2022-10 uploads include "Estrategia de Promocion de pruebas VIH dirigida a Poblacion clave" (408,846), "Flujo de la Atención en VIH" (1,046,606) and an adherence leaflet. Guidance documents. NEGATIVE.
- Mapa de Mortalidad Materna 2018, 2020, 2022. Maternal deaths only. NEGATIVE.
- News pages 2014-2026 report HIV figures in text (for example "Ministerio de Salud informa avances en la lucha contra el VIH en el I trimestre" 2019, "avanzamos contra vih" 2025). Secondary text, not read in round one.

Budget (MHCP, Ministerio de Hacienda y Crédito Público).
- Presupuesto General de la República, health ministry chapter 19.MinisterioSalud.pdf at hacienda.gob.ni/presupuesto{yyyy}/pgr/. HEAD 200 with sizes for 2020 (373,337 bytes), 2021 (528,873), 2022 (354,856), 2023 (370,492), 2024 (181,876), 2025 (317,718). 2018, 2019 and 2026 redirect (301) away from the PDF.
- 2024 annexes 38.DonacionesPrestamosExternosOrigen.pdf (external donations and loans by origin, 155,444 bytes) and 39.DetalleGastoProgramaFuenteFinanciamiento.pdf (spending by programme and funding source, 188,790 bytes).
- Whether an HIV programme or activity line exists in any chapter is NOT VERIFIED. If present, ADDITIVE (panel holds no domestic_hiv_spend). Download candidates. GRADE 2 if confirmed.

MCP Nicaragua (mcp.org.ni, the Global Fund CCM). WP REST media listing, 911 media items, 14 documents (scratchpad ni_mcp_m.json). Documents are newsletters 2017-2018, a sustainability strategy bulletin, institutional strengthening reports, a TB study and a 2020 MINSA HIV sticker. No funding landscape table, NASA or surveillance file. NEGATIVE.

NASA (class sweep above). NASA_Nicaragua_2009-2010_es.pdf (1,347,469 bytes, files.unaids.org) and NASA_Nicaragua_2012_es.pdf (647,804 bytes, unaids.org). ADDITIVE, since the panel holds no domestic_hiv_spend.

Death registration (sec 9ae class). The external WHO MDB holds NIC 2005-2022 and the panel holds no registered deaths. INIDE Compendios may add a department split and 2023 (UNVERIFIED, above).

Round-two retry list adds: www.minsa.gob.ni and mapasalud.minsa.gob.ni live (curl and browser both failed), the remaining SILAIS HIV tables in the archive, INIDE sizes through the browser, hacienda.gob.ni 2018, 2019 and 2026 chapter paths.

## Jamaica (6 October 2026)
Panel position. 1,375 rows, 232 admin1, all admin1 rows from pepfar_snu for four health regions (North East, South East, Southern, Western). Admin1 indicators art_initiations, hiv_tests_performed, new_diagnoses, on_art_count, prep_recipients, viral_suppression_count, viral_suppression_pct. domestic_hiv_spend unaids_gam_expenditure 2013-2014 (two rows). hiv_expenditure_total unaids_aidsinfo 2012-2022. National new_diagnoses PEPFAR only (pepfar_modality and pepfar_panorama 2018-2025). No aids_deaths rows. plhiv and new_infections unaids_aidsinfo and who_gho. on_art_count global_fund 2017-2025, pepfar_panorama 2018-2025, unaids_aidsinfo 2010-2024, who_gho 2000-2025. The external WHO MDB holds JAM 2000-2014, 13 years (595 HIV deaths in the last year).

REACH. www.moh.gov.jm and hstu.moh.gov.jm return a Cloudflare challenge to curl (403, cf-mitigated) and load in the browser with no challenge, so both were read in the browser. statinja.gov.jm 200. www.mof.gov.jm 200. www.pioj.gov.jm 200 for pages, 403 from a ZENEDGE firewall on /wp-json (not pursued). data.gov.jm, nfpb.gov.jm, rgd.gov.jm, jamaicaccm.org, ccmjamaica.org, jccm.org.jm, jamaicaccm.com and jccmjamaica.org give no answer.

STATIN (Statistical Institute of Jamaica), registered deaths by cause.
- The births, deaths and migration page (Demo_SocialStats/newbirthdeathmarriage.aspx) is an ASP.NET tree. Each table node posts back and returns a page that embeds a dataZoa table (dataZoa is a commercial data-hosting service STATIN uses for web tables). The dataZoa table is an open HTML page at a stable address, read without a download.
- Table 20374 "Occurrences of Deaths of the Total Population Five Years and older, by Cause" (dataZoa th=469BCD578F, series demography/00003675 for HIV disease). Source Registrar General Department, ICD-10. "HIV disease" deaths aged five and over 486 (2018), 445 (2019), 386 (2020), 291 (2021), 316 (2022), 296 (2023).
- Table 20375 males (th=1D851B8D28) 286, 246, 203, 176, 165, 162. Table 20386 females (th=419EAE97B7) 200, 199, 183, 115, 151, 134. Males plus females equal the total in all six years.
- Footnote. NA means values withheld from disclosure (Tuberculosis is NA in every year). Covid-19 deaths come from the health ministry and cover all ages.
- Deaths by parish of residence (20336, th=2357A34124) gives all-cause totals by 14 parishes 2019-2024, no cause split. Not HIV.
- Coverage limit. Deaths under age five are not in tables 20374, 20375 and 20386. The displayed window is 2018-2023. Whether the dataZoa series holds earlier years is not checked.
- Additive test. Panel holds no aids_deaths rows for JAM. The MDB stops in 2014. ADDITIVE for 2018-2023, by sex. GRADE 2 (open HTML table, no query endpoint). Connector candidate that needs no download permission beyond reading HTML.

Ministry of Health and Wellness (moh.gov.jm). WP media 1,959 items, 1,906 enumerated. HEAD sizes, none opened.
- 2017-HIV-Epi-Profile-Jamaica.pdf 1,582,154. HIV-EPIDEMIOLOGICAL-PROFILE-20161.pdf 1,055,099. 2014-HIV-Epi-Update.pdf 1,345,941. 2010.HIV_.EPI_.Update.discussion.pdf 741,115. HIV-Epidemic-Update-Facts-and-Figures-2011.pdf 678,806. AIDS_dataJan_Dec09_final.pdf 874,133.
- National HIV Programme annual reports. NHP_Annual_Report_2006.pdf 2,691,165, 2007 3,453,215, 2008_Pg-30-39 7,074,547, 2010 5,119,415, 2011 3,971,762. FINAL-NHP-Annual-Report-2017.pdf 9,119,436. MOH-2016-Annual-Report.pdf 4,559,334 (National HIV/STI Unit Report 2016). MOH_HIV_STI_Annual-Report-2012-2015.pdf 9,683,264. Annual-Report-final-v5-May-2-2017-min.pdf 936,911.
- Jamaica-NASA-Final-Sept-2012-Final-Report-1-2.pdf 2,409,483. 2014-Global-AIDS-Response-Progress-Report-FINAL.pdf 47,767,346 (GARPR, the UNAIDS country submission, DUPLICATE in principle). Report-NEW-UNAIDS- Annual Report 2020.pdf 19,106,068.
- 543 Weekly-Bulletin-EW files 2015-2026. HIV content not verified. National Surveillance Manual 2009 and July 2026. Guidelines for HIV case-based surveillance. Terms of reference for a KABP 2021 survey and an MSM survey.
- Search snippets (UNVERIFIED). The 2016 profile has Table 1, HIV cases by parish 2011-2016 (Kingston and St Andrew 682 and St James 168 in 2016). The 2017 profile has cases by year and sex 1982-2017 and AIDS deaths by parish 1982-2017. The NSP 2023-2030 was launched, and search text puts people living with HIV at about 30,000.

HIV/STI/TB Unit (hstu.moh.gov.jm). Statistics page /media/statistics/. WP media 37 items. HEAD sizes.
- 2023-HIV_STI_TB-NHP-Annual-Report-FINAL.pdf 4,152,831. 2022-HIV_STI_TB-Annual-Report.pdf 10,305,894. 2021-ANNUAL-REPORT-HIV-STI-TB-FINAL.pdf 4,181,082 (all three uploaded 2026-01-28).
- Bulletins. Bulletin-March-2023-quarter-1.pdf 361,098. Bulletin-December-2022-quarter-4-3.pdf 261,358. Bulletin-September-2022-quarter-3-1.pdf 224,408. HSTU-Bulletin-January-June-2022-1.pdf 383,988. SI-Quarterly-Bulletin-Q1.pdf 713,802 and Q2 650,011 (2021).
- Epi updates. Final-Epi-Update-2013-Revised.pdf 2,957,131. 2015-Epi-Update-Revised-Final.pdf 1,737,426. 2012-Epi-Update.pdf 441,200. NHP.Tables.Jan-Dec.2010.pdf 104,075.
- Safer Sex Week reports 2021 (839,118) and 2025 (1,475,170). Duplicates of the 2009-2017 epi files held on moh.gov.jm.
- The page's "2017 HIV Epi Update" link points to Clinical-Management-of-HIV-Disease-2017.pdf, a wrong target.
- Additive test (on titles and UNVERIFIED snippets). The surveillance reports carry national new diagnoses and AIDS deaths and a split across 14 parishes. Panel new_diagnoses is PEPFAR only, panel holds no aids_deaths, and panel admin1 covers four PEPFAR regions. ADDITIVE if the tables are confirmed. GRADE 2. Download candidates. Gap. No surveillance report for 2018-2020 found.

Budget (Ministry of Finance and the Public Service, mof.gov.jm, page resources-annual-and-supplementary-estimates).
- Estimates of Expenditure PDFs 2005-06 and 2009-10 to 2026-27, with As Passed versions from 2022-23. Sizes from HEAD. 2012-2013 13,963,513. 2017-2018 17,348,427. 2024-2025 As Passed 15,296,705. 2025-2026 As Passed 27,466,667. Supplementary estimates 2011-12 to 2025-26. Public Sector Consolidated Estimates 2019-20 to 2026-27.
- Open data files per budget year (machine-readable). 2017-2018_Budget.xlsx 2,758,977. 2018-2019 3,148,256. 2019-2020 2,951,075. 2020-2021 3,257,787. 2021-2022 2,894,257. 2022-2023_Approved-Budget.xlsx 5,910,088. 2023-2024 3,500,973. 2024-2025 2,773,565. 2025-2026 2,856,856. 2025-2026_Revised-Budget-at-4th.csv 11,733,368. 2026-2027-Approved-Estimates.csv 10,891,264. 2026-2027-As-Presented-Estimates.csv 12,262,651. All last-modified July 2026. None opened.
- JIS articles (Jamaica Information Service, the government news agency, secondary text). The 2017-18 Estimates carry "HIV Prevalence in Most-at-Risk Population Reduced Project", J$492.25 million, funded by the Government of Jamaica and USAID (JIS, 15 February 2017). The 2022-23 Estimates carry "National HIV/AIDS Response in Jamaica Project", J$1 billion (JIS, 17 February 2022). The 2024-25 Estimates carry the same project at more than J$1 billion (JIS, 19 February 2024). The articles quote project targets and achievements by key population (for example 6,879 MSM reached by December 2023). UNVERIFIED against the Estimates.
- Additive test. Panel domestic_hiv_spend is 2013-2014 only. An HIV project line split by funding source in the Estimates is ADDITIVE for the government counterpart share, 2017-18 onward. The external funding inside the same project (USAID, probably the Global Fund for the later project, NOT VERIFIED) is DUPLICATE of donor series and must be kept apart. GRADE 1 if the open-data xlsx and CSV files carry project lines with funding source, GRADE 2 through the PDFs. Download candidates (one xlsx first, to settle the structure).

PIOJ (Planning Institute of Jamaica). The Economic and Social Survey Jamaica (ESSJ) full volume is sold through the PIOJ shop (US$35). Overview and selected-indicators editions are free through the same shop (2014-2018 and 2025 listed), behind a cart step. The ESSJ health chapter draws on ministry surveillance, so the ESSJ adds little beyond the ministry reports. GRADE 3 for the full volume (paid). Not pursued.

CCM (JCCM, Jamaica Country Coordinating Mechanism). No site found. Six candidate domains give no answer. The ministry tender page holds terms of reference for a JCCM oversight consultant (CCM Evolution initiative 2020-2023). NEGATIVE for round one.

NASA (class sweep above). JAM 2011-2012, 2013-2015, 2015-2017. The NASA 2012 report is also on moh.gov.jm (2,409,483 bytes). ADDITIVE for 2011-2012 and 2015-2017.

Round-two retry list adds: data.gov.jm, nfpb.gov.jm (National Family Planning Board), rgd.gov.jm (Registrar General Department), a JCCM site, the dataZoa series history before 2018, and surveillance reports for 2018-2020.

## Trinidad and Tobago (6 October 2026)
Panel position. 669 rows, no admin1 rows. domestic_hiv_spend unaids_gam_expenditure 2020 only. new_diagnoses PEPFAR 2018-2025 only. No aids_deaths rows. plhiv and new_infections who_gho only. on_art_count pepfar_panorama 2019-2025, who_gho and who_tme. The external WHO MDB holds TTO 1999-2020.

Scope question for Jason. regions.py excludes high-income countries, and the World Bank has listed Trinidad and Tobago as high income for most years since 2006 (NOT VERIFIED for the current list). Panama and Guyana need the same check.

REACH. health.gov.tt 200 (not WordPress, /wp-json 404). nacc.gov.tt redirects to health.gov.tt/nacc. cso.gov.tt 200 (WordPress). www.finance.gov.tt 200 (WordPress, media API 401). ttparliament.org 200 (WordPress, media API 401). data.gov.tt shows "Under Maintenance". opm.gov.tt, planning.gov.tt and legalaffairs.gov.tt up.

CSO (Central Statistical Office). WP media 2,565 of 2,656 items enumerated (scratchpad tt_cso_media.json). Cause-of-Death-by-Sex-and-Age-Group-2011.xls.xlsx 279,961 bytes, one year. REVIEW-OF-VITAL-STATISTICS-2008.pdf 22,550 bytes. Other death files 2012-2018 are tables by age, sex and month with no cause. The MDB already holds 1999-2020. DUPLICATE for 2011, NEGATIVE otherwise.

Ministry of Health and NACC (National AIDS Coordinating Committee, inside the ministry).
- The HIV/AIDS Coordinating Unit page holds an HIV rapid testing SOP only.
- NACC reports page. Amalgamated NCPI 2021 (National Commitments and Policy Instrument, the UNAIDS policy questionnaire), the Green Paper on HIV policy, the workplace policy, the Operational Plan 2013-2014 and the NSP 2013-2018. Policy documents. NEGATIVE for data.
- Wayback CDX for health.gov.tt (1,654 lines) and the NACC paths (61 lines). Only "MoH Statistical Report 1994-1995" (1,844,743 bytes) and an Epidemiologic Update of May 2021 (COVID) carry statistics. The World AIDS Day 2023 page has no figures. NEGATIVE.

Budget, Ministry of Finance (finance.gov.tt). Each estimates volume is a separate post.
- Draft-Estimates-of-Development-Programme-2026.pdf 2,348,861 bytes. Draft-Estimates-Details-of-Recurrent-Expenditure-2026.pdf 164,148,746 bytes.
- PSIP (Public Sector Investment Programme, the narrative report on capital projects) posts 2017-2026 plus Tobago 2021. Trinidad-PSIP-2017.pdf 4,436,840. PUBLIC-SECTOR-INVESTMENT-PROGRAMME-2020.pdf 10,174,617. PSIP-Trinidad2025-Final-Digital.pdf (PSIP 2026) 6,499,241. The 2023 post page lists no file link. Narrative, so a weaker route than the estimates.

Budget, Parliament Financial Scrutiny Unit (ttparliament.org). A budget guide per ministry head (Head 28 is the Ministry of Health) summarises recurrent and development spending with allocation and actual for earlier years. Pages /publications/budget-summaries/, /budget-summaries-2/ and /budget-summaries-2025-2026/ list the files. HEAD sizes, none opened.
- Budget-Summary-2022-Ministry-of-Health.pdf 1,501,769. BG2023_MOH.pdf 1,405,374. BG2024_MOH.pdf 1,469,801. bg2025-h28-MOH.pdf 1,161,990. MOH-Budget-Guide-2026.pdf 1,913,424. 2562.pdf "Head 28 Ministry of Health" 1,069,964 (uploaded 2022-01, budget year NOT VERIFIED).
- Older Head 28 files found through the Wayback CDX, all live. b2001h28.pdf 23,595. b2004h28.pdf 647,283. b2006h28.pdf 31,074. b2007h28.pdf 50,909. b2011h28.pdf 48,912. b2019h28.pdf 217,196. b2019h28g.pdf 109,653. Content NOT VERIFIED (the small files may be supplementary appropriations).
- Joint Select Committee reports on the ministry (p11 and p12 series, 2017-2024) also sit in uploads. Oversight reports, not a data series.
- Search snippets (UNVERIFIED). A guide reports the Development Programme item "Special Programme HIV/AIDS" in 2017-2018 with allocation TT$5,500,000 and actual TT$2,995,578. The 2026 guide reports TT$43.8 million allocated for HIV/AIDS activities in fiscal 2025 with TT$38.8 million spent, and TT$0.3 million for the NACC national policy project.
- Additive test. Panel domestic_hiv_spend is 2020 only. An HIV allocation and actual line per year from the guides is ADDITIVE for the other years, if the line is confirmed and the series is consistent across guides. GRADE 2. Download candidates (one guide first, BG2024_MOH.pdf, to settle the structure).

CCM. No national Trinidad and Tobago CCM site found. Trinidad and Tobago has no national Global Fund request or document (Global Fund class sweep below). The Global Fund API lists Caribbean multi-country grants under the labels MCC, Multicountry Caribbean (grants QRB-C-CVC and QRB-C-OECS), and CARICOM/PANCAP (grants QRA-H-CARICOM, QRA-304-G01-H and MAC-910-G02-H), in gf_grants_all.json. Whether Trinidad and Tobago is among the countries served by the Caribbean multi-country grants is NOT VERIFIED. Corrected 6 October 2026, after the API showed no grant code starting QME, so the earlier code QME was wrong. NEGATIVE.

NASA (class sweep above). TTO 2002-2006. ADDITIVE for those years.

Round-two retry list adds: data.gov.tt after maintenance, the content of the b20xxh28 files, and the year of 2562.pdf.

## Guyana (6 October 2026)
Panel position. 1,280 rows, no admin1 rows. No domestic_hiv_spend rows. new_diagnoses PEPFAR 2018-2022 only. aids_deaths unaids_aidsinfo and who_gho. The external WHO MDB holds GUY 1991-2020.

REACH. statisticsguyana.gov.gy 200 for the home page, then an Apache 403 to curl on every inner page and a Cloudflare 403 on /wp-json (blocks, not pursued). The same inner pages load in the browser with no challenge and were read there. health.gov.gy 200 (WordPress). finance.gov.gy 200 (WordPress). parliament.gov.gy 200, www.parliament.gov.gy 403. dpi.gov.gy 200. naps.gov.gy, data.gov.gy and ccmguyana.org give no answer.

Bureau of Statistics. The demography and vital statistics subject page lists 18 web tables. The only deaths table is "Yearly and Quarterly Deaths by Region and by Sex, Guyana 2009 to 2025" with no cause split. Other tables cover births, marriages, migration, child survival 2007-2017 and nutrition. Publications list the DHS 2009 final report (HIV testing module, survey class), MICS5 2014, the 2018 women's health survey and census volumes. No cause-of-death table. NEGATIVE for HIV deaths. The MDB already holds 1991-2020.

Ministry of Health (health.gov.gy). WP media 85 documents. Newsletters 2025-2026, guidelines (STI 2024, PrEP and nPEP 2022, hepatitis B 2022), legislation and World Bank project safeguards. No surveillance or annual HIV report. NEGATIVE.
- Wayback CDX (5,062 lines, scratchpad gy_moh_cdx.txt). Health Statistical Bulletins 2004-2009 archived only. moh_stats_bulletin_04.pdf 652,093 bytes, _05 122,907, _06 121,002, _07 2,578,762, _08 1,602,260, _09 1,906,226 (sizes from CDX). GHDx lists the bulletin series for 2004-2009 only. HIV content NOT VERIFIED. If the bulletins carry HIV cases or deaths by region, the region split is ADDITIVE (panel holds no GUY admin1 rows) for 2004-2009. GRADE 2 through the archive.
- Search text (UNVERIFIED) cites a "National AIDS Programme 2023 Annual Report" with 94-72-87 against the 95-95-95 targets. No copy found online. The National AIDS Programme Secretariat (NAPS) has no live site. GRADE 3.5 for the NAPS annual reports until a copy is found.

Budget (finance.gov.gy, /budget/budget-estimates/, six listing pages). Estimates in three volumes per year, 2010-2026 (Volume 3 from 2010, Volume 1 and Volume 2 for nearly all years). Sizes from HEAD. volume_1_2010.pdf 5,144,406. volume_2_2010.pdf 2,043,844. volume_1_2016.pdf 12,991,213. volume_2_2016.pdf 10,586,434. Volume 1 2022 10,697,185. Volume 2 2022 3,833,749. 2026 Volume 1 12,117,852, Volume 2 6,965,982, Volume 3 6,365,069. Mid-year reports 2010-2026. Whether a Ministry of Health programme or capital project carries an HIV line is NOT VERIFIED. News text (UNVERIFIED) lists eight health programmes in 2022 and no named HIV programme. If an HIV line exists, ADDITIVE (panel holds no GUY domestic_hiv_spend). Download candidate (one Volume 2 first).

CCM. A Guyana Global Fund CCM exists (DPI news, 2018) with no website found. NEGATIVE.

NASA. The class sweep found no NASA report for GUY. PAHO Core Indicator 93 carries GUY new diagnoses 2012-2025 from the ministry and NAPS (section below), the only open national surveillance series found for Guyana.

Round-two retry list adds: a NAPS annual report copy, the content of the 2004-2009 bulletins, and the parliament.gov.gy documents-laid library (the HIV policy document sits there).

## Suriname (6 October 2026)
Panel position. 954 rows, 8 admin1 rows from pepfar_snu (five districts). No domestic_hiv_spend rows. new_diagnoses PEPFAR 2018-2019 only (59 and 37, PEPFAR-supported sites). aids_deaths unaids_aidsinfo 2000-2024 and who_gho 2000-2025. The external WHO MDB holds SUR 1995-2014.

REACH. statistics-suriname.org 200 (WordPress, media API 2,098 items, scratchpad sr_abs_media.json). gov.sr 200 (WordPress behind Cloudflare with no challenge to curl, media API 4,216 items, sr_gov_media.json). www.dna.sr 200 (the National Assembly, Umbraco CMS). www.cbvs.sr 200. bogsuriname.com answers with a stale 2021 page carrying spam links, media API 404. No answer from bog.gov.sr, ccmsuriname.org, planningsbureau.net or financien.gov.sr.

ABS (Algemeen Bureau voor de Statistiek, the national statistics office). The population statistics page lists the Demografische Data publications (2009-2014, 2013-2016, 2015-2018, 2017-2019, 2018-2021). The keywords on every listing name birth, death, maternal, child and age-specific mortality rates. No listing names cause of death. HEAD sizes, none opened.
- Demographic Data 2018-2021 4,304,699. Demographic Data 2017-2019 9,316,777 (tables docx 362,915). Demografische Statistieken 2015-2018 15,810,806 (tables docx 211,119). Demographic Data 2013-2016 18,371,616. Demographic Data 2009-2014 3,625,917.
- Statistical Yearbook 2020-2022 (corrected January 2025) 13,616,117. 2019-2020 34,267,347. 2018-2019 12,125,510. 2016-2017 4,015,219. 2013 5,117,488.
- ODIN 5.1-5.2 "Diseases prevalence, immunization data and other relevant health statistics 2015-2021" docx 33,538. ODIN 6.2-6.6 mortality and fertility indicators 2018-2020 docx 16,742. ODIN (Open Data Inventory, the Open Data Watch assessment that prompted these uploads).
- 3._SDG-3_Health-REVISED.xlsx (April 2026) 2,232,629, plus 3.Final_SDG-3_Health_MARCH-2025_AK.xlsx. SDG 3.3.1 (HIV incidence) in national SDG tables usually copies the UNAIDS estimate, NOT VERIFIED here.
- Health budget files. Begroting Volksgezondheid 2019-2020 docx 30,143. Health budget by functional categories 2013-2018 docx 33,293. ODIN 4.3 health expenditure, budget and planning 2020, 2021 and 2022 doc files.
- Census 8 Volume III Fertiliteit en Mortaliteit 893,933. Crude death rate by sex 2000-2017 (rate only). Gender publications 2021, 2023 and 2025.
- Additive test. The MDB stops at 2014. A table of deaths by cause in Demographic Data 2018-2021 or a yearbook would be ADDITIVE for HIV deaths from 2015, but no listing names cause of death, so the table is NOT VERIFIED. ODIN 5.1-5.2 may carry HIV case counts 2015-2021, which would duplicate PAHO indicator 93 (next paragraph) if the counts are national totals.

Ministry of Health (Volksgezondheid, now Volksgezondheid, Welzijn en Arbeid). No ministry site of its own. News goes through gov.sr.
- The World AIDS Day 2021 page on gov.sr (HTML, read) states 597 new diagnoses in 2018, 598 in 2019 and 414 in 2020, and an estimated 5,200 people living with HIV. The earlier search snippet with the same three counts is now confirmed.
- PAHO Core Indicator 93 holds SUR 2012, 2013, 2015 and 2018-2024 (2012 505, 2013 470, 2015 511, 2018 597, 2019 598, 2020 414, 2021 552, 2022 507, 2023 685, 2024 686), with the provider "Ministry of Health of Suriname. National Aids Programme (NAP)" up to 2019 and later variants of the ministry name. The gov.sr counts are DUPLICATE of PAHO.
- A later gov.sr page (no date in the markup) quotes the ministry HIV focal point with an estimate of 8,000 people living with HIV, about 4,000 aware of their status and 85% of those in care. Narrative. NEGATIVE.
- A 2025 journal paper (PMC12229956, interrupted time series on testing, enrolment, ART and mortality) draws on the national HIV test database and the HIV patient management information system. Those registers are not open. GRADE 3. Search snippet (UNVERIFIED) from the same literature, HIV mortality 7.8 per 100,000 in 2019, rising after 2021.

Budget, National Assembly (dna.sr, /wetgeving/surinaamse-wetten/begrotingen/). One page per year 2010-2026 (scratchpad sr_dna_begroting_links.txt, 159 file links). Up to 2017 each ministry has its own budget law. From 2018 one law covers all ministries. HEAD sizes, none opened.
- Volksgezondheid laws. S.B. 2011 no. 122 634,571. S.B. 2012 no. 109 1,194,186. S.B. 2013 no. 76 1,143,092. S.B. 2014 no. 138 599,575. S.B. 2015 no. 125 1,273,991 (supplementary S.B. 2015 no. 187 107,782). S.B. 2016 no. 87 695,936 (supplementary S.B. 2016 no. 170 9,126,339). S.B. 2017 no. 115 7,149,804. No health law in the 2010 list.
- Whole-budget laws. S.B. 2018 no. 42 4,981,591. S.B. 2019 no. 95 7,276,496. S.B. 2021 no. 6 (budget 2020) 5,530,353. S.B. 2021 no. 103 7,428,502. S.B. 2022 no. 108 7,672,443. S.B. 2023 no. 46 7,204,514. S.B. 2024 no. 19 17,693,526. S.B. 2025 no. 122 12,681,018. S.B. 2026 no. 82 12,499,275 (also on sris.sr). Draft budgets 2021 (6,674,142) and 2022 (8,546,348), and the Financieel Jaarplan 2026 (6,710,353).
- Search snippets (UNVERIFIED). The 2011 health law carries "Global fund ter bestrijding van HIV/AIDS, Tuberculose en Malaria" at SRD 19,909,000. Later laws carry "Aanpak HIV/AIDS, Tuberculose en Eliminatie van Malaria" at SRD 37,483,000 (2018), SRD 19,326,000 (2021, under an "Ovh/Global Fund" heading) and SRD 60,000,000 (2022).
- Additive test. The panel holds no SUR domestic_hiv_spend. The budget line joins HIV, TB and malaria and appears to pass Global Fund grant money through the state budget, so the line does not measure domestic HIV spending. ADDITIVE only as a separate series (state-budget HIV, TB and malaria programme allocation, with the financing source recorded), never as domestic_hiv_spend. GRADE 2. Download candidate (S.B. 2014 no. 138, the smallest health law, to settle the line structure).
- gov.sr Begrotingsuitvoering (budget execution) reports, quarterly and annual 2023-2026 (sizes not returned, chunked transfer). Whether execution reaches programme level is NOT VERIFIED. Begrotingsuitputting 2021 per ministry, the health file and the overview both 404 although listed in the media API.

BOG (Bureau voor Openbare Gezondheidszorg, the public health bureau that keeps the cause-of-death register). The site is stale. The register reaches the public only through the MDB, which stops at 2014. NEGATIVE, GRADE 3.5 for the register after 2014.

CCM. A Suriname Global Fund CCM exists (a governance manual sits in the WHO medicines library, and the UNAIDS 2020 country report credits the CCM with the 2021-2024 grant of US$2,355,648, UNVERIFIED). No CCM website answers. NEGATIVE.

NASA. The class sweep found no NASA report for SUR.

Round-two retry list adds: the content of ODIN 5.1-5.2, a cause table in Demographic Data 2018-2021, and the HIV line in one health budget law.

## PAHO Core Indicator 93 coverage for the LAC set (6 October 2026)
Query on Indicators_Data_2022 (model 3091957, read through the public querydata API, scratchpad paho_ci.py and paho_ci93.json). Indicator 93 is the count of new HIV diagnoses reported by each ministry. 833 rows in all regions.
- Years per country. ARG 2003-2024 (22). BLZ 1995-2025 (31). BOL 1995-2025 (31). BRA 1995-2024 (30). COL 2014-2025 (12). CRI 2011-2025 (15). CUB 1995-2025 (31). DOM 2014-2025 (11). ECU 2015-2025 (11). SLV 2008-2025 (18). GTM 2010-2023 (14). GUY 2012-2025 (14). HND 2008-2024 (17). JAM 2009-2024 (16). MEX 1995-2025 (31). NIC 2010-2025 (16). PAN 2001-2024 (24). PRY 2014-2025 (12). PER 2009-2025 (16). SUR 2012-2024 (10). TTO 2014-2025 (12). VEN 2014-2020 (7). HTI none.
- GUY values. 2012 820, 2013 833, 2014 597, 2015 705, 2016 855, 2017 961, 2018 772, 2019 807, 2020 293, 2021 590, 2022 459, 2023 628, 2024 449, 2025 528. The Guyana NASA line, first written as 2018-2024, now reads 2012-2025 from the Core table.
- TTO 2014-2025 (2014 1,053 to 2025 401), providers the Ministry of Health and the National Health Authority. Additive against the TTO panel position (PEPFAR new_diagnoses only).
- HTI has no rows in the Core table. The Interactive HIV Data Dashboard rows for HTI (the "Ministry of Health of Guyana. NAPS" anomaly in the PAHO section above) therefore have no counterpart in the Core table. Round two should settle which PAHO table is the source for HTI.
- Consequence for every country section. A national new-diagnosis count found on a ministry page is DUPLICATE when PAHO indicator 93 already holds the same year. PAHO indicator 93 itself is ADDITIVE for all 22 countries listed, because the panel new_diagnoses rows are PEPFAR and Global Fund programme counts only.

## Belize (6 October 2026)
Panel position. 894 rows, 3 admin1 rows from pepfar_snu (Belize, Cayo and Orange Walk districts, hiv_tests_performed only). domestic_hiv_spend unaids_gam_expenditure 2021-2023. hiv_expenditure_total unaids_aidsinfo 2012-2022 (3 rows). new_diagnoses NONE. aids_deaths unaids_aidsinfo 2000-2024 and who_gho 2000-2025. on_art_count global_fund 2017-2025. The external WHO MDB holds BLZ 1997-2022. PAHO indicator 93 holds BLZ 1995-2025 (31 years).

REACH. sib.org.bz and www.health.gov.bz return 406 to curl with a short user agent, and both load in the browser with no challenge (recorded as "406 to curl, browser loads with no challenge", not a block). nacbelize.org 200. www.pressoffice.gov.bz 200 (WordPress, media API 2,682 application items, scratchpad blz_press_media.json). www.audit.gov.bz 200 (WordPress, 106 items, blz_audit_media.json). www.belize.gov.bz 503. www.nationalassembly.gov.bz redirects to a cPanel suspended page. No answer from mof.gov.bz (Wayback holds a capture from 29 September 2026, so the host is up but silent to curl), med.gov.bz, ccmbelize.org or hecopab.gov.bz. The Wayback Machine refused connections for several minutes after about 40 requests in a row, then answered again.

WHO MDB registered HIV deaths, BLZ, all ages both sexes. 1997 17, 1998 30, 1999 44, 2000 47, 2001 31, 2002 68, 2003 84, 2004 85, 2005 76, 2006 75, 2007 79, 2008 62, 2009 101, 2010 104, 2011 99, 2012 105, 2013 110, 2014 101, 2015 114, 2016 121, 2017 131, 2018 113, 2019 95, 2020 52, 2021 95, 2022 71. All-cause deaths 2017 1,870, 2018 1,917, 2019 1,990, 2020 1,422, 2021 2,444, 2022 2,269. The 2020 fall in both series (HIV 52, all causes 1,422) points to incomplete registration in 2020, not to a fall in deaths.

SIB (Statistical Institute of Belize). Media API 1,067 items. Abstract of Statistics 1984-2025 sizes recorded in an earlier session. "MOH Metadata" page id 5870.
- Abstract Table 3.11 (2021, read as HTML) gives 2,493 deaths in all, of which HIV disease 71 (2.8%), source Ministry of Health. MDB 2021 reads 95 HIV deaths of 2,444. MDB 2022 reads 71, which may be a coincidence or a year shift. The SIB table is a separate ministry tabulation for one year that differs from the MDB. LOW PRIORITY, flagged for the reconciliation page if ever used.
- Health files, HEAD sizes, none opened. HealthStatistics.xlsx 53,678. DeathCauses2021.xlsx 34,755. CommunicableNonCommunicableDiseases2021.xlsx 25,497. AdministrativeHealthStatistics2021.xlsx 28,193. OtherStatisticsTable.xlsx 10,143. MetaDataTable.xlsx 10,418.
- Surveys. KAP_SBS_2013_Report.pdf (2013 survey of knowledge, attitudes, practices and sexual behaviour) 4,901,797. SBSBrochure.pdf 1,337,965. SexualBehavior.pdf 599,835. MICS_Main_Report_2006.pdf 1,498,287. MICS4_Report_2011.pdf 16,216,823. MICS5_KeyFindingsReport_2015.pdf 3,540,142. MICS5_Report_2015.pdf 7,668,594. MICS7KeyFindingsReport.pdf 8,024,714. ChronicIllness_Census2010.pdf 5,678,193. LGBTQ_LegalEmpiricalAnalysisBelize.pdf 138,555,534. The survey files carry knowledge and testing indicators, none of which is a panel indicator. NEGATIVE for the panel.

Ministry of Health and Wellness (health.gov.bz). The live site is a contact-only placeholder since about June 2025. Wayback CDX holds 2,051 HTML captures and 404 application captures (blz_moh_cdx_html.txt, blz_moh_cdx.txt, blz_moh_attach_cdx.txt).
- The 2022 Epidemiology Unit page (read) describes the unit and lists no report.
- The old Joomla site (2010-2019) carried an "HIV/AIDS/Tuberculosis" publications list with yearly and quarterly HIV/AIDS reports 2004-2009, a statistical report 2011, data 2012, programme reports 2013, an annual report 2014, surveillance reports 2015 and 2016 and an annual HIV statistical report 2017 (scratchpad blz_moh_hivpages.txt, blz_moh_yearly_summaries.txt).
- Counts written into the archived HTML pages (read). New HIV infections 2004 457, 2005 434, 2006 443, 2007 450, 2009 365 (stated as a 14.1% fall from 2008, so 2008 near 425). New AIDS deaths 2004 86, 2005 76, 2006 75, 2007 79, 2009 101. New AIDS cases 2004 63, 2005 30, 2006 43, 2007 120, 2009 92. Cumulative HIV infections since 1986 reach 2,928 at the end of 2004 and 4,255 at the end of 2007. The quarterly pages for 2007 give 93, 137, 100 (later restated as 96) and 122 new infections, which sum to 452 against the yearly 450. The third-quarter 2009 page states that the count covers only tests run at the Central Medical Laboratory and leaves rapid tests uncounted.
- Additive test, new diagnoses. PAHO indicator 93 reads 457, 434, 443 and 450 for 2004-2007, the same as the ministry pages, so the ministry pages are DUPLICATE for 2004-2007. PAHO reads 314 for 2008 and 326 for 2009 against the ministry figures near 425 and 365. The ministry pages give the provisional counts and PAHO the revised counts. DUPLICATE, with the 2008-2009 difference recorded.
- Additive test, deaths. Ministry AIDS deaths match the MDB for 2005, 2006, 2007 and 2009 and differ by one for 2004 (86 against 85). DUPLICATE of the MDB.
- Files that survive on Wayback, sizes from CDX, none opened. Statistical Report 2011 (article 646) 151,347. TB & HIV Programmatic Report 2014 (article 849) 1,013,770. TB 09 annual report 213,628. plan-2009-2011aids (PDF render) 412,741. National HIV Treatment Guidelines Booklet 732,357. Files NOT archived (404 or never captured) include the 2009 yearly and fourth-quarter reports, Annual Health Report 2009, the 2013 statistics and programme reports, HIV Surveillance Report 2015 and Final Surveillance Report 2016, and the 2008 files under /moh/pdf/HIV/.

NAC (National AIDS Commission, nacbelize.org). WordPress media API holds 110 images and no application files. The /reports/ page links files under /wp-content/uploads/2015/11/, all 200, last modified 5 December 2023. HEAD sizes, none opened.
- Surveillance and statistics. Epi-Report-2010.pdf 1,135,367. HIV-TB-2011-Annual-Report.pdf 562,385. NAP-Statistics-2011-WAD.pdf 1,454,281. Statistical-Report-2011.pdf 208,510 (a different size from the ministry copy of 151,347). Best-Final-HIV-Surviellance-Report-2017-2.pdf 1,224,571. HIV-stats-report-for-2018.pdf 1,541,580. Global-AIDS-Response-Progress-Report-2012.pdf 721,308.
- Annual reports. NAC-Annual-Report-2016-2017.pdf 9,148,351. NAC-ANNUAL-REPORT-2018.pdf 15,295,848. NAC-Annual-Report-2019.pdf 32,111,458.
- Plans and costing. Costing-Belizes-National-Strategic-Plan-for-HIVAIDS.pdf 496,832. Planning-Costing-and-Budgeting-Framework.xls 287,744. ImplementationPlan_NSP_HIV_TB_ViralHepatitis_STIs294-FINAL-PRINT.xlsx 1,765,148. NSP-2016-2020.pdf 1,444,736. ME-Plan-2016-2020.pdf 1,973,232. Belize_NSP_HIV_TB_ViralHepatiti-PRINT.pdf 1,208,728. MESS-Final-Report.pdf 478,162. LFA-Budget-Review-Checklist.pdf 750,414. Test2014.pdf 22,010.
- Dropbox links (not followed). NAC quarterly reports 2021, HIV Testing Report 2019-2020, NAC Annual Report 2020, National HIV Guidelines 2021, MICS 2015-2016, Belize Stigma Index 2019.
- Wayback also holds "The Secretariat" newsletters 2015-2018.
- Additive test. National new-diagnosis totals for 2010, 2011, 2017 and 2018 would duplicate PAHO indicator 93. Two parts of the surveillance reports could be ADDITIVE and are NOT VERIFIED without opening a report. (1) District counts of new diagnoses (the 2009 ministry excerpt discusses district prevalence, and the panel holds no admin1 new_diagnoses for BLZ). (2) People on ART for 2010-2016, before the Global Fund series starts in 2017. GRADE 2. Download candidate (HIV-stats-report-for-2018.pdf, 1,541,580, to settle whether district and ART tables exist).

Budget (Ministry of Finance, mof.gov.bz, via Wayback). Approved estimates archived for 2013-2014 (cdn.gov.bz, 2,301,780), 2015-2016 (1,537,886), 2018-2019 (cdn.gov.bz, 4,974,772), 2024-2025 (955,707) and 2025-2026 (6,017,870). Draft estimates for 2024-2025 (5,773,145) and 2025-2026 (5,811,386). The 2014-2015 link on cdn.gov.bz returns 522 on Wayback. The folders /wp-content/uploads/2023/04 and /2023/09 hold 239 and 210 PDF files with random names, which no archived page maps to a ministry. Whether the estimates carry an HIV line or a NAC subvention line is NOT VERIFIED. The press office lists budget speeches 2018 and 2022-2026 and Budget-for-FY2023-2024.pdf (2,564,058). Additive test. GAM covers 2021-2023 and NASA 2008-2009, so a budget HIV line would add 2013-2020 at best, as an allocation series, never as domestic_hiv_spend. GRADE 2 if the line exists. Download candidate (APPROVED ESTIMATES 2018-19, 4,974,772, from the Wayback copy on cdn.gov.bz).

Auditor General (audit.gov.bz). Reports for 2015-2016, 2016-2017 and 2017-2018 and the office's own budgets. No HIV file. NEGATIVE.

Press office (pressoffice.gov.bz). HIV press releases 2022-2025 (World AIDS Day 2022, the Ministry of Labour workplace policy 2023, the Ministry of Economic Development as the new Global Fund principal recipient in November 2024 and its sub-recipient contracts in January 2025, a new NAC chair in April 2025, two HIV partnership releases in August 2025). Narrative, none opened. NEGATIVE for the panel.

CCM. No Belize CCM site answers. ccm.bz on Wayback is an unrelated site. The Global Fund grant itself is in the panel (on_art_count 2017-2025). NEGATIVE.

Summary for Belize. Nothing new beyond PAHO indicator 93 and the MDB, both already counted as ADDITIVE for the region. Two open questions for round two, both needing one download each with Jason's permission. (1) District and ART tables in the NAC surveillance reports. (2) An HIV or NAC line in the approved estimates.

## Haiti (6 October 2026)
Panel position. 2,627 rows, 1,108 admin1 rows across the 10 departments (pepfar_snu 640, pepfar_agency_snu 468). Department rows from pepfar_snu run 2016-2025 for art_initiations, hiv_tests_performed, new_diagnoses and on_art_count, and 2017-2025 for prep_recipients and viral suppression. Department rows from pepfar_agency_snu run 2018-2025. National rows. domestic_hiv_spend unaids_gam_expenditure 2014-2016. hiv_expenditure_total unaids_aidsinfo 2012-2021 (8) and unaids_gam_expenditure 2014-2021 (7). new_diagnoses global_fund 2021-2023, pepfar_modality and pepfar_panorama 2018-2025. aids_deaths, plhiv and new_infections unaids_aidsinfo 2000-2024 and who_gho 2000-2025. on_art_count global_fund 2017-2025, pepfar_panorama 2018-2025, unaids_aidsinfo 2010-2024, who_gho 2000-2025. hiv_tests_performed global_fund 2021-2024, pepfar_modality and pepfar_panorama 2018-2025, unaids_aidsinfo 2019-2024, who_gho 2022-2024. Outside the panel, the WHO MDB holds no HTI rows and PAHO indicator 93 holds no HTI rows. The PAHO Interactive HIV Data Dashboard holds HTI new diagnoses 2018-2024 (19,041 in 2018 to 13,554 in 2024) under the provider mislabel recorded in the PAHO dashboard section of the LAC notes.

Note on sizes from the Wayback CDX. The CDX length field is the length of the compressed archive record, close to the file size but not equal. Bulletin no 15 reads 3,487,298 in the CDX and 3,634,205 on a live HEAD. The same caveat applies to every size marked "from CDX" in the earlier sections.

REACH. mspp.gouv.ht and www.mspp.gouv.ht 200 (Drupal on Apache). ihsi.gouv.ht 200 (nginx). www.mef.gouv.ht and mef.gouv.ht 200 (LiteSpeed). budget.gouv.ht 200 (www.budget.gouv.ht 404). cscca.gouv.ht 200. www.brh.ht, www.primature.gouv.ht and mpce.gouv.ht 200. ccmhaiti.ht 200. The WordPress media API returns 404 on the MSPP, IHSI, MEF and CSCCA hosts. www.ihsi.ht and ihsi.ht now redirect to znaki.fm, an unrelated site now holding the old statistics institute domain. No answer from pnls.mspp.gouv.ht, pnls.ht, ccmhaiti.org, ccm-haiti.org, sisnu.mspp.gouv.ht, dhis2.mspp.gouv.ht, www.haiti.gouv.ht, www.parlement.ht or www.cscca.gouv.ht. bibliotheque.mspp.gouv.ht (the MSPP documentation library) asks for a login at login.php. GRADE 3, not logged in.

MSPP (Ministère de la Santé Publique et de la Population, the health ministry). The live /publications list holds 735 files, mostly 2022-2026 (scratchpad hti_mspp_pubs.txt). HIV and statistics files, live HEAD sizes, none opened, all last modified 4 June 2026. feuillet info PNLS mars 2024 166,671. Rapport Statistique MSPP 2022 2,299,058. Rapport Statistique MSPP 2023_web 1,821,690. Presentation Annuaire Statistique 2022 3,499,344. Presentation Annuaire Statistique 2023 6,908,610. Rapport des Comptes Nationaux de Santé Janvier 2023 7,373,087. The SRMNIA plan link returns 404. The rest of the live list is press notes, recruitment notices, cholera profiles, emergency statistics and pharmacy lists.

PNLS surveillance bulletins (PNLS is the Programme National de Lutte contre les IST/VIH/SIDA, the national HIV programme inside MSPP). The Wayback CDX for mspp.gouv.ht holds 7,642 application captures (hti_mspp_cdx.txt), and the "Bulletin de Surveillance Epidémiologique VIH/Sida" series is in the captures (hti_pnls_bulletins.txt). Sizes from CDX, none opened. no 1 1,054,511. no 2 1,204,031. no 3 1,290,202. no 4 2,871,770. no 5 1,944,017 (first captured October 2013, so the series began no later than 2013). no 6 3,922,417. no 7 1,512,817. no 8 2,117,872. no 9 893,094 (a February 2015 copy reads 1,094,526). no 10 1,940,763. no 11 1,148,862. no 12 1,115,393. no 14 3,403,866. no 15 3,486,933. no 16 3,591,938. no 17 (March 2018) 4,431,240. no 19 (December 2018) 4,012,684. December 2019 2,356,474. Issues no 13 and no 18 were never captured. Issues no 15, no 16 and no 19 are also live under /sites/default/files/publications, live HEAD sizes 3,634,205, 3,788,621 and 4,322,279.

Other MSPP files on Wayback, sizes from CDX, none opened.
- HIV spending. "REDES 2017 rapport final sur flux ressources et depenses VIHsida en 2016" 709,467 (REDES is the PAHO and UNAIDS method for tracking HIV financing and spending, the regional form of NASA). "Rapport Final REDES 2016" 1,578,834. "RAPPORT REDES.pdf" 839,270, year not given in the file name.
- Health accounts. Comptes Nationaux de Santé 1,471,347 (captured 2013) and a web version 1,471,244. Presentation du rapport des comptes nationaux de santé 380,610. Rapport des comptes nationaux de santé (2) 380,478. The January 2023 health accounts report reads 6,273,184 in a 2025 capture against 7,373,087 on the live HEAD, a gap larger than the compression gap seen on the bulletins, so the live file may be a later version.
- Statistical reports. Annuaire statistique MSPP 2012 version web 1,629,127. Rapport_statistique_Annuel.zip 7,707,889 (2010 capture), with the same folder holding Rapport_2004.pdf 4,967,349, Rapport_2005_2007.pdf 2,974,004 and Rapport_annuel_2006 4,832,349. The three annual reports were also captured separately in 2013.
- Estimates. Profil Estimations projections VIH 2010-2015 1,317,857 and a 2013 version 551,004. Spectrum projections, modelled. NEGATIVE, duplicate in kind of the UNAIDS modelled series.
- Surveys and studies. EMMUS 1994-1995 5,947,188 and EMMUS 2000 5,712,437 (EMMUS is the Haiti DHS, already reached through the DHS class). EMMUS deep analysis of HIV among young women (March 2015) 382,438. Enquête nationale d'évaluation de l'impact du VIH 756,446. ART retention studies 2016 1,384,147, 2017 842,119 and an earlier compressed report 794,560. Stigma and discrimination opinion survey (SEFIS, PNLS, UNAIDS, CDC) 594,027 (a copy on mail.mspp.gouv.ht reads 583,728). Study and survey indicators are not panel indicators. NEGATIVE for the panel.
- Plans. PSNM riposte au VIH 2018-2023 977,998 and the mid-term evaluation of PSNM 2018-2023 2,000,489. Narrative and targets. NEGATIVE for the panel.
- Reports of the national surveillance network for single epidemiological weeks of 2018, 2019 and 2020, cholera commune tables for 2011, COVID-19 daily case notes for 2020 and 2021 in Haitian Creole, LNSP (the national public health laboratory) notices and 330 FBR (results-based financing) captures. NEGATIVE for the panel. Two general national epidemiological bulletins dated February 2013 and May 2013 exist. Whether the February 2013 and May 2013 bulletins carry an HIV table is NOT VERIFIED.

IHSI (Institut Haïtien de Statistique et d'Informatique, the statistics institute). The live vital statistics page lists births, deaths, marriages and divorces, all four marked "En attente" (pending), with no file. The statistics menu has no health theme. The regular publications are national accounts, the ICAE activity index and the consumer price index. The old ihsi.ht domain holds 589 application captures on Wayback and ihsi.gouv.ht holds 292. Health items in the old captures are the health chapter of the living conditions survey ECVH (Enquête sur les Conditions de Vie en Haïti, ECVHVolumeI/sante.pdf 283,741), a mortality table (tableau/MORTALITE.pdf 191,287) and the November 2010 MDG report (OMD_Novembre_2010.pdf 665,460, with an analysis note of 108,310). NEGATIVE. Haiti has no published death registration series at IHSI or in the WHO MDB.

Budget (MEF, the finance ministry, and DGB, the MEF budget directorate at budget.gouv.ht). Read as HTML.
- www.mef.gouv.ht/budgets/lois lists budget laws and decrees from 1849 to 2026, every fiscal year from 2001-2002 on except 2010-2011, 2012-2013, 2017-2018 and 2018-2019 (2016-2017 is present as a rectifying law only). 113 PDF files. Décret établissant le Budget Général 2025-2026 23,040,399 (HEAD).
- /budgets/documents lists Documents Annexes au Budget for 2013-2014 to 2016-2017, 2019-2020, 2020-2021, 2023-2024 and 2025-2026, plus three annexes to the 2024-2025 budget framing letter. 11 PDF files. Annexes 2025-2026 40,656,583 (HEAD).
- /depenses/depense_social lists monthly social spending reports from July 2017 to July 2025, with yearly reports for 2009-2010, 2010-2011 and 2011-2012, 19 PDF files and 17 xlsx files in all. Dépenses sociales 2024-2025 (financement domestique) 276,135 (HEAD). Dépenses Sociales 2011-2012 16,938 (HEAD). budget.gouv.ht carries the same series through August 2026 and a monthly "Solde des Crédits" by section through August 2026.
- Whether the MSPP lines name PNLS or HIV is NOT VERIFIED without opening a file. Additive test. GAM domestic spending covers 2014-2016 only, so a PNLS line would add an allocation or execution series for the other years, never domestic_hiv_spend. GRADE 2 if the line exists. Download candidate (Dépenses sociales 2024-2025 financement domestique, 276,135, to see the level of detail at the smallest cost).

CSCCA (Cour Supérieure des Comptes et du Contentieux Administratif, the audit court). Budget execution reports for 2023-2024 and 2024-2025, reports on the financial situation of the country and the efficiency of public spending (RSFPEDP) for 2022-2023 and 2023-2024, a preliminary report on the 2023-2024 settlement law, opinions on the 2018-2019 and 2019-2020 finance bills, the third PetroCaribe audit report (August 2020), a COVID-19 report, two reports on the PUM emergency programme, contract memoranda and legal texts. No HIV file. NEGATIVE.

MPCE (the planning ministry). WordPress media API, 40 application items. Weekly MPCE bulletins 2026, the register of recognised NGOs since 1982, procedure manuals and eight FSSE reporting forms, including a form named "Fichier Santé" (FSSE-02, 42,409, a form by name, not opened). NEGATIVE.

CCM (Country Coordinating Mechanism of the Global Fund). ccmhaiti.ht answers 200. Wayback holds 108 captures from 2021 to 2025 (two in 2021, 97 in 2024, nine in 2025) with no PDF or office file. The 23 HTML captures are the home page, about.php, feeds, crawler files and the SPIP blog login. ccmhaiti.org, ccm-haiti.org and mcp-haiti.org have no captures. The Global Fund grant itself is in the panel. NEGATIVE.

Additive test.
- National new diagnoses. The PAHO dashboard holds 2018-2024 and the panel holds PEPFAR 2018-2025 and Global Fund 2021-2023. Bulletin national totals for years before 2018 would be ADDITIVE, because no national surveillance count for HTI before 2018 exists in the panel or at PAHO. Bulletin no 19 and the December 2019 bulletin are DUPLICATE of the PAHO dashboard for 2018 and 2019. NOT VERIFIED which years the earlier bulletins cover.
- Department new diagnoses. The panel department rows are PEPFAR programme counts from 2016. Bulletin department tables, if present, would be ADDITIVE for the years before 2016 and a second source for 2016 onwards. Whether the bulletins report by department is NOT VERIFIED.
- People on ART. National ART is DUPLICATE, because who_gho covers 2000-2025 and aidsinfo 2010-2024. Department ART in the bulletins would be ADDITIVE before 2016. NOT VERIFIED.
- Spending. REDES for 2016 is DUPLICATE of the GAM row for 2016. The NASA class sweep already lists HTI reports for 2009-2011 as ADDITIVE, and "RAPPORT REDES.pdf" or the 2013 health accounts may be the same reports. Nothing new beyond the class sweep until a file is opened.
- Statistical reports 2004-2007 and 2012. Department testing and positive counts, if present, would be ADDITIVE, because the panel department series starts in 2016. Rapport Statistique 2022 and 2023 would give a second source for department-years already filled by PEPFAR, useful for reconciliation and adding no coverage.

Summary for Haiti. One candidate series beyond the class sweeps, the PNLS surveillance bulletins nos 1-19 and December 2019, GRADE 2, value depending on the years and the department tables inside. Download candidates for round two, every download needing Jason's permission. (1) Bulletin no 16, live on mspp.gouv.ht, 3,788,621. (2) REDES 2017 on 2016, Wayback copy, about 709,467. (3) Rapport Statistique MSPP 2023_web, live, 1,821,690. (4) Dépenses sociales 2024-2025 financement domestique, live, 276,135. The documentation library is GRADE 3. The bulletin series runs from no 1 (date not read) to December 2019, with no 5 first captured in October 2013.

## Cuba (6 October 2026)
Panel position. 961 rows, 0 admin1 rows. domestic_hiv_spend NONE. hiv_expenditure_total unaids_aidsinfo 2012-2022 (3 rows). new_diagnoses NONE. aids_deaths, plhiv and new_infections unaids_aidsinfo 2000-2024 (25) and who_gho 2000-2025 (26). on_art_count global_fund 2017-2025 (9), unaids_aidsinfo 2010-2024 (15), who_gho 2000-2025 (26) and who_tme 2021-2024 (4). hiv_tests_performed global_fund 2021-2024 (4), unaids_aidsinfo 2019-2024 (4 rows) and who_gho 2022-2024 (3). Outside the panel, PAHO indicator 93 holds CUB 1995-2025 (31 years), ADDITIVE for national new diagnoses. The WHO MDB holds CUB 2000-2021, with 406 registered HIV deaths in 2021 against the UNAIDS estimate of 500 AIDS deaths.

REACH. salud.msp.gob.cu 200 (nginx, Varbase on Drupal, so the WordPress media API returns 410). www.gacetaoficial.gob.cu 301 to /es, which answers 200. www.mep.gob.cu 301 to /es. mep.gob.cu no answer. www.mfp.gob.cu 302 to /inicio/portada, which answers 200, while every file under /ficheros/publicaciones returns 302 to /inicio/forbidden, with or without a referer. The forbidden redirect was not worked around. mfp.gob.cu has no DNS record. www.parlamentocubano.gob.cu 200 (bills only). parlamentocubano.gob.cu 400. onei.gob.cu, www.onei.gob.cu, www.sld.cu and www.ipk.sld.cu have no DNS record. files.sld.cu, temas.sld.cu, bvscuba.sld.cu and instituciones.sld.cu resolve to 190.92.127.122 and give no answer. The statistics office ONEI and the Infomed hosts (sld.cu is Infomed, the national health information network) are therefore reachable only through Wayback. Scratchpad cub_reach.txt.

MINSAP (Ministerio de Salud Pública, the health ministry, salud.msp.gob.cu). The live /anuario-estadistico page links the Anuario Estadístico de Salud (the national health statistics yearbook) for 2011-2019 under /sites/minsap/files/anuarios/2021-03/. The page double-encodes the accent in the 2016-2019 file names (%25C3%25B3), and the double-encoded links return 410, while the single-encoded paths return 200. Live HEAD sizes, all last modified 4 March 2022, none opened (cub_msp_head.txt). 2011 2,848,056. 2012 1,983,845. 2013 2,150,530. 2014 1,079,076. 2015 2,890,199. 2016 (edición 2017) 3,090,776. 2017 (edición 2018) 3,563,783. 2018 (edición 2019) 1,784,776. 2019 (edición 2020) 2,424,500.
- The older MSP WordPress site survives on Wayback (cub_cdx_msp.txt, 318 file rows in cub_msp_files.txt). Sizes from CDX. Anuario-2020.pdf 3,104,850 and Anuario-2022.pdf 2,808,824. Anuario-2020.pdf and Anuario-2022.pdf return 410 live.
- The other MSP captures are calendars of health days, legal texts (ministerial resolutions, decree-laws, laws and gazette copies), Objetivos_2021_MINSAP.pdf 564,236, the draft health law (Anteproyecto de Ley de Salud) 749,876 and the programme of the 2022 Jornadas Cubanas contra la Homofobia y la Transfobia. NEGATIVE for the panel, apart from the yearbooks.

DNE (Dirección Nacional de Registros Médicos y Estadísticas de Salud, the MINSAP statistics directorate, files.sld.cu/dne). Wayback only. 382 file rows (cub_cdx_dne.txt, cub_dne_files.txt). Sizes from CDX, none opened.
- Yearbook PDF, Spanish edition. 2008 672,132. 2009 1,788,893 (a second copy 1,794,545). 2010 863,760 (without charts). 2011 1,596,546. 2012 1,828,334. 2013 2,078,661. 2014 1,007,744. 2015 2,777,021. 2016 (edición 2017) 2,990,537. 2017 (edición 2018) 3,336,470. 2019 (edición 2020) 2,256,569. 2021 (edición 2022) two files, 3,859,744 and 6,635,734. 2022 (edición 2023) 2,813,516. 2023 (edición 2024) 2,056,658. 2024 (AES-2024-para-sitio-3.pdf) 2,297,695. The DNE folder holds only errata for the Spanish 2018 and 2020 editions. Across the DNE folder on Wayback, the live MINSAP page and the MSP site on Wayback, the Spanish yearbook PDF exists for every year 2008-2024.
- Yearbook xlsx. 1998 304,189. 2006 380,311. 2007 483,624. 2008 452,128. 2009 521,780. 2010 1,847,956. 2011 509,126. 2012 436,995. 2013 448,006. 2017 538,597. 2018 512,452. 2019 522,799. 2020 537,221. 2021 two files, 436,713 and 435,317. 2022 444,062. 2023 444,625. No xlsx for 1999-2005, 2014-2016 or 2024.
- English yearbook editions 2010-2019, basic indicator leaflets (Indicadores Básicos) for 2012-2015, 2018, 2020, 2023 and 2024, UNICEF child and women health indicators 2013-2016, morbidity series 1970-2008 (498,520) and 1970-2010 (380,887), time series 1970-2013 (1,964,576), standardised mortality series 2008 and 2010, and MICS reports (Cuba-2000-MICS-2.pdf 326,017, the MICS4 report encuesta-de-indicadores-multiples-e.pdf 1,173,070, mics5-2014-cuba.pdf 2,800,012).
- Content signal for the yearbooks, from two temas.sld.cu posts read as HTML. The post "Estadísticas ITS y sida 2009" (5 April 2011) cites the yearbook table "Incidencia de algunas enfermedades de declaración obligatoria según sexo" (incidence of some notifiable diseases by sex). The post "Estadísticas nacionales de la coinfección VIH-TB en 2010" (24 March 2011) cites the yearbooks and names provinces. Whether the yearbooks give HIV new diagnoses by province is NOT VERIFIED. Provincial HIV tables would be ADDITIVE at admin1, because the panel holds 0 admin1 rows for CUB. The xlsx route is close to GRADE 1 (a structured file, one per year, although not an API). The PDF route is GRADE 2.

ONEI (Oficina Nacional de Estadística e Información, the national statistics office). Wayback only. 4,579 capture rows (cub_cdx_onei.txt). Sizes from CDX, none opened.
- Chapter 19 of the Anuario Estadístico de Cuba (the national statistical yearbook, chapter on public health and social assistance). 2019 PDF 631,121 and zip 1,044,815. 2020 PDF 2,082,071 and zip 1,671,075. 2021 PDF 2,427,529 and zip 2,553,686. 2022 two editions, 19_salud_publica-_asistencia-social-2022-edicion-2023.pdf 460,237 and 19-salud-publica-y-asistencia-social-2022.pdf 539,624. 2024 edition, 19-salud-publica-y-proteccion-social_aec2024.pdf 607,316. A 2023-01 capture of 19-salud-publica.pdf carries a negative CDX length, so the size of the 2023-01 capture is unknown.
- 210 single-table xls files under datos-estadisticos cover chapters 1 to 22 of the national yearbook. None of the 210 xls files belongs to chapter 19.
- nota_dia_mundial_del_sida_2022.docx (an ONEI note for World AIDS Day 2022) 53,253. The gender portal holds 7_EP_VIHsida-2017.pdf 3,364,765, a survey report on HIV knowledge and behaviour. Survey indicators are not panel indicators. NEGATIVE for the panel.
- Provincial yearbooks (anuario_est_provincial) 78 captures and municipal yearbooks (anuario_est_municipal) 724 PDF captures. HIV content of the provincial and municipal yearbooks is NOT VERIFIED. Whether national chapter 19 holds anything beyond the MINSAP yearbook tables is NOT VERIFIED. Until a file shows otherwise, chapter 19 counts as a second route to the MINSAP yearbook figures, not as a new series.

Cuban HIV portal on Infomed (temas.sld.cu/vihsida, 6,447 capture rows, and the older files.sld.cu/sida, 247 file rows of which 226 are not feeds or images). Wayback only.
- Figures on the portal pages are single-year counts quoted from press items, for example 23,283 people living with HIV at 31 October 2017, 83% of all people diagnosed. NEGATIVE as a series.
- National strategic plans, sizes from CDX. 2001-2006 568,136. 2007-2011 957,744. 2014-2018 2,160,330. PEN (Plan Estratégico Nacional) for STI, HIV and hepatitis 2024-2028, 4,736,071. The strategic plans hold narrative and targets. NEGATIVE unless a plan carries a costing annex (NOT VERIFIED).
- CNP bulletins (Centro Nacional de Prevención de las ITS-VIH/sida) no 1 to no 10, 2008-2011, plus a special issue and a supplement of no 10. SITUACIÓN-EPIDEMIOLÓGICA-VF.pdf (May 2016) 202,455. A 2011 report on the situation of sexually transmitted infections 163,000. A copy of the 2012 health yearbook (anuario_2012.pdf) 1,832,648. The UNAIDS 2011 epidemiological fact sheet for Cuba 204,405. Seven bulletin files dated August 2016 to August 2017, three of the seven named Boletín Habana and covering one province. Content of the CNP bulletins and the 2016-2017 bulletins NOT VERIFIED.

Budget. Read as HTML.
- Gaceta Oficial (the official gazette, POST search at /es/getdata). Ley 181 de 2025, Del Presupuesto del Estado para el año 2026, identifier GOC-2025-594-O99, published in Gaceta Oficial No. 99 Ordinaria of 29 December 2025. Gazette issue file goc-2025-o99_1.pdf 852,803 (HEAD). Acuerdo X-173 de 2026 of the national assembly approves the Liquidación (the outturn) of the 2025 state budget.
- MFP (Ministerio de Finanzas y Precios, the finance ministry). The live publications page lists Libro Liquidación del Presupuesto del Estado 2024 (stated 2.65 MB), Libro Presupuesto del Estado 2025 (stated 557.39 KB), Libro Presupuesto del Estado 2026 (stated 1.33 MB) and Libro Liquidación del Presupuesto del Estado 2025 (stated 2.82 MB), plus the budget laws as gazette copies from 2022 onwards. Every live file is forbidden. Wayback copies, sizes from CDX. P-LIBRO[LQ-2024].pdf 2,594,767. P-LIBRO[PP-2025].pdf 554,094. P-LIBRO[PP-2026].pdf 1,247,017. Presupuesto_2025.pdf 567,055 (cub_cdx_mfp.txt, 1,302 capture rows).
- Whether a Cuban budget law or budget book names an HIV programme line is NOT VERIFIED. An HIV line would be ADDITIVE, because domestic_hiv_spend for CUB is NONE in the panel. GRADE 2 if the line exists.

CCM (Country Coordinating Mechanism of the Global Fund, MCP Cuba). The CCM pages sit on the HIV portal (temas.sld.cu/vihsida/mecanismo-de-coordinacion-de-pais) and hold governance documents only, namely statutes, rules and annexes in the sixth revision of 2018 and the seventh revision of 18 March 2022, an ethics code, a 2014 call and timetable for the 2015-2017 concept note, and a 2024 meeting notice. The Global Fund grant itself is in the panel. NEGATIVE.

Additive test.
- National new diagnoses. DUPLICATE of PAHO indicator 93 (1995-2025) for any national count in the MINSAP yearbooks, portal pages or CNP bulletins.
- Province new diagnoses. ADDITIVE if the MINSAP yearbook carries HIV by province, because the panel holds no CUB admin1 rows. NOT VERIFIED.
- Deaths. The yearbook mortality tables would duplicate the WHO MDB for 2000-2021 and could add 2022-2024 as registered HIV deaths. NOT VERIFIED whether the yearbook lists HIV as a separate cause.
- People on ART and tests. National series are DUPLICATE of who_gho, aidsinfo and Global Fund.
- Spending. A budget HIV line would be ADDITIVE as an allocation series, never as domestic_hiv_spend. NOT VERIFIED.

Summary for Cuba. One candidate series beyond PAHO indicator 93 and the MDB, the MINSAP health yearbook 2008-2024 (PDF) and 1998, 2006-2013 and 2017-2023 (xlsx), GRADE 2 for the PDF and close to GRADE 1 for the xlsx, value depending on whether HIV appears by province. Download candidates for round two, every download needing Jason's permission. (1) Anuario-estadistico-salud-2023.xlsx, Wayback copy of files.sld.cu/dne, about 444,625, to see whether HIV appears by province. (2) Failing (1), anuario_2019_edición_2020.pdf, live on salud.msp.gob.cu, 2,424,500. (3) goc-2025-o99_1.pdf, live on gacetaoficial.gob.cu, 852,803, to see whether the 2026 budget law names an HIV line. (4) 19-salud-publica-y-proteccion-social_aec2024.pdf, Wayback copy of onei.gob.cu, about 607,316, to compare ONEI chapter 19 against the MINSAP yearbook. Round two should retry onei.gob.cu and files.sld.cu live.

## Venezuela (6 October 2026)
Panel position. 920 rows, 0 admin1 rows. domestic_hiv_spend unaids_gam_expenditure 2016-2019 (4). hiv_expenditure_total unaids_aidsinfo 2012-2022 (9) and unaids_gam_expenditure 2016-2022 (7). new_diagnoses NONE. aids_deaths, plhiv and new_infections unaids_aidsinfo 2000-2024 (25) and who_gho 2000-2025 (26). on_art_count global_fund 2024-2025 (2), unaids_aidsinfo 2010-2024 (15), who_gho 2000-2025 (26) and who_tme 2020-2024 (5). hiv_tests_performed unaids_aidsinfo 2023-2024 (2) and who_gho 2022-2024 (3). Outside the panel, PAHO indicator 93 holds VEN 2014-2020 (7 years), ADDITIVE for national new diagnoses. The WHO MDB holds VEN 1996-2016, with 2,496 registered HIV deaths in 2016. The NASA class sweep found no NASA report for VEN.

REACH (scratchpad ven_reach.txt). mpps.gob.ve 200, with www.mpps.gob.ve 302 to mpps.gob.ve. The MPPS WordPress media API answers with 251 items. ine.gob.ve 200, with www.ine.gob.ve 301 to ine.gob.ve. The INE media API returns 403. www.mppef.gob.ve 200. The MPPEF WordPress REST endpoints for pages, posts and media return 401 with the code itsec_rest_api_access_restricted (a block set by the iThemes Security plugin, not worked around). mppef.gob.ve returns 404 on http and a self-signed certificate on https. www.cgr.gob.ve 200. www.saime.gob.ve 200. www.imprentanacional.gob.ve and www.ivss.gob.ve answer on http only. www.bcv.org.ve redirects to https, and the https request fails on the certificate chain. www.inhrr.gob.ve 301 to inhrr.gob.ve. onapre.gob.ve, www.tsj.gob.ve, historico.tsj.gob.ve and www.gacetaoficial.gob.ve time out. www.mppre.gob.ve gives no answer. No DNS record for www.onapre.gob.ve, www.mf.gob.ve, asambleanacional.gob.ve, www.asambleanacional.gob.ve, www.accsi.org.ve, accsi.org.ve, www.patria.org.ve and www.minpptrass.gob.ve.

MPPS (Ministerio del Poder Popular para la Salud, the health ministry), live site. Live HEAD sizes, none opened (ven_mpps_head.txt).
- Anuario de Mortalidad (the mortality yearbook) for every year 1995-2017. 1995 1,869,059. 2013 2,244,610. 2014 8,134,734. 2015 2,640,063. 2016 2,822,391. 2017 in two files, 33-Anuario2017.pdf 3,061,890 and ANUARIO_2017C.pdf 3,066,459. The yearbooks for 1996-2012 run from 2,051,685 (2004) to 4,375,344 (2002).
- Anuario de Morbilidad (the morbidity yearbook, notified cases by disease) for 2000-2002, 2004-2008, 2010, 2011 and 2013. 2000 95,912, 2001 107,748 and 2002 134,217, sizes small enough that the 2000-2002 files may hold only part of a yearbook (NOT VERIFIED). 2004 2,289,849. 2013 3,763,740. The 2009 morbidity yearbook survives on Wayback only (Phoca category 15, 2,758,609 from CDX). No morbidity yearbook for 2003 or 2012 was found live or on Wayback.
- Anuario de Natalidad (the natality yearbook) for 2002-2005 and 2012-2014. Births only. NEGATIVE.
- Boletín Epidemiológico (the weekly epidemiological bulletin) for 2026, weeks one to 37. Week one 670,089. Week 37 722,477. Whether the weekly bulletin tabulates HIV is NOT VERIFIED.
- Forms and guides. EPI-14, the weekly consolidated form of notifiable diseases and events, 77,147. The 2005 list of events notifiable to CNERSI (a national notification centre, full name not read) 96,287. Guia-Rapida-VIH_Emergencias_ONUSIDA_2026 1,209,502. Forms, lists and guides hold no counts. NEGATIVE for the panel. The EPI-14 form and the CNERSI list would show whether HIV is a notifiable event.

MPPS on Wayback (the older Joomla site with Phoca Download categories, ven_cdx_mpps.gob.ve.txt). Sizes from CDX unless marked as stated, none opened.
- Weekly bulletins 2002-2014, with missing issues. Whether the 2002-2014 weekly bulletins tabulate HIV is NOT VERIFIED.
- Category 11, mortality yearbooks 1995-2012, the same years as the live site.
- Category 41, Anuario Estadístico (the general statistical yearbook of the ministry, year not given on the category page) in four parts. Part one, demographic data, stated 3.02 MB, CDX 2,529,854. Part two, morbidity, stated 2.16 MB, CDX 1,181,017. Part three, mortality, stated 2.24 MB, CDX 1,192,897. Part four, "Redes de Servicios y Programas de Salud" (service networks and health programmes), stated 2.09 MB, CDX 1,152,906. The gap between the stated sizes and the CDX lengths of parts two to four is far wider than the compression gap seen elsewhere, so the archived copies of parts two to four may be incomplete (NOT VERIFIED). Whether part four reports the HIV programme is NOT VERIFIED.
- Category 2, Indicadores Epidemiológicos (epidemiological indicator books). 2006 16,527,067 (stated 19.01 MB). 2007 61,070,909 (stated 66.56 MB). 2008 60,213,274 (stated 65.17 MB).
- Category 17, surveillance forms, including the HIV case form (fichainfeccionasintomatica-vih-sida) 1,966,737. NEGATIVE, a form.
- GUIA_VIH_2014-2016.pdf 2,554,613, a clinical guideline. The folder /ms/Boletines/sida/ holds guidelines only. The antirretrovirales distribution folder holds no table. NEGATIVE.

msds.gov.ve (the domain of the health ministry under the earlier name Ministerio de Salud y Desarrollo Social). Wayback only, 1,629 capture rows (ven_cdx_msds.gov.ve.txt). Sizes from CDX, none opened.
- Yearbooks under Epidemiologia/Estadistica/Anuarios. Anuario95.pdf 1,619,374 to Anuario03.pdf 1,915,756, then Anuario2004.zip 3,130,290, Anuario2005N.zip 1,677,165, Anuario2006.zip 2,117,599 and Anuario2007.zip 2,226,973. The file names do not say which yearbook. If the msds files are the mortality yearbooks, the msds files are a second route to the live MPPS files (NOT VERIFIED).
- Memoria y Cuenta (the annual report and accounts of the ministry to the National Assembly). Memoria y Cuenta 2002 7,283,771 and 2003 2,499,095, one zip per year. Memoria 2004 2,669,474, 2005 3,430,447, 2006 1,650,198, 2007 1,756,540 and 2008 1,342,180. Cuenta 2004 41,678,116, 2005 39,997,445, 2006 35,727,123, 2007 13,251,449 and 2008 81,659,355. All zip files. Whether the Memoria reports PNSIDA (Programa Nacional de SIDA/ITS, the national HIV programme) spending, or people on ART by state, is NOT VERIFIED.

INE (Instituto Nacional de Estadística, the national statistics office). Sizes from CDX, none opened.
- Estadísticas Vitales (vital statistics bulletins). 12 PDF files named 20001996 to 20122008, with an xls twin for every PDF file, the xls twins running from 17,270 to 39,233 bytes on ine.gob.ve. Most file names join a publication year and a reference year, giving reference years from 1996 to 2008 (reading of the names NOT VERIFIED). 20122008.pdf 9,241,886. Whether the vital statistics bulletins give deaths by cause is NOT VERIFIED. National HIV deaths for 1996-2008 would be DUPLICATE of the WHO MDB.
- Boletín de Salud (the INE health bulletin). The archived directory listing of April 2019 holds three issues only. 201101 5,677,099 (stated 5.4M). 201202 6,261,034 (stated 6.0M, and 5,570,161 for the copy on ine.gov.ve, the older domain). 201303 4,334,687 (stated 4.1M). Indicadores_de_Salud/BoletinSalud.pdf 4,786,574 (stated 5.4M in February 2014). The Indicadores_de_Salud xls folder was empty in February 2014.
- IOE (Inventario de Operaciones Estadísticas, the national inventory of statistical operations), operation 111, lists Cuadro VIH tables at 5,575, 4,135, 5,649 and 4,862 bytes. The producer of the Cuadro VIH tables is NOT VERIFIED.
- The live site links the Anuario Estadístico (the national statistical yearbook) for 2002 and 2003 only. Whether the 2002 and 2003 yearbooks hold a health chapter is NOT VERIFIED.

ONAPRE (Oficina Nacional de Presupuesto, the national budget office). The live host times out, so every ONAPRE file below is a Wayback copy. Sizes from CDX unless marked as stated, none opened. Scratchpad ven_cdx_onapre.gob.ve.txt (2,457 rows), ven_cdx_onapre.gov.ve.txt (159 rows), ven_cdx_onapre_html.txt (450 rows) and ven_cdx_onapre_ip.txt (85 rows).
- Health ministry code in the budget law. Code 49 in 2006, 2007 and 2008, read from the archived index pages ("49 Ministerio de Salud" in 2006 and 2007, "49 Ministerio del Poder Popular para la Salud" in 2008). Code 54 in 2014, read from the archived category pages. Code 54 in 2010 is NOT VERIFIED.
- 2000-2005 (onapre.gov.ve). 2000 Ley de Presupuesto 1,485,224, Distribución Institucional 3,015,322 and Exposición de Motivos 1,668,378. 2001 Ley 2,976,012 and Distribución Institucional 3,262,056. 2002 Ley 3,260,057, Distribución General 3,115,635 and Exposición de Motivos 1,744,779. 2003 Ley 7,186,812 and Distribución General 3,251,653. 2004 Distribución General 27,590,043 and Exposición de Motivos 2,963,742. 2005 Ley 10,538,667, Distribución General 4,875,966 and the Exposición de Motivos of the 2005 bill 1,664,154. Consolidated budget files for 1999 7,246,696, 2000 1,547,581 and 2001 1,683,311.
- 2006 (site.onapre.gob.ve). Título II separata for organism 49, Sep_49.pdf, 6,117,746, captured 12 October 2006. The 2006 separata lengths rise with every organism code, from Sep_01 at 318,149 to Sep_49, so each 2006 separata file may hold every organism up to the code in the file name (NOT VERIFIED). T3_49 and Dist_49 for 2006 were never captured. No code 49 file for 2007 or 2008 was captured.
- 2008-2011 (201.249.236.149:7777, an older ONAPRE server reached by IP address). Exposición de Motivos 2008 1,994,531, 2009 2,366,545, 2010 2,086,260 and 2011 1,820,146. Título I 2008 659,668. 2010 Sep_54.pdf 304,660. Informe Global 2011 1,377,068. No file for 2012 or 2013 was found.
- 2014 (category 5, jDownloads). Decreto de Distribución General 2014 127,981. Título I 275,552. Título II, Capítulo I (revenue) 26,400 and Capítulo III (savings, investment and financing account) 123,515. Título II Capítulo II for the health ministry, 169-54-ministerio-del-poder-popular-para-la-salud, stated 1.41 MB, uploaded 6 August 2014, 837 downloads, CDX 1,061,859, captured 21 August 2017. Distribución por Organismos for the health ministry, 30-54-ministerio-del-poder-popular-para-la-salud, stated 1.66 MB, uploaded 30 July 2014, 816 downloads, CDX 1,405,228, captured 15 August 2017. Two later copies of the health distribution sit in category 488 at 1,405,249 and 1,405,245.
- 2015 (category 46). Título I 270,726. Título II 6,601,069 (stated 6.75 MB, uploaded 23 January 2015). Título III Tomo I 4,901,050, Tomo II 5,184,381 (stated 5.46 MB) and Tomo III 7,500,053 (stated 7.88 MB). Título IV 1,901,679. Resumen de la Distribución General 1,360,893. The 2015 decree category (51) holds 0 files.
- 2016 (category 54). Título I 255,689. Título II 13,649,211 (stated 13.52 MB, uploaded 16 February 2016). Título III Tomo I 13,042,019, Tomo II 16,185,642 and Tomo III 18,469,021. Título IV 2,844,978. Decreto de la Distribución General 11,860,019. Resumen 1,298,840.
- Whether any ONAPRE budget file names a PNSIDA or HIV line is NOT VERIFIED.

MPPEF (Ministerio del Poder Popular de Economía y Finanzas, the finance ministry). The live WordPress Download Manager sitemap (ven_mppef_wpdm_sitemap.xml, 116 entries) lists "Gobierno Central Presupuestario" (budgetary central government) and "Sector Público Restringido" (restricted public sector) files for each year 1998-2009 and as a 1998-2009 series, fiscal aggregates. The other sitemap entries are debt communiqués, a 2023 tender, and manuals for the monetary redenomination. No budget law and no ministry-level execution file is listed. NEGATIVE for HIV (content of the fiscal aggregates NOT VERIFIED).

Gaceta Oficial (the official gazette). www.gacetaoficial.gob.ve times out. The Imprenta Nacional site (the state printer that publishes the gazette) answers on http, links the gazette to www.gacetaoficial.gob.ve, and offers certification and validation pages for single gazette issues. The ONAPRE files already hold the budget law texts for 2000-2016. Gazette search goes to round two.

ACCSI (Acción Ciudadana Contra el SIDA, a Venezuelan HIV advocacy group). Both accsi.org.ve hosts have no DNS record. Wayback holds 917 capture rows (ven_cdx_accsi.txt), 737 of the 917 rows PDF, 648 of the 917 rows captured in 2022. Sizes from CDX, none opened.
- Reports on access to antiretroviral medicines and on shortages. November 2009 to January 2012 663,514. 17 February to 14 March 2014 1,009,549. 28 March to 9 April 2014 651,548. May 2014 1,350,430. June 2014 950,827. Situation at 3 May 2016 643,512. ACCSI-RVG-COVIP report on 2019 1,376,211. ACCSI-RVG report on 2020 875,283. January 2021 to April 2022 3,572,335. Report on antiretroviral medicines at the IVSS (Instituto Venezolano de los Seguros Sociales, the social security institute) 87,492.
- Other reports. IV Informe anual VIH/SIDA y DDHH 1999-2000 186,211. ACCSI-AVESA Informe Comunitario 2008 353,460. Study of ARV adherence and counselling services in seven states 773,831. Gente Positiva bulletins, issues 7 to 35 with gaps, 35 capture rows.
- The ACCSI reports are civil-society monitoring. Any ART count by state quoted from MPPS inside an ACCSI report would be a secondary source (NOT VERIFIED). Most other ACCSI files cover hate crimes. NEGATIVE.

Global Fund and CCM (Country Coordinating Mechanism). No separate Venezuelan CCM site was found. Web search snippets (UNVERIFIED) name UNDP Venezuela as Principal Recipient for 2024-2026, give a grant of USD 21.7 million for HIV and TB with USD 6.13 million spent in 2024, and date the Plan Maestro (the master plan for the HIV, TB and malaria response) to 2018, drawn up by MPPS, PAHO, UNAIDS and civil society. The Global Fund board annex archive_bm39-edp11_annex_es.pdf answers 200 at 2,141,182 (HEAD, last modified 3 March 2025), with an English version at 2,117,172. The Global Fund grant itself is in the panel (on_art_count 2024-2025).

PAHO news item of 28 February 2019 (read as HTML, ven_paho_20190228.html). The PAHO news item mentions 37 pharmacies in 24 states and 9 million tablets of the DLT triple combination (dolutegravir, lamivudine and tenofovir) received in January and February 2019, with no count by state. NEGATIVE.

CGR (Contraloría General de la República, the national comptroller). The report pages /informes/gestion/026 and /informes/actuacion/027 list the annual management reports (Informe de Gestión) from 2014 to 2025, and the audit books for 2016 and 2017 by sector and by state. The page text lists MPPS audit items, such as the verification of a handover record on 17 March 2014, and never mentions VIH or SIDA. NEGATIVE (content of the CGR PDFs NOT VERIFIED).

IVSS. The IVSS home page shows news from March 2021 and online services for employers and insured people, with no statistics section. NEGATIVE.

Additive test.
- National new diagnoses. PAHO indicator 93 covers 2014-2020. National counts from the MPPS morbidity yearbooks 2000-2013, if HIV is a notified disease in the morbidity yearbooks, would be ADDITIVE for 2000-2013. NOT VERIFIED.
- State new diagnoses. ADDITIVE for any year, because the panel holds no VEN admin1 rows. Depends on the morbidity yearbooks or the 2002-2014 weekly bulletins giving HIV by state. NOT VERIFIED.
- Deaths. The MPPS mortality yearbooks 1995-2017 would duplicate the WHO MDB for 1996-2016 at national level and add 1995 and 2017. HIV deaths by state would be ADDITIVE at admin1. NOT VERIFIED whether the mortality yearbooks list HIV by state.
- People on ART and tests. National series are DUPLICATE of who_gho, aidsinfo, who_tme and Global Fund. ART by state would be ADDITIVE, with the Memoria y Cuenta 2002-2008 and the ACCSI reports as the only candidates found. NOT VERIFIED.
- Spending. GAM domestic spending covers 2016-2019. A PNSIDA line in the ONAPRE budget files (2000-2016), the Exposición de Motivos (2000-2011) or the Memoria y Cuenta (2002-2008) would be ADDITIVE as an allocation series for the years before 2016, never as domestic_hiv_spend. NOT VERIFIED.

Grades. MPPS yearbooks and bulletins, live, GRADE 2. MPPS, msds and INE files on Wayback, GRADE 2 by route. ONAPRE budget files, Wayback only, GRADE 2 by route. INE vital statistics xls, close to GRADE 1 (structured, one file per year, Wayback only). ACCSI reports, GRADE 2, secondary.

Summary for Venezuela. Two candidate series beyond PAHO indicator 93 and the MDB. (1) The MPPS morbidity yearbooks 2000-2013 for HIV cases before 2014 and by state (NOT VERIFIED). (2) The MPPS mortality yearbooks 1995-2017 for HIV deaths by state (NOT VERIFIED). A weaker candidate is a PNSIDA budget line in the ONAPRE files or the Memoria y Cuenta (NOT VERIFIED). Download candidates for round two, every download needing Jason's permission. (1) Anuario-de-Morbilidad-2013.pdf, live on mpps.gob.ve, 3,763,740. (2) 33-Anuario2017.pdf, live on mpps.gob.ve, 3,061,890. (3) EPI-14 form, live, 77,147, to see whether HIV is a notifiable event. (4) Boletin-Epidemiologico-SEM-37.pdf, live, 722,477. (5) Memoria_2008_MinisterioSalud.zip, Wayback copy of msds.gov.ve, 1,342,180 from CDX. (6) ONAPRE 2014 health ministry Título II Capítulo II, Wayback copy, stated 1.41 MB, 1,061,859 from CDX. (7) ONAPRE 2014 health ministry distribution, Wayback copy, stated 1.66 MB, 1,405,228 from CDX. (8) Exposicion_de_Motivos_2011.pdf, Wayback copy, 1,820,146 from CDX. (9) The ACCSI-RVG-COVIP report on 2019, Wayback copy, 1,376,211 from CDX. Round two should check the Gaceta Oficial, look again for ONAPRE files for 2012 and 2013, and confirm code 54 for 2010.

## CLASS SWEEP. Global Fund funding-request documents, LAC entries (6 October 2026)

Route. The Global Fund data API (fetch.theglobalfund.org/v4.2/odata, an open OData service with 22 entity sets and no login) lists application documents in the Documents entity set and funding requests from the 2017-2019 allocation period onward in the FundingRequests entity set. A funding request is the application a country sends to the Global Fund for a three-year allocation period. A concept note is the earlier application form, dated 2013-2016 in the LAC entries. A proposal is the application form of the numbered funding rounds (Rounds 1 to 10). Document URLs point to zip packages on docs.theglobalfund.org with spaces in the path, so the HEAD script gf_head.py encodes the path first. Package sizes come from HEAD requests. No package was opened.

Scratch files. gf_docs_all.json (the Documents records), gf_docs_rows.json (2,283 application-document rows with country, document type, component, title and URL), gf_fundingrequests.json (615 FundingRequests records), gf_head.json and gf_head.log (HEADs of the 109 funding-request and concept-note packages labelled HIV, TB/HIV or Multicomponent, 98 national and 11 multi-country, all status 200), gf_head_noarea.json (HEADs of the 28 LAC documents with no activity area, all status 200), gf_head_sur2024.txt, gf_fin_indicators_list.json, gf_eligibility_top3.json, gf_cdx_docs.txt, gf_grants_all.json (1,589 Grants records), gf_geographies.json (300 Geographies records), lac_domestic_years.txt (panel domestic spend years) and gf_lac_table.txt (the per-country block below).

Counts.
- The Documents records hold 311 documents for the 23 LAC countries. By type, Funding Request 132, Proposal 119, Concept Note 33, Full Covid Funding Request 17, Additional Covid Funding Request nine, Fast-track Covid Funding Request one.
- By country, ARG three, BLZ seven, BOL 25, BRA two, COL 11, CRI eight, CUB 15, DOM 17, ECU 14, GTM 27, GUY 18, HND 24, HTI 18, JAM eight, MEX one, NIC 25, PAN five, PER 19, PRY 19, SLV 21, SUR 15, VEN nine, TTO none.
- The 28 documents with no activity area are the 27 Covid requests and the 2024 Suriname HIV request (SUR-H_FundingRequest_1_en.zip, 6,429,764 bytes, Last-Modified 6 November 2024, gf_head_sur2024.txt).
- The FundingRequests records hold 87 requests for 19 LAC countries across all diseases. 53 of the 87 requests carry an HIV component, with the request code ending in H (HIV), C (HIV and TB) or Z (HIV, TB, malaria and RSSH, resilient and sustainable systems for health).

NEGATIVE for ARG, BRA, MEX and TTO. The FundingRequests records hold no request for Argentina, Brazil, Mexico or Trinidad and Tobago. Argentina has Round 1 HIV proposals in English and Spanish and a Round 10 HIV proposal. Brazil has a Round 5 TB proposal and a Round 8 malaria proposal. Mexico has a Round 9 HIV proposal. Trinidad and Tobago has no document.

Per-country requests and packages. Request codes, windows, allocation periods and submission dates come from the API. Package years, components, languages and sizes come from the Documents records and HEAD.
- BLZ. Requests (API). FR375-BLZ-C (HIV and TB, Window 5, 2017-2019, submitted 1 May 2018). FR992-BLZ-H (HIV, Window 5, 2020-2022, submitted 30 April 2021). FR1664-BLZ-H (HIV, Window 5, 2023-2025, submitted 29 April 2024).
  Packages (HEAD, bytes). 2015 concept note TB/HIV English 1,514,759. 2018 request TB/HIV English 2,202,846. 2021 request HIV English 3,891,159. 2024 request HIV English 6,726,335.
- BOL. Requests (API). FR15-BOL-H (HIV, Window 4, 2017-2019, submitted 7 February 2018). FR1213-BOL-C (HIV and TB, Window 7, 2020-2022, submitted 18 February 2022). FR1679-BOL-C (HIV and TB, Window 7, 2023-2025, submitted 17 February 2025).
  Packages (HEAD, bytes). 2016 concept note HIV English 2,834,272. 2018 request HIV English 3,127,668. 2022 request TB/HIV English 9,534,817. 2022 request TB/HIV Español 10,920,401. 2025 request TB/HIV English 10,955,671. 2025 request TB/HIV Español 10,905,252.
- COL. Requests (API). FR32-COL-H (HIV, Window 6, 2017-2019, submitted 7 August 2018). FR1029-COL-H (HIV, Window 7, 2020-2022, submitted 18 February 2022). FR1693-COL-H (HIV, Window 7, 2023-2025, submitted 17 February 2025).
  Packages (HEAD, bytes). 2015 concept note HIV English 2,945,163. 2018 request HIV English 4,821,126. 2022 request HIV English 5,014,504. 2022 request HIV Español 5,039,447. 2025 request HIV Español 8,868,711.
- CRI. Requests (API). FR319-CRI-H (HIV, Window 3, 2017-2019, submitted 28 August 2017). FR955-CRI-H (HIV, Window 3, 2020-2022, submitted 30 August 2020). FR1591-CRI-H (HIV, Window 4, 2023-2025, submitted 5 February 2024).
  Packages (HEAD, bytes). 2015 concept note HIV English 1,245. 2017 request HIV English 2,551,268. 2020 request HIV English 1,513,137. 2020 request HIV Español 4,486,467. 2024 request HIV English 2,681,741. 2024 request HIV Español 2,606,419.
- CUB. Requests (API). FR100-CUB-H (HIV, Window 1, 2017-2019, submitted 21 March 2017). FR639-CUB-H (HIV, Window 1, 2020-2022, submitted 23 March 2020). FR1445-CUB-H (HIV, Window 2, 2023-2025, submitted 30 May 2023).
  Packages (HEAD, bytes). 2014 concept note HIV English 2,071,051. 2017 request HIV English 1,240,341. 2020 request HIV English 5,342,300. 2020 request HIV Español 6,215,866. 2020 request HIV English 4,671,352. 2020 request HIV Español 4,609,545. 2023 request HIV English 7,068,374. 2023 request HIV Español 5,774,856.
- DOM. Requests (API). FR39-DOM-H (HIV, Window 4, 2017-2019, submitted 7 February 2018). FR990-DOM-H (HIV, Window 5, 2020-2022, submitted 30 April 2021). FR1659-DOM-H (HIV, Window 5, 2023-2025, submitted 29 April 2024).
  Packages (HEAD, bytes). 2015 concept note HIV English 2,386,651. 2018 request HIV English 2,123,751. 2021 request HIV English 6,399,273. 2021 request HIV Español 6,393,748. 2024 request HIV English 9,632,336. 2024 request HIV Español 10,769,280.
- ECU. Requests (API). FR40-ECU-H (HIV, Window 5, 2017-2019, submitted 1 May 2018). FR1212-ECU-H (HIV, Window 7, 2020-2022, submitted 18 February 2022). FR1694-ECU-H (HIV, Window 7, 2023-2025, submitted 17 February 2025).
  Packages (HEAD, bytes). 2016 concept note HIV English 2,032,283. 2018 request HIV English 1,785,143. 2022 request HIV English 2,359,059. 2022 request HIV Español 2,416,648. 2025 request HIV English 7,801,354. 2025 request HIV Español 7,762,392.
- SLV. Requests (API). FR325-SLV-H (HIV, Window 5, 2017-2019, submitted 1 May 2018). FR979-SLV-H (HIV, Window 4, 2020-2022, submitted 8 February 2021). FR1732-SLV-H (HIV, Window 5, 2023-2025, submitted 29 April 2024).
  Packages (HEAD, bytes). 2013 concept note HIV English 670,175. 2018 request HIV English 4,230,921. 2021 request HIV English 1,751,115. 2021 request HIV Español 1,768,334. 2024 request HIV English 7,057,502. 2024 request HIV Español 8,312,059.
- GTM. Requests (API). FR100-GTM-H-01 (HIV, Window 4, 2017-2019, submitted 7 February 2018). FR645-GTM-H (HIV, Window 2b, 2020-2022, submitted 31 May 2020). FR1424-GTM-H (HIV, Window 1, 2023-2025, submitted 30 March 2023).
  Packages (HEAD, bytes). 2018 request HIV English 3,511,283. 2020 request HIV English 6,581,650. 2020 request HIV Español 6,625,526. 2022 request HIV English 5,852,055. 2023 request HIV English 7,022,322. 2023 request HIV Español 6,899,350.
- GUY. Requests (API). FR55-GUY-H (HIV, Window 1, 2017-2019, submitted 20 March 2017). FR1028-GUY-C (HIV and TB, Window 4, 2020-2022, submitted 8 February 2021). FR1699-GUY-C (HIV and TB, Window 5, 2023-2025, submitted 29 April 2024).
  Packages (HEAD, bytes). 2017 request HIV English 924,894. 2021 request TB/HIV English 4,229,897. 2024 request TB/HIV English 7,662,283.
- HTI. Requests (API). FR278-HTI-C (HIV and TB, Window 1, 2017-2019, submitted 19 March 2017). FR681-HTI-Z (HIV, TB, malaria and RSSH, Window 1, 2020-2022, submitted 23 March 2020). FR1457-HTI-Z (HIV, TB, malaria and RSSH, Window 2, 2023-2025, submitted 30 May 2023).
  Packages (HEAD, bytes). 2015 concept note TB/HIV English 3,319,844. 2017 request TB/HIV English 1,700,269. 2020 request Multicomponent English 18,697,295. 2020 request Multicomponent Français 15,622,205. 2023 request Multicomponent English 13,075,499. 2023 request Multicomponent Français 14,258,625.
- HND. Requests (API). FR61-HND-H (HIV, Window 6, 2017-2019, submitted 7 August 2018). FR1010-HND-C-01 (HIV and TB, Window 7, 2020-2022, submitted 18 February 2022). FR1670-HND-C (HIV and TB, Window 7, 2023-2025, submitted 17 February 2025).
  Packages (HEAD, bytes). 2015 concept note HIV English 4,953,724. 2019 request HIV English 5,946,667. 2022 request TB/HIV English 25,252,952. 2022 request TB/HIV Español 27,845,734. 2025 request TB/HIV English 8,461,525. 2025 request TB/HIV Español 8,566,418.
- JAM. Requests (API). FR66-JAM-H (HIV, Window 4, 2017-2019, submitted 9 February 2018). FR1000-JAM-H (HIV, Window 5, 2020-2022, submitted 30 April 2021). FR1636-JAM-H (HIV, Window 5, 2023-2025, submitted 29 April 2024).
  Packages (HEAD, bytes). 2015 concept note HIV English 1,270,915. 2018 request HIV English 1,630,884. 2021 request HIV English 3,310,163. 2024 request HIV English 16,219,391.
- NIC. Requests (API). FR82-NIC-H (HIV, Window 1, 2017-2019, submitted 21 March 2017). FR1002-NIC-C (HIV and TB, Window 4, 2020-2022, submitted 8 February 2021). FR1663-NIC-C (HIV and TB, Window 5, 2023-2025, submitted 29 April 2024).
  Packages (HEAD, bytes). 2014 concept note HIV English 2,501,421. 2017 request HIV English 2,669,706. 2021 request TB/HIV English 5,459,693. 2021 request TB/HIV Español 6,062,110. 2024 request TB/HIV English 15,734,481. 2024 request TB/HIV Español 18,926,008.
- PAN. Requests (API). FR376-PAN-C (HIV and TB, Window 5, 2017-2019, submitted 30 April 2018).
  Packages (HEAD, bytes). 2015 concept note TB/HIV English 3,021,704. 2018 request TB/HIV English 2,041,711.
- PRY. Requests (API). FR89-PRY-H (HIV, Window 1, 2017-2019, submitted 20 March 2017). FR829-PRY-H (HIV, Window 2c, 2020-2022, submitted 30 June 2020). FR1507-PRY-H (HIV, Window 2, 2023-2025, submitted 30 May 2023).
  Packages (HEAD, bytes). 2014 concept note HIV English 2,365,266. 2017 request HIV English 1,728,698. 2020 request HIV English 2,457,168. 2020 request HIV Español 4,269,102. 2023 request HIV English 5,116,172. 2023 request HIV Español 5,032,696.
- PER. Requests (API). FR90-PER-H (HIV, Window 6, 2017-2019, submitted 27 July 2018). FR1044-PER-C (HIV and TB, Window 6, 2020-2022, submitted 10 September 2021). FR1657-PER-C (HIV and TB, Window 7, 2023-2025, submitted 17 February 2025).
  Packages (HEAD, bytes). 2015 concept note HIV English 2,979,164. 2018 request HIV English 2,154,153. 2021 request TB/HIV English 6,657,633. 2021 request TB/HIV Español 6,691,917. 2025 request TB/HIV English 18,822,905. 2025 request TB/HIV Español 21,000,405.
- SUR. Requests (API). FR415-SUR-C (HIV and TB, Window 4, 2017-2019, submitted 8 February 2018). FR1025-SUR-H (HIV, Window 4, 2020-2022, submitted 8 February 2021). FR1688-SUR-H (HIV, Window 6, 2023-2025, submitted 9 September 2024).
  Packages (HEAD, bytes). 2015 concept note TB/HIV English 2,853,710. 2017 request TB/HIV English 1,261,308. 2021 request HIV English 5,449,477. 2024 request HIV English 6,429,764.
- VEN. Requests (API). FR1409-VEN-C (HIV and TB, Window 1, 2023-2025, submitted 30 March 2023).
  Packages (HEAD, bytes). 2022 request TB/HIV English 5,645,111. 2023 request TB/HIV English 7,221,069. 2023 request TB/HIV Español 7,599,528.

Package notes.
- The CRI 2015 concept note (CRI-H_ConceptNote_0_en.zip) answers at 1,245 bytes, so the CRI 2015 concept-note package is probably empty or broken.
- CUB holds two sets of 2020 packages. CUB-H_FundingRequest_0 has no window in the title (English 5,342,300, Spanish 6,215,866, Last-Modified August 2021). CUB-H_FundingRequest_1 is labelled Window 1 (English 4,671,352, Spanish 4,609,545, Last-Modified September 2023). Which set matches FR639-CUB-H is NOT VERIFIED.
- The GTM 2022 package (GTM-H_FundingRequest_1_en.zip) and the VEN 2022 package (VEN-C_FundingRequest_1_en.zip) carry no window in the title and match no FundingRequests record.
- PAN has a single request, FR376-PAN-C for 2017-2019. No PAN request appears for 2020-2022 or 2023-2025.

Multi-country entries. The 11 multi-country packages belong to LAC regional applicants.
- MCC (the Global Fund label for a Caribbean multi-country TB/HIV applicant). Requests FR414-MCC-C (2017-2019, submitted 30 April 2018), FR999-MCC-C (2020-2022, submitted 10 September 2021) and FR1700-MCC-C (2023-2025, submitted 9 September 2024). Packages 2015 concept note TB/HIV 2,179,749, 2018 request 1,207,323, 2021 request 10,354,629. The Documents records list no package for FR1700-MCC-C.
- CARICOM/PANCAP (the Pan Caribbean Partnership against HIV and AIDS of the Caribbean Community). Requests FR1257-MCCARICOM/PANCAP-H (2020-2022, submitted 20 April 2022, a continuation reviewed by the Grant Approvals Committee) and FR1756-MCCARICOMPANCAP-H (2023-2025, submitted 17 February 2025). Packages 2016 concept note 2,534,556 and 2025 request 9,386,711.
- REDCA (the Central American network of people living with HIV). Packages 2014 concept note 1,490,705, 2015 concept note 2,013,985 and 2017 request 1,268,740.
- REDLACTRANS (the Latin American and Caribbean network of trans people). 2015 concept note 1,947,937.
- ICW (the International Community of Women Living with HIV). 2015 concept note 2,048,552.
- CVC/COIN (the Caribbean Vulnerable Communities Coalition with COIN, a Dominican civil-society organisation). 2016 concept note 2,559,914.
- MCALEP (Global Fund label Multicountry HIV Latin America ALEP) and MCHIVLA (Multicountry HIV Latin America). Requests FR1258-MCALEP-H (2020-2022, submitted 20 April 2022) and FR1750-MCHIVLATINAMERICA-H (2023-2025, submitted 17 February 2025). The Documents records list no funding-request package for FR1258-MCALEP-H or FR1750-MCHIVLATINAMERICA-H, and list a 2021 Full Covid Funding Request for MCALEP.
- Older regional applicants with round proposals only. MCOECS (Organisation of Eastern Caribbean States) Round 3, MCCRN (CRN+, the Caribbean regional network of people living with HIV) Round 4, MCCOPRECOS (COPRECOS, the Latin American and Caribbean committee of the armed and police forces on HIV) Round 9, MCREDTRASEX (REDTRASEX, the Latin American and Caribbean network of women sex workers) Round 10. The Geographies records also list MCLACPCC (Multicountry HIV Caribbean PCC Consortium), MCIOM, MCEMMIE (malaria) and MCORAS-CONHU (TB).
- The regional packages are expected to hold regional grant budgets, not national domestic spending (NOT VERIFIED). Low priority.

API negatives.
- FinancialIndicatorsList holds 32 indicators (gf_fin_indicators_list.json). The 32 indicators cover C19RM (the COVID-19 Response Mechanism) awards, commitments, communicated allocations, disbursements, expenditure by module and intervention, expenditure by investment landscape, grant budgets, implementation-period totals, operating expenses, and donor pledges and contributions. All 32 indicators measure Global Fund money. No indicator records domestic co-financing. NEGATIVE for domestic_hiv_spend through the API.
- Eligibility records income level, disease burden, eligibility, eligibility year, funding stream and policy reference by geography and disease component (gf_eligibility_top3.json). Not a panel indicator. NEGATIVE.

Wayback. The CDX domain query on docs.theglobalfund.org returned 461 rows (gf_cdx_docs.txt), mostly results-profile PDFs and GF_PD programme-document zips, and none of the 461 rows sits under /files/Applications. The prefix query on /files/Applications (gf_cdx_apps.txt) and the landscape filter queries on docs.theglobalfund.org and www.theglobalfund.org returned zero rows. NEGATIVE as a route. The live packages answer HEAD, so Wayback copies are not needed.

Expected content and classification rule.
- The funding landscape table (a Global Fund spreadsheet annex listing domestic and external funding for the disease programme by year, past and planned) is expected in the packages from 2017 onward. The MCP-ES uploads under El Salvador show a separate landscape xlsx for the 2024 SLV HIV request, known from file names only. Whether the zip packages hold the landscape table, which years the landscape table covers, and whether the template keeps one layout across countries are NOT VERIFIED.
- Government lines for past years may copy GAM or NASA figures. A past-year government line counts as DUPLICATE or as a cross-check unless the landscape table names a source other than GAM or NASA.
- Government lines for future years are commitments, not spending, and never enter domestic_hiv_spend. A year counts as ADDITIVE only where the landscape table reports executed spending.
- Global Fund and other donor lines DUPLICATE the donor connectors.

Additive test against panel domestic_hiv_spend. All LAC panel rows for domestic_hiv_spend come from unaids_gam_expenditure at national level (lac_domestic_years.txt, read 6 October 2026). The years covered by any landscape table are NOT VERIFIED, so every ADDITIVE line below is conditional.
- BOL, CUB, GUY, NIC and SUR hold no panel domestic spend. Any past-year government spending line would be ADDITIVE. The strongest case in the class.
- BLZ panel 2021-2023. ADDITIVE for years before 2021 and possibly for 2024.
- COL panel 2022 only. ADDITIVE for every year other than 2022.
- CRI panel 2014, 2018-2020 and 2022-2024. ADDITIVE for 2015-2017 and 2021.
- DOM panel 2013-2024 with no gap. DUPLICATE or cross-check.
- ECU panel 2017-2022. ADDITIVE for years before 2017 and for 2023-2024.
- SLV panel 2015 and 2017-2024. ADDITIVE for 2016 and for years before 2015.
- GTM panel 2011-2013, 2016-2021 and 2023-2024. ADDITIVE for 2014, 2015 and 2022.
- HTI panel 2014-2016. ADDITIVE for years before 2014 and from 2017.
- HND panel 2020-2024. ADDITIVE for years before 2020.
- JAM panel 2013-2014. ADDITIVE from 2015 and for years before 2013.
- PAN panel 2018 and 2020-2024. ADDITIVE for years before 2018. The 2019 gap falls after the last PAN request of 2018, so no PAN package is likely to fill 2019.
- PRY panel 2018-2020 and 2022. ADDITIVE for 2021, for 2023 onward and for years before 2018.
- PER panel 2020 and 2022-2024. ADDITIVE for 2021 and for years before 2020.
- VEN panel 2016-2019. ADDITIVE for 2020-2022 from the 2022 and 2023 packages.
- ARG, BRA, MEX and TTO. NEGATIVE for the class, with no funding request and no concept note.
- Concept notes from 2013-2016 and round proposals may hold counterpart financing tables for older years (NOT VERIFIED, lower priority).

Grade. GRADE 2 (open born-digital report). Structured xlsx annexes are expected inside open zip packages, listed by an open API, with no login. Close to GRADE 1 if the landscape template keeps one layout across countries and years (NOT VERIFIED).

Download candidates, every download needing Jason's permission.
- 20240508_fundingrequest_fundinglandscape_table_aa_VIH_GF_4.30pm.xlsx, mcpelsalvador.org.sv (uploads 2024/06), 1,654,228 bytes. Would settle the template layout and the years covered.
- SLV-H_FundingRequest_1_en.zip, the English package of the 2021 SLV request, docs.theglobalfund.org, 1,751,115 bytes. Would confirm whether a package holds the landscape table. The SLV package is the second-smallest national HIV package from 2020 onward, after CRI-H_FundingRequest 2020 English at 1,513,137 bytes, and is preferred because the MCP-ES landscape xlsx covers the same country.
- A package for a country with no panel domestic spend could follow, for example GUY-C_FundingRequest_1_en.zip (2021 request, TB/HIV) at 4,229,897 bytes.

## CLASS SWEEP. Brazil federal budget lines for HIV (6 October 2026)

Routes. Two open federal routes, read as page JSON and SPARQL JSON, with no file downloaded.
- Portal da Transparência is the federal transparency portal run by CGU (Controladoria-Geral da União, the federal comptroller). The page for budget action 4370 (portaldatransparencia.gov.br/programas-e-acoes/acao/4370) loads page JSON from endpoints listed in /static/js/despesas/painelAcaoEspecifica.js (bra_pt_painelAcao.js). Files read on 6 October 2026 were the action page (bra_pt_4370.html), yearly payments for 2014-2026 (bra_pt_4370_evol.json), the 2024 execution stages (bra_pt_4370_execucao-despesas-ano-corrente_2024.json) and the restos a pagar files for 2024 and 2022. Restos a pagar are commitments from an earlier budget year, paid or cancelled in a later year.
- After about six requests, CloudFront answered HTTP 202 with an empty body and the header x-amzn-waf-action set to challenge, which is an AWS WAF bot challenge. Requests to the portal stopped, with no bypass and no switch to a browser. The requests for the 2022 execution stages and for the 2024 split by state returned empty files (bra_pt_4370_execucao-despesas-ano-corrente_2022.json, bra_pt_4370_regional_2024.json).
- orcamento.dados.gov.br/sparql/ is the federal budget linked-data endpoint (OpenLink Virtuoso 06.01.3127). The endpoint needs no login, and no challenge appeared in any query sent on 6 October 2026. The endpoint holds 27 named graphs for budget years, a graph for every year from 2000 to 2026 (bra_sparql_graphs.json). The endpoint also holds the vocabulary graph http://vocab.e.gov.br/2013/09/loa# and a graph named http://www.siop.planejamento.gov.br/sioplegis/, which was not explored.
- Every budget line (class ItemDespesa) carries the action, programme, budget unit, sub-plan (plano orçamentário), locality subtitle (subtítulo), function, sub-function, expenditure group, application modality and funding source, with six values. The six values are the bill (valorProjetoLei), the initial allocation in the budget law (valorDotacaoInicial), the allocation after supplementary credits (valorLeiMaisCredito), the committed amount (valorEmpenhado), the liquidated amount (valorLiquidado, meaning goods or services delivered and verified) and the paid amount (valorPago).
- Queries go as GET with query and format=application/sparql-results+json. Virtuoso 6 rejects GROUP_CONCAT and VALUES. A query across every graph with a text filter on sub-plan titles returned an empty result, probably a timeout, so the sub-plan search ran a year at a time.
- Last-update dates (loa:dataUltimaAtualizacao on the Exercicio record of every graph, bra_sparql_updated.json) are 2014-09-01 for the graphs for 2000-2009, 2014-08-29 for 2010-2013, 2015-10-23 for 2014, 2016-03-30 for 2015, 2021-03-23 for 2016, 2021-03-24 for 2017, 2023-03-18 for 2018, 2023-04-29 for 2019, 2023-05-03 for 2020, 2023-05-04 for 2021, 2023-05-04 for 2022, 2024-08-27 for 2023, 2025-02-11 for 2024, 2026-01-24 for 2025, 2026-10-03 for 2026.

Check of the SPARQL endpoint against the portal for action 4370.
- SPARQL paid values equal the portal yearly payments to the nearest real in every year from 2014 to 2024 (11 years). The portal gives centavos and the SPARQL sums give whole reais. For 2014-2018 the portal file also lists the older action title with R$ 0,00.
- CONFLICT for 2025. SPARQL paid R$ 2,443,674,819 (graph updated 2026-01-24). Portal paid R$ 2,125,216,692.32. The difference is R$ 318,458,127. Cause NOT RESOLVED. Round two.
- 2026 is a partial year. SPARQL paid R$ 1,917,808,035 (graph updated 2026-10-03). Portal paid R$ 1,909,025,165.07 (read 6 October 2026).
- The portal gives 2024 stages of R$ 2,673,499,980.25 committed, R$ 2,382,237,973.86 liquidated and R$ 2,378,817,533.69 paid, with R$ 2,673,500,000.00 in the third column, read as the updated allocation (NOT VERIFIED). SPARQL gives R$ 2,382,257,371 liquidated for 2024, so the liquidated amounts differ by R$ 19,398. The paid amounts match.
- Restos a pagar under action 4370 on the portal. The 2024 file gives R$ 195,870,286.67 paid and R$ 774,632.51 cancelled, with R$ 209,978,281.86 in the third column. The 2022 file gives R$ 222,976,096.24 paid and R$ 4,211,224.03 cancelled, with R$ 706,418,213.64 in the third column. The third column is read as the total carried into the year (NOT VERIFIED).

Action 4370, titles by year (bra_sparql_4370_acao.json). The scope widens over time, and action 4370 is never an HIV-only line.
- 2000-2001. "Produção, Aquisição e Distribuição de Medicamentos para Tratamento dos Portadores da Síndrome da Imunodeficiência Adquirida - Aids e das Doenças Sexualmente Transmissíveis - Dst"
- 2002-2003. "Atendimento à População com Medicamentos para Tratamento dos Portadores da Síndrome da Imunodeficiência Adquirida - AIDS e das Doenças Sexualmente Transmissíveis - DST"
- 2004-2019. "Atendimento à População com Medicamentos para Tratamento dos Portadores de HIV/AIDS e outras Doenças Sexualmente Transmissíveis"
- 2020-2021. "Atendimento à População com Medicamentos para Tratamento dos Portadores de HIV/AIDS, outras Infecções Sexualmente Transmissíveis e Hepatites Virais"
- 2022-2023. "Atendimento à População para Prevenção, Controle e Tratamento de HIV/AIDS, outras Infecções Sexualmente Transmissíveis e Hepatites Virais"
- 2024-2026. "Atendimento à População para Prevenção, Controle e Tratamento do Vírus da Imunodeficiência Humana e Síndrome da Imunodeficiência Adquirida (HIV/AIDS) e outras infecções sexualmente transmissíveis (IST) e Hepatites Virais"
- Up to 2019 the action covers medicines for AIDS or HIV/AIDS and other sexually transmitted diseases. The 2020-2021 title adds viral hepatitis. From 2022 the action covers prevention, control and treatment of HIV/AIDS, other sexually transmitted infections and viral hepatitis.

Action 4370 by year, nominal reais, whole reais as summed by SPARQL (bra_sparql_4370_yearly.json). Initial means valorDotacaoInicial. Authorised means valorLeiMaisCredito. 2026 is partial.

| Year | Lines | Initial | Authorised | Committed | Liquidated | Paid |
|---|---|---|---|---|---|---|
| 2000 | 103 | 423,100,000 | 557,040,000 | 556,404,995 | 556,404,995 | 472,325,543 |
| 2001 | 140 | 515,500,000 | 515,500,000 | 515,500,000 | 515,500,000 | 496,712,540 |
| 2002 | 140 | 516,000,000 | 615,000,000 | 611,869,976 | 611,869,976 | 481,798,534 |
| 2003 | 100 | 516,000,000 | 551,000,000 | 550,999,998 | 550,999,998 | 502,090,559 |
| 2004 | 104 | 516,000,000 | 567,600,000 | 563,950,492 | 563,950,492 | 484,691,024 |
| 2005 | 102 | 550,000,000 | 550,000,000 | 549,750,540 | 549,750,540 | 516,894,592 |
| 2006 | 168 | 960,000,000 | 960,000,000 | 959,915,531 | 959,915,531 | 733,970,712 |
| 2007 | 96 | 984,000,000 | 710,170,228 | 708,178,407 | 708,178,407 | 441,239,833 |
| 2008 | 98 | 1,013,300,000 | 782,270,000 | 604,892,620 | 604,892,620 | 373,083,991 |
| 2009 | 84 | 1,084,100,000 | 758,900,000 | 739,185,905 | 739,185,905 | 490,993,006 |
| 2010 | 47 | 784,100,000 | 608,100,000 | 605,788,366 | 605,788,366 | 545,439,431 |
| 2011 | 69 | 846,820,000 | 804,802,000 | 804,802,000 | 804,802,000 | 643,479,530 |
| 2012 | 66 | 788,400,000 | 823,600,000 | 820,430,588 | 820,430,588 | 581,942,512 |
| 2013 | 43 | 770,200,000 | 770,200,000 | 770,200,000 | 770,200,000 | 577,447,941 |
| 2014 | 93 | 780,250,000 | 864,187,200 | 863,694,200 | 863,694,200 | 649,643,328 |
| 2015 | 85 | 980,000,000 | 1,101,000,000 | 1,097,454,246 | 860,038,195 | 835,937,608 |
| 2016 | 45 | 1,100,000,000 | 1,100,000,000 | 1,099,686,607 | 916,093,393 | 884,219,101 |
| 2017 | 106 | 1,300,000,000 | 1,130,000,000 | 1,129,999,238 | 793,088,509 | 783,922,735 |
| 2018 | 81 | 1,169,000,000 | 1,260,800,000 | 1,260,799,999 | 1,076,924,392 | 1,068,676,071 |
| 2019 | 59 | 1,653,200,000 | 1,843,590,000 | 1,843,589,812 | 1,657,969,053 | 1,645,235,021 |
| 2020 | 63 | 1,880,532,167 | 2,076,837,039 | 2,076,837,028 | 1,840,424,987 | 1,839,886,831 |
| 2021 | 66 | 1,830,000,000 | 1,880,000,000 | 1,879,999,990 | 1,651,928,396 | 1,651,233,046 |
| 2022 | 119 | 2,224,663,100 | 2,224,663,100 | 2,224,663,095 | 1,561,347,517 | 1,560,654,989 |
| 2023 | 82 | 1,928,100,000 | 1,944,100,000 | 1,944,092,323 | 1,782,805,360 | 1,781,162,340 |
| 2024 | 116 | 2,673,500,000 | 2,673,500,000 | 2,673,499,980 | 2,382,257,371 | 2,378,817,534 |
| 2025 | 155 | 2,701,000,000 | 2,737,690,000 | 2,737,689,902 | 2,502,701,129 | 2,443,674,819 |
| 2026 | 152 | 2,705,000,000 | 2,826,395,000 | 2,372,151,438 | 1,929,079,406 | 1,917,808,035 |

- Paid falls more than 10 per cent below liquidated in 2000, 2002, 2004, 2006-2009, 2011-2014 (2026 not counted, as a partial year). For example, 2008 gives R$ 373,083,991 paid against R$ 604,892,620 liquidated. The unpaid part of the liquidated amount is paid in later years as restos a pagar and does not return to the paid value of the original year. Liquidated in the year is the closer measure of goods delivered in the year. Which stage enters any panel row is a decision for Jason and Adrian.
- The 2013 graph gives R$ 0 as the bill value (valorProjetoLei) for action 4370.

Action 4370 sub-plans (bra_sparql_4370_po_yearly.json).
- 2000-2012 carry the sub-plan code @ with the title "Valor Não Detalhado" (value not detailed). 2013 carries the code 0000 with the title "Valor não detalhado". 2014-2021 carry the code 0000 under the action title.
- 2017 adds a sub-plan EREL (Emenda de Relator, an amendment by the budget rapporteur in Congress) paying R$ 75,902,954.
- 2022 paid by sub-plan. 0001 medicines R$ 1,321,510,731, 0002 supplies (older title) R$ 219,144,258, 0003 logistics R$ 20,000,000.
- 2023 paid by sub-plan. 0001 medicines R$ 1,761,162,340, 0003 logistics R$ 20,000,000.
- 2024 paid by sub-plan. 0001 medicines R$ 2,192,895,060, 0002 supplies (newer title) R$ 105,158,239, 0002 supplies (older title) R$ 58,218,586, 0003 logistics R$ 22,545,649.
- 2025 paid by sub-plan. 0001 medicines R$ 2,122,697,051, 0002 supplies (newer title) R$ 268,524,416, 0002 supplies (older title) R$ 2,453,351, 0003 logistics R$ 50,000,000.
- 2026 paid by sub-plan. 0001 medicines R$ 1,594,976,028, 0002 supplies (newer title) R$ 271,504,472, 0002 supplies (older title) R$ 6,487,613, 0003 logistics R$ 44,839,923.
- Sub-plan 0001 is "Disponibilização de medicamentos para tratamento dos portadores de Vírus da Imunodeficiência Humana e Síndrome da Imunodeficiência Adquirida (HIV/AIDS) e outras infecções sexualmente transmissíveis (IST) e Hepatites Virais" in 2024. Sub-plan 0003 is "Logística para distribuição de medicamentos e insumos para tratamento de Imunodeficiência Humana e Síndrome da Imunodeficiência Adquirida (HIV/AIDS), e outras infecções sexualmente transmissíveis (IST) e Hepatites Virais" in 2024.
- The older supplies title is "Disponibilização de Insumos para Prevenção e Controle de Doenças para Hiv/Aids, Sífilis e Hepatites Virais" and sits under budget unit 36201 in 2024. The newer supplies title is "Disponibilização de Insumos para Prevenção e Controle do Vírus da Imunodeficiência Humana e Síndrome da Imunodeficiência Adquirida (HIV/AIDS), outras infecções sexualmente transmissíveis (IST), Sífilis e Hepatites Virais" and sits under budget unit 36901 in 2024. The budget unit comes from the first five digits of the sub-plan identifier (bra_sparql_po_2024_4370.json). The 2025 and 2026 graphs also hold the older and the newer supplies titles under the code 0002. The 2023 graph holds no sub-plan 0002 under action 4370, and the 2023 supplies for HIV/AIDS, syphilis and viral hepatitis sit in sub-plan 0004 of action 21DZ (below).
- Hepatitis medicines sit inside sub-plan 0001, so no sub-plan of action 4370 isolates HIV.

Action 4370 by place, budget unit and modality.
- Every paid real of action 4370 in 2000-2026 sits under the locality subtitle "Nacional" (bra_sparql_4370_subtitulo.json). State-named or city-named subtitles appear in some years (eight distinct names, for example "No Município de Campinas - SP" in 2014), and every state-named or city-named subtitle carries a paid value of zero. A line under "No Estado de Goiás" in 2009 liquidated R$ 100,000 and paid nothing. NEGATIVE for admin1 through action 4370. The portal split by state is not needed for action 4370.
- 2024 paid by budget unit and modality (bra_sparql_4370_split_2024.json). Unit 36201 modality 90 R$ 1,594,858,013, unit 36901 modality 90 R$ 732,779,191, unit 36901 modality 80 R$ 51,179,364, unit 36201 modality 91 R$ 966.
- 2025 paid by budget unit and modality (bra_sparql_4370_split_2025.json). Unit 36201 modality 90 R$ 1,534,531,035, unit 36901 modality 90 R$ 891,343,085, unit 36901 modality 80 R$ 17,680,238, unit 36201 modality 91 R$ 120,461.
- Labels from bra_sparql_labels_2019.json and bra_sparql_labels_2024.json. Unit 36901 is Fundo Nacional de Saúde (the National Health Fund). Unit 36201 is Fundação Oswaldo Cruz (Fiocruz, a federal public-health research foundation which also makes medicines). Modality 90 is Aplicações Diretas (direct application). Modality 80 is Transferências ao Exterior (transfers abroad). Modality 91 is "Aplicação Direta Decorrente de Operação entre Órgãos, Fundos e Entidades Integrantes dos Orçamentos F/S" (direct application between bodies inside the federal fiscal and social security budgets). What the transfers abroad buy is NOT VERIFIED.
- In 2024 every paid real of action 4370 came from funding source 1001 (Recursos Livres da Seguridade Social) or funding source 1002 (Atividades-fim da Seguridade Social). The labels of funding sources 1001 and 1002 name social security revenue.

Other federal budget lines for HIV. The search matched action titles in every graph (bra_sparql_hiv_acoes.json, terms HIV, AIDS, DST, Sexualmente and Imunodefici) and sub-plan titles a year at a time for 2013-2026 (bra_sparql_hiv_po_items_YYYY.json).
- False matches dropped. Action 0391 "Contribuição à Coleção Archives" (2000-2003) matched the letters hiv inside Archives. Sub-plan 0001 of action 4185, the "Programa de Apoio ao Desenvolvimento do Setor de Tecnologia da Informação (PADSTI)", matched the letters DST inside PADSTI.

Transfers to states and municipalities for HIV. A single line every year from 2003, paid and liquidated in nominal reais.

| Year | Budget line | Paid | Liquidated |
|---|---|---|---|
| 2003 | 0214 | 49,084,567 | 57,984,997 |
| 2004 | 0214 | 98,400,366 | 108,078,301 |
| 2005 | 0214 | 112,290,988 | 123,987,921 |
| 2006 | 0214 | 112,298,318 | 135,500,000 |
| 2007 | 0214 | 133,987,815 | 143,033,851 |
| 2008 | 20AC | 119,496,969 | 124,334,873 |
| 2009 | 20AC | 125,036,870 | 138,352,500 |
| 2010 | 20AC | 135,977,844 | 154,542,202 |
| 2011 | 20AC | 129,683,595 | 144,000,000 |
| 2012 | 20AC | 159,136,728 | 164,200,000 |
| 2013 | 20AC | 159,684,191 | 159,734,191 |
| 2014 | 20AC | 163,546,906 | 178,437,979 |
| 2015 | 20AC | 163,407,914 | 163,407,914 |
| 2016 | 20AC | 179,801,896 | 179,801,896 |
| 2017 | 20AC | 163,253,076 | 163,253,076 |
| 2018 | 20AL sub-plan 0002 | 178,031,205 | 178,031,205 |
| 2019 | 20AL sub-plan 0002 | 163,157,204 | 163,157,204 |
| 2020 | 20AL sub-plan 0002 | 163,568,122 | 163,568,122 |
| 2021 | 20AL sub-plan 0002 | 178,437,951 | 178,437,951 |
| 2022 | 20AL sub-plan 0002 | 196,624,828 | 196,624,828 |
| 2023 | 20AL sub-plan 0002 | 199,999,959 | 199,999,959 |
| 2024 | 20AL sub-plan 0002 | 299,999,919 | 299,999,919 |
| 2025 | 20AL sub-plan 0002 | 299,504,595 | 299,504,595 |
| 2026 | 20AL sub-plan 0002 | 174,999,946 | 174,999,946 |

- Values for 2003-2017 are action totals (bra_sparql_hiv_other_yearly.json). For 2014-2017 the sums by sub-plan 0000 differ from the action totals by at most R$ 2, a rounding difference in the SPARQL sums.
- Action titles for 0214 (2003-2007) and 20AC (2008-2017).
  - 2003. "Incentivo Financeiro a Municípios para Ações de Prevenção e Controle de DST e AIDS"
  - 2004. "Incentivo Financeiro a Estados e Municípios para Ações de Prevenção e Qualificação da Atenção em HIV/AIDS e outras Doenças Sexualmente Transmissíveis"
  - 2005-2013. "Incentivo Financeiro a Estados, Distrito Federal e Municípios para Ações de Prevenção e Qualificação da Atenção em HIV/AIDS e outras Doenças Sexualmente Transmissíveis"
  - 2014-2017. "Incentivo Financeiro às ações de vigilância, prevenção e controle das DST/AIDS e Hepatites Virais"
- From 2018 the transfers sit in sub-plan 0002 of action 20AL, a general health-surveillance transfer action. Action 20AL is "Incentivo Financeiro aos Estados, Distrito Federal e Municípios para a Vigilância em Saúde" in 2019 and "Apoio aos Estados, Distrito Federal e Municípios para a Vigilância em Saúde" in 2023. Sub-plan 0002 titles follow.
  - 2018. "Incentivo Financeiro às Ações de Vigilância, Prevenção e Controle das DST/AIDS e Hepatites Virais"
  - 2019-2023. "Incentivo Financeiro às ações de vigilância, prevenção e controle das IST/AIDS e Hepatites Virais"
  - 2024. "Incentivo Financeiro às ações de vigilância, prevenção e controle do Vírus da Imunodeficiência Humana e Síndrome da Imunodeficiência Adquirida (HIV/AIDS), das infecções sexualmente transmissíveis (IST) e Hepatites Virais"
  - 2025-2026. "Incentivo Financeiro às ações de vigilância, prevenção e controle do Vírus da Imunodeficiência Humana e Síndrome da Imunodeficiência Adquirida (HIV/AIDS), das infecções sexualmente transmissíveis (IST), Hepatites Virais e Tuberculose"
- Viral hepatitis enters the transfer titles in 2014. Tuberculosis enters the sub-plan 0002 title in 2025.
- Every year from 2003 to 2026 holds 28 locality subtitles, made up of 26 state subtitles ("No Estado de", "do" or "da" followed by the state), "No Distrito Federal" and "Nacional" (bra_sparql_20AC_subtitulo.json for 2003-2017, the sub-plan files for 2018-2026). Paid under "Nacional" was R$ 534,897 in 2003, R$ 31,260,235 in 2012, R$ 8,327,067 in 2017, R$ 11,751,205 in 2018 and R$ 17,217,919 in 2024.
- A state subtitle groups transfers to the state government with transfers to municipalities in the same state. Sub-plan 0002 of action 20AL in 2024 paid R$ 219,934,041 under modality 41 (Transferências a Municípios - Fundo a Fundo) and R$ 80,065,878 under modality 31 (Transferências a Estados e ao Distrito Federal - Fundo a Fundo). Action 20AC in 2012 paid R$ 107,824,452 under modality 41 and R$ 51,312,277 under modality 31. Action 0214 in 2005 paid R$ 72,347,127 under modality 40 (Transferências a Municípios) and R$ 39,943,861 under modality 30 (Transferências a Estados e ao Distrito Federal). The modality code sits on the same budget line as the subtitle, so a split by state and by recipient level looks possible (NOT VERIFIED by state).
- Examples. The São Paulo subtitle paid R$ 45,300,000 in 2018 and R$ 73,082,000 in 2024. The Acre subtitle paid R$ 660,000 in 2018 and R$ 1,125,000 in 2024.

National coordination, surveillance and supplies outside action 4370 and outside the transfers. Paid in nominal reais.

| Year | Action 8670 | Action 20QD | 20YJ sub-plan 0001 | 20YE sub-plan 0003 | 21DZ sub-plan 0004 | Smaller actions 2000-2007 |
|---|---|---|---|---|---|---|
| 2000 |  |  |  |  |  | 55,024,643 |
| 2001 |  |  |  |  |  | 61,824,693 |
| 2002 |  |  |  |  |  | 109,417,404 |
| 2003 |  |  |  |  |  | 34,325,937 |
| 2004 |  |  |  |  |  | 49,760,715 |
| 2005 |  |  |  |  |  | 66,818,523 |
| 2006 |  |  |  |  |  | 70,936,602 |
| 2007 |  |  |  |  |  | 39,003,241 |
| 2008 | 59,225,963 |  |  |  |  |  |
| 2009 | 21,510,354 |  |  |  |  |  |
| 2010 | 34,495,047 |  |  |  |  |  |
| 2011 | 76,342,704 |  |  |  |  |  |
| 2012 |  | 93,707,241 |  |  |  |  |
| 2013 |  |  | 104,645,573 |  |  |  |
| 2014 |  |  | 102,179,129 |  |  |  |
| 2015 |  |  | 132,167,762 |  |  |  |
| 2016 |  |  | 46,398,417 |  |  |  |
| 2017 |  |  | 33,393,925 |  |  |  |
| 2018 |  |  | 26,833,707 |  |  |  |
| 2019 |  |  | 32,126,188 | 109,542,019 |  |  |
| 2020 |  |  | 25,732,838 | 75,150,240 |  |  |
| 2021 |  |  | 30,126,350 | 197,451,699 |  |  |
| 2022 |  |  | 26,765,348 |  |  |  |
| 2023 |  |  |  |  | 122,739,919 |  |

- Action 8670 is "Vigilância, Prevenção e Controle em HIV/AIDS e Outras Doenças Sexualmente Transmissíveis". Action 20QD (2012) is "Coordenação Nacional da Vigilância, Prevenção e Controle em HIV/AIDS, Hepatites Virais e Outras Doenças Sexualmente Transmissíveis".
- Action 20YJ is "Fortalecimento do Sistema Nacional de Vigilância em Saúde" in 2019 and "Fortalecimento do Sistema Nacional de Vigilância em Saúde e Ambiente" in 2024. Sub-plan 0001 is "Coordenação Nacional da Vigilância, Prevenção e Controle em HIV/AIDS, Hepatites Virais e Outras Doenças Sexualmente Transmissíveis" in 2013 and "Coordenação Nacional da Vigilância, Prevenção e Controle em HIV/AIDS, Hepatites Virais e Outras Infecções Sexualmente Transmissíveis" in 2019, with a single national subtitle every year. Sub-plan 0001 last appears in 2022.
- Action 20YE is "Aquisição e Distribuição de Imunobiológicos e Insumos para Prevenção e Controle de Doenças" in 2019. Sub-plan 0003 is "Aquisição, Acondicionamento e Distribuição de Insumos para Prevenção e Controle de Doenças para Hiv/Aids, Sífilis e Hepatites Virais".
- Action 21DZ is "Aquisição e Distribuição de Insumos para Prevenção e Controle de Doenças" in 2023. Sub-plan 0004 is "Disponibilização de Insumos para Prevenção e Controle de Doenças para Hiv/Aids, Sífilis e Hepatites Virais". In 2022 and from 2024 the supplies for HIV/AIDS, syphilis and viral hepatitis sit in sub-plan 0002 of action 4370.
- The smaller actions of 2000-2007 are 2721, 2875, 3878, 3880, 3897, 3910, 3943, 3954, 4297, 4298, 4309, 4327. The titles of the smaller actions cover an education campaign (3878), staff training (3880), studies and research (3897), day-hospital and home care services (3910), technical events (3943), promotion of safer practices (3954, 2721), condoms (4297), tests for public laboratories (4298), the Disque-AIDS phone line (4309) and laboratory diagnosis and follow-up (2875, 4327). From 2004 the title of action 4327 becomes health care for people with HIV/AIDS and other sexually transmitted diseases. Whether any of the smaller actions carries state subtitles is NOT VERIFIED.
- 2013 also holds sub-plan 0001 of action 20YK ("Incentivo Financeiro a Estados, Distrito Federal e Municípios para Ações de Prevenção e Qualificação da Atenção em HIV/AIDS e outras Doenças Sexualmente Transmissíveis", 28 subtitles) and sub-plan 0003 of action 20YO ("Atendimento à População com Medicamentos para Tratamento dos Portadores de HIV/AIDS e outras Doenças Sexualmente Transmissíveis"). Sub-plan 0001 of action 20YK and sub-plan 0003 of action 20YO paid nothing in 2013.

Coverage limits.
- The search reads titles only. Federal money for HIV inside lines whose action and sub-plan titles carry no HIV term, for example general hospital and outpatient care, cannot be identified. The federal HIV lines found here give a lower bound on federal HIV spending.
- State and municipal spending from own revenues sits outside the federal budget and outside the SPARQL endpoint.
- Values are nominal reais. Any comparison with the USD panel needs an exchange-rate rule.

Additive test against the BRA panel (read 6 October 2026).
- The BRA panel holds domestic_hiv_spend for 2017-2024 from unaids_gam_expenditure, hiv_expenditure_total for 2012, 2014, 2017-2024 from unaids_aidsinfo and for 2017-2024 from unaids_gam_expenditure, and GAM programme splits, for example hiv_spend_treatment for 2017-2024.
- BRA admin1 rows come only from pepfar_agency_snu and pepfar_snu for 2020-2025, and every BRA admin1 row is a service count or rate, with no spending row.
- National. The federal lines measure federal budget execution in reais, not total domestic HIV spending in USD, and the GAM total already counts federal spending. As domestic_hiv_spend the federal lines are DUPLICATE in concept for 2017-2024. As a separate federal-execution indicator the federal lines are ADDITIVE for 2000-2016 and 2025-2026 and serve as a cross-check for 2017-2024. The federal lines never enter domestic_hiv_spend without a decision from Jason and Adrian.
- Admin1. The transfers to states and municipalities (action 0214, then action 20AC, then sub-plan 0002 of action 20AL) are ADDITIVE for 2003-2026 across 27 federative units (26 states and the Federal District), as a federal transfer indicator by state. From 2025 the sub-plan 0002 title also names tuberculosis, so the scope of the series changes in 2025. The "Nacional" subtitle is not allocated to a state and stays national.

Grade. GRADE 1 (open structured feed). The SPARQL endpoint answers JSON per query with no login and no challenge, and covers 2000-2026 with a graph for every year. The portal page JSON is also structured but throttled by the AWS WAF challenge.

Other Brazilian budget routes, status only.
- Tesouro Transparente (the National Treasury open-data portal) CKAN package_search answered 200 JSON. Not needed while the SPARQL endpoint covers 2000-2026.
- SIOP (Sistema Integrado de Planejamento e Orçamento, the federal planning and budget system) root answered 403. The anonymous QlikView page for IAS/Execucao_Orcamentaria.qvw answered 200 HTML (5,119 bytes). Not explored.

Round two for Brazil budget lines.
- Resolve the 2025 conflict between SPARQL and the portal, and the 2024 liquidated difference.
- Check whether any of the smaller actions of 2000-2007 carries state subtitles.
- Check the general surveillance action 20AL for other HIV or hepatitis sub-plans beyond sub-plan 0002.
- Look at the sioplegis graph on the SPARQL endpoint.
- Decide with Jason which stage (liquidated or paid) a connector would read, and whether a federal-execution indicator enters the panel at all.

## CLASS SWEEP. Regional health bodies (CARPHA, PANCAP, COMISCA, ORAS-CONHU, MERCOSUR, GCTH, OECS), LAC entries (6 October 2026)

Scope. A regional health body publishes for a group of LAC countries, so a sweep of the regional bodies can find tables missed by the country searches. Pages were read as HTML or REST JSON, and file sizes were taken by HEAD request. No PDF, CSV or docx file was opened. The bodies searched, with members in the LAC set, are listed below.
- CARPHA (Caribbean Public Health Agency, the public health agency of CARICOM, the Caribbean Community). CARPHA hosts the annual and surveillance reports of CAREC (Caribbean Epidemiology Centre), the earlier regional epidemiology centre. LAC members are BLZ, GUY, HTI, JAM, SUR and TTO.
- PANCAP (Pan Caribbean Partnership against HIV and AIDS, a CARICOM partnership). The PANCAP country data pages cover eight LAC countries, BLZ, CUB, DOM, GUY, HTI, JAM, SUR and TTO.
- COMISCA (Consejo de Ministros de Salud de Centroamérica y República Dominicana, the council of health ministers of SICA, the Central American Integration System). LAC members are BLZ, CRI, SLV, GTM, HND, NIC, PAN and DOM.
- ORAS-CONHU (Organismo Andino de Salud, Convenio Hipólito Unanue, the Andean health organisation). LAC members are BOL, COL, ECU, PER and VEN. Chile is a member outside the LAC set.
- MERCOSUR health ministers' meeting (Reunión de Ministros de Salud del MERCOSUR). Founding MERCOSUR members in the LAC set are ARG, BRA and PRY. Uruguay is outside the LAC set.
- GCTH (Grupo de Cooperación Técnica Horizontal, the group of directors of national HIV programmes in Latin America and the Caribbean).
- OECS (Organisation of Eastern Caribbean States). No OECS member is in the LAC set, so the OECS is out of scope.

### PANCAP
Site. pancap.org runs WordPress with an open REST interface at /wp-json/wp/v2/. The REST page list holds 110 pages (reg_pancap_pages.json) and the REST media list holds 319 files (reg_pancap_media.json).

Country Data tables. The page for a country (pancap.org/pancap-data/{country}/) is an HTML table built with the wpDataTables plugin, with the columns Indicators, Estimates and Sources. The tables for BLZ, CUB, DOM, HTI, JAM, SUR and TTO carry a title row of the form "HAITI | 2023" and put the Indicators column sixth. The Guyana table carries no title row and puts the Indicators column second, after wdt_ID. The parse found every column by header name (reg_pancap_table_{country}.json, reg_pancap_compare.json). The Trinidad and Tobago table shows "..." for every estimate, with the note "Estimates were not available at the time of publication." The table rows carry UNAIDS estimates and GAM (Global AIDS Monitoring, the UNAIDS country reporting system) programme counts, and the survey rows cite DHS, MICS and IBBS (integrated biological and behavioural surveillance) surveys.

Comparison for 2023 with the panel (read 6 October 2026) and with the raw UNAIDS PrEP export in data/raw/unaids, for PLHIV (people living with HIV), the ART count (people receiving antiretroviral therapy), the PMTCT count (pregnant women receiving antiretroviral medicines to prevent vertical transmission of HIV from mother to child) and the PrEP count (people receiving pre-exposure prophylaxis). Panel figures are national rows for all ages, for men and women together. A dash in the table means no row.

| Country | PLHIV PANCAP | PLHIV panel (unaids_aidsinfo, who_gho) | ART PANCAP | ART panel | PMTCT PANCAP | PMTCT panel | PrEP PANCAP | PrEP raw UNAIDS 2023 |
|---|---|---|---|---|---|---|---|---|
| BLZ | 3,600 | 3,800, 3,200 | 1,766 | who_tme 1,766, who_gho 1,392 | 41 | 34 | 68 | <100 |
| CUB | 44,000 | 41,000, 40,000 | 28,405 | who_gho 28,405 | 215 | 215 | 1,541 | 1500 |
| DOM | 84,000 | 84,000, 85,000 | 51,775 | who_gho 51,775 | ... | 1,546 | 3,658 | 3700 |
| GUY | 10,000 | 10,000, 10,000 | 6,765 | who_gho 6,765 | 197 | 199 | 692 | 690 |
| HTI | 140,000 | 140,000, 140,000 | 117,761 | who_gho 117,761 | 3,664 | 3,664 | 23,957 | 24 000 |
| JAM | 26,000 | 28,000, 28,000 | 14,735 | who_gho 14,887, global_fund 14,755 | 365 | 365 | 284 | <500 |
| SUR | 7,400 | 7,700, 7,700 | 3,361 | who_gho 3,795, global_fund 3,327 | 95 | 95 | - | - |
| TTO | ... | -, 11,000 | ... | who_gho 7,222 | ... | 75 | - | - |

Guyana PLHIV in PANCAP carries the range "10 000 [7500 - 15 000]".

Row-by-row comparison. Every PANCAP row with a matching panel indicator was compared with the panel (reg_pancap_rowcompare.py and reg_pancap_rowclass.py, output reg_pancap_rowclass.json). 181 PANCAP rows map to a panel indicator, with the cascade row "Percent of people living with HIV who are on ART" counted once, because the cascade row repeats the ART coverage row. The Guyana table carries no section header above the first estimates rows, so reg_pancap_rowcompare.py assigns the Guyana rows above the first section header to "HIV and AIDS Estimates". A PANCAP row is compared with a single primary panel source, who_tme for the WHO TB and HIV estimates, who_gho for the ART and PMTCT counts, unaids_gam_expenditure for the HIV expenditure rows and unaids_aidsinfo for every other row. When the primary source has no row, the comparison falls back to the next source in a fixed order written in reg_pancap_rowclass.py. Panel rows are national rows for 2023, for men and women together, and for all ages unless the PANCAP row names children aged 0 to 14. Key-population rows are compared with the panel's unaids_aidsinfo rows labelled 2024 ("Most recent data as of 2024" in the UNAIDS export) under any sex code, because the panel codes the sex-worker ART coverage row as female. A PANCAP figure counts as within rounding when rounding the panel figure to a whole number or to three significant figures gives the PANCAP figure, when rounding either figure to two significant figures gives the other figure, or when a censored figure such as "<100" contains the other figure. Rounding the panel figure to three significant figures changes the class of the DOM HIV expenditure rows and of no other row.

| Kind of PANCAP row | Rows | Equal | Within rounding or censoring | Differs | Blank in PANCAP | No panel row |
|---|---|---|---|---|---|---|
| Modelled UNAIDS estimates, and percentages with a modelled denominator | 93 | 21 | 2 | 46 | 16 | 8 |
| Reported programme figures (ART count, PMTCT count, PrEP count, TB and HIV co-management) | 36 | 16 | 10 | 6 | 4 | 0 |
| WHO TB and HIV estimates (TB incidence and TB deaths among people living with HIV) | 14 | 0 | 6 | 8 | 0 | 0 |
| Key-population survey rows (size, prevalence, testing, ART coverage) | 34 | 20 | 0 | 12 | 1 | 1 |
| HIV expenditure (DOM only) | 4 | 0 | 4 | 0 | 0 | 0 |

- Modelled rows. EARLIER ROUND, NOT ADDITIVE. Modelled PANCAP rows differ from the primary panel source in 46 of the 69 rows with a figure in PANCAP and in the panel. PLHIV equals the unaids_aidsinfo figure for DOM, GUY and HTI, and differs for BLZ (3,600 in PANCAP against 3,800 in the panel), CUB (44,000 against 41,000), JAM (26,000 against 28,000) and SUR (7,400 against 7,700). JAM new infections in PANCAP (1,200) differ from unaids_aidsinfo (1,300) and equal who_gho. UNAIDS revises the whole modelled series at every estimates round, and a PANCAP table copied from an earlier round would explain why modelled PANCAP rows differ from the panel more often than reported counts and survey rows do (NOT VERIFIED). A modelled figure from an earlier round does not enter the panel beside figures from the current round.
- Modelled rows with no panel row. NOT ADDITIVE without a decision from Jason. PANCAP gives JAM AIDS deaths ("<1000"), JAM PMTCT coverage (90), JAM pregnant women needing ARV for PMTCT ("<500"), the JAM vertical transmission rate (6.87), BLZ PMTCT coverage (81), BLZ pregnant women needing ARV for PMTCT ("<100"), the BLZ vertical transmission rate (17.29) and BLZ ART coverage for children aged 0 to 14 (37), and the panel holds no 2023 row for any of the JAM and BLZ figures listed. The current raw UNAIDS exports in data/raw/unaids carry "..." in every year for JAM AIDS deaths, for JAM and BLZ PMTCT coverage, pregnant women needing ARV and the vertical transmission rate, and for BLZ in the children's testing and treatment cascade. The BLZ rows in the raw exports carry the footnote "Children estimates were not available at the time of publication." The current UNAIDS estimates round publishes no figure for the JAM and BLZ rows listed, so entering the PANCAP figures would put earlier-round estimates into series the current round leaves empty.
- Reported programme figures. PANCAP equals the primary panel source, or falls within rounding or censoring, in 26 of the 32 rows with a figure in PANCAP and in the panel. The differing rows are BLZ ART (1,766 in PANCAP against 1,392 in who_gho, with who_tme at 1,766), JAM ART (14,735 against 14,887, with global_fund at 14,755), SUR ART (3,361 against 3,795, with global_fund at 3,327), BLZ children on ART (29 against 27), BLZ PMTCT (41 against 34) and GUY PMTCT (197 against 199). The PANCAP SUR count for adults aged 15 and over (3,327) equals the panel's global_fund SUR count for all ages, and whether the global_fund row counts adults only is NOT VERIFIED. Cause of the JAM and SUR ART differences NOT RESOLVED, possibly a GAM figure revised after PANCAP published. DOM PMTCT shows "..." in PANCAP against 1,546 in who_gho. DUPLICATE for the ART, PMTCT and TB and HIV co-management rows that equal the panel or fall within rounding. The PrEP rows fall within rounding or censoring and are treated separately below.
- WHO TB and HIV estimates. EARLIER ROUND, NOT ADDITIVE. TB incidence among people living with HIV differs from who_tme for BLZ, CUB, DOM, HTI, JAM, SUR and TTO, every PANCAP country with a figure, for example HTI at 2,400 in PANCAP against 3,000 in who_tme. The Guyana table carries no TB and HIV section. HTI TB deaths among people living with HIV differ (1,100 against 1,200). The TB death rows for BLZ, CUB, DOM, JAM, SUR and TTO give a censored PANCAP figure ("<100", or "<500" for DOM) that contains the who_tme figure. An earlier WHO estimates round would explain the incidence differences (NOT VERIFIED).
- Key-population survey rows. PANCAP equals the panel's unaids_aidsinfo rows labelled 2024 in 20 of the 32 rows with a figure in PANCAP and in the panel. The differing key-population rows are CUB ART coverage for sex workers (82.6 in PANCAP against 81.7 in the panel), gay men and other men who have sex with men (84.4 against 81.5) and transgender people (86.8 against 84.6), DOM size estimates for sex workers (102,900 against 103,700) and for gay men and other men who have sex with men (143,700 against 145,700), DOM ART coverage for sex workers (25.1 against 43), gay men and other men who have sex with men (35.7 against 46.7) and transgender people (19.9 against 10.4), prisoner HIV prevalence for HTI (2.8 against 3.3), JAM (6.9 against 2.0) and TTO (0.3 against 0.7), and the TTO prisoner size estimate (3,400 against 3,100). The HTI prisoner row cites "HTW: Données de programme", where HTW is Health Through Walls, a prison health programme named in the Haiti table. Cause of the key-population differences NOT RESOLVED. DUPLICATE where PANCAP equals the panel.
- HTI ART coverage among sex workers. ADDITIVE, single point. PANCAP gives 74 per cent ("Source: IBBS 2023"). The panel holds no HTI row for sex-worker ART coverage, and the raw UNAIDS sex-worker ART coverage export has no Haiti row.
- DOM HIV expenditure. DUPLICATE. The DOM table alone carries an "HIV expenditure" section, with total spending of 80,200,000 US dollars, domestic public spending of 32,300,000, domestic private spending of 16,200,000 and international spending of 31,700,000, and the source note "Source:GAM_2024" on every expenditure row. The PANCAP expenditure figures equal the panel's unaids_gam_expenditure figures for 2023 (80,229,484, 32,349,667, 16,168,458 and 31,711,360 US dollars) rounded to three significant figures, and the PANCAP total equals the unaids_aidsinfo total for 2023 (80,200,000). The unaids_gam_expenditure total for 2024 (79,042,985) does not round to the PANCAP total, so the PANCAP expenditure rows report spending in 2023, the year in the DOM table title.
- PrEP count (people receiving pre-exposure prophylaxis). ADDITIVE AT PRECISION for six countries and the single year 2023. The raw UNAIDS export rounds or censors the 2023 figure, and the panel keeps the UNAIDS figure with the censoring notation in extra. The panel holds BLZ as a bound from 0 to 100 ("<100") where PANCAP gives 68, and JAM as a bound from 0 to 500 ("<500") where PANCAP gives 284. For CUB, DOM, GUY and HTI the panel holds rounded figures (1,500, 3,700, 690 and 24,000) where PANCAP gives 1,541, 3,658, 692 and 23,957. Every PANCAP PrEP figure falls inside the rounding or censoring of the UNAIDS figure. SUR and TTO have no PrEP row in PANCAP or in the raw export. The panel's pepfar_panorama PrEP rows for 2023 (DOM 1,047, HTI 13,392, JAM 246) differ from the national figures, and the definition of the Panorama PrEP rows was not checked in the regional-bodies sweep.
- ART count by sex. ADDITIVE as a new breakdown for BLZ, CUB, DOM, GUY, HTI, JAM and SUR, the single year 2023. PANCAP gives ART counts for women and for men aged 15 and over and for children aged 0 to 14 in every LAC table with estimates. In the BLZ, CUB, DOM, GUY, HTI, JAM and SUR tables, the counts for women and for men sum to the PANCAP count for adults aged 15 and over, and the adult and children counts sum to the PANCAP total. Counts for 2023 are BLZ 851 women, 886 men and 29 children, CUB 6,048 women, 22,322 men and 35 children, DOM 26,261 women, 25,000 men and 514 children, GUY 3,651 women, 3,056 men and 58 children, HTI 71,379 women, 43,151 men and 3,231 children, JAM 8,077 women, 6,525 men and 133 children, SUR 1,762 women, 1,565 men and 34 children. TTO shows "..." for every ART row. The panel holds no ART count or ART coverage row by sex for any PANCAP country, apart from key-population rows. The raw UNAIDS exports hold the ART count for all ages only. The raw cascade exports for female and male adults ("Testing and treatment cascade - Female adults (15+)" and "... - Male adults (15+)") hold percentages, and the unaids_aidsinfo connector lists the cascade files in DECLARED_UNMAPPED because of a two-row header. The JAM and SUR totals in PANCAP differ from who_gho, so the JAM and SUR breakdowns sum to totals the panel does not hold. Whether AIDSinfo serves the ART count by sex is a round-two check.
- Rows absent from the panel by policy. NOT ADDITIVE under the current panel scope. PANCAP gives key-population condom use, DHS stigma attitudes, intimate partner violence, family planning demand and HIV prevention knowledge. The unaids_aidsinfo connector excludes the matching UNAIDS exports in DECLARED_UNMAPPED. The unaids_aidsinfo connector gives the stigma and condom-use exports the reason "single-point 2024 snapshot, outcome of a different question", gives the gender exports, which hold partner violence and family planning, the reason "attitudes and partner violence, a different research question", and gives the HIV prevention knowledge export the reason "survey knowledge measure, a different research question".

PANCAP rows with no panel indicator. The PANCAP rows in the table below match no panel indicator, so reg_pancap_rowclass.py did not compare the rows with the panel. The rows were checked instead against the raw UNAIDS exports in data/raw/unaids and against DECLARED_UNMAPPED in the unaids_aidsinfo connector. A country counts as having a figure when the PANCAP row carries a number or a censored number.

| PANCAP rows | LAC countries with a figure | Matching export in data/raw/unaids | Reason in the unaids_aidsinfo connector | Additive test |
|---|---|---|---|---|
| PLHIV, new infections and AIDS deaths for adults aged 15 and over and for children aged 0 to 14 | BLZ, CUB, DOM, GUY, HTI, JAM, SUR | Adults (15+) and Children (0-14) exports for PLHIV, new infections and AIDS deaths | "age band of an indicator already in the panel, needs an age_group column" | EARLIER ROUND, NOT ADDITIVE. Against the raw age exports for 2023, 18 PANCAP age rows are equal, two rows give a censored PANCAP figure that contains the raw figure, three rows give a different censoring bound, 13 rows differ, for example HTI adults living with HIV (130,000 in PANCAP against 140,000) and DOM children living with HIV (2,800 against 3,300), and six rows carry a PANCAP figure where the raw export carries "..." (BLZ children living with HIV, newly infected and dying of AIDS, JAM children newly infected, and JAM adults and children dying of AIDS). The panel holds no PLHIV, new infection or AIDS death row by age for any PANCAP country. The connector reason is out of date, as noted below the table. |
| PLHIV, new infections and AIDS deaths for women and for men aged 15 and over, HIV prevalence for women and for men aged 15 to 49, and HIV prevalence among young women and young men | BLZ, CUB, DOM, GUY, HTI, JAM, SUR | No export by sex for PLHIV, new infections or AIDS deaths | No reason, since no export exists | NOT VERIFIED. The PANCAP rows by sex are modelled, so a current-round AIDSinfo series by sex would take precedence over the PANCAP figures. The panel holds no PLHIV, new infection or AIDS death row by sex for any PANCAP country, and holds HIV prevalence by sex only as DHS survey rows for DOM (2002, 2007, 2013) and HTI (2006, 2012, 2016). Round two checks whether AIDSinfo serves the modelled estimates by sex. |
| HIV incidence per 1,000 uninfected population, for all ages and for adults aged 15 to 49 | BLZ, CUB, DOM, GUY, HTI, JAM, SUR | Yes | "derivable from new_infections and population" | NOT ADDITIVE, derivable from panel rows. |
| Epidemic transition metrics (incidence to prevalence ratio, incidence to mortality ratio, per cent change in new infections and in AIDS deaths since 2010) | BLZ, CUB, DOM, GUY, HTI, JAM, SUR | Yes, four exports | "derivable from two indicators already in the panel", "derivable from new_infections" and "derivable from aids_deaths" | NOT ADDITIVE, derivable from panel rows. |
| Orphans due to AIDS aged 0 to 17, HIV-exposed children who are uninfected, and new infections averted by PMTCT | BLZ, CUB, DOM, GUY, HTI, JAM, SUR | Yes | "modelled consequence, not a service count" for orphans and exposed children, "modelled counterfactual, not a service count" for infections averted | NOT ADDITIVE under the current panel scope. |
| Cascade counts ("People living with HIV who know their status", "People living with HIV who are on ART" and "People living with HIV who have suppressed viral loads") | BLZ, CUB, DOM, GUY, HTI, JAM, SUR | The cascade exports hold percentages, and the JAM row of the all-ages cascade export holds no value above 100 | "two-row header this parser cannot read, and the conditional bars need a decision" | EARLIER ROUND, NOT ADDITIVE. Every PANCAP cascade count divided by the PANCAP PLHIV figure comes within three percentage points of the PANCAP cascade percentage (18 counts, largest gap 2.8 points), so the counts carry the modelled PANCAP PLHIV figure. |
| Cervical cancer screening among women living with HIV (survey data) | DOM, 81 per cent, "Source: 2013 DHS; reported having undergone a Pap smear" | Yes | "single-year or near-empty, cannot show a change" | NOT ADDITIVE under the current panel scope. |
| Hepatitis C testing, and people coinfected with HIV and HCV (hepatitis C virus) starting HCV treatment | BLZ ("Source: MIN OF HEALTH BHIS 2019") and CUB ("Source: Registro informatizado VIH/sida 2018") | HCV treatment export only | "different disease, would widen the research question" | NOT ADDITIVE under the current panel scope. |
| Hepatitis B and hepatitis C coinfection with HIV, and hepatitis C among prisoners | CUB, DOM, SUR | Prisoner viral hepatitis export only | "single-point 2024 snapshot, outcome of a different question" | NOT ADDITIVE under the current panel scope. |
| TB infection among prisoners | HTI, 5.1 per cent, "Source: Programme data, 2022" | No export | No reason, since no export exists | NOT ADDITIVE under the current panel scope, a single point with no panel indicator for prisoner TB. |
| Condoms distributed in prison HIV prevention programmes | DOM, 120,750, "Source: Routine programme data, 2022" | Yes, the prison programmes export | "single-point 2024 snapshot, one population only" | NOT ADDITIVE under the current panel scope. |

Out-of-date connector reason. The DECLARED_UNMAPPED comment in hivimpact/connectors/unaids_aidsinfo.py (line 146) still says "The panel has no age_group column", and the age exports carry the reason "needs an age_group column". The panel now carries an age_group column, with the values 0-14, 0-19, 0-9, 10-19, 15+, 15-24, 15-49, 18+, 20-24 and 25+, from the sources cm_cnls, ne_annuaire, ng_ndr, td_annuaire, who_gho, who_tme and za_thembisa. The same connector comment says mapping the age exports would add roughly 173,000 values and more than double the panel, and leaves the decision to the researcher. Whether to map the age exports is a decision for Jason.

CSV files. The REST media list holds per-country CSV files, read by HEAD only, with no CSV file opened (reg_pancap_csv_head.json). The LAC set accounts for 23 files, totalling 161,586 bytes.
- Uploaded 2025-04-23, eight files named "{Country}-2023.csv", 40,490 bytes in total.
- Uploaded 2024-07-30, eight files named "data_{Country}_2023.csv", 42,268 bytes in total. The 2024 upload and the 2025 upload differ in size for every LAC country, for example Haiti at 7,534 bytes in the 2024 upload and 7,063 bytes in the 2025 upload, so PANCAP has published two versions of the 2023 table.
- Uploaded 2017-05-09, six files with no year in the name (belize.csv, guyana.csv, haiti.csv, jamaica.csv, suriname.csv, trinidad-tobago.csv), 20,513 bytes in total.
- Uploaded 2021-05-09, Countries_Data.csv at 58,315 bytes.
- The 2017 and 2021 files may hold earlier years, which would turn the PANCAP PrEP and ART-by-sex rows into short series. NOT VERIFIED.

Document Library. 337 items over 17 pages (pancap.org/resources/document-library/?sf_paged=N, reg_pancap_doclib_titles.json). The listing gives title, publication date and publisher, with no direct file link. No title names a data table. Titles that suggest HIV figures are listed below, and no item was opened.
- "HIV in the Caribbean at a glance – 2019 Data" (Jul 2020).
- "Understanding “the Last 90” in Guyana’s HIV Treatment Cascade A Facility-Based Assessment of the Viral Loads of Key Populations" (Nov 2019).
- Situational analyses by the Latin America and the Caribbean Regional Platform for Support (Plataforma LAC) for Haiti, Cuba, Belize, Suriname and Guyana (2018-2019).
- "Report on the Global Fund Project for the Period October 2016 – December 2017" and "Baseline assessment report for the PANCAP and CVC/COIN Global Fund Grants 5 June, 2017". The baseline title names CVC/COIN (the Caribbean Vulnerable Communities Coalition with COIN, the Centro de Orientación e Investigación Integral, a Dominican civil-society organisation) beside PANCAP as holders of Global Fund grants.
- National strategic plans for Jamaica (2014-2019), Belize (2012-2016 and the HIV and TB plan for 2016-2020), Trinidad and Tobago (2013-2018) and Guyana (HIVision 2020).
- PAHO "Antiretroviral Treatment in the Spotlight" reports for 2013, 2014 and 2015, and PAHO "HIV Prevention in the Spotlight" (Nov 2017).
- "Spending on health and HIV/AIDS: domestic health spending and development assistance in 188 countries, 1995–2015", the paper by IHME (the Institute for Health Metrics and Evaluation) behind the IHME database of development assistance for health, already graded GRADE 3 in PHASE4_FEASIBILITY_WCA.md.

Grade. GRADE 1 for the Country Data tables (open HTML tables and open CSV files, no login), with a single year (2023) in the tables read. GRADE 2 for the Document Library (open PDF reports, unopened).

### CARPHA
Site. carpha.org runs DNN (DotNetNuke). The publications catalogue at /What-We-Do/Health-Information/Publications loads a category by ASP.NET postback, read with stream=True and kept only as text/html. No HIV data page was found on the site, and no file name in any category carries HIV or AIDS.
Categories read, links per category. Annual reports 26, newsletters 17 (15 CAREC Surveillance Reports and two OECS newsletters), clinical guidelines seven, communicable diseases three, manuals three, monitoring and evaluation five, other six and research eight (reg_carpha_cat_*.txt). The site map (reg_carpha_sitemap.xml) lists no Surveillance Report.
HEAD requests went to 41 report files (reg_carpha_head.json). The server answered 200 with a PDF for 37 files and answered 404 for four files, "Annual Report 2017.pdf", "Annual Report 2018.pdf", "Annual Report 2019.pdf" and "CARPH ANNUAL REPORT 2013 EVERSION.pdf".
- CAREC Annual Reports 2001-2011, 11 files. Sizes in bytes 2001 1,209,618, 2002 1,711,712, 2003 58,897,612, 2004 8,628,965, 2005 3,006,230, 2006 4,007,827, 2007 4,006,496, 2008 5,467,772, 2009 29,126,246, 2010 14,364,651, 2011 11,339,066.
- Annual reports 2005-2010 (annualreport{year}.pdf), six files. Sizes in bytes 2005 724,867, 2006 650,392, 2007 1,243,629, 2008 1,201,365, 2009 1,187,324, 2010 1,917,644.
- CAREC Surveillance Reports, 15 issues from April 2002 to December 2012 (Apr2002, Nov2003, Mar2005, Jun2005, Jun2010, Aug2010, Apr2011, May2011, Aug2011, Dec2011, Mar2012, May2012, Aug2012, Nov2012, Dec2012), from 320,552 to 1,384,209 bytes.
- CARPHA Annual Report 2023 at 32,927,709 bytes, State of Public Health 2019 at 10,612,363, State of Public Health in the Caribbean 2014-2016 at 6,776,189, the inaugural State of Public Health report 2013 at 8,545,852, and the CCH-IV Regional Public Good Report at 20,295,763.
Additive test. NOT VERIFIED. HIV content of the CAREC and CARPHA reports is unknown until a report is opened. Reported HIV cases by country for 2001-2012 would be ADDITIVE, because the panel's new_diagnoses rows for GUY, HTI, JAM, SUR and TTO start in 2018 and come from PEPFAR and the Global Fund, and BLZ has no new_diagnoses row.
Grade. GRADE 2 if the reports carry country tables (open PDF).

### COMISCA
sica.int answered HTTP 403 with an F5 block page ("Servicio no disponible") on 6 October 2026 (reg_sica_comisca_403.html). Recorded as BLOCKED, with no bypass. A web search snippet says the COMISCA executive secretariat (SE-COMISCA) runs the regional coordinating mechanism for HIV, tuberculosis and malaria (UNVERIFIED). Round two checks the Wayback Machine CDX index for sica.int/comisca pages.

### ORAS-CONHU
Site. orasconhu.org runs Drupal 9, with no wp-json route, no JSON:API route and no site map. The publications listing (/es/publicaciones?page=0 to 31) holds 244 items over 32 pages (reg_oras_pubs_titles.json). File sizes come from HEAD (reg_oras_head.json), and no file was opened.
- HIV items, three in all. "Plan Andino para la eliminación del estigma y la discriminación contra las personas con VIH, población clave y población vulnerable en la Región Andina al 2030" (7,546,834 bytes), "Análisis de Situación de Estigma VIH/Plan Subregional de Salud" (ORAS_CONHU74 ONUSIDA.pdf, 1,228,145 bytes) and "Invertir para obtener repercusión en la lucha contra el VIH, la tuberculosis o la malaria" (doc_tec_1_nota_conceptual.pdf, 1,392,536 bytes). The Andean stigma plan and the stigma situation analysis are policy documents, and "Invertir para obtener repercusión" is a guide to writing Global Fund concept notes.
- The pages of the Andean committee on HIV/AIDS and hepatitis (Comité Andino de VIH/SIDA y Hepatitis, five pages) carry two COVID-19 mental-health PDFs and two links present on every page of the site, with no HIV data.
- Border health situation analyses (análisis de situación de salud, ASIS) for five border areas, Tumbes-El Oro, San Ignacio-Zamora, Palca-Charaña, Desaguadero (Bolivia-Peru) and Arica-Tacna, from 18,639,020 to 34,596,965 bytes. Whether an ASIS holds local HIV case counts is NOT VERIFIED, because no ASIS file was opened, and the publication years are unknown. Arica is in Chile, outside the LAC set.
- Blog post 371 (11 October 2018) says the ORAS-CONHU tuberculosis programme supports CAR-LAC, the regional advisory committee for the Global Fund regional grants in Latin America and the Caribbean, and names ICW (International Community of Women Living with HIV), REDLACTRANS (the Latin American and Caribbean network of trans people), REDCA+ (the Central American network of people living with HIV) and ORAS-CONHU as principal recipients of regional grants.
Negative result. orasconhu.org holds no HIV data series.

### MERCOSUR
A PAHO news page dated 28 August 2012 and titled "Lanzamiento del Boletín Epidemiológico de VIH/ITS del Mercosur" (reg_mercosur_paho_news.html) reports that the intergovernmental HIV/AIDS commission of the MERCOSUR health ministers' meeting presented the first issue of an epidemiological bulletin on HIV and sexually transmitted infections, written by the HIV programmes of the member states. The PAHO page gives no file link. Whether later issues exist is UNVERIFIED. A web search found commission minutes as docx files on documentos.mercosur.int, for example 106962_RMS-CIVIH_2025_ACTA01_ES.docx, not opened. Round two checks the Wayback Machine for the 2012 bulletin.

### GCTH and OECS
- GCTH. No GCTH data site found. A search snippet says the GCTH brings together the directors of national HIV programmes of 20 countries (UNVERIFIED). Negative result.
- OECS. Out of scope, with no member in the LAC set. Two OECS newsletters sit in the CARPHA newsletter category.

### Summary for the regional-bodies class
- ADDITIVE AT PRECISION. PANCAP PrEP counts for 2023 for BLZ, CUB, DOM, GUY, HTI and JAM, unrounded where UNAIDS rounds or censors. Single year in the tables read.
- ADDITIVE as a new breakdown. PANCAP ART counts for women and for men aged 15 and over, 2023, for BLZ, CUB, DOM, GUY, HTI, JAM and SUR. The panel already has a sex column, so the breakdown fits the panel schema.
- ADDITIVE, single point. HTI ART coverage among sex workers, 74 per cent in the 2023 IBBS.
- NOT ADDITIVE without a decision from Jason. PANCAP figures where the current UNAIDS round publishes no figure, for JAM AIDS deaths, for JAM and BLZ PMTCT coverage, pregnant women needing ARV and the vertical transmission rate, for BLZ ART coverage among children, and for the JAM and BLZ age rows listed in the table of PANCAP rows with no panel indicator.
- EARLIER ROUND, NOT ADDITIVE. Modelled PANCAP rows, including the rows by age and the cascade counts, and the WHO TB and HIV estimates.
- NOT VERIFIED. Modelled PANCAP rows by sex, pending a round-two check of AIDSinfo.
- DUPLICATE. PANCAP reported programme figures that equal the panel or fall within rounding, key-population rows that equal the panel, and the DOM HIV expenditure rows.
- NOT RESOLVED. Cause of the differing JAM and SUR ART counts, the BLZ and GUY PMTCT counts and the differing key-population rows.
- NOT ADDITIVE under the current panel scope. PANCAP rows matching UNAIDS exports in DECLARED_UNMAPPED (condom use, stigma, partner violence and family planning, HIV prevention knowledge, incidence per 1,000, epidemic transition metrics, orphans, HIV-exposed uninfected children, infections averted, cervical screening, hepatitis and prison programmes), and HTI prisoner TB.
- POSSIBLY ADDITIVE, unopened. CAREC Surveillance Reports and CAREC annual reports for 2001-2012, and the ORAS-CONHU border ASIS reports.
- BLOCKED. sica.int (COMISCA), F5 block page.
- NONE. ORAS-CONHU data series, GCTH, OECS.

Downloads to ask Jason about (filename, source, size). No file was downloaded.
- PANCAP Haiti-2023.csv (7,063 bytes) and data_Haiti_2023.csv (7,534 bytes), pancap.org, to compare the two 2023 versions.
- PANCAP haiti.csv (3,880 bytes, uploaded 2017-05-09) and Countries_Data.csv (58,315 bytes, uploaded 2021-05-09), pancap.org, to see whether earlier years exist.
- CARPHA CAREC_Surveillance_Report_Dec2012.pdf (1,093,934 bytes) and 2011 CAREC Annual Report.pdf (11,339,066 bytes), carpha.org, to test for HIV case tables.
- ORAS-CONHU ASIS Desaguadero baj.pdf (29,166,128 bytes), orasconhu.org, to test for local HIV counts.

Round two for regional bodies.
- Open the PANCAP CSVs listed above, if Jason agrees, and check whether the 2017 and 2021 files hold years before 2023.
- Check AIDSinfo for unrounded PrEP counts, for the ART count by sex and for the modelled estimates by sex. An AIDSinfo series for any of the listed measures would make the matching PANCAP rows DUPLICATE.
- Find the definition of the pepfar_panorama PrEP rows before any PrEP comparison.
- Wayback Machine CDX for sica.int/comisca and for the 2012 MERCOSUR bulletin.
- Ask Jason whether PANCAP figures may fill the JAM and BLZ rows the current UNAIDS round leaves empty, and whether the unaids_aidsinfo connector should now map the age exports.

## CLASS SWEEP. Household surveys (DHS, MICS and national surveys outside the DHS Program), LAC entries (6 October 2026)

Scope. A household survey interviews a national sample of households. A survey can also carry an HIV biomarker, a blood test for HIV taken from respondents during the interview visit. The only panel series built from household surveys is hiv_prevalence_15_49 from the dhs connector. Three survey families were searched.
- DHS (Demographic and Health Surveys, the USAID survey programme), read through the DHS Program API (api.dhsprogram.com, JSON). A DHS survey identifier joins the two-letter DHS country code, the survey year and the survey type, so HT2016DHS is the Haiti DHS with survey year 2016.
- MICS (Multiple Indicator Cluster Surveys, the UNICEF household survey programme), read through the UNICEF SDMX HIV_AIDS dataset (sdmx.data.unicef.org, SDMX-JSON) and through the World Bank Microdata Library catalogue. mics.unicef.org/surveys and mics.unicef.org/api/survey returned HTTP 403 with the Cloudflare page "Just a moment..." on 6 October 2026. BLOCKED, not bypassed.
- National surveys run outside the DHS Program, read through the World Bank Microdata Library and the IHSN (International Household Survey Network) catalogue. The World Bank Microdata Library and the IHSN catalogue run the NADA catalogue software, whose API returns JSON.
No PDF, CSV, zip or sav file was opened.

### DHS Program API
Countries. The API holds DHS country codes for 15 LAC countries (BOL, BRA, COL, DOM, ECU, GTM, GUY, HND, HTI, MEX, NIC, PER, PRY, SLV and TTO). The API holds no code for ARG, BLZ, CRI, CUB, JAM, PAN, SUR and VEN (mics_dhs_api1.json).

Surveys. The default survey list holds 51 LAC surveys, and the list requested with surveyStatus=all holds 64. Every survey in the all-status list carries the status Completed, so the API shows no LAC survey in progress. The latest LAC household survey is HT2016DHS, published in July 2018, and the latest LAC survey of any type is HT2017SPA, a survey of health facilities published in April 2019 (mics_dhs_api1.json, mics_dhs_api2.json).

HIV testing. Six surveys carry the HIV testing characteristic (characteristic 23), DR2002DHS, DR2007DHS and DR2013DHS for the Dominican Republic and HT2006DHS, HT2012DHS and HT2016DHS for Haiti. GY2005AIS, GY2009DHS, HN2011DHS, GU2015DHS, CO2015DHS and BO2008DHS carry HIV behaviour and HIV knowledge characteristics without HIV testing, as do PE2013DHS and PE2014DHS.

National prevalence. The API returns 18 national rows of HIV prevalence among people aged 15 to 49 (HA_HIVP_B_HIV for women and men together, HA_HIVP_W_HIV for women, HA_HIVP_M_HIV for men) for the Dominican Republic in 2002, 2007 and 2013 and for Haiti in 2006, 2012 and 2016. Every value equals the matching dhs row of hiv_prevalence_15_49 in the panel, and the panel holds 18 LAC dhs rows. DUPLICATE.

Sub-national prevalence. Requested with breakdown=subnational, the API returns 192 region rows, 81 for the Dominican Republic and 111 for Haiti. The Dominican Republic surveys give nine regions per survey, including a row labelled "Region 0". The Haiti surveys give 12 regions in HT2006DHS, 13 in HT2012DHS including a row labelled "Camps", and 12 in HT2016DHS. Every region appears for women and men together, for women and for men. The panel holds no dhs row with an admin1 value in any country, because the dhs connector calls the API without a breakdown parameter and so receives national rows only. ADDITIVE AT admin1 for survey years 2002 to 2016. HT2006DHS, HT2012DHS and HT2016DHS list "..Grande-Anse" and "..Nippes" beside "Grande-Anse/Nippes". A connector reading the region rows must keep only the combined Grande-Anse/Nippes row, or only the ..Grande-Anse and ..Nippes rows, to avoid counting the same respondents twice.

Antenatal HIV testing. HA_CATH_W_ATR is named in the API "Pregnant women tested for HIV during ANC or labor and receiving the results". The API returns 11 LAC values (mics_dhs_api4.json).

| Survey | HA_CATH_W_ATR (%) | Panel anc_hiv_testing_pct, same country and year |
|---|---|---|
| CO2010DHS | 84.1 | - |
| CO2015DHS | 89.1 | 62 |
| DR2007DHS | 92 | - |
| DR2013DHS | 0.8 | - |
| GU2015DHS | 49.3 | 42 |
| GY2005AIS | 55.4 | - |
| GY2009DHS | 75.1 | - |
| HN2011DHS | 75.1 | - |
| HT2006DHS | 26.4 | - |
| HT2012DHS | 61.2 | - |
| HT2016DHS | 70 | 73 |

The panel holds 170 LAC rows of anc_hiv_testing_pct, all from unaids_aidsinfo, where the figures come from the routine programme reports of Global AIDS Monitoring. The DHS figure is reported by women in the survey interview, while the panel figure is counted by clinics. Three country-years overlap, COL 2015 (panel 62, DHS 89.1), GTM 2015 (panel 42, DHS 49.3) and HTI 2016 (panel 73, DHS 70). POSSIBLY ADDITIVE as a survey series beside the routine series, decision for Jason.

DR2007DHS and DR2013DHS antenatal figures (mics_dhs_api7.json).

| Indicator | API name | DR2007DHS | DR2013DHS |
|---|---|---|---|
| HA_CATH_W_CSL | Pregnant women counselled for HIV during ANC visit | 60.4 | 55.1 |
| HA_CATH_W_ATR | Pregnant women tested for HIV during ANC or labor and receiving the results | 92 | 0.8 |
| HA_CATH_W_ATN | Pregnant women tested for HIV during ANC or labor, but did not receive the results | 1.6 | 96.2 |
| HA_CATH_W_NRS | Pregnant women tested for HIV during ANC not receiving results | 1.6 | 96.2 |

The DR2013DHS values for women tested and receiving the result and for women tested without the result look swapped, since 96.2% of women would otherwise have been tested without receiving the result. NOT VERIFIED against the DR2013 final report, which was not opened. A connector must not take HA_CATH_W_ATR for DR2013DHS from the API until the DR2013 final report settles whether HA_CATH_W_ATR and HA_CATH_W_ATN are swapped.

Surveys outside the default list. The 13 extra surveys in the all-status list are BR1991DHS (footnote "Northeast region"), PE2013DHS and PE2014DHS (the PE2013DHS footnote points to the INEI microdata site), the SPA facility surveys GU1997SPA, GY2004SPA, HT2013SPA and HT2017SPA (SPA is the Service Provision Assessment, a survey of health facilities), the surveys of DHS type OTH (DR1986OTH, GU1997OTH, PE1986OTH and HT2013OTH, footnoted "Sexual Activity Pilot Survey"), and the special surveys DR2007SPE and DR2013SPE.
- DR2007SPE and DR2013SPE are the Bateyes surveys of the Dominican Republic, run by CESDEM (Centro de Estudios Sociales y Demográficos). The DR2007SPE footnote reads "BATEYES (this is a sample of the population who live and work in sugar cane plantations)". DR2007SPE fieldwork ran from July to August 2007 with 2,540 households, 1,575 women and 1,820 men. DR2013SPE fieldwork ran from July to October 2013 with 2,569 households, 1,707 women and 2,101 men. The survey records list characteristic 23 (HIV testing), and the IHSN metadata for the 2013 survey states that the blood samples and the HIV test followed the protocols of ENDESA 2013, the 2013 Dominican Republic DHS. The surveycharacteristics endpoint returns nothing for the Bateyes surveys, IndicatorData is 0, and the API serves no HA_HIVP row (mics_dhs_api6.json). The DHS survey pages list the final reports FR212 (PDF, 1876K) and FR303 (PDF, 1415K), not opened. Batey residents are not a panel population group. NOT ADDITIVE under current panel scope. The Bateyes prevalence figures sit only in the FR212 and FR303 reports or in DHS microdata released after registration, GRADE 3.
- The DR2002DHS survey record carries the footnote "There is no possibility of linking the HIV Test data to the survey data." The national prevalence figure for 2002 is unaffected, since the API serves the figure directly.

### UNICEF SDMX HIV_AIDS dataset
Request. The dataset has the dimensions REF_AREA, INDICATOR, AGE, SEX, WEALTH_QUINTILE, RESIDENCE, DATA_SOURCE and TIME_PERIOD (mics_sdmx_structure.xml). The request for the 23 LAC countries returned SDMX-JSON holding 32,866 observations (mics_sdmx_lac.json, flattened in mics_sdmx_lac_flat.csv).

| Source class | Observations |
|---|---|
| UNAIDS 2026 estimates | 29,087 |
| MICS | 1,499 |
| DHS and AIS | 1,184 |
| Global AIDS Monitoring, alone or with UNAIDS 2026 estimates | 1,082 |
| JAM survey of 2012, source not named as MICS or DHS | 14 |

Survey rows. The MICS, DHS and JAM 2012 rows number 2,697 and cover seven indicators, which measure people ever tested for HIV who received the result of the last test, people tested in the last 12 months who received the result, comprehensive correct knowledge of HIV, knowing a place to get tested, condom use at last sex among people with more than one partner in the past 12 months, condom use at last sex with a non-marital, non-cohabiting partner, and discriminatory attitudes towards people living with HIV. The survey rows cover ages 15 to 19, 20 to 24 and 15 to 24, and also 15 to 49 for every indicator except HVA_PREV_CNDM_REG. No survey indicator in the dataset is a panel indicator, and the unaids_aidsinfo connector lists HIV prevention knowledge, stigma and discrimination, and condom use among the AIDSinfo indicators kept outside the panel. NOT ADDITIVE under current panel scope. The latest MICS in the dataset is 2019, for ARG, CUB, DOM and HND.

Newer UNAIDS round. UNICEF labels the modelled rows "UNAIDS 2026 estimates", with COVERAGE_TIME "2000 to 2025" and values for 2025. The panel holds unaids_aidsinfo LAC rows for 2000 to 2024, all retrieved on 5 September 2026, and the year columns of the raw AIDSinfo exports in data/raw/unaids end at 2024.
- The UNICEF modelled rows cover the child, adolescent and youth age groups only, with no all-ages row for people living with HIV, new infections or deaths. For children aged 0 to 14 in 2010 to 2024, 503 of 780 figures for people living with HIV, new infections and deaths match the raw UNAIDS children exports exactly and 277 differ. HTI children living with HIV in 2024 read 7,200 in UNICEF and 6,800 in the raw export. For 2025, UNICEF gives 51 rows with no raw column to compare (mics_sdmx_child_cmp.csv).
- All-ages PMTCT rows (mics_sdmx_pmtct_cmp.csv). PMTCT (prevention of mother-to-child transmission) coverage holds 248 rows and the vertical transmission rate 253 rows, for 2010 to 2025. The count of pregnant women receiving antiretroviral medicines holds 266 rows of rounded Global AIDS Monitoring counts, for example HTI 2023 3,700 against who_gho 3,664. DUPLICATE at lower precision for the UNICEF count of pregnant women receiving antiretroviral medicines.
- Coverage and vertical transmission rows with no panel row. Values for 2025 in 11 countries for coverage and 13 for vertical transmission, BOL 2024 coverage and COL 2024 vertical transmission. JAM coverage for 2010 to 2022 and 2025 (2025 reads ">95") and JAM vertical transmission for 2010 to 2022. TTO and VEN for 2010 to 2025, 16 rows per country and indicator. The raw AIDSinfo exports show "..." in every year for JAM, TTO and VEN on coverage and on vertical transmission, and the TTO rows carry the footnote "Estimates were not available at the time of publication." BLZ has no UNICEF row for coverage or vertical transmission.
- Where the 2026 round and the round behind the panel give a value for the same year, the UNICEF and panel figures can differ. HTI 2024 coverage reads 58 in UNICEF and 60 in the panel, and HTI 2024 vertical transmission reads 17.5 in UNICEF and 20 in the panel.
- READING. A 2026 UNAIDS round exists and publishes JAM, TTO and VEN figures that the raw exports behind the panel show as "...". The 2026 round affects every region of the project, not only LAC, and bears on the PANCAP decision about the JAM rows. Whether aidsinfo.unaids.org itself now serves the 2026 round is NOT VERIFIED.

### MICS through the World Bank Microdata Library
The NADA catalogue search for MICS (mics_wb1.py), filtered locally to the LAC set, lists 31 LAC MICS surveys (mics_wb_lac.json). Every entry carries the NADA access form "remote", meaning the World Bank catalogue describes the survey and points to the MICS programme site for the microdata. The MICS site returned the Cloudflare page, so the terms of microdata access were not read.
- ARG 2011 to 2012 and 2019 to 2020. BLZ 2006, 2011 and 2015 to 2016. BOL 2000. CRI 2011 and 2018. CUB 2006, 2010 to 2011, 2014 and 2019. DOM 2000, 2014 and 2019. GUY 2000, 2014 and 2019. HND 2019. JAM 2005 to 2006 and 2011. MEX 2015. PAN 2013. PRY 2016. SLV 2014. SUR 1999 to 2000, 2010 and 2018. TTO 2000 and 2011. VEN 2000.
- The newest World Bank MICS entries are ARG 2019, CRI 2018, CUB 2019, DOM 2019, GUY 2019, HND 2019 and SUR 2018. The titles of CRI 2018, CUB 2019 and GUY 2019 name MICS round 6. The catalogue lists no MICS7 survey for LAC, although the Belize statistics office lists MICS7KeyFindingsReport.pdf (8,024,714 bytes, notes line 789, not opened).
- 13 catalogue entries have no year match among the MICS sources of the UNICEF SDMX dataset, BLZ 2006, BOL 2000, CUB 2006, DOM 2000, GUY 2000, GUY 2019, JAM 2005 to 2006, JAM 2011, PAN 2013, SUR 1999 to 2000, SUR 2018, TTO 2000 and VEN 2000. The SDMX dataset therefore lacks the GUY survey of 2019 and the SUR survey of 2018.
- The SDMX dataset holds no HIV prevalence row from any MICS. The MICS rows in the SDMX dataset cover HIV knowledge, testing history, condom use and discriminatory attitudes only. NOT ADDITIVE under current panel scope.

### National surveys outside the DHS Program
Search. The World Bank and IHSN catalogues were searched with 20 terms, including Demografía y Salud, ENDESA, ENSANUT, FESAL, ENSMI, ENDEMAIN, Reproductive Health Survey, VIH, HIV and biomarker (mics_nat1.py). The filter by identifier prefix or country name kept 1,788 LAC hits (mics_nat_lac.json).

Surveys found.
- BLZ Family Health Survey 1991 and 1999. BOL EDSA (Encuesta de Demografía y Salud) 2016 and 2023. CRI ENSR (Encuesta Nacional de Salud Reproductiva) 1992 to 1993.
- ECU ENDEMAIN (Encuesta Demográfica y de Salud Materna e Infantil) 1989, 1994, 1999 and 2004. SLV FESAL (Encuesta Nacional de Salud Familiar) 1993, 1998 and 2008. GTM ENSMI (Encuesta Nacional de Salud Materno Infantil) 2002 and 2008 to 2009.
- HND ENESF (Encuesta Nacional de Epidemiología y Salud Familiar) 1991 to 1992 and 1996, ENSM (Encuesta Nacional de Salud Masculina) 1996, and the joint ENESF and ENSM of 2001. JAM Reproductive Health Survey 1997, 2002 and 2008 to 2009.
- MEX ENSANUT (Encuesta Nacional de Salud y Nutrición) 2011 and the mid-term ENSANUT of 2016. NIC ESF (Encuesta sobre Salud Familiar) 1992 to 1993 and ENDESA (Encuesta Nicaragüense de Demografía y Salud) 2006 to 2007 and 2011 to 2012. PRY ENSMI 1998 and ENDSSR (Encuesta Nacional de Demografía y Salud Sexual y Reproductiva) 2004 and 2008.

Metadata test (mics_nat2.py, mics_nat2.json). The study metadata of the 29 surveys above and of the 2013 Bateyes survey were read as API JSON and searched for HIV test and biomarker terms. The metadata of BOL EDSA 2016 and 2023, SLV FESAL 1998 and 2008, GTM ENSMI 2008 to 2009 and HND ENESF and ENSM 2001 mention anaemia or the HemoCue haemoglobin meter, and SLV FESAL 1998 also mentions retinol. No survey run outside the DHS Program names an HIV test in the metadata. The only HIV blood test named is in the 2013 Bateyes survey.

Absent from the World Bank and IHSN catalogues. Peru ENDES after 2012 (ENDES is the continuous DHS run by INEI, the Peruvian statistics institute, and the catalogues list the continuous survey to PER_2012_DHSC while the DHS API adds PE2013DHS and PE2014DHS), the Honduras ENDESA and MICS of 2019 (the World Bank lists HND_2019_MICS, probably the same survey, NOT VERIFIED), ENSANUT rounds after 2016, and the Brazil PNDS 2006 and PNS (Pesquisa Nacional de Saúde).

Met in the country sweeps. BOL EDSA 2023 (notes lines 444 to 446, questions on ever tested and on collecting the result, microdata behind a login, GRADE 3). HND ENDESA 2019 (notes line 566, HIV knowledge and testing questions only). NIC ENDESA 2011/12 (notes line 597, sav files listed open). HTI EMMUS (Enquête Mortalité, Morbidité et Utilisation des Services, the Haiti DHS, notes line 833). The Peru ENDES testing questions are not yet checked (notes line 276).

READING. Outside the DHS Program, LAC national surveys carry HIV knowledge and self-reported testing only. NOT ADDITIVE to panel indicators. Self-reported ever tested by department (EDSA 2023, ENDES, ENDESA) remains a candidate new indicator for Jason to decide, as recorded for Bolivia.

Other catalogue classes seen. The Global School-based Student Health Survey for 19 LAC countries, the World Health Survey 2003 for BRA, DOM, ECU, GTM, MEX and PRY, and SAGE (the WHO Study on Global Ageing and Adult Health) for Mexico. School and adult health surveys sit outside panel scope and were not checked for HIV items.

### Household survey readings for Jason
- DHS sub-national HIV prevalence for DOM and HTI is ADDITIVE AT admin1 for 2002 to 2016, through the existing dhs connector with breakdown=subnational. The dhs connector must keep either the combined Grande-Anse/Nippes row or the separate ..Grande-Anse and ..Nippes rows, never the combined row together with the separate rows.
- The DHS antenatal testing figures are a survey measure beside the routine anc_hiv_testing_pct series. Adding the DHS figures needs a decision by Jason, and DR2013DHS first needs a check of whether HA_CATH_W_ATR and HA_CATH_W_ATN are swapped.
- The 2026 UNAIDS round, seen through UNICEF, fills JAM, TTO and VEN PMTCT coverage and vertical transmission and adds 2025 values. The 2026 round affects every region.
- MICS and the national surveys outside the DHS Program carry no HIV biomarker. NOT ADDITIVE.

Downloads to ask Jason about (filename, source, size). No file was downloaded.
- DHS final reports FR212 (1876K) and FR303 (1415K), dhsprogram.com, for the Bateyes prevalence figures if Jason widens the population groups.
- DHS final report for DR2013DHS, dhsprogram.com, size not taken, to check whether HA_CATH_W_ATR and HA_CATH_W_ATN are swapped for DR2013DHS.

Round two for household surveys.
- Read aidsinfo.unaids.org as HTML to see whether the 2026 round is live there.
- Read the INEI microdata pages for Peru ENDES 2015 onward as HTML, and confirm whether HND_2019_MICS is the Honduras ENDESA and MICS of 2019.
- Retry mics.unicef.org from another network only if Jason chooses. The Cloudflare page is not to be bypassed.

## CLASS SWEEP. Routine health information systems (DHIS2 and national equivalents), LAC entries (6 October 2026)

Scope. A routine health information system collects monthly counts from health facilities, for example HIV tests, positive results and people on treatment. DHIS2 (District Health Information Software 2, open-source software from the University of Oslo) runs the routine system of many health ministries. A DHIS2 server can publish dashboards or an API without a login, and the Africa and WCA sweeps found DHIS2 servers behind a login only. The LAC sweep looked for a DHIS2 server, or a national routine system with public output, for the 23 LAC countries and for CARPHA (Caribbean Public Health Agency). Requests were unauthenticated GET requests for HTML or JSON, HEAD requests and DNS lookups, with TLS verification on. No login was attempted, no demonstration account was tried and no file was downloaded.

### Host discovery
- Certificate logs. crt.sh (a public search of TLS certificate logs) was queried for host names containing "dhis" under the country domain of every LAC country. ARG timed out at 44 seconds, and BLZ, BOL and BRA returned HTTP 502. A narrower query for mspp.gouv.ht also timed out at 44 seconds. The job was stopped. crt.sh UNAVAILABLE on 6 October 2026.
- DNS, round one (dhis_dns1.json). 118 guessed names, made of the labels dhis2, dhis, hmis and sis and a control label zz-no-such-host-8472, which no real host uses, under 23 domains (22 health ministry domains and carpha.org), plus sisnu.org, www.sisnu.org and dhis2.sisnu.org. The SUR health ministry publishes through gov.sr and has no site under a domain of the ministry (notes line 750), so no SUR name was guessed. Eight names resolve. The five salud.gob.ec names, control included, resolve to 190.152.52.141, so salud.gob.ec answers every name (wildcard DNS) and the ECU results mean nothing. The names dhis.minsa.gob.pa (PAN, 190.34.154.94), sis.minsa.gob.pe (PER, 190.116.92.81) and sis.mpps.gob.ve (VEN, 190.202.54.9) resolve, and the controls under minsa.gob.pa, minsa.gob.pe and mpps.gob.ve do not. The sisnu.org names do not resolve.
- DNS, round two (dhis_dns2.json), nine names built from system names in the web leads below. siis.salud.gob.hn (HND, 181.210.26.198) and hacu.health.gov.tt (TTO, 200.108.14.114) resolve, and the HND and TTO controls do not. No answer for sisnu.mspp.gouv.ht, dhis2.health.gov.tt, dhis2.carpha.org, dhis.carpha.org and the HTI control.

### Host probes
The probe requested the root page and the DHIS2 paths /api/system/info.json, /dhis-web-commons/security/login.action, /api/dashboards.json and /api/apps. A DHIS2 server behind a login answers the API paths with a redirect to the login page.
- dhis.minsa.gob.pa (PAN). Connection timeout on port 443 for every path, and on ports 80 and 8080 over plain HTTP. REACH FAILURE.
- sis.minsa.gob.pe (PER). Connection reset by the server on every path, over HTTPS and over plain HTTP. REACH FAILURE.
- sis.mpps.gob.ve (VEN). The TLS handshake fails with the server alert TLSV1_ALERT_INTERNAL_ERROR, a fault on the server side and not a failure to verify the certificate chain. REACH FAILURE.
- hacu.health.gov.tt (TTO). Connection timeout on every path. REACH FAILURE.
- siis.salud.gob.hn (HND). The root page is the default nginx page "Welcome to nginx!", and the DHIS2 paths at the root return HTTP 404, with a Tomcat 404 page at the login path. The same host serves two DHIS2 servers under sub-paths.
  - /dhis/ is SIIS (Sistema Integrado de Información en Salud, the integrated health information system of the Honduras health ministry). The root redirects to the DHIS2 start page, and /api/system/info.json, /api/dashboards.json and /api/loginConfig redirect to the login page. The login page carries the SIIS title and the Honduras flag, and offers no public dashboard link. The DHIS2 version is not exposed. GATED, GRADE 3.
  - /dhis2/ redirects to the DHIS2 login app, and the older login path carries the title "DHIS2 Demo Login". /dhis2/api/loginConfig, a DHIS2 endpoint open without a login by design, returns API version 2.42.4, an empty application title, self-registration off, account recovery off and no single sign-on provider. The /dhis2/ server is a demonstration or test server, GATED.
  - Every redirect points to plain http:// although the request used HTTPS. The path /siis/ returns 404.

### Ministry home pages
The home pages of 22 health ministries and of CARPHA (23 pages, dhis_links1.json) were scanned for links to DHIS2, dashboards, statistics or SIIS-type systems. No page links to a DHIS2 server.
- Not read. GTM www.mspas.gob.gt returned HTTP 403 with the Cloudflare page "Just a moment...", and MEX www.gob.mx/salud returned a "Challenge Validation" page. The Cloudflare block and the MEX challenge were not bypassed. SLV returned HTTP 522. COL, ECU and GUY timed out at connection, HTI timed out on reading, NIC failed at TLS and PRY failed to connect. DOM returned HTTP 200 with no links in the HTML, because a script builds the page.
- Read with no relevant link. Nine pages, ARG, BLZ, BOL, BRA, CRI, HND, JAM, TTO and CARPHA. The only ARG match is a LinkedIn link, and the only BRA match is "Painel Estatístico de Pessoal", a federal staff panel. NEGATIVE.
- Links already covered by the country sections. CUB links to the MINSAP statistical yearbooks (Cuba section), and VEN links to ESTADÍSTICAS VITALES (Venezuela section).
- Links followed. PER "Estadísticas - REUNIS" and "Tablero de Control PP 0018", and PAN "Estadísticas de Salud", reported below.

### Peru, REUNIS and RADAR
- REUNIS (Repositorio Único Nacional de Información en Salud, the statistics portal of MINSA, the Peruvian health ministry, minsa.gob.pe/reunis). The HIV menu holds one item, "Indicador Cobertura de tamizaje de VIH en población estimada" (HIV screening coverage of the estimated population), and the HIV menu entry sits inside an HTML comment. The HIV page has an empty static content block. In the built-in browser the HIV page loads a single iframe, the Tableau Public workbook SIHCEMINSA_17029315336290, view Historia1. The Tableau Public workbook API gives the title "SIHCE MINSA", the author "OGEI MINSA 2024", nine sheets, 4,659 views and a last update on 16 January 2024. SIHCE is the electronic health record system of MINSA, so the HIV page shows no HIV screening figure. NEGATIVE.
- REUNIS budget and morbidity pages ("Meta Física y Financiera", "PPR: Indicadores de Desempeño", "Morbilidad General", "Atenciones de Consulta Externa") have empty static content blocks, and a script fills the budget and morbidity pages. Every REUNIS page carries the same 20 Power BI publish-to-web links, so the report behind a given page is NOT MAPPED.
- RADAR PP0018 (mef.pythonanywhere.com, a budget tracker for the MINSA non-communicable disease programme). The RADAR page asks for a Google sign-in ("Acceso restringido"). Off topic for HIV, GRADE 3. NEGATIVE.

### Panama, MINSA statistical yearbooks 2019 to 2022
The Panama section lists the MINSA yearbooks for 1999 to 2018 as single PDF files (notes line 478). The page /informacion-salud/anuarios-estadisticos also links the yearbooks for 2019 to 2022 as pages of single tables, with a PDF and an XLSX file per table (pan_anuarios_rows.json). The yearbook pages hold 44 tables for 2019, 40 for 2020, 48 for 2021 and 50 for 2022.
- HIV tables. Every yearbook from 2019 to 2022 has a single HIV table, the AIDS cases reported by health region (Casos Reportados de SIDA por Región de Salud). The 2019 table covers 1984 to 2019, the 2020 table covers 1984 to 2020 and adds the case fatality rate (letalidad), and the 2021 and 2022 tables cover 2010 to 2021 and 2010 to 2022. XLSX sizes from HEAD requests (pan_sida_heads.json) are 24,692 bytes for 2019, 25,646 for 2020, 26,195 for 2021 and 25,220 for 2022. Not downloaded.
- Additive test. AIDS case reports count people diagnosed at the AIDS stage, a different measure from new HIV diagnoses, and the panel has no indicator for AIDS case reports. The panel holds PAN new_diagnoses from PEPFAR sources only. POSSIBLY ADDITIVE AT admin1, as a new indicator of AIDS cases reported by health region, if Jason accepts AIDS case reports into the panel. GRADE 1 by file.
- Other yearbook tables. The 2022 yearbook lists the ten leading causes of death nationally and the five leading causes by province and indigenous comarca. Whether HIV appears among the leading causes is NOT VERIFIED. The page /informacion-salud/indicadores-de-salud links basic health indicator PDFs for 2013 to 2023 and provincial indicator PDFs, with HIV content NOT VERIFIED.

### Routine systems named in web search leads, no public host found
The leads below come from search snippets and are UNVERIFIED unless a page was read.
- HTI. SISNU (Système d'Information Sanitaire National Unique, the national health information system of Haiti) runs on DHIS2 and covers 1,048 facilities, UNVERIFIED. The sisnu names above do not resolve, and mspp.gouv.ht timed out. A PAHO news item of 24 September 2026, read as HTML, reports that the Haiti health ministry presented the "Rapport Statistique 2025 de la santé en Haïti" on 28 August 2026 from SISNU data. The news item gives no link and does not mention HIV. A printed SISNU extract of the kind found for Cameroon, DR Congo and Chad is possible, NOT VERIFIED.
- TTO. HIV case-based surveillance on DHIS2 Tracker. A DHIS2 community forum post of 20 November 2025, read as HTML, reports a rollout from March 2025 with 52 nurses at 32 facilities, a 97% match between the digital and paper records, and all 60 rapid testing sites planned by January 2026. The post says the data feed Power BI dashboards, does not say whether the dashboards are public and names no host. The UCSF Caribbean programme page returned HTTP 403 and was not retried. health.gov.tt/node/216 holds a rapid testing procedure only.
- JAM. An HIV data warehouse called SUPA, not DHIS2, UNVERIFIED. No public host found.
- SUR, GTM, ECU and SLV. DHIS2 used for COVID-19 vaccination, the HEARTS hypertension programme or vaccines, UNVERIFIED. HIV not mentioned.
- CARPHA. A regional DHIS2 for syndromic surveillance, severe acute respiratory infection and laboratory surveillance, migrated in 2023 (DHIS2 community abstract, read as HTML). HIV not mentioned. dhis2.carpha.org and dhis.carpha.org do not resolve.

### National routine systems already covered by the country sections
- GTM. SIGSA datos de salud (sigsa.mspas.gob.gt) covers 13 topics with no HIV topic, NEGATIVE (notes line 324). The MSPAS HIV situation room category refuses access, GRADE 3 (notes line 322).
- BOL. The SNIS-VE hosts (Sistema Nacional de Información en Salud y Vigilancia Epidemiológica) did not answer, REACH FAILURE (notes lines 434 and 453).
- SLV. SIMMOW (the MINSAL morbidity and mortality system) and SUMEVE (the HIV monitoring and surveillance system) returned the Cloudflare block page, BLOCKED (notes line 494).
- PAHO. PAHO Core Indicators 93 to 96 (new HIV diagnoses) carry the collection process "DHIS2" (notes line 25). The label probably refers to a PAHO collection platform for country submissions and not to a country server, NOT VERIFIED.

### Assessment
- Round one found no DHIS2 server or national routine system with an open API or public dashboard for any LAC country. NEGATIVE for a GRADE 1 routine feed in LAC.
- HND SIIS on DHIS2 is GATED, GRADE 3. The indicators held in SIIS are NOT VERIFIED.
- PAN MINSA yearbook tables of AIDS cases by health region, 2010 to 2022 and back to 1984 in the 2019 and 2020 editions, POSSIBLY ADDITIVE AT admin1 as a new indicator, GRADE 1 by file. Decision for Jason.
- PER REUNIS HIV page NEGATIVE. RADAR PP0018 NEGATIVE.
- REACH FAILURE for dhis.minsa.gob.pa, sis.minsa.gob.pe, sis.mpps.gob.ve and hacu.health.gov.tt. Whether any of the four hosts runs DHIS2 is NOT VERIFIED.

### Round two
- Retry crt.sh for host names containing dhis, sisnu, siis and hmis under the LAC country domains.
- Retry dhis.minsa.gob.pa, sis.minsa.gob.pe, sis.mpps.gob.ve and hacu.health.gov.tt, and test the sub-paths /dhis and /dhis2 on every host that answers, because the HND servers sit under sub-paths.
- Find the link to the Haiti Rapport Statistique 2025 and check for HIV tables.
- Find whether the TTO HIV Power BI dashboards are public.
- Look for printed SIIS extracts in Honduras health ministry reports.
- Map the Power BI reports behind the REUNIS budget and morbidity pages.
- Check the PAN yearbook mortality tables for HIV among the leading causes.

### Downloads to ask Jason about
- PAN MINSA yearbook AIDS case tables, XLSX, minsa.b-cdn.net (redirects to minsa.gob.pa), 24,692 bytes (2019), 25,646 (2020), 26,195 (2021) and 25,220 (2022).

## ROUND TWO ITEM AND CLASS SWEEP. MERCOSUR HIV bulletins, and dataZoa tables at national statistics offices, LAC entries (6 October 2026)

### MERCOSUR HIV bulletins (round-two item from the regional-bodies section)
- Route. The regional-bodies section planned a Wayback Machine search for the 2012 MERCOSUR bulletin (notes lines 1378 and 1408). A web search found the 2012 bulletin and a 2015 edition live on gub.uy, the site of MSP (Ministerio de Salud Pública, the Uruguay health ministry), so the Wayback route was not needed (mercosur_bol.json, mercosur_bol_heads.json).
- 2012 edition. The gub.uy page "Boletín Epidemiológico - VIH 2012 Mercosur" carries the date 22/06/2012 and credits the Comissão Intergovernamental de HIV/Aids do MERCOSUL, the intergovernmental HIV/AIDS commission of the MERCOSUR health ministers' meeting. File "Boletin epidemiologico VIH 2012 Mercosur_0.pdf", HEAD 200, application/pdf, 4,842,592 bytes, Last-Modified 17 February 2020. Not opened.
- 2015 edition. The gub.uy page "Boletín Epidemiológico - Revista Mercosur VIH 2015" carries the date 15/02/2015 and credits the Revista da Comissão Intergovernamental de HIV/Aids do MERCOSUL, the journal of the MERCOSUR HIV/AIDS commission. File "Revista Mercosur VIH 2015_0.pdf", HEAD 200, application/pdf, 5,391,020 bytes, Last-Modified 17 February 2020. Not opened.
- Content. The PAHO launch news of 28 August 2012 (reg_mercosur_paho_news.html) says the 2012 bulletin gives an epidemiological profile of populations at higher risk for HIV, AIDS and congenital syphilis, and supports joint goals for the region and the border areas. Whether the 2012 bulletin or the 2015 edition holds tables by country, by year or by border area is NOT VERIFIED.
- Later editions. Two web searches found no MERCOSUR HIV edition after 2015. The gub.uy publication search returned the same 11 publication links for three different queries, so the gub.uy site search does not filter by query, and whether gub.uy holds more MERCOSUR editions is NOT VERIFIED.
- COVIGSAL bulletin. A web search found "boletin-epidemiologico-mercosur-covigsal.pdf" for 2025 under the special bulletins of the Brazilian health ministry on gov.br. A file name in the search results (102358_SGT11-COVIGSAL_2024_ACTA02_ES.doc, not opened) places COVIGSAL under SGT11, the MERCOSUR working subgroup on health. The search summary says the 2025 bulletin is volume three and covers ARG, BRA, PRY and Uruguay (UNVERIFIED). gov.br answered HTTP 403 to a HEAD request for the PDF, recorded as BLOCKED with no retry. Whether the COVIGSAL bulletin covers HIV is UNVERIFIED.
- Additive test. NOT RUN, because no bulletin was opened. Uruguay is outside the LAC set, and which member and associate states the 2012 bulletin and the 2015 edition cover is NOT VERIFIED. GRADE 2 (open report) for the 2012 and 2015 PDFs. POSSIBLY ADDITIVE, unopened.
- COMISCA. The Wayback route for sica.int/comisca (notes line 1408) was not run. sica.int answered with an F5 block page (notes line 1367), and reading archived copies of sica.int could count as getting around the F5 block on sica.int. Jason decides whether the Wayback Machine may be used for sica.int.

### dataZoa tables at national statistics offices (class sweep)
- Scope. dataZoa is a commercial data-hosting service. STATIN, the Jamaican statistics office, publishes the tables of registered deaths by cause through dataZoa, with HIV disease deaths for 2018 to 2023 (notes lines 649 to 654). The dataZoa sweep asks which other LAC statistics offices publish through dataZoa.
- Home pages (dz_sweep.json). The home pages of the 23 LAC national statistics offices were read as HTML and searched for the string "datazoa". Of the 23 home pages, 16 were readable, and no readable page carries the string, the STATIN home page included. A home-page search therefore cannot detect a dataZoa publisher.
- Blocks recorded, with no bypass. CRI inec.cr HTTP 403 "Access Denied". DOM one.gob.do HTTP 403 Cloudflare. SLV onec.bcr.gob.sv "Request Rejected" page. GTM ine.gob.gt Radware CAPTCHA page. No answer from CUB onei.gob.cu (connection timeout), PAN inec.gob.pa (connection timeout) and PRY ine.gov.py (connection error).
- WordPress REST search (dz_wp.json). Seven sites answered the WordPress REST API with JSON (BLZ, BOL, ECU, GUY, HND, SUR, TTO), and the search for "datazoa" in pages and posts returned zero items on all seven WordPress sites.
- Method error, recorded. The WordPress script used the final address of every home page, so the GTM requests went to validate.perfdrive.com, the Radware challenge host, and the SLV requests went to onec.bcr.gob.sv, the host that had returned the "Request Rejected" page. Two requests went to validate.perfdrive.com and two to onec.bcr.gob.sv, and every answer was a challenge page or a rejection page. No challenge was solved and no request was repeated.
- Second publisher found. dataZoa account dzuuid=256 belongs to ABS (Algemeen Bureau voor de Statistiek, the Suriname statistics office), because the table page loads the icon of statistics-suriname.org (dz_sur_256.html). Table th=a9Bwi9IWRh gives total nominal labour costs per employee for 2004 to 2009. Not health. The ABS WordPress search returned zero items, so the WordPress test also misses a known dataZoa publisher. The ABS publication listings name no cause-of-death table (notes line 741).
- JAM series history. The per-series link for HIV disease (series demography/00003675) on the STATIN table returns a PNG chart (HEAD 200, image/png, 13,588 bytes, not opened, dz_jm_series_head.json). The links on the table page for sending series to an account lead to the dataZoa login page. Whether the HIV disease series holds years before 2018 stays NOT VERIFIED.
- Assessment. Confirmed dataZoa publishers in LAC are STATIN (JAM) and ABS (SUR). No open method lists dataZoa publishers by country, so the dataZoa class is NOT RESOLVED for the other 21 countries. The only HIV series found on dataZoa remains the STATIN deaths table, ADDITIVE and already recorded in the Jamaica section.

### Round two
- Ask Jason whether the Wayback Machine may be used for sica.int/comisca.
- Retry the COVIGSAL bulletin listing page on gov.br, HTML only, and stop at any further 403.
- Ask the ABS or STATIN, through Jason, whether a list of dataZoa tables exists, and whether the STATIN HIV disease series starts before 2018.

### Downloads to ask Jason about
- MERCOSUR HIV bulletin 2012, "Boletin epidemiologico VIH 2012 Mercosur_0.pdf", gub.uy, 4,842,592 bytes.
- MERCOSUR HIV journal 2015, "Revista Mercosur VIH 2015_0.pdf", gub.uy, 5,391,020 bytes.

## ROUND TWO. Reachability retries for hosts that gave no answer in round one, LAC entries (6 October 2026)

Method. A GET of the home page of 17 hosts with TLS verification on and a 40-second timeout, keeping the HTTP status and the HTML title (retry1.py, retry1.json). No challenge page was worked around. A second script read the home pages of four more Infomed and ONEI hosts (sld5.py, sld5.json). Infomed is the Cuban national health information network under sld.cu. A third script walked the live listing pages of files.sld.cu/dne and files.sld.cu/sida as HTML (sld3.py, sld3.json) and sent a HEAD request to every yearbook file on the DNE listing (sld4.py, sld4.json). No file was opened.

### Hosts that still give no answer
- NIC. For www.minsa.gob.ni and mapasalud.minsa.gob.ni the TLS handshake ends with an unexpected end of file (SSLEOFError). Round one read www.minsa.gob.ni and mapasalud.minsa.gob.ni through Wayback (notes line 592). No change.
- HND. sshome.salud.gob.hn has no DNS record. piep.sefin.gob.hn fails certificate verification, TLS chain not verifiable, as in round one (notes line 582). portalunico.iaip.gob.hn returns HTTP 403 with the page title "Just a moment...", a browser challenge page. Round one recorded HTTP 403 for portalunico.iaip.gob.hn from curl (notes line 561). The transparency portal is BLOCKED. Round two did not work around the browser challenge on the transparency portal and sends no further request to portalunico.iaip.gob.hn.
- JAM. nfpb.gov.jm, jamaicaccm.org, ccmjamaica.org, jccm.org.jm, jamaicaccm.com and jccmjamaica.org have no DNS record. data.gov.jm resets the connection. rgd.gov.jm fails certificate verification, TLS chain not verifiable. No change from round one (notes line 646).
- PAN. www.inec.gob.pa times out on connection, as in round one (notes line 465).
- PRY. www.ine.gov.py has no DNS record, as in round one (notes line 396).
- CUB. www.onei.gob.cu and onei.gob.cu time out on connection. In round one the ONEI host names had no DNS record (notes line 863), so the ONEI names now resolve while the ONEI server does not answer. www.sld.cu still has no DNS record.

### Infomed hosts now reachable (CUB)
Round one found files.sld.cu, temas.sld.cu, bvscuba.sld.cu and instituciones.sld.cu giving no answer and read the Infomed hosts through Wayback only (notes line 863). In round two files.sld.cu returns HTTP 200 with the title "Ficheros del Portal de Infomed". temas.sld.cu/vihsida returns 200 ("ITS-VIH/sida"). instituciones.sld.cu returns 200 ("Portales institucionales"). bvscuba.sld.cu returns the default page of an Apache web server.
- DNE file listing (files.sld.cu/dne, the MINSAP statistics directorate, MINSAP being the Cuban health ministry). The live listing runs to 37 pages and links 171 files. Of the 171 live files, 36 are absent from the round-one Wayback list of 382 file rows (cub_dne_files.txt, notes line 869). Three of the 36 files absent from the Wayback list are yearbook workbooks. Anuario-estadistico-salud-.2004.xls, 940,544 bytes, last modified 28 April 2026. Anuario-estadistico-salud-2005.xls, 801,792 bytes, last modified 11 August 2025. Anuario-estadistico-salud-2024.xlsx, 500,936 bytes, last modified 17 November 2025. The 33 files absent from the Wayback list that are not yearbooks comprise six manuals for statistical reporting (file names carrying "SIE"), two coding lists, a digital health regulation, 19 conference posters, a dental manual and a correction to the dental manual, a report on surgery and anaesthesia, an English indicators leaflet for 2009 and a bulletin from March 2009. No file name absent from the Wayback list mentions HIV. NEGATIVE for the 33 files that are not yearbooks.
- Live yearbook workbooks. The live DNE listing links a yearbook workbook for 1998, 2004-2013 and 2017-2024, with two files for 2021, and every workbook answers HEAD 200. Workbooks for 1999-2003 and 2014-2016 are absent. Round one listed no workbook for 1999-2005, 2014-2016 or 2024 (notes line 871), so the live listing adds 2004, 2005 and 2024. Whether the MINSAP yearbooks give HIV new diagnoses by province stays NOT VERIFIED (notes line 873).
- HIV file listing (files.sld.cu/sida). The live sida listing runs to 17 pages and links 158 files. Only a photograph of a 2018 meeting of health promoters is absent from the round-one Wayback list (cub_cdx_sidafiles.txt, notes line 881). NEGATIVE.
- HIV portal (temas.sld.cu/vihsida). The live home page of temas.sld.cu/vihsida links pages on the national strategy, research articles, news and links to UNAIDS data, and no statistics page. NEGATIVE as a series, as in round one (notes line 882).

### What the retries change
- CUB. files.sld.cu is now a live route, so the DNE yearbook workbooks need no Wayback copy. The open yearbook workbooks now cover 1998, 2004-2013 and 2017-2024. Whether the MINSAP yearbook workbooks add to the panel still depends on whether HIV appears by province. Round one proposed the Wayback copy of the 2023 workbook as the first Cuban download (notes line 900). The first Cuban download candidate changes to the live 2024 workbook, listed below.
- HND. The 403 from portalunico.iaip.gob.hn is a challenge page, so the transparency portal moves from REACH FAILURE to BLOCKED.
- NIC, JAM, PAN and PRY hosts, and the ONEI host names in CUB, stay REACH FAILURE with no change. Round two sends no further retry to the REACH FAILURE hosts.

### Downloads to ask Jason about
- Anuario-estadistico-salud-2024.xlsx, files.sld.cu/dne, 500,936 bytes, the MINSAP health yearbook workbook for 2024, to see whether HIV appears by province. The 2024 workbook replaces the round-one candidate, the Wayback copy of the 2023 workbook.

## ROUND TWO. crt.sh, DHIS2 host retries and the UNAIDS 2026 estimates round, LAC entries (6 October 2026)

### Method
- crt.sh retry. One query for host names containing "dhis" under the BLZ country domain (.bz) was sent to crt.sh, a public search of TLS certificate logs. After the HTTP 502 reply the crt.sh retry stopped, so the planned queries for sisnu, siis and hmis were not sent (crt_retry1.json).
- DHIS2 host retry. dhis_retry2.py requested the root page of dhis.minsa.gob.pa, sis.minsa.gob.pe, sis.mpps.gob.ve and hacu.health.gov.tt with a timeout of 40 seconds and TLS verification on (dhis_retry2.json). DHIS2 is the open health information software used by many health ministries. dhis_retry2.py requested the sub-paths /dhis/ and /dhis2/ and the DHIS2 login settings page /api/loginConfig only on a host whose root page answered.
- UNAIDS release check. The UNAIDS fact sheet page, the core epidemiology slides page and the document page of the UNAIDS estimates spreadsheet were read as HTML. HEAD requests went to the estimates spreadsheet, the fact sheet PDF and the slides file (unaids_2026_pages.json, unaids_2026_heads.json). No file was opened. A read-only pandas read of the panel and of the raw exports in data/raw/unaids gave the years held (unaids_panel_range.json).

### Results
- crt.sh. HTTP 502 after 14 seconds. crt.sh stays UNAVAILABLE on 6 October 2026, as in round one (notes line 1529). The certificate-log search for dhis, sisnu, siis and hmis stays NOT RUN.
- dhis.minsa.gob.pa (PAN). Connection timeout. sis.minsa.gob.pe (PER). Connection reset by the server. sis.mpps.gob.ve (VEN). The server ends the TLS handshake with the alert TLSV1_ALERT_INTERNAL_ERROR. hacu.health.gov.tt (TTO). Connection timeout. No root page answered, so no sub-path was requested. The errors for the PAN, PER, VEN and TTO hosts match round one (notes lines 1535 to 1538). REACH FAILURE.
- UNAIDS estimates spreadsheet. The document page carries the title "HIV estimates with uncertainty bounds 1990-2025" and links two workbooks, HIV_estimates_from_1990-to-present_0.xlsx and HIV_estimates_from_1990-to-present_1.xlsx. The _0 and _1 workbooks have the same size, 6,165,844 bytes, and were last modified on 27 July 2026, seven minutes apart. The document page says the estimates spreadsheet was "updated 27 July 2026".
- UNAIDS fact sheet. The fact sheet page reports data from "172 countries reporting to UNAIDS for the year 2025" and says the country data are on aidsinfo.unaids.org "as of 27 July 2026". The fact sheet PDF (2026_UNAIDS_Global_HIV_Factsheet_en.pdf, 265,758 bytes) was last modified on 27 July 2026. The core epidemiology slides (2026_core-epidemiology-slides_en.pptx, 279,227 bytes) were last modified on 22 September 2026.
- Panel position. The panel holds 49,127 unaids_aidsinfo rows for 2000-2024, all with the retrieved_at date 5 September 2026. The retrieved_at date records the connector run. The 146 raw AIDSinfo exports in data/raw/unaids carry file dates of 18 July 2026, nine days before the UNAIDS release of 27 July 2026. No raw export holds a value for 2025. Of the 95 exports with one column per year, 89 end at 2024, three at 2023, two at 2019 and one at 2016. A further 51 exports give only a column headed "Most recent data as of 2024".
- Additive test. NEWER ROUND. The UNAIDS 2026 estimates round adds the year 2025 for every country that reports to UNAIDS. The NEWER ROUND marker for unaids_aidsinfo covers every region in the panel, not only LAC. Whether the 2026 round also changes the unaids_aidsinfo figures for 2000-2024 is NOT VERIFIED, because the UNAIDS pages read in round two give no statement on revisions to earlier years.

### What round two changes
- crt.sh stays UNAVAILABLE. The search for DHIS2 hosts in LAC still rests on the DNS guesses and web leads of round one (notes lines 1530 and 1531).
- dhis.minsa.gob.pa, sis.minsa.gob.pe, sis.mpps.gob.ve and hacu.health.gov.tt stay REACH FAILURE. Whether dhis.minsa.gob.pa, sis.minsa.gob.pe, sis.mpps.gob.ve or hacu.health.gov.tt runs DHIS2 stays NOT VERIFIED (notes line 1581). Round two sends no further request to the PAN, PER, VEN and TTO hosts.
- UNAIDS. The unaids_aidsinfo rows are one estimates round behind in every region. A fresh export from aidsinfo.unaids.org would add 2025 and would show whether the figures for earlier years changed.

### For Jason to decide
- Whether to re-export the 146 AIDSinfo files from aidsinfo.unaids.org and rerun the unaids_aidsinfo connector. The re-export and the connector run are for Jason to carry out.
- Whether to download HIV_estimates_from_1990-to-present_0.xlsx (unaids.org, 6,165,844 bytes) to compare the 2026 round with the panel figures for 2000-2024 before the re-export.

## ROUND TWO. Peru ENDES and the identity of HND_2019_MICS, LAC entries (6 October 2026)

### Method
- HND_2019_MICS. The World Bank microdata catalogue entry for HND_2019_MICS_v01_M was read as NADA catalogue JSON and as HTML, with the related-materials and get-microdata pages (hnd_mics1.py, hnd_mics1.json). NADA is the catalogue software behind the World Bank microdata library. The saved round-one copy of the INE Honduras databases page (hn_ine_bases-de-datos.html) was searched for the survey name. INE Honduras is the national statistics institute. No file was opened, and no request went to mics.unicef.org or to the UNICEF file store linked from the World Bank page.
- Peru ENDES. The INEI ENDES pages were read as HTML (per_endes1.py to per_endes4.py, per_endes1.json to per_endes4.json). INEI is the Peruvian statistics institute, and ENDES (Encuesta Demográfica y de Salud Familiar) is the continuous DHS survey run by INEI. HEAD requests went to the newest report files. No file was opened.

### HND_2019_MICS
- The World Bank entry HND_2019_MICS_v01_M carries the title "Multiple Indicator Cluster Survey 2019", the subtitle "Round 6" and the alternative title "MICS 2019", names UNICEF as the authoring entity, and sends data requests to mics.unicef.org. The World Bank metadata are version 01 of 27 July 2023. The related-materials page links a Spanish survey findings report and a Spanish file of statistical snapshots on the UNICEF file store.
- The INE Honduras databases page names one 2019 survey under a joint title, "ENDESA/MICS 2019, Encuesta Nacional de Demografía y Salud", and links the SPSS file BasesdatosENDESA2019.zip (notes line 566). The round-one searches of the World Bank and IHSN catalogues found no other MICS identifier for Honduras in 2019 (mics_nat_lac.json).
- Identity. HND_2019_MICS and the INE Honduras ENDESA 2019 are one survey, published by INE Honduras under the joint name ENDESA/MICS 2019 and catalogued by the World Bank as MICS round six. The round-one entry NOT VERIFIED (notes line 1501) becomes VERIFIED. DUPLICATE of the round-one ENDESA 2019 entry, with HIV knowledge and testing questions only (notes line 566). NOT ADDITIVE to panel indicators.
- The INE Honduras ENDESA dashboard covers the gender and citizen security module for 2019, 2012 and 2006 only. NEGATIVE for HIV.

### Peru ENDES
- Microdata portal. proyectos.inei.gob.pe/microdatos/ returns HTTP 200, but the portal page runs the survey query and the documentation query by script, so the HTML lists no survey. The survey years held on the INEI microdata portal stay NOT VERIFIED.
- Main reports. The ENDES home page and the results page link the national main report for 2016 to 2023. INEI also lists department reports for 2000 and 2009-2023 (departamentales.asp). The 2023 department listing page needs the Flash plug-in and links no PDF, and the directory /endes/2023/ returns HTTP 403. The files inside the department reports stay NOT VERIFIED.
- Report on noncommunicable and communicable diseases. The ENDES health page (salud.asp) links an annual report titled "Enfermedades no transmisibles y transmisibles" for every year from 2013 to 2023. The 2023 report (ENFERMEDADES_ENDES_2023.pdf) is 59,609,235 bytes. A zip with the same name (ENFERMEDADES_ENDES_2023.zip, 4,713,177 bytes, last modified 23 May 2024) sits beside the 2023 report. INEI also lists department versions of the disease report for 2019-2023. Whether the ENDES disease report gives HIV testing by department is NOT VERIFIED from the HTML.
- Budget programme indicators. The ENDES budget programme page (ppr.asp) links the annual report "Principales Indicadores de Resultados de los Programas Presupuestales" from a baseline edition onward, with annex files packed as zip or rar files, and the older rar files carry "EXCEL" in the file name. The newest files are the 2023 annual report (17,937,974 bytes, last modified 20 March 2024) with Anexos_2023.zip (4,372,982 bytes), and the report for the first half of 2024 (195,920,370 bytes, last modified 23 August 2024) with Anexos.zip (4,561,750 bytes). Anexos_PPR_2017_2022.zip (4,152,538 bytes) holds the annexes for 2017-2022. The text of the budget programme page names no HIV indicator. Whether the budget programme annexes carry HIV testing by department is NOT VERIFIED.
- ENDES after 2023. The INEI pages read link no ENDES report for 2024 or 2025 beyond the report for the first half of 2024. NOT VERIFIED whether INEI publishes later ENDES reports on another host.
- Additive test. Self-reported HIV testing from ENDES would be a new survey indicator for the panel (notes line 1505). Department figures would be ADDITIVE AT admin1 if Jason adopts the indicator. POSSIBLY ADDITIVE, GRADE 1 if the ENDES annex files hold HIV rows.

### What round two changes
- HND. HND_2019_MICS needs no separate entry, because the World Bank MICS entry and the INE Honduras ENDESA 2019 describe one survey.
- PER. The ENDES search moves from "not yet checked" (notes line 276) to a list of open INEI report files up to the first half of 2024. Whether the ENDES annexes carry HIV testing by department still needs one file opened.

### Downloads to ask Jason about
- Anexos_2023.zip, proyectos.inei.gob.pe/endes/2023/ppr/, 4,372,982 bytes, the annexes of the ENDES budget programme report for 2023, to see whether HIV testing appears by department.
- ENFERMEDADES_ENDES_2023.zip, proyectos.inei.gob.pe/endes/2023/SALUD/, 4,713,177 bytes, the companion zip of the ENDES disease report for 2023, to see whether HIV testing appears by department.

## ROUND TWO. Panama yearbook mortality tables and the Haiti MSPP publications library, LAC entries (6 October 2026)

### Method
- PAN. The saved MINSA yearbook pages for 2019 to 2022 (pan_anuario_2019.html to pan_anuario_2022.html, pan_anuarios_rows.json) were searched for table titles on deaths and causes of death and for the words VIH and SIDA. HEAD requests went to the PDF and XLSX files of the yearbook tables of leading causes of death (pan_causes_heads.json). No file was opened. A read-only pandas read of the panel gave the PAN death indicators held.
- HTI. One GET of the MSPP publications page, www.mspp.gouv.ht/publications (hti_mspp_r2.json). MSPP is the Haiti health ministry. Then GETs of the publications search for "statistique", "Riposte", "Rapport Statistique", "Annuaire", "VIH", "SIDA", "PNLS" and "SISNU", every result page, and of the first 16 result pages of the "Bulletins" category (hti_mspp_r2s.json, hti_mspp_r2c.json). HEAD requests went to the statistical reports, the statistical yearbooks, the PNLS information sheets and bulletin no 22 (hti_mspp_r2h.json). PNLS is the national HIV programme inside MSPP. No file was opened.

### Results, Panama
- Yearbook tables. The yearbook pages for 2019 to 2022 name SIDA only in the title of the AIDS case table (notes line 1558), and no yearbook page contains the word VIH. Every yearbook from 2019 to 2022 has a table of the ten leading causes of death nationally and a table of the five leading causes of death by province and indigenous comarca, an indigenous territory with the rank of a province. The cause names sit inside the table files, so whether HIV ranks among the leading causes stays NOT VERIFIED (notes line 1560).
- File sizes (HEAD, all HTTP 200). The 2022 XLSX files, last modified on 18 June 2025, read 55,036 bytes for the ten leading causes and 46,148 bytes for the five leading causes by province. The XLSX files of earlier years read 27,842 and 45,195 bytes for 2019, 26,321 and 53,177 for 2020, and 26,578 and 43,580 for 2021.
- Panel position. The panel holds PAN aids_deaths from unaids_aidsinfo for 2000-2024 and from who_gho for 2000-2025, national figures only, with no admin1 row.
- Additive test. A table of leading causes names HIV only where HIV ranks among the leading causes, so any province coverage would be partial. Registered deaths from HIV are a count from death certificates, a different measure from the modelled aids_deaths of UNAIDS and WHO. POSSIBLY ADDITIVE AT admin1 if HIV appears in the province tables and Jason adopts registered HIV deaths as an indicator. The class sweep of registered causes of death waits for Jason's decision.

### Results, Haiti
- Library size. The MSPP publications page reports 5,928 publications. Round one listed 735 files from the live publications list (hti_mspp_pubs.txt, notes line 824) and found the older HIV files through the Wayback Machine. The publications search reaches the older files on the live MSPP host.
- Rapport Statistique 2025. The newest publication on the first page of the MSPP library is dated 25 April 2026, and the newest result of the search for "statistique" is dated 1 July 2025. The search for "SISNU" returns no result. The Rapport Statistique 2025, presented on 28 August 2026 according to the PAHO news item (notes line 1564), is absent from the MSPP library on 6 October 2026.
- Annual statistical reports. The live MSPP library holds the Rapport Statistique MSPP for 2013 (1,608,343 bytes), 2014 (2,548,364), 2015 (7,630,772), 2016 (4,684,286), 2017 (1,401,135), 2018 (1,823,662), 2020 (3,060,944), 2021 (2,756,588), 2022 (2,299,058) and 2023 (1,821,690). No report for 2019 appears. A second file for 2014 returns HTTP 404. The library also holds a presentation of the 2018 report (2,451,931) and the Annuaire Statistique for 2011 (file CGES.pdf, 1,974,197) and 2012 (1,783,208). Round one had the reports for 2004-2007 and the 2012 annuaire through the Wayback Machine (notes line 831) and the 2022 and 2023 reports live. Every MSPP file checked by HEAD in round two carries the Last-Modified date 4 June 2026, as in round one, so the Last-Modified header gives no publication date.
- Bulletin no 22. "Bulletin de Surveillance Epidemiologique VIH Sida No. 22 Decembre 2020", posted on 8 December 2020, 4,872,564 bytes. Round one ended the PNLS bulletin series at the December 2019 issue (notes line 826). No issue numbered 20 or 21 appears in the VIH or SIDA search results, and the December 2019 issue carries no number in the title.
- PNLS information sheets. "Statistiques de la Riposte" for October 2023 to March 2024 (file "feuillet info PNLS mars 2024", 166,671 bytes, listed in round one) and for October 2023 to September 2024 (file "Feuillet informatif Dec24VFP", 1,067,128 bytes, posted on 30 November 2024). The October to September period matches the US fiscal year used by PEPFAR. Whether the PNLS information sheets give department figures is NOT VERIFIED.
- Category labels. The MSPP library files 22 HIV surveillance bulletin files under the label "Rapports Choléra", including bulletin no 1, so a filter on the MSPP category labels would miss HIV files. Of the first 320 items in the "Bulletins" category, 305 are COVID-19 and cholera bulletins and situation reports, and 15 are health messages in Haitian Creole, health and environment bulletins, pharmaceutical bulletins with a list of licensed pharmacies, a bulletin of the Nord-Est health directorate, two human resources documents and a note on mpox. No title among the first 320 items names HIV. Items 321 to 1,142 of the "Bulletins" category were not listed.

### Additive test, Haiti
- The panel department rows for HTI come from pepfar_snu and pepfar_agency_snu and start in 2016 (notes line 856). Department HIV testing or diagnosis tables in the Rapport Statistique MSPP for 2013, 2014 and 2015 would be ADDITIVE AT admin1, and department tables in the reports for 2016-2023 would be a second source for department-years filled by PEPFAR. Whether the MSPP statistical reports carry HIV tables by department is NOT VERIFIED.
- National new diagnoses for 2020 in bulletin no 22 would be DUPLICATE of the PAHO dashboard, which holds 2018-2024 (notes line 852). Department tables in bulletin no 22 are NOT VERIFIED.

### What round two changes
- PAN. The HTML lists of the MINSA yearbooks give no HIV cause-of-death table. Checking whether HIV ranks among the leading causes of death needs one XLSX file opened.
- HTI. The MSPP annual statistical reports now run 2004-2007 through the Wayback Machine and 2011-2018 and 2020-2023 live. The PNLS bulletin series now runs to no 22 (December 2020). The Rapport Statistique 2025 is not yet posted. The Rapport Statistique MSPP 2013 becomes the first Haiti download candidate, the smallest report from before 2016, to see whether HIV appears by department.

### Downloads to ask Jason about
- PAN. The 2022 MINSA yearbook XLSX tables of the ten leading causes of death (55,036 bytes) and of the five leading causes by province and comarca (46,148 bytes), minsa.b-cdn.net.
- HTI. Rapport Statistique MSPP 2013, www.mspp.gouv.ht, 1,608,343 bytes.
- HTI. Bulletin de Surveillance Epidemiologique VIH Sida No. 22, www.mspp.gouv.ht, 4,872,564 bytes.

## ROUND TWO. Peru ENDES reports for 2024 and 2025 on gob.pe, LAC entries (6 October 2026)

### Method
- gob.pe is the web platform of the Peruvian government and carries the publication pages of INEI, the Peruvian statistics institute. One GET of the gob.pe JSON search endpoint (busquedas.json) asked for INEI publications matching "ENDES" and returned 60 publications, newest first. The first page held 25 results, and one result was empty (per_gobpe2.py, per_gobpe2_raw.json, per_gobpe2_rows.json).
- Six gob.pe publication pages were read as HTML, namely the ENDES reports for 2024 and 2025, the INEI reports on noncommunicable and communicable diseases for 2024 and 2025, the ENDES annual series for 1986-2025 and the ENDES 2026 survey page (per_gobpe3.py, per_gobpe4.py, per_gobpe3.json, per_gobpe4.json). HEAD requests gave the size and date of the 14 linked report files. No file was opened.

### ENDES 2025
- INEI published the national and department report "Perú: Encuesta Demográfica y de Salud Familiar 2025 - Nacional y Departamental" on gob.pe on 19 June 2026. The gob.pe page links the full report on www.inei.gob.pe (publicaciones_digitales/Est/Lib2089/libro.pdf, 172,255,089 bytes, last modified 18 June 2026), a zip of statistical tables, databases and method documents (Lib2089/informacion_complementaria.zip, 93,329,501 bytes, last modified 21 July 2026) and a summary PDF on cdn.www.gob.pe (2,895,464 bytes).
- The 2025 disease report "Perú: Enfermedades No Transmisibles y Transmisibles, 2025" appeared on the same day. The gob.pe page text for the 2025 disease report says the ENDES health questionnaire ran from January to December 2025 in a sample of 36,750 dwellings and reached 30,226 women and men aged 15 and over. The gob.pe page links the full report (Lib2090/libro.pdf, 48,193,550 bytes, last modified 18 June 2026), a zip of statistical tables, databases and method documents (Lib2090/informacion_complementaria.zip, 11,496,607 bytes, last modified 18 June 2026) and a PDF of main indicators (2,735,302 bytes).
- The ENDES annual series "Perú: Series anuales de principales indicadores de la ENDES, 1986-2025" appeared on 19 June 2026 as well. The page text describes 11 chapters and more than 60 statistical tables. The gob.pe page links the PDF (4,429,639 bytes) and a zip of the statistical tables (750,421 bytes).
- No gob.pe page text read in the check names HIV, under the Spanish terms VIH or SIDA or the English term HIV. Whether the 2025 reports and zips carry HIV tables is NOT VERIFIED.

### ENDES 2024 and ENDES 2026
- The ENDES 2024 report and the 2024 disease report appeared on gob.pe on 28 May 2025. The ENDES 2024 report (Lib2016/libro.pdf) is 176,858,961 bytes, with a zip of tables, databases and method documents of 112,022,961 bytes. The 2024 disease report (Lib2017/libro.pdf) is 44,185,410 bytes, with a zip of 11,026,238 bytes. The 2024 reports and zips were all last modified on 27 May 2025.
- The gob.pe page for ENDES 2026, published on 11 February 2026, links a technical sheet and an anaemia method document only. ENDES 2026 results are not yet published.
- The gob.pe search also shows the publishing calendar. The ENDES annual series to 2023 appeared on 23 May 2024, the 2024 editions on 28 May 2025 and the 2025 editions on 19 June 2026.

### Correction to the round-two Peru entry
- Notes line 1694 recorded no ENDES report for 2024 or 2025 on the INEI pages read, beyond the report for the first half of 2024. The ENDES pages on proyectos.inei.gob.pe do not list the 2024 and 2025 reports, but INEI posts the 2024 and 2025 reports under www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/ and lists the reports on gob.pe. The open question on notes line 1694 becomes VERIFIED. ENDES national and department reports run to 2025.

### Additive test
- Self-reported HIV testing by department from ENDES remains a candidate new indicator for Jason to decide (notes line 1695). The 2024 and 2025 reports extend the candidate series by two years. Whether the disease report tables give HIV testing by department is NOT VERIFIED. POSSIBLY ADDITIVE AT admin1, GRADE 1, if Jason adopts the indicator.

### What round two changes
- PER. The ENDES file list now runs to the 2025 reports published on 19 June 2026. The newest ENDES disease report zip replaces the 2023 zip as the first Peru download candidate.

### Downloads to ask Jason about
- Lib2090/informacion_complementaria.zip, www.inei.gob.pe, 11,496,607 bytes, the tables of the 2025 ENDES disease report, to see whether HIV testing appears by department. The 2025 zip replaces ENFERMEDADES_ENDES_2023.zip in the download list (notes line 1703).
- 8284167-cuadros-estadisticos.zip, cdn.www.gob.pe, 750,421 bytes, the tables of the ENDES annual series for 1986-2025, to see whether a national HIV testing series appears.

## ROUND TWO. Trinidad and Tobago HIV dashboards and the Honduras SESAL HIV reports, LAC entries (6 October 2026)

### Method
- TTO. The health ministry home page, the NACC pages and the page of the HIV/AIDS Coordinating Unit on health.gov.tt were read as HTML and searched for Power BI links and report files (tto_pbi1.py, tto_pbi2.py). NACC is the National AIDS Coordinating Committee of Trinidad and Tobago. The DHIS2 community forum post of 20 November 2025 (notes line 1565) was read as Discourse JSON, the format of the forum software (tto_pbi3.py, tto_pbi3.json). One web search asked for a Trinidad and Tobago HIV dashboard in Power BI. No request went to hacu.health.gov.tt.
- HND. ASONAPVSIDAH, the national association of people living with HIV in Honduras, runs a Wix site. The Wix sitemaps listed 75 pages and posts (hnd_aso3.py). Every post whose address names the SESAL HIV statistical report, a post on the 2025 HIV situation and the statistics category page were read as HTML (hnd_aso4.py, hnd_aso4.json). SESAL is the Secretaría de Salud, the Honduras health ministry. The SESAL document API on www.salud.gob.hn was read again for units 1-120, where round one read units 1-60 (hnd_sesal2.py, hnd_sesal2.json). No file was opened.

### TTO dashboards
- No page read on health.gov.tt carries a Power BI link or an embedded frame. The NACC reports page lists five documents, namely a green paper on HIV policy, the amalgamated NCPI for 2021, a workplace HIV policy, an operational plan for 2013-2014 and the national strategic plan for 2013-2018. NCPI is the National Commitments and Policy Instrument, the UNAIDS policy questionnaire. The HIV/AIDS Coordinating Unit page links an HIV rapid testing procedure of October 2025 only. The NACC media page timed out after 40 seconds.
- The DHIS2 forum post holds two messages and no Power BI link. The post says DHIS2 entries fill Power BI dashboards, giving the ministry instant access to national HIV testing trends. The wording describes an internal ministry tool.
- The TTO HIV dashboards stay NOT VERIFIED as public. No public address was found. NEGATIVE for a public TTO HIV dashboard on 6 October 2026.

### Honduras SESAL HIV reports
- ASONAPVSIDAH posts the SESAL report "Informe Estadístico de la Epidemia de VIH en Honduras" for October 2021, December 2021, March 2022, June 2023, September 2023 and December 2023, posted between 31 October 2021 and 15 March 2024. The posts for 2021 and 2022 carry the report as images with no text. The posts for 2023 carry a text summary of the SESAL report and images. No post links a PDF.
- The post for December 2023, posted on 15 March 2024, gives 42,249 notified HIV cases from 1985 to December 2023, of which 26,361 were advanced infection and 15,888 asymptomatic HIV, and names eight departments holding 85.7% of notified cases. The round-one search snippet with the 42,249 cases (notes line 572) is now VERIFIED against the ASONAPVSIDAH text, a second-hand copy of the SESAL report.
- A post of 10 September 2026 summarises the SESAL "Boletín Epidemiológico de VIH en Honduras 2025", made by the SESAL health surveillance unit and covering all 53 epidemiological weeks of 2025. The post gives 1,191 HIV cases notified in 2025, with 866 men and 325 women, and 854 asymptomatic cases and 337 cases of advanced infection. The post gives 44,620 cases registered from 1985 to 2025. The post says the cumulative counts differ between departments and shows the department counts in 16 images, which were not read.
- The SESAL document API returns 18 documents for units 1-120, the same count as round one (notes line 570), and no document names HIV. The SESAL HIV bulletin for 2025 is NOT FOUND on www.salud.gob.hn.
- Printed SIIS extracts. No ASONAPVSIDAH page read in the round names SIIS. Whether the SESAL HIV bulletins draw on SIIS is NOT VERIFIED. SIIS stays GATED, GRADE 3 (notes line 1578).

### Additive test, Honduras
- The panel holds HND new diagnoses from pepfar_snu for 2016-2025 by department and from global_fund for 2022-2025 at national level. The SESAL count of 1,191 cases notified in 2025 is a national figure for a year the panel already holds. NOT ADDITIVE at national level for 2025. The SESAL count covers all notified cases, and PEPFAR counts cover PEPFAR-supported sites only.
- Annual department counts from SESAL bulletins for years before 2016 would be ADDITIVE AT admin1. The post texts read give department shares and cumulative department counts only. Whether the SESAL bulletins carry annual department counts is NOT VERIFIED. GRADE 2 through the ASONAPVSIDAH copies, because the SESAL originals were not found.

### What round two changes
- TTO. The round-two question on the Power BI dashboards closes as NEGATIVE for a public dashboard.
- HND. The SESAL HIV statistical report series is now known for 2021-2023 through ASONAPVSIDAH copies, and a SESAL HIV bulletin for 2025 exists but is not posted on the SESAL site.

## ROUND TWO. REUNIS report map and the budget programme 0016 sheet, Peru, LAC entries (7 October 2026)

### Method
- The REUNIS HIV page saved in round one (reunis_vih.html) carries 20 Power BI publish-to-web links. Every link was matched to the link title and to the menu heading above the link (reunis_pbi_titles.json). The report key and the tenant, the Microsoft account holding a report, were decoded from every link address. Report metadata for the five reports titled "Indicadores CG" were requested from the Power BI public API (reunis_pbi1.py, reunis_pbi2.py).
- The REUNIS morbidity and budget pages were opened in the built-in browser, and the address of the embedded frame was read on every page (reunis_browser_obs.json). Tableau Public workbook metadata were read as JSON (reunis_tab1.py, reunis_tab1.json). On the Tableau Public sheet OGPPM_0016 the filter lists for region, product and indicator were read in the browser. No file was downloaded and no table was exported.

### Power BI links
- The 20 Power BI links are menu links. 11 links sit under the menu heading "Medicamentos" (medicines), eight under "Recursos Humanos" (human resources) and one under "Estado Nutricional" (nutrition), and the nutrition link sits inside an HTML comment. The medicines links cover six reports on medicine stock, availability, antimicrobial monitoring and consumption, and five reports titled "Indicadores CG" for 2022 to 2026. The REUNIS page does not expand the abbreviation CG. The human resources links cover staff availability and density, the rural health service, management agreements and staff development plans.
- No link title names HIV, AIDS, STI, antiretroviral treatment or PrEP. No Power BI link sits under the menu headings "Morbilidad" or "Presupuesto" (budget).
- The links belong to three tenants, with 16 links on the tenant 7905c1fc, the reports "Indicadores CG" for 2022, 2023 and 2024 on the tenant 34f32419, and the nutrition link on the tenant b4761cee.
- The Power BI routing endpoint answered HTTP 403 for all three tenants. For all five "Indicadores CG" reports the redirect host answered HTTP 403 and the primary API host for the South Central US region answered HTTP 401. The reports were not read by another tool. The content of the "Indicadores CG" reports is NOT VERIFIED.

### Morbidity and budget pages
- Round one found empty static content blocks on the REUNIS budget and morbidity pages (notes line 1553). In the browser a script adds one Tableau Public frame to every page read, and no page read embeds a Power BI report.
- "Morbilidad General" embeds the workbook "Morbilidad HIS", 12 sheets, last updated on 8 September 2026.
- "Atenciones de Consulta Externa" embeds the workbook "Atenciones_HisMinsa", 16 sheets, last updated on 30 September 2026.
- "Meta Física y Financiera" embeds the workbook "TABLERO_SEGUIMIENTO", seven sheets, last updated on 6 October 2026.
- "PPR: Indicadores de Desempeño" embeds the workbook "SegEval_PP_OGPPM", 11 sheets, last updated on 6 October 2026.
- "PP 0104" embeds the workbook "EJECUCION_DIGTEL", three sheets, last updated on 28 August 2026.
- "Cuentas de Salud (2002-2022)" embeds the workbook "Tablero_cuentas_de_salud", 33 sheets, last updated on 31 October 2025.
- No sheet title in the six workbooks names HIV. The workbook "SegEval_PP_OGPPM" holds one sheet per budget programme, and the sheet OGPPM_0016 covers programme 0016. Whether the morbidity workbook lists HIV among the diagnosis groups is NOT VERIFIED. The health accounts workbook shows no disease breakdown in the sheet titles, and HIV content in the health accounts workbook is NOT VERIFIED.

### Budget programme 0016 sheet
- The sheet OGPPM_0016 carries the banner "0016. TBC-VIH/SIDA", the TB and HIV budget programme of Peru. Round one named programme 0016 as the HIV target without reading the programme name from a data row (notes line 259). The MINSA dashboard now confirms the programme name.
- The region filter lists 26 regions and a national entry. The product filter lists five products and the specific result of the programme, a reduction in TB and HIV/AIDS illness and death. Product 3043969, people diagnosed with HIV/AIDS receiving comprehensive care, names HIV alone. Product 3043952 covers healthy family practices for HIV and TB prevention. Product 3043961, the high-risk population receiving information and preventive care, names no disease, and the indicator of product 3043961 is HIV screening. Two products cover TB alone.
- Product 3043961 carries indicator 073, HIV screening coverage in the high-risk population, as a percentage from HIS MINSA, the MINSA outpatient information system. Product 3043969 carries indicator 026, the percentage of men and women with HIV receiving antiretroviral treatment, from "DPVIH -BASE TAR", the treatment database of the MINSA HIV directorate. The indicator list for product 3043952 was NOT READ.
- For every region and product the sheet shows the opening budget (PIA), the modified budget (PIM) and accrued spending (devengado). The budget years run 2020-2025 for product 3043961 and 2021-2025 for product 3043969, and a regional chart shows 2018-2025. The indicator chart runs 2020-2026.

### Additive test, Peru
- The panel holds no PER row at admin1 for any indicator. The panel holds PER art_coverage_pct at national level from unaids_aidsinfo for 2010-2024 and from who_gho for 2000-2025, and PER domestic_hiv_spend at national level from unaids_gam_expenditure for 2020-2024.
- Regional ART coverage from the MINSA treatment database would be ADDITIVE AT admin1. Whether the denominator of indicator 026 matches the panel definition of art_coverage_pct is NOT VERIFIED.
- Regional programme 0016 budget for products 3043961 and 3043969 would be ADDITIVE AT admin1 as domestic HIV spending for 2018-2025. The MEF files of round one hold the same budget at full detail, at 6,776,006,081 bytes for 2012 and 10,237,853,250 bytes for 2024 (notes line 258). The REUNIS sheet gives a smaller route. GRADE 2, because the sheet is a dashboard and a table export from Tableau Public is a download needing Jason's permission.

### What round two changes
- The REUNIS question at notes line 1553 closes. The 20 Power BI links are menu links for medicines, human resources and nutrition, NEGATIVE for HIV by title, and the budget and morbidity pages embed Tableau Public workbooks.
- New candidate. The Tableau Public sheet OGPPM_0016 gives programme 0016 budget and two HIV indicators by region, POSSIBLY ADDITIVE AT admin1.

### Downloads to ask Jason about
- A table export of the Tableau Public sheet OGPPM_0016 (workbook SegEval_PP_OGPPM_17344697689330), all regions, products 3043961 and 3043969, size unknown.

## ROUND TWO. Retry of budget and data portals in MEX, BOL, ECU and TTO, and the Bolivian weekly bulletins, LAC entries (7 October 2026)

Method. A GET of the home page of nine hosts recorded in round one as unreachable or blocked and missing from the reachability retry of 6 October 2026 (retry1.py), with TLS verification on and a 40-second timeout (retry2.py, retry2.json). A second script read pages on www.minsalud.gob.bo as HTML (r2h_bol.py, r2h_bol.json, r2h_bol_cards.json) and sent HEAD requests for four linked files (r2h_bol_heads.json). No file was opened and no challenge page was worked around.

### Hosts
- MEX. www.transparenciapresupuestaria.gob.mx and nptp.hacienda.gob.mx time out on connection. Round one recorded no answer from the Hacienda budget sites on 5 October 2026 (notes lines 164 to 165). The route to the federal budget programme P016 stays REACH FAILURE, and round two sends no further retry to www.transparenciapresupuestaria.gob.mx or nptp.hacienda.gob.mx.
- BOL. datos.gob.bo returns HTTP 403 from nginx with the title "403 Forbidden", the same answer as in round one (notes line 434). snis.minsalud.gob.bo and siccaf.minsalud.gob.bo/snis/ time out on connection. www.economiayfinanzas.gob.bo, the site of MEFP (Ministerio de Economía y Finanzas Públicas, the Bolivian finance ministry), fails certificate verification, TLS chain not verifiable, where round one had no answer within 25 seconds. The SIGEP budget route therefore stays unreached (notes line 458). www.minsalud.gob.bo, the site of MSyD (Ministerio de Salud y Deportes, the Bolivian health ministry), now returns HTTP 200 with the title "Ministerio de Salud y Deportes de Bolivia - Institucional".
- ECU. www.datosabiertos.gob.ec and aplicaciones3.ecuadorencifras.gob.ec return HTTP 403 from Apache with the title "403 Forbidden" on the home page. Round one recorded HTTP 403 on the CKAN API, on the HTML search and on the BIINEC data bank (notes lines 332 to 334). The national open-data catalogue stays NOT enumerated, and round two sends no further retry to www.datosabiertos.gob.ec or aplicaciones3.ecuadorencifras.gob.ec.
- TTO. data.gov.tt returns HTTP 200 with the title "Data.gov.tt - Under Maintenance", as in round one (notes line 715). The Trinidad and Tobago open-data catalogue stays NOT enumerated.

### MSyD weekly epidemiological bulletins (BOL)
- Listing pages. The MSyD page "Boletines Epidemiológicos - 2026" lists 26 weekly bulletins for Semana Epidemiológica (SE, the epidemiological week) 03 to 38 of 2026, posted from 2026-01-25 to 2026-10-05, with 17 to 29 pages per bulletin. The first page of the MSyD listing "Boletines del Ministerio de Salud" links 101 files, namely 100 earlier bulletins titled "Parte Epidemiológico", posted from 2018-03-02 to 2020-03-03, and the bulletin for SE 27 of 2024. The listing runs to a second page, which was not read. The jdownloads category pages for the bulletins return HTTP 404, so the bulletins posted between March 2020 and January 2026 are NOT enumerated.
- Summaries. Every listing entry carries a summary paragraph written by MSyD. No summary on the 2026 page or on the first page of the earlier listing mentions VIH or SIDA. The summary for SE 27 of 2024 covers rabies, leptospirosis, severe dengue and COVID-19 and gives the bulletin a length of 19 pages. A round-one search snippet (UNVERIFIED, notes line 450) says the SE 27 bulletin of 2024 reports 1,630 HIV and AIDS cases to week 27. Whether the weekly bulletins hold an HIV table, and whether an HIV table splits cases by department, is NOT VERIFIED.
- Files (HEAD, none opened). "Boletin epidemiológico_38 2026.pdf", application/pdf, 888,761 bytes, Last-Modified 5 October 2026. "BoletinEpidemiologico_SE_27-2024.pdf", application/pdf, 1,559,078 bytes, Last-Modified 23 June 2026.
- HIV programme page. The MSyD page "Normas y Manuales Programa Nacional ITS/VIH/SIDA" links 11 files, namely two antiretroviral therapy guides for children, an antiretroviral therapy guide for adolescents and adults, an antiretroviral therapy guide for adults, a guide on preventing mother-to-child transmission of HIV and congenital syphilis, a guide on syndromic management of sexually transmitted infections, a guide on TB and HIV coinfection, care manuals for trans people and for gay and bisexual men and other men who have sex with men, the national norm for STI, HIV and AIDS care, and a title on severe obstetric morbidity. NEGATIVE as a data series.
- Budget files on the MSyD site (HEAD, none opened). "prespuesto ejecutado.pdf", the MSyD budget execution file, 239,354 bytes. "Fuentes de Financiamiento.pdf", the MSyD file on funding sources, 94,066 bytes. Whether the execution file or the funding file names the national STI, HIV and AIDS programme is NOT VERIFIED.

### Additive test (BOL)
- The panel holds no BOL new_diagnoses and no BOL admin1 rows (notes line 432). PAHO indicator 93 holds national BOL new diagnoses for 1995-2025 (notes line 773). A weekly bulletin gives counts for the year to date. A national count for a part of a year does not fit the annual panel, NOT ADDITIVE, and a national count for the last week of a year would duplicate PAHO indicator 93.
- An HIV table by department in the weekly bulletins would be ADDITIVE AT admin1, GRADE 2 (PDF tables). POSSIBLY ADDITIVE AT admin1, unopened.

### What round two changes
- BOL. The MSyD site answers again, and the weekly bulletins sit on www.minsalud.gob.bo, while the SNIS hosts still give no answer. The round-one assessment at notes line 453, a national series on hosts giving no answer, changes to a reachable route with HIV content NOT VERIFIED.
- MEX P016, BOL datos.gob.bo, BOL MEFP, the ECU catalogue and the TTO catalogue stay unreached or blocked. Round two records the MEFP host as TLS chain not verifiable and does not turn TLS verification off.

### Downloads to ask Jason about
- "Boletin epidemiológico_38 2026.pdf", www.minsalud.gob.bo, 888,761 bytes, to check for an HIV table by department.
- "BoletinEpidemiologico_SE_27-2024.pdf", www.minsalud.gob.bo, 1,559,078 bytes, to check the 1,630 cases in the round-one snippet.
- "prespuesto ejecutado.pdf", minsalud.gob.bo, 239,354 bytes, to check for an HIV programme line.

## ROUND TWO. Guyana parliament library and NAPS report, Guatemala open-data retry, and round-two items waiting on downloads or on gov.br, LAC entries (7 October 2026)

Method. The page reader r2h_bol.py read two pages on parliament.gov.gy as HTML (r2i_gy.json). A web search on 7 October 2026 looked for the 2023 annual report of NAPS (the National AIDS Programme Secretariat of the Guyana Ministry of Health). The browser pane loaded the datos.gob.gt home page once and waited 10 seconds (r2i_obs.json). No file was opened, nothing on a challenge page was clicked, and no challenge page was worked around.

### Guyana
- Documents-laid library. parliament.gov.gy/documents/documents-laid/ returns HTTP 403 with the title "403 Forbidden" in an ISO-8859-1 page. Round one recorded HTTP 200 for the parliament.gov.gy home page and HTTP 403 for www.parliament.gov.gy (notes line 720). The library holding the HIV policy document named in the round-one retry list (notes line 734) is BLOCKED, and round two sends no further retry to the documents-laid path.
- Site search. The parliament.gov.gy search for HIV (parliament.gov.gy/?s=HIV) returns HTTP 200 with the home-page title "National Assembly of the Parliament of Guyana | Parliament of Guyana", 104,627 characters and 217 links. No link names HIV or AIDS, and the word HIV is absent from the page text. The parliament.gov.gy search gives no route to the HIV policy document. NEGATIVE.
- NAPS annual report. The web search found no copy of the NAPS annual report for 2023. The closest result was "Guyana country report 2022 2023" on open.unaids.org, a report by UNAIDS (the Joint United Nations Programme on HIV/AIDS) on support from United Nations agencies to Guyana, not the NAPS annual report, and not opened. The figures of 94-72-87 against the 95-95-95 targets in round-one search text stay UNVERIFIED (notes line 726). NAPS annual reports NOT FOUND, and GRADE 3.5 stands.
- Health Statistical Bulletins 2004-2009. The Guyana bulletins for 2004 to 2009 exist only as six Wayback copies of PDF files of 121,002 to 2,578,762 bytes (notes line 725). Reading the bulletin content needs a download, so the HIV content stays NOT VERIFIED.

### Guatemala
- datos.gob.gt, the Guatemalan open-data catalogue on CKAN. On 7 October 2026 the browser pane showed the Cloudflare page "Just a moment..." with the text "Performing security verification" on the home page, unchanged after a 10-second wait. Round one saw the same Cloudflare page on the API URL after eight seconds (notes lines 314 to 315). BLOCKED. The catalogue stays NOT enumerated, and round two sends no further retry to datos.gob.gt.

### Brazil items waiting on gov.br
- The round-two budget checks for Brazil need requests to the federal budget SPARQL endpoint orcamento.dados.gov.br (notes line 1084) or to the transparency portal portaldatransparencia.gov.br. The Brazil budget checks cover the 2025 conflict of R$ 318,458,127 between SPARQL paid and portal paid for action 4370 (notes line 1091), the 2024 liquidated difference, state subtitles in the smaller actions of 2000-2007, other HIV or hepatitis sub-plans under action 20AL, and the sioplegis graph (notes lines 1261 to 1264). The retry of the COVIGSAL bulletin listing also sits on gov.br (notes line 1619).
- The current search rules place every gov.br host off-limits, so round two sends no request for the Brazil budget checks or for the COVIGSAL listing. Decisions for Jason, namely whether the search may query orcamento.dados.gov.br again, and which budget stage, liquidated or paid, a connector would read (notes line 1265).

### Round-two items waiting on downloads
- TTO. The content of the b20xxh28 files and the budget year of 2562.pdf (notes line 715). The b20xxh28 files are Head 28 Ministry of Health budget files from the Wayback CDX, between 23,595 and 647,283 bytes (notes line 706). 2562.pdf is 1,069,964 bytes (notes line 705). The first candidate stays BG2024_MOH.pdf, 1,469,801 bytes, to settle the structure of the HIV line (notes line 709).
- GUY. The Health Statistical Bulletins 2004-2009 above.
- SUR. ODIN 5.1-5.2, a docx of 33,538 bytes on disease prevalence and other health statistics for 2015-2021 (notes line 744). A cause table in Demographic Data 2018-2021, 4,304,699 bytes (notes line 742). The HIV line in the health budget law S.B. 2014 no. 138, 599,575 bytes (notes lines 757 and 760).
- BLZ. HIV-stats-report-for-2018.pdf, 1,541,580 bytes, for district and ART tables (notes line 805). APPROVED ESTIMATES 2018-19, 4,974,772 bytes, from the Wayback copy on cdn.gov.bz, for an HIV or NAC line (notes line 807). Round one left the Belize question on district and ART tables and the Belize question on a budget line open for round two (notes line 815).
- None of the TTO, GUY, SUR or BLZ items can move without a download, so round two records the items as waiting on Jason and sends no request for the files.

## ROUND TWO. Venezuela budget-office and gazette hosts, Gaceta Oficial searches, and the Cuba round-two status, LAC entries (7 October 2026)

Method. A GET of the home page over http and https for onapre.gob.ve, www.gacetaoficial.gob.ve and historico.tsj.gob.ve, with TLS verification on and a 40-second timeout (r2j_ven.py, r2j_ven.json). Every ONAPRE and Gaceta Oficial request on the first attempt failed at name resolution, while a DNS lookup straight after returned the round-one addresses (r2j_ven_dns.json), so a second attempt went to onapre.gob.ve and www.gacetaoficial.gob.ve (r2j_ven_b.py, r2j_ven_b.json). Three HTML search GETs went to the Gaceta Oficial filter page (r2j_gaceta.py, r2j_gaceta_b.py), followed by a HEAD and a GET of one gazette view page (r2j_gaceta_head.json, r2j_gaceta_view.json). No gazette PDF was opened.

### Venezuela
- ONAPRE (Oficina Nacional de Presupuesto, the national budget office). onapre.gob.ve times out on connection over http and https on the second attempt, as in round one (notes line 905). Every ONAPRE file stays a Wayback copy (notes line 932). REACH FAILURE, and round two sends no further retry to onapre.gob.ve.
- TSJ (Tribunal Supremo de Justicia, the supreme court). historico.tsj.gob.ve times out on connection over http and https. REACH FAILURE, and round two sends no further retry to historico.tsj.gob.ve.
- Gaceta Oficial. www.gacetaoficial.gob.ve now answers HTTP 200 over http with the title "Calendario de Gacetas", while https times out. The home page carries a filter form for gazette number, date, issuing body, title and text, where round one found no answer (notes line 944).
- Search for VIH. The text filter for VIH, described on the form as a search of gazette texts and summaries, returns 26 issues, all ordinary issues, dated from 2012 to 2026 (12 in 2012, one in 2013, one in 2021, five in 2025 and seven in 2026). The view page of the most recent issue, no. 43.460 of 16 September 2026, lists the summary of every act in the issue and links one PDF file. No summary entry on the view page for no. 43.460 mentions VIH, SIDA or antiretroviral drugs, so the match probably lies in the PDF text, and which act in no. 43.460 mentions HIV is NOT VERIFIED. The view pages of the 25 earlier issues were not read.
- Search for the budget law. The title filter for presupuesto returns no issue, because the listing gives every issue the generic title "GACETA OFICIAL" or "República Bolivariana de Venezuela". The text filter for the full phrase "Ley de Presupuesto para el Ejercicio Económico Financiero" also returns no issue. The summary of no. 43.460 does contain the shorter phrase "Ley de Presupuesto y sus modificaciones", inside a delegation of payment authority. Whether the gazette index holds the budget laws after 2016 is NOT VERIFIED, and the search found no budget-law issue.
- Additive test. The ONAPRE Wayback files already hold the budget law texts for 2000-2016 (notes line 944). A PNSIDA line in a budget law after 2016 would extend the allocation series named at notes line 964, never as domestic_hiv_spend. Reading any gazette text needs a PDF download. NOT VERIFIED.

### Cuba
- Round one asked round two to retry onei.gob.cu and files.sld.cu live (notes line 900). The reachability retry of 6 October 2026 covered onei.gob.cu and files.sld.cu. The ONEI hosts time out and stay REACH FAILURE (notes line 1636). files.sld.cu answers HTTP 200 (notes line 1639), and the first Cuban download candidate became the live 2024 MINSAP yearbook workbook (notes line 1651). No Cuban round-two item remains open beyond downloads.
- The Cuban budget-law candidate goc-2025-o99_1.pdf on gacetaoficial.gob.cu, 852,803 bytes (notes line 900), still needs a download.

### What round two changes
- VEN. The Gaceta Oficial host moves from REACH FAILURE to reachable over http, with a searchable index of ordinary issues. The gazette route to an HIV budget line after 2016 stays NOT VERIFIED. ONAPRE and the TSJ archive stay REACH FAILURE.
- CUB. No change beyond the retry section at notes line 1626.

## ROUND TWO STOP CHECK. The ACCESS_LADDER §8e stop rule applied to the LAC round-two passes (7 October 2026)

Method. ACCESS_LADDER §8e gives the stop rule "Stop when a pass produces only sources you already know how to classify." The ladder adds "a pass that changes the rule is a pass that was worth running". The stop check lists every round-two outcome recorded in the notes from line 1595 to line 1906, names the round-one class of every outcome, and asks whether any outcome needed a class round one did not have, or changed a rule about what counts as a source. The stop check sent no web request and opened no file.

### Source classes known from round one
- Health ministry reports, yearbooks and bulletins, read country by country, for example Haiti from notes line 817 and Cuba from notes line 860.
- Household survey reports (class sweep at notes line 1411).
- Budget documents, namely the MEF expenditure files of Peru (notes line 258) and budget laws printed in official gazettes in Suriname (notes line 757) and Cuba (notes line 887).
- Dashboards on government sites, with a Tableau Public workbook of the Ecuador statistics office (notes line 345) and Power BI links on REUNIS, the statistics portal of the Peruvian health ministry (notes line 1552).
- Routine health information systems (class sweep at notes line 1524).
- Regional health bodies (class sweep at notes line 1267).
- Statistics office tables hosted on dataZoa, a commercial data-hosting service, with the STATIN tables of HIV disease deaths in Jamaica (notes lines 649 to 654).
- Sources already in the panel, for example the unaids_aidsinfo rows.

### Round-two outcomes by class
- Regional health bodies. The MERCOSUR HIV bulletins of 2012 and 2015 on gub.uy, POSSIBLY ADDITIVE, unopened (notes line 1604). Known class.
- dataZoa tables. The class sweep found a second LAC publisher, ABS (the Suriname statistics office), with no health table (notes line 1613). Whether the other 21 countries publish through dataZoa is NOT RESOLVED (notes line 1615). Known class.
- Health ministry reports, yearbooks and bulletins. The Cuban DNE yearbook workbooks live on files.sld.cu (notes line 1646), the Panama MINSA yearbook tables (notes line 1730), the Haiti MSPP reports and PNLS bulletins (notes line 1731), the Bolivian weekly bulletins on www.minsalud.gob.bo (notes line 1856), and the SESAL HIV reports of Honduras through copies posted by ASONAPVSIDAH, the national association of people living with HIV (notes line 1788). Round one already cited an ASONAPVSIDAH post in the Honduras section (notes line 572), so a copy posted by a civil-society association was already a known route. Known class.
- Household surveys. The INEI ENDES reports for Peru up to the 2025 reports published on 19 June 2026 (notes line 1762), and the finding of notes line 1698, where HND_2019_MICS and the INE Honduras ENDESA 2019 describe one survey. Known class.
- Budget documents. The Venezuelan Gaceta Oficial index, now reachable over http, as a route to budget laws after 2016 (notes line 1905), and the Brazil budget checks waiting on a gov.br decision (notes line 1879). Known class.
- Dashboards. The TTO HIV dashboards, NEGATIVE for a public dashboard (notes line 1791), and the Tableau Public sheet OGPPM_0016 on REUNIS, POSSIBLY ADDITIVE AT admin1 (notes line 1829). Known class.
- Routine health information systems. crt.sh stays UNAVAILABLE, and dhis.minsa.gob.pa, sis.minsa.gob.pe, sis.mpps.gob.ve and hacu.health.gov.tt stay REACH FAILURE (notes lines 1669 to 1670). No new source.
- Sources already in the panel. The unaids_aidsinfo rows are one estimates round behind in every region (notes line 1671). Known source, newer edition.
- Reachability. The Honduras transparency portal moves to BLOCKED (notes line 1647). The portals in MEX, BOL, ECU and TTO stay unreached or blocked (notes line 1857). The parliament.gov.gy documents-laid library and datos.gob.gt are BLOCKED (notes lines 1869 and 1875). ONAPRE and the TSJ archive stay REACH FAILURE (notes lines 1893 to 1894). No new source.

### Answer to the stop rule
- Every round-two outcome fits a class known from round one. Round two produced no source needing a new class, so the LAC search meets the §8e stop condition.
- Round two changed no rule about what counts as a source. Round two left the grade of the Tableau Public class unsettled, met a limit of the search method at the download gate, and found the unaids_aidsinfo rows one estimates round behind.

### Findings for the ladder
- Tableau Public grade. ACCESS_LADDER §7c defines GRADE 3.5 as data published to a person, not to a machine, and the ladder defines GRADE 2 as an open born-digital report. The Ecuador Tableau Public workbook carries GRADE 3.5 (notes line 349), and the Peru sheet OGPPM_0016 carries GRADE 2 (notes line 1825). Round two read Tableau Public workbook metadata as JSON (notes line 1798), so the Tableau Public metadata route answers a script. Whether a Tableau Public table export answers a script decides the grade of the Ecuador workbook and the Peru sheet together. The grade of the Tableau Public class is NOT SETTLED, and the OGPPM_0016 export in the download list (notes line 1832) would settle the grade of the Tableau Public class.
- Download gate. Round two reached live hosts in CUB, PAN, HTI, PER, BOL and VEN, and for the candidates on the hosts in CUB, PAN, HTI, PER, BOL and VEN the additive test needs one file opened (notes lines 1651, 1730, 1731, 1699, 1860 and 1898). A third search pass with no download would add more entries of known class marked NOT VERIFIED, and under §8e would not be worth running.
- Editions of sources already ingested. §8e names columns inside sources already ingested as the key of a fourth round. The UNAIDS finding adds editions to columns, because an ingested source with a newer round published becomes a candidate again (notes line 1671). The UNAIDS finding applies to every region, and the re-export of the AIDSinfo files is a decision for Jason (notes line 1674).
- dataZoa detection. A home-page search cannot detect a dataZoa publisher, because the STATIN home page carries no dataZoa string (notes line 1609). The dataZoa class therefore needs an answer from the statistics offices, not a further pass (notes line 1620).

### Recommendation
- No third search pass for LAC. The next LAC step is a download pass chosen by Jason, starting with the smallest file per country able to settle the additive test.
- First candidates from the round-two download lists. For CUB, Anuario-estadistico-salud-2024.xlsx, 500,936 bytes (notes line 1651). For PAN, the 2022 MINSA yearbook tables of 55,036 and 46,148 bytes (notes line 1734). For HTI, Rapport Statistique MSPP 2013, 1,608,343 bytes (notes line 1735). For PER, 8284167-cuadros-estadisticos.zip, 750,421 bytes, for a national HIV testing series, and Lib2090/informacion_complementaria.zip, 11,496,607 bytes, for HIV testing by department (notes lines 1765 to 1766). For BOL, "Boletin epidemiológico_38 2026.pdf", 888,761 bytes (notes line 1860). For PER, the OGPPM_0016 table export, size unknown, which would also settle the Tableau Public grade (notes line 1832).
- Search questions waiting on Jason, not on a further pass. Whether the Wayback Machine may be used for sica.int (notes line 1618). Whether the search may query orcamento.dados.gov.br again for the Brazil budget checks (notes line 1879). Whether ABS or STATIN can be asked for a list of dataZoa tables (notes line 1620). The WHO Mortality Database class sweep for LAC, deferred to Jason. Whether TTO, PAN and GUY fall outside the scope of regions.py as high-income countries (notes line 689).
- After the LAC download decisions, the next document is docs/PHASE5_FEASIBILITY_LAC.md, built from round one and round two on the pattern of docs/PHASE4_FEASIBILITY_WCA.md.

## ROUND TWO. Download pass one, files from CUB, PAN, HTI, PER and BOL and the Tableau Public export of OGPPM_0016, LAC entries (7 October 2026)

Method. Jason permitted the seven downloads of the stop-check list (notes line 1945) and the OGPPM_0016 export (notes line 1832) on 7 October 2026. The script dl1.py fetched the permitted files into the scratch folder dl/, never into data/, and compared every byte count with the size round two recorded (dl1.json). Every file returned HTTP 200 with the expected size. Workbooks were read with openpyxl, PDF text with pypdf, and Cap_009_2025.xls, the one old-format Excel file, by a byte search in Latin-1 and UTF-16, because the xlrd reader is not installed. The OGPPM_0016 export used the CSV route of the Tableau Public view URL (dl_tableau.json). Read-only checks used the panel file and indicators.py. No collection script ran, and nothing was written to data/.

### Files and hashes (first 12 characters of the SHA-256 hash)
- CUB. Anuario-estadistico-salud-2024.xlsx, 500,936 bytes, 45766c171fd3.
- PAN. "Cuadro 8" of the 2022 MINSA yearbook, 55,036 bytes, 9e6547f19d8f, and "Cuadro 9", 46,148 bytes, 0db2b27f66de.
- HTI. Rapport Statistique MSPP 2013, 1,608,343 bytes, 833e57853aa1.
- PER. 8284167-cuadros-estadisticos.zip, 750,421 bytes, 373bbf05adf7, and Lib2090/informacion_complementaria.zip, 11,496,607 bytes, 5030f6c8ef9a.
- BOL. "Boletin epidemiológico_38 2026.pdf", 888,761 bytes, 147c9682b9ae.
- PER. The OGPPM_0016 CSV export, 438 bytes, 81b6d74bcdcb.

### Cuba
- Deaths. Sheets M.18, M.19 and M.20 of the 2024 yearbook of MINSAP, the Cuban health ministry, list "Sida (B20-B24)" among the first 35 causes of death for men and women together, for men alone and for women alone. The yearbook gives 293 AIDS deaths in 2023, a crude rate of 2.9 per 100,000 people, and 381 in 2024, a crude rate of 3.8. Men account for 251 deaths in 2023 and 303 in 2024, and women for 42 and 78, and the sums by sex match the totals (cub_pan_parse.json). Sheets M.18, M.19 and M.20 also give adjusted rates. The round-one question of notes line 896 closes, because the yearbook lists AIDS as a separate cause of death.
- Cases. Sheet M.63, the incidence of selected notifiable diseases by sex, gives AIDS cases ("Sida") of 764 in 2010 (638 men, 126 women), 557 in 2023 (454 men, 103 women) and 282 in 2024 (228 men, 54 women), with rates per 1,000,000 people of 68, 54.4 and 28.5.
- Province. Of the 170 sheets in the workbook, nine mention HIV or AIDS, namely M.18, M.19, M.20, M.54, M.55, M.63, R.101, FI.166 and FI.167 (cub_hiv_sheets.json). Sheets M.55 and R.101 are the only HIV or AIDS sheets with province labels. Sheet M.55 gives deaths from infectious and parasitic diseases (A00-B99) by province for 2024, with the note "Incluye defunciones por sida", so AIDS deaths sit inside a wider total. Sheet R.101 counts health units by type and province, with "Sanatorio Sida" as a unit type. Sheet FI.167 lists the national register "Morbilidad por VIH/sida" among the registers of the health system, and no sheet tabulates the HIV register by province. The province question of notes line 895 closes NEGATIVE for the 2024 workbook.
- Panel. The panel holds no CUB row at admin1. The panel aids_deaths value for CUB is 500 in 2023 and 2024 from unaids_aidsinfo and from who_gho, a modelled estimate (cub_pan_panel_cmp.json). The yearbook counts are registered deaths, a different measure from the modelled estimate. indicators.py defines aids_deaths as a modelled estimate and has no indicator for registered deaths or for AIDS cases, so the Cuban counts are NOT ADDITIVE under the current indicators and go to Jason as decisions.

### Panama
- "Cuadro 8", the ten leading causes of death in Panama for 2021-2022, lists "Enfermedad por Virus de la Inmunodeficiencia Humana [VIH]" with 471 deaths in 2021, a rate of 10.85 and rank 10. The 2022 columns of the HIV row show "..", which the table note defines as "No Aplica" (not applicable), so HIV falls outside the ten leading causes in 2022.
- "Cuadro 9", the five leading causes of death by province and comarca (indigenous territory), shows HIV only where HIV ranks in the top five. Bocas del Toro 2022 has 40 deaths (rate 21.06, 31 men and nine women). Comarca Ngäbe Buglé has 65 deaths in 2021 (rate 28.21, 55 men and 10 women) and 51 in 2022 (rate 21.61, 38 men and 13 women). The source lines of "Cuadro 8" and "Cuadro 9" name the Contraloría General de la República and INEC, the Panamanian statistics institute, with the MINSA health records department as institutional source.
- Panel. The panel holds PAN rows at admin1 from PEPFAR and no PAN aids_deaths row at admin1. The panel spells the comarca "Ngöbe Buglé" and the MINSA table "Ngäbe Buglé", a name-matching point for any connector. National aids_deaths for 2021 is 650 from unaids_aidsinfo and 500 from who_gho. The HIV rows of "Cuadro 9" cover three province-years and stop wherever HIV leaves the top five, so "Cuadro 9" gives no HIV series by province. NOT ADDITIVE, and the national count of 471 joins the registered-deaths decision.

### Haiti
- The Rapport Statistique MSPP 2013 has 62 pages. Tables 2.8.1.1, 2.8.1.2 and 2.8.1.4 on PDF pages 45 to 47 give laboratory HIV tests, HIV tests of pregnant women and people "enrôlées sous ARV" for the ten departments. The department sums match the national totals (hti2013_parse.json), and the source lines of the tables on pages 45 to 47 cite the statistics reports of PNLS, the Haitian national AIDS programme.
- Totals for 2013. 1,154,561 HIV tests with 3.2% positive, 246,396 pregnant women tested for HIV with 1.7% positive, and 18,705 patients on ARV reported nationally during 2013. Ouest, the department with the most tests, has 498,419 tests at 3.4% positive, 105,020 pregnant women tested at 1.8% positive, and 8,436 people on ARV.
- Panel. HTI rows at admin1 start in 2016 from pepfar_snu and in 2018 from pepfar_agency_snu. The panel uses the same ten department names, spelling "Grande-Anse" where the report has "GRAND-ANSE". The 2013 department test counts are ADDITIVE AT admin1 as hiv_tests_performed, for a year before PEPFAR coverage at admin1.
- ARV figure. The 2013 total of 18,705 equals none of the panel values for 2013, namely on_art_count of 29,000 from unaids_aidsinfo and 29,426 from who_gho, and art_initiations of 24,117 from who_tme (hti2013_panel_cmp.json). The report text reads "Au cours de l’année 2013, au niveau national, 18 705 patients enrôlés sous ARV ont été rapportés". Whether the 18,705 patients started ARV during 2013 or were on ARV at any point in 2013, and whether the PNLS reports cover every treatment site, is NOT VERIFIED.
- Antenatal figures. The panel indicator anc_hiv_testing_pct is a percentage. Whether the report gives the number of pregnant women seen in antenatal care, the denominator for anc_hiv_testing_pct, is NOT VERIFIED.

### Peru
- 8284167-cuadros-estadisticos.zip holds 11 chapter workbooks of the ENDES annual series, the Peruvian demographic and health survey of INEI, the national statistics institute. Ten workbooks are xlsx files and Cap_009_2025.xls is in the old Excel format. No row in any xlsx workbook of the zip names HIV or AIDS. The byte search of Cap_009_2025.xls finds no "VIH", and every match of "SIDA" sits inside the word "OBESIDAD". NEGATIVE for a national HIV testing series.
- Lib2090/informacion_complementaria.zip holds three methodology PDF files, two SPSS microdata files (not opened) and four table workbooks of the 2025 ENDES health report, "Anexo 4_2025.xlsx" and chapters one to three. Table 3.3 of "Cap. 3_2025.xlsx" gives the percentage of people aged 15 to 49 who had an HIV test in the last 12 months, national from the second half of 2013 to 2025 and by department from 2014 to 2025 (per_endes_hiv.json). Table 3.3 has 26 department rows, with Callao as a separate row and with Lima split into Lima Metropolitana and Departamento de Lima.
- Values of table 3.3. National 13.64% in the second half of 2013, 23.03% in 2019, 14.68% in 2020 and 24.79% in 2025. In 2025 the department values run from 14.57% in Puno to 37.73% in Moquegua. Table 3.4 gives people tested in the last 12 months who knew the result, between 92.29% and 96.2% nationally. Every national value of table 3.4 exceeds the table 3.3 value for the same year, so the base of table 3.4 is people tested, not all people aged 15 to 49. Table 3.2 covers knowledge of HIV prevention at ages 15 to 29.
- Panel. The panel holds no PER row at admin1. The survey rows in the panel cover hiv_prevalence_15_49, kp_hiv_prevalence, kp_prevention_coverage_pct and kp_size_estimate, and indicators.py has no indicator for recent HIV testing from a household survey. The ENDES department series would be ADDITIVE AT admin1 under a new survey indicator, and is NOT ADDITIVE under the current indicators. Decision for Jason.

### Bolivia
- The weekly bulletin of the Bolivian health ministry for epidemiological week 38 of 2026 has 26 pages with sections on 11 events, namely chikungunya, respiratory viruses, acute diarrhoeal disease, haemorrhagic fever, acute respiratory infections and pneumonia, leishmaniasis, leptospirosis, malaria, canine rabies, measles and whooping cough (bol_se38_scan.json). The bulletin text never mentions HIV, AIDS, syphilis or sexual transmission. NEGATIVE for an HIV table by department in the week-38 bulletin of 2026. Whether the 2024 bulletin for week 27 carries an HIV section stays NOT VERIFIED (notes line 1861).

### Tableau Public export of OGPPM_0016
- The first request, to the view URL with .csv added, redirected to the Tableau Public profile application and returned HTTP 404 with an HTML page of 2,026 bytes. Nothing on the redirected page was worked around.
- The second request added the parameter ":showVizHome=no" and returned HTTP 200 as text/csv, 438 bytes, saved as dl/per_ogppm_0016.csv. The CSV holds three measures by year for 2020 to 2025, namely PIA (the opening budget), PIM (the modified budget) and Devengado (accrued spending). For 2024 the CSV gives PIA 159,239, PIM 305,891 and Devengado 277,614.16.
- The CSV holds no region, product or unit column. The export gives the first worksheet of the dashboard at the default filter state. The region, product and unit behind the default filter state are NOT VERIFIED.
- A region-by-region export needs the field names of the dashboard filters. The view HTML now loads through a script named PreBootstrap.min.js, and the tsConfigContainer block of the view HTML is empty, so the older route to the session JSON did not answer (tab_view.html). The region split stays NOT VERIFIED.
- Grade. The CSV route answers a script for the default view of a Tableau Public dashboard. The Peru sheet keeps GRADE 2 (notes line 1825), and the Tableau Public class settles at GRADE 2 for default views, closing the question of notes line 1938. The Ecuador workbook (notes lines 345 and 349) would move from GRADE 3.5 to GRADE 2 by the same route. NOT VERIFIED until the Ecuador CSV route is tried, a download needing Jason's permission.

### What download pass one changes
- CUB. Registered AIDS deaths for 2023-2024 and AIDS cases for 2010 and 2023-2024 now have a born-digital source, and the province question closes NEGATIVE.
- PAN. Registered HIV deaths at national level for 2021 and for three province-years, with no series by province.
- HTI. The first department figures before PEPFAR coverage, ADDITIVE AT admin1 for HIV tests in 2013.
- PER. A survey series of recent HIV testing by department for 2014 to 2025, and NEGATIVE for the ENDES annual series zip.
- BOL. NEGATIVE for the week-38 bulletin of 2026.
- Tableau Public. GRADE 2 for default views, with the region split NOT VERIFIED.

### Decisions for Jason
- Registered deaths. Whether the panel should carry registered AIDS or HIV deaths from civil registration beside the modelled aids_deaths, starting from the CUB yearbook for 2023-2024 and the PAN table for 2021.
- AIDS cases. Whether the panel should carry notified AIDS cases, starting from CUB sheet M.63.
- Survey testing indicator. Whether the panel should carry the ENDES percentage tested for HIV in the last 12 months, national and by department for Peru.
- HTI ARV figure. Whether to read the Haitian statistical reports of other years to settle the meaning of "enrôlées sous ARV" before any connector uses the 2013 ARV column.
- Next downloads. The Ecuador Tableau CSV route for the grade check, HTI Bulletin de Surveillance No. 22 (4,872,564 bytes, notes line 1736), the Bolivian week-27 bulletin of 2024 (1,559,078 bytes, notes line 1861), and the TTO, GUY, SUR and BLZ files of the round-two waiting list.

## ROUND TWO. Jason's decisions on new indicators and the rigour checks behind the decisions, LAC entries (7 October 2026)

Jason's reply of 7 October 2026 to the decisions of the download-pass section reads "if carrying these enriches the panel but does not jeopardise the sceintific rigour and accuracy, then yes. And I give you permissions for all necessary downloads". The checks below test every proposed indicator against the condition in Jason's reply, using read-only reads of schema.py, indicators.py, the Haiti report of 2013 and the ENDES workbook "Cap. 3_2025.xlsx" (per_endes_flags.py, per_endes_flags.json, per_endes_flag_rows.py, per_endes_flag_rows.json). No code file and no data file was changed.

### Correction to the Haiti entry
- Notes lines 1975 and 1998 mark the 2013 department test counts of Haiti ADDITIVE AT admin1 as hiv_tests_performed. indicators.py defines hiv_tests_performed as "HIV tests performed with the result returned to the person". Table 2.8.1.1 of the Haiti report is titled "Répartition des examens de laboratoire effectués selon le type et les résultats", a count of laboratory examinations performed, and the Haiti report does not say whether results reached the person or whether one person can count twice. The Haiti test counts are NOT ADDITIVE as hiv_tests_performed, and notes lines 1975 and 1998 are withdrawn on the Haiti test counts. The Haiti test counts stay a candidate for a separate indicator of laboratory HIV examinations, NOT VERIFIED until a second Haitian report year defines the count.

### Registered deaths
- Enrichment. Registered AIDS deaths for CUB in 2023 and 2024 (notes line 1965) and registered HIV deaths for PAN in 2021 (notes line 1968), national counts from civil registration next to the modelled aids_deaths.
- Rigour. schema.py holds five source classes, described in the schema.py docstring as "The five source classes from section 4 of the indicator document." and followed by the instruction "Keep this faithful to the document's taxonomy." Deaths from civil registration fit none of the source classes in schema.py. Carrying registered deaths needs a sixth source class or a decision to file registered deaths under routine_programme_record. Decision for Jason and Adrian.
- Rigour. The Panama province rows exist only where HIV ranks among the five leading causes (notes line 1970), so a province series built from the Panama rows would hold only years of high HIV mortality. Only national counts qualify.
- Rigour. Registered deaths and the modelled aids_deaths measure different things and must sit under separate indicator ids, never summed and never drawn as one line.
- Status. Passes the condition in Jason's reply for national counts under a separate indicator id, once Jason and Adrian settle the source class.

### AIDS cases
- Enrichment. One country so far, CUB, with 2010, 2023 and 2024 (notes line 1963).
- Rigour. Notified AIDS cases fit routine_programme_record. AIDS case definitions can differ between national surveillance systems, so AIDS case counts from different countries may not compare.
- Status. Low enrichment from one country with three years. Recommendation to Jason, hold the AIDS-case indicator until the search finds a source covering more than one country.

### Survey indicator of recent HIV testing
- Enrichment. ENDES table 3.3 gives national values from the second half of 2013 to 2025 and values for 26 department rows from 2014 to 2025 (notes line 1981). The panel holds no PER row at admin1 (notes line 1983).
- Rigour. The survey class fits. Table 3.3 counts people aged 15 to 49, women and men together, who had an HIV test in the last 12 months, with no condition on receiving the result. Table 3.4 counts people who also learned the result, as a share of people tested. A survey indicator of people tested who received the result, as a share of all people aged 15 to 49, differs from table 3.3 and from table 3.4, so the ENDES series needs an indicator id carrying the ENDES definition, and the panel carries no product of table 3.3 and table 3.4.
- Rigour. ENDES marks low precision and suppression by cell format while the stored value stays a number. The table 3.3 footnote reads "( ) Comprende a estimadores con coeficiente de variación mayor a 15% considerados como referenciales." and the table 3.4 footnote reads "(a) Las tasas o porcentajes basados en menos de 20 casos sin ponderar no se muestran.". The parse of round two read the numbers and lost the formats (notes line 1982). Table 3.3 holds 12 values in the low-precision format "(0.0)", seven in the row for people of foreign nationality ("Extranjera") and five in department rows, namely Apurímac 2014 (7.5), Cajamarca 2014 (9.3), Huancavelica 2014 (12.5), Puno 2014 (9.3) and Puno 2020 (10.7). Table 3.4 holds 38 values in the suppression format "a", all in the "Extranjera" row, values INEI chose not to show. A connector must read the cell formats, flag the low-precision values and drop the suppressed values. The 2025 Puno value of 14.57% in notes line 1982 carries no flag.
- Status. Passes the condition in Jason's reply under a survey indicator with the ENDES definition, with the low-precision values flagged and the suppressed values dropped.

### Haitian ARV figure
- Status. Reading a second Haitian report year needs a download, which Jason's reply permits. Until the second report year settles the meaning of "enrôlés sous ARV", the 2013 ARV column stays out of any connector.

## ROUND TWO. Download pass two, the Bolivian week-27 bulletin of 2024 and the Haitian PNLS bulletin no 22, LAC entries (7 October 2026)

Method. Under the download permission in Jason's reply of 7 October 2026, dl2.py fetched two files into the scratchpad and recorded URL, HTTP status, bytes and SHA-256 hash in dl2.json. dl2_parse.py read the text with pypdf and checked every figure below by assert (dl2_parse.json). A read-only pass over the panel CSV wrote bol_panel_cmp.json.

### Files and hashes
- BOL. BoletinEpidemiologico_SE_27-2024.pdf, 1,559,078 bytes, 6dce25b2c394, equal to the size from the earlier HEAD request.
- HTI. Bulletin de Surveillance Epidemiologique VIH Sida No. 22 Decembre 2020, 4,872,564 bytes, a1c4ab007ab7, equal to the size from the earlier HEAD request.

### Bolivia
- Page four of the bulletin reads "Hasta la S.E. 27 se registra en sistema 1.630 casos notificados de VIH/SIDA, de ellos 131 (8,0%) fueron captados en fase SIDA (dato preliminar)." The round-one snippet of notes line 450 is VERIFIED.
- Page 17 gives notified HIV and AIDS cases with a notification rate per 100,000 people for the nine departments, from the start of 2024 to week 27 ending 6 July 2024, from SIMONE, the MSyD register of HIV cases, extracted on 8 July 2024 and marked preliminary. Totals by department, Santa Cruz 535, La Paz 416, Cochabamba 314, Beni 95, Chuquisaca 72, Oruro 67, Potosí 67, Tarija 43, Pando 21. The department sums equal the national 1,499 HIV cases, 131 AIDS cases and 1,630 cases in total. Weekly bulletins do hold an HIV table by department, which answers the question of notes line 1846.
- Panel. The panel holds no BOL row at admin1 and no BOL new_diagnoses row (bol_panel_cmp.json). indicators.py defines new_diagnoses as "Number newly diagnosed HIV-positive (PEPFAR MER HTS_TST_POS)", and the panel fills new_diagnoses from positive test counts of PEPFAR, the Global Fund and the Thai HIV hub. SIMONE counts notified cases, a case report per person, not positive tests. POSSIBLY ADDITIVE AT admin1 as new_diagnoses, NOT SETTLED.
- Rigour. The week-27 figures cover half a year and are preliminary. An annual department count needs the closing bulletin of every year, week 52 or week 53, read from the MSyD bulletin listing.

### Haiti
- Bulletin no 22 is a thematic issue of 44 pages with articles on research, treatment interruption, people diagnosed but never enrolled, HIV self-testing and the SALVH data system, named on page 31 as the "système de suivi actif longitudinal du VIH en Haïti", the national patient database. The bulletin holds no department table for a calendar year.
- Vocabulary. Page 20 reads "Au 30 juin 202 0, les patients actifs sous traitement ARV étaient de 114 231." and page 44 reads "Nombre de personnes actives sous ARV au 30 mars 2020 119 700", so PNLS uses "actifs sous ARV" for people on treatment at a date. Page 20 defines the non-enrolled as patients "qui n’ont jamais reçu de traitement" and page 22 speaks of "clients nouvellement enrôlés au cours de cette période", so PNLS uses "enrôlés" for entry into care or treatment during a period.
- Haitian ARV figure for 2013. Read with the PNLS vocabulary, the 18,705 patients "enrôlés sous ARV" during 2013 (notes line 1974) count entries into treatment during 2013. The panel holds 24,117 ART initiations for HTI in 2013 from who_tme and 29,000 (unaids_aidsinfo) and 29,426 (who_gho) people on ART. The figure of 18,705 matches none of the panel series. The meaning is now likely, and the count is NOT SETTLED. The 2013 ARV column stays out of any connector, as a candidate for art_initiations at admin1 once the gap of 5,412 against who_tme is explained.
- Department figures. "Tableau 2" counts non-enrolled people by department over October 2017 to June 2020, and "Figure 3" charts patients in treatment interruption by department over October 2019 to September 2020. No calendar year matches the period of "Tableau 2" or the period of "Figure 3", and "Figure 3" is a chart, so the department figures are NOT ADDITIVE.

### Decisions for Jason
- BOL notified cases. Whether SIMONE notified cases may enter new_diagnoses, or need an indicator id of notified HIV cases.

## ROUND TWO. Download pass two continued, the Suriname health tables of 2015 to 2021, the Belize HIV surveillance report of 2018 and the Trinidad and Tobago health budget guides of 2024 and 2026, LAC entries (8 October 2026)

Jason's reply of 8 October 2026 to the decisions at the end of the r2n section (notes line 2038) reads "that's fine". Recorded as three decisions. Notified HIV cases from national case surveillance go under a separate indicator id of notified HIV cases and never into new_diagnoses, as the r2n section recommends. The AIDS-case indicator is held until a source covers more than one country. The source class for registered deaths stays open for Jason and Adrian (r2m section, notes line 2010).

Consequence for notes line 777. PAHO Core Indicator 93 is the count of new HIV diagnoses reported by national ministries (notes line 772), labelled "Public Health Surveillance" in the PAHO rows (notes line 180). Under Jason's reply PAHO indicator 93 goes under the indicator of notified HIV cases and not under new_diagnoses. The ADDITIVE marker at notes line 777 now applies to the new indicator id and is withdrawn for new_diagnoses. Every country entry marking a national ministry count DUPLICATE of PAHO indicator 93 keeps the DUPLICATE marker under the new id.

Files. Four downloads on 8 October 2026 under Jason's permission of 7 October 2026, saved to the scratchpad folder dl and recorded in dl2.json, every size equal to the HEAD size of round one. sur_odin_5_1_5_2.docx 33,538 bytes (sha256 1b0171419f0b) from statistics-suriname.org. blz_hiv_stats_2018.pdf 1,541,580 bytes (sha256 743943e943ed) from nacbelize.org. tto_bg2024_moh.pdf 1,469,801 bytes (sha256 594c937d2928) and tto_bg2026_moh.pdf 1,913,424 bytes (sha256 8a589ada92e4) from ttparliament.org. Text came from pypdf and from a read of the docx XML (dl3_extract.py). The section builder build_r2o_section.py checks every figure below by assert, with read-only reads of the panel CSV, paho_ci93.json and indicators.py.

### Suriname, ODIN 5.1-5.2 of the Algemeen Bureau voor de Statistiek
- Contents. Tables "Tabel 11.6" to "Tabel 11.11c", namely hospital cases of leptospirosis, dengue, malaria and chikungunya for 2015-2021, selected health statistics for 2015-2019 ("Tabel 11.10") and COVID-19 tables. No table of HIV cases. The guess at notes line 748 of HIV case counts for 2015-2021 fails. NEGATIVE for notified HIV cases.
- Deaths. The "Tabel 11.10" row "HIV/AIDS" under the heading "Sterfte aantallen ten gevolge van / Mortality numbers due to" reads 2015 61, 2016 69, 2017 46, 2018 48 and 2019 54, with the source line "Bron : Bureau voor Openbare Gezondheidszorg / Source : Bureau for Public Health". The table gives no definition. Whether the counts come from death certificates is NOT VERIFIED.
- Panel position. SUR aids_deaths for 2015-2019 comes from unaids_aidsinfo and who_gho only, with the UNAIDS marks "<200" for 2015-2018 and "<500" for 2019 in the extra field. Notes line 748 records the gap in registered HIV deaths from 2015.
- Status. National registered HIV deaths for 2015-2019, ADDITIVE under the registered-deaths indicator once Jason and Adrian settle the source class. GRADE 2. Kept apart from the modelled aids_deaths under the r2m rule.

### Belize, HIV Surveillance Report 2018 of the Ministry of Health Epidemiology Unit
- Source. Published July 2019 by the Epidemiology Unit and hosted on the National AIDS Commission site. 29 pages. Data from the HIV case-based surveillance in BHIS (Belize Health Information System) for January to December 2018, with many counts marked preliminary.
- Tests. "Table 1" gives 40,162 HIV tests done in 2018 (14,224 male, 25,938 female) against 36,947 in 2017. BHIS captured 35,276 of the tests, and 4,886 came from sources outside BHIS. "Table 2" splits the BHIS tests by district, Corozal 4,041, Orange Walk 4,100, Belize 10,763, Cayo 8,768, Stann Creek 4,450, Toledo 3,102 and unknown 52. Panel BLZ hiv_tests_performed holds no 2018 row and holds district rows only for 2016 (pepfar_snu). The report counts tests done and never says whether the result reached the person. POSSIBLY ADDITIVE as hiv_tests_performed, national and by district for 2018, NOT SETTLED on the definition. The district split covers BHIS tests only, so 4,886 tests carry no district.
- Notified cases. "Table 3" and "Table 4" give 254 newly diagnosed HIV infections in 2018 (84 female, 170 male), by district Corozal 17, Orange Walk 15, Belize 139, Cayo 36, Stann Creek 42, Toledo three and unknown two. PAHO indicator 93 reads 254 for 2018, so the national count is DUPLICATE. The counts come from case surveillance, so under Jason's reply the district counts go under the indicator of notified HIV cases, ADDITIVE AT admin1 for 2018. GRADE 2. The report text gives 223 for 2017, while "Table 13" of the same report and PAHO indicator 93 give 224, a difference of one.
- ART. "Table 5" gives 1,455 people alive and on ART at the end of 2018 (719 female, 736 male). Panel on_art_count for 2018 reads 1,486 (global_fund), 1,500 (unaids_aidsinfo) and 1,065 (who_gho). The report holds no district table of ART and no year before 2018, so the ART series for 2010-2016 sought at notes line 805 is not in the report. NOT ADDITIVE.
- Viral load. "Table 10" gives people tested for viral load as 140 in 2015, 940 in 2016, 304 in 2017 and 935 in 2018, and 563 of the 935 people tested in 2018 had a suppressed viral load. indicators.py defines viral_load_tests_performed as "People on ART with a viral-load result in the year", and the panel holds no BLZ row of viral_load_tests_performed. The report counts people living with HIV who received a test and does not restrict the count to people on ART. POSSIBLY ADDITIVE for 2015-2018, NOT SETTLED on the ART condition.
- Deaths. "Table 6" and "Table 7" give 105 HIV-related deaths in 2018 (38 female, 67 male), preliminary, by district Corozal five, Orange Walk three, Belize 62, Cayo 15, Stann Creek 17 and Toledo three. The district counts sum to the national count, so the selection problem of the Panama province rows (r2m section) does not arise. The registered HIV deaths at notes line 784 read 113 for 2018, eight more than the preliminary count. Whether the Epidemiology Unit counts deaths from death certificates or from the case register is NOT VERIFIED. NOT ADDITIVE until a report with final counts exists.
- PMTCT. "Table 8" gives 39 women with HIV who delivered in 2018, of whom 38 received ART during pregnancy. Panel pmtct_arv_count for 2018 reads 49 (unaids_aidsinfo and who_gho). The cause of the gap of 11 is NOT VERIFIED. NOT ADDITIVE, difference recorded.
- TB and HIV. The report gives 30 TB patients with HIV in 2018, and panel tb_patients_hiv_positive (who_tme) reads 31. NOT ADDITIVE.

### Trinidad and Tobago, Ministry of Health budget guides for fiscal 2024 and fiscal 2026 from the Parliament Financial Scrutiny Unit
- Guide for 2024 (71 pages). The tables "Major Programmes and Developments for the Period 2021 to 2024" and "Noteworthy Development Programme Estimates 2018-2024" list the largest development items only, and no HIV item appears. The supplementary list for fiscal 2023 carries "004/07/D/022 – President’s Emergency Programme for AIDS Relief (PEPFAR) - $6,443,600", needed for "the payment of salaries to the staff of PEPFAR to September 30, 2023". The investment pages allot TT$0.1 million in fiscal 2024 to the National AIDS Coordinating Committee (NACC) project on the national HIV and AIDS policy.
- Guide for 2026 (69 pages). TT$0.3 million allocated in fiscal 2025 to the same NACC policy project, and "CF 004-07D-024 – National AIDS Coordinating Committee (NACC) $639,000" among the new projects for fiscal 2026. The list of ministry services names an "HIV/AIDS Coordinating Unit" with no money figure.
- Correction to notes line 708. The search snippet of TT$43.8 million allocated for HIV/AIDS activities in fiscal 2025 with TT$38.8 million spent is wrong. The 2026 guide gives TT$43.8 million and TT$38.8 million for the Health Services Support Programme, an IDB (Inter-American Development Bank) loan aimed at non-communicable diseases. The snippet is withdrawn. The snippet on the item "Special Programme HIV/AIDS" for 2017-2018 stays UNVERIFIED, because no guide read so far covers 2017-2018.
- Status. The 2024 guide and the 2026 guide carry no yearly HIV line with allocation and actual, so the plan at notes line 709 to read the guides as a series fails for 2021-2026. The HIV money in the guides is small project money (TT$0.1 million to TT$0.6 million) and one PEPFAR staff item. Whether item 004/07/D/022 is state money paying staff of the PEPFAR programme or US money passing through the state budget is NOT SETTLED. The Draft Estimates of Development Programme (footnote 29 of the 2024 guide, HEAD 15,050,422 bytes for the 2024 volume) would give the item by year. ADDITIVE only as a separate allocation series with the financing source recorded, never as domestic_hiv_spend. GRADE 2.

Next downloads. The 2024 Draft Estimates of Development Programme for item 004/07/D/022, a Haitian report year after 2013, the Bolivian year-end bulletins and the Ecuador Tableau CSV route.

## ROUND TWO. Download pass two continued, the Trinidad and Tobago development estimates for 2024 and the Ecuador Tableau Public CSV route, LAC entries (8 October 2026)

Files. One download on 8 October 2026 under Jason's permission of 7 October 2026, saved to the scratchpad folder dl and recorded in dl2.json. tto_dev_estimates_2024.pdf, 15,050,422 bytes (sha256 5bd865f4e528), from finance.gov.tt, equal to the HEAD size in the r2o section (notes line 2089). Two CSV requests to Tableau Public for the Ecuador workbook, recorded in dl2.json with status 404 and the response bodies saved as ecu_tab_listaresumen.csv and ecu_tab_menu.csv. The workbook metadata and the status of the HTML views were read as JSON and HTML and saved as ecu_tab_check.json. The section builder build_r2p_section.py checks every figure below by assert, with read-only reads of the panel CSV and ACCESS_LADDER.md.

### Trinidad and Tobago, Draft Estimates of Development Programme for the financial year 2024, Ministry of Finance
- Format. The volume has 254 pages, and pypdf found under 50 characters of text on 253 pages. Only the cover carries a text layer, so the volume is a PDF of page images. The text below came from tesseract OCR (optical character recognition, software reading printed characters from a page image) run on the largest image of every page (ocr_tto.py, output in the scratchpad folder ocr_tto).
- Ladder rule. ACCESS_LADDER.md (line 47) records scanned PDFs as files the project does not OCR, "because an OCR error in a count is invisible and unfalsifiable". The OCR read here was a search for HIV items, and every HIV figure below passed two tests. Every HIV figure sits in a block of rows whose printed subtotal, or whose printed difference between the amounts brought forward and carried forward, equals the sum of the OCR figures of the block, in all four money columns, with one exception named below. The PEPFAR row on page 84 was also compared with the page image and matches the OCR text. Whether OCR with a subtotal test meets the ladder rule is a decision for Jason, and until Jason decides, the figures below stay outside the panel.
- Layout. Four money columns in Trinidad and Tobago dollars, headed "2022 Actual", "2023 Estimate", "2023 Revised Estimate" and "2024 Estimate". The summary page splits the programme into Part A, the Consolidated Fund, and Part B, the Infrastructure Development Fund, with the note "Part 'B' represents funds disbursed directly from the Infrastructure Development Fund."
- PEPFAR item. Head 28 Ministry of Health, Part A, sub-head 09, item 004, sub-item 07 "HEALTH", project group D "OTHER SERVICES", project 022 "President's Emergency Programme for AIDS Relief (PEPFAR)". TT$5,776,246 actual for 2022, TT$500,000 estimate for 2023, TT$6,943,600 revised estimate for 2023 and TT$3,000,000 estimate for 2024. The revised estimate for 2023 less the estimate for 2023 is TT$6,443,600, equal to the supplementary sum for item 004/07/D/022 in the 2024 budget guide (notes line 2086). Group D sums to TT$94,242,230, TT$120,700,000, TT$92,143,600 and TT$190,882,000, as printed.
- Other HIV items. Head 13 Office of the Prime Minister, project 106 on the finalisation, launch and dissemination of the national HIV and AIDS policy, with no actual for 2022, TT$134,000 as estimate and as revised estimate for 2023 and TT$100,000 for 2024. The 2024 figure equals the TT$0.1 million for the NACC policy project in the 2024 budget guide (notes line 2086). The 2022 column of the Head 13 group is not tested, because the OCR text of one project in the group shows a bracket in place of the last digit of the 2022 actual. Head 15 Tobago House of Assembly, project 437 "HIV/AIDS and Substance Abuse Programme", TT$500,000 in the first three columns and TT$200,000 for 2024, a project joining HIV with substance abuse. Head 15, project 044 "Tobago HIV/AIDS Strategic Response", TT$500,000 in all four columns. Head 30 Ministry of Labour, project 099 on a national baseline survey of knowledge, attitudes, beliefs and practices on HIV in the workplace, TT$8,890 actual for 2022, TT$240,000 estimate for 2023, no revised estimate for 2023 and TT$300,000 for 2024.
- Totals. The five HIV items add up to TT$6,785,136 actual for 2022, TT$1,874,000 estimate for 2023, TT$8,077,600 revised estimate for 2023 and TT$4,100,000 estimate for 2024. The PEPFAR item carries 85 per cent of the actual for 2022. No other HIV, AIDS, PEPFAR or NACC item appears in the OCR text of the 254 pages.
- Financing source. The PEPFAR item sits in Part A, the Consolidated Fund, and no HIV item sits in Part B. The explanation column of the PEPFAR item is empty, and the volume says nothing about a US grant behind the item. The question at notes line 2089, state money paying staff of the PEPFAR programme or US money passing through the state budget, narrows to money appropriated by Parliament from the Consolidated Fund and stays NOT SETTLED.
- Panel position. Panel TTO domestic_hiv_spend holds one row, US$10,685,318 for 2020 from unaids_gam_expenditure (GAM reporting cycle 2022). The development programme covers projects and not the recurrent budget of the ministries, so the five items are not total domestic HIV spending.
- Status. Development-programme HIV items for 2022 to 2024, POSSIBLY ADDITIVE as a separate allocation series with the financing source recorded, never as domestic_hiv_spend. GRADE 3, because the volume is a scanned PDF. NOT ADDITIVE until Jason rules on OCR with a subtotal test. Earlier volumes of the same series would give actuals for earlier years. Whether earlier volumes carry a text layer is NOT VERIFIED.

### Ecuador, Tableau Public CSV route for the death registration workbook of INEC
- Workbook. The Tableau Public workbook API, read as JSON, gives the workbook Registroestadsticodedefuncionesgenerales_15907230182570 with the title "Registro estadístico de defunciones generales", the author "Instituto Nacional de Estadística y Censos (INEC)", 12 sheets, 230,705 views and a last update on 27 November 2022, matching notes line 345.
- CSV route. Requests for the sheets "Lista resumen de causas" and "Menú", with ".csv" added to the view address and the parameter ":showVizHome=no", returned HTTP 404 with a JSON body of 382 bytes of type "missing-view". The HTML views of the two sheets returned HTTP 200 with 6,569 bytes. Nothing on the error page was worked around.
- Grade. The CSV route of the r2l section (notes line 1993) fails for the Ecuador workbook. The Ecuador workbook keeps GRADE 3.5 (notes line 349), and the Tableau Public class keeps GRADE 2 for default views where the CSV route answers. Whether the Becker short list of causes keeps HIV as a line of the list stays NOT VERIFIED.

Next downloads. Earlier volumes of the Trinidad and Tobago development estimates once Jason rules on OCR, a Haitian report year after 2013 and the Bolivian year-end bulletins.

## ROUND TWO. Download pass two continued, the Haitian MSPP statistical reports for 2014, 2015 and 2016 and the WHO TB data dictionary, LAC entries (8 October 2026)

Files. Four downloads on 8 October 2026 under Jason's permission of 7 October 2026, saved to the scratchpad folder dl and recorded in dl2.json, every size equal to the HEAD size of round two (notes line 1720) or, for the dictionary, with no HEAD size to match. hti_rapport_stat_2014.pdf 2,548,364 bytes (sha256 b60d3b14c348), hti_rapport_stat_2015.pdf 7,630,772 bytes (sha256 035198956ebc) and hti_rapport_stat_2016.pdf 4,684,286 bytes (sha256 f254a25a91c9), from www.mspp.gouv.ht. who_tme_dictionary.csv 108,122 bytes (sha256 2b0aecd442bf), the data dictionary of the WHO tuberculosis dataset from extranet.who.int, named as the authority on column meanings in the docstring of hivimpact/connectors/who_tme.py. The three MSPP reports carry a text layer, read with pypdf and with no OCR. Every typed table value re-renders the source line exactly, and the department rows sum to the printed total in every count column (hti_r2q_parse.py, hti_r2q_parse.json).

### Rapport Statistique MSPP 2014
- Contents. 53 pages. HIV appears on one page, the annex row "Proportion de cas positifs parmi les examens de VIH", 4.3%, 3.89%, 3.2% and 3.0% for 2011 to 2014. The 3.2% for 2013 equals the positive share in the 2013 report (notes line 1974). The 2014 report gives no HIV table, no HIV count and no ARV figure.
- Status. NEGATIVE for the ARV question and for department tables. The positivity row gives rates with no counts and is NOT ADDITIVE.

### Rapport Statistique MSPP 2015
- Contents. 76 pages. Three HIV tables by department for 2015, every table with the source line "PNLS/MSPP, www.mesi.ht".
- Table 34. Exposed infants registered 2,933 and exposed infants tested by PCR before eight weeks 2,007 (68.4%).
- Table 35. The count column is headed "Nouveaux enrôlés soins pré ARV et ARV", new enrolees in pre-ART care and in ART care. 21,304 new enrolees, of whom 18,450 were placed on INH (isoniazid, the TB preventive treatment), 86.6%. Nord prints 3,370 placed on INH against 2,964 enrolees (113.7%). Grand-Anse prints 29.3% while 262 of 859 gives 30.5%, and the report text repeats 29.3.
- Table 36. TB cases 16,431, TB patients tested for HIV 14,817 and TB patients positive for HIV 2,426.
- Panel comparison, national, 2015. The who_tme art_initiations row from the column hiv_reg_new2 reads 21,317, 13 above the MSPP enrolee total. The unaids_aidsinfo tpt_initiation_new_pct row reads 86.6, equal to 18,450 over 21,304. The who_tme tb_patients_hiv_tested row reads 14,817, equal to Table 36. The who_tme tb_patients_hiv_positive row reads 2,427, one above Table 36.
- Definition. The WHO dictionary defines hiv_reg_new2 as "Total number of adults and children newly enrolled in HIV treatment (i.e. those who registered for antiretroviral therapy) during the reporting period", and indicators.py labels art_initiations "People newly enrolled on ART during the year". The MSPP column counts new enrolees in pre-ART care as well as in ART care. The near-equal totals point to a Haitian figure for 2015 under hiv_reg_new2 counting enrolment in HIV care with pre-ART included. Whether the WHO figure of 21,317 and the MSPP figure of 21,304 come from one count is NOT VERIFIED. The HTI art_initiations row for 2015 from who_tme may include people in pre-ART care. NOT SETTLED, for Jason. No panel edit.
- Additive test. Department rows for HTI in the panel start in 2016 (notes line 856), and the panel holds no HTI department row of any TB indicator. Table 36 by department for 2015 is ADDITIVE AT admin1 under tb_patients_hiv_tested and tb_patients_hiv_positive, with the department sum of TB patients tested equal to the national who_tme row. GRADE 2. Table 35 by department does not fit art_initiations, because the MSPP column includes pre-ART enrolees, and would need an indicator id of new enrolment in HIV care. POSSIBLY ADDITIVE. Table 34 by department uses registered exposed infants as the denominator, and whether the UNAIDS early_infant_diagnosis_pct row shares the denominator is NOT VERIFIED. POSSIBLY ADDITIVE.
- Weekly notifiable diseases. Table 10 gives 4,485 confirmed HIV cases by department from epidemiological week 35 of 2015 only. A part-year count, NOT ADDITIVE.

### Rapport Statistique MSPP 2016
- Contents. 57 pages. No page carries the word "enrôlés" or "enrôlées".
- Table 22. People tested for HIV who know the result, by department, 1,265,480, of whom 1,048,116 are men and non-pregnant women and 217,364 pregnant women. Source line "MSPP-PNLS".
- Tables 23 and 24. HIV cases diagnosed in 2016, 17,471 with 275 not located to a department, from SALVH (Suivi Actif Longitudinal du VIH/sida en Haïti, the case database of the PNLS, the national HIV programme). Positivity 1.38%. Cumulative notified cases after removal of duplicates 245,460. The report text dates the cumulative total to the end of June 2016 and the table header to the end of 2016.
- Panel comparison, departments, 2016. Against pepfar_snu hiv_tests_performed (MER HTS_TST), the MSPP count of people tested is higher in eight departments and lower in Nord (140,561 against 143,087) and Sud-Est (24,736 against 25,453). The 10 departments sum to 1,265,480 at MSPP and 1,228,340 at PEPFAR. Against pepfar_snu new_diagnoses (MER HTS_TST_POS), PEPFAR is higher in all 10 departments, 26,856 against 17,196 located MSPP cases. MSPP counts unique cases after removal of duplicates, and PEPFAR counts positive test results. Whether the PEPFAR year 2016 covers the 12 months of the MSPP calendar year is NOT VERIFIED.
- Additive test. The SALVH cases come from case surveillance and go under the indicator of notified HIV cases (Jason's decision, notes line 2063). The national count of 17,471 for 2016 is ADDITIVE under the notified-cases indicator, because the PAHO dashboard starts in 2018 (notes line 852). The department counts for 2016 are ADDITIVE AT admin1 under the same indicator. GRADE 2. Table 22 by department is a second source for the pepfar_snu testing rows of 2016, NOT ADDITIVE and useful for reconciliation.

### Haitian ARV figure for 2013 (notes line 2055)
- The 2014 and 2016 reports give no ARV enrolment figure. The 2015 report puts the Haitian figure under hiv_reg_new2 within 13 of the MSPP count of new enrolees in pre-ART and ART care. If the same reporting held in 2013, the who_tme figure of 24,117 counts enrolment in HIV care and the MSPP figure of 18,705 counts enrolment on ARV, which would account for the gap of 5,412. The 2013 report gives no pre-ART figure to test the account. The account is plausible and NOT VERIFIED, and the 2013 count stays NOT SETTLED.

Next downloads. The Rapport Statistique MSPP 2017 (1,401,135 bytes) and 2018 (1,823,662 bytes), to see whether the enrolment table and the SALVH case table return, the Bolivian year-end bulletins, and earlier volumes of the Trinidad and Tobago development estimates once Jason rules on OCR.

## ROUND TWO. Download pass two continued, the Haitian MSPP statistical reports for 2017 and 2018, LAC entries (8 October 2026)

Files. Two downloads on 8 October 2026 under Jason's permission of 7 October 2026, saved to the scratchpad folder dl and recorded in dl2.json, every size equal to the HEAD size of round two (notes line 1720). hti_rapport_stat_2017.pdf 1,401,135 bytes (sha256 bd82389f045e) and hti_rapport_stat_2018.pdf 1,823,662 bytes (sha256 d6a26947bdb9), from www.mspp.gouv.ht. Text layer read with pypdf and with no OCR. Checks as in the r2q section (notes line 2115), in hti_r2r_parse.py and hti_r2r_parse.json.

### Rapport Statistique MSPP 2017
- Contents. 60 pages. The text layer splits department numbers across lines, so only the total rows are parsed. HIV cases diagnosed in 2017 24,610, people tested 1,291,214, cumulative notified cases 289,332, people active on ARV 84,526 at 31 December 2016 and 94,376 at 31 December 2017, and 39,996 people with a viral-load test. No page carries the word "enrôlés" or "enrôlées".
- Status. The national case count of 24,610 for 2017 is ADDITIVE under the indicator of notified HIV cases (notes line 2063), because the PAHO dashboard starts in 2018 (notes line 852). GRADE 2. The department rows of 2017 are NOT VERIFIED, because the text layer breaks the numbers.

### Rapport Statistique MSPP 2018
- Contents. 70 pages. Tables 3.4.2, 3.4.3 and 3.4.4 by department for 2018. The report text dates the Haitian adoption of "Tester et Traiter" (test and treat) to 2017.
- Table 3.4.2. HIV cases diagnosed 18,731 (seven not located), people tested 958,265 and people tested who know the result 927,249, source "MSPP-PNLS/NASTAD-Haïti- SALVH". The printed positivity equals cases over people tested. Nord-Est prints 41,592 who know the result against 40,815 tested.
- Table 3.4.3. Cases diagnosed 18,731, cumulative notified cases 308,063 and "Nombre de nouveaux patients enrôlés sous ARV" (new patients enrolled on ARV) 19,543, source "SALVH, NASTAD-Haïti / Mesi".
- Table 3.4.4. People active on ARV at 31 December 2018 91,514 and 58.3% of active patients virally suppressed, source "www.mesi.ht". The viral-load column reads 70,104 under the header "Cumul de patients ayant un test de charge virale" (cumulative patients with a viral-load test), while the report text on PDF page 48 gives 70,104 as the number of people with a viral-load test in 2018 against 39,996 in 2017. Whether the 70,104 figure counts 2018 alone or all years is NOT SETTLED.
- Panel comparison, ART enrolment, 2018. The who_tme art_initiations row (hiv_reg_new2) reads 20,245, 702 above the MSPP count of new patients enrolled on ARV (3.6%). The 10 pepfar_snu art_initiations rows (MER TX_NEW) sum to 20,247, two above the WHO figure. PEPFAR is higher than MSPP in seven departments and lower in Grande-Anse, Nord-Est and Nord-Ouest.
- Panel comparison, people on ART, 2018. The 10 pepfar_snu on_art_count rows (MER TX_CURR) sum to 101,597 against 91,514 active at MSPP, higher in eight departments and lower in Grande-Anse and Nord-Ouest. The national on_art_count rows for 2018 read 62,000 from unaids_aidsinfo and 61,905 from who_gho. The MSPP text gives 91,500 active at the end of 2018. The gap between the MSPP count of about 91,500 and the UNAIDS figure of 62,000 is NOT SETTLED.
- Panel comparison, testing and cases, 2018. The pepfar_snu testing rows sum to 932,109 against 958,265 at MSPP. The pepfar_snu new_diagnoses rows (MER HTS_TST_POS) sum to 21,773 against 18,724 MSPP cases placed in a department, a count of positive test results against a count of diagnosed cases.
- Additive test. The department case counts of 2018 are ADDITIVE AT admin1 under the indicator of notified HIV cases, since the PEPFAR department rows count positive results. Whether the national count of 18,731 equals PAHO indicator 93 for 2018 is NOT VERIFIED. GRADE 2. The department rows of ART enrolment, people on ART and testing are a second source for the pepfar_snu rows of 2018, NOT ADDITIVE and useful for reconciliation.

### Haitian ARV figure for 2013 (notes line 2055)
- In 2018, after test and treat, the MSPP count of new patients enrolled on ARV sits 702 below the who_tme figure (3.6%). In 2013 the MSPP count of 18,705 sits 5,412 below the who_tme figure of 24,117 (28.9%). In 2015 the who_tme figure sits within 13 of the MSPP count of new enrolees in pre-ART and ART care (notes line 2129). The figures of 2013, 2015 and 2018 fit a reading of the who_tme figures for 2013 and 2015 as enrolment in HIV care with pre-ART included and of the MSPP figure of 18,705 as enrolment on ARV. The reading stays NOT VERIFIED, because no source gives the pre-ART count for 2013. The 2013 count stays NOT SETTLED, and the question for Jason on the definition of the HTI art_initiations rows (notes line 2129) gains the years 2013-2016, the years before test and treat.

Next downloads. The MSPP statistical reports for 2020, 2021, 2022 and 2023 (notes line 1720), for department case counts after 2018, then the Bolivian year-end bulletins, and earlier volumes of the Trinidad and Tobago development estimates once Jason rules on OCR.

## ROUND TWO. Download pass two continued, the Haitian MSPP statistical reports for 2020 to 2023, LAC entries (8 October 2026)

Files. Four downloads on 8 October 2026 under Jason's permission of 7 October 2026, saved to the scratchpad folder dl and recorded in dl2.json, every size equal to the HEAD size of round two (notes line 1720). hti_rapport_stat_2020.pdf 3,060,944 bytes (sha256 a68eb34c8850), hti_rapport_stat_2021.pdf 2,756,588 bytes (sha256 f73f1df895a6), hti_rapport_stat_2022.pdf 2,299,058 bytes (sha256 94412fa46f06) and hti_rapport_stat_2023.pdf 1,821,690 bytes (sha256 f8db4c6609a3), from www.mspp.gouv.ht. Text layer read with pypdf and with no OCR. Checks in hti_r2s_parse.py and hti_r2s_parse.json. Every department row is the only reading of the printed digits whose columns sum to the printed TOTAL row, every printed positivity rate equals cases over people tested to one decimal, and the column of people tested in every positivity table equals the total column of the testing table.

### Tables read
- 2020 report, 107 pages, Tables 44 to 47 on PDF pages 80 to 83. 2021 report, 93 pages, Tables 41 to 44 on PDF pages 68 to 71. 2022 report, 109 pages, Tables 49 to 52 on PDF pages 79 to 82. 2023 report, 124 pages, Tables 52 to 55 on PDF pages 93 to 96. All four reports give the 10 departments and a TOTAL row, with sources among MSPP-PNLS, PNLS, SALVH and www.mesi.ht.
- National totals for 2020, 2021, 2022 and 2023. People tested who know the result 547,694, 415,602, 404,843 and 411,497. HIV-positive people 18,666, 14,695, 11,973 and 13,940. New patients enrolled on ARV 17,703, 14,622, 11,873 and 13,433. People active on ARV at 31 December 122,033, 127,421, 111,133 and 121,147. The testing tables split people tested into pregnant women seen in antenatal care or maternity and all other people.
- Enrolment tables for 2020, 2021 and 2022 add the enrolment performance and the 12-month retention on ARV by department. The 2023 enrolment table adds the enrolment performance and a column with a truncated header, summing to 3,561, which the report text describes as treatment interruptions.

### Data quality
- 2020 headers. The headers of Table 45 put cases before people tested, but the first column equals the Table 44 totals and the printed positivity equals the second column over the first. The title and headers of Table 46 describe new unique cases and cumulative notified cases, but the first column sums to 17,703, the count the report text gives as people initiated on ARV in 2020, and the second column equals enrolees over cases, rounded and capped at 100, in all 10 departments and the TOTAL row. The 2020 department figures therefore rest on arithmetic and on the report text, not on the printed headers.
- 2020 viral load. The viral-load column of Table 47 sums to the printed 99,294, but exceeds the active count in six departments, and Ouest prints 1,687 against 57,390 active. The department viral-load counts of 2020 are NOT VERIFIED.
- Deduplication from 2022. The 2022 report text describes the deduplication of the HIV-positive people of 2022 with a matching algorithm, and attributes the fall in new enrolees on ARV from 14,622 to 11,873 to the removal of duplicates. The same text gives 103,919 unique patients in the electronic systems against 111,133 active. The MSPP case and enrolment series break between 2021 and 2022, and every row carried from the reports needs a flag for the break in extra.
- 2023 report. The enrolment performance column differs from enrolees over cases in nine of 11 rows, and the viral-load column of Table 55 is a percentage. The report text gives the suppression rate of 86.0% for the end of 2022 in the section on 2023.
- Numbers printed without a thousands space. 2021 Sud-Est people tested 10756, 2022 Ouest cases 4758, and 2023 Sud and Sud-Est active 7356 and 2879, read by the column sums. The 2022 report text gives 407,681 people tested in 2021, against the 2021 table total of 415,602.

### Panel comparison, national, 2020 to 2023
- ART enrolment. The who_tme art_initiations rows (hiv_reg_new2) read 17,835, 14,598, 11,930 and 12,892, against the MSPP enrolees of 17,703, 14,622, 11,873 and 13,433, a difference of 132, minus 24, 57 and minus 541. The WHO figure for 2022 sits within 57 of the deduplicated MSPP count. The pepfar_snu department rows sum to 17,425, 14,934, 13,743 and 13,069.
- People on ART. The unaids_aidsinfo on_art_count rows read 100,000, 110,000, 110,000 and 120,000, 22,033 and 17,421 below the MSPP active count in 2020 and 2021 and 1,133 and 1,147 below in 2022 and 2023. The global_fund rows read 121,999, 127,379, 131,064 and 137,657, within 34 and 42 of MSPP in 2020 and 2021 and 19,931 and 16,510 above in 2022 and 2023. The pepfar_snu department rows sum to 116,829, 125,438, 131,226 and 137,106. The 2018 gap at notes line 2159 stays NOT SETTLED.
- Cases and positive tests. The global_fund new_diagnoses rows (number of HIV-positive tests) read 14,954, 14,302 and 13,802 for 2021 to 2023, and the pepfar_snu department rows sum to 18,098, 14,983, 15,002 and 14,865, against the MSPP counts of positive people of 18,666, 14,695, 11,973 and 13,940.
- Testing. The pepfar_snu department rows sum to 543,509, 433,705, 378,903 and 360,295. The unaids_aidsinfo row for 2023 reads 410,717, within 780 of the MSPP count of 411,497. Whether the PEPFAR department years follow the calendar year stays NOT VERIFIED.

### Additive tests
- Department counts of HIV-positive people, 2020 to 2023. ADDITIVE AT admin1 under the indicator of notified HIV cases (notes line 2063), since the PEPFAR department rows count positive results, with the 2022 break and the 2020 header error flagged in extra. GRADE 2. Whether the national counts equal PAHO indicator 93 (notes line 852) is NOT VERIFIED.
- Department enrolment on ARV, people active on ARV and people tested, 2020 to 2023. A second source for the pepfar_snu rows, NOT ADDITIVE and useful for reconciliation.
- Department 12-month retention on ARV, 2020 to 2022. POSSIBLY ADDITIVE, because the panel holds no retention indicator.
- Department counts of pregnant women tested, 2020 to 2023. POSSIBLY ADDITIVE, because the panel holds anc_hiv_testing_pct as a percentage and no count of pregnant women tested.

Next reads. The national PMTCT tables (2020 Table 48, 2021 Table 45, 2022 Table 53, 2023 Table 56) against the panel PMTCT rows, and the department TB/HIV tables (2020 Table 52, 2021 Table 49, 2022 Table 60, 2023 Table 61) against the tb_patients_hiv_tested and tb_patients_hiv_positive rows, from the same four files. Section r2r sits at notes line 2145.

## ROUND TWO. Download pass two continued, the TB/HIV tables of the Haitian MSPP statistical reports for 2020 to 2023, LAC entries (8 October 2026)

Files. No new download. The MSPP statistical reports for 2020 to 2023 downloaded in section r2s (notes line 2168), text layer read with pypdf and with no OCR. Checks in hti_r2t_parse.py and hti_r2t_parse.json. Every department column sums to the printed TOTAL row, and every printed percentage equals the count over the co-infected patients, rounded, with one rounding difference (2022 Sud prints 86.3 for 86.25).
- Tables. 2020 Table 52 (PDF page 88), 2021 Table 49 (PDF page 76) and 2022 Table 60 (PDF page 90) give, by department, TB/HIV co-infected patients, co-infected patients on cotrimoxazole and co-infected patients on ARV. Sources "Traqueur TB / DHIS2" for 2020 and 2021 and the PNLT (the national TB programme) for 2022. National totals of co-infected patients 1,585, 1,492 and 1,595, on cotrimoxazole 1,420, 1,399 and 1,452, on ARV 1,444, 1,385 and 1,419. The 2023 report gives national figures only, in Table 61 (PDF page 100, source PNLT), with 10,127 TB patients tested for HIV, 1,389 co-infected patients, 1,184 co-infected patients on ARV, 71 co-infected patients aged under 15 and 56 co-infected patients aged under 15 on ARV.
- Panel comparison. The national who_tme tb_patients_hiv_positive rows read 1,507, 1,414, 1,544 and 1,389 for 2020 to 2023, the tb_patients_hiv_tested rows read 11,273, 9,768, 10,598 and 10,127, and the tbhiv_on_art rows read 1,283, 1,303, 1,388 and 1,184. The MSPP counts of co-infected patients sit 78, 78 and 51 above the WHO rows for 2020, 2021 and 2022, and the MSPP counts on ARV sit 161, 82 and 31 above. Every figure of the 2023 Table 61 equals a who_tme row, with the counts aged under 15 equal to the rows for the age group 0-14 (newrel_hivpos_014 and newrel_art_014). The panel holds no department TB/HIV row for Haiti and no tbhiv_on_cpt row for Haiti. The only tbhiv_on_cpt rows in the panel are three Global Fund rows for 2017 and 2018.
- Additive test. The 2023 Table 61 is a DUPLICATE of the who_tme rows. The department counts of co-infected patients and of co-infected patients on ARV, 2020 to 2022, are ADDITIVE AT admin1 under tb_patients_hiv_positive and tbhiv_on_art, as for the 2015 Table 36 (section r2q, notes line 2115). The counts of co-infected patients on cotrimoxazole, 2020 to 2022, are ADDITIVE under tbhiv_on_cpt at national level and AT admin1. GRADE 2. The national gap against WHO, 51 to 78 co-infected patients and 31 to 161 patients on ARV, is NOT SETTLED, so every department row needs a note in extra naming the MSPP table as the source and the WHO national row as a different count.

## ROUND TWO. Download pass two continued, the PMTCT and Spectrum tables of the Haitian MSPP statistical reports for 2020 to 2023, LAC entries (8 October 2026)

Files. No new download. The MSPP statistical reports for 2020 to 2023 downloaded in section r2s (notes line 2168), text layer read with pypdf and with no OCR. hti_r2u_parse.py asserts every figure below as a string printed on the page, and hti_r2u_parse.json stores the figures. PMTCT (prevention of mother-to-child transmission) results sit in 2020 Table 48 (PDF page 83), 2021 Table 45 (PDF page 71), 2022 Table 53 (PDF page 82) and 2023 Table 56 (PDF page 96). Spectrum estimates sit in 2020 Table 49 (PDF page 85), 2021 Table 46 (PDF page 72), 2022 Table 54 (PDF page 84) and 2023 Table 57 (PDF page 98). The PMTCT tables name MESI (the national HIV data system at www.mesi.ht) as the source of the counts and UEP-MSPP (the studies and programming unit of the ministry) as the source of the estimate of pregnant women.
- Pregnant women on ARV. Women on ARV seen in antenatal care 2,535, 2,460, 2,213 and 2,013 for 2020 to 2023. New HIV-positive pregnant women receiving ARV 1,601, 1,560, 1,466 and 1,651. The tables print no total. The sums of women on ARV seen in antenatal care and new HIV-positive pregnant women receiving ARV, 4,136, 4,020, 3,679 and 3,664, compare with the unaids_aidsinfo pmtct_arv_count rows of 4,448, 4,223, 3,834 and 3,664 and the global_fund rows of 4,134, 4,007, 3,537 and 3,324. The 2023 sum equals the UNAIDS row, and the 2020 sum sits two above the Global Fund row. Whether women on ARV seen in antenatal care and new HIV-positive pregnant women overlap is NOT VERIFIED.
- PMTCT coverage. The MSPP tables print 71%, 87%, 62% and 63%, with the source printed as "MESI/Estimations" and no denominator. The unaids_aidsinfo pmtct_coverage_pct rows read 84, 78, 70 and 67. No printed count reproduces the MSPP percentage. NOT VERIFIED.
- Pregnant women tested. Women seen in antenatal care and tested for HIV 148,400, 150,000 and 131,200 for 2020 to 2022, and for 2023 pregnant women tested with known HIV status 172,187. Women seen in maternity with known HIV status 41,000, 38,700, 33,000 and 31,119. For 2020 to 2022 the antenatal and maternity counts add to 189,400, 188,700 and 164,200, within 100 of the pregnant women in the department testing tables of section r2s (189,434, 188,634 and 164,300), consistent with the same counts rounded to the nearest hundred. The 2023 count of 172,187 differs from the testing-table total of 169,169 and from the testing-table total less the maternity count. NOT SETTLED. The estimate of pregnant women reads 336,000 in every year from 2020 to 2023. The department totals over 336,000 give 56%, 56%, 49% and 50%, against unaids_aidsinfo anc_hiv_testing_pct rows of 87, 83, 84 and 81, so the UNAIDS percentage uses a different numerator or denominator. NOT SETTLED.
- Exposed infants. Registered HIV-exposed infants 3,544, 3,432, 3,135 and 2,682. Percentage of exposed infants testing HIV-positive 4.8, 3.7, 3.3 and 2.8. Percentage of exposed infants put on ARV within 72 hours 92, 90, 93 and 91. The panel early_infant_diagnosis_pct rows (unaids_aidsinfo 49, 47, 54 and 37) count infants tested within two months of birth, a different measure. No panel id holds registered exposed infants or infant ARV prophylaxis.
- Other rows. HIV seroprevalence among women seen in antenatal care 2.8%, 2.6%, 2.8% and 2.7%, and the percentage of pregnant women seen at a first antenatal visit 72, 75, 75 and 64. No panel id holds the antenatal seroprevalence or the first-visit percentage. Mother-to-child transmission at six weeks reads 11% for 2022 and 16.6% for 2023, from Spectrum, against the unaids_aidsinfo vertical_transmission_pct rows of 18 and 19.
- Spectrum tables. People living with HIV 153,000, 150,000, 140,000 and 145,000 against the unaids_aidsinfo plhiv rows of 130,000, 140,000, 140,000 and 140,000. New infections 5,000, 4,400, 6,600 and 5,600 against 7,000, 6,600, 6,700 and 6,200. Deaths due to HIV 2,200, 1,400, 1,600 and 1,500 against the unaids_aidsinfo aids_deaths rows of 1,800, 1,400, 1,300 and 1,300. ARV coverage of children 45%, 63%, 50% and 51% against the who_gho art_coverage_pct rows for ages 0-14 of 45, 45, 46 and 45. Prevalence among people aged 15 to 49 for 2023 1.6 against 1.7.
- Additive test. The Spectrum rows and the transmission rate at six weeks are EARLIER ROUND, NOT ADDITIVE, as for the modelled PANCAP rows (notes line 1389). The coverage percentages stay NOT ADDITIVE while NOT VERIFIED. The rounded counts of pregnant women tested are NOT ADDITIVE, because the department testing tables give the exact counts (POSSIBLY ADDITIVE in section r2s). The national sums of women on ARV for 2020 to 2022 are POSSIBLY ADDITIVE as a second national source of pmtct_arv_count, subject to Jason's ruling on a figure made by adding two printed counts and to a reading of the MESI definitions on whether women on ARV seen in antenatal care and new HIV-positive pregnant women overlap. The 2023 sum is a DUPLICATE of the UNAIDS row. Registered exposed infants, infant ARV prophylaxis, the antenatal seroprevalence and the first-visit percentage fit no panel id and stay NOT ADDITIVE, with registered exposed infants and infant ARV prophylaxis as candidates for the indicator proposals of the LAC feasibility note.

## ROUND TWO. Download pass two continued, the Bolivian year-end bulletins and the MSyD epidemiology yearbooks of 2015 and 2016, LAC entries (8 October 2026)

Method. Under Jason's permission for all necessary downloads, dl2.py fetched four files from www.minsalud.gob.bo, the site of the MSyD (Ministerio de Salud y Deportes, the Bolivian health ministry), into the scratchpad and recorded URL, HTTP status, bytes and SHA-256 hash in dl2.json. r2h_bol.py read the listing pages of the MSyD file store (the jDownloads component of the MSyD site) as HTML only. bol_yb_parse.py asserts every yearbook figure below against text printed on the page, with no OCR, and stores the figures in bol_yb_parse.json. build_r2v_section.py repeats the checks and adds a read-only pass over the panel CSV.
- Files. Parte Epidemiológico (the weekly notifiable-event bulletin) for week 52 of 2018, 1,320,877 bytes, fd823f8606e6. Parte Epidemiológico for week 52 of 2019, 922,477 bytes, 63d5e7564b99. Revista Epidemiológica 2015, 10,135,004 bytes, 50b372619417. Anuario Epidemiología 2016, served under the filename ANUARIO_2017_EPIDEMIOLOGIA.pdf, 7,192,405 bytes, 37058ec803ca. Every downloaded size equals the expected size recorded before the download.
- Week-52 bulletins of 2018 and 2019. The bulletins of 2018 and 2019 run to five pages apiece and list notifiable events, with measles, dengue and influenza among the events. The text layers of the 2018 and 2019 bulletins hold none of the strings "VIH", "SIDA" or "ITS" (the Spanish abbreviations for HIV, AIDS and sexually transmitted infections). NEGATIVE for HIV.
- Listings. The root pages of the MSyD file store list 71 categories. With the parameter Itemid=465 the category pages answer with HTTP 200, against the HTTP 404 replies recorded in notes line 1845. The category of the Parte Epidemiológico series runs to 30 listing pages, and the last page holds the bulletin for week nine of year 14 of the series. The latest posting date in the listing of notes line 1845 is 3 March 2020. The category of the 2020 Boletín Informativo holds weekly information bulletins, unread, from the first week, 20 to 26 April 2020, to week 33, 30 November to 6 December 2020. The category of weekly bulletins holds 26 bulletins of 2026, and the category of 2024 bulletins holds the bulletin for week 27 of 2024 only. The category named Boletines holds no file. The yearbook category (Folletos Epidemiológicos) holds the yearbooks of 2015 and 2016 only. The category of the national STI/HIV/AIDS programme holds 11 clinical guidelines and manuals and no statistical report.
- Year-end bulletins. The bulletin categories read hold no bulletin for week 52 or week 53 of any year from 2020 to 2025, so the annual department count asked for in notes line 2050 is NOT REACHABLE on the MSyD site. A request to the MSyD for the closing bulletins of 2020 to 2025, or for the SIMONE surveillance extracts behind the bulletins, is a lead for Jason.
- Yearbook of 2016, national series. A chart on page 80 prints notified cases for every year from 1990 to 2016, split into cases notified with HIV and cases notified in the AIDS phase. The years 2014 to 2016 read 1,752 and 388 for 2014, 1,873 and 397 for 2015, and 1,920 and 459 for 2016. Page 79 gives a cumulative 17,871 cases, 14,501 with HIV and 3,370 in the AIDS phase. The chart series for 1990 to 2016 adds to 14,498 and 3,348, so 25 cases fall before 1990, the first year of the chart.
- Yearbook of 2016, departments. The table of page 82 gives notified cases for 2016 by department, from the "Programa Nacional ITS/VIH/SIDA-HV" (the national programme for STIs, HIV, AIDS and viral hepatitis). Cases with HIV and cases in the AIDS phase read La Paz 516 and 129, Santa Cruz 767 and 124, Cochabamba 323 and 89, Chuquisaca 86 and 14, Potosí 48 and 11, Oruro 71 and 44, Tarija 30 and 21, Beni 69 and 26, and Pando 10 with HIV and a single case in the AIDS phase. The department figures add to the national 1,920 and 459, and the cases with HIV and the cases in the AIDS phase together add to 2,379 cases notified in 2016.
- Yearbook of 2016, sex and age. A second table of page 82 gives the cases of 2016 as 1,661 men and 718 women, with no case of unknown sex, total 2,379. By age group the cases read 53 under 15, 822 aged 15 to 24, 711 aged 25 to 34, 390 aged 35 to 44 and 403 aged 45 and over, total 2,379. In the cumulative columns of the same table, the row of unknown age prints a total of 117 against parts adding to 185, a gap of 68. The age chart on page 82 is titled for 2016 but prints shares within five cases of the cumulative column for 1984 to 2016, not shares of the 2016 cases, so the age chart stays out.
- Yearbook of 2016, other figures. Page 84 reports HIV testing for 87% of expected pregnancies in 2016. Page 74 reports 258 TB patients with HIV in 2016 and HIV testing for 86.7% of TB patients.
- Yearbook of 2015, data to 2014. Page 58 gives 1,704 cases notified with HIV and 383 in the AIDS phase for 2014, total 2,087, and the table of page 61 splits the 2014 cases into 1,369 men and 718 women. The 2014 and 2016 tables print the same total of 718 women, but the counts of women differ in every age group from 15 to 24 upwards, so the equal totals are not a copied column. The 2016 yearbook revises the 2014 counts to 1,752 and 388, total 2,140. Page 59 gives cumulative cases for 1984 to 2014 by department, total 13,180, as a text table, and the table of 2014 cases by department on page 60 is an image with no text layer. Page 64 reports 4,062 people with HIV receiving ARV treatment. A table on page 71 gives HIV rapid tests among TB patients and TB/HIV co-infected cases for 2009 to 2014 as 871 and 62, 1,961 and 107, 4,198 and 144, 5,146 and 167, 5,908 and 170, and 6,090 and 216.
- Cumulative tables. The cumulative total grows by 4,691 from the 2015 yearbook to the 2016 yearbook, against 4,649 cases printed for 2015 and 2016, a gap of 42. A department count for 2015 found by subtracting the cumulative tables would carry the gap of 42 and the 2014 revision, so no department count for 2015 is derived.
- Panel. The panel holds no BOL row at admin1, no BOL new_diagnoses row and no BOL row of notified cases. The who_tme rows of tb_patients_hiv_positive and tb_patients_hiv_tested for BOL start in 2015, with 241 co-infected and 6,012 tested for 2016, against 258 co-infected in the yearbook. The on_art_count rows for 2014 read 3,803 (who_gho) and 3,800 (unaids_aidsinfo), against 4,062 in the 2015 yearbook. The unaids_aidsinfo anc_hiv_testing_pct rows read 94 for 2015 and 84 for 2017, with no row for 2016.
- Additive test. The notified cases of 2016 by department are ADDITIVE AT admin1, and the national total and the split by sex and age group are ADDITIVE, under the indicator id of notified HIV cases in Jason's decision (notes line 2063). GRADE 2. The split into cases with HIV and cases in the AIDS phase goes in extra while the AIDS-case indicator is held. The national series of 1990 to 2016 from the chart of page 80 is ADDITIVE under the same id as the latest printed round, GRADE 2, with the 2014 revision noted in extra. The 2014 counts and the 2014 split by sex of the 2015 yearbook are EARLIER ROUND and NOT ADDITIVE. The TB/HIV counts of 2009 to 2014 are POSSIBLY ADDITIVE under tb_patients_hiv_positive and tb_patients_hiv_tested for years with no panel row, NOT SETTLED until the 2016 gap of 17 co-infected cases against who_tme is explained. The 4,062 people on ARV treatment are NOT ADDITIVE while the gap of 259 against who_gho is NOT SETTLED. The testing share of 87% of expected pregnancies is POSSIBLY ADDITIVE under anc_hiv_testing_pct for 2016, NOT VERIFIED, because the yearbook prints no numerator or denominator.
- Decision for Jason. The who_tme file may hold TB/HIV counts for 2009 to 2014 under a variable of an earlier WHO reporting form. Jason may check the who_tme file for BOL before 2015, since the rule on reads keeps data/raw/who_tme closed to the assistant.
- Leads. The SUIS category (Sistema Único de Información en Salud, the national health information system) of the MSyD file store holds a statistical report on births and deaths for 2019 to 2023 and a mortality profile of Bolivia for 2022. The statistical report and the mortality profile are unread and are leads for HIV deaths once Jason and Adrian decide the source class for registered deaths. The bulletin of the STI/HIV programme of SEDES La Paz (the departmental health service of La Paz) in notes line 452 is unread and may hold counts for the department of La Paz in 2024. A Los Tiempos report (a Cochabamba newspaper) of 2 December 2025 gives 605 HIV cases in Cochabamba in 2025, a press figure only, UNVERIFIED.

## ROUND TWO. Download pass two continued, the STI/HIV bulletin of SEDES La Paz, LAC entries (8 October 2026)

Method. Under Jason's permission for all necessary downloads, dl2.py fetched the bulletin of the STI/HIV programme of SEDES La Paz (the departmental health service of La Paz) named in notes line 452 and in the leads of notes line 2232. pypdf read the text layer, and build_r2w_section.py asserts every quoted figure against the text layer and adds a read-only pass over the panel CSV.
- File. bol_sedes_lapaz_its_vih_2024.pdf, from www.sedeslapaz.gob.bo, uploaded in October 2024, 4,079,636 bytes, df3dc44238ac, equal to the size from the earlier HEAD request.
- Content. The bulletin runs to 12 pages. Eight pages carry narrative text, and four pages carry under 100 characters of text apiece, mostly titles of diagnostic algorithms. The text layer gives the period as 1987 to 2018 for the CDVIR LP (the departmental HIV surveillance, information and referral centre of La Paz) and names no year after 2018. The charts cite the SIMONE software 13 times and also cite the CDVIR pharmacy, the CDVIR laboratory, the national programme and the authors. No chart value reaches the text layer, so the bulletin holds no printed count by year or by municipality.
- National cascade of 2018. Citing the national programme, the bulletin gives 22,000 people with HIV estimated for Bolivia, 93% diagnosed, and 18,402 people alive among the notified cases, 54% with access to ARV treatment. The panel row of plhiv for BOL in 2018 reads 26,000 (unaids_aidsinfo, range 22,000 to 32,000), so the figure of 22,000 equals the lower bound of the unaids_aidsinfo range and may come from an earlier round of estimates, NOT VERIFIED. The share of 54% applied to 18,402 gives about 9,937 people on treatment, a derived figure within 34 of the who_gho on_art_count of 9,971 for 2018, against 10,000 (unaids_aidsinfo) and 9,797 (global_fund). DUPLICATE in substance and NOT ADDITIVE.
- La Paz cascade of 2018. The CDVIR LP sets the cascade targets from the 3,357 people notified with HIV in La Paz up to 2018, with 3,021 people as the diagnosis target, and reports 86% diagnosed and alive, 70% linked to care, 56% retained, 55% on treatment and 46% with viral suppression below 1,000 copies per ml. The denominators are notified cases, not estimates of people with HIV, so the La Paz percentages do not match the definitions of the panel cascade indicators. NOT ADDITIVE. The yearbook of 2016 gives 2,967 cases with HIV in La Paz from 1984 to 2016 and 516 cases with HIV in 2016 alone (section r2v), so the CDVIR LP total of 3,357 up to 2018 would leave 390 cases for 2017 and 2018 together. The CDVIR LP count and the yearbook count therefore cover different sets of cases, NOT SETTLED.
- Result. The bulletin gives no department count for 2020 to 2025 and closes the lead of notes line 2232. The 2024 counts for La Paz from search snippets in notes line 451 stay UNVERIFIED.

## ROUND TWO. Download pass two continued, the PNLS information sheets of March 2024 and December 2024, LAC entries (8 October 2026)

Method. Under Jason's permission for all necessary downloads, dl2.py fetched two information sheets of the PNLS (Programme National de Lutte contre les IST/VIH/SIDA, the Haitian national STI/HIV/AIDS programme) from the publications list of the MSPP site in notes line 824. pypdf read the text layers, and build_r2x_section.py asserts every quoted figure against the text layer and adds a read-only pass over the panel CSV.
- Files. hti_feuillet_pnls_2024_03.pdf, 166,671 bytes, 5643908faa9e. hti_feuillet_informatif_2024_12.pdf, 1,067,128 bytes, 1d9c61124b7b. The byte counts of the two downloads equal the expected sizes recorded in dl2.json, and the size of the sheet of March 2024 equals the listing in notes line 824.
- Sheet of March 2024. The sheet of March 2024 runs to two pages of images with no text layer. Under the rule against OCR the sheet of March 2024 stays out of the panel.
- Sheet of December 2024. The sheet of December 2024 is titled for the response statistics of October 2023 to September 2024 and runs to two pages with a text layer. The programme counts cite data systems named on the sheet as Radar, MESI and SISNU, with no expansion of the names on the sheet, and the PNLT (the national TB programme), the estimates cite the Estimations 2024, and the key population figures cite the IBBS of 2023 (the integrated bio-behavioural survey).
- Treatment and PrEP. The sheet gives 18,063 people newly enrolled on PrEP, 12,408 people newly placed on ARV treatment, 124,177 patients active on ARV treatment on 30 September 2024 and 3,221 children on ARV treatment. The panel rows for 2024 read prep_recipients 18,039 (pepfar_panorama) and 33,000 (unaids_aidsinfo), art_initiations 12,219 (global_fund), 11,927 (pepfar_panorama) and 12,238 (who_tme), on_art_count 125,491 (global_fund), 138,770 (pepfar_panorama), 130,000 (unaids_aidsinfo) and 126,780 (who_gho), and on_art_count for children under 15 of 3,108 (who_gho). The PrEP count sits 24 above the pepfar_panorama row for the panel year 2024. NOT ADDITIVE, because the panel already holds rows from at least two sources for every indicator named in the treatment and PrEP line.
- Key populations. The IBBS of 2023 gives size estimates of 87,645 sex workers, 48,868 men who have sex with men and 3,232 transgender people, with HIV prevalence of 8.5%, 9.4% and 34.8%. The unaids_aidsinfo rows for 2024 read 87,600, 48,900 and 3,200 for size and 8.6%, 10.2% and 34.8% for prevalence. The size estimates are DUPLICATE after rounding. The prevalence among men who have sex with men differs by 0.8 points, NOT SETTLED, and the key population prevalence figures are NOT ADDITIVE.
- TB/HIV. The sheet gives 1,184 incident TB cases with HIV receiving ARV and TB treatment in 2023, citing the PNLT, equal to the who_tme tbhiv_on_art row of 1,184 for 2023. DUPLICATE.
- PMTCT. For October 2023 to September 2024 the sheet gives 193,600 pregnant women seen at a first antenatal visit (SISNU), 124,207 pregnant women with known HIV status at the first visit, 1,478 pregnant women newly diagnosed with HIV (MESI), 3,135 pregnant women with HIV, known before or newly diagnosed, 3,134 pregnant women with HIV on ARV, 2,450 infants born to women with HIV, 71% of the infants with ARV prophylaxis within 72 hours, 2,450 infants with a first PCR test between birth and 12 months and 68 infants confirmed with HIV by the first PCR test. The pmtct_arv_count rows for 2024 read 3,238 (unaids_aidsinfo and who_gho), 3,096 (global_fund) and 2,997 (pepfar_panorama), so the count of 3,134 is NOT ADDITIVE. The counts of exposed infants, of infants with a first PCR test and of infants confirmed with HIV fit no panel id (notes line 2211) and stay NOT ADDITIVE, as candidates for the indicator proposals of the LAC feasibility note (notes line 2214), with a caution on the fiscal year of the sheet, October to September. The equal counts of 2,450 exposed infants and 2,450 infants with a first PCR test are printed as given and need a check against a second MSPP source before any use.
- Estimates. Under the Estimations 2024 the sheet gives for 2023 145,000 people with HIV, 1,500 AIDS deaths and 5,600 new HIV infections. The panel rows for 2023 read plhiv 140,000 (unaids_aidsinfo and who_gho), aids_deaths 1,300 (unaids_aidsinfo) and 1,400 (who_gho), and new_infections 6,200 (unaids_aidsinfo) and 5,500 (who_gho). The sheet figures belong to a different round of the national estimates, NOT ADDITIVE.

## DECISIONS OF 12 OCTOBER 2026, open questions of the Phase 5 draft

Jason's reply of 12 October 2026 to the open questions of the Phase 5 draft reads "Follow your recommendations". Recorded as the decisions below, one per question.
- OCR decision. No figure read by OCR enters the panel, and the ACCESS_LADDER rule against OCR of scanned PDFs stands (notes line 2099). The Trinidad and Tobago development-programme items for 2022 to 2024 stay NOT ADDITIVE (notes line 2106). Reason. The subtotal test checks the sum of a block of rows and leaves the split between rows untested, so two errors that cancel inside a block pass the test, and the series at stake is a single allocation series for three years in a country the World Bank lists as high income.
- MSyD request decision. Jason sends the request to the MSyD for the closing bulletins of 2020 to 2025 or for the SIMONE extracts (notes line 2222). The draft of the request is research/phase5_lac/msyd_request_draft.md. The search sends no message.
- AIDSinfo decision. Jason re-exports the 146 AIDSinfo files from aidsinfo.unaids.org and reruns the panel (notes line 1674). Reason. The unaids_aidsinfo rows sit an estimates round behind in every region (notes line 1671).
- sica.int decision. The search makes no use of Wayback Machine copies of sica.int, because sica.int answers with an F5 block page and an archived copy would route around a live block (notes lines 1395 and 1618). COMISCA stays BLOCKED.
- Brazil budget decision. The search sends no further query to orcamento.dados.gov.br, and every gov.br host stays off-limits (notes line 1879). The 2025 difference of R$ 318,458,127 between the SPARQL and portal paid totals stays NOT SETTLED (notes line 1091).
- Registered-death routes decision. The request to ABS or STATIN for a list of dataZoa tables and the WHO Mortality Database class sweep wait on the ruling of Jason and Adrian about the source class of registered deaths, because the STATIN and ABS series found so far are registered deaths (notes lines 650, 1620, 2019 and 2071).
- Scope decision. The LAC list keeps the 23 countries of regions.py for Phase 5. The World Bank country API (api.worldbank.org/v2/country, read on 12 October 2026) lists CRI, GUY, PAN and TTO as High income, lists CHL and URY as High income, and lists the other 19 LAC countries as upper middle income or lower middle income. The regions.py docstring excludes high-income countries, so the docstring and the LAC list disagree for CRI, GUY, PAN and TTO. A change to the LAC list moves the site counts and waits on Jason and Adrian at the publication of the LAC region page. Every Phase 5 finding for CRI, GUY, PAN and TTO is read with the income level in view.
