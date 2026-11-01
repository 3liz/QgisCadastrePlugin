"""Locaux of a parcel in the fiche parcellaire: a summary table, then the details of each local.

The data is read by one query per level (locaux, parties d'évaluation (PEV), descriptions of the PEV,
exonérations, owners), filtered on the parcel, then grouped in Python:

    Local (local00, local10) ──< PEV ──< habitation (pevprincipale), dependances, local professionnel
      │                          └──< exonérations (pevexoneration), taxation (pevtaxation, one per PEV)
      └── compte communal ──< proprietaires
"""

__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import html

from dataclasses import dataclass, field

from qgis.core import QgsAbstractDatabaseProviderConnection

from cadastre.fiche import (
    DATE_MASK,
    DisplayOptions,
    Field,
    Row,
    Section,
    codes,
    date_fr,
    fetch_rows,
    label,
    number,
    percent,
    surface,
    table_html,
    yes_no,
)

# The local00 of the parcel, the tables are joined from it because local00.parcelle is indexed
FROM_LOCAUX = """
FROM local00 l
JOIN local10 l10 ON l10.local00 = l.local00
"""

SQL_LOCAUX = (
    """
SELECT
    l10.local10 AS local10,
    l.invar AS invariant,
    l.dnubat AS batiment,
    l.descr AS entree,
    l.dniv AS niveau,
    l.dpor AS porte,
    Coalesce(ltrim(l.dnvoiri, '0'), '') || Coalesce(l.dindic, '') AS numero_voirie,
    CASE
        WHEN v.libvoi IS NOT NULL THEN Coalesce(v.natvoi || ' ', '') || v.libvoi
        ELSE l.dvoilib
    END AS voie,
    l10.comptecommunal AS comptecommunal,
    l10.jdatat AS date_acte,
    dteloc.dteloc_lib AS type,
    cconlc.cconlc_lib AS nature,
    ccoplc.ccoplc_lib AS construction,
    l10.jannat AS annee_construction,
    l10.dnbniv AS niveaux
"""
    + FROM_LOCAUX
    + """
LEFT JOIN voie v
    ON SUBSTR(l.voie, 1, 6) || SUBSTR(l.voie, 12, 4) = SUBSTR(v.voie, 1, 6) || SUBSTR(v.voie, 12, 4)
LEFT JOIN dteloc ON dteloc.dteloc = l10.dteloc
LEFT JOIN cconlc ON cconlc.cconlc = l10.cconlc
LEFT JOIN ccoplc ON ccoplc.ccoplc = l10.ccoplc
WHERE l.parcelle = {parcelle}
ORDER BY l.dnubat, l.descr, l.dniv, l.dpor, l.invar
"""
)

SQL_PROPRIETAIRES = (
    """
SELECT
    l10.local10 AS local10,
    pr.dnulp AS numero,
    pr.dnuper AS code,
    trim(
        Coalesce(trim(pr.dqualp) || ' ', '')
        || CASE
            WHEN trim(pr.dnomus) != trim(pr.dnomlp)
            THEN Coalesce(trim(pr.dnomus) || '/' || trim(pr.dprnus) || ', née ', '')
            ELSE ''
        END
        || Coalesce(trim(pr.ddenom), '')
    ) AS nom,
    trim(
        Coalesce(ltrim(trim(pr.dlign4), '0') || ' ', '')
        || Coalesce(trim(pr.dlign5) || ' ', '')
        || Coalesce(trim(pr.dlign6), '')
    ) AS adresse,
    pr.jdatnss AS date_naissance,
    pr.dldnss AS lieu_naissance,
    ccodro.ccodro_lib AS droit,
    ccodem.ccodem_lib AS demembrement,
    pr.gdesip AS destinataire
"""
    + FROM_LOCAUX
    + """
JOIN proprietaire pr ON pr.comptecommunal = l10.comptecommunal
LEFT JOIN ccodro ON ccodro.ccodro = pr.ccodro
LEFT JOIN ccodem ON ccodem.ccodem = pr.ccodem
WHERE l.parcelle = {parcelle}
ORDER BY l10.local10, pr.dnulp, pr.dnuper
"""
)

