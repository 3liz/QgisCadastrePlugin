-- Creation des tables EDIGEO
CREATE TABLE IF NOT EXISTS batiment_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    dur character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);
CREATE TABLE IF NOT EXISTS batiment_id_label (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    fon character varying,
    hei double precision,
    tyu character varying,
    cef double precision,
    csp double precision,
    di1 double precision,
    di2 double precision,
    di3 double precision,
    di4 double precision,
    tpa character varying,
    hta character varying,
    vta character varying,
    atr character varying,
    ogr_obj_lnk character varying,
    ogr_obj_lnk_layer character varying,
    ogr_atr_val character varying,
    ogr_angle double precision,
    ogr_font_size double precision
);
CREATE TABLE IF NOT EXISTS borne_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    creat_date integer,
    update_date integer
);
CREATE TABLE IF NOT EXISTS commune_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    idu character varying,
    tex2 character varying,
    creat_date integer,
    update_date integer
);
CREATE TABLE IF NOT EXISTS croix_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    creat_date integer,
    update_date integer
);
CREATE TABLE IF NOT EXISTS id_s_obj_z_1_2_2 (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    fon character varying,
    hei double precision,
    tyu character varying,
    cef double precision,
    csp double precision,
    di1 double precision,
    di2 double precision,
    di3 double precision,
    di4 double precision,
    tpa character varying,
    hta character varying,
    vta character varying,
    atr character varying,
    ogr_obj_lnk character varying,
    ogr_obj_lnk_layer character varying,
    ogr_atr_val character varying,
    ogr_angle double precision,
    ogr_font_size double precision
);
CREATE TABLE IF NOT EXISTS lieudit_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    tex10 character varying,
    tex2 character varying,
    tex3 character varying,
    tex4 character varying,
    tex5 character varying,
    tex6 character varying,
    tex7 character varying,
    tex8 character varying,
    tex9 character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);

CREATE TABLE IF NOT EXISTS lieudit_id_label (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    fon character varying,
    hei double precision,
    tyu character varying,
    cef double precision,
    csp double precision,
    di1 double precision,
    di2 double precision,
    di3 double precision,
    di4 double precision,
    tpa character varying,
    hta character varying,
    vta character varying,
    atr character varying,
    ogr_obj_lnk character varying,
    ogr_obj_lnk_layer character varying,
    ogr_atr_val character varying,
    ogr_angle double precision,
    ogr_font_size double precision
);

CREATE TABLE IF NOT EXISTS numvoie_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);

CREATE TABLE IF NOT EXISTS numvoie_id_label (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    fon character varying,
    hei double precision,
    tyu character varying,
    cef double precision,
    csp double precision,
    di1 double precision,
    di2 double precision,
    di3 double precision,
    di4 double precision,
    tpa character varying,
    hta character varying,
    vta character varying,
    atr character varying,
    ogr_obj_lnk character varying,
    ogr_obj_lnk_layer character varying,
    ogr_atr_val character varying,
    ogr_angle double precision,
    ogr_font_size double precision
);

CREATE TABLE IF NOT EXISTS parcelle_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    coar character varying,
    codm character varying,
    idu character varying,
    indp character varying,
    supf double precision,
    tex2 character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);

CREATE TABLE IF NOT EXISTS parcelle_id_label (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    fon character varying,
    hei double precision,
    tyu character varying,
    cef double precision,
    csp double precision,
    di1 double precision,
    di2 double precision,
    di3 double precision,
    di4 double precision,
    tpa character varying,
    hta character varying,
    vta character varying,
    atr character varying,
    ogr_obj_lnk character varying,
    ogr_obj_lnk_layer character varying,
    ogr_atr_val character varying,
    ogr_angle double precision,
    ogr_font_size double precision
);

CREATE TABLE IF NOT EXISTS ptcanv_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    can character varying,
    idu character varying,
    map character varying,
    palt character varying,
    ppln character varying,
    sym character varying,
    creat_date integer,
    update_date integer
);

CREATE TABLE IF NOT EXISTS section_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    idu character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);

CREATE TABLE IF NOT EXISTS section_id_label (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    fon character varying,
    hei double precision,
    tyu character varying,
    cef double precision,
    csp double precision,
    di1 double precision,
    di2 double precision,
    di3 double precision,
    di4 double precision,
    tpa character varying,
    hta character varying,
    vta character varying,
    atr character varying,
    ogr_obj_lnk character varying,
    ogr_obj_lnk_layer character varying,
    ogr_atr_val character varying,
    ogr_angle double precision,
    ogr_font_size double precision
);

CREATE TABLE IF NOT EXISTS subdfisc_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);

