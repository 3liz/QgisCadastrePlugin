-- Locaux of the carte d'identité de la parcelle: one row per local and per owner.
-- The rows of a local are grouped in a single line of the table by carte_identite.load_locaux.
-- Parameter: {parcelle}, the identifier of the parcel, quoted by fetch_rows

SELECT
    -- code du local
    l10.local10 AS local10,
    -- Number of the owner in the compte communal, to sort the owners of a local
    pr.dnulp AS numero,
    -- Name of the owner: civility, usage and first name, birth name ("née") if it is different, denomination
    trim(
        Coalesce(trim(pr.dqualp) || ' ', '')
        || CASE
            WHEN trim(pr.dnomus) != trim(pr.dnomlp)
            THEN Coalesce(trim(pr.dnomus) || '/' || trim(pr.dprnus) || ', née ', '')
            ELSE ''
        END
        || Coalesce(trim(pr.ddenom), '')
    ) AS nom,
    -- Address of the owner: the 4 lines, without the leading zeros of the number
    replace(trim(
        Coalesce(trim(pr.dlign3) || ' ', '')
        || Coalesce(ltrim(trim(pr.dlign4), '0') || ' ', '')
        || Coalesce(trim(pr.dlign5) || ' ', '')
        || Coalesce(trim(pr.dlign6), '')
    ), '  ', ' ') AS adresse,
    -- invariant, clé
    l.invar AS invariant,
    l.cleinvar AS cle,

    -- démembrement and occupation (right) of the owner, nature du local
    ccodem.ccodem_lib AS demembrement,
    cconlc.cconlc_lib AS nature,
    ccodro.ccodro_lib AS occupation,

    -- Lot, numérateur, dénominateur, empty when the local is not in a lot.
    -- CAST and || instead of ::int and concat, which do not exist in Spatialite
    CASE
        WHEN ll.lot IS NOT NULL
        THEN 'Lot ' || Coalesce(CAST(CAST(ll.lot AS integer) AS text), '')
            || ' : ' || Coalesce(CAST(CAST(ll.numerateur AS integer) AS text), '')
            || '/' || Coalesce(CAST(CAST(ll.denominateur AS integer) AS text), '')
    END AS lots,

    -- Surface pièces
    s.surface AS surface,

    -- batiment, entree, niveau, porte,
    l.dnubat AS batiment,
    l.descr AS entree,
    l.dniv AS niveau,
    l.dpor AS porte
FROM local00 l
JOIN local10 l10 ON l10.local00 = l.local00
-- Lots of the locaux of the parcel only: a subquery correlated to each local would read
-- the whole table lotslocaux for each local when it has no index on local00.
-- IN and not a join: without this index, SQLite would also read the table for each local
LEFT JOIN (
    SELECT
        lll.local00 AS local00,
        min(lll.dnulot) AS lot,
        min(lll.dnumql) AS numerateur,
        min(lll.ddenql) AS denominateur
    FROM lotslocaux lll
    WHERE lll.local00 IN (SELECT ll0.local00 FROM local00 ll0 WHERE ll0.parcelle = {parcelle})
    GROUP BY lll.local00
) ll ON ll.local00 = l.local00
-- Surface of the rooms of the locaux of the parcel only, read once: a subquery correlated to each
-- local would read the whole table pev for each local when it has no index on local10.
-- IN and not a join: without this index, SQLite would read pevprincipale for each local
LEFT JOIN (
    SELECT
        spev.local10 AS local10,
        sum(spp.dsupdc) AS surface
    FROM pev spev
    JOIN pevprincipale spp ON spp.pev = spev.pev
    WHERE spev.local10 IN (
        SELECT sl10.local10
        FROM local10 sl10
        JOIN local00 sl0 ON sl0.local00 = sl10.local00
        WHERE sl0.parcelle = {parcelle}
    )
    GROUP BY spev.local10
) s ON s.local10 = l10.local10
-- A local without owner is kept
LEFT JOIN proprietaire pr ON pr.comptecommunal = l10.comptecommunal
LEFT JOIN ccodro ON ccodro.ccodro = pr.ccodro
LEFT JOIN ccodem ON ccodem.ccodem = pr.ccodem
LEFT JOIN cconlc ON cconlc.cconlc = l10.cconlc
WHERE l.parcelle = {parcelle}
-- The locaux are sorted by the name of their first owner. load_locaux sorts the owners of a local by their number
ORDER BY nom, batiment, entree, niveau, porte, pr.dnulp, pr.dnuper
