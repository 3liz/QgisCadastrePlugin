-- clé primaire : parcelle
ALTER TABLE parcelle ADD CONSTRAINT parcelle_pk PRIMARY KEY  (parcelle);
-- clé primaire : suf
ALTER TABLE suf ADD CONSTRAINT suf_pk PRIMARY KEY  (suf);
-- clé primaire : sufexoneration
ALTER TABLE sufexoneration ADD CONSTRAINT sufexoneration_pk PRIMARY KEY  (sufexoneration );
-- clé primaire : suftaxation
ALTER TABLE suftaxation ADD CONSTRAINT suftaxation_pk PRIMARY KEY  (suftaxation );
-- clé primaire : local00
ALTER TABLE local00 ADD CONSTRAINT local00_pk PRIMARY KEY  (local00);
-- clé primaire : local10
ALTER TABLE local10 ADD CONSTRAINT local10_pk PRIMARY KEY  (local10);
-- clé primaire : pev
ALTER TABLE pev ADD CONSTRAINT pev_pk PRIMARY KEY  (pev);
-- clé primaire : pevexoneration
ALTER TABLE pevexoneration ADD CONSTRAINT pevexoneration_pk PRIMARY KEY  (pevexoneration);
-- clé primaire : pevtaxation
ALTER TABLE pevtaxation ADD CONSTRAINT pevtaxation_pk PRIMARY KEY  (pevtaxation);
-- clé primaire : pevprincipale
ALTER TABLE pevprincipale ADD CONSTRAINT pevprincipale_pk PRIMARY KEY  (pevprincipale);
-- clé primaire : pevprofessionnelle
ALTER TABLE pevprofessionnelle ADD CONSTRAINT pevprofessionnelle_pk PRIMARY KEY  (pevprofessionnelle);
-- clé primaire : pevdependances
ALTER TABLE pevdependances ADD CONSTRAINT pevdependances_pk PRIMARY KEY  (pevdependances);
-- clé primaire : proprietaire
ALTER TABLE proprietaire ADD CONSTRAINT proprietaire_pk PRIMARY KEY  (proprietaire);
-- clé primaire : comptecommunal
ALTER TABLE comptecommunal ADD CONSTRAINT comptecommunal_pk PRIMARY KEY  (comptecommunal);
-- clé primaire : pdl
ALTER TABLE pdl ADD CONSTRAINT pdl_pk PRIMARY KEY  (pdl);
-- clé primaire : parcellecomposante
ALTER TABLE parcellecomposante ADD CONSTRAINT parcellecomposante_pk PRIMARY KEY  (parcellecomposante);
-- clé primaire : lots
ALTER TABLE lots ADD CONSTRAINT lots_pk PRIMARY KEY  (lots);
-- clé primaire : lotslocaux
ALTER TABLE lotslocaux ADD CONSTRAINT loclocaux_pk PRIMARY KEY  (lotslocaux);
-- clé primaire : commune
ALTER TABLE commune ADD CONSTRAINT commune_pk PRIMARY KEY  (commune);
-- clé primaire : voie
ALTER TABLE voie ADD CONSTRAINT voie_pk PRIMARY KEY  (voie);
-- clé primaire : geo_commune
ALTER TABLE  geo_commune ADD CONSTRAINT geo_commune_pk PRIMARY KEY (geo_commune );
-- clé primaire : geo_section
ALTER TABLE  geo_section ADD CONSTRAINT geo_section_pk PRIMARY KEY (geo_section );
-- clé primaire : geo_subdsect
ALTER TABLE geo_subdsect ADD CONSTRAINT geo_subdsect_pk PRIMARY KEY (geo_subdsect );
-- clé primaire : geo_parcelle
ALTER TABLE geo_parcelle ADD CONSTRAINT geo_parcelle_pk PRIMARY KEY (geo_parcelle );
-- clé primaire : geo_subdfisc
ALTER TABLE geo_subdfisc ADD CONSTRAINT geo_subdfisc_pk PRIMARY KEY (geo_subdfisc );
-- clé primaire : geo_subdfisc_parcelle
ALTER TABLE geo_subdfisc_parcelle ADD CONSTRAINT geo_subdfisc_parcelle_pk PRIMARY KEY (geo_subdfisc_parcelle );
-- clé primaire : geo_voiep
ALTER TABLE geo_voiep ADD CONSTRAINT geo_voiep_pk PRIMARY KEY (geo_voiep );
-- clé primaire : geo_numvoie
ALTER TABLE geo_numvoie ADD CONSTRAINT geo_numvoie_pk PRIMARY KEY (geo_numvoie );
-- clé primaire : geo_numvoie_parcelle
ALTER TABLE geo_numvoie_parcelle ADD CONSTRAINT geo_numvoie_parcelle_pk PRIMARY KEY (geo_numvoie_parcelle );
-- clé primaire : geo_lieudit
ALTER TABLE geo_lieudit ADD CONSTRAINT geo_lieudit_pk PRIMARY KEY (geo_lieudit );
-- clé primaire : geo_batiment
ALTER TABLE geo_batiment ADD CONSTRAINT geo_batiment_pk PRIMARY KEY (geo_batiment );
-- clé primaire : geo_batiment_parcelle
ALTER TABLE geo_batiment_parcelle ADD CONSTRAINT geo_batiment_parcelle_pk PRIMARY KEY (geo_batiment_parcelle );
-- clé primaire : geo_zoncommuni
ALTER TABLE geo_zoncommuni ADD CONSTRAINT geo_zoncommuni_pk PRIMARY KEY (geo_zoncommuni );
-- clé primaire : geo_tronfluv
ALTER TABLE geo_tronfluv ADD CONSTRAINT geo_tronfluv_pk PRIMARY KEY (geo_tronfluv );
-- clé primaire : geo_tronroute
ALTER TABLE geo_tronroute ADD CONSTRAINT geo_tronroute_pk PRIMARY KEY (geo_tronroute );
-- clé primaire : geo_ptcanv
ALTER TABLE geo_ptcanv ADD CONSTRAINT geo_ptcanv_pk PRIMARY KEY (geo_ptcanv );
-- clé primaire : geo_borne
ALTER TABLE geo_borne ADD CONSTRAINT geo_borne_pk PRIMARY KEY (geo_borne );
-- clé primaire : geo_borne_parcelle
ALTER TABLE geo_borne_parcelle ADD CONSTRAINT geo_borne_parcelle_pk PRIMARY KEY (geo_borne_parcelle );
-- clé primaire : geo_croix
ALTER TABLE geo_croix ADD CONSTRAINT geo_croix_pk PRIMARY KEY (geo_croix );
-- clé primaire : geo_croix_parcelle
ALTER TABLE geo_croix_parcelle ADD CONSTRAINT geo_croix_parcelle_pk PRIMARY KEY (geo_croix_parcelle );
-- clé primaire : geo_symblim
ALTER TABLE geo_symblim ADD CONSTRAINT geo_symblim_pk PRIMARY KEY (geo_symblim );
-- clé primaire : geo_symblim_parcelle
ALTER TABLE geo_symblim_parcelle ADD CONSTRAINT geo_symblim_parcelle_pk PRIMARY KEY (geo_symblim_parcelle );
-- clé primaire : geo_tpoint
ALTER TABLE geo_tpoint ADD CONSTRAINT geo_tpoint_pk PRIMARY KEY (geo_tpoint );
-- clé primaire : geo_tline
ALTER TABLE geo_tline ADD CONSTRAINT geo_tline_pk PRIMARY KEY (geo_tline );
-- clé primaire : geo_tpoint_commune
ALTER TABLE geo_tpoint_commune ADD CONSTRAINT geo_tpoint_commune_pk PRIMARY KEY (geo_tpoint_commune );
-- clé primaire : geo_tline_commune
ALTER TABLE geo_tline_commune ADD CONSTRAINT geo_tline_commune_pk PRIMARY KEY (geo_tline_commune );
-- clé primaire : geo_tsurf
ALTER TABLE geo_tsurf ADD CONSTRAINT geo_tsurf_pk PRIMARY KEY (geo_tsurf );
-- clé primaire : geo_tsurf_commune
ALTER TABLE geo_tsurf_commune ADD CONSTRAINT geo_tsurf_commune_pk PRIMARY KEY (geo_tsurf_commune );
-- clé étrangère : parcelle -> comptecommunal
ALTER TABLE parcelle ADD CONSTRAINT parcelle_comptecommunal_fk FOREIGN KEY (comptecommunal) REFERENCES comptecommunal (comptecommunal) ON DELETE CASCADE;
-- clé étrangère : parcelle -> pdl
ALTER TABLE parcelle ADD CONSTRAINT parcelle_pdl_fk FOREIGN KEY (pdl) REFERENCES pdl (pdl) ON DELETE CASCADE;
-- clé étrangère : parcelle -> voie
ALTER TABLE parcelle ADD CONSTRAINT parcelle_voie_fk FOREIGN KEY ( voie) REFERENCES voie ( voie) ON DELETE CASCADE;
-- clé étrangère : parcelle -> gpdl
ALTER TABLE parcelle ADD CONSTRAINT parcelle_gpdl_fk FOREIGN KEY (gpdl) REFERENCES gpdl (gpdl) ON DELETE CASCADE;
-- clé étrangère : parcelle -> geo_parcelle
ALTER TABLE parcelle ADD CONSTRAINT parcelle_geo_parcelle_fk FOREIGN KEY (geo_parcelle) REFERENCES geo_parcelle (geo_parcelle) ON DELETE SET NULL;
-- clé étrangère : suf -> parcelle
ALTER TABLE suf ADD CONSTRAINT suf_parcelle_fk FOREIGN KEY (parcelle) REFERENCES parcelle (parcelle) ON DELETE CASCADE;
-- clé étrangère : suf -> comptecommunal
ALTER TABLE suf ADD CONSTRAINT suf_comptecommunal_fk FOREIGN KEY (comptecommunal) REFERENCES comptecommunal (comptecommunal) ON DELETE CASCADE;
-- clé étrangère : suf -> pdl
ALTER TABLE suf ADD CONSTRAINT suf_pdl_fk FOREIGN KEY (pdl) REFERENCES pdl (pdl) ON DELETE CASCADE;
-- clé étrangère : suf -> gnexps
ALTER TABLE suf ADD CONSTRAINT suf_gnexps_fk FOREIGN KEY (gnexps) REFERENCES gnexps (gnexps) ON DELETE CASCADE;
-- clé étrangère : suf -> cgrnum
ALTER TABLE suf ADD CONSTRAINT suf_cgrnum_fk FOREIGN KEY (cgrnum) REFERENCES cgrnum (cgrnum) ON DELETE CASCADE;
-- clé étrangère : suf -> dsgrpf
ALTER TABLE suf ADD CONSTRAINT suf_dsgrpf_fk FOREIGN KEY (dsgrpf) REFERENCES dsgrpf (dsgrpf) ON DELETE CASCADE;
-- clé étrangère : suf -> cnatsp
ALTER TABLE suf ADD CONSTRAINT suf_cnatsp_fk FOREIGN KEY (cnatsp) REFERENCES cnatsp (cnatsp) ON DELETE CASCADE;
-- clé étrangère : sufexoneration -> suf
ALTER TABLE sufexoneration ADD CONSTRAINT sufexoneration_suf_fk FOREIGN KEY (suf) REFERENCES suf (suf) ON DELETE CASCADE;
-- clé étrangère : sufexoneration -> ccolloc
ALTER TABLE sufexoneration ADD CONSTRAINT sufexoneration_ccolloc_fk FOREIGN KEY (ccolloc) REFERENCES ccolloc (ccolloc) ON DELETE CASCADE;
-- clé étrangère : sufexoneration -> gnexts
ALTER TABLE sufexoneration ADD CONSTRAINT sufexoneration_gnexts_fk FOREIGN KEY (gnexts) REFERENCES gnexts (gnexts) ON DELETE CASCADE;
-- clé étrangère : suftaxation -> suf
ALTER TABLE suftaxation ADD CONSTRAINT suftaxation_suf_fk FOREIGN KEY (suf ) REFERENCES suf (suf) ON DELETE CASCADE;
-- clé étrangère : local00 -> parcelle
ALTER TABLE local00 ADD CONSTRAINT local00_parcelle_fk FOREIGN KEY (parcelle) REFERENCES parcelle (parcelle) ON DELETE CASCADE;
-- clé étrangère : local00 -> voie
ALTER TABLE local00 ADD CONSTRAINT local00_voie_fk FOREIGN KEY ( voie) REFERENCES voie ( voie) ON DELETE CASCADE;
-- clé étrangère : local10 -> local00
ALTER TABLE local10 ADD CONSTRAINT local10_local00_fk FOREIGN KEY (local00) REFERENCES local00 (local00) ON DELETE CASCADE;
-- clé étrangère : local10 -> parcelle
ALTER TABLE local10 ADD CONSTRAINT local10_parcelle_fk FOREIGN KEY (parcelle) REFERENCES parcelle (parcelle) ON DELETE CASCADE;
-- clé étrangère : local10 -> comptecommunal
ALTER TABLE local10 ADD CONSTRAINT local10_comptecommunal_fk FOREIGN KEY (comptecommunal) REFERENCES comptecommunal (comptecommunal) ON DELETE CASCADE;
-- clé étrangère : local10 -> voie
ALTER TABLE local10 ADD CONSTRAINT local10_voie_fk FOREIGN KEY (voie) REFERENCES voie (voie) ON DELETE CASCADE;
-- clé étrangère : local10 -> ccoeva
ALTER TABLE local10 ADD CONSTRAINT local10_ccoeva_fk FOREIGN KEY (ccoeva) REFERENCES ccoeva (ccoeva) ON DELETE CASCADE;
-- clé étrangère : local10 -> dteloc
ALTER TABLE local10 ADD CONSTRAINT local10_dteloc_fk FOREIGN KEY (dteloc) REFERENCES dteloc (dteloc) ON DELETE CASCADE;
-- clé étrangère : local10 -> ccoplc
ALTER TABLE local10 ADD CONSTRAINT local10_ccoplc_fk FOREIGN KEY (ccoplc) REFERENCES ccoplc (ccoplc) ON DELETE CASCADE;
-- clé étrangère : local10 -> cconlc
ALTER TABLE local10 ADD CONSTRAINT local10_cconlc_fk FOREIGN KEY (cconlc) REFERENCES cconlc (cconlc) ON DELETE CASCADE;
-- clé étrangère : local10 -> top48a
ALTER TABLE local10 ADD CONSTRAINT local10_top48a_fk FOREIGN KEY (top48a) REFERENCES top48a (top48a) ON DELETE CASCADE;
-- clé étrangère : local10 -> dnatlc
ALTER TABLE local10 ADD CONSTRAINT local10_dnatlc_fk FOREIGN KEY (dnatlc) REFERENCES dnatlc (dnatlc) ON DELETE CASCADE;
-- clé étrangère : local10 -> hlmsem
ALTER TABLE local10 ADD CONSTRAINT local10_hlmsem_fk FOREIGN KEY (hlmsem) REFERENCES hlmsem (hlmsem) ON DELETE CASCADE;
-- clé étrangère : pev -> local10
ALTER TABLE pev ADD CONSTRAINT pev_local10_fk FOREIGN KEY (local10) REFERENCES local10 (local10) ON DELETE CASCADE;
-- clé étrangère : pev -> ccoaff
ALTER TABLE pev ADD CONSTRAINT pev_ccoaff_fk FOREIGN KEY (ccoaff) REFERENCES ccoaff (ccoaff) ON DELETE CASCADE;
-- clé étrangère : pev -> gnexpl
ALTER TABLE pev ADD CONSTRAINT pev_gnexpl_fk FOREIGN KEY (gnexpl) REFERENCES gnexpl (gnexpl) ON DELETE CASCADE;
-- clé étrangère : pevexoneration -> pev
ALTER TABLE pevexoneration ADD CONSTRAINT pevexoneration_pev_fk FOREIGN KEY (pev) REFERENCES pev (pev) ON DELETE CASCADE;
-- clé étrangère : pevexoneration -> ccolloc
ALTER TABLE pevexoneration ADD CONSTRAINT pevexoneration_ccolloc_fk FOREIGN KEY (ccolloc) REFERENCES ccolloc (ccolloc) ON DELETE CASCADE;
-- clé étrangère : pevexoneration -> gnextl
ALTER TABLE pevexoneration ADD CONSTRAINT pevexoneration_gnextl_fk FOREIGN KEY (gnextl) REFERENCES gnextl (gnextl) ON DELETE CASCADE;
-- clé étrangère : pevtaxation -> pev
ALTER TABLE pevtaxation ADD CONSTRAINT pevtaxation_pev_fk FOREIGN KEY (pev) REFERENCES pev (pev) ON DELETE CASCADE;
-- clé étrangère : pevprincipale -> pev
ALTER TABLE pevprincipale ADD CONSTRAINT pevprincipale_pev_fk FOREIGN KEY (pev) REFERENCES pev (pev) ON DELETE CASCADE;
-- clé étrangère : pevprincipale -> cconad 1 à 4
ALTER TABLE pevprincipale ADD CONSTRAINT pevprincipale_dep1_cconad_fk FOREIGN KEY (dep1_cconad) REFERENCES cconad (cconad) ON DELETE CASCADE;
ALTER TABLE pevprincipale ADD CONSTRAINT pevprincipale_dep2_cconad_fk FOREIGN KEY (dep2_cconad) REFERENCES cconad (cconad) ON DELETE CASCADE;
ALTER TABLE pevprincipale ADD CONSTRAINT pevprincipale_dep3_cconad_fk FOREIGN KEY (dep3_cconad) REFERENCES cconad (cconad) ON DELETE CASCADE;
ALTER TABLE pevprincipale ADD CONSTRAINT pevprincipale_dep4_cconad_fk FOREIGN KEY (dep4_cconad) REFERENCES cconad (cconad) ON DELETE CASCADE;
-- clé étrangère : pevprofessionnelle -> pev
ALTER TABLE pevprofessionnelle ADD CONSTRAINT pevprofessionnelle_pev_fk FOREIGN KEY (pev) REFERENCES pev (pev) ON DELETE CASCADE;
-- clé étrangère : pevdependances -> pev
ALTER TABLE pevdependances ADD CONSTRAINT pevdependances_pev_fk FOREIGN KEY (pev) REFERENCES pev (pev) ON DELETE CASCADE;
-- clé étrangère : pevdependances -> cconad
ALTER TABLE pevdependances ADD CONSTRAINT pevdependances_cconad_fk FOREIGN KEY (cconad) REFERENCES cconad (cconad) ON DELETE CASCADE;
-- clé étrangère : pdl -> parcelle
ALTER TABLE pdl ADD CONSTRAINT pdl_parcelle_fk FOREIGN KEY (parcelle) REFERENCES parcelle (parcelle) ON DELETE CASCADE;
-- clé étrangère : pdl -> comptecommunal
ALTER TABLE pdl ADD CONSTRAINT pdl_comptecommunal_fk FOREIGN KEY (comptecommunal) REFERENCES comptecommunal (comptecommunal) ON DELETE CASCADE;
-- clé étrangère : pdl -> ctpdl
ALTER TABLE pdl ADD CONSTRAINT pdl_ctpdl_fk FOREIGN KEY (ctpdl) REFERENCES ctpdl (ctpdl) ON DELETE CASCADE;
-- clé étrangère : lots -> pdl
ALTER TABLE lots ADD CONSTRAINT lots_pdl_fk FOREIGN KEY (pdl) REFERENCES pdl (pdl) ON DELETE CASCADE;
-- clé étrangère : lots -> comptecommunal
ALTER TABLE lots ADD CONSTRAINT lots_comptecommunal_fk FOREIGN KEY (comptecommunal ) REFERENCES comptecommunal ( comptecommunal ) ON DELETE CASCADE;
-- clé étrangère : lots -> parcelle
ALTER TABLE lots ADD CONSTRAINT lots_parcelle_fk FOREIGN KEY (parcelle) REFERENCES parcelle (parcelle) ON DELETE CASCADE;
-- clé étrangère : lots -> cconlo
ALTER TABLE lots ADD CONSTRAINT lots_cconlo_fk FOREIGN KEY (cconlo) REFERENCES cconlo (cconlo) ON DELETE CASCADE;
-- clé étrangère : proprietaire -> comptecommunal
ALTER TABLE proprietaire ADD CONSTRAINT proprietaire_comptecommunal_fk FOREIGN KEY (comptecommunal) REFERENCES comptecommunal (comptecommunal) ON DELETE CASCADE;
-- clé étrangère : proprietaire -> ccodro
ALTER TABLE proprietaire ADD CONSTRAINT proprietaire_ccodro_fk FOREIGN KEY (ccodro) REFERENCES ccodro (ccodro) ON DELETE CASCADE;
-- clé étrangère : proprietaire -> ccodem
ALTER TABLE proprietaire ADD CONSTRAINT proprietaire_ccodem_fk FOREIGN KEY (ccodem) REFERENCES ccodem (ccodem) ON DELETE CASCADE;
-- clé étrangère : proprietaire -> gtoper
ALTER TABLE proprietaire ADD CONSTRAINT proprietaire_gtoper_fk FOREIGN KEY (gtoper) REFERENCES gtoper (gtoper) ON DELETE CASCADE;
-- clé étrangère : proprietaire -> ccoqua
ALTER TABLE proprietaire ADD CONSTRAINT proprietaire_ccoqua_fk FOREIGN KEY (ccoqua) REFERENCES ccoqua (ccoqua) ON DELETE CASCADE;
-- clé étrangère : proprietaire -> dnatpr
ALTER TABLE proprietaire ADD CONSTRAINT proprietaire_dnatpr_fk FOREIGN KEY (dnatpr) REFERENCES dnatpr (dnatpr) ON DELETE CASCADE;
-- clé étrangère : proprietaire -> ccogrm
ALTER TABLE proprietaire ADD CONSTRAINT proprietaire_ccogrm_fk FOREIGN KEY (ccogrm) REFERENCES ccogrm (ccogrm) ON DELETE CASCADE;
-- clé étrangère : proprietaire -> gtyp3
ALTER TABLE proprietaire ADD CONSTRAINT proprietaire_gtyp3_fk FOREIGN KEY (gtyp3) REFERENCES gtyp3 (gtyp3) ON DELETE CASCADE;
-- clé étrangère : proprietaire -> gtyp4
ALTER TABLE proprietaire ADD CONSTRAINT proprietaire_gtyp4_fk FOREIGN KEY (gtyp4) REFERENCES gtyp4 (gtyp4) ON DELETE CASCADE;
-- clé étrangère : proprietaire -> gtyp5
ALTER TABLE proprietaire ADD CONSTRAINT proprietaire_gtyp5_fk FOREIGN KEY (gtyp5) REFERENCES gtyp5 (gtyp5) ON DELETE CASCADE;
-- clé étrangère : proprietaire -> gtyp6
ALTER TABLE proprietaire ADD CONSTRAINT proprietaire_gtyp6_fk FOREIGN KEY (gtyp6) REFERENCES gtyp6 (gtyp6) ON DELETE CASCADE;
-- clé étrangère : parcellecomposante -> pdl
ALTER TABLE parcellecomposante ADD CONSTRAINT parcellecomposante_pdl_fk FOREIGN KEY (pdl) REFERENCES pdl (pdl) ON DELETE CASCADE;
-- clé étrangère : parcellecomposante -> parcelle x 2
ALTER TABLE parcellecomposante ADD CONSTRAINT parcellecomposante_parcelle_fk FOREIGN KEY (parcelle) REFERENCES parcelle (parcelle) ON DELETE CASCADE;
ALTER TABLE parcellecomposante ADD CONSTRAINT parcellecomposante_parcellea_fk FOREIGN KEY (parcellea) REFERENCES parcelle (parcelle) ON DELETE CASCADE;
-- clé étrangère : lotslocaux -> lots
ALTER TABLE lotslocaux ADD CONSTRAINT lotslocaux_lots_fk FOREIGN KEY ( lots ) REFERENCES lots (lots) ON DELETE CASCADE;
-- clé étrangère : lotslocaux -> local00
ALTER TABLE lotslocaux ADD CONSTRAINT lotslocaux_local00_fk FOREIGN KEY (local00) REFERENCES local00 (local00) ON DELETE CASCADE;
-- clé étrangère : lotslocaux -> local10
ALTER TABLE lotslocaux ADD CONSTRAINT lotslocaux_local10_fk FOREIGN KEY (local10) REFERENCES local10 (local10) ON DELETE CASCADE;
-- clé étrangère : commune -> geo_commune
ALTER TABLE commune ADD CONSTRAINT commune_geo_commune_fk FOREIGN KEY (geo_commune) REFERENCES geo_commune (geo_commune) ON DELETE SET NULL;
-- clé étrangère : commune -> typcom
ALTER TABLE commune ADD CONSTRAINT lotslocaux_typcom_fk FOREIGN KEY (typcom) REFERENCES typcom (typcom) ON DELETE CASCADE;
-- clé étrangère : voie -> commune
ALTER TABLE voie ADD CONSTRAINT voie_commune_fk FOREIGN KEY (commune) REFERENCES commune (commune) ON DELETE CASCADE;
-- clé étrangère : voie -> typcom
ALTER TABLE voie ADD CONSTRAINT voie_typcom_fk FOREIGN KEY (typcom) REFERENCES typcom (typcom) ON DELETE CASCADE;
-- clé étrangère : voie -> natvoiriv
ALTER TABLE voie ADD CONSTRAINT voie_natvoiriv_fk FOREIGN KEY (natvoiriv) REFERENCES natvoiriv (natvoiriv) ON DELETE CASCADE;
-- clé étrangère : voie -> carvoi
ALTER TABLE voie ADD CONSTRAINT voie_carvoi_fk FOREIGN KEY (carvoi) REFERENCES carvoi (carvoi) ON DELETE CASCADE;
-- clé étrangère : voie -> annul
ALTER TABLE voie ADD CONSTRAINT voie_annul_fk FOREIGN KEY (annul) REFERENCES annul (annul) ON DELETE CASCADE;
-- clé étrangère : voie -> typvoi
ALTER TABLE voie ADD CONSTRAINT voie_typvoi_fk FOREIGN KEY (typvoi) REFERENCES typvoi (typvoi) ON DELETE CASCADE;
-- clé étrangère : voie -> indldnbat
ALTER TABLE voie ADD CONSTRAINT voie_indldnbat_fk FOREIGN KEY (indldnbat) REFERENCES indldnbat (indldnbat) ON DELETE CASCADE;
-- clé étrangère : geo_commune -> commune
ALTER TABLE geo_commune ADD CONSTRAINT geo_commune_commune_fk FOREIGN KEY (commune) REFERENCES commune (commune) ON DELETE SET NULL;
-- clé étrangère : geo_section -> geo_commune
ALTER TABLE geo_section ADD CONSTRAINT geo_section_commune_fk FOREIGN KEY (geo_commune) REFERENCES geo_commune (geo_commune) ON DELETE CASCADE;
-- clé étrangère : geo_subdsect -> geo_qupl_fk
ALTER TABLE geo_subdsect ADD CONSTRAINT geo_subdsect_qupl_fk FOREIGN KEY (geo_qupl) REFERENCES geo_qupl (geo_qupl) ON DELETE CASCADE;
-- clé étrangère : geo_subdsect -> geo_copl
ALTER TABLE geo_subdsect ADD CONSTRAINT geo_subdsect_copl_fk FOREIGN KEY (geo_copl) REFERENCES geo_copl (geo_copl) ON DELETE CASCADE;
-- clé étrangère : geo_subdsect -> geo_inp_fk
ALTER TABLE geo_subdsect ADD CONSTRAINT geo_subdsect_inp_fk FOREIGN KEY (geo_inp) REFERENCES geo_inp (geo_inp) ON DELETE CASCADE;
-- clé étrangère : geo_subdsect -> geo_section
ALTER TABLE geo_subdsect ADD CONSTRAINT geo_subdsect_section_fk FOREIGN KEY (geo_section) REFERENCES geo_section (geo_section) ON DELETE CASCADE;
-- clé étrangère : geo_parcelle -> geo_indp
ALTER TABLE geo_parcelle ADD CONSTRAINT geo_parcelle_indp_fk FOREIGN KEY (geo_indp) REFERENCES geo_indp (geo_indp) ON DELETE CASCADE;
-- clé étrangère : geo_parcelle -> geo_section
ALTER TABLE geo_parcelle ADD CONSTRAINT geo_parcelle_section_fk FOREIGN KEY (geo_section) REFERENCES geo_section (geo_section) ON DELETE CASCADE;
-- clé étrangère : geo_parcelle -> geo_subdsect
ALTER TABLE geo_parcelle ADD CONSTRAINT geo_parcelle_subdsect_fk FOREIGN KEY (geo_subdsect) REFERENCES geo_subdsect (geo_subdsect) ON DELETE CASCADE;
-- clé étrangère : geo_parcelle -> geo_parcelle
ALTER TABLE geo_parcelle ADD CONSTRAINT geo_parcelle_parcelle_fk FOREIGN KEY (parcelle) REFERENCES parcelle (parcelle) ON DELETE SET NULL;
-- clé étrangère : geo_subdfisc_parcelle_s_fk
ALTER TABLE geo_subdfisc_parcelle ADD CONSTRAINT geo_subdfisc_parcelle_s_fk FOREIGN KEY (geo_subdfisc) REFERENCES geo_subdfisc (geo_subdfisc) ON DELETE CASCADE;
-- clé étrangère : geo_subdfisc_parcelle_p_fk
ALTER TABLE geo_subdfisc_parcelle ADD CONSTRAINT geo_subdfisc_parcelle_p_fk FOREIGN KEY (geo_parcelle) REFERENCES geo_parcelle (geo_parcelle) ON DELETE CASCADE;
-- clé étrangère : geo_numvoie_parcelle_n_fk
ALTER TABLE geo_numvoie_parcelle ADD CONSTRAINT geo_numvoie_parcelle_n_fk FOREIGN KEY (geo_numvoie) REFERENCES geo_numvoie (geo_numvoie) ON DELETE CASCADE;
-- clé étrangère : geo_numvoie_parcelle_p_fk
ALTER TABLE geo_numvoie_parcelle ADD CONSTRAINT geo_numvoie_parcelle_p_fk FOREIGN KEY (geo_parcelle) REFERENCES geo_parcelle (geo_parcelle) ON DELETE CASCADE;
-- clé étrangère : geo_batiment -> geo_dur
ALTER TABLE geo_batiment ADD CONSTRAINT geo_batiment_dur_fk FOREIGN KEY (geo_dur) REFERENCES geo_dur (geo_dur) ON DELETE CASCADE;
-- clé étrangère : geo_batiment_parcelle_n_fk
ALTER TABLE geo_batiment_parcelle ADD CONSTRAINT geo_batiment_parcelle_n_fk FOREIGN KEY (geo_batiment) REFERENCES geo_batiment (geo_batiment) ON DELETE CASCADE;
-- clé étrangère : geo_batiment_parcelle_p_fk
ALTER TABLE geo_batiment_parcelle ADD CONSTRAINT geo_batiment_parcelle_p_fk FOREIGN KEY (geo_parcelle) REFERENCES geo_parcelle (geo_parcelle) ON DELETE CASCADE;
-- clé étrangère : geo_ptcanv -> geo_can
ALTER TABLE geo_ptcanv ADD CONSTRAINT geo_ptcanv_can_fk FOREIGN KEY (geo_can) REFERENCES geo_can (geo_can) ON DELETE CASCADE;
-- clé étrangère : geo_ptcanv -> geo_ppln
ALTER TABLE geo_ptcanv ADD CONSTRAINT geo_ptcanv_ppln_fk FOREIGN KEY (geo_ppln) REFERENCES geo_ppln (geo_ppln) ON DELETE CASCADE;
-- clé étrangère : geo_ptcanv -> geo_palt
ALTER TABLE geo_ptcanv ADD CONSTRAINT geo_ptcanv_palt_fk FOREIGN KEY (geo_palt) REFERENCES geo_palt (geo_palt) ON DELETE CASCADE;
-- clé étrangère : geo_ptcanv -> geo_map
ALTER TABLE geo_ptcanv ADD CONSTRAINT geo_ptcanv_map_fk FOREIGN KEY (geo_map) REFERENCES geo_map (geo_map) ON DELETE CASCADE;
-- clé étrangère : geo_ptcanv -> geo_sym
ALTER TABLE geo_ptcanv ADD CONSTRAINT geo_ptcanv_sym_fk FOREIGN KEY (geo_sym) REFERENCES geo_sym (geo_sym) ON DELETE CASCADE;
-- clé étrangère : geo_borne_parcelle_n_fk
ALTER TABLE geo_borne_parcelle ADD CONSTRAINT geo_borne_parcelle_n_fk FOREIGN KEY (geo_borne) REFERENCES geo_borne (geo_borne) ON DELETE CASCADE;
-- clé étrangère : geo_borne_parcelle_p_fk
ALTER TABLE geo_borne_parcelle ADD CONSTRAINT geo_borne_parcelle_p_fk FOREIGN KEY (geo_parcelle) REFERENCES geo_parcelle (geo_parcelle) ON DELETE CASCADE;
-- clé étrangère : geo_croix_parcelle_n_fk
ALTER TABLE geo_croix_parcelle ADD CONSTRAINT geo_croix_parcelle_n_fk FOREIGN KEY (geo_croix) REFERENCES geo_croix (geo_croix) ON DELETE CASCADE;
-- clé étrangère : geo_croix_parcelle_p_fk
ALTER TABLE geo_croix_parcelle ADD CONSTRAINT geo_croix_parcelle_p_fk FOREIGN KEY (geo_parcelle) REFERENCES geo_parcelle (geo_parcelle) ON DELETE CASCADE;
-- clé étrangère : geo_symblim -> geo_sym
ALTER TABLE geo_symblim ADD CONSTRAINT geo_symblim_sym_n_fk FOREIGN KEY (geo_sym) REFERENCES geo_sym (geo_sym) ON DELETE CASCADE;
-- clé étrangère : geo_symblim_parcelle_n_fk
ALTER TABLE geo_symblim_parcelle ADD CONSTRAINT geo_symblim_parcelle_n_fk FOREIGN KEY (geo_symblim) REFERENCES geo_symblim (geo_symblim) ON DELETE CASCADE;
-- clé étrangère : geo_symblim_parcelle_p_fk
ALTER TABLE geo_symblim_parcelle ADD CONSTRAINT geo_symblim_parcelle_p_fk FOREIGN KEY (geo_parcelle) REFERENCES geo_parcelle (geo_parcelle) ON DELETE CASCADE;
-- clé étrangère : geo_tpoint -> geo_sym
ALTER TABLE geo_tpoint ADD CONSTRAINT geo_tpoint_sym_n_fk FOREIGN KEY (geo_sym) REFERENCES geo_sym (geo_sym) ON DELETE CASCADE;
-- clé étrangère : geo_tpoint_commune_n_fk
ALTER TABLE geo_tpoint_commune ADD CONSTRAINT geo_tpoint_commune_n_fk FOREIGN KEY (geo_tpoint) REFERENCES geo_tpoint (geo_tpoint) ON DELETE CASCADE;
-- clé étrangère : geo_tpoint_commune_p_fk
ALTER TABLE geo_tpoint_commune ADD CONSTRAINT geo_tpoint_commune_p_fk FOREIGN KEY (geo_commune) REFERENCES geo_commune (geo_commune) ON DELETE CASCADE;
-- clé étrangère : geo_tline -> geo_sym
ALTER TABLE geo_tline ADD CONSTRAINT geo_tline_sym_n_fk FOREIGN KEY (geo_sym) REFERENCES geo_sym (geo_sym) ON DELETE CASCADE;
-- clé étrangère : geo_tline_commune_n_fk
ALTER TABLE geo_tline_commune ADD CONSTRAINT geo_tline_commune_n_fk FOREIGN KEY (geo_tline) REFERENCES geo_tline (geo_tline) ON DELETE CASCADE;
-- clé étrangère : geo_tline_commune_p_fk
ALTER TABLE geo_tline_commune ADD CONSTRAINT geo_tline_commune_p_fk FOREIGN KEY (geo_commune) REFERENCES geo_commune (geo_commune) ON DELETE CASCADE;
-- clé étrangère : geo_tsurf -> geo_sym
ALTER TABLE geo_tsurf ADD CONSTRAINT geo_tsurf_sym_n_fk FOREIGN KEY (geo_sym) REFERENCES geo_sym (geo_sym) ON DELETE CASCADE;
-- clé étrangère : geo_tsurf_commune_n_fk
ALTER TABLE geo_tsurf_commune ADD CONSTRAINT geo_tsurf_commune_n_fk FOREIGN KEY (geo_tsurf) REFERENCES geo_tsurf (geo_tsurf) ON DELETE CASCADE;
-- clé étrangère : geo_tsurf_commune_p_fk
ALTER TABLE geo_tsurf_commune ADD CONSTRAINT geo_tsurf_commune_p_fk FOREIGN KEY (geo_commune) REFERENCES geo_commune (geo_commune) ON DELETE CASCADE;

