
SELECT --p.parcelle, p.geo_parcelle,
l.ccosec AS section, l.dnupla AS ndeplan,
regexp_replace(l.dnvoiri, '^0+', '') AS ndevoirie,
v.natvoi || v.libvoi AS adresse,
l.ccoriv AS coderivoli,
l.dnubat AS bat, l.descr AS ent, l.dniv AS niv, l.dpor AS ndeporte, l.invar AS numeroinvar,
pev.ccostb AS star, l10.ccoeva AS meval, pev.ccoaff AS af, l10.cconlc AS natloc, pev.dcapec AS cat,
px.rcexba2 AS revenucadastral, px.ccolloc AS coll, px.gnextl AS natexo, px.janimp AS anret, px.jandeb AS andeb, px.dvldif2a AS fractionrcexo,
px.pexb AS pourcentageexo, l10.gtauom AS txom, '' AS coefreduc
FROM
parcelle p
INNER JOIN local00 l ON l.parcelle = p.parcelle
INNER JOIN local10 l10 ON l10.local00 = l.local00
INNER JOIN pev ON pev.local10 = l10.local10
INNER JOIN voie v ON v.voie = l.voie
LEFT JOIN pevexoneration px ON px.pev = pev.pev
LEFT JOIN pevtaxation pt ON pt.pev = pev.pev
WHERE 2>1
$and
ORDER BY p.parcelle, l.dnvoiri, v.natvoi, v.libvoi, bat, ent, niv
