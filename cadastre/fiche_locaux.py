"""Locaux of a parcel in the fiche parcellaire: a summary table, then the details of each local.

The data is read by one query per level (locaux, parties d'évaluation (PEV), descriptions of the PEV,
exonérations, owners), filtered on the parcel, then grouped in Python. The queries are the files
cadastre/sql/fiche/locaux*.sql:

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
    DisplayOptions,
    Field,
    Row,
    Section,
    codes,
    date_fr,
    fetch_rows,
    load_sql,
    label,
    number,
    percent,
    surface,
    table_html,
    yes_no,
)
from cadastre.fiche_parcelle import proprietaires_section


@dataclass
class Pev:
    """A partie d'évaluation (PEV) of a local, with the rows describing it"""

    # Row of fiche/locaux_pevs.sql
    values: Row
    habitations: list[Row] = field(default_factory=list)
    dependances: list[Row] = field(default_factory=list)
    professionnels: list[Row] = field(default_factory=list)
    exonerations: list[Row] = field(default_factory=list)


@dataclass
class Local:
    """A local of the parcel, with its owners and its PEV"""

    # Row of fiche/locaux.sql
    values: Row
    # Rows of fiche/locaux_proprietaires.sql
    proprietaires: list[Row] = field(default_factory=list)
    pevs: list[Pev] = field(default_factory=list)

    @property
    def destinataire(self) -> str:
        """Return the names of the owners receiving the tax notice, separated by commas"""
        names = [p["nom"] for p in self.proprietaires if p.get("destinataire") == "1" and p.get("nom")]
        return ", ".join(names)


def load_locaux(
    connector: QgsAbstractDatabaseProviderConnection, connection_params: dict[str, str], parcelle: str
) -> list[Local]:
    """Read the locaux of the parcel, with their owners, their PEV and the descriptions of the PEV.

    Each query returns the rows of one level for the whole parcel, they are attached to their local
    or to their PEV by their identifier (local10 or pev).

    :param connector: The connection to the database.
    :param connection_params: The parameters of the connection, see fetch_rows.
    :param parcelle: The identifier of the parcel, like 1320290000A0107.
    :return: The locaux, in the order of the building, the entrance, the level and the door.
    """

    def fetch(name: str) -> list[Row]:
        return fetch_rows(connector, connection_params, load_sql(f"fiche/{name}"), parcelle=parcelle)

    # The locaux, by their identifier local10
    locaux = {row["local10"]: Local(row) for row in fetch("locaux")}
    for row in fetch("locaux_proprietaires"):
        if row["local10"] in locaux:
            locaux[row["local10"]].proprietaires.append(row)

    # The PEV, by their identifier pev, attached to their local
    pevs = {}
    for row in fetch("locaux_pevs"):
        if row["local10"] in locaux:
            pevs[row["pev"]] = Pev(row)
            locaux[row["local10"]].pevs.append(pevs[row["pev"]])
    # The rows describing the PEV, attached to their PEV
    for name, attribute in (
        ("locaux_habitations", "habitations"),
        ("locaux_dependances", "dependances"),
        ("locaux_professionnels", "professionnels"),
        ("locaux_exonerations", "exonerations"),
    ):
        for row in fetch(name):
            if row["pev"] in pevs:
                getattr(pevs[row["pev"]], attribute).append(row)

    return list(locaux.values())


# Description of the tables

# Labels of the codes of the MAJIC description (articles 40 and 60 of the fichier des propriétés bâties)
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
    """Return the dependances incorporated in the habitation, like "Garage (15 m²), Cave (8 m²)".

    :param row: A row of fiche/locaux_habitations.sql, with the 4 dependances dep1 to dep4 and their surfaces.
    :return: The labels and the surfaces of the dependances, separated by commas.
    """
    names = []
    for i in range(1, 5):
        if row.get(f"dep{i}"):
            area = row.get(f"dep{i}_surface")
            names.append(f"{row[f'dep{i}']} ({surface(str(area))})" if area else row[f"dep{i}"])
    return ", ".join(names)


def numero_voirie_et_voie(row: Row) -> str:
    """Return the address of a local, like "22 VC MONTEE DES AIRES", from a row of fiche/locaux.sql"""
    return " ".join(v for v in (row.get("numero_voirie"), row.get("voie")) if v).strip()


# Summary of the locaux: one line per local, the number of PEV and the destinataire are computed
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

# Description of a local
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

PROPRIETAIRES = proprietaires_section("local.proprietaires")

# PEV of a local: one line per PEV, with its bases d'imposition by collectivité.
# The parts of the valeur locative imposable (vlbaia) are hidden by default.
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

# Evaluation of a PEV
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
    """Create the fields of the elements of comfort: water, electricity, heating, bathrooms...

    :param optional: True to hide the elements which are empty, like for a garage.
    :return: The fields, added to the sections of the habitations and of the dependances.
    """
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


# Description of the PEV of a habitation
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

# Dependances of a PEV: one line per dependance
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

# Description of the PEV of a professional local, the surfaces depend on the MAJIC format
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

# Exonerations of a PEV: one line per exoneration
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
    """Build the HTML of the tab Locaux.

    The tab contains the summary of the locaux, then for each local: its description, its owners,
    the table of its PEV, then for each PEV its evaluation, its description and its exonerations.

    :param locaux: The locaux of the parcel, see load_locaux.
    :param options: The fields to display and the sensitive data allowed.
    :return: The HTML of the tab.
    """
    options = options or DisplayOptions()
    count = len(locaux)
    text = "<h2>Locaux</h2>"
    if not locaux:
        return text + "<p>La parcelle ne contient aucun local</p>"
    text += f"<p>La parcelle contient {count} {'local' if count == 1 else 'locaux'}</p>"

    # Summary, with the values computed for each local
    summary = [
        {**local.values, "destinataire": local.destinataire, "nombre_pev": str(len(local.pevs))}
        for local in locaux
    ]
    text += table_html(SUMMARY, summary, options)

    for local in locaux:
        # Title like "Local 0290002178 : Maison, 22 VC MONTEE DES AIRES"
        title = ", ".join(v for v in (local.values.get("type"), numero_voirie_et_voie(local.values)) if v)
        text += f"<h3>Local {html.escape(local.values.get('invariant') or '')}"
        text += f" : {html.escape(title)}</h3>" if title else "</h3>"
        text += table_html(LOCAL, [local.values], options)
        text += table_html(PROPRIETAIRES, local.proprietaires, options)
        pev_rows = [{**pev.values, "nombre_exonerations": str(len(pev.exonerations))} for pev in local.pevs]
        text += table_html(PEVS, pev_rows, options)

        # Details of each PEV, not displayed if the table of the PEV is hidden
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
