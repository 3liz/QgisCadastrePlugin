SELECT

    '<table class="table table-condensed table-striped" border=1 cellspacing=0 cellpadding=3 width="100p">' ||
    '<tr>' ||
        '<th>Id Lot</th>' ||
        '<th>Compte proprietaire</th>' ||
        '<th>Etat civil</th>' ||
        '<th>Adresse</th>' ||
        '<th>Date de naissance</th>' ||
        '<th>Ville</th>' ||
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
        '<td>' || trim(coalesce(proprietaire.dqualp, '')) || ' ' || trim(coalesce(proprietaire.ddenom, '')) || '</td>' ||
        '<td>' || ltrim(trim(coalesce(proprietaire.dlign3, '')), '0') || trim(coalesce(proprietaire.dlign4, '')) || ' ' || trim(coalesce(proprietaire.dlign5, '')) || '</td>' ||
        '<td>' || coalesce( trim(cast(proprietaire.jdatnss AS text) ), '-') || '</td>' ||
        '<td>' || coalesce(trim(proprietaire.dlign6), '-') || '</td>' ||
        '<td>' || coalesce(proprietaire.ccodem, '') || '</td>' ||
        '<td>' || coalesce(proprietaire.ccodro, '') || '</td>' ||
    '</tr>'
    AS line
    FROM  lots l
    LEFT JOIN proprietaire ON proprietaire.comptecommunal = l.comptecommunal
     WHERE l.parcelle = '%s'
    ORDER BY l.dnulot
) foo
