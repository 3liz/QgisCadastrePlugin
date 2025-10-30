SELECT

    '<table class="table table-condensed table-striped" border=1 cellspacing=0 cellpadding=3 width="100p">' ||
    '<tr>' ||
        '<th>Id Lot</th>' ||
        '<th>Compte proprietaire</th>' ||
        '<th>Etat civil</th>' ||
        '<th>Adresse</th>' ||
        CASE WHEN {not_for_third_part} THEN '<th>Date de naissance</th>' ELSE '' END ||
        '<th>Code indivision</th>' ||
        '<th>Code droits</th>' ||
    '</tr>' ||
    string_agg(line, '') ||
    '</table>'

FROM (
    SELECT
    '<tr>' ||
        '<td>' || l.dnulot || '</td>' ||
        '<td>' || l.comptecommunal || '</td>' ||
        '<td>' || trim(coalesce(p.dqualp, '')) || ' ' || trim(coalesce(p.ddenom, '')) || '</td>' ||
        '<td>' || replace(trim(trim(coalesce(p.dlign3, '')) || ' ' || ltrim(trim(coalesce(p.dlign4, '')), '0') || ' ' || trim(coalesce(p.dlign5, '')) || ' ' || trim(coalesce(p.dlign6, ''))), '  ', ' ') || '</td>' ||
        CASE WHEN {not_for_third_part} THEN '<td>' || Coalesce( trim(cast(p.jdatnss AS text) ), '-') || '</td>' ELSE '' END ||
        '<td>' || coalesce(p.ccodem, '') || '</td>' ||
        '<td>' || coalesce(p.ccodro, '') || '</td>' ||
    '</tr>'
    AS line
    FROM  lots l
    LEFT JOIN proprietaire p ON p.comptecommunal = l.comptecommunal
     WHERE l.parcelle = '{parcelle_id}'
    ORDER BY l.dnulot
) foo
