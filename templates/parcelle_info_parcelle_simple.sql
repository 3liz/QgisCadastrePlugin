SELECT

    '<table class="table table-condensed table-striped" border=1 cellspacing=0 cellpadding=3>' ||
        '<tr><th>Code</th><td>' || p.idu || '</td></tr>' ||
        '<tr><th>Commune</th><td>' || c.tex2 || '</td></tr>' ||
        '<tr><th>Surface géographique</th><td>' || round(ST_Area(p.geom)) || '</td></tr>' ||
    '</table>'

FROM geo_parcelle p
INNER JOIN geo_commune c
ON ST_Intersects(ST_Centroid(p.geom), c.geom)
WHERE geo_parcelle = '%s'
