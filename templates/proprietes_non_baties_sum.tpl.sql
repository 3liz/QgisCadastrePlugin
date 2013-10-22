SELECT --p.parcelle,

sum(s.drcsuba) AS drcsuba

FROM parcelle p
INNER JOIN suf s ON p.parcelle = s.parcelle
LEFT JOIN sufexoneration se ON s.suf = se.suf
WHERE 2>1
$and

