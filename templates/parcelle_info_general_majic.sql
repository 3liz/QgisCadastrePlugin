SELECT
c.libcom AS nomcommune, c.ccocom AS codecommune, p.dcntpa AS contenance,
CASE
        WHEN v.libvoi IS NOT NULL THEN trim(ltrim(p.dnvoiri, '0') || ' ' || trim(v.natvoi) || ' ' || v.libvoi)
        ELSE ltrim(p.cconvo, '0') || p.dvoilib
END AS adresse,
CASE
        WHEN p.gurbpa = 'U' THEN 'Oui'
        ELSE 'Non'
END  AS urbain,
ccosec || dnupla,
p.jdatat
FROM parcelle p
LEFT OUTER JOIN commune c ON p.ccocom = c.ccocom AND c.ccodep = p.ccodep
LEFT OUTER JOIN voie v ON v.voie = p.voie
WHERE 2>1
AND parcelle = '%s'
LIMIT 1
