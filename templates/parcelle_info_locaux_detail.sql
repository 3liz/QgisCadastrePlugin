WITH infos AS (
    SELECT
    p.parcelle,
    -- identification
    l.dnubat AS l_batiment, l.descr AS l_numero_entree,
    l.dniv AS l_niveau_etage, l.dpor AS l_numero_local,
    l.invar AS l_invariant,
    (l.dnubat || l.descr || l.dniv || l.dpor) AS l_identifiant,

    -- adresse
    ltrim(l.dnvoiri, '0') || l.dindic AS l_numero_voirie,
    CASE WHEN v.libvoi IS NOT NULL THEN v.natvoi || v.libvoi ELSE p.cconvo || p.dvoilib END AS l_adresse,

    -- proprio et acte
    string_agg((l10.ccodep || l10.ccocom || '-' ||l10.dnupro), '|') AS l10_compte_proprietaire,

    string_agg(
        '<tr>' ||
            '<td>' || pr.dnulp || '</td>' ||
            '<td>' || pr.dnuper || '</td>' ||
            '<td>' ||
            trim(coalesce(pr.dqualp, '')) || ' ' ||
            CASE WHEN trim(pr.dnomus) != trim(pr.dnomlp) THEN Coalesce( trim(pr.dnomus) || '/' || trim(pr.dprnus) || ', née ', '' ) ELSE '' END ||
            trim(coalesce(pr.ddenom, '')) ||
            '</td>' ||
            '<td>' || ltrim(trim(coalesce(pr.dlign4, '')), '0') || trim(coalesce(pr.dlign5, '')) || ' ' || trim(coalesce(pr.dlign6, '')) || '</td>' ||
            '<td>' || Coalesce( trim(cast(pr.jdatnss AS text) ), '-') || '</td>' ||
            '<td>' || coalesce(trim(pr.dldnss), '-') || '</td>' ||
            '<td>' || Coalesce(ccodro_lib, '') || '</td>' ||
            '<td>' || Coalesce(ccodem_lib, '') || '</td>' ||
        '</tr>'
        , ''
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
    pev.dnupev AS pev_dnupev,
    ccoaff_lib AS pev_affectation,
    pev.ccostb AS pev_lettre_serie,
    pev.dcapec AS pev_categorie,
    pev.dcetlc AS pev_entretien,
    pev.dvlper AS pev_valeur_locative_ref,
    pev.dvlpera AS pev_valeur_locative_an,
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
    LEFT JOIN voie v ON v.voie = l.voie
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
    AND p.parcelle = '%s'

    GROUP BY
    p.parcelle,
    l.invar,
    l.dnubat, l.dniv, l.descr, l.dpor,
    l.dnvoiri, l.dindic,
    v.natvoi, v.libvoi, p.cconvo, p.dvoilib,
    l10.ccodep, l10.ccocom, l10.dnupro, l10.jdatat,
    dteloc_lib, cconlc_lib, ccoplc_lib, l10.jannat, l10.dnbniv, dnatlc_lib,
    pev.pev, ccoaff_lib, pev.ccostb, pev.dcapec, pev.dcetlc, pev.dvlpera, pev.gnexpl, pev.dnuref, pev.dcsplca, pev.dcsglca,
    pt.co_vlbaia, pt.gp_vlbaia, pt.de_vlbaia, pt.re_vlbaia, px.pexb, pt.co_bipevla, pt.gp_bipevla, pt.de_bipevla, pt.re_bipevla

    ORDER BY l_identifiant

),

pevs AS (
    SELECT pp.pev,
        'Habitation' AS type_pev, 'Habitation' AS sous_type_pev,
        (
            '<b>Nombre de pièces: </b>' || pp.dnbpdc || '<br/><b>Pièces principales: </b>' || pp.dnbppr ||
            '<br/><b>Surface des pièces: </b>' || pp.dsupdc || ' m2' || '<br/><b>Salles à manger: </b>' || pp.dnbsam || '<br/><b>Chambres: </b>' || pp.dnbcha ||
            '<br/><b>Cuisines - 9m2: </b>' || pp.dnbcu8 || '<br/><b>Cuisines > 9m2: </b>' || pp.dnbcu9 ||
            '<br/><b>Salles d''eau: </b>' || pp.dnbsea || '<br/><b>Pièces annexes: </b>' || pp.dnbann
        ) AS descriptif,
        (
            '<b>Eau: </b>' || pp.geaulc || '<br/><b>Électricité: </b>' || pp.gelelc ||
            '<br/><b>Gaz: </b>' || pp.ggazlc || '<br/><b>Chauffage central: </b>' || pp.gchclc ||
            '<br/><b>Baignoire(s): </b>' || pp.dnbbai || '<br/><b>Douche(s): </b>' || pp.dnbdou ||
            '<br/><b>Lavabo(s): </b>' || pp.dnblav || '<br/><b>WC: </b>' || pp.dnbwc
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
            '<br/><b>Chauffage central: </b>' || pd.gchclc || '<br/><b>Baignoire(s): </b>' || pd.dnbbai ||
            '<br/><b>Douche(s): </b>' || pd.dnbdou || '<br/><b>Lavabo(s): </b>' || pd.dnblav || '<br/><b>WC: </b>' || pd.dnbwc
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
    l_batiment, l_numero_entree, l_niveau_etage, l_numero_local, l_invariant, l_identifiant, l_numero_voirie, l_adresse,
    l10_compte_proprietaire, l10_proprietaires, l10_date_acte, l10_type_local, l10_nature_local, l10_nature_occupation, l10_nature_construction_particuliere, l10_annee_construction, l10_nombre_niveaux,
    pev_dnupev, pev_affectation, pev_lettre_serie, pev_categorie, pev_entretien, pev_valeur_locative_ref, pev_valeur_locative_an, pev_nature_exoneration_permanente,
    pev_numero_local_type, pev_coefficient_situation_particuliere, pev_coefficient_situation_generale,
    co_vlbaia, gp_vlbaia, de_vlbaia, re_vlbaia, co_bipevla, gp_bipevla, de_bipevla, re_bipevla,
    count(p.pev) AS nb_pev,
    string_agg(
        '<tr>' ||
            '<td>' || pev_dnupev || '</td>' ||
            '<td>' || type_pev || '</td>' ||
            '<td>' || Coalesce(sous_type_pev, '') || '</td>' ||
            '<td>' || descriptif || '</td>' ||
            '<td>' || confort || '</td>' ||
        '</tr>'
        , ''
    )
    AS infos_pev
    FROM infos i
    JOIN pevs p ON i.pev = p.pev
    GROUP BY
    parcelle,
    l_batiment, l_numero_entree, l_niveau_etage, l_numero_local, l_invariant, l_identifiant, l_numero_voirie, l_adresse,
    l10_compte_proprietaire, l10_proprietaires, l10_date_acte, l10_type_local, l10_nature_local, l10_nature_occupation, l10_nature_construction_particuliere, l10_annee_construction, l10_nombre_niveaux,
    pev_dnupev, pev_affectation, pev_lettre_serie, pev_categorie, pev_entretien, pev_valeur_locative_ref, pev_valeur_locative_an, pev_nature_exoneration_permanente,
    pev_numero_local_type, pev_coefficient_situation_particuliere, pev_coefficient_situation_generale,
    co_vlbaia, gp_vlbaia, de_vlbaia, re_vlbaia, co_bipevla, gp_bipevla, de_bipevla, re_bipevla
    ORDER BY l_identifiant
)

SELECT
'La parcelle contient ' || count(l_identifiant) || CASE WHEN count(l_identifiant) > 1 THEN ' locaux' ELSE ' local' END
||
'<div>' || string_agg(
    (
        '<h2>Local ' ||  l_invariant ||  '</h2>' ||
        '<h3>Description générale</h3>' ||

        '<h4>Identification</h4>' ||
        '<p>' ||
        '<table class="table table-condensed table-striped" border=1 cellspacing=0 cellpadding=3 width="100p">' ||
        '<tr>' ||
            '<th>Invariant</th>' ||
            '<th>Bat.</th>' ||
            '<th>Entrée</th>' ||
            '<th>Etage</th>' ||
            '<th>Local</th>' ||
            '<th>Identifiant</th>' ||
            '<th>Adresse</th>' ||
        '</tr>' ||
        '<tr>' ||
            '<td>' || l_invariant || '</td>' ||
            '<td>' || l_batiment || '</td>' ||
            '<td>' || l_numero_entree || '</td>' ||
            '<td>' || l_niveau_etage || '</td>' ||
            '<td>' || l_numero_local || '</td>' ||
            '<td>' || l_identifiant || '</td>' ||
            '<td>'||  l_adresse || '</td>' ||
        '</tr>' ||
        '</table>' ||
        '</p>' ||

        '<h4>Propriété</h4>' ||
        '<p>' ||
        '<b>Compte propriétaire: </b>' ||  l10_compte_proprietaire ||
        '<br/><b>Date de l''acte: </b>' ||  Coalesce(l10_date_acte::text, '-') ||
        '</p>' ||

        '<h4>Caractéristiques</h4>' ||
        '<p>' ||
        '<b>Type: </b>' ||  l10_type_local ||
        '<br/><b>Nature: </b>' ||  l10_nature_local ||
        '<br/><b>Occupation: </b>' ||  l10_nature_occupation ||
        '<br/><b>Construction: </b>' ||  l10_nature_construction_particuliere ||
        '<br/><b>Année de construction: </b>' ||  l10_annee_construction ||
        '<br/><b>Niveaux: </b>' ||  l10_nombre_niveaux ||
        '</p>' ||

        '<h3>Description foncière</h3>' ||

        '<h4>Évaluation</h4>' ||
        '<p>' ||
        '<b>Numéro de PEV: </b>' ||  pev_dnupev ||
        '<br/><b>Affectation: </b>' ||  pev_affectation ||
        '<br/><b>Lettre de série: </b>' ||  pev_lettre_serie ||
        '<br/><b>Catégorie: </b>' ||  pev_categorie ||
        '<br/><b>Entretien: </b>' ||  Coalesce(pev_entretien, -1) ||
        '<br/><b>Valeur locative (en valeur de référence): </b>' ||  Coalesce(pev_valeur_locative_ref, -1) ||
        '<br/><b>Valeur locative (en valeur de l''année): </b>' ||  Coalesce(pev_valeur_locative_an, -1) ||
        '<br/><b>Exonération permanente: </b>' ||  Coalesce(pev_nature_exoneration_permanente, '') ||
        '<br/><b>Numéro du local type: </b>' ||  Coalesce(pev_numero_local_type, '') ||
        '<br/><b>Situation générale: </b>' ||  Coalesce(pev_coefficient_situation_generale, '') ||
        '<br/><b>Situation particulière: </b>' ||  Coalesce(pev_coefficient_situation_particuliere, '') ||
        '</p>' ||

        '<h4>Taxation</h4>' ||
        '<p>' ||
        '<b>Commune: </b>' ||  co_bipevla ||
        '<br/><b>Intercommunalité: </b>' ||  gp_bipevla ||
        '<br/><b>Département: </b>' ||  de_bipevla ||
        '<br/><b>Région: </b>' ||  re_bipevla ||
        '</p>' ||

        '<h3>Parties d''évaluation</h3>' ||
        'Le local contient ' || nb_pev || ' parties.' ||
        '<p>' ||
        '<table class="table table-condensed table-striped" border=1 cellspacing=0 cellpadding=3 width="100p">' ||
        '<tr>' ||
            '<th>PEV</th>' ||
            '<th>Type</th>' ||
            '<th>Sous-type</th>' ||
            '<th>Descriptif</th>' ||
            '<th>Confort</th>' ||
        '</tr>' ||
        Coalesce(infos_pev, '') ||
        '</table>' ||
        '</p>' ||

        '<h3>Propriétaires</h3>' ||
        '<table class="table table-condensed table-striped" border=1 cellspacing=0 cellpadding=3 width="100p">' ||
        '<tr>' ||
            '<th>Numéro</th>' ||
            '<th>Code</th>' ||
            '<th>Nom</th>' ||
            '<th>Adresse</th>' ||
            '<th>Date de naissance</th>' ||
            '<th>Lieux de naissance</th>' ||
            '<th>Code droit</th>' ||
            '<th>Code démembrement</th>' ||
        '</tr>' ||
        l10_proprietaires ||
        '</table>' ||
        '</p>'

    )
    , '</div><br/><div>'
) || '</div>' AS locaux
FROM source
GROUP BY parcelle
;
