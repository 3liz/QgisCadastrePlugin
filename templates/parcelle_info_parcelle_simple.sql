SELECT

    '<table class="table table-condensed table-striped" border=1 cellspacing=0 cellpadding=3>' ||
        '<tr><th>Code</th><td>' || p.idu || '</td></tr>' ||
        '<tr><th>Commune</th><td>' || c.tex2 || '</td></tr>' ||
        '<tr><th>Surface géographique</th><td>' || round(ST_Area(p.geom)) || ' m²</td></tr>' ||
        '<tr><th>Surface bâtie</th><td>' || coalesce(sum(round(ST_Area(b.geom))), 0) || ' m²</td></tr>' ||
        '<tr><th>Pourcentage du bâti</th><td>' || coalesce(round(100 * sum(ST_Area(b.geom)) / ST_Area(p.geom)), 0) || '</td></tr>' ||
    '</table>'

FROM geo_parcelle p
INNER JOIN geo_commune c
    ON ST_Intersects(ST_Centroid(p.geom), c.geom)
LEFT OUTER JOIN geo_batiment b
    ON ST_Intersects(ST_Centroid(b.geom), p.geom)
WHERE 2>1
AND geo_parcelle = '%s'
GROUP BY p.idu, p.geom, c.tex2
