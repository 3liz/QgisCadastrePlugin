CREATE TABLE bati (tmp text);
CREATE TABLE lloc (tmp text);
CREATE TABLE nbat (tmp text);
CREATE TABLE pdll (tmp text);
CREATE TABLE prop (tmp text);

CREATE TABLE topo (
    ogc_fid serial,
    code_topo character varying,
    nature_de_voie character varying,
    libelle character varying,
    type_commune_actuel_r_ou_n character varying,
    type_commune_fip_r_ou_nfip character varying,
    rur_actuel character varying,
    rur_fip character varying,
    caractere_voie character varying,
    annulation character varying,
    date_annulation character varying,
    date_creation_de_article character varying,
    type_voie character varying,
    mot_classant character varying,
    date_derniere_transition character varying
);

CREATE TABLE parcelle (
    parcelle text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    ccopre text,
    ccosec text,
    dnupla text,
    dcntpa integer,
    dsrpar text,
    dnupro text,
    comptecommunal text,
    jdatat text,
    dreflf text,
    gpdl text,
    cprsecr text,
    ccosecr text,
    dnuplar text,
    dnupdl text,
    pdl text,
    gurbpa text,
    dparpi text,
    ccoarp text,
    gparnf text,
    gparbat text,
    parrev text,
    gpardp text,
    fviti text,
    dnvoiri text,
    dindic text,
    ccovoi text,
    ccoriv text,
    voie text,
    ccocif text,
    ccpper text,
    gpafpd text,
    ajoutcoherence text,
    cconvo text,
    dvoilib text,
    ccocomm text,
    ccoprem text,
    ccosecm text,
    dnuplam text,
    parcellefiliation text,
    type_filiation text,
    ccoifp integer,
    inspireid text,
    lot text
);

CREATE TABLE suf (
    suf text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    ccopre text,
    ccosec text,
    dnupla text,
    parcelle text,
    ccosub text,
    dcntsf integer,
    dnupro text,
    comptecommunal text,
    gnexps text,
    drcsub numeric(10,2),
    drcsuba numeric(10,2),
    ccostn text,
    cgrnum text,
    dsgrpf text,
    dclssf text,
    cnatsp text,
    drgpos text,
    ccoprel text,
    ccosecl text,
    dnuplal text,
    dnupdl text,
    pdl text,
    dnulot text,
    rclsi text,
    gnidom text,
    topja text,
    datja text,
    postel text,
    ccortar integer,
    lot text
);

CREATE TABLE sufexoneration (
    sufexoneration text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    ccopre text,
    ccosec text,
    dnupla text,
    ccosub text,
    suf text,
    rnuexn text,
    vecexn numeric(10,2),
    ccolloc text,
    pexn integer,
    gnexts text,
    jandeb text,
    jfinex text,
    fcexn text,
    fcexna text,
    rcexna text,
    rcexnba numeric(10,2),
    mpexnba text,
    lot text
);

CREATE TABLE suftaxation (
    suftaxation text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    ccopre text,
    ccosec text,
    dnupla text,
    ccosub text,
    suf text ,
    c1majposa numeric(10,2),
    c1bisufad numeric(10,2),
    c2majposa numeric(10,2),
    c2bisufad numeric(10,2),
    c3majposa numeric(10,2),
    c3bisufad numeric(10,2),
    c4majposa numeric(10,2),
    c4bisufad numeric(10,2),
    cntmajtc integer,
    majposca numeric(10,2),
    lot text
);

CREATE TABLE local00 (
    local00 text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    invar text,
    ccopre text,
    ccosec text,
    dnupla text,
    parcelle text,
    dnubat text,
    descr text,
    dniv text,
    dpor text,
    ccoriv text,
    voie text,
    ccovoi text,
    dnvoiri text,
    dindic text,
    ccocif text,
    dvoilib text,
    cleinvar text,
    assietf text,
    ccpper text,
    locinc text,
    codique text,
    lot text
);

CREATE TABLE local10 (
    local10 text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    invar text,
    local00 text,
    ccopre text,
    ccosec text,
    dnupla text,
    parcelle text,
    ccoriv text,
    voie text,
    ccovoi text,
    dnvoiri text,
    gpdl text,
    dsrpar text,
    dnupro text,
    comptecommunal text,
    jdatat text,
    dnufnl text,
    ccoeva text,
    ccitlv text,
    dteloc text,
    gtauom text,
    dcomrd text,
    ccoplc text,
    cconlc text,
    dvltrt integer,
    ccoape text,
    cc48lc text,
    dloy48a integer,
    top48a text,
    dnatlc text,
    dnupas text,
    gnexcf text,
    dtaucf text,
    cchpr text,
    jannat text,
    dnbniv text,
    hlmsem text,
    postel text,
    dnatcg text,
    jdatcgl text,
    dnutbx text,
    dvltla text,
    janloc text,
    ccsloc text,
    fburx integer,
    gimtom text,
    cbtabt text,
    jdtabt text,
    jrtabt text,
    jacloc text,
    cconac text,
    toprev text,
    ccoifp integer,
    lot text
);

CREATE TABLE pev (
    pev text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    invar text,
    local10 text,
    dnupev text,
    ccoaff text,
    ccostb text,
    dcapec text,
    dcetlc numeric(3,2),
    dcsplc text,
    dsupot integer,
    dvlper integer,
    dvlpera integer,
    gnexpl text,
    libocc text,
    ccthp text,
    retimp text,
    dnuref text,
    rclsst text,
    gnidom text,
    dcsglc text,
    ccogrb text,
    cocdi text,
    cosatp text,
    gsatp text,
    clocv text,
    dvltpe integer,
    dcralc text,
    dcsplca text,
    dcsglca text,
    dcralca text,
    topcn integer,
    tpevtieom integer,
    ccocac text,
    dnutrf text,
    dcfloc integer,
    ccortar integer,
    ccorvl text,
    dtaurv integer,
    dcmloc integer,
    jancmp text,
    lot text
);

CREATE TABLE pevexoneration (
    pevexoneration text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    invar text,
    Janbil text,
    dnupev text,
    pev text,
    dnuexb text,
    ccolloc text,
    pexb numeric(5,2),
    gnextl text,
    jandeb text,
    janimp text,
    vecdif text,
    vecdifa text,
    fcexb text,
    fcexba text,
    rcexba text,
    dvldif2 integer,
    dvldif2a integer,
    fcexb2 integer,
    fcexba2 integer,
    rcexba2 integer,
    valplaf text,
    lot text
);

CREATE TABLE pevexoneration_imposable (
    pevexoneration_imposable text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    invar text,
    Janbil text,
    dnupev text,
    pev text,
    dnuexb text,
    ccolloc text,
    pexb numeric(5,2),
    gnextl text,
    jandeb text,
    janimp text,
    vecdif text,
    vecdifa text,
    fcexb text,
    fcexba text,
    rcexba text,
    dvldif2 integer,
    dvldif2a integer,
    fcexb2 integer,
    fcexba2 integer,
    rcexba2 integer,
    valplaf text,
    lot text
);

CREATE TABLE pevexoneration_imposee (
    pevexoneration_imposee text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    invar text,
    Janbil text,
    dnupev text,
    pev text,
    dnuexb text,
    ccolloc text,
    pexb numeric(5,2),
    gnextl text,
    jandeb text,
    janimp text,
    vecdif text,
    vecdifa text,
    fcexb text,
    fcexba text,
    rcexba text,
    dvldif2 integer,
    dvldif2a integer,
    fcexb2 integer,
    fcexba2 integer,
    rcexba2 integer,
    valplaf text,
    lot text
);

CREATE TABLE pevtaxation (
    pevtaxation text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    invar text,
    janbil text,
    dnupev text,
    pev text,
    co_vlbai integer,
    co_vlbaia integer,
    co_bipevla integer,
    de_vlbai integer,
    de_vlbaia integer,
    de_bipevla integer,
    re_vlbai integer,
    re_vlbaia integer,
    re_bipevla integer,
    gp_vlbai integer,
    gp_vlbaia integer,
    gp_bipevla integer,
    bateom integer,
    baomec integer,
    tse_vlbai integer,
    tse_vlbaia integer,
    tse_bipevla integer,
    mvltieomx integer,
    pvltieom bigint,
    lot text
);

CREATE TABLE pevprincipale (
    pevprincipale text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    invar text,
    dnupev text,
    pev text,
    dnudes text,
    dep1_cconad text,
    dep1_dsueic integer,
    dep1_dcimei numeric(2,1),
    dep2_cconad text,
    dep2_dsueic integer,
    dep2_dcimei numeric(2,1),
    dep3_cconad text,
    dep3_dsueic integer,
    dep3_dcimei numeric(2,1),
    dep4_cconad text,
    dep4_dsueic integer,
    dep4_dcimei numeric(2,1),
    geaulc text,
    gelelc text,
    gesclc text,
    ggazlc text,
    gasclc text,
    gchclc text,
    gvorlc text,
    gteglc text,
    dnbbai text,
    dnbdou text,
    dnblav text,
    dnbwc text,
    deqdha integer,
    dnbppr text,
    dnbsam text,
    dnbcha text,
    dnbcu8 text,
    dnbcu9 text,
    dnbsea text,
    dnbann text,
    dnbpdc text,
    dsupdc integer,
    dmatgm text,
    dmatto text,
    jannat text,
    detent text,
    dnbniv text,
    lot text
);

CREATE TABLE pevprofessionnelle (
    pevprofessionnelle text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    invar text,
    dnupev text,
    pev text,
    dnudes text,
    vsupot text,
    vsurz1 text,
    vsurz2 text,
    vsurz3 text,
    vsurzt integer,
    vsurb1 text,
    vsurb2 text,
    dsupot text,
    dsup1 text,
    dsup2 text,
    dsup3 text,
    dsupk1 text,
    dsupk2 text,
    lot text
);

CREATE TABLE pevlissage (
    pevlissage text,
    annee  text,
    ccodep text,
    ccodir text,
    ccocom text,
    invar  text,
    dnupev text,
    pev    text, -- dnupec dans doc DGFiP
    mlbcom integer,
    mlbsyn integer,
    mlbcu integer,
    mlbdep integer,
    mlbts1 integer,
    mlbts2 integer,
    mlbtas integer,
    mlbgem integer,
    mlbtom integer,
    tbfpas integer,
    mlbtfc integer,
    lot text
);

CREATE TABLE pevdependances (
    pevdependances text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    invar text,
    dnupev text,
    pev text,
    dnudes text,
    dsudep integer,
    cconad text,
    asitet text,
    dmatgm text,
    dmatto text,
    detent text,
    geaulc text,
    gelelc text,
    gchclc text,
    dnbbai text,
    dnbdou text,
    dnblav text,
    dnbwc text,
    deqtlc integer,
    dcimlc numeric(2,1),
    dcetde numeric(3,2),
    dcspde text,
    dcspdea text,
    lot text
);

CREATE TABLE proprietaire (
    id serial NOT NULL,
    proprietaire text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    dnupro text,
    comptecommunal text,
    dnulp text,
    ccocif text,
    dnuper text,
    ccodro text,
    ccodem text,
    gdesip text,
    gtoper text,
    ccoqua text,
    gnexcf text,
    dtaucf text,
    dnatpr text,
    ccogrm text,
    dsglpm text,
    dforme text,
    ddenom text,
    gtyp3 text,
    dlign3 text,
    gtyp4 text,
    dlign4 text,
    gtyp5 text,
    dlign5 text,
    gtyp6 text,
    dlign6 text,
    ccopay text,
    ccodep1a2 text,
    ccodira text,
    ccocom_adr text,
    ccovoi text,
    ccoriv text,
    dnvoiri text,
    dindic text,
    ccopos text,
    dnirpp text,
    dqualp text,
    dnomlp text,
    dprnlp text,
    jdatnss text,
    dldnss text,
    epxnee text,
    dnomcp text,
    dprncp text,
    topcdi text,
    oriard text,
    fixard text,
    datadr text,
    topdec text,
    datdec text,
    dsiren text,
    ccmm text,
    topja text,
    datja text,
    anospi text,
    cblpmo text,
    gtodge text,
    gpctf text,
    gpctsb text,
    jmodge text,
    jandge text,
    jantfc text,
    jantbc text,
    dformjur text,
    dnomus text,
    dprnus text,
    lot text
);

CREATE TABLE comptecommunal (
    comptecommunal text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    dnupro text,
    ajoutcoherence text,
    lot text
);


CREATE TABLE pdl (
    pdl text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    ccopre text,
    ccosec text,
    dnupla text,
    parcelle text,
    dnupdl text,
    dnivim text,
    ctpdl text,
    dmrpdl text,
    gprmut text,
    dnupro text,
    comptecommunal text,
    ccocif text,
    lot text
);

CREATE TABLE parcellecomposante(
    parcellecomposante text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    ccopre text,
    ccosec text,
    dnupla text,
    parcelle text,
    dnupdl text,
    pdl text,
    ccoprea text,
    ccoseca text,
    dnuplaa text,
    parcellea text,
    ccocif text,
    lot text
);

CREATE TABLE lots (
    lots text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    ccopre text,
    ccosec text,
    dnupla text,
    parcelle text,
    dnupdl text,
    pdl text,
    dnulot text,
    cconlo text,
    dcntlo integer,
    dnumql integer,
    ddenql integer,
    dfilot text,
    datact text,
    dnuprol text,
    comptecommunal text,
    dreflf text,
    ccocif text,
    lot text
);

CREATE TABLE lotslocaux (
    lotslocaux text,
    annee text,
    ccodepl text,
    ccodirl text,
    ccocoml text,
    ccoprel text,
    ccosecl text,
    dnuplal text,
    dnupdl text,
    dnulot text,
    lots text,
    ccodebpb text,
    ccodird text,
    ccocomb text,
    ccopreb text,
    invloc text,
    local00 text,
    local10 text,
    dnumql text,
    ddenql text,
    lot text
);

CREATE TABLE commune_majic(
    commune text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    libcom text,
    lot text
);

CREATE TABLE commune (
    commune text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    clerivili text,
    libcom text,
    typcom text,
    ruract text,
    carvoi text,
    indpop text,
    poprel integer,
    poppart integer,
    popfict integer,
    annul text,
    dteannul text,
    dtecreart text,
    codvoi text,
    typvoi text,
    indldnbat text,
    motclas text,
    geo_commune text,
    lot text
);

CREATE TABLE voie (
    voie text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    commune text,
    natvoiriv text,
    ccoriv text,
    clerivili text,
    natvoi text,
    libvoi text,
    typcom text,
    ruract text,
    carvoi text,
    indpop text,
    poprel text,
    poppart integer,
    popfict integer,
    annul text,
    dteannul text,
    dtecreart text,
    codvoi text,
    typvoi text,
    indldnbat text,
    motclas text,
    lot text
);