SQL_PEVS = (
    """
SELECT
    pev.pev AS pev,
    pev.local10 AS local10,
    pev.dnupev AS numero,
    ccoaff.ccoaff_lib AS affectation,
    pev.ccostb AS lettre_serie,
    pev.dcapec AS categorie,
    pev.dcetlc AS entretien,
    pev.dvlper AS valeur_locative_reference,
    pev.dvlpera AS valeur_locative,
    gnexpl.gnexpl_lib AS exoneration_permanente,
    pev.dnuref AS local_type,
    pev.dcsglca AS situation_generale,
    pev.dcsplca AS situation_particuliere,
    pt.co_vlbaia AS co_vlbaia, pt.co_bipevla AS co_bipevla,
    pt.gp_vlbaia AS gp_vlbaia, pt.gp_bipevla AS gp_bipevla,
    pt.tse_vlbaia AS tse_vlbaia, pt.tse_bipevla AS tse_bipevla,
    pt.de_vlbaia AS de_vlbaia, pt.de_bipevla AS de_bipevla
"""
    + FROM_LOCAUX
    + """
JOIN pev ON pev.local10 = l10.local10
LEFT JOIN pevtaxation pt ON pt.pev = pev.pev
LEFT JOIN ccoaff ON ccoaff.ccoaff = pev.ccoaff
LEFT JOIN gnexpl ON gnexpl.gnexpl = pev.gnexpl
WHERE l.parcelle = {parcelle}
ORDER BY pev.pev
"""
)

SQL_HABITATIONS = (
    """
SELECT
    pp.pev AS pev,
    pp.dnbpdc AS pieces, pp.dnbppr AS pieces_principales, pp.dsupdc AS surface_pieces,
    pp.dnbsam AS salles_a_manger, pp.dnbcha AS chambres,
    pp.dnbcu8 AS cuisines_moins_9, pp.dnbcu9 AS cuisines_plus_9,
    pp.dnbsea AS salles_eau, pp.dnbann AS pieces_annexes,
    pp.dmatgm AS murs, pp.dmatto AS toiture, pp.detent AS etat_entretien,
    pp.geaulc AS eau, pp.gelelc AS electricite, pp.ggazlc AS gaz, pp.gchclc AS chauffage,
    pp.dnbbai AS baignoires, pp.dnbdou AS douches, pp.dnblav AS lavabos, pp.dnbwc AS wc,
    c1.cconad_lib AS dep1, pp.dep1_dsueic AS dep1_surface,
    c2.cconad_lib AS dep2, pp.dep2_dsueic AS dep2_surface,
    c3.cconad_lib AS dep3, pp.dep3_dsueic AS dep3_surface,
    c4.cconad_lib AS dep4, pp.dep4_dsueic AS dep4_surface
"""
    + FROM_LOCAUX
    + """
JOIN pev ON pev.local10 = l10.local10
JOIN pevprincipale pp ON pp.pev = pev.pev
LEFT JOIN cconad c1 ON c1.cconad = pp.dep1_cconad
LEFT JOIN cconad c2 ON c2.cconad = pp.dep2_cconad
LEFT JOIN cconad c3 ON c3.cconad = pp.dep3_cconad
LEFT JOIN cconad c4 ON c4.cconad = pp.dep4_cconad
WHERE l.parcelle = {parcelle}
ORDER BY pp.pev, pp.dnudes
"""
)

SQL_DEPENDANCES = (
    """
SELECT
    pd.pev AS pev,
    pd.dnudes AS numero,
    cconad.cconad_lib AS nature,
    pd.dsudep AS surface,
    pd.dcimlc AS ponderation,
    pd.dcspdea AS situation_particuliere,
    pd.dmatgm AS murs, pd.dmatto AS toiture, pd.detent AS etat_entretien,
    pd.geaulc AS eau, pd.gelelc AS electricite, pd.gchclc AS chauffage,
    pd.dnbbai AS baignoires, pd.dnbdou AS douches, pd.dnblav AS lavabos, pd.dnbwc AS wc
"""
    + FROM_LOCAUX
    + """
JOIN pev ON pev.local10 = l10.local10
JOIN pevdependances pd ON pd.pev = pev.pev
LEFT JOIN cconad ON cconad.cconad = pd.cconad
WHERE l.parcelle = {parcelle}
ORDER BY pd.pev, pd.dnudes
"""
)

SQL_PROFESSIONNELS = (
    """
SELECT
    po.pev AS pev,
    Coalesce(po.dsupot, po.vsupot) AS surface_ponderee,
    po.dsup1 AS surface_principale,
    po.dsup2 AS surface_secondaire_couverte,
    po.dsup3 AS surface_secondaire_non_couverte,
    po.dsupk1 AS stationnement_couvert,
    po.dsupk2 AS stationnement_non_couvert,
    po.vsurzt AS surface_reelle
"""
    + FROM_LOCAUX
    + """
JOIN pev ON pev.local10 = l10.local10
JOIN pevprofessionnelle po ON po.pev = pev.pev
WHERE l.parcelle = {parcelle}
ORDER BY po.pev
"""
)

