-- Description of the PEV of the professional locaux, the surfaces of the older and newer formats
-- Parameter: {parcelle}, the identifier of the parcel, quoted by fetch_rows

SELECT
    po.pev AS pev,
    Coalesce(po.dsupot, po.vsupot) AS surface_ponderee,
    po.dsup1 AS surface_principale,
    po.dsup2 AS surface_secondaire_couverte,
    po.dsup3 AS surface_secondaire_non_couverte,
    po.dsupk1 AS stationnement_couvert,
    po.dsupk2 AS stationnement_non_couvert,
    po.vsurzt AS surface_reelle
FROM local00 l
JOIN local10 l10 ON l10.local00 = l.local00
JOIN pev ON pev.local10 = l10.local10
JOIN pevprofessionnelle po ON po.pev = pev.pev
WHERE l.parcelle = {parcelle}
ORDER BY po.pev
