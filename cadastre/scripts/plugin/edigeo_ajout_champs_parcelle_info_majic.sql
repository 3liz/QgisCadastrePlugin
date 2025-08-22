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

COMMENT ON COLUMN parcelle_info.parcelle_batie IS 'Indique si la parcelle est bâtie ou non (issu du champ parcelle.gparbat)';
COMMENT ON COLUMN parcelle_info.adresse IS 'Adresse de la parcelle';
COMMENT ON COLUMN parcelle_info.urbain IS 'Déclare si la parcelle est urbaine ou non';
COMMENT ON COLUMN parcelle_info.code IS 'Code de la parcelle (6 caractères, ex: AB0001)';
COMMENT ON COLUMN parcelle_info.comptecommunal IS 'Compte communal du propriétaire';
COMMENT ON COLUMN parcelle_info.voie IS 'Code de la voie (lien avec voie)';
COMMENT ON COLUMN parcelle_info.proprietaire IS 'Information sur les propriétaires: code DNUPER, nom, et type. Les informations sont séparées par | entre propriétaires.';
COMMENT ON COLUMN parcelle_info.proprietaire_info IS 'Informations détaillées sur les propriétaires bis: code DNUPER, adresse, date et lieu de naissance. Les informations sont séparées par | entre propriétaires.';
