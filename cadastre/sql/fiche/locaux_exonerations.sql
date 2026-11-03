-- Exonerations of the PEV: one row per exoneration, several for a PEV.
-- The amounts are read in the integer columns rcexba2 and fcexba2, or in the text columns rcexba and fcexba
-- Parameter: {parcelle}, the identifier of the parcel, quoted by fetch_rows

SELECT
    px.pev AS pev,
    ccolloc.ccolloc_lib AS collectivite,
    gnextl.gnextl_lib AS nature,
    px.jandeb AS annee_debut,
    px.janimp AS annee_retour,
    px.pexb AS taux,
    Coalesce(Cast(px.fcexba2 AS text), NULLIF(trim(px.fcexba), '')) AS fraction_vl,
    Coalesce(Cast(px.rcexba2 AS text), NULLIF(trim(px.rcexba), '')) AS revenu
FROM local00 l
JOIN local10 l10 ON l10.local00 = l.local00
JOIN pev ON pev.local10 = l10.local10
JOIN pevexoneration px ON px.pev = pev.pev
LEFT JOIN ccolloc ON ccolloc.ccolloc = px.ccolloc
LEFT JOIN gnextl ON gnextl.gnextl = px.gnextl
WHERE l.parcelle = {parcelle}
ORDER BY px.pev, px.dnuexb
