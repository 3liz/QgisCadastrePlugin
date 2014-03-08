SELECT --p.parcelle,

CASE WHEN length(Cast(sum(s.dcntsf) AS text)) > 4 THEN substring(Cast(sum(s.dcntsf) AS text), 0, length(Cast(sum(s.dcntsf) AS text))-3) ELSE '0' END AS sum_ha_contenance,
CASE WHEN length(Cast(sum(s.dcntsf) AS text)) > 2 THEN substring(Cast(sum(s.dcntsf) AS text), length(Cast(sum(s.dcntsf) AS text))-3, 2) ELSE '0' END AS sum_a_contenance,
CASE WHEN length(Cast(sum(s.dcntsf) AS text)) > 0 THEN substring(Cast(sum(s.dcntsf) AS text), length(Cast(sum(s.dcntsf) AS text))-1, 2) ELSE '0' END AS sum_ca_contenance,

sum(s.drcsuba) AS sum_drcsuba

FROM parcelle p
INNER JOIN suf s ON p.parcelle = s.parcelle
--LEFT JOIN sufexoneration se ON s.suf = se.suf
WHERE 2>1
$and

