-- Création des unités foncières pour Spatialite
INSERT INTO geo_unite_fonciere (comptecommunal, annee, lot, geom)
SELECT comptecommunal, '[ANNEE]' AS annee, '[LOT]' AS lot, CastToMultiPolygon(st_unaryunion(st_collect(a.geom))) as geom
FROM v_geo_parcelle a
WHERE 2>1
AND comptecommunal IS NOT NULL
AND ST_IsValid(a.geom)
GROUP BY comptecommunal
