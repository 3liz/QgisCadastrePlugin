DROP INDEX IF EXISTS idxan_local00;
DROP INDEX IF EXISTS idxan_local10;
DROP INDEX IF EXISTS idx_local10_invar;
DROP INDEX IF EXISTS idx_local00_invar;
DROP INDEX IF EXISTS idxan_proprietaire;
DROP INDEX IF EXISTS idxan_voie;
DROP INDEX IF EXISTS idxan_suf;
DROP INDEX IF EXISTS idxan_sufexoneration;
DROP INDEX IF EXISTS idxan_suftaxation;
DROP INDEX IF EXISTS idxan_pev;
DROP INDEX IF EXISTS idxan_pevexoneration_imposable;
DROP INDEX IF EXISTS idxan_pevexoneration_imposee;
DROP INDEX IF EXISTS idxan_pevtaxation;
DROP INDEX IF EXISTS idxan_pevprincipale;
DROP INDEX IF EXISTS idxan_pevprofessionnelle;
DROP INDEX IF EXISTS idxan_pevdependances;
DROP INDEX IF EXISTS idxan_pdl;
DROP INDEX IF EXISTS idxan_parcellecomposante;
DROP INDEX IF EXISTS idx_lots_tmp1;
DROP INDEX IF EXISTS idxan_lotslocaux;
DROP INDEX IF EXISTS idxan_commune;
DROP INDEX IF EXISTS idxan_majic_commune;
DROP INDEX IF EXISTS proprietaire_dnupro_idx;
DROP INDEX IF EXISTS proprietaire_ddenom_idx;
DROP INDEX IF EXISTS parcelle_dnupro_idx;
DROP INDEX IF EXISTS suf_parcelle_idx;
DROP INDEX IF EXISTS sufexoneration_suf_idx;

DROP INDEX IF EXISTS idx_proprietaire_ccocom;
DROP INDEX IF EXISTS idx_commune_ccocom;
DROP INDEX IF EXISTS idx_proprietaire_ccodro;
DROP INDEX IF EXISTS idx_proprietaire_proprietaire;
DROP INDEX IF EXISTS idx_proprietaire_comptecommunal;
DROP INDEX IF EXISTS idx_local00_parcelle;
DROP INDEX IF EXISTS idx_local00_voie;
DROP INDEX IF EXISTS idx_local10_local00;
DROP INDEX IF EXISTS idx_local10_comptecommunal;
DROP INDEX IF EXISTS idx_pevexoneration_imposable_pev;
DROP INDEX IF EXISTS idx_pevexoneration_imposee_pev;
DROP INDEX IF EXISTS idx_pevtaxation_pev;
DROP INDEX IF EXISTS idx_parcelle_voie;
DROP INDEX IF EXISTS idx_parcelle_comptecommunal;

DROP INDEX IF EXISTS parcelle_info_geom_idx;
DROP INDEX IF EXISTS parcelle_info_geo_section_idx;
DROP INDEX IF EXISTS parcelle_info_codecommune_idx;
DROP INDEX IF EXISTS parcelle_info_geo_parcelle_idx;
DROP INDEX IF EXISTS parcelle_info_voie_substr_idx;
DROP INDEX IF EXISTS parcelle_info_compte_communal_idx;
