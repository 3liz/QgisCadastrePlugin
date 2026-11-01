""" Locaux in the fiche parcellaire, described in cadastre/fiche_locaux.py """

import re

import pytest

from qgis.core import QgsVectorLayer

import cadastre.cadastre_common_base as common_utils

from cadastre.cadastre_common_base import SensitiveData
from cadastre.fiche import DisplayOptions, Field, Section, codes, date_fr, number, table_html
from cadastre.fiche_locaux import EXONERATIONS, PEVS, PROPRIETAIRES, Local, load_locaux, locaux_html

from .test_majic_data import COPROPRIETE, database, feature, fetch, parcelles  # noqa: F401


@pytest.fixture(scope="module")
def multiple_pev() -> tuple[str, str]:
    """ Parcel and invariant of the house with 2 PEV and 2 exonerations of the test data """
    rows = fetch(
        "SELECT l10.parcelle, l10.invar FROM cadastre.pev "
        "JOIN cadastre.local10 l10 ON l10.local10 = pev.local10 "
        "GROUP BY l10.parcelle, l10.invar HAVING count(*) > 1"
    )
    assert len(rows) == 1
    return tuple(rows[0])


def locaux(parcelles: QgsVectorLayer, geo_parcelle: str) -> list[Local]:  # noqa: F811
    params = common_utils.getConnectionParameterFromDbLayer(parcelles)
    connector = common_utils.getConnectorFromUri(params)
    return load_locaux(connector, params, geo_parcelle)


def test_load_multiple_pev(parcelles: QgsVectorLayer, multiple_pev: tuple[str, str]):  # noqa: F811
    geo_parcelle, invariant = multiple_pev
    result = locaux(parcelles, geo_parcelle)

    local = next(local for local in result if local.values["invariant"] == invariant)
    assert [pev.values["numero"] for pev in local.pevs] == ["001", "002"]
    habitation, garage = local.pevs
    assert len(habitation.habitations) == 1
    assert [e["collectivite"] for e in habitation.exonerations] == ["Commune", "Groupement de communes"]
    assert [float(e["taux"]) for e in habitation.exonerations] == [100, 50]
    assert not garage.exonerations
    assert [d["nature"] for d in garage.dependances] == ["Garage"]
    # The owners are listed once for the local, not once per PEV or exoneration
    assert local.proprietaires
    assert len({p["code"] for p in local.proprietaires}) == len(local.proprietaires)


def test_html_multiple_pev(parcelles: QgsVectorLayer, multiple_pev: tuple[str, str]):  # noqa: F811
    geo_parcelle, invariant = multiple_pev
    result = locaux(parcelles, geo_parcelle)

    text = locaux_html(result, DisplayOptions(sensitive=SensitiveData.full()))

    # One section per local, with its 2 PEV, whatever the number of exonerations
    assert len(re.findall(r"<h3>Local ", text)) == len(result)
    assert text.count(f"<h3>Local {invariant}") == 1
    count = len(result)
    assert f"La parcelle contient {count} {'local' if count == 1 else 'locaux'}</p>" in text
    assert "<h4>PEV 001 : Habitation</h4>" in text
    assert "<h4>PEV 002 : Habitation</h4>" in text
    assert "<td>100 %</td>" in text
    assert "<td>50 %</td>" in text
    assert "<td>Garage</td>" in text
    assert "XXX" not in text


def test_html_masked(parcelles: QgsVectorLayer, multiple_pev: tuple[str, str]):  # noqa: F811
    geo_parcelle, _ = multiple_pev

    text = locaux_html(locaux(parcelles, geo_parcelle))

    assert "<td>XX/XX/XXXX</td>" in text
    assert "<td>100 %</td>" not in text
    assert text.count("<td>XXX</td>") > 10


def test_copropriete(parcelles: QgsVectorLayer):  # noqa: F811
    result = locaux(parcelles, COPROPRIETE)

    text = locaux_html(result)

    assert len(result) == 5
    assert "La parcelle contient 5 locaux</p>" in text
    assert len(re.findall(r"<h3>Local \w+ : Appartement", text)) == 4
    # The syndic receives the tax notice of the garage of the copropriete
    assert "PROVENCE GESTION IMMOBILIERE" in text