SQL_EXONERATIONS = (
    """
SELECT
    px.pev AS pev,
    ccolloc.ccolloc_lib AS collectivite,
    gnextl.gnextl_lib AS nature,
    px.jandeb AS annee_debut,
    px.janimp AS annee_retour,
    px.pexb AS taux,
    Coalesce(Cast(px.fcexba2 AS text), NULLIF(trim(px.fcexba), '')) AS fraction_vl,
    Coalesce(Cast(px.rcexba2 AS text), NULLIF(trim(px.rcexba), '')) AS revenu
"""
    + FROM_LOCAUX
    + """
JOIN pev ON pev.local10 = l10.local10
JOIN pevexoneration px ON px.pev = pev.pev
LEFT JOIN ccolloc ON ccolloc.ccolloc = px.ccolloc
LEFT JOIN gnextl ON gnextl.gnextl = px.gnextl
WHERE l.parcelle = {parcelle}
ORDER BY px.pev, px.dnuexb
"""
)


@dataclass
class Pev:
    values: Row
    habitations: list[Row] = field(default_factory=list)
    dependances: list[Row] = field(default_factory=list)
    professionnels: list[Row] = field(default_factory=list)
    exonerations: list[Row] = field(default_factory=list)


@dataclass
class Local:
    values: Row
    proprietaires: list[Row] = field(default_factory=list)
    pevs: list[Pev] = field(default_factory=list)

    @property
    def destinataire(self) -> str:
        names = [p["nom"] for p in self.proprietaires if p.get("destinataire") == "1" and p.get("nom")]
        return ", ".join(names)


def load_locaux(
    connector: QgsAbstractDatabaseProviderConnection, connection_params: dict[str, str], parcelle: str
) -> list[Local]:
    """The locaux of the parcel, with their owners and their PEV"""

    def fetch(sql: str) -> list[Row]:
        return fetch_rows(connector, connection_params, sql, parcelle=parcelle)

    locaux = {row["local10"]: Local(row) for row in fetch(SQL_LOCAUX)}
    for row in fetch(SQL_PROPRIETAIRES):
        if row["local10"] in locaux:
            locaux[row["local10"]].proprietaires.append(row)

    pevs = {}
    for row in fetch(SQL_PEVS):
        if row["local10"] in locaux:
            pevs[row["pev"]] = Pev(row)
            locaux[row["local10"]].pevs.append(pevs[row["pev"]])
    for sql, attribute in (
        (SQL_HABITATIONS, "habitations"),
        (SQL_DEPENDANCES, "dependances"),
        (SQL_PROFESSIONNELS, "professionnels"),
        (SQL_EXONERATIONS, "exonerations"),
    ):
        for row in fetch(sql):
            if row["pev"] in pevs:
                getattr(pevs[row["pev"]], attribute).append(row)

    return list(locaux.values())


# Description of the tables

MURS = {
    "1": "pierre",
    "2": "meulière",
    "3": "béton",
    "4": "briques",
    "5": "aggloméré",
    "6": "bois",
    "9": "autres",
}
TOITURES = {"1": "tuiles", "2": "ardoises", "3": "zinc aluminium", "4": "béton", "9": "autres"}
ENTRETIEN = {
    "0": "indéterminé",
    "1": "bon",
    "2": "assez bon",
    "3": "passable",
    "4": "médiocre",
    "5": "mauvais",
}


def dependances_incorporees(row: Row) -> str:
    """The dependances described with the habitation, like a garage or a cellar"""
    names = []
    for i in range(1, 5):
        if row.get(f"dep{i}"):
            area = row.get(f"dep{i}_surface")
            names.append(f"{row[f'dep{i}']} ({surface(str(area))})" if area else row[f"dep{i}"])
    return ", ".join(names)


def numero_voirie_et_voie(row: Row) -> str:
    return " ".join(v for v in (row.get("numero_voirie"), row.get("voie")) if v).strip()


SUMMARY = Section(
    "locaux",
    "",
    [
        Field("Invariant", "invariant"),
        Field("Bât.", "batiment"),
        Field("Entrée", "entree"),
        Field("Niveau", "niveau"),
        Field("Porte", "porte"),
        Field("Type", "type"),
        Field("Nature", "nature"),
        Field("Année de construction", "annee_construction"),
        Field("Date de l'acte", "date_acte", format=date_fr),
        Field("Destinataire de l'avis", "destinataire"),
        Field("Nombre de PEV", "nombre_pev"),
    ],
)

