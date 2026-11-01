SELECT
l.ccosec AS section, ltrim(l.dnupla, '0') AS ndeplan,
ltrim(l.dnvoiri, '0') || l.dindic AS ndevoirie,
CASE WHEN v.libvoi IS NOT NULL THEN Coalesce(v.natvoi || ' ', '') || v.libvoi ELSE p.cconvo || ' ' || p.dvoilib END AS adresse,
l.ccoriv AS coderivoli,
l.dnubat AS bat, l.descr AS ent, l.dniv AS niv, l.dpor AS ndeporte, substring(l.invar, 4, length(l.invar)) || ' ' || l.cleinvar AS numeroinvar,
pev.ccostb AS star, l10.ccoeva AS meval, pev.ccoaff AS af, l10.cconlc AS natloc, pev.dcapec AS cat,
-- Revenu cadastral of the PEV, half of its valeur locative, only on the line of its first exoneration
-- to be counted once
CASE
  WHEN px.dnuexb IS NULL
    OR px.dnuexb = (SELECT min(e.dnuexb) FROM $schema"pevexoneration" e WHERE e.pev = pev.pev)
  THEN Cast(pev.dvlpera / 2 AS integer)
END AS revenucadastral,
px.ccolloc AS coll, px.gnextl AS natexo, px.janimp AS anret, px.jandeb AS andeb,
-- Revenu cadastral exonéré, the percentage of the exoneration is already applied
Coalesce(px.rcexba2, Cast(NULLIF(trim(px.rcexba), '') AS integer)) AS fractionrcexo,
px.pexb AS pourcentageexo, l10.gtauom AS txom, '' AS coefreduc,
CASE
  WHEN px.dnuexb IS NULL
    OR px.dnuexb = (SELECT min(e.dnuexb) FROM $schema"pevexoneration" e WHERE e.pev = pev.pev)
  THEN pt.bateom
END AS rcteom
FROM
$schema"parcelle" p
INNER JOIN $schema"local00" l ON l.parcelle = p.parcelle
INNER JOIN $schema"local10" l10 ON l10.local00 = l.local00
INNER JOIN $schema"pev" pev ON pev.local10 = l10.local10
LEFT OUTER JOIN $schema"voie" v
  ON SUBSTR(l.voie, 1, 6) || SUBSTR(l.voie, 12, 4) = SUBSTR(v.voie, 1, 6) || SUBSTR(v.voie, 12, 4)
LEFT JOIN $schema"pevexoneration" px ON px.pev = pev.pev
LEFT JOIN $schema"pevtaxation" pt ON pt.pev = pev.pev
WHERE 2>1
$and
ORDER BY p.parcelle, l.dnvoiri, v.natvoi, v.libvoi, bat, ent, niv, pev.pev, px.dnuexb