CREATE TABLE IF NOT EXISTS subdfisc_id_label (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    fon character varying,
    hei double precision,
    tyu character varying,
    cef double precision,
    csp double precision,
    di1 double precision,
    di2 double precision,
    di3 double precision,
    di4 double precision,
    tpa character varying,
    hta character varying,
    vta character varying,
    atr character varying,
    ogr_obj_lnk character varying,
    ogr_obj_lnk_layer character varying,
    ogr_atr_val character varying,
    ogr_angle double precision,
    ogr_font_size double precision
);

CREATE TABLE IF NOT EXISTS subdsect_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    copl character varying,
    dedi character varying,
    dis character varying,
    dred character varying,
    eor character varying,
    icl double precision,
    idu character varying,
    inp character varying,
    qupl character varying,
    creat_date integer,
    update_date integer
);

CREATE TABLE IF NOT EXISTS symblim_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    ori double precision,
    sym character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);

CREATE TABLE IF NOT EXISTS tline_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    sym character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);

CREATE TABLE IF NOT EXISTS tline_id_label (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    fon character varying,
    hei double precision,
    tyu character varying,
    cef double precision,
    csp double precision,
    di1 double precision,
    di2 double precision,
    di3 double precision,
    di4 double precision,
    tpa character varying,
    hta character varying,
    vta character varying,
    atr character varying,
    ogr_obj_lnk character varying,
    ogr_obj_lnk_layer character varying,
    ogr_atr_val character varying,
    ogr_angle double precision,
    ogr_font_size double precision
);

CREATE TABLE IF NOT EXISTS tpoint_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    ori double precision,
    sym character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);

CREATE TABLE IF NOT EXISTS tpoint_id_label (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    fon character varying,
    hei double precision,
    tyu character varying,
    cef double precision,
    csp double precision,
    di1 double precision,
    di2 double precision,
    di3 double precision,
    di4 double precision,
    tpa character varying,
    hta character varying,
    vta character varying,
    atr character varying,
    ogr_obj_lnk character varying,
    ogr_obj_lnk_layer character varying,
    ogr_atr_val character varying,
    ogr_angle double precision,
    ogr_font_size double precision
);

CREATE TABLE IF NOT EXISTS tronfluv_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    tex10 character varying,
    tex2 character varying,
    tex3 character varying,
    tex4 character varying,
    tex5 character varying,
    tex6 character varying,
    tex7 character varying,
    tex8 character varying,
    tex9 character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);

CREATE TABLE IF NOT EXISTS tronfluv_id_label (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    fon character varying,
    hei double precision,
    tyu character varying,
    cef double precision,
    csp double precision,
    di1 double precision,
    di2 double precision,
    di3 double precision,
    di4 double precision,
    tpa character varying,
    hta character varying,
    vta character varying,
    atr character varying,
    ogr_obj_lnk character varying,
    ogr_obj_lnk_layer character varying,
    ogr_atr_val character varying,
    ogr_angle double precision,
    ogr_font_size double precision
);

CREATE TABLE IF NOT EXISTS tronroute_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    rcad character varying,
    tex10 character varying,
    tex2 character varying,
    tex3 character varying,
    tex4 character varying,
    tex5 character varying,
    tex6 character varying,
    tex7 character varying,
    tex8 character varying,
    tex9 character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);

CREATE TABLE IF NOT EXISTS tronroute_id_label (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    fon character varying,
    hei double precision,
    tyu character varying,
    cef double precision,
    csp double precision,
    di1 double precision,
    di2 double precision,
    di3 double precision,
    di4 double precision,
    tpa character varying,
    hta character varying,
    vta character varying,
    atr character varying,
    ogr_obj_lnk character varying,
    ogr_obj_lnk_layer character varying,
    ogr_atr_val character varying,
    ogr_angle double precision,
    ogr_font_size double precision
);

CREATE TABLE IF NOT EXISTS tsurf_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    sym character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);

CREATE TABLE IF NOT EXISTS tsurf_id_label (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    fon character varying,
    hei double precision,
    tyu character varying,
    cef double precision,
    csp double precision,
    di1 double precision,
    di2 double precision,
    di3 double precision,
    di4 double precision,
    tpa character varying,
    hta character varying,
    vta character varying,
    atr character varying,
    ogr_obj_lnk character varying,
    ogr_obj_lnk_layer character varying,
    ogr_atr_val character varying,
    ogr_angle double precision,
    ogr_font_size double precision
);

CREATE TABLE IF NOT EXISTS voiep_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);

