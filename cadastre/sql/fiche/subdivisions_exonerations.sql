-- Exonerations of the subdivisions fiscales: one row per exoneration, 4 at most per subdivision
-- Parameter: {parcelle}, the identifier of the parcel, quoted by fetch_rows

SELECT
    s.ccosub AS lettre,
    ccolloc.ccolloc_lib AS collectivite,
    Coalesce(gnexts.gnexts_lib, se.gnexts) AS nature,
    se.jandeb AS annee_debut,
    se.jfinex AS annee_retour,
    se.pexn AS taux,
    se.rcexnba AS revenu
FROM suf s
JOIN sufexoneration se ON se.suf = s.suf
LEFT JOIN gnexts ON trim(gnexts.gnexts) = se.gnexts
LEFT JOIN ccolloc ON ccolloc.ccolloc = se.ccolloc
WHERE s.parcelle = {parcelle}
ORDER BY s.ccosub, se.rnuexn
