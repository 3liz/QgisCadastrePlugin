-- SUPPRESSION DES CONTRAINTES D'INTEGRITEES : DEBUT;

-- suppression clefs primaires;
ALTER TABLE ${PREFIXE}geo_tsurf_commune DROP CONSTRAINT IF EXISTS geo_tsurf_commune_pk;
ALTER TABLE ${PREFIXE}geo_tsurf DROP CONSTRAINT IF EXISTS geo_tsurf_pk;
ALTER TABLE ${PREFIXE}geo_tline_commune DROP CONSTRAINT IF EXISTS geo_tline_commune_pk;
ALTER TABLE ${PREFIXE}geo_tline DROP CONSTRAINT IF EXISTS geo_tline_pk;
ALTER TABLE ${PREFIXE}geo_tpoint_commune DROP CONSTRAINT IF EXISTS geo_tpoint_commune_pk;
ALTER TABLE ${PREFIXE}geo_tpoint DROP CONSTRAINT IF EXISTS geo_tpoint_pk;
ALTER TABLE ${PREFIXE}geo_symblim_parcelle DROP CONSTRAINT IF EXISTS geo_symblim_parcelle_pk;
ALTER TABLE ${PREFIXE}geo_symblim DROP CONSTRAINT IF EXISTS geo_symblim_pk;
ALTER TABLE ${PREFIXE}geo_croix_parcelle DROP CONSTRAINT IF EXISTS geo_croix_parcelle_pk;
ALTER TABLE ${PREFIXE}geo_croix DROP CONSTRAINT IF EXISTS geo_croix_pk;
ALTER TABLE ${PREFIXE}geo_borne_parcelle DROP CONSTRAINT IF EXISTS geo_borne_parcelle_pk;
ALTER TABLE ${PREFIXE}geo_borne DROP CONSTRAINT IF EXISTS geo_borne_pk;
ALTER TABLE ${PREFIXE}geo_ptcanv DROP CONSTRAINT IF EXISTS geo_ptcanv_pk;
ALTER TABLE ${PREFIXE}geo_tronfluv DROP CONSTRAINT IF EXISTS geo_tronfluv_pk;
ALTER TABLE ${PREFIXE}geo_tronroute DROP CONSTRAINT IF EXISTS geo_tronroute_pk;
ALTER TABLE ${PREFIXE}geo_zoncommuni DROP CONSTRAINT IF EXISTS geo_zoncommuni_pk;
ALTER TABLE ${PREFIXE}geo_batiment_parcelle DROP CONSTRAINT IF EXISTS geo_batiment_parcelle_pk;
ALTER TABLE ${PREFIXE}geo_batiment DROP CONSTRAINT IF EXISTS geo_batiment_pk;
ALTER TABLE ${PREFIXE}geo_lieudit DROP CONSTRAINT IF EXISTS geo_lieudit_pk;
ALTER TABLE ${PREFIXE}geo_numvoie_parcelle DROP CONSTRAINT IF EXISTS geo_numvoie_parcelle_pk;
ALTER TABLE ${PREFIXE}geo_numvoie DROP CONSTRAINT IF EXISTS geo_numvoie_pk;
ALTER TABLE ${PREFIXE}geo_voiep DROP CONSTRAINT IF EXISTS geo_voiep_pk;
ALTER TABLE ${PREFIXE}geo_subdfisc_parcelle DROP CONSTRAINT IF EXISTS geo_subdfisc_parcelle_pk;
ALTER TABLE ${PREFIXE}geo_subdfisc DROP CONSTRAINT IF EXISTS geo_subdfisc_pk;
ALTER TABLE ${PREFIXE}geo_parcelle DROP CONSTRAINT IF EXISTS geo_parcelle_pk;
ALTER TABLE ${PREFIXE}geo_subdsect DROP CONSTRAINT IF EXISTS geo_subdsect_pk;
ALTER TABLE ${PREFIXE}geo_section DROP CONSTRAINT IF EXISTS geo_section_pk;
ALTER TABLE ${PREFIXE}geo_commune DROP CONSTRAINT IF EXISTS geo_commune_pk;
ALTER TABLE ${PREFIXE}voie DROP CONSTRAINT IF EXISTS voie_pk;
ALTER TABLE ${PREFIXE}commune DROP CONSTRAINT IF EXISTS commune_pk;
ALTER TABLE ${PREFIXE}commune_majic DROP CONSTRAINT IF EXISTS commune_majic_pk;
ALTER TABLE ${PREFIXE}lotslocaux DROP CONSTRAINT IF EXISTS loclocaux_pk;
ALTER TABLE ${PREFIXE}lots DROP CONSTRAINT IF EXISTS lots_pk;
ALTER TABLE ${PREFIXE}parcellecomposante DROP CONSTRAINT IF EXISTS parcellecomposante_pk;
ALTER TABLE ${PREFIXE}pdl DROP CONSTRAINT IF EXISTS pdl_pk;
ALTER TABLE ${PREFIXE}comptecommunal DROP CONSTRAINT IF EXISTS comptecommunal_pk;
ALTER TABLE ${PREFIXE}proprietaire DROP CONSTRAINT IF EXISTS proprietaire_pk;
ALTER TABLE ${PREFIXE}pevdependances DROP CONSTRAINT IF EXISTS pevdependances_pk;
ALTER TABLE ${PREFIXE}pevlissage DROP CONSTRAINT IF EXISTS pevlissage_pk;
ALTER TABLE ${PREFIXE}pevprofessionnelle DROP CONSTRAINT IF EXISTS pevprofessionnelle_pk;
ALTER TABLE ${PREFIXE}pevprincipale DROP CONSTRAINT IF EXISTS pevprincipale_pk;
ALTER TABLE ${PREFIXE}pevtaxation DROP CONSTRAINT IF EXISTS pevtaxation_pk;
ALTER TABLE ${PREFIXE}pevexoneration DROP CONSTRAINT IF EXISTS pevexoneration_pk;
ALTER TABLE ${PREFIXE}pev DROP CONSTRAINT IF EXISTS pev_pk;
ALTER TABLE ${PREFIXE}local10 DROP CONSTRAINT IF EXISTS local10_pk;
ALTER TABLE ${PREFIXE}local00 DROP CONSTRAINT IF EXISTS local00_pk;
ALTER TABLE ${PREFIXE}suftaxation DROP CONSTRAINT IF EXISTS suftaxation_pk;
ALTER TABLE ${PREFIXE}sufexoneration DROP CONSTRAINT IF EXISTS sufexoneration_pk;
ALTER TABLE ${PREFIXE}suf DROP CONSTRAINT IF EXISTS suf_pk;
ALTER TABLE ${PREFIXE}parcelle DROP CONSTRAINT IF EXISTS parcelle_pk;
ALTER TABLE ${PREFIXE}geo_unite_fonciere DROP CONSTRAINT IF EXISTS geo_unite_fonciere_pk;

--~ -- SUPPRESSION DES CONTRAINTES D'INTEGRITEES : FIN;
