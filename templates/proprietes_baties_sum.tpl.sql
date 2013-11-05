
SELECT

CASE
  WHEN sum(px.rcexba2) > 0 THEN sum(px.rcexba2)
  ELSE sum(pt.tse_bipevla)
END AS revenucadastral,

Sum(Cast(pt.co_vlbaia * px.pexb / 100 AS numeric(10,2))) as co_vlbaia, sum(pt.co_bipevla) as co_bipevla,
Sum(Cast(pt.gp_vlbaia * px.pexb / 100 AS numeric(10,2))) as gp_vlbaia, sum(pt.gp_bipevla) as gp_bipevla,
Sum(Cast(pt.de_vlbaia * px.pexb / 100 AS numeric(10,2))) as de_vlbaia, sum(pt.de_bipevla) as de_bipevla,
Sum(Cast(pt.re_vlbaia * px.pexb / 100 AS numeric(10,2))) as re_vlbaia, sum(pt.re_bipevla) as re_bipevla
FROM
parcelle p
INNER JOIN local00 l ON l.parcelle = p.parcelle
INNER JOIN local10 l10 ON l10.local00 = l.local00
INNER JOIN pev ON pev.local10 = l10.local10
LEFT JOIN pevexoneration px ON px.pev = pev.pev
LEFT JOIN pevtaxation pt ON pt.pev = pev.pev
WHERE 2>1
$and