LOCAL = Section(
    "local",
    "Description générale",
    [
        Field("Invariant", "invariant"),
        Field("Bâtiment", "batiment"),
        Field("Entrée", "entree"),
        Field("Niveau", "niveau"),
        Field("Porte", "porte"),
        Field("Adresse", "adresse", value=numero_voirie_et_voie),
        Field("Compte propriétaire", "comptecommunal"),
        Field("Date de l'acte", "date_acte", format=date_fr),
        Field("Type", "type"),
        Field("Nature", "nature"),
        Field("Construction", "construction"),
        Field("Année de construction", "annee_construction"),
        Field("Niveaux", "niveaux", format=number),
    ],
    layout="list",
)

PROPRIETAIRES = Section(
    "local.proprietaires",
    "Propriétaires",
    [
        Field("Numéro", "numero"),
        Field("Code", "code"),
        Field("Nom", "nom"),
        Field("Adresse", "adresse"),
        Field("Date de naissance", "date_naissance", sensitive="birth", mask=DATE_MASK, format=date_fr),
        Field("Lieu de naissance", "lieu_naissance", sensitive="birth"),
        Field("Droit", "droit"),
        Field("Démembrement", "demembrement"),
    ],
)

PEVS = Section(
    "local.pevs",
    "Parties d'évaluation (PEV)",
    [
        Field("PEV", "numero"),
        Field("Affectation", "affectation"),
        Field("Lettre de série", "lettre_serie"),
        Field("Catégorie", "categorie"),
        Field("Coefficient d'entretien", "entretien", format=number),
        Field("Valeur locative", "valeur_locative", sensitive="revenue"),
        Field("VL imposable commune", "co_vlbaia", sensitive="revenue", visible=False),
        Field("Base commune", "co_bipevla", sensitive="revenue"),
        Field("VL imposable groupement", "gp_vlbaia", sensitive="revenue", visible=False),
        Field("Base groupement de communes", "gp_bipevla", sensitive="revenue"),
        Field("VL imposable TSE", "tse_vlbaia", sensitive="revenue", visible=False, optional=True),
        Field("Base TSE", "tse_bipevla", sensitive="revenue", optional=True),
        Field("VL imposable département", "de_vlbaia", sensitive="revenue", visible=False, optional=True),
        Field("Base département", "de_bipevla", sensitive="revenue", optional=True),
        Field("Exonérations", "nombre_exonerations"),
    ],
)

EVALUATION = Section(
    "pev.evaluation",
    "Évaluation",
    [
        Field("Valeur locative (valeur de référence)", "valeur_locative_reference", sensitive="revenue"),
        Field("Valeur locative (valeur de l'année)", "valeur_locative", sensitive="revenue"),
        Field("Exonération permanente", "exoneration_permanente", sensitive="exoneration", optional=True),
        Field("Numéro du local type", "local_type", optional=True),
        Field("Coefficient de situation générale", "situation_generale", optional=True),
        Field("Coefficient de situation particulière", "situation_particuliere", optional=True),
    ],
    layout="list",
)


def confort(optional: bool = False) -> list[Field]:
    """Elements of comfort, not displayed for dependances without them"""
    return [
        Field("Eau", "eau", format=yes_no, optional=optional),
        Field("Électricité", "electricite", format=yes_no, optional=optional),
        Field("Gaz", "gaz", format=yes_no, optional=True),
        Field("Chauffage central", "chauffage", format=yes_no, optional=optional),
        Field("Baignoires", "baignoires", format=number, optional=optional),
        Field("Douches", "douches", format=number, optional=optional),
        Field("Lavabos", "lavabos", format=number, optional=optional),
        Field("WC", "wc", format=number, optional=optional),
    ]


