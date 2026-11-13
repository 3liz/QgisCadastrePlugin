-- Locaux of a list of parcelles: one row per local and owner, a local without owner has one row.
-- Only the parcelles with a geometry are exported (parcelle_info), like in Lizmap.
-- The lot, the surface of the rooms and the category of the local are not used by the CSV exports,
-- but by the carte d'identité de la parcelle. A local has several PEV, hence the sum and the minimum.
-- Parameters:
-- * {parcelles}, the identifiers of the parcelles, quoted and separated by commas
-- * {naissance}, TRUE if the user can see the birth data of the owners, otherwise FALSE

SELECT
    p.parcelle AS parcelle,
    l.local00 AS local00,
    l.invar AS invar,
    l.cleinvar AS cleinvar,
    l.dnubat AS dnubat,
    l.descr AS descr,
    l.dniv AS dniv,
    l.dpor AS dpor,
    l.dnvoiri AS dnvoiri,
    l.dindic AS dindic,
    v.natvoi AS natvoi,
    v.libvoi AS libvoi,
    p.cconvo AS cconvo,
    p.dvoilib AS dvoilib,
    l10.local10 AS local10,
    l10.ccodep AS ccodep,
    l10.ccocom AS ccocom,
    l10.dnupro AS dnupro,
    l10.dteloc AS dteloc,
    dteloc.dteloc_lib AS dteloc_lib,
    l10.cconlc AS cconlc,
    cconlc.cconlc_lib AS cconlc_lib,
    l10.ccoplc AS ccoplc,
    ccoplc.ccoplc_lib AS ccoplc_lib,
    l10.jannat AS jannat,
    l10.dnbniv AS dnbniv,
    l10.dnatlc AS dnatlc,
    dnatlc.dnatlc_lib AS dnatlc_lib,
    ll.dnulot AS dnulot,
    ll.dnumql AS dnumql,
    ll.ddenql AS ddenql,
    s.dsupdc AS dsupdc,
    s.dcapec AS dcapec,
    pr.comptecommunal AS comptecommunal,
    pr.dnulp AS dnulp,
    pr.dnuper AS dnuper,
    pr.dqualp AS dqualp,
    pr.dnomus AS dnomus,
    pr.dprnus AS dprnus,
    pr.dnomlp AS dnomlp,
    pr.ddenom AS ddenom,
    pr.dlign3 AS dlign3,
    pr.dlign4 AS dlign4,
    pr.dlign5 AS dlign5,
    pr.dlign6 AS dlign6,
    pr.ccopos AS ccopos,
    CASE WHEN {naissance} THEN pr.jdatnss END AS jdatnss,
    CASE WHEN {naissance} THEN pr.dldnss END AS dldnss,
    pr.ccodro AS ccodro,
    ccodro.ccodro_lib AS ccodro_lib,
    pr.ccodem AS ccodem,
    ccodem.ccodem_lib AS ccodem_lib
FROM parcelle p
JOIN parcelle_info gp ON gp.geo_parcelle = p.parcelle
JOIN local00 l ON l.parcelle = p.parcelle
JOIN local10 l10 ON l10.local00 = l.local00
-- Lots of the locaux of the parcelles only: a subquery correlated to each local would read
-- the whole table lotslocaux for each local when it has no index on local00.
-- IN and not a join: without this index, SQLite would also read the table for each local
LEFT JOIN (
    SELECT
        lll.local00 AS local00,
        min(lll.dnulot) AS dnulot,
        min(lll.dnumql) AS dnumql,
        min(lll.ddenql) AS ddenql
    FROM lotslocaux lll
    WHERE lll.local00 IN (SELECT ll0.local00 FROM local00 ll0 WHERE ll0.parcelle IN ({parcelles}))
    GROUP BY lll.local00
) ll ON ll.local00 = l.local00
-- Surface of the rooms and category of the locaux of the parcelles only, read once: a subquery
-- correlated to each local would read the whole table pev for each local when it has no index on local10.
-- IN and not a join: without this index, SQLite would read pevprincipale for each local
-- LEFT JOIN on pevprincipale: the category is given by all the PEV, the surface by those of the habitations
LEFT JOIN (
    SELECT
        spev.local10 AS local10,
        sum(spp.dsupdc) AS dsupdc,
        min(spev.dcapec) AS dcapec
    FROM pev spev
    LEFT JOIN pevprincipale spp ON spp.pev = spev.pev
    WHERE spev.local10 IN (
        SELECT sl10.local10
        FROM local10 sl10
        JOIN local00 sl0 ON sl0.local00 = sl10.local00
        WHERE sl0.parcelle IN ({parcelles})
    )
    GROUP BY spev.local10
) s ON s.local10 = l10.local10
LEFT JOIN voie v
    ON SUBSTR(l.voie, 1, 6) || SUBSTR(l.voie, 12, 4) = SUBSTR(v.voie, 1, 6) || SUBSTR(v.voie, 12, 4)
LEFT JOIN dteloc ON dteloc.dteloc = l10.dteloc
LEFT JOIN cconlc ON cconlc.cconlc = l10.cconlc
LEFT JOIN ccoplc ON ccoplc.ccoplc = l10.ccoplc
LEFT JOIN dnatlc ON dnatlc.dnatlc = l10.dnatlc
LEFT JOIN proprietaire pr ON pr.comptecommunal = l10.comptecommunal
LEFT JOIN ccodro ON ccodro.ccodro = pr.ccodro
LEFT JOIN ccodem ON ccodem.ccodem = pr.ccodem
WHERE p.parcelle IN ({parcelles})
ORDER BY p.parcelle, l.dnubat, l.descr, l.dniv, l.dpor, l.invar, pr.dnulp, pr.dnuper
