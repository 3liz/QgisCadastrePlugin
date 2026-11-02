-- Description of the dependances (pevdependances): one row per dependance, several for a PEV
-- Parameter: {parcelle}, the identifier of the parcel, quoted by fetch_rows

SELECT
    pd.pev AS pev,
    pd.dnudes AS numero,
    cconad.cconad_lib AS nature,
    pd.dsudep AS surface,
    pd.dcimlc AS ponderation,
    pd.dcspdea AS situation_particuliere,
    pd.dmatgm AS murs, pd.dmatto AS toiture, pd.detent AS etat_entretien,
    pd.geaulc AS eau, pd.gelelc AS electricite, pd.gchclc AS chauffage,
    pd.dnbbai AS baignoires, pd.dnbdou AS douches, pd.dnblav AS lavabos, pd.dnbwc AS wc
FROM local00 l
JOIN local10 l10 ON l10.local00 = l.local00
JOIN pev ON pev.local10 = l10.local10
JOIN pevdependances pd ON pd.pev = pev.pev
LEFT JOIN cconad ON cconad.cconad = pd.cconad
WHERE l.parcelle = {parcelle}
ORDER BY pd.pev, pd.dnudes
