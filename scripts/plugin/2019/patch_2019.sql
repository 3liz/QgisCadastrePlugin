-- modification de strucutre en 2019
-- attribut ccpper ajouté en 2019
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

-- attribut ccpper ajouté en 2019
DROP TABLE IF EXISTS parcelle CASCADE;
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

-- nouvelle table de nomenclature
DROP TABLE IF EXISTS fburx CASCADE;
CREATE TABLE fburx 
(
    fburx text NOT NULL,
    fburx_lib text,
    CONSTRAINT fburx_pkey PRIMARY KEY (fburx)
);