-- General information of a parcel without MAJIC data, from the EDIGEO tables only: one row
-- Parameter: {parcelle}, the identifier of the parcel, quoted by fetch_rows

SELECT
    p.idu AS code,
    c.tex2 AS commune,
    round(ST_Area(p.geom)) AS surface_geographique,
    sum(round(ST_Area(b.geom))) AS surface_batie,
    round(100 * sum(ST_Area(b.geom)) / ST_Area(p.geom)) AS pourcentage_bati
FROM geo_parcelle p
INNER JOIN geo_commune c ON ST_Intersects(ST_Centroid(p.geom), c.geom)
LEFT JOIN geo_batiment b
    ON ST_Intersects(b.geom, p.geom) AND ST_Intersects(ST_Centroid(b.geom), p.geom)
WHERE p.geo_parcelle = {parcelle}
GROUP BY p.idu, p.geom, c.tex2
