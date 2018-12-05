SELECT

'<table class="table table-condensed table-striped" border=1 cellspacing=0 cellpadding=3 width="100p">' ||
    '<tr>' ||
        '<th>Subdivision</th>' ||
        '<th>Nature</th>' ||
        '<th>Libellé</th>' ||
        '<th>Collectivité</th>' ||
        '<th>Pourcentage</th>' ||
        '<th>Montant</th>' ||
    '</tr>' ||
    string_agg(line, '') ||
'</table>'

FROM (
    SELECT

    '<tr>' ||
        '<td>' || s.ccosub || '</td>' ||
        '<td>' || se.gnexts || '</td>' ||
        '<td>' || gnexts_lib || '</td>' ||
        '<td>' || ccolloc_lib || '</td>' ||
        '<td>' || Cast(se.pexn / 100 AS numeric(10,2)) || '</td>' ||
        '<td>' || round(Cast(s.drcsuba * Cast(se.pexn / 100 AS numeric(10,2)) / 100 AS numeric) , 2) || '</td>' ||
    '</tr>'
    AS line

    FROM suf s
    LEFT JOIN sufexoneration se ON s.suf = se.suf
    LEFT JOIN "gnexts" ON se.gnexts = trim(gnexts.gnexts)
    LEFT JOIN "ccolloc" ON se.ccolloc = ccolloc.ccolloc
    WHERE 2>1 AND s.parcelle = '%s' AND s.suf = '%s'
) foo
