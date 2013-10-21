
SELECT ccodro_lib || ' - ' || p.dnuper || ' - ' || trim(p.dqualp) || ' ' || trim(p.ddenom) || ' - ' ||trim(p.dlign3) || ' / ' || trim(regexp_replace(p.dlign4, '^0+', '')) || trim(p.dlign5) || ' ' || trim(p.dlign6) || ' - Né(e) le ' || to_char(jdatnss, 'dd/mm/YYYY') || ' à ' || p.dldnss
FROM proprietaire p
INNER JOIN ccodro ON ccodro.ccodro = p.ccodro
WHERE 2>1
$and

