
SELECT ccodro_lib || ' ' || p.dnuper || ' ' || trim(p.dqualp) || ' ' || trim(p.ddenom) || ' ' ||trim(p.dlign3) || ' ' || trim(p.dlign4) || trim(p.dlign5) || ' ' || trim(p.dlign6) || '@'
FROM proprietaire p
INNER JOIN ccodro ON ccodro.ccodro = p.ccodro
WHERE 2>1
$and

