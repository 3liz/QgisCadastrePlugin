-- Creation de la table pour stocker les unites foncieres
CREATE TABLE geo_unite_fonciere
(
  id serial NOT NULL,
  comptecommunal character varying,
  annee character varying(4) NOT NULL,
  lot character varying
);
SELECT AddGeometryColumn ( current_schema::text, 'geo_unite_fonciere', 'geom', 2154 , 'MULTIPOLYGON', 2 );


COMMENT ON TABLE geo_unite_fonciere IS 'Regroupe les unités foncières, c est a dire la fusion de parcelles adjacentes d un même propriétaire';
COMMENT ON COLUMN geo_unite_fonciere.id IS 'Identifiant des unités foncières';
COMMENT ON COLUMN geo_unite_fonciere.comptecommunal IS 'Compte communal des parcelles composant l unité foncière';
COMMENT ON COLUMN geo_unite_fonciere.annee IS 'Année';
