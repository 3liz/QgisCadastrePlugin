-- FORMATAGE DONNEES : DEBUT;
BEGIN;
DELETE FROM [PREFIXE]geo_tsurf WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_numvoie WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_voiep  WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_lieudit WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_zoncommuni WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_tpoint WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_tline WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_tronfluv WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_symblim WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_croix WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_borne WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_ptcanv WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_subdfisc WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_batiment WHERE lot='[LOT]';
DELETE FROM [PREFIXE]geo_commune WHERE lot='[LOT]';

-- index pour optimisation
CREATE INDEX idx_edigeorel_vers ON [PREFIXE]edigeo_rel (vers);
CREATE INDEX idx_edigeorel_de ON [PREFIXE]edigeo_rel (de);

-- geo_commune;
INSERT INTO [PREFIXE]geo_commune
( geo_commune, annee, object_rid, idu, tex2, creat_date, update_dat, geom, lot, ogc_fid)
SELECT DISTINCT ON (tex2, idu) '[ANNEE]'||SUBSTRING(idu,1,3), '[ANNEE]', object_rid, idu, tex2, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(geom), '[LOT]', ogc_fid
FROM [PREFIXE]commune_id
ORDER BY tex2, idu, update_date DESC, creat_date DESC;
UPDATE [PREFIXE]geo_commune set commune= p.commune FROM [PREFIXE]commune p WHERE p.annee='[ANNEE]' AND p.commune=SUBSTRING(geo_commune.geo_commune,1,4)||'[DEPDIR]'||SUBSTRING(geo_commune.geo_commune,5,3) AND geo_commune.annee='[ANNEE]';
UPDATE [PREFIXE]commune SET geo_commune=g.geo_commune FROM [PREFIXE]geo_commune g WHERE g.commune=commune.commune AND g.annee='[ANNEE]';

-- geo_section;
INSERT INTO [PREFIXE]geo_section
( geo_section, annee, object_rid, idu, tex, geo_commune, creat_date, update_dat, geom, lot, ogc_fid)
SELECT DISTINCT '[ANNEE]'||SUBSTRING(idu,1,8), '[ANNEE]', object_rid, idu, tex, '[ANNEE]'||SUBSTRING(idu,1,3), to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(ST_Union((geom))), '[LOT]', ogc_fid
FROM [PREFIXE]section_id
GROUP BY object_rid, idu, tex, creat_date, update_date, ogc_fid;

-- geo_subdsect;
INSERT INTO [PREFIXE]geo_subdsect
(geo_subdsect, annee, object_rid, idu, geo_section, geo_qupl, geo_copl, eor, dedi, icl, dis, geo_inp, dred, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]'||SUBSTRING(idu,1,10), '[ANNEE]', object_rid, idu, '[ANNEE]'||SUBSTRING(idu,1,8), qupl, copl, to_number(eor,'0000000000'), to_date(dedi, 'DD/MM/YYYYY'), floor(icl), to_date(dis, 'DD/MM/YYYYY'), inp, to_date(dred,'DD/MM/YYYY'), to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(geom),'[LOT]'
FROM [PREFIXE]subdsect_id;

-- geo_parcelle;
INSERT INTO [PREFIXE]geo_parcelle
(geo_parcelle, annee, object_rid, idu, geo_section, supf, geo_indp, coar, tex, tex2, codm, creat_date, update_dat, geom, lot, ogc_fid)
SELECT '[ANNEE]'||idu, '[ANNEE]', object_rid, idu, '[ANNEE]'||SUBSTRING(idu,1,8), supf, indp, coar, tex, tex2, codm, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(geom), '[LOT]', ogc_fid
FROM [PREFIXE]parcelle_id;
-- ajout des subdsect
UPDATE [PREFIXE]geo_parcelle set geo_subdsect=s.geo_subdsect FROM [PREFIXE]geo_subdsect s, [PREFIXE]edigeo_rel r
WHERE s.annee=geo_parcelle.annee AND geo_parcelle.annee='[ANNEE]' AND r.nom='Rel_PARCELLE_SUBDSECT' AND r.de=geo_parcelle.object_rid AND vers=s.object_rid;

