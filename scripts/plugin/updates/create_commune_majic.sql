CREATE TABLE IF NOT EXISTS commune_majic (
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
