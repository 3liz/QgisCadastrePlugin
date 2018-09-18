SELECT c.tex2 AS nomcommune, c.idu AS codecommune, '' AS contenance,
'' AS adresse,
'' AS urbain,
p.idu,
'' AS jdatat
FROM geo_parcelle p
INNER JOIN geo_commune c
ON ST_Intersects(p.geom, c.geom)
WHERE geo_parcelle = '%s'
