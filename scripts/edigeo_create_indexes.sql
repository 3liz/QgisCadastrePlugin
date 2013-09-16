-- geometries
CREATE INDEX geo_commune_geom_idx ON geo_commune USING gist (geom );
CREATE INDEX geo_section_geom_idx ON geo_section USING gist (geom );
CREATE INDEX geo_subdsect_geom_idx ON geo_subdsect USING gist (geom );
CREATE INDEX geo_parcelle_geom_idx ON geo_parcelle USING gist (geom );
CREATE INDEX geo_subdfisc_geom_idx ON geo_subdfisc USING gist (geom );
CREATE INDEX geo_voiep_geom_idx ON geo_voiep USING gist (geom );
CREATE INDEX geo_numvoie_geom_idx ON geo_numvoie USING gist (geom );
CREATE INDEX geo_lieudit_geom_idx ON geo_lieudit USING gist (geom );
CREATE INDEX geo_batiment_geom_idx ON geo_batiment USING gist (geom );
CREATE INDEX geo_zoncommuni_geom_idx ON geo_zoncommuni USING gist (geom );
CREATE INDEX geo_tronfluv_geom_idx ON geo_tronfluv USING gist (geom );
CREATE INDEX geo_ptcanv_geom_idx ON geo_ptcanv USING gist (geom );
CREATE INDEX geo_borne_geom_idx ON geo_borne USING gist (geom );
CREATE INDEX geo_croix_geom_idx ON geo_croix USING gist (geom );
CREATE INDEX geo_symblim_geom_idx ON geo_symblim USING gist (geom );
CREATE INDEX geo_tpoint_geom_idx ON geo_tpoint USING gist (geom );
CREATE INDEX geo_tline_geom_idx ON geo_tline USING gist (geom );
CREATE INDEX geo_tsurf_geom_idx ON geo_tsurf USING gist (geom );
-- attributes
CREATE INDEX geo_commune_tex2_idx ON geo_commune (tex2);
CREATE INDEX geo_section_idu_idx ON geo_section (idu);
CREATE INDEX geo_parcelle_idu_idx ON geo_parcelle (idu);
CREATE INDEX parcelle_geo_parcelle_idx ON parcelle (geo_parcelle);
CREATE INDEX proprietaire_dnupro_idx ON proprietaire (dnupro);
CREATE INDEX proprietaire_ddenom_idx ON proprietaire (ddenom);
CREATE INDEX parcelle_dnupro_idx ON parcelle (dnupro);
CREATE INDEX geo_section_geo_commune_idx ON geo_section (geo_commune);
CREATE INDEX geo_parcelle_geo_section_idx ON geo_parcelle (geo_section);
CREATE INDEX geo_parcelle_comptecommunal_idx ON geo_parcelle (comptecommunal);
CREATE INDEX geo_parcelle_dvoilib_idx ON geo_parcelle (dvoilib);
-- Primary keys
ALTER TABLE geo_commune ADD PRIMARY KEY (ogc_fid);
ALTER TABLE geo_section ADD PRIMARY KEY (ogc_fid);
ALTER TABLE geo_parcelle ADD PRIMARY KEY (ogc_fid);
