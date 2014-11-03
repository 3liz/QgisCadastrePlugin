-- Création des unités foncières
UPDATE [PREFIXE]geo_parcelle SET geom_uf=NULL WHERE parcelle IN (SELECT parcellea FROM [PREFIXE]parcellecomposante WHERE annee='[ANNEE]');
UPDATE [PREFIXE]geo_parcelle SET geom_uf=p.geom FROM (
  SELECT parcelle, st_multi(st_union(geom)) AS geom FROM (
   SELECT pc.parcelle AS parcelle , st_multi(st_union(g.geom)) AS geom FROM [PREFIXE]geo_parcelle g, [PREFIXE]parcellecomposante pc WHERE g.parc
   UNION
   SELECT parcelle, geom FROM [PREFIXE]geo_parcelle WHERE parcelle NOT IN  (SELECT DISTINCT parcellea FROM [PREFIXE]parcellecomposante pc WHERE
  ) a GROUP BY parcelle) p
WHERE p.parcelle=geo_parcelle.parcelle;
