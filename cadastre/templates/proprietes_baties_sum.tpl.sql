
SELECT

CASE
  WHEN sum(px.rcexba2) > 0 THEN Coalesce(sum(px.rcexba2), '0')
  ELSE sum(pt.tse_bipevla)
END AS revenucadastral,

Coalesce(Sum(Cast(pt.co_vlbaia * px.pexb / 100 AS numeric(10,2))) , 0) as co_vlbaia, sum(pt.co_bipevla) as co_bipevla,
Coalesce(Sum(Cast(pt.gp_vlbaia * px.pexb / 100 AS numeric(10,2))) , 0) as gp_vlbaia, sum(pt.gp_bipevla) as gp_bipevla,
Coalesce(Sum(Cast(pt.de_vlbaia * px.pexb / 100 AS numeric(10,2))) , 0) as de_vlbaia, sum(pt.de_bipevla) as de_bipevla,
Coalesce(Sum(Cast(pt.re_vlbaia * px.pexb / 100 AS numeric(10,2))) , 0) as re_vlbaia, Coalesce(sum(pt.re_bipevla), 0)  as re_bipevla
FROM
parcelle p
INNER JOIN local00 l ON l.parcelle = p.parcelle
INNER JOIN local10 l10 ON l10.local00 = l.local00
INNER JOIN pev ON pev.local10 = l10.local10
LEFT JOIN pevexoneration px ON px.pev = pev.pev
LEFT JOIN pevtaxation pt ON pt.pev = pev.pev
WHERE 2>1
$and

