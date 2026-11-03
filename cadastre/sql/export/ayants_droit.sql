-- Ayants droit of a list of parcelles: one row per parcelle and owner, a parcelle without owner has one row.
-- Only the parcelles with a geometry are exported (parcelle_info), like in Lizmap.
-- Parameters:
-- * {parcelles}, the identifiers of the parcelles, quoted and separated by commas
-- * {naissance}, TRUE if the user can see the birth data of the owners, otherwise FALSE

SELECT
    p.parcelle AS parcelle,
    c.libcom AS commune,
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
LEFT JOIN proprietaire pr ON pr.comptecommunal = p.comptecommunal
LEFT JOIN commune c ON c.commune = pr.ccodep || pr.ccodir || pr.ccocom
LEFT JOIN ccodro ON ccodro.ccodro = pr.ccodro
LEFT JOIN ccodem ON ccodem.ccodem = pr.ccodem
WHERE p.parcelle IN ({parcelles})
ORDER BY p.parcelle, pr.dnulp, pr.dnuper