HABITATION = Section(
    "pev.habitation",
    "Habitation",
    [
        Field("Nombre de pièces", "pieces", format=number),
        Field("Pièces principales", "pieces_principales", format=number),
        Field("Surface des pièces", "surface_pieces", format=surface),
        Field("Salles à manger", "salles_a_manger", format=number),
        Field("Chambres", "chambres", format=number),
        Field("Cuisines de moins de 9 m²", "cuisines_moins_9", format=number),
        Field("Cuisines de plus de 9 m²", "cuisines_plus_9", format=number),
        Field("Salles d'eau", "salles_eau", format=number),
        Field("Pièces annexes", "pieces_annexes", format=number),
        Field("Dépendances incorporées", "dependances", value=dependances_incorporees, optional=True),
        Field("Matériaux des gros murs", "murs", format=codes(MURS)),
        Field("Matériaux des toitures", "toiture", format=codes(TOITURES)),
        Field("État d'entretien", "etat_entretien", format=label(ENTRETIEN), optional=True),
        *confort(),
    ],
    layout="list",
)

DEPENDANCES = Section(
    "pev.dependances",
    "Dépendances",
    [
        Field("N°", "numero"),
        Field("Nature", "nature"),
        Field("Surface réelle", "surface", format=surface),
        Field("Pondération", "ponderation", format=number),
        Field("Situation particulière", "situation_particuliere", optional=True),
        Field("Matériaux des gros murs", "murs", format=codes(MURS)),
        Field("Matériaux des toitures", "toiture", format=codes(TOITURES)),
        Field("État d'entretien", "etat_entretien", format=label(ENTRETIEN)),
        *confort(optional=True),
    ],
)

PROFESSIONNEL = Section(
    "pev.professionnel",
    "Local professionnel",
    [
        Field("Surface pondérée", "surface_ponderee", format=surface, optional=True),
        Field("Surface des parties principales", "surface_principale", format=surface, optional=True),
        Field(
            "Surface des parties secondaires couvertes",
            "surface_secondaire_couverte",
            format=surface,
            optional=True,
        ),
        Field(
            "Surface des parties secondaires non couvertes",
            "surface_secondaire_non_couverte",
            format=surface,
            optional=True,
        ),
        Field("Surface des stationnements couverts", "stationnement_couvert", format=surface, optional=True),
        Field(
            "Surface des stationnements non couverts",
            "stationnement_non_couvert",
            format=surface,
            optional=True,
        ),
        Field("Surface réelle", "surface_reelle", format=surface, optional=True),
    ],
    layout="list",
)

EXONERATIONS = Section(
    "pev.exonerations",
    "Exonérations",
    [
        Field("Collectivité", "collectivite", sensitive="exoneration"),
        Field("Nature", "nature", sensitive="exoneration"),
        Field("Année de début", "annee_debut", sensitive="exoneration"),
        Field("Année de retour à imposition", "annee_retour", sensitive="exoneration"),
        Field("Taux", "taux", sensitive="exoneration", format=percent),
        Field("Fraction de VL exonérée", "fraction_vl", sensitive="exoneration", format=number),
        Field("Revenu cadastral exonéré", "revenu", sensitive="exoneration", format=number),
    ],
)


def locaux_html(locaux: list[Local], options: DisplayOptions | None = None) -> str:
    options = options or DisplayOptions()
    count = len(locaux)
    text = "<h2>Locaux</h2>"
    if not locaux:
        return text + "<p>La parcelle ne contient aucun local</p>"
    text += f"<p>La parcelle contient {count} {'local' if count == 1 else 'locaux'}</p>"

    summary = [
        {**local.values, "destinataire": local.destinataire, "nombre_pev": str(len(local.pevs))}
        for local in locaux
    ]
    text += table_html(SUMMARY, summary, options)

    for local in locaux:
        title = ", ".join(v for v in (local.values.get("type"), numero_voirie_et_voie(local.values)) if v)
        text += f"<h3>Local {html.escape(local.values.get('invariant') or '')}"
        text += f" : {html.escape(title)}</h3>" if title else "</h3>"
        text += table_html(LOCAL, [local.values], options)
        text += table_html(PROPRIETAIRES, local.proprietaires, options)
        pev_rows = [{**pev.values, "nombre_exonerations": str(len(pev.exonerations))} for pev in local.pevs]
        text += table_html(PEVS, pev_rows, options)

        for pev in local.pevs:
            if not options.is_visible(PEVS):
                break
            title = " : ".join(v for v in (pev.values.get("numero"), pev.values.get("affectation")) if v)
            text += f"<h4>PEV {html.escape(title)}</h4>"
            text += table_html(EVALUATION, [pev.values], options, "h5")
            text += table_html(HABITATION, pev.habitations, options, "h5")
            text += table_html(DEPENDANCES, pev.dependances, options, "h5")
            text += table_html(PROFESSIONNEL, pev.professionnels, options, "h5")
            text += table_html(EXONERATIONS, pev.exonerations, options, "h5")
    return text
