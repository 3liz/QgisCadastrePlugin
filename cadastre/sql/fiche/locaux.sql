-- Locaux of the parcel: one row per local, with its address and its description
-- Parameter: {parcelle}, the identifier of the parcel, quoted by fetch_rows

SELECT
    l10.local10 AS local10,
    l.invar AS invariant,
    l.dnubat AS batiment,
    l.descr AS entree,
    l.dniv AS niveau,
    l.dpor AS porte,
    Coalesce(ltrim(l.dnvoiri, '0'), '') || Coalesce(l.dindic, '') AS numero_voirie,
    CASE
        WHEN v.libvoi IS NOT NULL THEN Coalesce(v.natvoi || ' ', '') || v.libvoi
        ELSE l.dvoilib
    END AS voie,
    l10.comptecommunal AS comptecommunal,
    l10.jdatat AS date_acte,
    dteloc.dteloc_lib AS type,
    cconlc.cconlc_lib AS nature,
    ccoplc.ccoplc_lib AS construction,
    l10.jannat AS annee_construction,
    l10.dnbniv AS niveaux
FROM local00 l
JOIN local10 l10 ON l10.local00 = l.local00
LEFT JOIN voie v
    ON SUBSTR(l.voie, 1, 6) || SUBSTR(l.voie, 12, 4) = SUBSTR(v.voie, 1, 6) || SUBSTR(v.voie, 12, 4)
LEFT JOIN dteloc ON dteloc.dteloc = l10.dteloc
LEFT JOIN cconlc ON cconlc.cconlc = l10.cconlc
LEFT JOIN ccoplc ON ccoplc.ccoplc = l10.ccoplc
WHERE l.parcelle = {parcelle}
ORDER BY l.dnubat, l.descr, l.dniv, l.dpor, l.invar