-- ajout de l'identifiant de parcelle dans la table geo_parcelle
UPDATE [PREFIXE]geo_parcelle SET (parcelle, dvoilib, comptecommunal ) = (p.parcelle, p.dvoilib, p.comptecommunal)
FROM [PREFIXE]parcelle p
WHERE p.annee='[ANNEE]' AND p.parcelle=SUBSTRING(geo_parcelle.geo_parcelle,1,4)||'[DEPDIR]'||SUBSTRING(geo_parcelle.geo_parcelle,5,3)||replace(SUBSTRING(geo_parcelle.geo_parcelle,8,5),'0','-')||SUBSTRING(geo_parcelle.geo_parcelle,13,4) AND geo_parcelle.annee='[ANNEE]';

-- ajout de l'identifiant de geo_parcelle dans la table parcelle
UPDATE [PREFIXE]parcelle SET geo_parcelle=g.geo_parcelle FROM [PREFIXE]geo_parcelle g WHERE g.parcelle=parcelle.parcelle AND g.annee='[ANNEE]';

-- geo_subdfisc;
INSERT INTO [PREFIXE]geo_subdfisc (annee, object_rid, tex, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid,  CASE WHEN tex IS NULL THEN '' ELSE tex END, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(geom), '[LOT]'
FROM [PREFIXE]subdfisc_id;

-- geo_subdfisc_parcelle;
INSERT INTO [PREFIXE]geo_subdfisc_parcelle (annee, geo_subdfisc, geo_parcelle)
SELECT s.annee, s.geo_subdfisc, p.geo_parcelle
FROM [PREFIXE]geo_subdfisc s, [PREFIXE]geo_parcelle p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND r.nom='Rel_SUBDFISC_PARCELLE' AND s.object_rid=r.de AND p.object_rid=r.vers;

-- geo_voiep;
INSERT INTO [PREFIXE]geo_voiep
( annee, object_rid, tex, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid, tex, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), geom, '[LOT]'
FROM [PREFIXE]voiep_id;

-- geo_numvoie;
INSERT INTO [PREFIXE]geo_numvoie
( annee, object_rid, tex, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid, tex, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), geom, '[LOT]'
FROM [PREFIXE]numvoie_id;

-- geo_numvoie_parcelle;
INSERT INTO [PREFIXE]geo_numvoie_parcelle (annee, geo_numvoie, geo_parcelle)
SELECT s.annee, s.geo_numvoie, p.geo_parcelle
FROM [PREFIXE]geo_numvoie s, [PREFIXE]geo_parcelle p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND r.nom='Rel_NUMVOIE_PARCELLE' AND s.object_rid=r.de AND p.object_rid=r.vers;

-- geo_lieudit;
INSERT INTO [PREFIXE]geo_lieudit
( annee, object_rid, tex, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid, tex, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(geom), '[LOT]'
FROM [PREFIXE]lieudit_id;

-- geo_batiment;
INSERT INTO [PREFIXE]geo_batiment( geo_batiment, annee, object_rid, geo_dur, tex, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]'||'[LOT]'||replace(to_char(ogc_fid,'0000000'),' ',''), '[ANNEE]', object_rid, dur, tex, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(geom), '[LOT]'
FROM [PREFIXE]batiment_id;

-- geo_batiment_parcelle;
INSERT INTO [PREFIXE]geo_batiment_parcelle (annee, geo_batiment, geo_parcelle)
SELECT s.annee, s.geo_batiment, p.geo_parcelle
FROM [PREFIXE]geo_batiment s, [PREFIXE]geo_parcelle p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND r.nom='Rel_BATIMENT_PARCELLE' AND s.object_rid=r.de AND p.object_rid=r.vers;

-- geo_zoncommuni;
INSERT INTO [PREFIXE]geo_zoncommuni( annee, object_rid, tex, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid, COALESCE(tex,'')||COALESCE(' '||tex2,'')||COALESCE(' '||tex3,'')||COALESCE(' '||tex4,'')||COALESCE(' '||tex5,'')||COALESCE(' '||tex6,'')||COALESCE(' '||tex7,'')||COALESCE(' '||tex8,'')||COALESCE(' '||tex9,'')||COALESCE(' '||tex10,'') as tex, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(geom), '[LOT]'
FROM [PREFIXE]zoncommuni_id;

-- geo_tronfluv;
INSERT INTO [PREFIXE]geo_tronfluv( annee, object_rid, tex, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid, COALESCE(tex,'')||COALESCE(' '||tex2,'')||COALESCE(' '||tex3,'')||COALESCE(' '||tex4,'')||COALESCE(' '||tex5,'')||COALESCE(' '||tex6,'')||COALESCE(' '||tex7,'')||COALESCE(' '||tex8,'')||COALESCE(' '||tex9,'')||COALESCE(' '||tex10,'') as tex, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(geom), '[LOT]'
FROM [PREFIXE]tronfluv_id;

-- geo_sym;
INSERT INTO [PREFIXE]geo_sym SELECT DISTINCT sym, 'Inconnu '||sym  FROM [PREFIXE]ptcanv_id WHERE sym NOT IN (SELECT geo_sym FROM [PREFIXE]geo_sym);
INSERT INTO [PREFIXE]geo_ptcanv( annee, object_rid, idu, geo_can, geo_ppln, geo_palt, geo_map, geo_sym, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid, idu, can, ppln, palt, map, sym, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), geom, '[LOT]'
FROM [PREFIXE]ptcanv_id;

-- geo_borne;
INSERT INTO [PREFIXE]geo_borne( annee, object_rid, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid,  to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), geom, '[LOT]'
FROM [PREFIXE]borne_id;

-- geo_borne_parcelle;
INSERT INTO [PREFIXE]geo_borne_parcelle (annee, geo_borne, geo_parcelle)
SELECT s.annee, s.geo_borne, p.geo_parcelle
FROM [PREFIXE]geo_borne s, [PREFIXE]geo_parcelle p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND r.nom='Rel_BORNE_PARCELLE' AND s.object_rid=r.de AND p.object_rid=r.vers;

-- geo_croix;
INSERT INTO [PREFIXE]geo_croix( annee, object_rid, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid,  to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), geom, '[LOT]'
FROM [PREFIXE]croix_id;

-- geo_croix_parcelle;
INSERT INTO [PREFIXE]geo_croix_parcelle (annee, geo_croix, geo_parcelle)
SELECT s.annee, s.geo_croix, p.geo_parcelle
FROM [PREFIXE]geo_croix s, [PREFIXE]geo_parcelle p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND r.nom='Rel_CROIX_PARCELLE' AND s.object_rid=r.de AND p.object_rid=r.vers;

-- geo_symblim;
INSERT INTO [PREFIXE]geo_symblim( annee, object_rid, ori, geo_sym, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid,  ori, sym, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), geom, '[LOT]'
FROM [PREFIXE]symblim_id;
UPDATE [PREFIXE]geo_symblim set ori=360-ori WHERE annee='[ANNEE]';

-- geo_symblim_parcelle;
INSERT INTO [PREFIXE]geo_symblim_parcelle (annee, geo_symblim, geo_parcelle)
SELECT s.annee, s.geo_symblim, p.geo_parcelle
FROM [PREFIXE]geo_symblim s, [PREFIXE]geo_parcelle p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND r.nom='Rel_SYMBLIM_PARCELLE' AND s.object_rid=r.de AND p.object_rid=r.vers;

-- geo_tpoint;
INSERT INTO [PREFIXE]geo_tpoint( annee, object_rid, ori,tex, geo_sym, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid,  ori, tex, sym, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), geom, '[LOT]'
FROM [PREFIXE]tpoint_id;
UPDATE [PREFIXE]geo_tpoint SET ori=360-ori WHERE annee='[ANNEE]' AND ori IS NOT NULL;

-- geo_tpoint_commune;
INSERT INTO [PREFIXE]geo_tpoint_commune (annee, geo_tpoint, geo_commune)
SELECT s.annee, s.geo_tpoint, p.geo_commune
FROM [PREFIXE]geo_tpoint s, [PREFIXE]geo_commune p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND r.nom='Rel_DETOPO_COMMUNE' AND p.object_rid=r.de AND s.object_rid=r.vers;

-- geo_tline;
INSERT INTO [PREFIXE]geo_tline( annee, object_rid, tex, geo_sym, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid,  tex, sym, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(geom), '[LOT]'
FROM [PREFIXE]tline_id;

-- geo_tline_commune;
INSERT INTO [PREFIXE]geo_tline_commune (annee, geo_tline, geo_commune)
SELECT s.annee, s.geo_tline, p.geo_commune
FROM [PREFIXE]geo_tline s, [PREFIXE]geo_commune p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND r.nom='Rel_DETOPO_COMMUNE' AND p.object_rid=r.de AND s.object_rid=r.vers;

-- geo_tsurf;
INSERT INTO [PREFIXE]geo_tsurf( annee, object_rid, tex, geo_sym, creat_date, update_dat, geom, lot)
SELECT '[ANNEE]', object_rid,  tex, sym, to_date(to_char(creat_date,'00000000'), 'YYYYMMDD'), to_date(to_char(update_date,'00000000'), 'YYYYMMDD'), ST_Multi(geom), '[LOT]'
FROM [PREFIXE]tsurf_id;

-- geo_tsurf_commune;
INSERT INTO [PREFIXE]geo_tsurf_commune (annee, geo_tsurf, geo_commune)
SELECT s.annee, s.geo_tsurf, p.geo_commune
FROM [PREFIXE]geo_tsurf s, [PREFIXE]geo_commune p, [PREFIXE]edigeo_rel r
WHERE s.annee='[ANNEE]' AND s.annee=p.annee AND r.nom='Rel_DETOPO_COMMUNE' AND p.object_rid=r.de AND s.object_rid=r.vers;

-- suppression des index
DROP INDEX [PREFIXE]idx_edigeorel_vers;
DROP INDEX [PREFIXE]idx_edigeorel_de;


-- ANALYSES;
ANALYSE [PREFIXE]geo_commune;
ANALYSE [PREFIXE]geo_section;
ANALYSE [PREFIXE]geo_subdsect;
ANALYSE [PREFIXE]geo_parcelle;
ANALYSE [PREFIXE]geo_subdfisc;
ANALYSE [PREFIXE]geo_subdfisc_parcelle;
ANALYSE [PREFIXE]geo_voiep;
ANALYSE [PREFIXE]geo_numvoie;
ANALYSE [PREFIXE]geo_numvoie_parcelle;
ANALYSE [PREFIXE]geo_lieudit;
ANALYSE [PREFIXE]geo_batiment;
ANALYSE [PREFIXE]geo_batiment_parcelle;
ANALYSE [PREFIXE]geo_zoncommuni;
ANALYSE [PREFIXE]geo_tronfluv;
ANALYSE [PREFIXE]geo_sym;
ANALYSE [PREFIXE]geo_ptcanv;
ANALYSE [PREFIXE]geo_borne;
ANALYSE [PREFIXE]geo_borne_parcelle;
ANALYSE [PREFIXE]geo_croix;
ANALYSE [PREFIXE]geo_croix_parcelle;
ANALYSE [PREFIXE]geo_symblim;
ANALYSE [PREFIXE]geo_symblim_parcelle;
ANALYSE [PREFIXE]geo_tpoint;
ANALYSE [PREFIXE]geo_tpoint_commune;
ANALYSE [PREFIXE]geo_tline;
ANALYSE [PREFIXE]geo_tline_commune;
ANALYSE [PREFIXE]geo_tsurf;
ANALYSE [PREFIXE]geo_tsurf_commune;
COMMIT;
-- FORMATAGE DONNEES : FIN;

