-- SQL pour récupérer les informations nécessaires pour l'affichage des lots
-- dans la fiche "Carte d'identité"
SELECT
    -- code du local
    l10.local10 AS local10,
    -- nom propriétaire / adresse / invariant / clé
    concat(
        -- nom
        trim(
            Coalesce(trim(pr.dqualp) || ' ', '')
            || CASE
                WHEN trim(pr.dnomus) != trim(pr.dnomlp)
                THEN Coalesce(trim(pr.dnomus) || '/' || trim(pr.dprnus) || ', née ', '')
                ELSE ''
            END
            || Coalesce(trim(pr.ddenom), '')
        ), '
',
        -- adresse
        replace(trim(
            Coalesce(trim(pr.dlign3) || ' ', '')
            || Coalesce(ltrim(trim(pr.dlign4), '0') || ' ', '')
            || Coalesce(trim(pr.dlign5) || ' ', '')
            || Coalesce(trim(pr.dlign6), '')
        ), '  ', ' '), '
',
        -- invariant
        l.invar, ' ',
        -- clé
        l.cleinvar
    ) AS nom_adresse_invariant_cle,

    -- démembrement, nature du local, occupation
    concat(
        Coalesce(ccodem.ccodem_lib, '-'), '
',
        cconlc.cconlc_lib, '
',
        ccodro.ccodro_lib
    ) AS demembrement_nature_occupation,

    -- Lot, numérateur, dénominateur, empty when the local is not in a lot
    CASE
        WHEN ll.lot IS NOT NULL
        THEN concat('Lot ', ll.lot::int, ' : ', ll.numerateur::int, '/', ll.denominateur::int)
    END AS lots,

    -- Surface pièces
    (
        SELECT sum(pp.dsupdc) FROM pev JOIN pevprincipale pp ON pp.pev = pev.pev
        WHERE pev.local10 = l10.local10
    ) AS surface,

    -- batiment, entree, niveau, porte,
    l.dnubat AS batiment,
    l.descr AS entree,
    l.dniv AS niveau,
    l.dpor AS porte
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

JOIN proprietaire pr ON pr.comptecommunal = l10.comptecommunal
    LEFT JOIN ccodro ON ccodro.ccodro = pr.ccodro
    LEFT JOIN ccodem ON ccodem.ccodem = pr.ccodem
LEFT JOIN dteloc ON dteloc.dteloc = l10.dteloc
LEFT JOIN cconlc ON cconlc.cconlc = l10.cconlc
LEFT JOIN ccoplc ON ccoplc.ccoplc = l10.ccoplc
WHERE l.parcelle = {parcelle}
GROUP BY
    "local10", nom_adresse_invariant_cle, demembrement_nature_occupation,
    lots, batiment, entree, niveau, porte,
    surface
ORDER BY nom_adresse_invariant_cle, batiment, entree, niveau, porte
