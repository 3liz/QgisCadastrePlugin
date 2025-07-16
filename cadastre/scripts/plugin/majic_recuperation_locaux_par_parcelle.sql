DROP TABLE IF EXISTS parcelle_info_locaux;
CREATE TABLE parcelle_info_locaux AS

WITH infos AS (
    SELECT
    p.parcelle,
    -- identification
    l.dnubat AS l_batiment, l.descr AS l_numero_entree,
    l.dniv AS l_niveau_etage, l.dpor AS l_numero_local,
    (l.dnubat || l.descr || l.dniv || l.dpor) AS l_identifiant,

    -- adresse
    ltrim(l.dnvoiri, '0') || l.dindic AS l_numero_voirie,
    CASE WHEN v.libvoi IS NOT NULL THEN Coalesce(v.natvoi || ' ', '') || v.libvoi ELSE p.cconvo || p.dvoilib END AS l_adresse,

    -- proprio et acte
    string_agg((l10.ccodep || l10.ccocom || '-' ||l10.dnupro), '|') AS l10_compte_proprietaire,

    string_agg(
        trim((
            '<b>Numéro: </b>' || pr.dnuper ||
            '<br/><b>Nom: </b>' || trim(coalesce(pr.dqualp, '')) || ' ' || trim(coalesce(pr.ddenom, '')) ||
            '<br/><b>Adresse: </b>' || ltrim(trim(coalesce(pr.dlign4, '')), '0') || trim(coalesce(pr.dlign5, '')) || ' ' || trim(coalesce(pr.dlign6, '')) ||
            '<br/><b>Date de naissance: </b>' || Coalesce( trim(cast(pr.jdatnss AS text) ), '-') ||
            '<br/><b>Lieux de naissance: </b>' || coalesce(trim(pr.dldnss), '-') ||
            '<br/><b>Code droit: </b>' || Coalesce(ccodro_lib, '') ||
            '<br/><b>Code démembrement: </b>' || Coalesce(ccodem_lib, '')
        ))
        , '|'
    ) AS l10_proprietaires,

    l10.jdatat AS l10_date_acte,

    -- autres infos
    dteloc_lib AS l10_type_local,
    cconlc_lib AS l10_nature_local,
    ccoplc_lib AS l10_nature_construction_particuliere,
    l10.jannat AS l10_annee_construction,
    l10.dnbniv AS l10_nombre_niveaux,
    dnatlc_lib AS l10_nature_occupation,

    -- pev : informations générales
    pev.pev,
    ccoaff_lib AS pev_affectation,
    pev.ccostb AS pev_lettre_serie,
    pev.dcapec AS pev_categorie,
    pev.dcetlc AS pev_entretien,
    pev.dvlpera AS pev_valeur_locative,
    pev.gnexpl AS pev_nature_exoneration_permanente,
    pev.dnuref AS pev_numero_local_type,
    pev.dcsplca AS pev_coefficient_situation_particuliere,
    pev.dcsglca AS pev_coefficient_situation_generale,

    -- pev : taxation (1 seule par PEV)
    Coalesce(Cast(pt.co_vlbaia * px.pexb / 100 AS numeric(10,2)) , 0) as co_vlbaia, pt.co_bipevla as co_bipevla,
    Coalesce(Cast(pt.gp_vlbaia * px.pexb / 100 AS numeric(10,2)) , 0) as gp_vlbaia, pt.gp_bipevla as gp_bipevla,
    Coalesce(Cast(pt.de_vlbaia * px.pexb / 100 AS numeric(10,2)) , 0) as de_vlbaia, pt.de_bipevla as de_bipevla,
    Coalesce(Cast(pt.re_vlbaia * px.pexb / 100 AS numeric(10,2)) , 0) as re_vlbaia, Coalesce(pt.re_bipevla, 0)  as re_bipevla

    FROM parcelle p
    INNER JOIN local00 l ON l.parcelle = p.parcelle
    INNER JOIN local10 l10 ON l10.local00 = l.local00
    INNER JOIN pev ON pev.local10 = l10.local10
    LEFT JOIN voie v ON SUBSTR(l.voie, 1, 6) || SUBSTR(l.voie, 12, 4) = SUBSTR(v.voie, 1, 6) || SUBSTR(v.voie, 12, 4)
    LEFT JOIN pevtaxation pt ON pt.pev = pev.pev
    LEFT JOIN pevexoneration px ON px.pev = pev.pev
    LEFT JOIN "dteloc" ON l10.dteloc = dteloc.dteloc
    LEFT JOIN "cconlc" ON l10.cconlc = cconlc.cconlc
    LEFT JOIN "ccoplc" ON l10.ccoplc = ccoplc.ccoplc
    LEFT JOIN "dnatlc" ON l10.dnatlc = dnatlc.dnatlc
    LEFT JOIN "ccoaff" ON pev.ccoaff = ccoaff.ccoaff
    LEFT JOIN proprietaire AS pr ON pr.comptecommunal = l10.comptecommunal
    LEFT JOIN "ccodro" c2 ON pr.ccodro = c2.ccodro
    LEFT JOIN "ccodem" c3 ON pr.ccodem = c3.ccodem

    WHERE 2>1
    --AND p.parcelle = '%s'

    GROUP BY
    p.parcelle,
    l.dnubat, l.dniv, l.descr, l.dpor,
    l.dnvoiri, l.dindic,
    v.natvoi, v.libvoi, p.cconvo, p.dvoilib,
    l10.ccodep, l10.ccocom, l10.dnupro, l10.jdatat,
    dteloc_lib, cconlc_lib, ccoplc_lib, l10.jannat, l10.dnbniv, dnatlc_lib,
    pev.pev, ccoaff_lib, pev.ccostb, pev.dcapec, pev.dcetlc, pev.dvlpera, pev.gnexpl, pev.dnuref, pev.dcsplca, pev.dcsglca,
    pt.co_vlbaia, pt.gp_vlbaia, pt.de_vlbaia, pt.re_vlbaia, px.pexb, pt.co_bipevla, pt.gp_bipevla, pt.de_bipevla, pt.re_bipevla

    ORDER BY l_identifiant

    --LIMIT 1
),

