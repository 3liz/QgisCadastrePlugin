SELECT --p.parcelle,
p.ccosec AS section, p.dnupla AS ndeplan,
p.dnvoiri || p.dindic AS ndevoirie,
v.natvoi || v.libvoi AS adresse,
p.ccoriv AS coderivoli,
p.dparpi AS nparcprim, p.gparnf AS fpdp, s.ccostn AS star, s.ccosub AS suf, s.cgrnum || '/' || s.dsgrpf AS grssgr, s.dclssf AS cl, s.cnatsp AS natcult,
s.dcntsf AS contenance, s.drcsuba AS revenucadastral, se.ccolloc AS coll, se.gnexts AS natexo, se.jfinex AS anret, se.fcexn AS fractionrcexo, se.pexn AS pourcentageexo, '' AS tc,
p.dreflf AS lff

FROM parcelle p
INNER JOIN suf s ON p.parcelle = s.parcelle
INNER JOIN voie v ON v.voie = p.voie
LEFT JOIN sufexoneration se ON s.suf = se.suf
WHERE 2>1
$and
ORDER BY p.parcelle, s.suf
