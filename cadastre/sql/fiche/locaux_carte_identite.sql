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

    -- Lots, numérateur, dénominateur
    string_agg(
        concat(
            'Lot ',
            (SELECT min(ll.dnulot) FROM lotslocaux ll WHERE ll.local00 = l.local00)::int, ' : ',
            (SELECT min(ll.dnumql) FROM lotslocaux ll WHERE ll.local00 = l.local00)::int, '/',
            (SELECT min(ll.ddenql) FROM lotslocaux ll WHERE ll.local00 = l.local00)::int
        ),
        '
'
    ) AS lots,

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

JOIN proprietaire pr ON pr.comptecommunal = l10.comptecommunal
    LEFT JOIN ccodro ON ccodro.ccodro = pr.ccodro
    LEFT JOIN ccodem ON ccodem.ccodem = pr.ccodem
LEFT JOIN dteloc ON dteloc.dteloc = l10.dteloc
LEFT JOIN cconlc ON cconlc.cconlc = l10.cconlc
LEFT JOIN ccoplc ON ccoplc.ccoplc = l10.ccoplc
WHERE l.parcelle = {parcelle}
GROUP BY
    "local10", nom_adresse_invariant_cle, demembrement_nature_occupation,
    batiment, entree, niveau, porte,
    surface
ORDER BY nom_adresse_invariant_cle, batiment, entree, niveau, porte
