-- Creation des tables EDIGEO
CREATE TABLE IF NOT EXISTS batiment_id (
    ogc_fid serial,
    object_rid character varying,
    dur character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);
SELECT AddGeometryColumn('batiment_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS borne_id (
    ogc_fid serial,
    object_rid character varying,
    creat_date integer,
    update_date integer
);
SELECT AddGeometryColumn('borne_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS commune_id (
    ogc_fid serial,
    object_rid character varying,
    idu character varying,
    tex2 character varying,
    creat_date integer,
    update_date integer
);
SELECT AddGeometryColumn('commune_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS croix_id (
    ogc_fid serial,
    object_rid character varying,
    creat_date integer,
    update_date integer
);
SELECT AddGeometryColumn('croix_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS id_s_obj_z_1_2_2 (
    ogc_fid serial,
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
SELECT AddGeometryColumn('id_s_obj_z_1_2_2', 'geom', 2154, 'POINT', 2);

CREATE TABLE IF NOT EXISTS lieudit_id (
    ogc_fid serial,
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
SELECT AddGeometryColumn('lieudit_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS numvoie_id (
    ogc_fid serial,
    object_rid character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);
SELECT AddGeometryColumn('numvoie_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS parcelle_id (
    ogc_fid serial,
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
SELECT AddGeometryColumn('parcelle_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS ptcanv_id (
    ogc_fid serial,
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
SELECT AddGeometryColumn('ptcanv_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS section_id (
    ogc_fid serial,
    object_rid character varying,
    idu character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);
SELECT AddGeometryColumn('section_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS subdfisc_id (
    ogc_fid serial,
    object_rid character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);
SELECT AddGeometryColumn('subdfisc_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS subdsect_id (
    ogc_fid serial,
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
SELECT AddGeometryColumn('subdsect_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS symblim_id (
    ogc_fid serial,
    object_rid character varying,
    ori double precision,
    sym character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);
SELECT AddGeometryColumn('symblim_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS tline_id (
    ogc_fid serial,
    object_rid character varying,
    sym character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);
SELECT AddGeometryColumn('tline_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS tpoint_id (
    ogc_fid serial,
    object_rid character varying,
    ori double precision,
    sym character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);
SELECT AddGeometryColumn('tpoint_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS tronfluv_id (
    ogc_fid serial,
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
SELECT AddGeometryColumn('tronfluv_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS tronroute_id (
    ogc_fid serial,
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
SELECT AddGeometryColumn('tronroute_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS tsurf_id (
    ogc_fid serial,
    object_rid character varying,
    sym character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);
SELECT AddGeometryColumn('tsurf_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS voiep_id (
    ogc_fid serial,
    object_rid character varying,
    tex character varying,
    creat_date integer,
    update_date integer
);
SELECT AddGeometryColumn('voiep_id', 'geom', 2154, 'GEOMETRY', 2);

CREATE TABLE IF NOT EXISTS zoncommuni_id (
    ogc_fid serial,
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
SELECT AddGeometryColumn('zoncommuni_id', 'geom', 2154, 'GEOMETRY', 2);
