
-- les requêtes SQL ci-dessous permettent de patcher une base de données
-- créée au format v 1.7.1


-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
-- mise à jour MAJIC version 2019

-- SET search_path = "cadastre_qgis" ;

-- nouvel attribut ccpper
DROP TABLE IF EXISTS parcelle CASCADE;
CREATE TABLE parcelle
(
    parcelle text NOT NULL,
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
    lot text,
    CONSTRAINT parcelle_pk PRIMARY KEY (parcelle)
);


-- la suppression / recréation de la table parcele implique de refaire la vue v_geo_parcelle
CREATE OR REPLACE VIEW v_geo_parcelle AS
 SELECT g.geo_parcelle,
    g.annee,
    g.object_rid,
    g.idu,
    g.geo_section,
    g.geo_subdsect,
    g.supf,
    g.geo_indp,
    g.coar,
    g.tex,
    g.tex2,
    g.codm,
    g.creat_date,
    g.update_dat,
    g.inspireid,
    g.lot,
    g.ogc_fid,
    g.geom,
    p.comptecommunal,
    p.voie
   FROM geo_parcelle g LEFT JOIN parcelle p ON g.geo_parcelle = p.parcelle;




-- nouvel attribut ccpper
DROP TABLE IF EXISTS local00 CASCADE;
CREATE TABLE local00
(
    local00 text NOT NULL,
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
    ccpper text,
    locinc text,
    lot text,
    CONSTRAINT local00_pk PRIMARY KEY (local00)
);

-- nouvelle table pevexoneration_imposable
DROP TABLE IF EXISTS pevexoneration_imposable CASCADE;
CREATE TABLE pevexoneration_imposable
(
    pevexoneration_imposable text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    invar text,
    janbil text,
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

-- nouvelle table pevexoneration_imposee
DROP TABLE IF EXISTS pevexoneration_imposee CASCADE;
CREATE TABLE pevexoneration_imposee
(
    pevexoneration_imposee text,
    annee text,
    ccodep text,
    ccodir text,
    ccocom text,
    invar text,
    janbil text,
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

-- nouvelle table de nomenclature
DROP TABLE IF EXISTS fburx CASCADE;
CREATE TABLE fburx 
(
    fburx text NOT NULL,
    fburx_lib text,
    CONSTRAINT fburx_pkey PRIMARY KEY (fburx)
);


-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
-- autres modifications

-- néant