CREATE TABLE IF NOT EXISTS voiep_id_label (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    fon character varying,
    hei double precision,
    tyu character varying,
    cef double precision,
    csp double precision,
    di1 double precision,
    di2 double precision,
    di3 double precision,
    di4 double precision,
    tpa character varying,
    hta character varying,
    vta character varying,
    atr character varying,
    ogr_obj_lnk character varying,
    ogr_obj_lnk_layer character varying,
    ogr_atr_val character varying,
    ogr_angle double precision,
    ogr_font_size double precision
);

CREATE TABLE IF NOT EXISTS zoncommuni_id (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    tex10 character varying,
    tex2 character varying,
    tex3 character varying,
    tex4 character varying,
    tex5 character varying,
    tex6 character varying,
    tex7 character varying,
    tex8 character varying,
    tex9 character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);

CREATE TABLE IF NOT EXISTS zoncommuni_id_label (
    ogc_fid serial PRIMARY KEY,
    geom public.geometry(Geometry,2154),
    object_rid character varying,
    fon character varying,
    hei double precision,
    tyu character varying,
    cef double precision,
    csp double precision,
    di1 double precision,
    di2 double precision,
    di3 double precision,
    di4 double precision,
    tpa character varying,
    hta character varying,
    vta character varying,
    atr character varying,
    ogr_obj_lnk character varying,
    ogr_obj_lnk_layer character varying,
    ogr_atr_val character varying,
    ogr_angle double precision,
    ogr_font_size double precision
);


CREATE INDEX batiment_id_geom_idx ON batiment_id USING gist (geom);
CREATE INDEX batiment_id_label_geom_idx ON batiment_id_label USING gist (geom);
CREATE INDEX borne_id_geom_idx ON borne_id USING gist (geom);
CREATE INDEX commune_id_geom_idx ON commune_id USING gist (geom);
CREATE INDEX croix_id_geom_idx ON croix_id USING gist (geom);
CREATE INDEX id_s_obj_z_1_2_2_geom_idx ON id_s_obj_z_1_2_2 USING gist (geom);
CREATE INDEX lieudit_id_geom_idx ON lieudit_id USING gist (geom);
CREATE INDEX lieudit_id_label_geom_idx ON lieudit_id_label USING gist (geom);
CREATE INDEX numvoie_id_geom_idx ON numvoie_id USING gist (geom);
CREATE INDEX numvoie_id_label_geom_idx ON numvoie_id_label USING gist (geom);
CREATE INDEX parcelle_id_geom_idx ON parcelle_id USING gist (geom);
CREATE INDEX parcelle_id_label_geom_idx ON parcelle_id_label USING gist (geom);
CREATE INDEX ptcanv_id_geom_idx ON ptcanv_id USING gist (geom);
CREATE INDEX section_id_geom_idx ON section_id USING gist (geom);
CREATE INDEX section_id_label_geom_idx ON section_id_label USING gist (geom);
CREATE INDEX subdfisc_id_geom_idx ON subdfisc_id USING gist (geom);
CREATE INDEX subdfisc_id_label_geom_idx ON subdfisc_id_label USING gist (geom);
CREATE INDEX subdsect_id_geom_idx ON subdsect_id USING gist (geom);
CREATE INDEX symblim_id_geom_idx ON symblim_id USING gist (geom);
CREATE INDEX tline_id_geom_idx ON tline_id USING gist (geom);
CREATE INDEX tline_id_label_geom_idx ON tline_id_label USING gist (geom);
CREATE INDEX tpoint_id_geom_idx ON tpoint_id USING gist (geom);
CREATE INDEX tpoint_id_label_geom_idx ON tpoint_id_label USING gist (geom);
CREATE INDEX tronfluv_id_geom_idx ON tronfluv_id USING gist (geom);
CREATE INDEX tronfluv_id_label_geom_idx ON tronfluv_id_label USING gist (geom);
CREATE INDEX tronroute_id_geom_idx ON tronroute_id USING gist (geom);
CREATE INDEX tronroute_id_label_geom_idx ON tronroute_id_label USING gist (geom);
CREATE INDEX tsurf_id_geom_idx ON tsurf_id USING gist (geom);
CREATE INDEX tsurf_id_label_geom_idx ON tsurf_id_label USING gist (geom);
CREATE INDEX voiep_id_geom_idx ON voiep_id USING gist (geom);
CREATE INDEX voiep_id_label_geom_idx ON voiep_id_label USING gist (geom);
CREATE INDEX zoncommuni_id_geom_idx ON zoncommuni_id USING gist (geom);
CREATE INDEX zoncommuni_id_label_geom_idx ON zoncommuni_id_label USING gist (geom);
