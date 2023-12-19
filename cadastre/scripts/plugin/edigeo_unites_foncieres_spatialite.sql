-- Création des unités foncières pour Spatialite
INSERT INTO geo_unite_fonciere (comptecommunal, annee, lot, geom)
  SELECT 
    comptecommunal,
    '${ANNEE}', '${LOT}', 
    CastToMultiPolygon(st_unaryunion(st_collect(a.geom))) as geom
  FROM v_geo_parcelle a
  WHERE
    a.annee = '${ANNEE}'
    AND a.lot = '${LOT}'
    AND ST_IsValid(a.geom)
    AND comptecommunal IS NOT NULL
    GROUP BY comptecommunal;
