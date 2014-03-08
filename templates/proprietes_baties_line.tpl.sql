
SELECT
l.ccosec AS section, ltrim(l.dnupla, '0') AS ndeplan,
ltrim(l.dnvoiri, '0') || l.dindic AS ndevoirie,
CASE WHEN v.libvoi IS NOT NULL THEN v.natvoi || v.libvoi ELSE p.cconvo || p.dvoilib END AS adresse,
l.ccoriv AS coderivoli,
l.dnubat AS bat, l.descr AS ent, l.dniv AS niv, l.dpor AS ndeporte, substring(l.invar, 4, length(l.invar)) || ' ' || l.cleinvar AS numeroinvar,
pev.ccostb AS star, l10.ccoeva AS meval, pev.ccoaff AS af, l10.cconlc AS natloc, pev.dcapec AS cat,

CASE
  WHEN px.rcexba2 > 0 THEN px.rcexba2
  ELSE pt.tse_bipevla
END AS revenucadastral,

px.ccolloc AS coll, px.gnextl AS natexo, px.janimp AS anret, px.jandeb AS andeb, Cast(px.rcexba2 * px.pexb / 100 AS numeric(10,2)) AS fractionrcexo,
px.pexb AS pourcentageexo, l10.gtauom AS txom, '' AS coefreduc
FROM
parcelle p
INNER JOIN local00 l ON l.parcelle = p.parcelle
INNER JOIN local10 l10 ON l10.local00 = l.local00
INNER JOIN pev ON pev.local10 = l10.local10
LEFT OUTER JOIN voie v ON v.voie = l.voie
LEFT JOIN pevexoneration px ON px.pev = pev.pev
LEFT JOIN pevtaxation pt ON pt.pev = pev.pev
WHERE 2>1
$and
ORDER BY p.parcelle, l.dnvoiri, v.natvoi, v.libvoi, bat, ent, niv
