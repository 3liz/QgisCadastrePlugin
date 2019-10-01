BEGIN;

-- Création de la table parcelle_info
DROP TABLE IF EXISTS [PREFIXE]parcelle_info;

CREATE TABLE [PREFIXE]parcelle_info
(
  ogc_fid integer,
  geo_parcelle text,
  idu text,
  tex text,
  geo_section text,
  nomcommune text,
  codecommune text,
  surface_geo integer,
  lot text
);
SELECT AddGeometryColumn ( current_schema::text, 'parcelle_info', 'geom', 2154 , 'MULTIPOLYGON', 2 );

INSERT INTO [PREFIXE]parcelle_info
SELECT gp.ogc_fid AS ogc_fid, geo_parcelle, gp.idu AS idu, gp.tex AS tex, gp.geo_section AS geo_section,
c.tex2 AS nomcommune, c.idu AS codecommune, Cast(ST_Area(gp.geom) AS integer) AS surface_geo,
gp.lot AS lot,
gp.geom AS geom
FROM [PREFIXE]geo_parcelle gp
INNER JOIN [PREFIXE]geo_commune c
ON c.geo_commune = SUBSTRING(gp.geo_parcelle,1,6)
;

ALTER TABLE [PREFIXE]parcelle_info ADD CONSTRAINT parcelle_info_pk PRIMARY KEY (ogc_fid);
CREATE INDEX parcelle_info_geom_idx ON [PREFIXE]parcelle_info USING gist (geom);
CREATE INDEX parcelle_info_geo_section_idx ON [PREFIXE]parcelle_info (geo_section);
CREATE INDEX parcelle_info_codecommune_idx ON [PREFIXE]parcelle_info (codecommune );
CREATE INDEX parcelle_info_geo_parcelle_idx ON [PREFIXE]parcelle_info (geo_parcelle );

COMMENT ON TABLE [PREFIXE]parcelle_info IS 'Table de parcelles consolidées, proposant les géométries et les informations MAJIC principales, dont les propriétaires';
COMMENT ON COLUMN parcelle_info.ogc_fid IS 'Identifiant unique (base de données)';
COMMENT ON COLUMN parcelle_info.geo_parcelle IS 'Identifiant de la parcelle : année + département + direction + idu';
COMMENT ON COLUMN parcelle_info.idu IS 'Identifiant de la parcelle (unique par département et direction seulement)';
COMMENT ON COLUMN parcelle_info.tex IS 'Etiquette (code à 3 chiffres)';
COMMENT ON COLUMN parcelle_info.geo_section IS 'Code de la section (lien vers table geo_section.geo_section)';
COMMENT ON COLUMN parcelle_info.nomcommune IS 'Nom de la commune';
COMMENT ON COLUMN parcelle_info.codecommune IS 'Code de la commune à 3 chiffres';
COMMENT ON COLUMN parcelle_info.surface_geo IS 'Surface de la parcelle, calculée spatialement';
COMMENT ON COLUMN parcelle_info.lot IS 'Lot utilisé pendant l''import';

COMMIT;