pevs AS (
    SELECT pp.pev,
        'Habitation' AS type_pev, 'Habitation' AS sous_type_pev,
        (
            '<b>Nombre de pièces: </b>' || pp.dnbpdc || '<br/><b>Pièces principales: </b>' || pp.dnbppr ||
            '<br/><b>Surface des pièces: </b>' || pp.dsupdc || ' m2' || '<br/>Salles à manger: </b>' || pp.dnbsam || '<br/>Chambres: </b>' || pp.dnbcha ||
            '<br/><b>Cuisines < 9m2: </b>' || pp.dnbcu8 || '<br/>Cuisines > 9m2: </b>' || pp.dnbcu9 ||
            '<br/><b>Salles d''eau: </b>' || pp.dnbsea || '<br/>Pièces annexes: </b>' || pp.dnbann
        ) AS descriptif,
        (
            '<b>Eau: </b>' || pp.geaulc || '<br/><b>Électricité: </b>' || pp.gelelc ||
            '<br/><b>Gaz: </b>' || pp.ggazlc || '<br/>Chauffage central: </b>' || pp.gchclc ||
            '<br/><b>Baignoire(s): </b>' || pp.dnbbai || '<br/>Douche(s): </b>' || pp.dnbdou ||
            '<br/><b>Lavabo(s): </b>' || pp.dnblav || '<br/>WC: </b>' || pp.dnbwc
        ) AS confort
    FROM pevprincipale pp
    JOIN infos ON infos.pev = pp.pev
    UNION ALL
    SELECT pd.pev,
        'Dépendance' AS type_pev, cconad_lib AS sous_type_pev,
        (
            '<b>Situation particulière: </b>' || pd.dcspdea || '<br/><b>Surface réelle: </b>' || pd.dsudep || ' m2</b>' ||
            '<br/><b>Pondération: </b>' || pd.dcimlc || '<br/><b>État d''entretien: </b>' || pd.detent
        ) AS descriptif,
        (
            '<b>Eau: </b>' || pd.geaulc || '<br/><b>Électricité: </b>' || pd.gelelc ||
            '<br/><b>Chauffage central: </b>' || pd.gchclc || '<br/>Baignoire(s): </b>' || pd.dnbbai ||
            '<br/><b>Douche(s): </b>' || pd.dnbdou || '<br/>Lavabo(s): </b>' || pd.dnblav || '<br/>WC: </b>' || pd.dnbwc
        ) AS confort
    FROM pevdependances pd
    JOIN infos ON infos.pev = pd.pev
    LEFT JOIN cconad ON cconad.cconad = pd.cconad
    UNION ALL
    SELECT po.pev,
        'Professionnel' AS type, 'Local professionnel' AS sous_type_pev,
        Coalesce('<b>Surface réelle: </b>' || po.vsurzt || ' m2', '') AS descriptif,
        '' AS confort
    FROM pevprofessionnelle po
    JOIN infos ON infos.pev = po.pev
),
source AS (
    SELECT
    parcelle,
    l_batiment, l_numero_entree, l_niveau_etage, l_numero_local, l_identifiant, l_numero_voirie, l_adresse,
    l10_compte_proprietaire, l10_proprietaires, l10_date_acte, l10_type_local, l10_nature_local, l10_nature_construction_particuliere, l10_annee_construction, l10_nombre_niveaux,
    pev_affectation, pev_lettre_serie, pev_categorie, pev_entretien, pev_valeur_locative, pev_nature_exoneration_permanente,
    pev_numero_local_type, pev_coefficient_situation_particuliere, pev_coefficient_situation_generale,
    co_vlbaia, gp_vlbaia, de_vlbaia, re_vlbaia, co_bipevla, gp_bipevla, de_bipevla, re_bipevla,
    count(p.pev) AS nb_pev,
    string_agg(
        ('<b>Type: </b>' || type_pev || '<br/><b>Sous-type: </b>' || Coalesce(sous_type_pev, '') || Coalesce('<h4>Descriptif</h4>' || descriptif, '') || Coalesce('<h4>Confort</h4></b>' || confort, '') ),
        '@')
    AS infos_pev
    FROM infos i
    JOIN pevs p ON i.pev = p.pev
    GROUP BY
    parcelle,
    l_batiment, l_numero_entree, l_niveau_etage, l_numero_local, l_identifiant, l_numero_voirie, l_adresse,
    l10_compte_proprietaire, l10_proprietaires, l10_date_acte, l10_type_local, l10_nature_local, l10_nature_construction_particuliere, l10_annee_construction, l10_nombre_niveaux,
    pev_affectation, pev_lettre_serie, pev_categorie, pev_entretien, pev_valeur_locative, pev_nature_exoneration_permanente,
    pev_numero_local_type, pev_coefficient_situation_particuliere, pev_coefficient_situation_generale,
    co_vlbaia, gp_vlbaia, de_vlbaia, re_vlbaia, co_bipevla, gp_bipevla, de_bipevla, re_bipevla
    ORDER BY l_identifiant
)

