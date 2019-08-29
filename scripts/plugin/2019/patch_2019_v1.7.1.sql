
-- les requêtes SQL ci-dessous permettent de patcher une base de données
-- créée au format v 1.7.1


-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
-- mise à jour MAJIC version 2019


-- SET search_path = "cadastre_qgis" ;




-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

-- table parcelle : nouvel attribut ccpper

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

-- les indexes
CREATE INDEX idx_parcelle_comptecommunal ON parcelle USING btree (comptecommunal);
CREATE INDEX idx_parcelle_voie ON parcelle USING btree (voie);
CREATE INDEX parcelle_dnupro_idx ON parcelle USING btree (dnupro);

-- les commentaires
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




-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


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




-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

-- table local00 : nouvel attribut ccpper


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

-- indexes
CREATE INDEX idx_local00_invar ON local00 USING btree (invar);
CREATE INDEX idx_local00_parcelle ON local00 USING btree (parcelle);
CREATE INDEX idx_local00_voie ON local00 USING btree (voie) ;
CREATE INDEX idxan_local00 ON local00 USING btree (annee) ;

-- commentaires
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
COMMENT ON COLUMN local00.ccpper IS 'Code de trésorerie gestionnaire - ';
COMMENT ON COLUMN local00.locinc IS 'code local sans évaluation - INDISPONIBLE';




-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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

-- indexes
CREATE INDEX idxan_pevexoneration_imposable ON pevexoneration_imposable (annee);
CREATE INDEX idx_pevexoneration_imposable_pev ON pevexoneration_imposable (pev);

-- commentaires
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

-- indexes
CREATE INDEX idxan_pevexoneration_imposee ON pevexoneration_imposee (annee);
CREATE INDEX idx_pevexoneration_imposee_pev ON pevexoneration_imposee (pev);


-- commentaires
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




-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


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


