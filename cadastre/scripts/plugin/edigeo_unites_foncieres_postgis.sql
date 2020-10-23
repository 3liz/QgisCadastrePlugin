-- Création des unités foncières pour PostGIS
INSERT INTO [PREFIXE]geo_unite_fonciere (comptecommunal, annee, lot, geom)
  SELECT 
    comptecommunal,
    '[ANNEE]', '[LOT]', 
    ST_Multi((St_Dump(St_Union(a.geom))).geom) as geom
  FROM [PREFIXE]v_geo_parcelle a
  WHERE
    a.annee = '[ANNEE]'
    AND a.lot = '[LOT]'
    AND ST_IsValid(a.geom)
    AND comptecommunal IS NOT NULL
    GROUP BY comptecommunal;
