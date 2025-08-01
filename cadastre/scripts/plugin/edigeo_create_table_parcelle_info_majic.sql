BEGIN;

-- Ajout des champs specifiques a la version MAJIC de la table parcelle_info

ALTER TABLE ${PREFIXE}parcelle_info ADD COLUMN IF NOT EXISTS parcelle_batie text;
ALTER TABLE ${PREFIXE}parcelle_info ADD COLUMN IF NOT EXISTS adresse text;
ALTER TABLE ${PREFIXE}parcelle_info ADD COLUMN IF NOT EXISTS urbain text;
ALTER TABLE ${PREFIXE}parcelle_info ADD COLUMN IF NOT EXISTS code text;
ALTER TABLE ${PREFIXE}parcelle_info ADD COLUMN IF NOT EXISTS comptecommunal text;
ALTER TABLE ${PREFIXE}parcelle_info ADD COLUMN IF NOT EXISTS voie text;
ALTER TABLE ${PREFIXE}parcelle_info ADD COLUMN IF NOT EXISTS proprietaire text;
ALTER TABLE ${PREFIXE}parcelle_info ADD COLUMN IF NOT EXISTS proprietaire_info text;

CREATE INDEX IF NOT EXISTS parcelle_info_voie_substr_idx ON ${PREFIXE}parcelle_info ((substr(voie, 1, 6) || substr(voie, 12, 4)));
CREATE INDEX IF NOT EXISTS parcelle_info_comptecommunal_idx ON ${PREFIXE}parcelle_info (comptecommunal);

-- Insertion pour le lot ${LOT}

INSERT INTO ${PREFIXE}parcelle_info
(
    ogc_fid, geo_parcelle, idu, tex, geo_section, nomcommune, codecommune,
    surface_geo, contenance, lot, geom, parcelle_batie, adresse, urbain, code,
    comptecommunal, voie, proprietaire, proprietaire_info
)
SELECT gp.ogc_fid AS ogc_fid, gp.geo_parcelle, gp.idu AS idu, gp.tex AS tex, gp.geo_section AS geo_section,
c.libcom AS nomcommune, p.ccocom AS codecommune, Cast(ST_Area(gp.geom) AS bigint) AS surface_geo, p.dcntpa AS contenance,
gp.lot AS lot,
gp.geom AS geom,
CASE
    WHEN coalesce(p.gparbat, '0') = '1' THEN 'Oui'
    ELSE 'Non'
END AS parcelle_batie,
CASE
        WHEN v.libvoi IS NOT NULL THEN trim(ltrim(p.dnvoiri, '0') || ' ' || trim(Coalesce(v.natvoi, '')) || v.libvoi)
        ELSE ltrim(p.cconvo, '0') || p.dvoilib
END AS adresse,
CASE
        WHEN p.gurbpa = 'U' THEN 'Oui'
        ELSE 'Non'
END  AS urbain,
ccosec || dnupla AS code,
p.comptecommunal AS comptecommunal, p.voie AS voie,

string_agg(
    trim(
        pr.dnuper || ' - ' ||
        trim(coalesce(pr.dqualp, '')) || ' ' ||
        trim(coalesce(pr.ddenom, '')) || ' - ' ||
        ccodro_lib
    ),
    '|'
) AS proprietaire,

string_agg(
    trim(
        pr.dnuper || ' - ' ||
        ltrim(trim(coalesce(pr.dlign4, '')), '0') ||
        trim(coalesce(pr.dlign5, '')) || ' ' ||
        trim(coalesce(pr.dlign6, '')) ||
        trim(
            CASE
                WHEN pr.jdatnss IS NOT NULL
                THEN ' - Né(e) le ' || pr.jdatnss || ' à ' || coalesce(pr.dldnss, '')
                ELSE ''
            END
        )
    ),
    '|'
) AS proprietaire_info

FROM ${PREFIXE}geo_parcelle gp
LEFT OUTER JOIN ${PREFIXE}parcelle p ON gp.geo_parcelle = p.parcelle
LEFT OUTER JOIN ${PREFIXE}proprietaire pr ON p.comptecommunal = pr.comptecommunal
LEFT OUTER JOIN ${PREFIXE}ccodro ON ccodro.ccodro = pr.ccodro
LEFT OUTER JOIN ${PREFIXE}commune c ON p.ccocom = c.ccocom AND c.ccodep = p.ccodep
LEFT OUTER JOIN ${PREFIXE}voie v ON SUBSTR(p.voie, 1, 6) || SUBSTR(p.voie, 12, 4) = SUBSTR(v.voie, 1, 6) || SUBSTR(v.voie, 12, 4)
WHERE gp.lot = '${LOT}'
GROUP BY gp.geo_parcelle, gp.ogc_fid, gp.idu, gp.tex, gp.geo_section, gp.lot,
c.libcom, p.ccocom, gp.geom, p.dcntpa, v.libvoi, p.dnvoiri, v.natvoi,
p.comptecommunal, p.cconvo, p.voie, p.dvoilib, p.gurbpa, p.gparbat,
ccosec, dnupla
;



COMMENT ON COLUMN parcelle_info.parcelle_batie IS 'Indique si la parcelle est bâtie ou non (issu du champ parcelle.gparbat)';
COMMENT ON COLUMN parcelle_info.adresse IS 'Adresse de la parcelle';
COMMENT ON COLUMN parcelle_info.urbain IS 'Déclare si la parcelle est urbaine ou non';
COMMENT ON COLUMN parcelle_info.code IS 'Code de la parcelle (6 caractères, ex: AB0001)';
COMMENT ON COLUMN parcelle_info.comptecommunal IS 'Compte communal du propriétaire';
COMMENT ON COLUMN parcelle_info.voie IS 'Code de la voie (lien avec voie)';
COMMENT ON COLUMN parcelle_info.proprietaire IS 'Information sur les propriétaires: code DNUPER, nom, et type. Les informations sont séparées par | entre propriétaires.';
COMMENT ON COLUMN parcelle_info.proprietaire_info IS 'Informations détaillées sur les propriétaires bis: code DNUPER, adresse, date et lieu de naissance. Les informations sont séparées par | entre propriétaires.';

COMMIT;
