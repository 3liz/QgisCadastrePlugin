CREATE TABLE IF NOT EXISTS geo_tronroute (
  geo_tronroute serial NOT NULL,
  annee character varying(4) NOT NULL,
  object_rid character varying(80),
  tex character varying,
  creat_date date,
  update_dat date,
  lot character varying
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_tronroute', 'geom', ${SRID} , 'MULTIPOLYGON', 2 );

COMMENT ON TABLE geo_tronroute IS 'Élément surfacique (fermé) utilisé pour tous les tronçons de routes. Un libellé y est associé.';
COMMENT ON COLUMN geo_tronroute.geo_tronroute IS 'Identifiant';
COMMENT ON COLUMN geo_tronroute.annee IS 'Année';
COMMENT ON COLUMN geo_tronroute.object_rid IS 'Numéro d''objet';
COMMENT ON COLUMN geo_tronroute.tex IS 'Nom du cours d''eau';
COMMENT ON COLUMN geo_tronroute.creat_date IS 'Date de création';
COMMENT ON COLUMN geo_tronroute.update_dat IS 'Date de dernière modification';

