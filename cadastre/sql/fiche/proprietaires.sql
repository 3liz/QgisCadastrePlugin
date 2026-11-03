-- Owners of the compte communal of the parcel: one row per owner
-- Parameter: {parcelle}, the identifier of the parcel, quoted by fetch_rows

SELECT
    pr.dnulp AS numero,
    pr.dnuper AS code,
    -- Name: civility, usage and first name, birth name ("née") if it is different, denomination
    trim(
        Coalesce(trim(pr.dqualp) || ' ', '')
        || CASE
            WHEN trim(pr.dnomus) != trim(pr.dnomlp)
            THEN Coalesce(trim(pr.dnomus) || '/' || trim(pr.dprnus) || ', née ', '')
            ELSE ''
        END
        || Coalesce(trim(pr.ddenom), '')
    ) AS nom,
    -- Address: the 4 lines, without the leading zeros of the number
    trim(
        Coalesce(trim(pr.dlign3) || ' ', '')
        || Coalesce(ltrim(trim(pr.dlign4), '0') || ' ', '')
        || Coalesce(trim(pr.dlign5) || ' ', '')
        || Coalesce(trim(pr.dlign6), '')
    ) AS adresse,
    pr.jdatnss AS date_naissance,
    pr.dldnss AS lieu_naissance,
    ccodro.ccodro_lib AS droit,
    ccodem.ccodem_lib AS demembrement
FROM parcelle p
JOIN proprietaire pr ON pr.comptecommunal = p.comptecommunal
LEFT JOIN ccodro ON ccodro.ccodro = pr.ccodro
LEFT JOIN ccodem ON ccodem.ccodem = pr.ccodem
WHERE p.parcelle = {parcelle}
ORDER BY pr.dnulp, pr.dnuper
