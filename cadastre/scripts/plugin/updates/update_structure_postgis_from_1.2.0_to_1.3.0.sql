-- table prop
ALTER TABLE prop ALTER COLUMN tmp SET DATA TYPE character varying;

-- table proprietaire
ALTER TABLE proprietaire ADD COLUMN dnomus character varying;
ALTER TABLE proprietaire ADD COLUMN dprnus character varying;
COMMENT ON COLUMN proprietaire.dnomus IS 'Nom d''usage (Depuis 2015)';
COMMENT ON COLUMN proprietaire.dprnus IS 'Prénom d''usage (Depuis 2015)';

-- table commune_majic
CREATE TABLE commune_majic(
    commune character varying (10),
    annee character varying (4),
    ccodep character varying (2),
    ccodir character varying (1),
    ccocom character varying (3),
    libcom character varying (50),
    lot character varying
);

COMMENT ON TABLE commune_majic IS 'Commune (MAJIC - introduit depuis le millésime 2015). Cet article contient le code INSEE associé au libellé de la commune.';
COMMENT ON COLUMN commune_majic.ccodep IS 'Code département - Code département INSEE';
COMMENT ON COLUMN commune_majic.ccodir IS 'Code direction - Code direction dge';
COMMENT ON COLUMN commune_majic.ccocom IS 'Code commune - 3 caractères';
COMMENT ON COLUMN commune_majic.libcom IS 'Libellé de la commune';

CREATE INDEX idx_commune_majic_ccocom ON commune_majic (ccocom);

-- Nomenclature
INSERT INTO gnextl VALUES ('AK', 'Exonération de 20 ans pour les logements intermédiaires loués dans les conditions de l’article 279-0 bis A (addition de construction) – art. 1384-0 A du CGI');
INSERT INTO gnextl VALUES ('NK', 'Exonération de 20 ans pour les logements intermédiaires loués dans les conditions de l’article 279-0 bis A (construction nouvelle) – art. 1384-0 A du CGI');
INSERT INTO gnextl VALUES ('RT', 'Abattement de 25 % pour les locaux faisant l’objet d’une convention ou d''un contrat de résidence temporaire – art. 1388 quinquies A du CGI');
INSERT INTO gnextl VALUES ('UM', 'Exonération de 5 ans pour les usines de méthanisation - art. 1387 A du CGI');
 
-- table geo_tronroute
CREATE TABLE geo_tronroute
(
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

-- table gnexts
ALTER TABLE gnexts ALTER COLUMN gnexts_lib SET DATA TYPE character varying);


