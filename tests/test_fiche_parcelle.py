""" Tabs Parcelle, Propriétaires and Subdivisions fiscales of the fiche parcellaire """

import pytest

from qgis.core import QgsVectorLayer

import cadastre.cadastre_common_base as common_utils

from cadastre.cadastre_common_base import SensitiveData

from .test_majic_data import COPROPRIETE, database, feature, fetch, parcelles  # noqa: F401


def item_html(
    parcelles: QgsVectorLayer, item: str, geo_parcelle: str, sensitive: SensitiveData | None = None  # noqa: F811
) -> str:
    params = common_utils.getConnectionParameterFromDbLayer(parcelles)
    connector = common_utils.getConnectorFromUri(params)
    return common_utils.getItemHtml(item, feature(parcelles, geo_parcelle), params, connector, sensitive)


def test_parcelle_majic(parcelles: QgsVectorLayer):  # noqa: F811
    text = item_html(parcelles, "parcelle_majic", COPROPRIETE)

    assert text.startswith("<h2>Parcelle</h2><table")
    assert "<tr><th>Code</th><td>A0107</td></tr>" in text
    assert "<tr><th>Commune</th><td>CORNILLON-CONFOUX</td></tr>" in text
    assert "<tr><th>Parcelle bâtie</th><td>Oui</td></tr>" in text
    assert "<tr><th>Surface cadastrale (contenance)</th><td>" in text
    assert " m²</td></tr><tr><th>Surface géographique</th><td>" in text


def test_parcelle_simple(parcelles: QgsVectorLayer):  # noqa: F811
    """ Without the MAJIC data, only the EDIGEO tables """
    text = item_html(parcelles, "parcelle_simple", COPROPRIETE)

    assert "<tr><th>Commune</th><td>CORNILLON-CONFOUX</td></tr>" in text
    assert "<th>Surface géographique</th>" in text
    assert "Parcelle bâtie" not in text
    assert "Surface cadastrale" not in text


def test_proprietaires(parcelles: QgsVectorLayer):  # noqa: F811
    text = item_html(parcelles, "proprietaires", COPROPRIETE)

    assert text.startswith("<h2>Propriétaires</h2><table")
    assert "COPROPRIETE LE CLOS DES OLIVIERS" in text
    assert "PROVENCE GESTION IMMOBILIERE" in text


def test_lots(parcelles: QgsVectorLayer):  # noqa: F811
    text = item_html(parcelles, "indivisions", COPROPRIETE)

    assert text.startswith("<h3>Lots de copropriété</h3>")
    # One line per owner of each lot
    for lot in range(1, 6):
        assert f"<tr><td>{lot:07d}</td>" in text
    assert "<td>2400/10000</td>" in text
    assert "<td>400/10000</td>" in text


def test_no_lots(parcelles: QgsVectorLayer):  # noqa: F811
    geo_parcelle = fetch("SELECT parcelle FROM cadastre.parcelle WHERE parcelle != '%s' LIMIT 1" % COPROPRIETE)[0][0]

    assert item_html(parcelles, "indivisions", geo_parcelle) == ""


@pytest.mark.parametrize("sensitive", [SensitiveData(), SensitiveData.full()], ids=["masked", "full"])
def test_subdivisions_exonerations(parcelles: QgsVectorLayer, sensitive: SensitiveData):  # noqa: F811
    """ The olive trees of the test data are exonerated """
    geo_parcelle = fetch(
        "SELECT s.parcelle FROM cadastre.suf s JOIN cadastre.sufexoneration se ON se.suf = s.suf ORDER BY 1 LIMIT 1"
    )[0][0]

    text = item_html(parcelles, "subdivisions", geo_parcelle, sensitive)

    assert text.startswith("<h2>Subdivisions fiscales</h2><table")
    assert "<h3>Exonérations</h3>" in text
    assert ("<td>100 %</td>" in text) == sensitive.exoneration
    assert ("<td>XXX</td>" in text) != sensitive.exoneration
