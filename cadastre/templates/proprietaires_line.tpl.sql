
SELECT Coalesce(ccodro_lib, '') || ' - ' || p.dnuper || ' - ' || trim(Coalesce(p.dqualp, '')) || ' ' || trim(Coalesce(p.ddenom, '')) AS mainprop,
CASE WHEN epxnee = 'NEE' THEN 'EP ' || trim(Coalesce(dnomlp, '')) || ' ' || trim(Coalesce(dprnlp, '')) ELSE '' END AS epousede,
trim(Coalesce(p.dlign3, '')) || ' / ' || ltrim(trim(Coalesce(p.dlign4, '')), '0') || trim(Coalesce(p.dlign5, '')) || ' ' || trim(Coalesce(p.dlign6, '')) AS adrprop,
CASE
  WHEN jdatnss IS NOT NULL
  THEN ' Né(e) le ' || jdatnss || ' à ' || coalesce(p.dldnss, '')
  ELSE ''
END AS nele
FROM $schema"proprietaire" p
INNER JOIN $schema"ccodro" cc ON cc.ccodro = p.ccodro
WHERE 2>1
$and

