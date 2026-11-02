-- Description of the PEV of the habitations (pevprincipale), with the 4 dependances incorporated
-- Parameter: {parcelle}, the identifier of the parcel, quoted by fetch_rows

SELECT
    pp.pev AS pev,
    pp.dnbpdc AS pieces, pp.dnbppr AS pieces_principales, pp.dsupdc AS surface_pieces,
    pp.dnbsam AS salles_a_manger, pp.dnbcha AS chambres,
    pp.dnbcu8 AS cuisines_moins_9, pp.dnbcu9 AS cuisines_plus_9,
    pp.dnbsea AS salles_eau, pp.dnbann AS pieces_annexes,
    pp.dmatgm AS murs, pp.dmatto AS toiture, pp.detent AS etat_entretien,
    pp.geaulc AS eau, pp.gelelc AS electricite, pp.ggazlc AS gaz, pp.gchclc AS chauffage,
    pp.dnbbai AS baignoires, pp.dnbdou AS douches, pp.dnblav AS lavabos, pp.dnbwc AS wc,
    c1.cconad_lib AS dep1, pp.dep1_dsueic AS dep1_surface,
    c2.cconad_lib AS dep2, pp.dep2_dsueic AS dep2_surface,
    c3.cconad_lib AS dep3, pp.dep3_dsueic AS dep3_surface,
    c4.cconad_lib AS dep4, pp.dep4_dsueic AS dep4_surface
FROM local00 l
JOIN local10 l10 ON l10.local00 = l.local00
JOIN pev ON pev.local10 = l10.local10
JOIN pevprincipale pp ON pp.pev = pev.pev
LEFT JOIN cconad c1 ON c1.cconad = pp.dep1_cconad
LEFT JOIN cconad c2 ON c2.cconad = pp.dep2_cconad
LEFT JOIN cconad c3 ON c3.cconad = pp.dep3_cconad
LEFT JOIN cconad c4 ON c4.cconad = pp.dep4_cconad
WHERE l.parcelle = {parcelle}
ORDER BY pp.pev, pp.dnudes
