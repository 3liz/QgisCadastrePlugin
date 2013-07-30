SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
CREATE SCHEMA opencadastre AUTHORIZATION postgres;
GRANT ALL ON SCHEMA opencadastre TO postgres;
COMMENT ON SCHEMA opencadastre IS 'OpenCadastre';
\set ON_ERROR_STOP on
SET search_path = opencadastre, public, pg_catalog;
\set wms_opencadastre_url '\'http://localhost/cartes/qgis/qgis_mapserv.fcgi.exe?SERVICE=WMS&VERSION=1.3.0&map=C:/wamp/www/opencadastre/app/qgis/projet.qgs\''

\i init.sql
\i create_metier.sql
\i create_table_dgi.sql
\i create_constraints.sql
\i insert_nomenclatures.sql
\i insert_droits.sql
\i insert_om_sig.sql
