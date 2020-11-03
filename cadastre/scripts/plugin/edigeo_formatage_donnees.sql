---- Les commentaires commençant par "-- " (2 tirets et un espace) seront affichés dans le log de progression
---- et utilisé comme étape d'import. Ex: "-- FORMATAGE DONNEES : DEBUT" ci-dessous
---- Pour écrire un commentaire non affiché, commencer par exemple par 4 tirets

-- FORMATAGE DONNEES : DEBUT
BEGIN;

-- Suppression des données du lot '[LOT]'
DELETE FROM [PREFIXE]geo_tsurf WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_numvoie WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_voiep  WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_lieudit WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_zoncommuni WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_tpoint WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_tline WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_tronfluv WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_tronroute WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_symblim WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_croix WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_borne WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_ptcanv WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_subdfisc WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_batiment WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_commune WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_section WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_subdsect WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_parcelle WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_unite_fonciere WHERE lot='[LOT]';

-- index pour optimisation
DROP INDEX IF EXISTS idx_edigeorel_vers;
DROP INDEX IF EXISTS idx_edigeorel_de;

CREATE INDEX idx_edigeorel_vers ON [PREFIXE]edigeo_rel (vers);
CREATE INDEX idx_edigeorel_de ON [PREFIXE]edigeo_rel (de);
CREATE INDEX idx_edigeorel_nom ON [PREFIXE]edigeo_rel (nom);

-- geo_commune
---- pour éviter les doublons des données EDIGEO on sélectionne les communes avec le update_date le plus récent
INSERT INTO [PREFIXE]geo_commune
( geo_commune, annee, object_rid, idu, tex2, creat_date, update_dat, commune, geom, lot)
  SELECT
    '[DEPDIR]'||SUBSTRING(idu,1,8), '[ANNEE]',
    object_rid, idu, tex2,
    to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'),
    to_date(to_char(update_date,'00000000'), 'YYYYMMDD'),
    '[DEPDIR]'||SUBSTRING(idu,1,3),
    ST_Multi(ST_Union(ST_CollectionExtract(ST_MakeValid(geom),3))),
    '[LOT]'
  FROM [PREFIXE]commune_id edi_commune
  WHERE ogc_fid = (
    SELECT ogc_fid
    FROM [PREFIXE]commune_id
    WHERE idu = edi_commune.idu
    ORDER BY update_date DESC
    LIMIT 1
  )
  GROUP BY object_rid, idu, tex2, creat_date, update_date
  ORDER BY idu, update_date DESC ;

UPDATE [PREFIXE]commune SET geo_commune=commune.commune;
DELETE FROM [PREFIXE]geo_commune WHERE tex2 IS NULL or trim(tex2) = '';
DELETE FROM [PREFIXE]commune WHERE ccocom IS NULL or trim(ccocom) = '';

-- geo_section
---- pour éviter les doublons des données EDIGEO on sélectionne les sections avec le update_date le plus récent
INSERT INTO [PREFIXE]geo_section
( geo_section, annee, object_rid, idu, tex, geo_commune, creat_date, update_dat, geom, lot)
  SELECT
    '[DEPDIR]'||SUBSTRING(idu,1,8), '[ANNEE]',
    object_rid, idu, tex, '[DEPDIR]'||SUBSTRING(idu,1,3),
    to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'),
    to_date(to_char(update_date,'00000000'), 'YYYYMMDD'),
    ST_Multi(ST_Union(ST_CollectionExtract(ST_MakeValid(geom),3))),
    '[LOT]'
  FROM [PREFIXE]section_id edi_section
  WHERE ogc_fid = (
    SELECT ogc_fid FROM [PREFIXE]section_id
    WHERE idu = edi_section.idu
    ORDER BY update_date DESC
    LIMIT 1
  )
  GROUP BY object_rid, idu, tex, creat_date, update_date
  ORDER BY idu, update_date DESC ;

