-- General information of a parcel with the MAJIC data: one row.
-- The buildings of the parcel are the EDIGEO buildings whose centroid is in the parcel,
-- the first ST_Intersects lets PostgreSQL use the spatial index of the buildings.
-- Parameter: {parcelle}, the identifier of the parcel, quoted by fetch_rows

SELECT
    p.ccosec || p.dnupla AS code,
    c.libcom AS commune,
    p.jdatat AS date_acte,
    p.dcntpa AS contenance,
    round(ST_Area(gp.geom)) AS surface_geographique,
    p.gparbat AS batie,
    sum(round(ST_Area(b.geom))) AS surface_batie,
    round(100 * sum(ST_Area(b.geom)) / ST_Area(gp.geom)) AS pourcentage_bati,
    CASE
        WHEN v.libvoi IS NOT NULL
        THEN trim(Coalesce(ltrim(p.dnvoiri, '0'), '') || ' ' || trim(Coalesce(v.natvoi, '')) || ' ' || v.libvoi)
        ELSE trim(Coalesce(ltrim(p.cconvo, '0'), '') || ' ' || Coalesce(p.dvoilib, ''))
    END AS adresse,
    p.gurbpa AS urbaine
FROM parcelle p
INNER JOIN geo_parcelle gp ON p.parcelle = gp.geo_parcelle
LEFT JOIN geo_batiment b
    ON ST_Intersects(b.geom, gp.geom) AND ST_Intersects(ST_Centroid(b.geom), gp.geom)
LEFT JOIN commune c ON p.ccocom = c.ccocom AND c.ccodep = p.ccodep
LEFT JOIN voie v
    ON SUBSTR(p.voie, 1, 6) || SUBSTR(p.voie, 12, 4) = SUBSTR(v.voie, 1, 6) || SUBSTR(v.voie, 12, 4)
WHERE p.parcelle = {parcelle}
GROUP BY p.ccosec, p.dnupla, c.libcom, p.jdatat, p.dcntpa, gp.geom, v.libvoi, p.dnvoiri, v.natvoi,
    p.cconvo, p.dvoilib, p.gurbpa, p.gparbat
