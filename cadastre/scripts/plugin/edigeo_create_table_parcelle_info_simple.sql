BEGIN;

INSERT INTO ${PREFIXE}parcelle_info
SELECT gp.ogc_fid AS ogc_fid, geo_parcelle, gp.idu AS idu, gp.tex AS tex, gp.geo_section AS geo_section,
c.tex2 AS nomcommune, c.idu AS codecommune, Cast(ST_Area(gp.geom) AS bigint) AS surface_geo, gp.supf AS contenance,
gp.lot AS lot,
gp.geom AS geom
FROM ${PREFIXE}geo_parcelle gp
INNER JOIN ${PREFIXE}geo_commune c
ON c.geo_commune = SUBSTRING(gp.geo_parcelle,1,6)
WHERE gp.lot = '${LOT}'
;

COMMIT;