def test_no_local(parcelles: QgsVectorLayer):  # noqa: F811
    geo_parcelle = fetch(
        "SELECT p.parcelle FROM cadastre.parcelle p "
        "LEFT JOIN cadastre.local00 l ON l.parcelle = p.parcelle WHERE l.local00 IS NULL ORDER BY 1 LIMIT 1"
    )[0][0]

    assert locaux_html(locaux(parcelles, geo_parcelle)) == "<h2>Locaux</h2><p>La parcelle ne contient aucun local</p>"


def test_get_item_html(parcelles: QgsVectorLayer, multiple_pev: tuple[str, str]):  # noqa: F811
    """ The item used by the dialog and by the GetHtml request of the server """
    geo_parcelle, invariant = multiple_pev
    params = common_utils.getConnectionParameterFromDbLayer(parcelles)
    connector = common_utils.getConnectorFromUri(params)

    text = common_utils.getItemHtml("locaux", feature(parcelles, geo_parcelle), params, connector)

    assert f"<h3>Local {invariant}" in text
    assert 'class="table table-condensed table-striped"' in text


# Without database


SECTION = Section(
    "test",
    "Test",
    [
        Field("Nom", "nom"),
        Field("Revenu", "revenu", sensitive="revenue"),
        Field("Caché", "cache", visible=False),
        Field("Ancien", "ancien", optional=True),
    ],
)
ROWS = [{"nom": "A & B", "revenu": "120", "cache": "x", "ancien": None}, {"nom": "C", "revenu": None}]


def test_table_masks():
    text = table_html(SECTION, ROWS, DisplayOptions())

    assert text.startswith("<h4>Test</h4><table")
    assert "<th>Nom</th><th>Revenu</th></tr>" in text
    # Escaped, masked when it exists, empty otherwise
    assert "<tr><td>A &amp; B</td><td>XXX</td></tr>" in text
    assert "<tr><td>C</td><td></td></tr>" in text


def test_table_options():
    options = DisplayOptions(SensitiveData(revenue=True), hidden=frozenset({"test.nom"}), shown=frozenset({"test.cache"}))

    text = table_html(SECTION, ROWS, options)

    assert "<th>Revenu</th><th>Caché</th></tr>" in text
    assert "<tr><td>120</td><td>x</td></tr>" in text
    assert table_html(SECTION, ROWS, DisplayOptions(hidden=frozenset({"test"}))) == ""
    assert table_html(SECTION, [], DisplayOptions()) == ""


def test_list_layout():
    section = Section("test", "", [Field("Nom", "nom"), Field("Revenu", "revenu")], layout="list")

    assert table_html(section, ROWS, DisplayOptions()) == (
        '<table class="table table-condensed table-striped" border=1 cellspacing=0 cellpadding=3 width="100%">'
        "<tr><th>Nom</th><td>A &amp; B</td></tr><tr><th>Revenu</th><td>120</td></tr></table>"
    )


@pytest.mark.parametrize(
    "value, expected", [("13082013", "13/08/2013"), ("1956-03-01", "01/03/1956"), ("2013", "2013")]
)
def test_date_fr(value: str, expected: str):
    assert date_fr(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [("05", "5"), ("1.00", "1"), ("326.18", "326.18"), ("326.10", "326.1"), ("1500000", "1500000"), ("A", "A")],
)
def test_number(value: str, expected: str):
    assert number(value) == expected


@pytest.mark.parametrize("value, expected", [("04", "briques"), ("14", "pierre, briques"), ("00", "indéterminé")])
def test_codes(value: str, expected: str):
    assert codes({"1": "pierre", "4": "briques"})(value) == expected


def test_sensitive_sections():
    """ The sensitive data of the locaux """
    assert {f.name for f in PROPRIETAIRES.fields if f.sensitive} == {"date_naissance", "lieu_naissance"}
    assert all(f.sensitive == "exoneration" for f in EXONERATIONS.fields)
    assert {f.name for f in PEVS.fields if f.sensitive == "revenue"} >= {"valeur_locative", "co_bipevla"}
