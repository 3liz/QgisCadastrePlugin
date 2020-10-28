
SELECT p.annee, p.ccodep, p.ccodir, p.ccocom, c.libcom
FROM $schema"proprietaire" p
LEFT OUTER JOIN $schema"commune" c ON c.ccocom = p.ccocom AND c.ccodep = p.ccodep
WHERE 2>1
$and
LIMIT 1

