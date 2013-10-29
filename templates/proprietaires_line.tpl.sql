
SELECT Coalesce(ccodro_lib, '') || ' - ' || p.dnuper || ' - ' || trim(Coalesce(p.dqualp, '')) || ' ' || trim(Coalesce(p.ddenom, '')) || ' - ' ||trim(Coalesce(p.dlign3, '')) || ' / ' || trim(Coalesce(p.dlign4, '')) || trim(Coalesce(p.dlign5, '')) || ' ' || trim(Coalesce(p.dlign6, '')) ||
        CASE
          WHEN jdatnss IS NOT NULL
          THEN ' - Né(e) le ' || coalesce(to_char(jdatnss, 'dd/mm/YYYY'), '') || ' à ' || coalesce(p.dldnss, '')
          ELSE ''
        END
FROM proprietaire p
INNER JOIN ccodro ON ccodro.ccodro = p.ccodro
WHERE 2>1
$and

