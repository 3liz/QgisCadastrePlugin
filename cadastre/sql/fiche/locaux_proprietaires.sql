-- Owners of the locaux: one row per owner of the compte communal of each local.
-- gdesip = 1 for the owner receiving the tax notice (destinataire de l'avis)
-- Parameter: {parcelle}, the identifier of the parcel, quoted by fetch_rows

SELECT
    l10.local10 AS local10,
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
    ccodem.ccodem_lib AS demembrement,
    pr.gdesip AS destinataire
FROM local00 l
JOIN local10 l10 ON l10.local00 = l.local00
JOIN proprietaire pr ON pr.comptecommunal = l10.comptecommunal
LEFT JOIN ccodro ON ccodro.ccodro = pr.ccodro
LEFT JOIN ccodem ON ccodem.ccodem = pr.ccodem
WHERE l.parcelle = {parcelle}
ORDER BY l10.local10, pr.dnulp, pr.dnuper
