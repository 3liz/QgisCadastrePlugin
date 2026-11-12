""" Carte d'identité de la parcelle: data, masks of the sensitive data and PDF """

from pathlib import Path

from qgis.core import QgsAbstractDatabaseProviderConnection, QgsLayoutExporter, QgsProject, QgsVectorLayer

import cadastre.cadastre_common_base as common_utils

from cadastre.cadastre_common_base import SensitiveData
from cadastre.carte_identite import (
    LOCAUX,
    CarteIdentite,
    PROPRIETAIRES,
    build_layout,
    export_carte_identite,
    load_carte_identite,
    section_values,
)
from cadastre.fiche import DisplayOptions

from .test_majic_data import COPROPRIETE, database, parcelles  # noqa: F401


def connection(layer: QgsVectorLayer) -> tuple[QgsAbstractDatabaseProviderConnection, dict[str, str]]:
    """ The connection to the test database and its parameters, from the layer of the parcelles """
    params = common_utils.getConnectionParameterFromDbLayer(layer)
    connector = common_utils.getConnectorFromUri(params)
    assert connector is not None
    return connector, params


def column(fields: list, rows: list[list[str]], name: str) -> list[str]:
    """ The values of a column of the rows of a section """
    index = [f.name for f in fields].index(name)
    return [row[index] for row in rows]


def test_load(parcelles: QgsVectorLayer):  # noqa: F811
    """ The parcel, its owners and one row per local, with its lot and its share in the copropriété """
    carte = load_carte_identite(*connection(parcelles), COPROPRIETE)
    assert carte is not None
    assert carte.values["code"].strip() == "A0107"
    assert carte.values["annee"]
    assert carte.proprietaires
    assert len(carte.locaux) == 5
    assert all(
        local["nom_adresse_invariant_cle"] and local["local10"] for local in carte.locaux
    )


def test_owners(parcelles: QgsVectorLayer):  # noqa: F811
    """ A local with several owners has one row, with all its owners """
    carte = load_carte_identite(*connection(parcelles), COPROPRIETE)
    assert carte is not None
    # Lot 1 belongs to M and MME CHABAUD
    rows = [local for local in carte.locaux if local["lots"] == "Lot 1 : 2400/10000"]
    assert len(rows) == 1
    text = rows[0]["nom_adresse_invariant_cle"]
    assert "M CHABAUD/GILLES" in text
    assert "MME CHABAUD/MONIQUE" in text
    # The invariant and its key are on the last line
    assert text.splitlines()[-1] == f"{rows[0]['invariant']} {rows[0]['cle']}"
    # Démembrement, nature and occupation on 3 lines, each value written once
    assert len(rows[0]["demembrement_nature_occupation"].splitlines()) == 3

    # assert load_carte_identite(*connection(parcelles), "1320290000Z9999") is None


def test_masks(parcelles: QgsVectorLayer):  # noqa: F811
    """ The sensitive data are masked without the right, like in the fiche parcellaire """
    carte = load_carte_identite(*connection(parcelles), COPROPRIETE)
    assert carte is not None

    fields, rows = section_values(PROPRIETAIRES, carte.proprietaires, DisplayOptions())
    assert set(column(fields, rows, "date_naissance")) <= {"XX/XX/XXXX", ""}
    fields, rows = section_values(LOCAUX, carte.locaux, DisplayOptions())
    # assert set(column(fields, rows, "valeur_locative")) <= {"XXX", ""}
    # assert set(column(fields, rows, "exonerations")) <= {"XXX", ""}

    options = DisplayOptions(sensitive=SensitiveData.full())
    fields, rows = section_values(PROPRIETAIRES, carte.proprietaires, options)
    assert "XX/XX/XXXX" not in column(fields, rows, "date_naissance")
    fields, rows = section_values(LOCAUX, carte.locaux, options)
    # assert "XXX" not in column(fields, rows, "valeur_locative")
    # assert any(column(fields, rows, "valeur_locative"))


def test_pdf(parcelles: QgsVectorLayer, tmp_path: Path, output_dir: Path):  # noqa: F811
    """ The PDF of the carte d'identité, and an image of its first page to look at """
    path = export_carte_identite(
        QgsProject.instance(), *connection(parcelles), COPROPRIETE, tmp_path, SensitiveData.full()
    )
    assert path is not None
    assert path.read_bytes().startswith(b"%PDF")

    carte = load_carte_identite(*connection(parcelles), COPROPRIETE)
    assert carte is not None
    layout = build_layout(QgsProject.instance(), carte, SensitiveData())
    assert layout.pageCollection().pageCount() >= 1
    image = output_dir / "carte_identite.png"
    settings = QgsLayoutExporter.ImageExportSettings()
    settings.dpi = 100
    assert QgsLayoutExporter(layout).exportToImage(str(image), settings) == QgsLayoutExporter.ExportResult.Success


def test_pages(output_dir: Path):
    """ A long table continues on the next pages, and the page numbers are written """
    locaux = [
        {
            "nom_adresse_invariant_cle": f"M DUPONT/JEAN, MME DUPONT/MARIE, SCI DES OLIVIERS DU MIDI ET DE PROVENCE 02900{i:05d}",
            "demembrement_nature_occupation": "Appartement",
            "lots": "1990  10/1000",
            "surface": "75", "categorie": "5",
            "batiment": "A", "entree": "01", "niveau": "02", "porte": f"{i:05d}",
        }
        for i in range(80)
    ]
    carte = CarteIdentite(
        "1320290000A0001",
        {
            "code": "A0001",
            "commune": "TEST",
            "adresse": "10 RUE MACHIN",
            "contenance": "100",
            "pourcentage_bati": "15",
        },
        [],
        locaux
    )
    layout = build_layout(QgsProject.instance(), carte, SensitiveData.full())
    pages = layout.pageCollection().pageCount()
    assert pages > 2
    image = output_dir / "carte_identite_pages.png"
    settings = QgsLayoutExporter.ImageExportSettings()
    settings.dpi = 100
    settings.pages = [1]
    assert QgsLayoutExporter(layout).exportToImage(str(image), settings) == QgsLayoutExporter.ExportResult.Success