-- geo_subdsect
INSERT INTO [PREFIXE]geo_subdsect
(geo_subdsect, annee, object_rid, idu, geo_section, geo_qupl, geo_copl, eor, dedi, icl, dis, geo_inp, dred, creat_date, update_dat, geom, lot)
SELECT DISTINCT '[DEPDIR]'||SUBSTRING(idu,1,10), '[ANNEE]', object_rid, idu, '[DEPDIR]'||SUBSTRING(idu,1,8), qupl, copl, to_number(eor,'0000000000'),
CASE WHEN dedi ~ '^\d{2}/\d{2}/\d{4}$' THEN to_date(dedi,'DD/MM/YYYY') ELSE NULL END,
floor(icl),
CASE WHEN dis ~ '^\d{2}/\d{2}/\d{4}$' THEN to_date(dis, 'DD/MM/YYYY') ELSE NULL END,
inp,
CASE WHEN dred ~ '^\d{2}/\d{2}/\d{4}$' THEN to_date(dred, 'DD/MM/YYYY') ELSE NULL END,
to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(ST_CollectionExtract(ST_MakeValid(geom),3)),'[LOT]'
FROM [PREFIXE]subdsect_id
;

-- geo_parcelle
DROP INDEX IF EXISTS [PREFIXE]parcelle_id_object_rid;
CREATE INDEX parcelle_id_object_rid ON [PREFIXE]parcelle_id (object_rid);
DROP INDEX IF EXISTS [PREFIXE]parcelle_id_temp_idx;
CREATE INDEX parcelle_id_temp_idx ON [PREFIXE]parcelle_id ('[DEPDIR]'||SUBSTR(idu,1,8));
DROP INDEX IF EXISTS [PREFIXE]geo_subdsect_annee_idx;
CREATE INDEX geo_subdsect_annee_idx ON [PREFIXE]geo_subdsect (annee);
DROP INDEX IF EXISTS [PREFIXE]geo_subdsect_lot_idx;
CREATE INDEX geo_subdsect_lot_idx ON [PREFIXE]geo_subdsect (lot);
DROP INDEX IF EXISTS [PREFIXE]geo_subdsect_object_rid_idx;
CREATE INDEX geo_subdsect_object_rid_idx ON [PREFIXE]geo_subdsect (object_rid);