SELECT
parcelle,
count(l_identifiant) AS nb_locaux,
string_agg(
    (
        '<h2>Local ' ||  l_identifiant ||  '</h2>' ||
        '<h3>Description générale</h3>' ||

        '<h4>Identification</h4>' ||
        '<p>' ||
        '<b>Bat: </b>' ||  l_batiment ||
        '<br/><b>Entrée: </b>' ||  l_numero_entree ||
        '<br/><b>Etage: </b>' ||  l_niveau_etage ||
        '<br/><b>Local: </b>' ||  l_numero_local ||
        '<br/><b>Identifiant: </b>' ||  l_identifiant ||
        '<br/><b>Adresse: </b>' ||  l_adresse ||
        '</p>' ||

        '<h4>Propriété</h4>' ||
        '<p>' ||
        '<b>Compte propriétaire: </b>' ||  l10_compte_proprietaire ||
        '<br/><b>Date de l''acte: </b>' ||  l10_date_acte ||
        '</p>' ||

        '<h4>Caractéristiques</h4>' ||
        '<p>' ||
        '<b>Type: </b>' ||  l10_type_local ||
        '<br/><b>Nature: </b>' ||  l10_nature_local ||
        '<br/><b>Construction: </b>' ||  l10_nature_construction_particuliere ||
        '<br/><b>Année de construction: </b>' ||  l10_annee_construction ||
        '<br/><b>Niveaux: </b>' ||  l10_nombre_niveaux ||
        '</p>' ||

        '<h3>Description foncière</h3>' ||

        '<h4>Évaluation</h4>' ||
        '<p>' ||
        '<b>Affectation: </b>' ||  pev_affectation ||
        '<br/><b>Lettre de série: </b>' ||  pev_lettre_serie ||
        '<br/><b>Catégorie: </b>' ||  pev_categorie ||
        '<br/><b>Entretien: </b>' ||  Coalesce(pev_entretien, -1) ||
        '<br/><b>Valeur locative: </b>' ||  Coalesce(pev_valeur_locative, -1) ||
        '<br/><b>Exonération permanente: </b>' ||  Coalesce(pev_nature_exoneration_permanente, '') ||
        '<br/><b>Numéro du local type: </b>' ||  Coalesce(pev_numero_local_type, '') ||
        '<br/><b>Situation générale: </b>' ||  Coalesce(pev_coefficient_situation_generale, '') ||
        '<br/><b>Situation particulière: </b>' ||  Coalesce(pev_coefficient_situation_particuliere, '') ||
        '</p>' ||

        '<h4>Taxation</h4>' ||
        '<p>' ||
        '<b>Commune: </b>' ||  Coalesce(co_bipevla, 0) ||
        '<br/><b>Intercommunalité: </b>' ||  Coalesce(gp_bipevla, 0) ||
        '<br/><b>Département: </b>' ||  Coalesce(de_bipevla, 0) ||
        '<br/><b>Région: </b>' ||  Coalesce(re_bipevla, 0) ||
        '</p>' ||

        '<h3>Description détaillée</h3>' ||
        'Le local contient ' || nb_pev || ' parties.' ||
        '<p>__________________________<br/> ' ||
        replace(infos_pev,  '@',  '<br/>__________________________</p><p>__________________________<br/>') ||
        '<br/>__________________________' ||
        '</p>' ||

        '<h3>Propriétaires</h3>' ||
        '<p>' ||
        replace( Coalesce(l10_proprietaires, ''),  '|', '<p/><p>') ||
        '</p>'

    )
    , '<hr>'
) AS locaux
FROM source
GROUP BY parcelle
;

CREATE INDEX parcelle_info_locaux_pk ON parcelle_info_locaux (parcelle);