-- Tables de nomenclature
CREATE TABLE gpdl (gpdl text primary key,gpdl_lib text);
CREATE TABLE gnexps (gnexps text primary key,gnexps_lib text );
CREATE TABLE cgrnum ( cgrnum text primary key,cgrnum_lib text );
CREATE TABLE dsgrpf (dsgrpf text primary key, dsgrpf_lib text);
CREATE TABLE cnatsp (cnatsp text primary key, cnatsp_lib text);
CREATE TABLE ccolloc (ccolloc text primary key, ccolloc_lib text);
CREATE TABLE gnexts (gnexts text primary key, gnexts_lib text);
CREATE TABLE ccoeva (ccoeva text primary key, ccoeva_lib text);
CREATE TABLE dteloc (dteloc text primary key, dteloc_lib text);
CREATE TABLE ccoplc (ccoplc text primary key, ccoplc_lib text);
CREATE TABLE cconlc (cconlc text primary key, cconlc_lib text);
CREATE TABLE top48a (top48a text primary key, top48a_lib text);
CREATE TABLE dnatlc (dnatlc text primary key, dnatlc_lib text);
CREATE TABLE dnatcg (dnatcg text primary key, dnatcg_lib text);
CREATE TABLE gimtom (gimtom text primary key, gimtom_lib text);
CREATE TABLE hlmsem (hlmsem text primary key, hlmsem_lib text);
CREATE TABLE ccoaff (ccoaff text primary key, ccoaff_lib text);
CREATE TABLE gnexpl (gnexpl text primary key, gnexpl_lib text);
CREATE TABLE cbtabt (cbtabt text primary key, cbtabt_lib text);
CREATE TABLE gnextl (gnextl text primary key, gnextl_lib text);
CREATE TABLE ccthp (ccthp text primary key, ccthp_lib text);
CREATE TABLE cconad (cconad text primary key, cconad_lib text);
CREATE TABLE ctpdl (ctpdl text primary key, ctpdl_lib text);
CREATE TABLE cconlo (cconlo text primary key, cconlo_lib text);
CREATE TABLE ccodro (ccodro text primary key, ccodro_lib text);
CREATE TABLE ccodem (ccodem text primary key, ccodem_lib text);
CREATE TABLE gtoper (gtoper text primary key, gtoper_lib text);
CREATE TABLE ccoqua (ccoqua text primary key, ccoqua_lib text);
CREATE TABLE dnatpr (dnatpr text primary key, dnatpr_lib text);
CREATE TABLE ccogrm (ccogrm text primary key, ccogrm_lib text);
CREATE TABLE gtyp3 (gtyp3 text primary key, gtyp3_lib text);
CREATE TABLE gtyp4 (gtyp4 text primary key, gtyp4_lib text);
CREATE TABLE gtyp5 (gtyp5 text primary key, gtyp5_lib text);
CREATE TABLE gtyp6 (gtyp6 text primary key, gtyp6_lib text);
CREATE TABLE typcom (typcom text primary key, typcom_lib text);
CREATE TABLE natvoi (natvoi text primary key, natvoi_lib text);
CREATE TABLE natvoiriv (natvoiriv text primary key, natvoiriv_lib text);
CREATE TABLE carvoi (carvoi text primary key, carvoi_lib text);
CREATE TABLE annul (annul text primary key, annul_lib text);
CREATE TABLE typvoi (typvoi text primary key, typvoi_lib text);
CREATE TABLE indldnbat (indldnbat text primary key, indldnbat_lib text);
CREATE TABLE dformjur (dformjur text primary key, formjur text, libformjur text);
CREATE TABLE ccocac (ccocac text primary key, ccocac_lib text);
CREATE TABLE cconac (cconac text primary key, cconac_lib text);
CREATE TABLE dmatgm (dmatgm text primary key, dmatgm_lib text);
CREATE TABLE dmatto (dmatto text primary key, dmatto_lib text);
CREATE TABLE drgpos (dgrpos text primary key, dgrpos_lib text);
CREATE TABLE detent (detent text primary key, detent_lib text);
CREATE TABLE type_filiation (type_filiation text primary key, type_filiation_lib text);
CREATE TABLE fburx (fburx text primary key, fburx_lib text);