INSERT INTO [PREFIXE]geo_parcelle
(geo_parcelle, annee, object_rid, idu, geo_section, geo_subdsect, supf, geo_indp, coar, tex, tex2, codm, creat_date, update_dat, inspireid, geom, lot)
SELECT DISTINCT '[DEPDIR]'||p.idu, '[ANNEE]', p.object_rid, p.idu, '[DEPDIR]'||SUBSTRING(p.idu,1,8), foo.geo_subdsect, p.supf, p.indp, p.coar, p.tex, p.tex2, p.codm, to_date(to_char(p.creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(p.update_date,'00000000'), 'YYYYMMDD'), 'FR'||'[DEPDIR]'||p.idu, ST_Multi(ST_CollectionExtract(ST_MakeValid(p.geom),3)), '[LOT]'
FROM [PREFIXE]parcelle_id AS p
LEFT JOIN (
    SELECT s.geo_section, s.geo_subdsect, r.de
    FROM
        [PREFIXE]geo_subdsect s,
        (SELECT DISTINCT de, vers FROM [PREFIXE]edigeo_rel WHERE nom='Rel_PARCELLE_SUBDSECT') AS r
    WHERE s.annee = '[ANNEE]' AND s.lot ='[LOT]' AND r.vers = s.object_rid
) foo
ON foo.de = p.object_rid  AND '[DEPDIR]'||SUBSTR(p.idu,1,8) = foo.geo_section
WHERE p.idu IS NOT NULL
;

DROP INDEX IF EXISTS [PREFIXE]parcelle_id_temp_idx;
DROP INDEX IF EXISTS [PREFIXE]geo_subdsect_annee_idx;
DROP INDEX IF EXISTS [PREFIXE]geo_subdsect_object_rid_idx;
DROP INDEX IF EXISTS [PREFIXE]geo_subdsect_lot_idx;

-- Indexes sur geo_parcelle et geo_commune pour optimisation
DROP INDEX IF EXISTS [PREFIXE]geo_parcelle_annee_idx;
CREATE INDEX geo_parcelle_annee_idx ON [PREFIXE]geo_parcelle (annee, object_rid );
DROP INDEX IF EXISTS [PREFIXE]geo_commune_annee_idx;
CREATE INDEX geo_commune_annee_idx ON [PREFIXE]geo_commune (annee, object_rid );

-- geo_subdfisc
INSERT INTO [PREFIXE]geo_subdfisc (annee, object_rid, tex, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid,  CASE WHEN tex IS NULL THEN '' ELSE tex END, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(ST_CollectionExtract(ST_MakeValid(geom),3)), '[LOT]'
FROM [PREFIXE]subdfisc_id;

-- geo_subdfisc_parcelle
DROP INDEX IF EXISTS [PREFIXE]geo_subdfisc_annee_idx;
CREATE INDEX geo_subdfisc_annee_idx ON [PREFIXE]geo_subdfisc (annee, object_rid);
INSERT INTO [PREFIXE]geo_subdfisc_parcelle (annee, geo_subdfisc, geo_parcelle)
SELECT s.annee, s.geo_subdfisc, p.geo_parcelle
FROM [PREFIXE]geo_subdfisc s, [PREFIXE]geo_parcelle p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND s.lot='[LOT]' AND p.lot=s.lot AND r.nom='Rel_SUBDFISC_PARCELLE' AND s.object_rid=r.de AND p.object_rid=r.vers;
DROP INDEX IF EXISTS [PREFIXE]geo_subdfisc_annee_idx;

-- geo_voiep
INSERT INTO [PREFIXE]geo_voiep
( annee, object_rid, tex, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid, tex, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), geom, '[LOT]'
FROM [PREFIXE]voiep_id;

-- geo_numvoie
INSERT INTO [PREFIXE]geo_numvoie
( annee, object_rid, tex, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid, tex, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), geom, '[LOT]'
FROM [PREFIXE]numvoie_id;

-- geo_numvoie_parcelle
DROP INDEX IF EXISTS [PREFIXE]geo_numvoie_annee_idx;
CREATE INDEX geo_numvoie_annee_idx ON [PREFIXE]geo_numvoie (annee, object_rid);
INSERT INTO [PREFIXE]geo_numvoie_parcelle (annee, geo_numvoie, geo_parcelle)
SELECT s.annee, s.geo_numvoie, p.geo_parcelle
FROM [PREFIXE]geo_numvoie s, [PREFIXE]geo_parcelle p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND s.lot='[LOT]' AND p.lot=s.lot AND r.nom='Rel_NUMVOIE_PARCELLE' AND s.object_rid=r.de AND p.object_rid=r.vers;
DROP INDEX IF EXISTS [PREFIXE]geo_numvoie_annee_idx;

-- geo_lieudit
INSERT INTO [PREFIXE]geo_lieudit
( annee, object_rid, tex, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid,
trim( Coalesce(trim(tex),'') || ' ' || Coalesce(trim(tex2),'') || ' ' || Coalesce(trim(tex3),'') || ' ' || Coalesce(trim(tex4),'') || ' ' || Coalesce(trim(tex5),'') || ' ' || Coalesce(trim(tex6),'') || ' ' || Coalesce(trim(tex7),'') || ' ' || Coalesce(trim(tex8),'') || ' ' || Coalesce(trim(tex9),'') || ' ' || Coalesce(trim(tex10),'')),
to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(ST_CollectionExtract(ST_MakeValid(geom),3)), '[LOT]'
FROM [PREFIXE]lieudit_id;

-- geo_batiment
INSERT INTO [PREFIXE]geo_batiment( geo_batiment, annee, object_rid, geo_dur, tex, creat_date, update_dat, geom, lot)
SELECT '[DEPDIR]'|| replace(to_char(ogc_fid,'0000000'),' ',''), '[ANNEE]', object_rid, dur, tex, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(ST_CollectionExtract(ST_MakeValid(geom),3)), '[LOT]'
FROM [PREFIXE]batiment_id;

-- geo_batiment_parcelle
DROP INDEX IF EXISTS [PREFIXE]geo_batiment_annee_idx;
CREATE INDEX geo_batiment_annee_idx ON [PREFIXE]geo_batiment (annee, object_rid);
DROP INDEX IF EXISTS [PREFIXE]geo_batiment_geom_idx;
CREATE INDEX geo_batiment_geom_idx ON [PREFIXE]geo_batiment USING GIST (ST_Centroid(geom));
DROP INDEX IF EXISTS [PREFIXE]geo_parcelle_geom_idx;
CREATE INDEX geo_parcelle_geom_idx ON [PREFIXE]geo_parcelle USING GIST (geom);
INSERT INTO [PREFIXE]geo_batiment_parcelle (annee, geo_batiment, geo_parcelle)
SELECT s.annee, s.geo_batiment, p.geo_parcelle
FROM [PREFIXE]geo_batiment s, [PREFIXE]geo_parcelle p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND s.lot='[LOT]' AND p.lot=s.lot AND r.nom='Rel_BATIMENT_PARCELLE'
AND s.object_rid=r.de AND p.object_rid=r.vers
AND ST_Intersects(ST_Centroid(s.geom), p.geom)
;
DROP INDEX IF EXISTS [PREFIXE]geo_batiment_annee_idx;
DROP INDEX IF EXISTS [PREFIXE]geo_batiment_geom_idx;
DROP INDEX IF EXISTS [PREFIXE]geo_parcelle_geom_idx;

-- geo_zoncommuni
INSERT INTO [PREFIXE]geo_zoncommuni( annee, object_rid, tex, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid, COALESCE(trim(tex),'')||COALESCE(' '||trim(tex2),'')||COALESCE(' '||trim(tex3),'')||COALESCE(' '||trim(tex4),'')||COALESCE(' '||trim(tex5),'')||COALESCE(' '||trim(tex6),'')||COALESCE(' '||trim(tex7),'')||COALESCE(' '||trim(tex8),'')||COALESCE(' '||trim(tex9),'')||COALESCE(' '||trim(tex10),'') as tex, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(ST_CollectionExtract(ST_MakeValid(geom),2)), '[LOT]'
FROM [PREFIXE]zoncommuni_id;

-- geo_tronfluv
INSERT INTO [PREFIXE]geo_tronfluv( annee, object_rid, tex, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid, COALESCE(trim(tex),'')||COALESCE(' '||trim(tex2),'')||COALESCE(' '||trim(tex3),'')||COALESCE(' '||trim(tex4),'')||COALESCE(' '||trim(tex5),'')||COALESCE(' '||trim(tex6),'')||COALESCE(' '||trim(tex7),'')||COALESCE(' '||trim(tex8),'')||COALESCE(' '||trim(tex9),'')||COALESCE(' '||trim(tex10),'') as tex, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(ST_CollectionExtract(ST_MakeValid(geom),3)), '[LOT]'
FROM [PREFIXE]tronfluv_id;

-- geo_tronroute
INSERT INTO [PREFIXE]geo_tronroute( annee, object_rid, tex, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid, COALESCE(trim(tex),'')||COALESCE(' '||trim(tex2),'')||COALESCE(' '||trim(tex3),'')||COALESCE(' '||trim(tex4),'')||COALESCE(' '||trim(tex5),'')||COALESCE(' '||trim(tex6),'')||COALESCE(' '||trim(tex7),'')||COALESCE(' '||trim(tex8),'')||COALESCE(' '||trim(tex9),'')||COALESCE(' '||trim(tex10),'') as tex, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(ST_CollectionExtract(ST_MakeValid(geom),3)), '[LOT]'
FROM [PREFIXE]tronroute_id;

-- geo_sym
INSERT INTO [PREFIXE]geo_sym SELECT DISTINCT sym, 'Inconnu '||sym
FROM [PREFIXE]ptcanv_id
WHERE sym NOT IN (SELECT geo_sym FROM [PREFIXE]geo_sym)
AND sym IS NOT NULL;

-- geo_ptcanv
INSERT INTO [PREFIXE]geo_ptcanv( annee, object_rid, idu, geo_can, geo_ppln, geo_palt, geo_map, geo_sym, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid, idu, can, ppln, palt, map, sym, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), geom, '[LOT]'
FROM [PREFIXE]ptcanv_id;

-- geo_borne
INSERT INTO [PREFIXE]geo_borne( annee, object_rid, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid,  to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), geom, '[LOT]'
FROM [PREFIXE]borne_id;

-- geo_borne_parcelle
DROP INDEX IF EXISTS [PREFIXE]geo_borne_annee_idx;
CREATE INDEX geo_borne_annee_idx ON [PREFIXE]geo_borne (annee, object_rid);
INSERT INTO [PREFIXE]geo_borne_parcelle (annee, geo_borne, geo_parcelle)
SELECT s.annee, s.geo_borne, p.geo_parcelle
FROM [PREFIXE]geo_borne s, [PREFIXE]geo_parcelle p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND s.lot='[LOT]' AND p.lot=s.lot AND r.nom='Rel_BORNE_PARCELLE' AND s.object_rid=r.de AND p.object_rid=r.vers;
DROP INDEX IF EXISTS [PREFIXE]geo_borne_annee_idx;

-- geo_croix
INSERT INTO [PREFIXE]geo_croix( annee, object_rid, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid,  to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), geom, '[LOT]'
FROM [PREFIXE]croix_id;

-- geo_croix_parcelle
DROP INDEX IF EXISTS [PREFIXE]geo_croix_annee_idx;
CREATE INDEX geo_croix_annee_idx ON [PREFIXE]geo_croix (annee, object_rid);
INSERT INTO [PREFIXE]geo_croix_parcelle (annee, geo_croix, geo_parcelle)
SELECT s.annee, s.geo_croix, p.geo_parcelle
FROM [PREFIXE]geo_croix s, [PREFIXE]geo_parcelle p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND s.lot='[LOT]' AND p.lot=s.lot AND r.nom='Rel_CROIX_PARCELLE' AND s.object_rid=r.de AND p.object_rid=r.vers;
DROP INDEX IF EXISTS [PREFIXE]geo_croix_annee_idx;

-- geo_symblim
INSERT INTO [PREFIXE]geo_symblim( annee, object_rid, ori, geo_sym, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid,  ori, sym, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), geom, '[LOT]'
FROM [PREFIXE]symblim_id;
UPDATE [PREFIXE]geo_symblim set ori=360-ori WHERE annee='[ANNEE]' AND lot='[LOT]';

-- geo_symblim_parcelle
DROP INDEX IF EXISTS [PREFIXE]geo_symblim_annee_idx;
CREATE INDEX geo_symblim_annee_idx ON [PREFIXE]geo_symblim (annee, object_rid);
INSERT INTO [PREFIXE]geo_symblim_parcelle (annee, geo_symblim, geo_parcelle)
SELECT s.annee, s.geo_symblim, p.geo_parcelle
FROM [PREFIXE]geo_symblim s, [PREFIXE]geo_parcelle p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND s.lot='[LOT]' AND p.lot=s.lot AND r.nom='Rel_SYMBLIM_PARCELLE' AND s.object_rid=r.de AND p.object_rid=r.vers;
DROP INDEX IF EXISTS [PREFIXE]geo_symblim_annee_idx;

-- geo_tpoint
INSERT INTO [PREFIXE]geo_tpoint( annee, object_rid, ori,tex, geo_sym, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid,  ori, tex, sym, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), geom, '[LOT]'
FROM [PREFIXE]tpoint_id;
UPDATE [PREFIXE]geo_tpoint SET ori=360-ori WHERE annee='[ANNEE]' AND lot='[LOT]' AND ori IS NOT NULL;

-- geo_tpoint_commune
DROP INDEX IF EXISTS [PREFIXE]geo_tpoint_object_rid_idx;
CREATE INDEX geo_tpoint_object_rid_idx ON [PREFIXE]geo_tpoint (object_rid);
DROP INDEX IF EXISTS [PREFIXE]geo_tpoint_annee_idx;
CREATE INDEX geo_tpoint_annee_idx ON [PREFIXE]geo_tpoint (annee);
INSERT INTO [PREFIXE]geo_tpoint_commune (annee, geo_tpoint, geo_commune)
SELECT s.annee, s.geo_tpoint, p.geo_commune
FROM [PREFIXE]geo_tpoint s, [PREFIXE]geo_commune p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND s.lot='[LOT]' AND p.lot=s.lot AND r.nom='Rel_DETOPO_COMMUNE' AND p.object_rid=r.de AND s.object_rid=r.vers;
DROP INDEX IF EXISTS [PREFIXE]geo_tpoint_object_rid_idx;
DROP INDEX IF EXISTS [PREFIXE]geo_tpoint_annee_idx;

-- geo_tline
INSERT INTO [PREFIXE]geo_tline( annee, object_rid, tex, geo_sym, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid,  tex, sym, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(ST_CollectionExtract(ST_MakeValid(geom),2)), '[LOT]'
FROM [PREFIXE]tline_id;

-- geo_tline_commune
DROP INDEX IF EXISTS [PREFIXE]geo_tline_object_rid_idx;
CREATE INDEX geo_tline_object_rid_idx ON [PREFIXE]geo_tline (object_rid);
DROP INDEX IF EXISTS [PREFIXE]geo_tline_annee_idx;
CREATE INDEX geo_tline_annee_idx ON [PREFIXE]geo_tline (annee);
INSERT INTO [PREFIXE]geo_tline_commune (annee, geo_tline, geo_commune)
SELECT s.annee, s.geo_tline, p.geo_commune
FROM [PREFIXE]geo_tline s, [PREFIXE]geo_commune p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND s.lot='[LOT]' AND p.lot=s.lot AND r.nom='Rel_DETOPO_COMMUNE' AND p.object_rid=r.de AND s.object_rid=r.vers;
DROP INDEX IF EXISTS [PREFIXE]geo_tline_object_rid_idx;
DROP INDEX IF EXISTS [PREFIXE]geo_tline_annee_idx;

-- geo_tsurf
INSERT INTO [PREFIXE]geo_tsurf( annee, object_rid, tex, geo_sym, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid,  tex, sym, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(ST_CollectionExtract(ST_MakeValid(geom),3)), '[LOT]'
FROM [PREFIXE]tsurf_id;

-- geo_tsurf_commune
DROP INDEX IF EXISTS [PREFIXE]geo_tsurf_object_rid_idx;
CREATE INDEX geo_tsurf_object_rid_idx ON [PREFIXE]geo_tsurf (object_rid);
DROP INDEX IF EXISTS [PREFIXE]geo_tsurf_annee_idx;
CREATE INDEX geo_tsurf_annee_idx ON [PREFIXE]geo_tsurf (annee);
INSERT INTO [PREFIXE]geo_tsurf_commune (annee, geo_tsurf, geo_commune)
SELECT s.annee, s.geo_tsurf, p.geo_commune
FROM [PREFIXE]geo_tsurf s, [PREFIXE]geo_commune p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND s.lot='[LOT]' AND p.lot=s.lot AND r.nom='Rel_DETOPO_COMMUNE' AND p.object_rid=r.de AND s.object_rid=r.vers;
DROP INDEX IF EXISTS [PREFIXE]geo_tsurf_object_rid_idx;
DROP INDEX IF EXISTS [PREFIXE]geo_tsurf_annee_idx;

-- suppression des index temporaires
DROP INDEX [PREFIXE]idx_edigeorel_vers;
DROP INDEX [PREFIXE]idx_edigeorel_de;
DROP INDEX [PREFIXE]idx_edigeorel_nom;

TRUNCATE [PREFIXE]edigeo_rel;
DROP INDEX IF EXISTS [PREFIXE]geo_parcelle_annee_idx;
DROP INDEX IF EXISTS [PREFIXE]geo_commune_annee_idx;

-- analyses
ANALYZE [PREFIXE]geo_commune;
ANALYZE [PREFIXE]geo_section;
ANALYZE [PREFIXE]geo_subdsect;
ANALYZE [PREFIXE]geo_parcelle;
ANALYZE [PREFIXE]geo_subdfisc;
ANALYZE [PREFIXE]geo_subdfisc_parcelle;
ANALYZE [PREFIXE]geo_voiep;
ANALYZE [PREFIXE]geo_numvoie;
ANALYZE [PREFIXE]geo_numvoie_parcelle;
ANALYZE [PREFIXE]geo_lieudit;
ANALYZE [PREFIXE]geo_batiment;
ANALYZE [PREFIXE]geo_batiment_parcelle;
ANALYZE [PREFIXE]geo_zoncommuni;
ANALYZE [PREFIXE]geo_tronfluv;
ANALYZE [PREFIXE]geo_tronroute;
ANALYZE [PREFIXE]geo_sym;
ANALYZE [PREFIXE]geo_ptcanv;
ANALYZE [PREFIXE]geo_borne;
ANALYZE [PREFIXE]geo_borne_parcelle;
ANALYZE [PREFIXE]geo_croix;
ANALYZE [PREFIXE]geo_croix_parcelle;
ANALYZE [PREFIXE]geo_symblim;
ANALYZE [PREFIXE]geo_symblim_parcelle;
ANALYZE [PREFIXE]geo_tpoint;
ANALYZE [PREFIXE]geo_tpoint_commune;
ANALYZE [PREFIXE]geo_tline;
ANALYZE [PREFIXE]geo_tline_commune;
ANALYZE [PREFIXE]geo_tsurf;
ANALYZE [PREFIXE]geo_tsurf_commune;
ANALYSE [PREFIXE]geo_unite_fonciere;
COMMIT;
-- FORMATAGE DONNEES : FIN

