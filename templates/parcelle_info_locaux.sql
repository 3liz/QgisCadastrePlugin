SELECT

'<table class="table table-condensed table-striped" border=1 cellspacing=0 cellpadding=3 width="100p">' ||
    '<tr>' ||
        '<th>bat-ent-et-porte</th>' ||
        '<th>Invariant</th>' ||
        '<th>Type</th>' ||
        '<th>Nature</th>' ||
        '<th>Occupation</th>' ||
        '<th>Date acte</th>' ||
        '<th>Année construction</th>' ||
        '<th>Destinataire de l''avis</th>' ||
    '</tr>' ||
    string_agg(line, '') ||
'</table>'

FROM (
    SELECT
    '<tr>' ||
        '<td>' || (l.dnubat || '-' || l.descr || '-' || l.dniv || '-' || l.dpor) || '</td>' ||
        '<td>' || l.invar || '</td>' ||
        '<td>' || dteloc_lib || '</td>' ||
        '<td>' || cconlc_lib || '</td>' ||
        '<td>' || dnatlc_lib || '</td>' ||
        '<td>' || COALESCE(cast(l10.jdatat AS text), '') || '</td>' ||
        '<td>' || Coalesce(cast(l10.jannat AS text), '') || '</td>' ||
        '<td>' ||
            trim(coalesce(pr.dqualp, '')) || ' ' ||
            CASE WHEN trim(pr.dnomus) != trim(pr.dnomlp) THEN Coalesce( trim(pr.dnomus) || '/' || trim(pr.dprnus) || ', née ', '' ) ELSE '' END ||
            trim(coalesce(pr.ddenom, '')) ||
        '</td>' ||
    '</tr>'
    AS line
    FROM local00 l
    INNER JOIN local10 l10 ON l10.local00 = l.local00
    LEFT JOIN "dteloc" ON l10.dteloc = dteloc.dteloc
    LEFT JOIN "cconlc" ON l10.cconlc = cconlc.cconlc
    LEFT JOIN "dnatlc" ON l10.dnatlc = dnatlc.dnatlc
    LEFT JOIN proprietaire AS pr ON pr.comptecommunal = l10.comptecommunal AND pr.gdesip = '1'-- pr.dnulp = '01'
    WHERE 2>1 AND l.parcelle = '%s'
    ORDER BY l.dnubat, l.descr, l.dniv, l.dpor

) foo
