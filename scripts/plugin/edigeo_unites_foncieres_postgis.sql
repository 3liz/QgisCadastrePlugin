-- Création des unités foncières pour PostGIS
INSERT INTO [PREFIXE]geo_unite_fonciere (comptecommunal, annee, lot, geom)
SELECT comptecommunal, '[ANNEE]', '[LOT]', ST_Multi((St_Dump(St_Union(a.geom))).geom) AS geom
FROM [PREFIXE]geo_parcelle a
WHERE 2>1
-- AND ST_GeometryType(a.geom) IN ('ST_Polygon')
AND ST_IsValid(a.geom)
AND a.annee = '[ANNEE]'
AND a.lot = '[LOT]'
GROUP BY comptecommunal;
