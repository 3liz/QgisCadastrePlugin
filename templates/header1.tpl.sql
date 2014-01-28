
SELECT p.annee, p.ccodep, p.ccodir, p.ccocom, c.libcom
FROM proprietaire p
LEFT OUTER JOIN commune c ON c.ccocom = p.ccocom AND c.ccodep = p.ccodep
WHERE 2>1
$and
LIMIT 1

