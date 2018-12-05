SELECT

'<table class="table table-condensed table-striped" border=1 cellspacing=0 cellpadding=3>' ||
    '<tr><th>Code</th> <td>' || ccosec || dnupla || '</td></tr>' ||
    '<tr><th>Commune</th> <td>' || c.libcom || '</td></tr>' ||
    '<tr><th>Date de l''acte</th> <td>' || COALESCE(p.jdatat, '') || '</td></tr>' ||
    '<tr><th>Contenance</th> <td>' || p.dcntpa || ' m²</td></tr>' ||
    '<tr><th>Surface géographique</th> <td>' || round(ST_Area(gp.geom)) || ' m²</td></tr>' ||

    '<tr><th>Adresse</th> <td>' ||
    CASE
            WHEN v.libvoi IS NOT NULL THEN trim(ltrim(p.dnvoiri, '0') || ' ' || trim(v.natvoi) || ' ' || v.libvoi)
            ELSE ltrim(p.cconvo, '0') || p.dvoilib
    END ||
    '</td></tr>' ||
    '<tr><th>Urbaine</th> <td>' ||
    CASE
            WHEN p.gurbpa = 'U' THEN 'Oui'
            ELSE 'Non'
    END ||
    '</td></tr>' ||
'</table>'

FROM parcelle p
INNER JOIN geo_parcelle gp ON p.parcelle = gp.geo_parcelle
LEFT OUTER JOIN commune c ON p.ccocom = c.ccocom AND c.ccodep = p.ccodep
LEFT OUTER JOIN voie v ON v.voie = p.voie
WHERE 2>1
AND parcelle = '%s'
LIMIT 1
