-- Locaux of the parcel: one row per local, with its address and its description
-- Parameter: {parcelle}, the identifier of the parcel, quoted by fetch_rows

SELECT
    l10.local10 AS local10,
    l.invar AS invariant,
    l.cleinvar AS cle,
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
    l10.dnbniv AS niveaux,
    -- Lot of a copropriété and its share, surface of the rooms of the habitations: carte d'identité
    ll.lot AS lot,
    ll.numerateur AS numerateur,
    ll.denominateur AS denominateur,
    (
        SELECT sum(pp.dsupdc) FROM pev JOIN pevprincipale pp ON pp.pev = pev.pev
        WHERE pev.local10 = l10.local10
    ) AS surface
FROM local00 l
JOIN local10 l10 ON l10.local00 = l.local00
-- Lots of the locaux of the parcel only: a subquery correlated to each local would read
-- the whole table lotslocaux for each local when it has no index on local00
LEFT JOIN (
    SELECT
        lll.local00 AS local00,
        min(lll.dnulot) AS lot,
        min(lll.dnumql) AS numerateur,
        min(lll.ddenql) AS denominateur
    FROM lotslocaux lll
    JOIN local00 ll0 ON ll0.local00 = lll.local00
    WHERE ll0.parcelle = {parcelle}
    GROUP BY lll.local00
) ll ON ll.local00 = l.local00
LEFT JOIN voie v
    ON SUBSTR(l.voie, 1, 6) || SUBSTR(l.voie, 12, 4) = SUBSTR(v.voie, 1, 6) || SUBSTR(v.voie, 12, 4)
LEFT JOIN dteloc ON dteloc.dteloc = l10.dteloc
LEFT JOIN cconlc ON cconlc.cconlc = l10.cconlc
LEFT JOIN ccoplc ON ccoplc.ccoplc = l10.ccoplc
WHERE l.parcelle = {parcelle}
ORDER BY l.dnubat, l.descr, l.dniv, l.dpor, l.invar, l.cleinvar
