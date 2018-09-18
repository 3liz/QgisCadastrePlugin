SELECT trim(
    '<b>Numéro: </b>' || p.dnuper ||
    '<br/><b>Nom: </b>' || trim(coalesce(p.dqualp, '')) || ' ' || trim(coalesce(p.ddenom, '')) ||
    '<br/><b>Adresse: </b>' || ltrim(trim(coalesce(p.dlign4, '')), '0') || trim(coalesce(p.dlign5, '')) || ' ' || trim(coalesce(p.dlign6, '')) ||
    '<br/><b>Date de naissance: </b>' || Coalesce( trim(cast(p.jdatnss AS text) ), '-') ||
    '<br/><b>Lieux de naissance: </b>' || coalesce(trim(p.dldnss), '-') ||
    '<br/><b>Code droit: </b>' || Coalesce(ccodro_lib, '') ||
    '<br/><b>Code démembrement: </b>' || Coalesce(ccodem_lib, '')
)
FROM proprietaire p
LEFT JOIN ccodro ON ccodro.ccodro = p.ccodro
LEFT JOIN ccodem ON ccodem.ccodem = p.ccodem
WHERE 2>1
AND comptecommunal = (
    SELECT comptecommunal FROM parcelle WHERE parcelle = '%s'
)
