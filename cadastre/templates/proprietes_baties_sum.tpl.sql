-- Totals of the PEV: revenu cadastral (half of the valeur locative), and for each collectivité
-- the revenu exonéré (R EXO, exonerations of this collectivité or of all of them)
-- and the revenu imposé (R IMP, base d'imposition)
SELECT
Cast(Coalesce(sum(rc), 0) AS integer) AS revenucadastral,
Cast(Coalesce(sum(co_exo), 0) AS integer) AS co_vlbaia, Cast(Coalesce(sum(co_bipevla), 0) AS integer) AS co_bipevla,
Cast(Coalesce(sum(gp_exo), 0) AS integer) AS gp_vlbaia, Cast(Coalesce(sum(gp_bipevla), 0) AS integer) AS gp_bipevla,
Cast(Coalesce(sum(de_exo), 0) AS integer) AS de_vlbaia, Cast(Coalesce(sum(de_bipevla), 0) AS integer) AS de_bipevla,
Cast(Coalesce(sum(re_exo), 0) AS integer) AS re_vlbaia, Cast(Coalesce(sum(re_bipevla), 0) AS integer) AS re_bipevla
FROM (
    SELECT
    Cast(pev.dvlpera / 2 AS integer) AS rc,
    pt.co_bipevla, pt.gp_bipevla, pt.de_bipevla, pt.re_bipevla,
    (
        SELECT sum(Coalesce(px.rcexba2, Cast(NULLIF(trim(px.rcexba), '') AS integer)))
        FROM $schema"pevexoneration" px WHERE px.pev = pev.pev AND px.ccolloc IN ('C', 'TC')
    ) AS co_exo,
    (
        SELECT sum(Coalesce(px.rcexba2, Cast(NULLIF(trim(px.rcexba), '') AS integer)))
        FROM $schema"pevexoneration" px WHERE px.pev = pev.pev AND px.ccolloc IN ('GC', 'TC')
    ) AS gp_exo,
    (
        SELECT sum(Coalesce(px.rcexba2, Cast(NULLIF(trim(px.rcexba), '') AS integer)))
        FROM $schema"pevexoneration" px WHERE px.pev = pev.pev AND px.ccolloc IN ('D', 'TC')
    ) AS de_exo,
    (
        SELECT sum(Coalesce(px.rcexba2, Cast(NULLIF(trim(px.rcexba), '') AS integer)))
        FROM $schema"pevexoneration" px WHERE px.pev = pev.pev AND px.ccolloc IN ('R', 'TC')
    ) AS re_exo
    FROM
    $schema"parcelle" p
    INNER JOIN $schema"local00" l ON l.parcelle = p.parcelle
    INNER JOIN $schema"local10" l10 ON l10.local00 = l.local00
    INNER JOIN $schema"pev" pev ON pev.local10 = l10.local10
    LEFT JOIN $schema"pevtaxation" pt ON pt.pev = pev.pev
    WHERE 2>1
    $and
) AS pevs
