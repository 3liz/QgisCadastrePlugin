SELECT --p.parcelle,
p.ccosec AS section, ltrim(p.dnupla, '0') AS ndeplan,
ltrim(p.dnvoiri, '0') || p.dindic AS ndevoirie,

CASE WHEN v.libvoi IS NOT NULL THEN v.natvoi || v.libvoi ELSE p.cconvo || p.dvoilib END AS adresse,
p.ccoriv AS coderivoli,
p.dparpi AS nparcprim, p.gparnf AS fpdp, s.ccostn AS star, s.ccosub AS suf, s.cgrnum || '/' || s.dsgrpf AS grssgr, s.dclssf AS cl, s.cnatsp AS natcult,
CASE WHEN length(Cast(s.dcntsf AS text)) > 4 THEN substring(Cast(s.dcntsf AS text), 0, length(Cast(s.dcntsf AS text))-3) ELSE '0' END AS ha_contenance,
CASE WHEN length(Cast(s.dcntsf AS text)) > 2 THEN substring(Cast(s.dcntsf AS text), length(Cast(s.dcntsf AS text))-3, 2) ELSE '0' END AS a_contenance,
CASE WHEN length(Cast(s.dcntsf AS text)) > 0 THEN substring(Cast(s.dcntsf AS text), length(Cast(s.dcntsf AS text))-1, 2) ELSE '0' END AS ca_contenance,
s.drcsuba AS revenucadastral, se.ccolloc AS coll, se.gnexts AS natexo, se.jfinex AS anret,
--se.fcexn AS fractionrcexo,
round(Cast(s.drcsuba * Cast(se.pexn / 100 AS numeric(10,2)) / 100 AS numeric) , 2) as fractionrcexo,
Cast(se.pexn / 100 AS numeric(10,2)) AS pourcentageexo, '' AS tc,
p.dreflf AS lff

FROM parcelle p
INNER JOIN suf s ON p.parcelle = s.parcelle
LEFT OUTER JOIN voie v ON v.voie = p.voie
LEFT JOIN sufexoneration se ON s.suf = se.suf
WHERE 2>1
$and
ORDER BY p.parcelle, s.suf