CREATE TABLE geo_commune
(
  geo_commune text NOT NULL,
  annee text NOT NULL,
  object_rid text,
  idu text,
  tex2 text,
  creat_date date,
  update_dat date,
  commune text,
  lot text,
  ogc_fid serial NOT NULL
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_commune', 'geom', ${SRID} , 'MULTIPOLYGON', 2 );



CREATE TABLE geo_section
(
  geo_section text NOT NULL,
  annee text NOT NULL,
  object_rid text,
  idu text,
  tex text,
  geo_commune text NOT NULL,
  creat_date date,
  update_dat date,
  lot text,
  ogc_fid serial NOT NULL
)
;
SELECT AddGeometryColumn ( current_schema::text, 'geo_section', 'geom', ${SRID} , 'MULTIPOLYGON', 2 );


CREATE TABLE geo_qupl (geo_qupl text PRIMARY KEY,geo_qupl_lib text);
CREATE TABLE geo_copl (geo_copl text PRIMARY KEY,geo_copl_lib text);
CREATE TABLE geo_inp (geo_inp text PRIMARY KEY,geo_inp_lib text);

CREATE TABLE geo_subdsect
(
  geo_subdsect text NOT NULL,
  annee text NOT NULL,
  object_rid text,
  idu text,
  geo_section text NOT NULL,
  geo_qupl text,
  geo_copl text,
  eor integer,
  dedi date,
  icl integer,
  dis date,
  geo_inp text,
  dred date,
  creat_date date,
  update_dat date,
  lot text,
  ogc_fid serial NOT NULL
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_subdsect', 'geom', ${SRID} , 'MULTIPOLYGON', 2 );


CREATE TABLE geo_indp (geo_indp text,geo_indp_lib text);
ALTER TABLE geo_indp ADD PRIMARY KEY (geo_indp);

CREATE TABLE geo_parcelle
(
  geo_parcelle text NOT NULL,
  annee text NOT NULL,
  object_rid text,
  idu text,
  geo_section text NOT NULL,
  geo_subdsect text,
  supf numeric,
  geo_indp text,
  coar text,
  tex text,
  tex2 text,
  codm text,
  creat_date date,
  update_dat date,
  inspireid text,
  lot text,
  ogc_fid serial NOT NULL
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_parcelle', 'geom', ${SRID} , 'MULTIPOLYGON', 2 );

CREATE VIEW v_geo_parcelle AS
SELECT g.*, p.comptecommunal, p.voie
FROM geo_parcelle g
LEFT OUTER JOIN parcelle p ON g.geo_parcelle = p.parcelle;

CREATE TABLE geo_subdfisc
(
  geo_subdfisc serial NOT NULL,
  annee text NOT NULL,
  object_rid text,
  tex text,
  creat_date date,
  update_dat date,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_subdfisc', 'geom', ${SRID} , 'MULTIPOLYGON', 2 );


CREATE TABLE geo_subdfisc_parcelle
(
  geo_subdfisc_parcelle serial NOT NULL,
  annee text NOT NULL,
  geo_subdfisc integer NOT NULL,
  geo_parcelle text NOT NULL
);

CREATE TABLE geo_voiep
(
  geo_voiep serial NOT NULL,
  annee text NOT NULL,
  object_rid text,
  tex text,
  creat_date date,
  update_dat date,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_voiep', 'geom', ${SRID} , 'POINT', 2 );


CREATE TABLE geo_numvoie
(
  geo_numvoie serial NOT NULL,
  annee text NOT NULL,
  object_rid text,
  tex text,
  creat_date date,
  update_dat date,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_numvoie', 'geom', ${SRID} , 'POINT', 2 );


CREATE TABLE geo_numvoie_parcelle
(
  geo_numvoie_parcelle serial NOT NULL,
  annee text NOT NULL,
  geo_numvoie integer NOT NULL,
  geo_parcelle text NOT NULL
);

CREATE TABLE geo_lieudit
(
  geo_lieudit serial NOT NULL,
  annee text NOT NULL,
  object_rid text,
  tex text,
  creat_date date,
  update_dat date,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_lieudit', 'geom', ${SRID} , 'MULTIPOLYGON', 2 );


CREATE TABLE geo_dur (geo_dur text,geo_dur_lib text);
ALTER TABLE geo_dur ADD PRIMARY KEY (geo_dur);

CREATE TABLE geo_batiment
(
  geo_batiment text NOT NULL,
  annee text NOT NULL,
  object_rid text,
  geo_dur text,
  tex text,
  creat_date date,
  update_dat date,
  lot text,
  ogc_fid serial NOT NULL
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_batiment', 'geom', ${SRID} , 'MULTIPOLYGON', 2 );


CREATE TABLE geo_batiment_parcelle
(
  geo_batiment_parcelle serial NOT NULL,
  annee text NOT NULL,
  geo_batiment text NOT NULL,
  geo_parcelle text NOT NULL
);

CREATE TABLE geo_zoncommuni
(
  geo_zoncommuni serial NOT NULL,
  annee text NOT NULL,
  object_rid text,
  tex text,
  creat_date date,
  update_dat date,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_zoncommuni', 'geom', ${SRID} , 'MULTILINESTRING', 2 );


CREATE TABLE geo_tronfluv
(
  geo_tronfluv serial NOT NULL,
  annee text NOT NULL,
  object_rid text,
  tex text,
  creat_date date,
  update_dat date,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_tronfluv', 'geom', ${SRID} , 'MULTIPOLYGON', 2 );


CREATE TABLE geo_tronroute
(
  geo_tronroute serial NOT NULL,
  annee text NOT NULL,
  object_rid text,
  tex text,
  creat_date date,
  update_dat date,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_tronroute', 'geom', ${SRID} , 'MULTIPOLYGON', 2 );


CREATE TABLE geo_can (geo_can text,geo_can_lib text);
ALTER TABLE geo_can ADD PRIMARY KEY (geo_can);
CREATE TABLE geo_ppln (geo_ppln text,geo_ppln_lib text);
ALTER TABLE geo_ppln ADD PRIMARY KEY (geo_ppln);
CREATE TABLE geo_palt (geo_palt text,geo_palt_lib text);
ALTER TABLE geo_palt ADD PRIMARY KEY (geo_palt);
CREATE TABLE geo_map (geo_map text,geo_map_lib text);
ALTER TABLE geo_map ADD PRIMARY KEY (geo_map);
CREATE TABLE geo_sym (geo_sym text,geo_sym_lib text);
ALTER TABLE geo_sym ADD PRIMARY KEY (geo_sym);

CREATE TABLE geo_ptcanv
(
  geo_ptcanv serial NOT NULL,
  annee text NOT NULL,
  object_rid text,
  idu text,
  geo_can text,
  geo_ppln text,
  geo_palt text,
  geo_map text,
  geo_sym text,
  creat_date date,
  update_dat date,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_ptcanv', 'geom', ${SRID} , 'POINT', 2 );


CREATE TABLE geo_borne
(
  geo_borne serial NOT NULL,
  annee text NOT NULL,
  object_rid text,
  creat_date date,
  update_dat date,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_borne', 'geom', ${SRID} , 'POINT', 2 );


CREATE TABLE geo_borne_parcelle
(
  geo_borne_parcelle serial NOT NULL,
  annee text NOT NULL,
  geo_borne integer NOT NULL,
  geo_parcelle text NOT NULL
);

CREATE TABLE geo_croix
(
  geo_croix serial NOT NULL,
  annee text NOT NULL,
  object_rid text,
  creat_date date,
  update_dat date,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_croix', 'geom', ${SRID} , 'POINT', 2 );


CREATE TABLE geo_croix_parcelle
(
  geo_croix_parcelle serial NOT NULL,
  annee text NOT NULL,
  geo_croix integer NOT NULL,
  geo_parcelle text NOT NULL
);

CREATE TABLE geo_symblim
(
  geo_symblim serial NOT NULL,
  annee text NOT NULL,
  object_rid text,
  ori numeric(12,9),
  geo_sym  text,
  creat_date date,
  update_dat date,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_symblim', 'geom', ${SRID} , 'POINT', 2 );


CREATE TABLE geo_symblim_parcelle
(
  geo_symblim_parcelle serial NOT NULL,
  annee text NOT NULL,
  geo_symblim integer NOT NULL,
  geo_parcelle text NOT NULL
);

CREATE TABLE geo_tpoint
(
  geo_tpoint serial NOT NULL,
  annee text NOT NULL,
  object_rid text,
  ori numeric(12,9),
  tex text,
  geo_sym  text,
  creat_date date,
  update_dat date,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_tpoint', 'geom', ${SRID} , 'POINT', 2 );


CREATE TABLE geo_tpoint_commune
(
  geo_tpoint_commune serial NOT NULL,
  annee text NOT NULL,
  geo_tpoint integer NOT NULL,
  geo_commune text NOT NULL
);

CREATE TABLE geo_tline
(
  geo_tline serial NOT NULL,
  annee text NOT NULL,
  object_rid text,
  tex text,
  geo_sym  text,
  creat_date date,
  update_dat date,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_tline', 'geom', ${SRID} , 'MULTILINESTRING', 2 );


CREATE TABLE geo_tline_commune
(
  geo_tline_commune serial NOT NULL,
  annee text NOT NULL,
  geo_tline integer NOT NULL,
  geo_commune text NOT NULL
);

CREATE TABLE geo_tsurf
(
  geo_tsurf serial NOT NULL,
  annee text NOT NULL,
  object_rid text,
  tex text,
  geo_sym  text,
  creat_date date,
  update_dat date,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_tsurf', 'geom', ${SRID} , 'MULTIPOLYGON', 2 );


CREATE TABLE geo_tsurf_commune
(
  geo_tsurf_commune serial NOT NULL,
  annee text NOT NULL,
  geo_tsurf integer NOT NULL,
  geo_commune text NOT NULL
);


CREATE TABLE geo_label
(
  ogc_fid serial NOT NULL,
  object_rid text,
  fon text,
  hei numeric(24,15),
  tyu text,
  cef numeric(24,15),
  csp numeric(24,15),
  di1 numeric(24,15),
  di2 numeric(24,15),
  di3 numeric(24,15),
  di4 numeric(24,15),
  tpa text,
  hta text,
  vta text,
  atr text,
  ogr_obj_lnk text,
  ogr_obj_lnk_layer text,
  ogr_atr_val text,
  ogr_angle double precision,
  ogr_font_size double precision,
  x_label numeric,
  y_label numeric
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_label', 'geom', ${SRID} , 'POINT', 2 );


CREATE TABLE edigeo_rel ( edigeo_rel serial,nom text,de text,vers text);
ALTER TABLE edigeo_rel ADD PRIMARY KEY (edigeo_rel );


CREATE TABLE geo_unite_fonciere
(
  id serial NOT NULL,
  comptecommunal text,
  annee text NOT NULL,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_unite_fonciere', 'geom', ${SRID} , 'MULTIPOLYGON', 2 );

-- Création la table parcelle_info ( EDIGEO + MAJIC )
CREATE TABLE parcelle_info
(
  ogc_fid integer,
  geo_parcelle text,
  idu text,
  tex text,
  geo_section text,
  nomcommune text,
  codecommune text,
  surface_geo bigint,
  contenance bigint,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'parcelle_info', 'geom', ${SRID} , 'MULTIPOLYGON', 2 );

-- COMMENTS

COMMENT ON TABLE parcelle IS 'Article descriptif de parcelle';
COMMENT ON COLUMN parcelle.ccodep IS 'Code département - ';
COMMENT ON COLUMN parcelle.ccodir IS 'Code direction - ';
COMMENT ON COLUMN parcelle.ccocom IS 'Code commune INSEE ou DGI d’arrondissement - ';
COMMENT ON COLUMN parcelle.ccopre IS 'Préfixe de section ou quartier servi pour les communes associées. - ';
COMMENT ON COLUMN parcelle.ccosec IS 'Section cadastrale - ';
COMMENT ON COLUMN parcelle.dnupla IS 'Numéro de plan - ';
COMMENT ON COLUMN parcelle.dcntpa IS 'Contenance de la parcelle - en centiares';
COMMENT ON COLUMN parcelle.dsrpar IS 'Lettre de série-role - INDISPONIBLE depuis 2018';
COMMENT ON COLUMN parcelle.dnupro IS 'Compte communal du propriétaire de la parcelle - ';
COMMENT ON COLUMN parcelle.jdatat IS 'Date de l acte - jjmmaaaa';
COMMENT ON COLUMN parcelle.dreflf IS 'Référence au Livre Foncier en Alsace-Moselle - ';
COMMENT ON COLUMN parcelle.gpdl IS 'Indicateur d’appartenance à pdl Identifiant de la pdl - cf. détail supra si gpdl =2';
COMMENT ON COLUMN parcelle.cprsecr IS 'Préfixe de la parcelle de référence - ';
COMMENT ON COLUMN parcelle.ccosecr IS 'Section de la parcelle de référence - ';
COMMENT ON COLUMN parcelle.dnuplar IS 'N° de plan de la parcelle de référence - ';
COMMENT ON COLUMN parcelle.dnupdl IS 'Numéro d’ordre de la pdl - en général, 001';
COMMENT ON COLUMN parcelle.gurbpa IS 'Caractère Urbain de la parcelle - U, * ou blanc';
COMMENT ON COLUMN parcelle.dparpi IS 'Numéro de parcelle primitive - ';
COMMENT ON COLUMN parcelle.ccoarp IS 'Indicateur d’arpentage - A ou blanc';
COMMENT ON COLUMN parcelle.gparnf IS 'Indicateur de parcelle non figurée au plan - 1 = figurée, 0 = non figurée';
COMMENT ON COLUMN parcelle.gparbat IS 'Indicateur de parcelle référençant un bâtiment - 1 = oui, sinon 0';
COMMENT ON COLUMN parcelle.parrev IS 'Info de la révision - INDISPONIBLE';
COMMENT ON COLUMN parcelle.gpardp IS 'parcelle n''appartenant pas au domaine public - INDISPONIBLE';
COMMENT ON COLUMN parcelle.fviti IS 'parcelle au casier viticole  Adresse de la parcelle - INDISPONIBLE';
COMMENT ON COLUMN parcelle.dnvoiri IS 'Numéro de voirie - ';
COMMENT ON COLUMN parcelle.dindic IS 'Indice de répétition - ';
COMMENT ON COLUMN parcelle.ccovoi IS 'Code Majic2 de la voie - ';
COMMENT ON COLUMN parcelle.ccoriv IS 'Code Rivoli de la voie - ';
COMMENT ON COLUMN parcelle.ccocif IS 'Code du cdif (code topad) - ';
COMMENT ON COLUMN parcelle.ccpper IS 'Code de la trésorerie (code TOPAD) - ';
COMMENT ON COLUMN parcelle.gpafpd IS 'Domanialité, représentation au plan - INDISPONIBLE';
COMMENT ON COLUMN parcelle.cconvo IS 'Code nature de la voie';
COMMENT ON COLUMN parcelle.dvoilib IS 'Libellé de la voie';
COMMENT ON COLUMN parcelle.ccocomm IS 'Code INSEE de la commune de la parcelle mère';
COMMENT ON COLUMN parcelle.ccoprem IS 'Code du préfixe de section de la parcelle mère';
COMMENT ON COLUMN parcelle.ccosecm IS 'Code section de la parcelle mère';
COMMENT ON COLUMN parcelle.dnuplam IS 'Numéro de plan de la parcelle mère';
COMMENT ON COLUMN parcelle.parcellefiliation IS 'Parcelle en filiation';
COMMENT ON COLUMN parcelle.type_filiation IS 'Type de filiation (D, R, T ou blanc)';
COMMENT ON COLUMN parcelle.ccoifp IS 'Code IFP';

COMMENT ON TABLE suf IS 'Article descriptif de suf';
COMMENT ON COLUMN suf.ccodep IS 'Code département - ';
COMMENT ON COLUMN suf.ccodir IS 'Code direction - ';
COMMENT ON COLUMN suf.ccocom IS 'Code commune INSEE ou DGI d’arrondissement - ';
COMMENT ON COLUMN suf.ccopre IS 'Préfixe de section ou quartier servi pour les communes associées - ';
COMMENT ON COLUMN suf.ccosec IS 'Section cadastrale - ';
COMMENT ON COLUMN suf.dnupla IS 'Numéro de plan - ';
COMMENT ON COLUMN suf.ccosub IS 'Lettres indicatives de suf - ';
COMMENT ON COLUMN suf.dcntsf IS 'Contenance de la suf - en centiares';
COMMENT ON COLUMN suf.dnupro IS 'Compte communal du propriétaire de la suf - ';
COMMENT ON COLUMN suf.gnexps IS 'Code exonération permanente - ep cd cr dr ni rt';
COMMENT ON COLUMN suf.drcsub IS 'Revenu cadastral en valeur actualise référence 1980 - Exprimé Euros';
COMMENT ON COLUMN suf.drcsuba IS 'Revenu cadastral revalorisé en valeur du 01-01 de l’année - Exprimé en Euros';
COMMENT ON COLUMN suf.ccostn IS 'Série-tarif - A à Z, sauf I,O,Q';
COMMENT ON COLUMN suf.cgrnum IS 'Groupe de nature de culture - 01 à 13';
COMMENT ON COLUMN suf.dsgrpf IS 'Sous-groupe alphabétique - ';
COMMENT ON COLUMN suf.dclssf IS 'Classe dans le groupe et la série-tarif - ';
COMMENT ON COLUMN suf.cnatsp IS 'code nature de culture spéciale - ';
COMMENT ON COLUMN suf.drgpos IS 'Top terrain constructible Liaison avec un lot de pdl - « 0 » ou « 1 » ';
COMMENT ON COLUMN suf.ccoprel IS 'Préfixe de la parcelle identifiant le lot - ';
COMMENT ON COLUMN suf.ccosecl IS 'Section de la parcelle identifiant le lot - ';
COMMENT ON COLUMN suf.dnuplal IS 'N° de plan de la parcelle de référence - ';
COMMENT ON COLUMN suf.dnupdl IS 'Numéro d ordre de la pdl - en général, 001';
COMMENT ON COLUMN suf.dnulot IS 'Numéro du lot - Le lot de BND se présente sous la forme 00Axxxx - ';
COMMENT ON COLUMN suf.rclsi IS 'Données classement révisé - INDISPONIBLE';
COMMENT ON COLUMN suf.gnidom IS 'Indicateur de suf non imposable - * ou blanc';
COMMENT ON COLUMN suf.topja IS 'Indicateur jeune agriculteur - J ou blanc';
COMMENT ON COLUMN suf.datja IS 'Date d’installation jeune agriculteur - peut être servie si topja = J';
COMMENT ON COLUMN suf.postel IS 'Indicateur de bien appartenant à la Poste - X ou blanc';
COMMENT ON COLUMN suf.ccortar IS 'Code commune origine du tarif';
COMMENT ON COLUMN suf.drgpos is 'Top terrain constructible Liaison avec un lot de pdl - « 0 » ou « 9 » ';

COMMENT ON TABLE sufexoneration IS 'Article exonération de suf';
COMMENT ON COLUMN sufexoneration.ccodep IS 'Code département - ';
COMMENT ON COLUMN sufexoneration.ccodir IS 'Code direction - ';
COMMENT ON COLUMN sufexoneration.ccocom IS 'Code commune INSEE ou DGI d’arrondissement - ';
COMMENT ON COLUMN sufexoneration.ccopre IS 'Préfixe de section ou quartier servi pour les communes associées - ';
COMMENT ON COLUMN sufexoneration.ccosec IS 'Section cadastrale - ';
COMMENT ON COLUMN sufexoneration.dnupla IS 'Numéro de plan - ';
COMMENT ON COLUMN sufexoneration.ccosub IS 'Lettres indicatives de suf - ';
COMMENT ON COLUMN sufexoneration.rnuexn IS 'Numéro d ordre d’exonération temporaire - 01 à 04';
COMMENT ON COLUMN sufexoneration.vecexn IS 'Montant de VL sur lequel porte l’exonération - en Euros';
COMMENT ON COLUMN sufexoneration.ccolloc IS 'Collectivité accordant l’exonération - TC, C, R d OU GC';
COMMENT ON COLUMN sufexoneration.pexn IS 'Pourcentage d’exonération - 100';
COMMENT ON COLUMN sufexoneration.gnexts IS 'Code d’exonération temporaire - TA TR NO PB PP PR PF ER TU OL HP HR ou NA';
COMMENT ON COLUMN sufexoneration.jandeb IS 'Année de début d’exonération - à blanc';
COMMENT ON COLUMN sufexoneration.jfinex IS 'Année de retour à imposition - à blanc';
COMMENT ON COLUMN sufexoneration.fcexn IS 'Fraction de vecsuf exonérée - INDISPONIBLE';
COMMENT ON COLUMN sufexoneration.fcexna IS 'fcexn en année N - INDISPONIBLE';
COMMENT ON COLUMN sufexoneration.rcexna IS 'revenu (4/5 fcexna) correspondant - INDISPONIBLE';
COMMENT ON COLUMN sufexoneration.rcexnba IS 'Revenu cadastral exonéré, en valeur de l’année - Exprimé en Euros';
COMMENT ON COLUMN sufexoneration.mpexnba IS 'Fraction majo TC exonérée, en valeur de l’année - INDISPONIBLE';
COMMENT ON TABLE suftaxation IS 'Article taxation de suf';
COMMENT ON COLUMN suftaxation.ccodep IS 'Code département - ';
COMMENT ON COLUMN suftaxation.ccodir IS 'Code direction - ';
COMMENT ON COLUMN suftaxation.ccocom IS 'Code commune INSEE ou DGI d’arrondissement - ';
COMMENT ON COLUMN suftaxation.ccopre IS 'Préfixe de section ou quartier servi pour les communes associées - ';
COMMENT ON COLUMN suftaxation.ccosec IS 'Section cadastrale - ';
COMMENT ON COLUMN suftaxation.dnupla IS 'Numéro de plan - ';
COMMENT ON COLUMN suftaxation.ccosub IS 'Lettres indicatives de suf - ';
COMMENT ON COLUMN suftaxation.c1majposa IS 'c1 - Montant de la majoration terrain constructible. Servi pour la part communale. Toujours à zéro pour autres collectivités. - exprimé en Euros';
COMMENT ON COLUMN suftaxation.c1bisufad IS 'c1 - Base d’imposition de la suf en valeur de l’année - exprimé en Euros';
COMMENT ON COLUMN suftaxation.c2majposa IS 'c2 - Montant de la majoration terrain constructible. Servi pour la part communale. Toujours à zéro pour autres collectivités. - exprimé en Euros';
COMMENT ON COLUMN suftaxation.c2bisufad IS 'c2 - Base d’imposition de la suf en valeur de l’année - exprimé en Euros';
COMMENT ON COLUMN suftaxation.c3majposa IS 'c3 - Montant de la majoration terrain constructible. Servi pour la part communale. Toujours à zéro pour autres collectivités. - exprimé en Euros';
COMMENT ON COLUMN suftaxation.c3bisufad IS 'c3 - Base d’imposition de la suf en valeur de l’année - exprimé en Euros';
COMMENT ON COLUMN suftaxation.c4majposa IS 'c4 - Montant de la majoration terrain constructible. Servi pour la part communale. Toujours à zéro pour autres collectivités. - exprimé en Euros';
COMMENT ON COLUMN suftaxation.c4bisufad IS 'c4 - Base d’imposition de la suf en valeur de l’année - exprimé en Euros';
COMMENT ON COLUMN suftaxation.cntmajtc IS 'Nouvelle contenance suf pour calcul majorationn TC';
COMMENT ON COLUMN suftaxation.majposca IS 'Majoration TC pour les chambres d’agriculture, exprimé en centimes d’Euros (à partir de 2014)';
COMMENT ON TABLE local00 IS 'Article identifiant du local';
COMMENT ON COLUMN local00.ccodep IS 'code département - ';
COMMENT ON COLUMN local00.ccodir IS 'code direction - ';
COMMENT ON COLUMN local00.ccocom IS 'code commune INSEE - ';
COMMENT ON COLUMN local00.invar IS 'numéro invariant - ';
COMMENT ON COLUMN local00.ccopre IS 'préfixe de section ou quartier servi pour les communes associées, - ';
COMMENT ON COLUMN local00.ccosec IS 'lettres de section - ';
COMMENT ON COLUMN local00.dnupla IS 'numéro de plan - ';
COMMENT ON COLUMN local00.dnubat IS 'lettre de bâtiment - ';
COMMENT ON COLUMN local00.descr IS 'numéro d’entrée - ';
COMMENT ON COLUMN local00.dniv IS 'niveau étage - ';
COMMENT ON COLUMN local00.dpor IS 'numéro de local - ';
COMMENT ON COLUMN local00.ccoriv IS 'Code Rivoli de la voie - ';
COMMENT ON COLUMN local00.ccovoi IS 'Code Majic2 de la voie - ';
COMMENT ON COLUMN local00.dnvoiri IS 'Numéro de voirie - ';
COMMENT ON COLUMN local00.dindic IS 'indice de répétition - ';
COMMENT ON COLUMN local00.ccocif IS 'code du cdi/cdif (code topad) - ';
COMMENT ON COLUMN local00.dvoilib IS 'libelle de la voie - ';
COMMENT ON COLUMN local00.cleinvar IS 'clé alpha no invariant - ';
COMMENT ON COLUMN local00.assietf IS 'Code SAGES du service gestionnaire de la taxe foncière';
COMMENT ON COLUMN local00.ccpper IS 'Code de trésorerie gestionnaire - ';
COMMENT ON COLUMN local00.locinc IS 'code local sans évaluation - INDISPONIBLE';
COMMENT ON COLUMN local00.codique IS 'Code codique du service de recouvrement de la TF';
COMMENT ON TABLE local10 IS 'Article identifiant du local';
COMMENT ON COLUMN local10.ccodep IS 'code département - ';
COMMENT ON COLUMN local10.ccodir IS 'code direction - ';
COMMENT ON COLUMN local10.ccocom IS 'code commune INSEE - ';
COMMENT ON COLUMN local10.invar IS 'numéro invariant - ';
COMMENT ON COLUMN local10.gpdl IS 'indicateur d’appartenance à un lot de pdl - 1 = oui, sinon 0';
COMMENT ON COLUMN local10.dsrpar IS 'lettre de série rôle - INDISPONIBLE';
COMMENT ON COLUMN local10.dnupro IS 'compte communal de propriétaire - ';
COMMENT ON COLUMN local10.jdatat IS 'date d’acte de mutation - jjmmaaaa';
COMMENT ON COLUMN local10.dnufnl IS 'compte communal de fonctionnaire logé - redevable de la tom';
COMMENT ON COLUMN local10.ccoeva IS 'code évaluation - A B C D E T tableau 2.3.1';
COMMENT ON COLUMN local10.ccitlv IS 'local imposable à la taxe sur les locaux vacants - indisponible';
COMMENT ON COLUMN local10.dteloc IS 'type de local - 1 à 8 tableau 2.3.2';
COMMENT ON COLUMN local10.gtauom IS 'zone de ramassage des ordures ménagères - P RA RB RC RD ou blanc';
COMMENT ON COLUMN local10.dcomrd IS 'Pourcentage de réduction sur tom - ';
COMMENT ON COLUMN local10.ccoplc IS 'Code de construction particulière - R U V W X Y Z ou blanc tabl. 2.3.3';
COMMENT ON COLUMN local10.cconlc IS 'Code nature de local - voir tableau 2.3.4';
COMMENT ON COLUMN local10.dvltrt IS 'Valeur locative totale retenue pour le local - ';
COMMENT ON COLUMN local10.ccoape IS 'Code NAF pour les locaux professionnels - ';
COMMENT ON COLUMN local10.cc48lc IS 'Catégorie de loi de 48 - ';
COMMENT ON COLUMN local10.dloy48a IS 'Loyer de 48 en valeur de l’année - ';
COMMENT ON COLUMN local10.top48a IS 'top taxation indiquant si la pev est impose au loyer ou a la vl - 1 = loyer o = vl';
COMMENT ON COLUMN local10.dnatlc IS 'Nature d occupation - A P V L T D tableau 2.3.6. ATTENTION: donnée plus restituée à compter du millésime 2025';
COMMENT ON COLUMN local10.dnupas IS 'no passerelle TH/TP - INDISPONIBLE';
COMMENT ON COLUMN local10.gnexcf IS 'code nature exo ecf - INDISPONIBLE';
COMMENT ON COLUMN local10.dtaucf IS 'taux exo ecf - INDISPONIBLE';
COMMENT ON COLUMN local10.cchpr IS 'Top indiquant une mutation propriétaire - * ou blanc';
COMMENT ON COLUMN local10.jannat IS 'Année de construction - ';
COMMENT ON COLUMN local10.dnbniv IS 'Nombre de niveaux de la construction - ';
COMMENT ON COLUMN local10.hlmsem IS 'Local appartenant à hlm ou sem - 5 = hlm, 6 = sem, sinon blanc';
COMMENT ON COLUMN local10.postel IS 'Local de Poste ou France Telecom - X, Y, Z, ou blanc ';
COMMENT ON COLUMN local10.dnutbx IS 'no gestionnaire déclarant taxe bureaux - INDISPONIBLE';
COMMENT ON COLUMN local10.dvltla IS 'VL totale du local actualisée - INDISPONIBLE';
COMMENT ON COLUMN local10.janloc IS 'Année de création du local - INDISPONIBLE';
COMMENT ON COLUMN local10.ccsloc IS 'Code cause création du local - INDISPONIBLE';
COMMENT ON COLUMN local10.fburx IS 'Indicateur présence bureaux - INDISPONIBLE';
COMMENT ON COLUMN local10.gimtom IS 'Indicateur imposition OM exploitable à partir de 2002  - D, E, V ou blanc';
COMMENT ON COLUMN local10.cbtabt IS 'Code exonération HLM zone sensible - ZS, ZT ou blanc';
COMMENT ON COLUMN local10.jdtabt IS 'Année début d’exonération ZS - ';
COMMENT ON COLUMN local10.jrtabt IS 'Année fin d’exonération ZS - ';
COMMENT ON COLUMN local10.jacloc IS 'Année d’achèvement du local - INDISPONIBLE';
COMMENT ON COLUMN local10.cconac IS 'Code NACE pour les locaux professionnels';
COMMENT ON COLUMN local10.dnatcg IS 'Code nature du changement d’évaluation (depuis 2013)';
COMMENT ON COLUMN local10.jdatcgl IS 'Date changement évaluation - JJMMSSAA (Depuis 2013)';
COMMENT ON COLUMN local10.toprev IS 'Top local révisé. 0 si non révisé, 1 si révisé.';
COMMENT ON COLUMN local10.ccoifp IS 'Code IFP';

COMMENT ON TABLE pev IS 'Article descriptif de pev';
COMMENT ON COLUMN pev.ccodep IS 'Code département - ';
COMMENT ON COLUMN pev.ccodir IS 'Code direction - ';
COMMENT ON COLUMN pev.ccocom IS 'Code commune INSEE - ';
COMMENT ON COLUMN pev.invar IS 'Numéro invariant - ';
COMMENT ON COLUMN pev.dnupev IS 'Numéro de pev - ';
COMMENT ON COLUMN pev.ccoaff IS 'Affectation de la pev - H P L S K tableau 2.3.7';
COMMENT ON COLUMN pev.ccostb IS 'lettre de série tarif bâtie ou secteur locatif - A à Z sauf';
COMMENT ON COLUMN pev.dcapec IS 'Catégorie - Commentaires 2.2.3';
COMMENT ON COLUMN pev.dcetlc IS 'Coefficient d entretien - 9V99';
COMMENT ON COLUMN pev.dcsplc IS 'Coefficient de situation particulière - S9V99 - INDISPONIBLE';
COMMENT ON COLUMN pev.dsupot IS 'Surface pondérée - Présence non systématique';
COMMENT ON COLUMN pev.dvlper IS 'Valeur locative de la pev, en valeur de référence (1970) sauf pour les établissements de code évaluation A - ';
COMMENT ON COLUMN pev.dvlpera IS 'Valeur locative de la pev, en valeur de l’année - ';
COMMENT ON COLUMN pev.gnexpl IS 'Nature d’exonération permanente - Gérée dans pour les tableau 2.3.8';
COMMENT ON COLUMN pev.libocc IS 'nom de l occupant INDISPONIBLE - ';
COMMENT ON COLUMN pev.ccthp IS 'Code occupation à la Th ou à la TP - ';
COMMENT ON COLUMN pev.retimp IS 'Top : retour partiel ou total à imposition - ';
COMMENT ON COLUMN pev.dnuref IS 'Numéro de local type - ';
COMMENT ON COLUMN pev.rclsst IS 'Données reclassement - INDISPONIBLE';
COMMENT ON COLUMN pev.gnidom IS 'Top : pev non imposable (Dom) - ';
COMMENT ON COLUMN pev.dcsglc IS 'Coefficient de situation générale - S9V99';
COMMENT ON COLUMN pev.ccogrb IS 'Code groupe bâti révisé - INDISPONIBLE';
COMMENT ON COLUMN pev.cocdi IS 'Code cdi topad - INDISPONIBLE';
COMMENT ON COLUMN pev.cosatp IS 'Code service topad - INDISPONIBLE';
COMMENT ON COLUMN pev.gsatp IS 'Nature service gérant tp - INDISPONIBLE';
COMMENT ON COLUMN pev.clocv IS 'Indicateur local vacant - INDISPONIBLE';
COMMENT ON COLUMN pev.dvltpe IS 'VL TOTALE DE LA PEV MAJIC2 - ';
COMMENT ON COLUMN pev.dcralc IS 'correctif d’ascenseur - format S9V99 - INDISPONIBLE';
COMMENT ON COLUMN pev.dcsplca IS 'Coefficient de situation particulière';
COMMENT ON COLUMN pev.dcsglca IS 'Coefficient de situation générale';
COMMENT ON COLUMN pev.dcralca IS 'Correctif d’ascenseur';
COMMENT ON COLUMN pev.topcn IS 'Top construction nouvelle (à partir de 2013)';
COMMENT ON COLUMN pev.tpevtieom IS 'Top Local passible de la TEOM (à partir de 2013)';
COMMENT ON COLUMN pev.ccocac IS 'Code catégorie du local';
COMMENT ON COLUMN pev.dnutrf IS 'Secteur révisé';
COMMENT ON COLUMN pev.dcfloc IS 'Coefficient de localisation';
COMMENT ON COLUMN pev.ccortar IS 'Code commune origine du tarif';
COMMENT ON COLUMN pev.ccorvl IS 'Code réduction du local';
COMMENT ON COLUMN pev.dtaurv IS 'Taux de réduction';
COMMENT ON COLUMN pev.dcmloc IS 'Coefficient de modulation du local';
COMMENT ON COLUMN pev.jancmp IS 'Année de début de compensation';


COMMENT ON TABLE pevexoneration IS 'Article exonération de pev imposable';
COMMENT ON COLUMN pevexoneration.ccodep IS 'Code département - ';
COMMENT ON COLUMN pevexoneration.ccodir IS 'Code direction - ';
COMMENT ON COLUMN pevexoneration.ccocom IS 'Code commune INSEE - ';
COMMENT ON COLUMN pevexoneration.invar IS 'Numéro invariant - ';
COMMENT ON COLUMN pevexoneration.Janbil IS 'Année d’immobilisation - servie pour ets. industriels';
COMMENT ON COLUMN pevexoneration.dnupev IS 'Numéro de pev - ';
COMMENT ON COLUMN pevexoneration.dnuexb IS 'Numéro d’ordre de l’article - 001 à 015';
COMMENT ON COLUMN pevexoneration.ccolloc IS 'Code de collectivité locale accordant l’exonération - C D R TC tableau 2.3.9';
COMMENT ON COLUMN pevexoneration.pexb IS 'Taux d’exonération accordée - 999V99';
COMMENT ON COLUMN pevexoneration.gnextl IS 'Nature d’exonération temporaire (et permanente pour ets. Industriels) - tableau des codes 2.3.10 et 2.3.8';
COMMENT ON COLUMN pevexoneration.jandeb IS 'année de début d’exonération - ';
COMMENT ON COLUMN pevexoneration.janimp IS 'année de retour à imposition - ';
COMMENT ON COLUMN pevexoneration.vecdif IS 'montant saisi de l’EC bénéficiant exo - INDISPONIBLE';
COMMENT ON COLUMN pevexoneration.vecdifa IS 'vecdif multiplié par coeff - INDISPONIBLE';
COMMENT ON COLUMN pevexoneration.fcexb IS 'Fraction EC exonérée - INDISPONIBLE';
COMMENT ON COLUMN pevexoneration.fcexba IS 'fcexb multiplié par coeff - INDISPONIBLE';
COMMENT ON COLUMN pevexoneration.rcexba IS 'revenu cadastral exonéré - INDISPONIBLE';
COMMENT ON COLUMN pevexoneration.dvldif2 IS 'Montant de VL exonérée (valeur 70) - ';
COMMENT ON COLUMN pevexoneration.dvldif2a IS 'Montant de VL exonérée (valeur de l’année) - ';
COMMENT ON COLUMN pevexoneration.fcexb2 IS 'Fraction de VL exonérée (valeur 70) - ';
COMMENT ON COLUMN pevexoneration.fcexba2 IS 'Fraction de VL exonérée (valeur de l’année) - ';
COMMENT ON COLUMN pevexoneration.rcexba2 IS 'Revenu cadastral exonéré (valeur de l’année) - ';
COMMENT ON COLUMN pevexoneration.valplaf IS 'Montant du planchonnement sur la base exonérée neutralisée';

COMMENT ON TABLE pevexoneration_imposable IS 'Article exonération de pev imposable';
COMMENT ON COLUMN pevexoneration_imposable.ccodep IS 'Code département - ';
COMMENT ON COLUMN pevexoneration_imposable.ccodir IS 'Code direction - ';
COMMENT ON COLUMN pevexoneration_imposable.ccocom IS 'Code commune INSEE - ';
COMMENT ON COLUMN pevexoneration_imposable.invar IS 'Numéro invariant - ';
COMMENT ON COLUMN pevexoneration_imposable.Janbil IS 'Année d’immobilisation - servie pour ets. industriels';
COMMENT ON COLUMN pevexoneration_imposable.dnupev IS 'Numéro de pev - ';
COMMENT ON COLUMN pevexoneration_imposable.dnuexb IS 'Numéro d’ordre de l’article - 001 à 015';
COMMENT ON COLUMN pevexoneration_imposable.ccolloc IS 'Code de collectivité locale accordant l’exonération - C D R TC tableau 2.3.9';
COMMENT ON COLUMN pevexoneration_imposable.pexb IS 'Taux d’exonération accordée - 999V99';
COMMENT ON COLUMN pevexoneration_imposable.gnextl IS 'Nature d’exonération temporaire (et permanente pour ets. Industriels) - tableau des codes 2.3.10 et 2.3.8';
COMMENT ON COLUMN pevexoneration_imposable.jandeb IS 'année de début d’exonération - ';
COMMENT ON COLUMN pevexoneration_imposable.janimp IS 'année de retour à imposition - ';
COMMENT ON COLUMN pevexoneration_imposable.vecdif IS 'montant saisi de l’EC bénéficiant exo - INDISPONIBLE';
COMMENT ON COLUMN pevexoneration_imposable.vecdifa IS 'vecdif multiplié par coeff - INDISPONIBLE';
COMMENT ON COLUMN pevexoneration_imposable.fcexb IS 'Fraction EC exonérée - INDISPONIBLE';
COMMENT ON COLUMN pevexoneration_imposable.fcexba IS 'fcexb multiplié par coeff - INDISPONIBLE';
COMMENT ON COLUMN pevexoneration_imposable.rcexba IS 'revenu cadastral exonéré - INDISPONIBLE';
COMMENT ON COLUMN pevexoneration_imposable.dvldif2 IS 'Montant de VL exonérée (valeur 70) - ';
COMMENT ON COLUMN pevexoneration_imposable.dvldif2a IS 'Montant de VL exonérée (valeur de l’année) - ';
COMMENT ON COLUMN pevexoneration_imposable.fcexb2 IS 'Fraction de VL exonérée (valeur 70) - ';
COMMENT ON COLUMN pevexoneration_imposable.fcexba2 IS 'Fraction de VL exonérée (valeur de l’année) - ';
COMMENT ON COLUMN pevexoneration_imposable.rcexba2 IS 'Revenu cadastral exonéré (valeur de l’année) - ';
COMMENT ON COLUMN pevexoneration_imposable.valplaf IS 'Montant du planchonnement sur la base exonérée neutralisée';

COMMENT ON TABLE pevexoneration_imposee IS 'Article exonération de pev imposée';
COMMENT ON COLUMN pevexoneration_imposee.ccodep IS 'Code département - ';
COMMENT ON COLUMN pevexoneration_imposee.ccodir IS 'Code direction - ';
COMMENT ON COLUMN pevexoneration_imposee.ccocom IS 'Code commune INSEE - ';
COMMENT ON COLUMN pevexoneration_imposee.invar IS 'Numéro invariant - ';
COMMENT ON COLUMN pevexoneration_imposee.Janbil IS 'Année d’immobilisation - servie pour ets. industriels';
COMMENT ON COLUMN pevexoneration_imposee.dnupev IS 'Numéro de pev - ';
COMMENT ON COLUMN pevexoneration_imposee.dnuexb IS 'Numéro d’ordre de l’article - 001 à 015';
COMMENT ON COLUMN pevexoneration_imposee.ccolloc IS 'Code de collectivité locale accordant l’exonération - C D R TC tableau 2.3.9';
COMMENT ON COLUMN pevexoneration_imposee.pexb IS 'Taux d’exonération accordée - 999V99';
COMMENT ON COLUMN pevexoneration_imposee.gnextl IS 'Nature d’exonération temporaire (et permanente pour ets. Industriels) - tableau des codes 2.3.10 et 2.3.8';
COMMENT ON COLUMN pevexoneration_imposee.jandeb IS 'année de début d’exonération - ';
COMMENT ON COLUMN pevexoneration_imposee.janimp IS 'année de retour à imposition - ';
COMMENT ON COLUMN pevexoneration_imposee.vecdif IS 'montant saisi de l’EC bénéficiant exo - INDISPONIBLE';
COMMENT ON COLUMN pevexoneration_imposee.vecdifa IS 'vecdif multiplié par coeff - INDISPONIBLE';
COMMENT ON COLUMN pevexoneration_imposee.fcexb IS 'Fraction EC exonérée - INDISPONIBLE';
COMMENT ON COLUMN pevexoneration_imposee.fcexba IS 'fcexb multiplié par coeff - INDISPONIBLE';
COMMENT ON COLUMN pevexoneration_imposee.rcexba IS 'revenu cadastral exonéré - INDISPONIBLE';
COMMENT ON COLUMN pevexoneration_imposee.dvldif2 IS 'Montant de VL exonérée (valeur 70) - ';
COMMENT ON COLUMN pevexoneration_imposee.dvldif2a IS 'Montant de VL exonérée (valeur de l’année) - ';
COMMENT ON COLUMN pevexoneration_imposee.fcexb2 IS 'Fraction de VL exonérée (valeur 70) - ';
COMMENT ON COLUMN pevexoneration_imposee.fcexba2 IS 'Fraction de VL exonérée (valeur de l’année) - ';
COMMENT ON COLUMN pevexoneration_imposee.rcexba2 IS 'Revenu cadastral exonéré (valeur de l’année) - ';
COMMENT ON COLUMN pevexoneration_imposee.valplaf IS 'Montant du planchonnement sur la base exonérée neutralisée';

COMMENT ON TABLE pevtaxation IS 'Article taxation de pev';
COMMENT ON COLUMN pevtaxation.ccodep IS 'Code département - ';
COMMENT ON COLUMN pevtaxation.ccodir IS 'Code direction - ';
COMMENT ON COLUMN pevtaxation.ccocom IS 'Code commune INSEE - ';
COMMENT ON COLUMN pevtaxation.invar IS 'Numéro invariant - ';
COMMENT ON COLUMN pevtaxation.janbil IS 'Année d’immobilisation - High value pour ets. Industriels';
COMMENT ON COLUMN pevtaxation.dnupev IS 'Numéro de pev - ';
COMMENT ON COLUMN pevtaxation.co_vlbai IS 'Commune - Part de VL imposée (valeur70) - ';
COMMENT ON COLUMN pevtaxation.co_vlbaia IS 'Commune - Part de VL imposée (valeur de l’année) - ';
COMMENT ON COLUMN pevtaxation.co_bipevla IS 'Commune - Base d’imposition de la pev(valeur de l’année) - ';
COMMENT ON COLUMN pevtaxation.de_vlbai IS 'Département - Part de VL imposée (valeur70) - ';
COMMENT ON COLUMN pevtaxation.de_vlbaia IS 'Département - Part de VL imposée (valeur de l’année) - ';
COMMENT ON COLUMN pevtaxation.de_bipevla IS 'Département - Base d’imposition de la pev(valeur de l’année) - ';
COMMENT ON COLUMN pevtaxation.re_vlbai IS 'Région (avant 2012) - Part de VL imposée (valeur70) - ';
COMMENT ON COLUMN pevtaxation.re_vlbaia IS 'Région (avant 2012) - Part de VL imposée (valeur de l’année) - ';
COMMENT ON COLUMN pevtaxation.re_bipevla IS 'Région (avant 2012) - Base d’imposition de la pev(valeur de l’année) - ';
COMMENT ON COLUMN pevtaxation.gp_vlbai IS 'Groupement de commune - Part de VL imposée (valeur70) - ';
COMMENT ON COLUMN pevtaxation.gp_vlbaia IS 'Groupement de commune - Part de VL imposée (valeur de l’année) - ';
COMMENT ON COLUMN pevtaxation.gp_bipevla IS 'Groupement de commune - Base d’imposition de la pev(valeur de l’année) - ';
COMMENT ON COLUMN pevtaxation.bateom IS 'BASE ORDURES MENAGERES - ';
COMMENT ON COLUMN pevtaxation.baomec IS 'BASE ORDURES MENAGERES ECRETEE - ';
COMMENT ON COLUMN pevtaxation.tse_vlbai IS 'TSE (à partir de 2012) - Part de VL imposée (valeur70) - ';
COMMENT ON COLUMN pevtaxation.tse_vlbaia IS 'TSE (à partir de 2012) - Part de VL imposée (valeur de l’année) - ';
COMMENT ON COLUMN pevtaxation.tse_bipevla IS 'TSE (à partir de 2012) - Base d’imposition de la pev(valeur de l’année) - ';
COMMENT ON COLUMN pevtaxation.mvltieomx IS 'Montant TIEOM (depuis 2013)';
COMMENT ON COLUMN pevtaxation.pvltieom IS 'Ratio VL n-1 de la PEV / VL n-1 collectivité - 9v999999999999999 (Depuis 2013 mais supprimée en 2014)';

COMMENT ON TABLE pevprincipale IS 'Article descriptif partie principale habitation';
COMMENT ON COLUMN pevprincipale.ccodep IS 'Code département - ';
COMMENT ON COLUMN pevprincipale.ccodir IS 'Code direction - ';
COMMENT ON COLUMN pevprincipale.ccocom IS 'Code commune INSEE - ';
COMMENT ON COLUMN pevprincipale.invar IS 'Numéro invariant - ';
COMMENT ON COLUMN pevprincipale.dnupev IS 'Numéro de pev - ';
COMMENT ON COLUMN pevprincipale.dnudes IS 'Numéro d’ordre de descriptif - bHb, bHA...';
COMMENT ON COLUMN pevprincipale.dep1_cconad IS 'Dépendance 1 - Nature de dépendance - Tableau 2.3.5';
COMMENT ON COLUMN pevprincipale.dep1_dsueic IS 'Dépendance 1 - Surface réelle de l’élément incorporé - ';
COMMENT ON COLUMN pevprincipale.dep1_dcimei IS 'Dépendance 1 - Coefficient de pondération - 9V9';
COMMENT ON COLUMN pevprincipale.dep2_cconad IS 'Dépendance 2 - Nature de dépendance - Tableau 2.3.5';
COMMENT ON COLUMN pevprincipale.dep2_dsueic IS 'Dépendance 2 - Surface réelle de l’élément incorporé - ';
COMMENT ON COLUMN pevprincipale.dep2_dcimei IS 'Dépendance 2 - Coefficient de pondération - 9V9';
COMMENT ON COLUMN pevprincipale.dep3_cconad IS 'Dépendance 3 - Nature de dépendance - Tableau 2.3.5';
COMMENT ON COLUMN pevprincipale.dep3_dsueic IS 'Dépendance 3 - Surface réelle de l’élément incorporé - ';
COMMENT ON COLUMN pevprincipale.dep3_dcimei IS 'Dépendance 3 - Coefficient de pondération - 9V9';
COMMENT ON COLUMN pevprincipale.dep4_cconad IS 'Dépendance 4 - Nature de dépendance - Tableau 2.3.5';
COMMENT ON COLUMN pevprincipale.dep4_dsueic IS 'Dépendance 4 - Surface réelle de l’élément incorporé - ';
COMMENT ON COLUMN pevprincipale.dep4_dcimei IS 'Dépendance 4 - Coefficient de pondération - 9V9';
COMMENT ON COLUMN pevprincipale.geaulc IS 'Présence d’eau - O = oui, N = non';
COMMENT ON COLUMN pevprincipale.gelelc IS 'Présence d’électricité - O = oui, N = non';
COMMENT ON COLUMN pevprincipale.gesclc IS 'Présence d’escalier de service (appartement) - O = oui, N = non, blanc';
COMMENT ON COLUMN pevprincipale.ggazlc IS 'Présence du gaz - O = oui, N = non';
COMMENT ON COLUMN pevprincipale.gasclc IS 'Présence d’ascenseur (appartement) - O = oui, N = non, blanc';
COMMENT ON COLUMN pevprincipale.gchclc IS 'Présence du chauffage central - O = oui, N = non';
COMMENT ON COLUMN pevprincipale.gvorlc IS 'Présence de vide-ordures (appartement)  - O = oui, N = non, blanc';
COMMENT ON COLUMN pevprincipale.gteglc IS 'Présence du tout à l’égout - O = oui, N = non';
COMMENT ON COLUMN pevprincipale.dnbbai IS 'Nombre de baignoires - ';
COMMENT ON COLUMN pevprincipale.dnbdou IS 'Nombre de douches - ';
COMMENT ON COLUMN pevprincipale.dnblav IS 'Nombre de lavabos - ';
COMMENT ON COLUMN pevprincipale.dnbwc IS 'Nombre de WC - ';
COMMENT ON COLUMN pevprincipale.deqdha IS 'Equivalence superficielle des éléments de confort Répartition des pièces - ';
COMMENT ON COLUMN pevprincipale.dnbppr IS 'Nombre de pièces principales - ';
COMMENT ON COLUMN pevprincipale.dnbsam IS 'Nombre de salles à manger - ';
COMMENT ON COLUMN pevprincipale.dnbcha IS 'Nombre de chambres - ';
COMMENT ON COLUMN pevprincipale.dnbcu8 IS 'Nombre de cuisines de moins de 9 m2 - ';
COMMENT ON COLUMN pevprincipale.dnbcu9 IS 'Nombre de cuisines d’au moins 9 m2 - ';
COMMENT ON COLUMN pevprincipale.dnbsea IS 'Nombre de salles d’eau - ';
COMMENT ON COLUMN pevprincipale.dnbann IS 'Nombre de pièces annexes - ';
COMMENT ON COLUMN pevprincipale.dnbpdc IS 'Nombre de pièces - ';
COMMENT ON COLUMN pevprincipale.dsupdc IS 'Superficie des pièces - ';
COMMENT ON COLUMN pevprincipale.dmatgm IS 'Matériaux des gros murs - 0 indéterminé 1 pierre 2 meulière 3 béton 4 briques 5 aggloméré 6 bois 9 autres ';
COMMENT ON COLUMN pevprincipale.dmatto IS 'Matériaux des toitures - 0 indéterminé 1 tuiles 2 ardoises 3 zinc aluminium 4 béton';
COMMENT ON COLUMN pevprincipale.jannat IS 'Année d’achèvement - ';
COMMENT ON COLUMN pevprincipale.detent IS 'état d’entretien - 1 bon 2 assez bon 3 passable 4 médiocre 5 mauvais';
COMMENT ON COLUMN pevprincipale.dnbniv IS 'Nombre de niveaux - ';
COMMENT ON TABLE pevprofessionnelle IS 'Article descriptif professionnel';
COMMENT ON COLUMN pevprofessionnelle.ccodep IS 'Code département - ';
COMMENT ON COLUMN pevprofessionnelle.ccodir IS 'Code direction - ';
COMMENT ON COLUMN pevprofessionnelle.ccocom IS 'Code commune INSEE - ';
COMMENT ON COLUMN pevprofessionnelle.invar IS 'Numéro invariant - ';
COMMENT ON COLUMN pevprofessionnelle.dnupev IS 'Numéro de pev - ';
COMMENT ON COLUMN pevprofessionnelle.dnudes IS 'Numéro d’ordre de descriptif - P01';
COMMENT ON COLUMN pevprofessionnelle.vsupot IS 'surface pondérée - INDISPONIBLE';
COMMENT ON COLUMN pevprofessionnelle.vsurz1 IS 'Surface réelle totale zone 1 - INDISPONIBLE';
COMMENT ON COLUMN pevprofessionnelle.vsurz2 IS 'Surface réelle totale zone 2 - INDISPONIBLE';
COMMENT ON COLUMN pevprofessionnelle.vsurz3 IS 'Surface réelle totale zone 3 - INDISPONIBLE';
COMMENT ON COLUMN pevprofessionnelle.vsurzt IS 'Surface réelle totale - ';
COMMENT ON COLUMN pevprofessionnelle.vsurb1 IS 'surface réelle des bureaux 1 - INDISPONIBLE';
COMMENT ON COLUMN pevprofessionnelle.vsurb2 IS 'surface réelle des bureaux 2 - INDISPONIBLE';

COMMENT ON COLUMN pevprofessionnelle.dsupot IS 'Surface pondérée';
COMMENT ON COLUMN pevprofessionnelle.dsup1 IS 'Surface des parties principales';
COMMENT ON COLUMN pevprofessionnelle.dsup2 IS 'Surface des parties secondaires couvertes';
COMMENT ON COLUMN pevprofessionnelle.dsup3 IS 'Surface des parties secondaires non couvertes';
COMMENT ON COLUMN pevprofessionnelle.dsupk1 IS 'Surface des stationnements couverts';
COMMENT ON COLUMN pevprofessionnelle.dsupk2 IS 'Surface des stationnements non couverts';

COMMENT ON TABLE pevlissage IS 'Descriptif des quotes-parts de lissage (locaux révisés). Bati enregistrement 52';
COMMENT ON COLUMN pevlissage.ccodep IS 'Code du département';
COMMENT ON COLUMN pevlissage.ccodir IS 'Code de direction';
COMMENT ON COLUMN pevlissage.ccocom IS 'Code commune INSEE';
COMMENT ON COLUMN pevlissage.invar  IS 'Numéro invariant';
COMMENT ON COLUMN pevlissage.dnupev IS 'Numéro de PEV';
COMMENT ON COLUMN pevlissage.pev    IS 'Code unique de PEV';
COMMENT ON COLUMN pevlissage.mlbcom IS 'Quote-part de lissage de la commune';
COMMENT ON COLUMN pevlissage.mlbsyn IS 'Quote-part de lissage du syndicat intercommunal';
COMMENT ON COLUMN pevlissage.mlbcu  IS 'Quote-part de lissage de l’intercommunalité';
COMMENT ON COLUMN pevlissage.mlbdep IS 'Quote-part de lissage du département';
COMMENT ON COLUMN pevlissage.mlbts1 IS 'Quote-part de lissage de la TSE';
COMMENT ON COLUMN pevlissage.mlbts2 IS 'Quote-part de lissage de la TSE autre';
COMMENT ON COLUMN pevlissage.mlbtas IS 'Quote-part de lissage de la TASA';
COMMENT ON COLUMN pevlissage.mlbgem IS 'Quote-part de lissage GEMAPI';
COMMENT ON COLUMN pevlissage.mlbtom IS 'Quote-part de lissage TEOM';
COMMENT ON COLUMN pevlissage.tbfpas IS 'Pas de lissage du local';
COMMENT ON COLUMN pevlissage.mlbtfc IS 'Quote-parte de lissage sur les friches commerciales (TFC)';
COMMENT ON COLUMN pevlissage.lot IS 'Code de lot d''import';


COMMENT ON TABLE pevdependances IS 'Article descriptif de dépendance. Bati enregistrement 60';
COMMENT ON COLUMN pevdependances.ccodep IS 'Code département - ';
COMMENT ON COLUMN pevdependances.ccodir IS 'Code direction - ';
COMMENT ON COLUMN pevdependances.ccocom IS 'Code commune INSEE - ';
COMMENT ON COLUMN pevdependances.invar IS 'Numéro invariant - ';
COMMENT ON COLUMN pevdependances.dnupev IS 'Numéro de pev - ';
COMMENT ON COLUMN pevdependances.dnudes IS 'Numéro d’ordre de descriptif - 001, 002';
COMMENT ON COLUMN pevdependances.dsudep IS 'Surface réelle de la dépendance - ';
COMMENT ON COLUMN pevdependances.cconad IS 'Nature de dépendance - cf tableau des codes';
COMMENT ON COLUMN pevdependances.asitet IS 'Localisation (bat, esc, niv) - ';
COMMENT ON COLUMN pevdependances.dmatgm IS 'Matériaux des gros murs - 0 à 9 cf art 40';
COMMENT ON COLUMN pevdependances.dmatto IS 'Matériaux des toitures - 0 à 4 cf art 40';
COMMENT ON COLUMN pevdependances.detent IS 'état d''entretien - 1 à 5 cf art 40';
COMMENT ON COLUMN pevdependances.geaulc IS 'Présence d''eau - O = oui, N = non';
COMMENT ON COLUMN pevdependances.gelelc IS 'Présence d’électricité - O = oui, N = non';
COMMENT ON COLUMN pevdependances.gchclc IS 'Présence du chauffage central - O = oui, N = non';
COMMENT ON COLUMN pevdependances.dnbbai IS 'Nombre de baignoires - ';
COMMENT ON COLUMN pevdependances.dnbdou IS 'Nombre de douches - ';
COMMENT ON COLUMN pevdependances.dnblav IS 'Nombre de lavabos - ';
COMMENT ON COLUMN pevdependances.dnbwc IS 'Nombre de WC - ';
COMMENT ON COLUMN pevdependances.deqtlc IS 'Equivalence superficielle des - ';
COMMENT ON COLUMN pevdependances.dcimlc IS 'Coefficient de pondération - 1,0 - 0,2 à 0,6';
COMMENT ON COLUMN pevdependances.dcetde IS 'Coefficient d entretien - 9V99';
COMMENT ON COLUMN pevdependances.dcspde IS 'Coefficient de situation particulière - S9V99 de -0,10 à +0,10  -- INDISPONIBLE';
COMMENT ON COLUMN pevdependances.dcspdea IS 'Coefficient de situation particulière';
COMMENT ON TABLE proprietaire IS 'Propriétaire';
COMMENT ON COLUMN proprietaire.ccodep IS 'code département - ';
COMMENT ON COLUMN proprietaire.ccodir IS 'code direction - ';
COMMENT ON COLUMN proprietaire.ccocom IS 'code commune INSEE - ';
COMMENT ON COLUMN proprietaire.dnupro IS 'compte communal - cgroup groupe de compte communal + * A B .. - ';
COMMENT ON COLUMN proprietaire.dnulp IS 'numéro de libellé partiel - 01 à 06';
COMMENT ON COLUMN proprietaire.ccocif IS 'code cdif - ';
COMMENT ON COLUMN proprietaire.dnuper IS 'numéro de personne dans le cdif - Il s’agit du numéro de personne ';
COMMENT ON COLUMN proprietaire.ccodro IS 'code du droit réel ou particulier - Nouveau code en 2009 : C (fiduciaire)';
COMMENT ON COLUMN proprietaire.ccodem IS 'code du démembrement/indivision - C S L I V';
COMMENT ON COLUMN proprietaire.gdesip IS 'indicateur du destinataire de l’avis d’imposition - 1 = oui, 0 = non';
COMMENT ON COLUMN proprietaire.gtoper IS 'indicateur de personne physique ou morale - 1 = physique, 2 = morale';
COMMENT ON COLUMN proprietaire.ccoqua IS 'Code qualité de personne physique - 1, 2 ou 3';
COMMENT ON COLUMN proprietaire.gnexcf IS 'code exo ecf - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.dtaucf IS 'taux exo ecf - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.dnatpr IS 'Code nature de personne physique ou morale - Voir $$ 2.2.7';
COMMENT ON COLUMN proprietaire.ccogrm IS 'Code groupe de personne morale - 0 à 9 - 0A à 9A';
COMMENT ON COLUMN proprietaire.dsglpm IS 'sigle de personne morale - ';
COMMENT ON COLUMN proprietaire.dforme IS 'forme juridique abrégée majic2 X Données Générales - ';
COMMENT ON COLUMN proprietaire.ddenom IS 'Dénomination de personne physique ou morale - ';
COMMENT ON COLUMN proprietaire.gtyp3 IS 'type de la 3eme ligne d’adresse - ';
COMMENT ON COLUMN proprietaire.gtyp4 IS 'Type de la 4eme ligne d’adresse - ';
COMMENT ON COLUMN proprietaire.gtyp5 IS 'type de la 5eme ligne d’adresse - ';
COMMENT ON COLUMN proprietaire.gtyp6 IS 'type de la 6eme ligne d’adresse - ';
COMMENT ON COLUMN proprietaire.dlign3 IS '3eme ligne d’adresse - ';
COMMENT ON COLUMN proprietaire.dlign4 IS '4eme ligne d’adresse - ';
COMMENT ON COLUMN proprietaire.dlign5 IS '5eme ligne d’adresse - ';
COMMENT ON COLUMN proprietaire.dlign6 IS '6eme ligne d’adresse X Codification de l’adresse - ';
COMMENT ON COLUMN proprietaire.ccopay IS 'code de pays étranger et TOM - non servi pour France métropole et Dom';
COMMENT ON COLUMN proprietaire.ccodep1a2 IS 'Code département de l’adresse - ';
COMMENT ON COLUMN proprietaire.ccodira IS 'Code direction de l’adresse - ';
COMMENT ON COLUMN proprietaire.ccocom_adr IS 'Code commune de l’adresse - ';
COMMENT ON COLUMN proprietaire.ccovoi IS 'Code majic2 de la voie - ';
COMMENT ON COLUMN proprietaire.ccoriv IS 'Code rivoli de la voie - ';
COMMENT ON COLUMN proprietaire.dnvoiri IS 'numéro de voirie - ';
COMMENT ON COLUMN proprietaire.dindic IS 'indice de répétition de voirie - ';
COMMENT ON COLUMN proprietaire.ccopos IS 'Code postal X Dénomination formatée de personne physique - ';
COMMENT ON COLUMN proprietaire.dnirpp IS 'zone à blanc - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.dqualp IS 'Qualité abrégée - M, MME ou MLE';
COMMENT ON COLUMN proprietaire.dnomlp IS 'Nom d’usage - ';
COMMENT ON COLUMN proprietaire.dprnlp IS 'Prénoms associés au nom d’usage - ';
COMMENT ON COLUMN proprietaire.jdatnss IS 'date de naissance - sous la forme jj/mm/aaaa';
COMMENT ON COLUMN proprietaire.dldnss IS 'lieu de naissance - ';
COMMENT ON COLUMN proprietaire.epxnee IS 'mention du complément - EPX ou NEE si complément';
COMMENT ON COLUMN proprietaire.dnomcp IS 'Nom complément - ';
COMMENT ON COLUMN proprietaire.dprncp IS 'Prénoms associés au complément - ';
COMMENT ON COLUMN proprietaire.topcdi IS 'top transalp - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.oriard IS 'origine adresse - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.fixard IS 'pérennité adresse - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.datadr IS 'date adresse - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.topdec IS 'origine décès - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.datdec IS 'date de décès - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.dsiren IS 'numéro siren - ';
COMMENT ON COLUMN proprietaire.ccmm IS 'création compte cadastral - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.topja IS 'indic jeune agriculteur - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.datja IS 'date jeune agriculteur - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.anospi IS 'ano transalp - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.cblpmo IS 'code blocage caractère personne morale - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.gtodge IS 'top appartenance à la DGE - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.gpctf IS 'top paiement centralisé à la taxe foncière - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.gpctsb IS 'top paiement centralisé à la TSBCS - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.jmodge IS 'mois d’entrée à la DGE - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.jandge IS 'année d’entrée à la DGE - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.jantfc IS 'année d’entrée paiement TF - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.jantbc IS 'année d’entrée paiement TSBCS - INDISPONIBLE';
COMMENT ON COLUMN proprietaire.dformjur IS 'Forme juridique (Depuis 2013)';
COMMENT ON COLUMN proprietaire.dnomus IS 'Nom d''usage (Depuis 2015)';
COMMENT ON COLUMN proprietaire.dprnus IS 'Prénom d''usage (Depuis 2015)';
COMMENT ON TABLE pdl IS 'Propriétés divisées en lots';
COMMENT ON COLUMN pdl.ccodep IS 'code département - ';
COMMENT ON COLUMN pdl.ccodir IS 'code direction - ';
COMMENT ON COLUMN pdl.ccocom IS 'code commune INSEE - ';
COMMENT ON COLUMN pdl.ccopre IS 'code du préfixe - ';
COMMENT ON COLUMN pdl.ccosec IS 'lettres de section - ';
COMMENT ON COLUMN pdl.dnupla IS 'numéro de plan - ';
COMMENT ON COLUMN pdl.dnupdl IS 'no de pdl - ';
COMMENT ON COLUMN pdl.dnivim IS 'niveau imbrication - ';
COMMENT ON COLUMN pdl.ctpdl IS 'type de pdl - bnd, cl, cv, tf, clv, mp.';
COMMENT ON COLUMN pdl.dmrpdl IS 'lot mère(plan+pdl+lot) - ';
COMMENT ON COLUMN pdl.gprmut IS 'top ''1ere mut effectuée - ';
COMMENT ON COLUMN pdl.dnupro IS 'compte de la pdl - ';
COMMENT ON COLUMN pdl.ccocif IS 'code cdif - ';
COMMENT ON TABLE lots IS 'Article descriptif du lot';
COMMENT ON COLUMN lots.ccodep IS 'code département - ';
COMMENT ON COLUMN lots.ccodir IS 'code direction - ';
COMMENT ON COLUMN lots.ccocom IS 'code commune INSEE - ';
COMMENT ON COLUMN lots.ccopre IS 'code du préfixe - ';
COMMENT ON COLUMN lots.ccosec IS 'lettres de section - ';
COMMENT ON COLUMN lots.dnupla IS 'numéro de plan - ';
COMMENT ON COLUMN lots.dnupdl IS 'no de pdl - ';
COMMENT ON COLUMN lots.dnulot IS 'Numéro de lot - ';
COMMENT ON COLUMN lots.cconlo IS 'Code nature du lot - ';
COMMENT ON COLUMN lots.dcntlo IS 'Superficie du lot - ';
COMMENT ON COLUMN lots.dnumql IS 'Numérateur - ';
COMMENT ON COLUMN lots.ddenql IS 'Dénominateur - ';
COMMENT ON COLUMN lots.dfilot IS 'pdl-fille du lot - ';
COMMENT ON COLUMN lots.datact IS 'date de l''acte - ';
COMMENT ON COLUMN lots.dnuprol IS 'Compte du lot - ';
COMMENT ON COLUMN lots.dreflf IS 'Référence livre foncier - ';
COMMENT ON COLUMN lots.ccocif IS 'code cdif - ';
COMMENT ON TABLE parcellecomposante IS 'Parcelle composante de la pdl autre que la parcelle de référence';
COMMENT ON COLUMN parcellecomposante.ccodep IS 'code département - ';
COMMENT ON COLUMN parcellecomposante.ccodir IS 'code direction - ';
COMMENT ON COLUMN parcellecomposante.ccocom IS 'code commune INSEE - ';
COMMENT ON COLUMN parcellecomposante.ccopre IS 'code du préfixe - ';
COMMENT ON COLUMN parcellecomposante.ccosec IS 'lettres de section - ';
COMMENT ON COLUMN parcellecomposante.dnupla IS 'numéro de plan - ';
COMMENT ON COLUMN parcellecomposante.dnupdl IS 'no de pdl - ';
COMMENT ON COLUMN parcellecomposante.ccoprea IS 'code du préfixe - ';
COMMENT ON COLUMN parcellecomposante.ccoseca IS 'lettres de section - ';
COMMENT ON COLUMN parcellecomposante.dnuplaa IS 'numéro de plan - ';
COMMENT ON COLUMN parcellecomposante.ccocif IS 'code cdif - ';
COMMENT ON TABLE lotslocaux IS 'Article descriptif du lot';
COMMENT ON COLUMN lotslocaux.ccodepl IS 'Lot - Code département - ';
COMMENT ON COLUMN lotslocaux.ccodirl IS 'Lot - Code direction - ';
COMMENT ON COLUMN lotslocaux.ccocoml IS 'Lot - Code INSEE de la commune - ';
COMMENT ON COLUMN lotslocaux.ccoprel IS 'Lot - Code préfixe - ';
COMMENT ON COLUMN lotslocaux.ccosecl IS 'Lot - Code section - ';
COMMENT ON COLUMN lotslocaux.dnuplal IS 'Lot - Numéro du plan - ';
COMMENT ON COLUMN lotslocaux.dnupdl IS 'Lot - Numéro de PDL - ';
COMMENT ON COLUMN lotslocaux.dnulot IS 'Lot - Numéro de lot - ';
COMMENT ON COLUMN lotslocaux.ccodebpb IS 'Local - Code département - ';
COMMENT ON COLUMN lotslocaux.ccodird IS 'Local - Code direction - ';
COMMENT ON COLUMN lotslocaux.ccocomb IS 'Local - Code commune - ';
COMMENT ON COLUMN lotslocaux.ccopreb IS 'Local - Code préfixe - ';
COMMENT ON COLUMN lotslocaux.invloc IS 'Local - Numéro invariant du local - ';
COMMENT ON COLUMN lotslocaux.dnumql IS 'Local - Numérateur du lot - ';
COMMENT ON COLUMN lotslocaux.ddenql IS 'Local - Dénominateur du lot - ';
COMMENT ON TABLE commune IS 'Commune (Fantoir)';
COMMENT ON COLUMN commune.ccodep IS 'Code département - Code département INSEE';
COMMENT ON COLUMN commune.ccodir IS 'Code direction - Code direction dge';
COMMENT ON COLUMN commune.ccocom IS 'Code commune - code commune définie par Majic2';
COMMENT ON COLUMN commune.clerivili IS 'Clé RIVOLI - zone alphabétique fournie par MAJIC2';
COMMENT ON COLUMN commune.libcom IS 'Libellé - désignation de la commune';
COMMENT ON COLUMN commune.typcom IS 'Type de commune actuel (R ou N) - N - commune rurale, R - commune rencencée';
COMMENT ON COLUMN commune.ruract IS 'RUR actuel - indique si la commune est pseudo-recensée ou non (3-commune pseudo-recensée, blanc si rien)';
COMMENT ON COLUMN commune.carvoi IS 'caractère de voie - zone indiquant si la voie est privée (1) ou publique (0)';
COMMENT ON COLUMN commune.indpop IS 'indicateur de population - Précise la dernière situation connue de la commune au regard de la limite de 3000 habitants (= blanc si < 3000 h sinon = *).';
COMMENT ON COLUMN commune.poprel IS 'population réelle - dénombre la population recencée lors du dernier recensement';
COMMENT ON COLUMN commune.poppart IS 'population à part - dénombre la population comptée à part dans la commune';
COMMENT ON COLUMN commune.popfict IS 'population fictive - population fictive de la commune';
COMMENT ON COLUMN commune.annul IS 'Annulation Cet article indique que plus aucune entité topo n’est représentée par ce code. - O - voie annulée sans transfert, Q - voie annulée avec transfert, Q - commune annulée avec transfert.';
COMMENT ON COLUMN commune.dteannul IS 'date d''annulation - ';
COMMENT ON COLUMN commune.dtecreart IS 'Date de création de l''article - Date à laquelle l''article a été créé par création MAJIC2.';
COMMENT ON COLUMN commune.codvoi IS 'Code identifiant la voie dans MAJIC2. - Permet de faire le lien entre le code voie RIVOLI et le code voie MAJIC2.';
COMMENT ON COLUMN commune.typvoi IS 'Type de voie - Indicateur de la classe de la voie. - 1 - voie, 2 - ensemble immobilier, 3 - lieu-dit, 4 -  pseudo-voie, 5 - voie provisoire.';
COMMENT ON COLUMN commune.indldnbat IS 'Indicateur lieu-dit non bâti - Zone servie uniquement pour les lieux-dits.Permet d’indiquer si le lieu-dit comporte ou non un bâtiment dans MAJIC.1 pour lieu-dit non bâti, 0 sinon.';
COMMENT ON COLUMN commune.motclas IS 'Mot classant - Dernier mot entièrement alphabétique du libellé de voie - Permet de restituer l''ordre alphabétique.';

COMMENT ON TABLE commune_majic IS 'Commune (MAJIC - introduit depuis le millésime 2015). Cet article contient le code INSEE associé au libellé de la commune.';
COMMENT ON COLUMN commune_majic.ccodep IS 'Code département - Code département INSEE';
COMMENT ON COLUMN commune_majic.ccodir IS 'Code direction - Code direction dge';
COMMENT ON COLUMN commune_majic.ccocom IS 'Code commune - 3 caractères';
COMMENT ON COLUMN commune_majic.libcom IS 'Libellé de la commune';

COMMENT ON TABLE voie IS 'Voie (Fantoir)';
COMMENT ON COLUMN voie.ccodep IS 'Code département - Code département INSEE';
COMMENT ON COLUMN voie.ccodir IS 'Code direction - Code direction dge';
COMMENT ON COLUMN voie.ccocom IS 'Code commune - code commune définie par Majic2';
COMMENT ON COLUMN voie.natvoiriv IS 'Nature de voie rivoli - ';
COMMENT ON COLUMN voie.ccoriv IS 'Code voie Rivoli - identifiant de voie dans la commune';
COMMENT ON COLUMN voie.clerivili IS 'Clé RIVOLI - zone alphabétique fournie par MAJIC2';
COMMENT ON COLUMN voie.natvoi IS 'nature de voie - ';
COMMENT ON COLUMN voie.libvoi IS 'libellé de voie - ';
COMMENT ON COLUMN voie.typcom IS 'Type de commune actuel (R ou N) - N - commune rurale, R - commune rencencée';
COMMENT ON COLUMN voie.ruract IS 'RUR actuel - indique si la commune est pseudo-recensée ou non (3-commune pseudo-recensée, blanc si rien)';
COMMENT ON COLUMN voie.carvoi IS 'caractère de voie - zone indiquant si la voie est privée (1) ou publique (0)';
COMMENT ON COLUMN voie.indpop IS 'indicateur de population - Précise la dernière situation connue de la commune au regard de la limite de 3000 habitants (= blanc si < 3000 h sinon = *).';
COMMENT ON COLUMN voie.poprel IS 'population réelle - dénombre la population recencée lors du dernier recensement';
COMMENT ON COLUMN voie.poppart IS 'population à part - dénombre la population comptée à part dans la commune';
COMMENT ON COLUMN voie.popfict IS 'population fictive - population fictive de la commune';
COMMENT ON COLUMN voie.annul IS 'Annulation Cet article indique que plus aucune entité topo n’est représentée par ce code. - O - voie annulée sans transfert, Q - voie annulée avec transfert, Q - commune annulée avec transfert.';
COMMENT ON COLUMN voie.dteannul IS 'date d''annulation - ';
COMMENT ON COLUMN voie.dtecreart IS 'Date de création de l''article - Date à laquelle l''article a été créé par création MAJIC2.';
COMMENT ON COLUMN voie.codvoi IS 'Code identifiant la voie dans MAJIC2. - Permet de faire le lien entre le code voie RIVOLI et le code voie MAJIC2.';
COMMENT ON COLUMN voie.typvoi IS 'Type de voie - Indicateur de la classe de la voie. - 1 - voie, 2 - ensemble immobilier, 3 - lieu-dit, 4 -  pseudo-voie, 5 - voie provisoire.';
COMMENT ON COLUMN voie.indldnbat IS 'Indicateur lieu-dit non bâti - Zone servie uniquement pour les lieux-dits.Permet d’indiquer si le lieu-dit comporte ou non un bâtiment dans MAJIC.1 pour lieu-dit non bâti, 0 sinon.';
COMMENT ON COLUMN voie.motclas IS 'Mot classant - Dernier mot entièrement alphabétique du libellé de voie - Permet de restituer l''ordre alphabétique.';

COMMENT ON TABLE geo_commune IS 'Territoire contenant un nombre entier de subdivisions de section cadastrales';
COMMENT ON COLUMN geo_commune.geo_commune IS 'Identifiant';
COMMENT ON COLUMN geo_commune.annee IS 'Année';
COMMENT ON COLUMN geo_commune.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_commune.idu IS 'Code INSEE';
COMMENT ON COLUMN geo_commune.tex2 IS 'Nom commune';
COMMENT ON COLUMN geo_commune.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_commune.update_dat IS 'Date de dernière modification';
COMMENT ON TABLE geo_section IS 'Partie du plan cadastral correspondant à une portion du territoire communal et comportant, suivant le cas, une ou plusieurs subdivisions de section';
COMMENT ON COLUMN geo_section.geo_section IS 'Identifiant';
COMMENT ON COLUMN geo_section.annee IS 'Année';
COMMENT ON COLUMN geo_section.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_section.idu IS 'Identifiant';
COMMENT ON COLUMN geo_section.tex IS 'Lettre(s) de section';
COMMENT ON COLUMN geo_section.geo_commune IS 'Commune';
COMMENT ON COLUMN geo_section.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_section.update_dat IS 'Date de dernière modification';
COMMENT ON TABLE geo_subdsect IS 'Portion de section cadastrale disposant de caractéristiques propres au regard notamment de son échelle, sa qualité, son mode de confection. Une section a au moins une subdivision de section. Cet objet correspond à la feuille cadastrale.';
COMMENT ON COLUMN geo_subdsect.geo_subdsect IS 'Identifiant';
COMMENT ON COLUMN geo_subdsect.annee IS 'Année';
COMMENT ON COLUMN geo_subdsect.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_subdsect.idu IS 'Identifiant';
COMMENT ON COLUMN geo_subdsect.geo_section IS 'Section';
COMMENT ON COLUMN geo_subdsect.geo_qupl IS 'Qualité du plan';
COMMENT ON COLUMN geo_subdsect.geo_copl IS 'Mode de confection';
COMMENT ON COLUMN geo_subdsect.eor IS 'Échelle d''origine du plan (que le dénominateur)';
COMMENT ON COLUMN geo_subdsect.dedi IS 'Date d''édition ou du confection du plan';
COMMENT ON COLUMN geo_subdsect.icl IS 'Orientation d''origine (en grade)';
COMMENT ON COLUMN geo_subdsect.dis IS 'Date d''incorporation PCI';
COMMENT ON COLUMN geo_subdsect.geo_inp IS 'Mode d''incorporation au plan';
COMMENT ON COLUMN geo_subdsect.dred IS 'Date de réédition';
COMMENT ON COLUMN geo_subdsect.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_subdsect.update_dat IS 'Date de dernière modification';
COMMENT ON TABLE geo_parcelle IS 'Portion de section cadastrale disposant de caractéristiques propres au regard notamment de son échelle, sa qualité, son mode de confection. Une section a au moins une subdivision de section. Cet objet correspond à la feuille cadastrale.';
COMMENT ON COLUMN geo_parcelle.geo_parcelle IS 'Identifiant';
COMMENT ON COLUMN geo_parcelle.annee IS 'Année';
COMMENT ON COLUMN geo_parcelle.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_parcelle.idu IS 'Identifiant';
COMMENT ON COLUMN geo_parcelle.geo_section IS 'Section';
COMMENT ON COLUMN geo_parcelle.supf IS 'Contenance MAJIC';
COMMENT ON COLUMN geo_parcelle.geo_indp IS 'Figuration de la parcelle au plan';
COMMENT ON COLUMN geo_parcelle.coar IS 'Code arpentage';
COMMENT ON COLUMN geo_parcelle.tex IS 'Numéro parcellaire';
COMMENT ON COLUMN geo_parcelle.tex2 IS 'tex2 - non documenté';
COMMENT ON COLUMN geo_parcelle.codm IS 'codm - non documenté';
COMMENT ON COLUMN geo_parcelle.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_parcelle.update_dat IS 'Date de dernière modification';
COMMENT ON TABLE geo_subdfisc IS 'Partie d''une parcelle ayant une seule nature de culture ou de propriété et constituant une unité au regard de la fiscalité directe locale.';
COMMENT ON COLUMN geo_subdfisc.geo_subdfisc IS 'Identifiant';
COMMENT ON COLUMN geo_subdfisc.annee IS 'Année';
COMMENT ON COLUMN geo_subdfisc.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_subdfisc.tex IS 'Lettre d''ordre';
COMMENT ON COLUMN geo_subdfisc.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_subdfisc.update_dat IS 'Date de dernière modification';
COMMENT ON TABLE geo_subdfisc_parcelle IS 'Lien subdivision fiscale - parcelle';
COMMENT ON COLUMN geo_subdfisc_parcelle.geo_subdfisc_parcelle IS 'Identifiant';
COMMENT ON COLUMN geo_subdfisc_parcelle.annee IS 'Année';
COMMENT ON COLUMN geo_subdfisc_parcelle.geo_subdfisc IS 'subdivision fiscale';
COMMENT ON COLUMN geo_subdfisc_parcelle.geo_parcelle IS 'geo_parcelle';
COMMENT ON TABLE geo_voiep IS 'Élément ponctuel permettant la gestion de l''ensemble immobilier auquel est associé son libellé.';
COMMENT ON COLUMN geo_voiep.geo_voiep IS 'Identifiant';
COMMENT ON COLUMN geo_voiep.annee IS 'Année';
COMMENT ON COLUMN geo_voiep.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_voiep.tex IS 'Nom de la voie';
COMMENT ON COLUMN geo_voiep.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_voiep.update_dat IS 'Date de dernière modification';
COMMENT ON TABLE geo_numvoie IS 'Numéro correspondant à l''adresse de la parcelle.';
COMMENT ON COLUMN geo_numvoie.geo_numvoie IS 'Identifiant';
COMMENT ON COLUMN geo_numvoie.annee IS 'Année';
COMMENT ON COLUMN geo_numvoie.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_numvoie.tex IS 'Numéro';
COMMENT ON COLUMN geo_numvoie.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_numvoie.update_dat IS 'Date de dernière modification';
COMMENT ON TABLE geo_numvoie_parcelle IS 'Lien subdivision fiscale - parcelle';
COMMENT ON COLUMN geo_numvoie_parcelle.geo_numvoie_parcelle IS 'Identifiant';
COMMENT ON COLUMN geo_numvoie_parcelle.annee IS 'Année';
COMMENT ON COLUMN geo_numvoie_parcelle.geo_numvoie IS 'Subdivision fiscale';
COMMENT ON COLUMN geo_numvoie_parcelle.geo_parcelle IS 'Parcelle';
COMMENT ON TABLE geo_lieudit IS 'Ensemble de parcelles entières comportant une même dénomination géographique résultant de l''usage.';
COMMENT ON COLUMN geo_lieudit.geo_lieudit IS 'Identifiant';
COMMENT ON COLUMN geo_lieudit.annee IS 'Année';
COMMENT ON COLUMN geo_lieudit.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_lieudit.tex IS 'Libellé';
COMMENT ON COLUMN geo_lieudit.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_lieudit.update_dat IS 'Date de dernière modification';
COMMENT ON TABLE geo_batiment IS 'Construction assise sur une ou plusieurs parcelles cadastrales.';
COMMENT ON COLUMN geo_batiment.geo_batiment IS 'Identifiant';
COMMENT ON COLUMN geo_batiment.annee IS 'Année';
COMMENT ON COLUMN geo_batiment.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_batiment.geo_dur IS 'Type de bâtiment';
COMMENT ON COLUMN geo_batiment.tex IS 'Texte du bâtiment';
COMMENT ON COLUMN geo_batiment.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_batiment.update_dat IS 'Date de dernière modification';
COMMENT ON TABLE geo_batiment_parcelle IS 'Lien subdivision fiscale - parcelle';
COMMENT ON COLUMN geo_batiment_parcelle.geo_batiment_parcelle IS 'Identifiant';
COMMENT ON COLUMN geo_batiment_parcelle.annee IS 'Année';
COMMENT ON COLUMN geo_batiment_parcelle.geo_batiment IS 'Bâtiment';
COMMENT ON COLUMN geo_batiment_parcelle.geo_parcelle IS 'Parcelle';
COMMENT ON TABLE geo_zoncommuni IS 'Voie du domaine non cadastré (ou passant sur des parcelles non figurées au plan) représentée par un élément linéaire correspondant à son axe.';
COMMENT ON COLUMN geo_zoncommuni.geo_zoncommuni IS 'Identifiant';
COMMENT ON COLUMN geo_zoncommuni.annee IS 'Année';
COMMENT ON COLUMN geo_zoncommuni.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_zoncommuni.tex IS 'Nom de la voie';
COMMENT ON COLUMN geo_zoncommuni.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_zoncommuni.update_dat IS 'Date de dernière modification';

COMMENT ON TABLE geo_tronfluv IS 'Élément surfacique (fermé) utilisé pour tous les cours d''eau et les rivages de mers. Un libellé y est associé.';
COMMENT ON COLUMN geo_tronfluv.geo_tronfluv IS 'Identifiant';
COMMENT ON COLUMN geo_tronfluv.annee IS 'Année';
COMMENT ON COLUMN geo_tronfluv.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_tronfluv.tex IS 'Nom du cours d''eau';
COMMENT ON COLUMN geo_tronfluv.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_tronfluv.update_dat IS 'Date de dernière modification';

COMMENT ON TABLE geo_tronroute IS 'Élément surfacique (fermé) utilisé pour tous les tronçons de routes. Un libellé y est associé.';
COMMENT ON COLUMN geo_tronroute.geo_tronroute IS 'Identifiant';
COMMENT ON COLUMN geo_tronroute.annee IS 'Année';
COMMENT ON COLUMN geo_tronroute.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_tronroute.tex IS 'Nom du cours d''eau';
COMMENT ON COLUMN geo_tronroute.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_tronroute.update_dat IS 'Date de dernière modification';

COMMENT ON TABLE geo_ptcanv IS 'Objet ponctuel servant d''appui aux opérations de lever des plans..';
COMMENT ON COLUMN geo_ptcanv.geo_ptcanv IS 'Identifiant';
COMMENT ON COLUMN geo_ptcanv.annee IS 'Année';
COMMENT ON COLUMN geo_ptcanv.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_ptcanv.idu IS 'Identifiant PCI';
COMMENT ON COLUMN geo_ptcanv.geo_can IS 'Origine du point';
COMMENT ON COLUMN geo_ptcanv.geo_ppln IS 'Précision planimétrique';
COMMENT ON COLUMN geo_ptcanv.geo_palt IS 'Précision altimétrique';
COMMENT ON COLUMN geo_ptcanv.geo_map IS 'Stabilité de matérialisation du support';
COMMENT ON COLUMN geo_ptcanv.geo_sym IS 'Genre du point';
COMMENT ON COLUMN geo_ptcanv.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_ptcanv.update_dat IS 'Date de dernière modification';

COMMENT ON TABLE geo_borne IS 'Borne située en limite de propriété et représentée par un symbole ponctuel.';
COMMENT ON COLUMN geo_borne.geo_borne IS 'Identifiant';
COMMENT ON COLUMN geo_borne.annee IS 'Année';
COMMENT ON COLUMN geo_borne.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_borne.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_borne.update_dat IS 'Date de dernière modification';
COMMENT ON TABLE geo_borne_parcelle IS 'Lien borne - parcelle';
COMMENT ON COLUMN geo_borne_parcelle.geo_borne_parcelle IS 'Identifiant';
COMMENT ON COLUMN geo_borne_parcelle.annee IS 'Année';
COMMENT ON COLUMN geo_borne_parcelle.geo_borne IS 'borne';
COMMENT ON COLUMN geo_borne_parcelle.geo_parcelle IS 'Parcelle';

COMMENT ON TABLE geo_croix IS 'Borne située en limite de propriété et représentée par un symbole ponctuel.';
COMMENT ON COLUMN geo_croix.geo_croix IS 'Identifiant';
COMMENT ON COLUMN geo_croix.annee IS 'Année';
COMMENT ON COLUMN geo_croix.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_croix.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_croix.update_dat IS 'Date de dernière modification';
COMMENT ON TABLE geo_croix_parcelle IS 'Lien croix - parcelle';
COMMENT ON COLUMN geo_croix_parcelle.geo_croix_parcelle IS 'Identifiant';
COMMENT ON COLUMN geo_croix_parcelle.annee IS 'Année';
COMMENT ON COLUMN geo_croix_parcelle.geo_croix IS 'Croix';
COMMENT ON COLUMN geo_croix_parcelle.geo_parcelle IS 'Parcelle';

COMMENT ON TABLE geo_symblim IS 'Symbole de limite de propriété représenté par un signe conventionnel de type ponctuel permettant de documenter le plan cadastral et d''en améliorer la lisibilité.';
COMMENT ON COLUMN geo_symblim.geo_symblim IS 'Identifiant';
COMMENT ON COLUMN geo_symblim.annee IS 'Année';
COMMENT ON COLUMN geo_symblim.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_symblim.ori IS 'Orientation';
COMMENT ON COLUMN geo_symblim.geo_sym IS 'Genre';
COMMENT ON COLUMN geo_symblim.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_symblim.update_dat IS 'Date de dernière modification';
COMMENT ON TABLE geo_symblim_parcelle IS 'Lien symblim - parcelle';
COMMENT ON COLUMN geo_symblim_parcelle.geo_symblim_parcelle IS 'Identifiant';
COMMENT ON COLUMN geo_symblim_parcelle.annee IS 'Année';
COMMENT ON COLUMN geo_symblim_parcelle.geo_symblim IS 'symblim';
COMMENT ON COLUMN geo_symblim_parcelle.geo_parcelle IS 'Parcelle';

COMMENT ON TABLE geo_tpoint IS 'Détail topographique ponctuel représenté par un signe conventionnel de type ponctuel permettant de documenter le plan cadastral et d''en améliorer la lisibilité.';
COMMENT ON COLUMN geo_tpoint.geo_tpoint IS 'Identifiant';
COMMENT ON COLUMN geo_tpoint.annee IS 'Année';
COMMENT ON COLUMN geo_tpoint.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_tpoint.ori IS 'Orientation';
COMMENT ON COLUMN geo_tpoint.tex IS 'Texte du détail';
COMMENT ON COLUMN geo_tpoint.geo_sym IS 'Genre';
COMMENT ON COLUMN geo_tpoint.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_tpoint.update_dat IS 'Date de dernière modification';
COMMENT ON TABLE geo_tpoint_commune IS 'Lien tpoint - commune';
COMMENT ON COLUMN geo_tpoint_commune.geo_tpoint_commune IS 'Identifiant';
COMMENT ON COLUMN geo_tpoint_commune.annee IS 'Année';
COMMENT ON COLUMN geo_tpoint_commune.geo_tpoint IS 'tpoint';
COMMENT ON COLUMN geo_tpoint_commune.geo_commune IS 'commune';

COMMENT ON TABLE geo_tline IS 'Détail topographique linéaire représenté par un signe conventionnel de type linéaire permettant de documenter le plan cadastral et d''en améliorer la lisibilité.';
COMMENT ON COLUMN geo_tline.geo_tline IS 'Identifiant';
COMMENT ON COLUMN geo_tline.annee IS 'Année';
COMMENT ON COLUMN geo_tline.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_tline.tex IS 'Texte du détail';
COMMENT ON COLUMN geo_tline.geo_sym IS 'Genre';
COMMENT ON COLUMN geo_tline.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_tline.update_dat IS 'Date de dernière modification';
COMMENT ON TABLE geo_tline_commune IS 'Lien tline - commune';
COMMENT ON COLUMN geo_tline_commune.geo_tline_commune IS 'Identifiant';
COMMENT ON COLUMN geo_tline_commune.annee IS 'Année';
COMMENT ON COLUMN geo_tline_commune.geo_tline IS 'tline';
COMMENT ON COLUMN geo_tline_commune.geo_commune IS 'commune';

COMMENT ON TABLE geo_tsurf IS 'Détail topographique surfacique représenté par un signe conventionnel de type surfacique permettant de documenter le plan cadastral et d''en améliorer la lisibilité';
COMMENT ON COLUMN geo_tsurf.geo_tsurf IS 'Identifiant';
COMMENT ON COLUMN geo_tsurf.annee IS 'Année';
COMMENT ON COLUMN geo_tsurf.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_tsurf.tex IS 'Texte du détail';
COMMENT ON COLUMN geo_tsurf.geo_sym IS 'Genre';
COMMENT ON COLUMN geo_tsurf.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_tsurf.update_dat IS 'Date de dernière modification';
COMMENT ON TABLE geo_tsurf_commune IS 'Lien tsurf - commune';
COMMENT ON COLUMN geo_tsurf_commune.geo_tsurf_commune IS 'Identifiant';
COMMENT ON COLUMN geo_tsurf_commune.annee IS 'Année';
COMMENT ON COLUMN geo_tsurf_commune.geo_tsurf IS 'tsurf';
COMMENT ON COLUMN geo_tsurf_commune.geo_commune IS 'commune';

COMMENT ON TABLE geo_label IS 'Libellés';
COMMENT ON COLUMN geo_label.ogc_fid IS 'Numéro d''enregistrement source';
COMMENT ON COLUMN geo_label.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_label.fon IS 'Nom en clair de la police typographique';
COMMENT ON COLUMN geo_label.hei IS 'Hauteur des caractères';
COMMENT ON COLUMN geo_label.tyu IS 'Type de l''unité utilisée';
COMMENT ON COLUMN geo_label.cef IS 'Facteur d''agrandissement';
COMMENT ON COLUMN geo_label.csp IS 'Espacement intercaractères';
COMMENT ON COLUMN geo_label.di1 IS 'Orientation composante X du vecteur hauteur';
COMMENT ON COLUMN geo_label.di2 IS 'Orientation composante Y du vecteur hauteur';
COMMENT ON COLUMN geo_label.di3 IS 'Orientation composante X du vecteur base';
COMMENT ON COLUMN geo_label.di4 IS 'Orientation composante Y du vecteur base';
COMMENT ON COLUMN geo_label.tpa IS 'Sens de l''écriture';
COMMENT ON COLUMN geo_label.hta IS 'Alignement horizontal du texte';
COMMENT ON COLUMN geo_label.vta IS 'Alignement vertical du texte';
COMMENT ON COLUMN geo_label.atr IS 'Identificateur de l''attribut à écrire';
COMMENT ON COLUMN geo_label.ogr_obj_lnk IS 'lien n°objet';
COMMENT ON COLUMN geo_label.ogr_obj_lnk_layer IS 'type objet';
COMMENT ON COLUMN geo_label.ogr_atr_val IS 'Ogr valeur';
COMMENT ON COLUMN geo_label.ogr_angle IS 'Ogr angle';
COMMENT ON COLUMN geo_label.ogr_font_size IS 'Ogr taille fonte';
COMMENT ON COLUMN geo_label.x_label IS 'Longitude';
COMMENT ON COLUMN geo_label.y_label IS 'Latitude';

COMMENT ON TABLE geo_unite_fonciere IS 'Regroupe les unités foncières, c est a dire la fusion de parcelles adjacentes d un même propriétaire';
COMMENT ON COLUMN geo_unite_fonciere.id IS 'Identifiant des unités foncières';
COMMENT ON COLUMN geo_unite_fonciere.comptecommunal IS 'Compte communal des parcelles composant l unité foncière';
COMMENT ON COLUMN geo_unite_fonciere.annee IS 'Année';

COMMENT ON TABLE parcelle_info IS 'Table de parcelles consolidées, proposant les géométries et les informations MAJIC principales, dont les propriétaires';
COMMENT ON COLUMN parcelle_info.ogc_fid IS 'Identifiant unique (base de données)';
COMMENT ON COLUMN parcelle_info.geo_parcelle IS 'Identifiant de la parcelle : année + département + direction + idu';
COMMENT ON COLUMN parcelle_info.idu IS 'Identifiant de la parcelle (unique par département et direction seulement)';
COMMENT ON COLUMN parcelle_info.tex IS 'Etiquette (code à 3 chiffres)';
COMMENT ON COLUMN parcelle_info.geo_section IS 'Code de la section (lien vers table geo_section.geo_section)';
COMMENT ON COLUMN parcelle_info.nomcommune IS 'Nom de la commune';
COMMENT ON COLUMN parcelle_info.codecommune IS 'Code de la commune à 3 chiffres';
COMMENT ON COLUMN parcelle_info.surface_geo IS 'Surface de la parcelle, calculée spatialement';
COMMENT ON COLUMN parcelle_info.contenance IS 'Surface cadastrale de la parcelle';
COMMENT ON COLUMN parcelle_info.lot IS 'Lot utilisé pendant l''import';
