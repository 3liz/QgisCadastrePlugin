-- Parties d'évaluation (PEV) of the locaux: one row per PEV, with its taxation (one per PEV)
-- Parameter: {parcelle}, the identifier of the parcel, quoted by fetch_rows

SELECT
    pev.pev AS pev,
    pev.local10 AS local10,
    pev.dnupev AS numero,
    ccoaff.ccoaff_lib AS affectation,
    pev.ccostb AS lettre_serie,
    pev.dcapec AS categorie,
    pev.dcetlc AS entretien,
    pev.dvlper AS valeur_locative_reference,
    pev.dvlpera AS valeur_locative,
    gnexpl.gnexpl_lib AS exoneration_permanente,
    pev.dnuref AS local_type,
    pev.dcsglca AS situation_generale,
    pev.dcsplca AS situation_particuliere,
    pt.co_vlbaia AS co_vlbaia, pt.co_bipevla AS co_bipevla,
    pt.gp_vlbaia AS gp_vlbaia, pt.gp_bipevla AS gp_bipevla,
    pt.tse_vlbaia AS tse_vlbaia, pt.tse_bipevla AS tse_bipevla,
    pt.de_vlbaia AS de_vlbaia, pt.de_bipevla AS de_bipevla
FROM local00 l
JOIN local10 l10 ON l10.local00 = l.local00
JOIN pev ON pev.local10 = l10.local10
LEFT JOIN pevtaxation pt ON pt.pev = pev.pev
LEFT JOIN ccoaff ON ccoaff.ccoaff = pev.ccoaff
LEFT JOIN gnexpl ON gnexpl.gnexpl = pev.gnexpl
WHERE l.parcelle = {parcelle}
ORDER BY pev.pev
