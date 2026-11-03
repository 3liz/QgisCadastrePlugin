-- Subdivisions fiscales of the parcel: one row per subdivision
-- Parameter: {parcelle}, the identifier of the parcel, quoted by fetch_rows

SELECT
    s.ccosub AS lettre,
    cgrnum.cgrnum_lib AS groupe,
    dsgrpf.dsgrpf_lib AS sous_groupe,
    Coalesce(cnatsp.cnatsp_lib, s.cnatsp) AS nature,
    s.dclssf AS classe,
    s.dcntsf AS contenance,
    s.drcsuba AS revenu
FROM suf s
LEFT JOIN cgrnum ON cgrnum.cgrnum = s.cgrnum
LEFT JOIN dsgrpf ON dsgrpf.dsgrpf = s.dsgrpf
LEFT JOIN cnatsp ON cnatsp.cnatsp = s.cnatsp
WHERE s.parcelle = {parcelle}
ORDER BY s.ccosub
