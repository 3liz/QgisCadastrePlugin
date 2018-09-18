SELECT
--suf
s.ccosub AS s_nom,
-- s.cgrnum AS s_groupe_nature_culture,
cgrnum_lib AS s_groupe_nature_culture_lib,
-- s.dsgrpf AS s_sous_groupe,
dsgrpf_lib AS s_sous_groupe_lib,
s.dclssf AS s_classe_dans_le_groupe,
s.cnatsp AS s_code_nature_de_culture_speciale,
s.drcsuba AS s_revenu_cadastral,

-- sufexoneration
-- se.gnexts AS se_nature_exoneration,
gnexts_lib AS se_nature_exoneration_lib,
-- se.ccolloc AS se_collectivite,
ccolloc_lib AS se_collectivite_lib,
Cast(se.pexn / 100 AS numeric(10,2)) AS se_pourcentage_exonere,
round(Cast(s.drcsuba * Cast(se.pexn / 100 AS numeric(10,2)) / 100 AS numeric) , 2) as se_montant_exonere
FROM suf s
LEFT JOIN "cgrnum" ON s.cgrnum = cgrnum.cgrnum
LEFT JOIN "dsgrpf" ON s.dsgrpf = dsgrpf.dsgrpf
LEFT JOIN sufexoneration se ON s.suf = se.suf
LEFT JOIN "gnexts" ON se.gnexts = trim(gnexts.gnexts)
LEFT JOIN "ccolloc" ON se.ccolloc = ccolloc.ccolloc
WHERE 2>1 AND s.parcelle = '%s'
