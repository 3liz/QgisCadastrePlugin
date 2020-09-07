SELECT

    '<table class="table table-condensed table-striped" border=1 cellspacing=0 cellpadding=3 width="100p">' ||
    '<tr>' ||
        '<th>Numéro</th>' ||
        '<th>Code</th>' ||
        '<th>Nom</th>' ||
        '<th>Adresse</th>' ||
        '<th>Date de naissance</th>' ||
        '<th>Lieux de naissance</th>' ||
        '<th>Code droit</th>' ||
        '<th>Code démembrement</th>' ||
    '</tr>' ||
    string_agg(line, '') ||
    '</table>'

FROM (
    SELECT

    '<tr>' ||
        '<td>' || p.dnulp || '</td>' ||
        '<td>' || p.dnuper || '</td>' ||
        '<td>' ||
            trim(coalesce(p.dqualp, '')) || ' ' ||
            CASE WHEN trim(p.dnomus) != trim(p.dnomlp) THEN Coalesce( trim(p.dnomus) || '/' || trim(p.dprnus) || ', née ', '' ) ELSE '' END ||
            trim(coalesce(p.ddenom, '')) ||
        '</td>' ||
        '<td>' || ltrim(trim(coalesce(p.dlign4, '')), '0') || trim(coalesce(p.dlign5, '')) || ' ' || trim(coalesce(p.dlign6, '')) || '</td>' ||
        '<td>' || Coalesce( trim(cast(p.jdatnss AS text) ), '-') || '</td>' ||
        '<td>' || coalesce(trim(p.dldnss), '-') || '</td>' ||
        '<td>' || Coalesce(ccodro_lib, '') || '</td>' ||
        '<td>' || Coalesce(ccodem_lib, '') || '</td>' ||
    '</tr>'
    AS line
    FROM proprietaire p
    LEFT JOIN ccodro ON ccodro.ccodro = p.ccodro
    LEFT JOIN ccodem ON ccodem.ccodem = p.ccodem
    WHERE 2>1
    AND comptecommunal = (
        SELECT comptecommunal FROM parcelle WHERE parcelle = '%s'
    )
    ORDER BY p.dnulp
) foo
