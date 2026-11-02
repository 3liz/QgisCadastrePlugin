""" Parameters of the fiche parcellaire: options of the plugin and table cadastre_parametre_fiche_parcelle """

from typing import Iterator

import pytest

from qgis.core import QgsVectorLayer
from qgis.PyQt.QtCore import Qt

import cadastre.cadastre_common_base as common_utils

from cadastre.cadastre_common_base import SensitiveData
from cadastre.cadastre_database import CadastreDatabase
from cadastre.dialogs.fiche_parameters_widget import FicheParametersWidget
from cadastre.fiche_parametres import (
    TABLE,
    complete_table,
    options_from_visibility,
    parameters,
    read_settings,
    visibility_from_options,
    write_settings,
    write_table,
)

from .test_majic_data import COPROPRIETE, database, feature, fetch, parcelles  # noqa: F401


@pytest.fixture
def settings() -> Iterator[None]:
    """ Restore the options of the plugin after the test """
    hidden, shown = read_settings()
    write_settings(set(), set())
    yield
    write_settings(hidden, shown)


def item_html(parcelles: QgsVectorLayer, item: str, sensitive: SensitiveData | None = None) -> str:  # noqa: F811
    params = common_utils.getConnectionParameterFromDbLayer(parcelles)
    connector = common_utils.getConnectorFromUri(params)
    return common_utils.getItemHtml(item, feature(parcelles, COPROPRIETE), params, connector, sensitive)


def set_visible(key: str, visible: bool):
    fetch(f"UPDATE cadastre.{TABLE} SET visible = {visible} WHERE cle = '{key}'")


# Without database


def test_parameters():
    """ One parameter per section and per field, each section is followed by its fields """
    result = parameters()

    assert len(result) == 159
    assert len({p.key for p in result}) == len(result)
    assert [p.order for p in result] == list(range(1, len(result) + 1))
    sections = {p.key for p in result if not p.field}
    assert len(sections) == 14
    for p in result:
        if p.field:
            assert p.key.rsplit(".", 1)[0] in sections
    vlbaia = next(p for p in result if p.key == "local.pevs.co_vlbaia")
    assert (vlbaia.tab, vlbaia.section, vlbaia.sensitive, vlbaia.default) == (
        "Locaux", "Parties d'évaluation (PEV)", "revenue", False
    )


def test_visibility_options():
    visibility = visibility_from_options({"parcelle.commune", "local.proprietaires"}, {"local.pevs.co_vlbaia"})

    assert not visibility["parcelle.commune"]
    assert not visibility["local.proprietaires"]
    assert visibility["local.pevs.co_vlbaia"]
    assert not visibility["local.pevs.gp_vlbaia"]
    assert visibility["parcelle.code"]
    # Only the differences with the defaults are stored in the options
    assert options_from_visibility(visibility) == (
        {"parcelle.commune", "local.proprietaires"}, {"local.pevs.co_vlbaia"}
    )


def test_widget(qgis_iface):
    widget = FicheParametersWidget()
    assert widget.visibility() == {p.key: p.default for p in parameters()}

    widget.set_visibility({"local.proprietaires": False, "local.pevs.co_vlbaia": True})
    assert not widget.visibility()["local.proprietaires"]
    assert widget.visibility()["local.pevs.co_vlbaia"]
    # The fields of a hidden section are disabled
    section = widget.items["local.proprietaires"]
    assert section.child(0).isDisabled()
    assert widget.items["local.proprietaires.nom"].checkState(0) == Qt.CheckState.Checked

    widget.reset()
    assert widget.visibility() == {p.key: p.default for p in parameters()}
    assert not section.child(0).isDisabled()


# With the test database


def test_table_created_by_import(database: CadastreDatabase):  # noqa: F811
    rows = database.fetch(f"SELECT cle, visible FROM cadastre.{TABLE} ORDER BY ordre")

    assert len(rows) == len(parameters())
    visibility = {key: visible.lower() == "true" for key, visible in rows}
    assert visibility == {p.key: p.default for p in parameters()}


def test_table_completed(database: CadastreDatabase, settings):  # noqa: F811
    """ A new import keeps the parameters set in the database, and adds the missing ones """
    set_visible("parcelle.commune", False)
    fetch(f"DELETE FROM cadastre.{TABLE} WHERE cle = 'parcelle.code'")
    try:
        assert complete_table(database) == 1

        rows = dict(database.fetch(f"SELECT cle, visible FROM cadastre.{TABLE}"))
        assert rows["parcelle.commune"].lower() == "false"
        assert rows["parcelle.code"].lower() == "true"
        assert complete_table(database) == 0
    finally:
        set_visible("parcelle.commune", True)


def test_table_used_by_fiche(parcelles: QgsVectorLayer):  # noqa: F811
    set_visible("parcelle.commune", False)
    set_visible("lots", False)
    try:
        assert "<th>Commune</th>" not in item_html(parcelles, "parcelle_majic")
        assert "<th>Code</th>" in item_html(parcelles, "parcelle_majic")
        assert item_html(parcelles, "indivisions") == ""
    finally:
        set_visible("parcelle.commune", True)
        set_visible("lots", True)
    assert "<th>Commune</th>" in item_html(parcelles, "parcelle_majic")


def test_table_sensitive_data(parcelles: QgsVectorLayer):  # noqa: F811
    """ The table can hide a sensitive field, but never displays its value without the right """
    assert "XX/XX/XXXX" in item_html(parcelles, "indivisions")
    assert "XX/XX/XXXX" not in item_html(parcelles, "indivisions", SensitiveData.full())

    set_visible("lots.date_naissance", False)
    try:
        assert "<th>Date de naissance</th>" not in item_html(parcelles, "indivisions", SensitiveData.full())
    finally:
        set_visible("lots.date_naissance", True)


def test_settings_without_table(database: CadastreDatabase, parcelles: QgsVectorLayer, settings):  # noqa: F811
    """ Without the table, the options of the plugin are used """
    fetch(f"DROP TABLE cadastre.{TABLE}")
    try:
        write_settings({"parcelle.commune"}, set())
        assert "<th>Commune</th>" not in item_html(parcelles, "parcelle_majic")
        write_settings(set(), set())
        assert "<th>Commune</th>" in item_html(parcelles, "parcelle_majic")
    finally:
        # Created again from the options of the plugin
        assert complete_table(database) == len(parameters())


def test_write_table(database: CadastreDatabase, parcelles: QgsVectorLayer):  # noqa: F811
    """ The parameters of the options dialog replace those of the database """
    visibility = {p.key: p.default for p in parameters()}
    try:
        write_table(database, {**visibility, "parcelle.commune": False})
        assert "<th>Commune</th>" not in item_html(parcelles, "parcelle_majic")
        assert len(database.fetch(f"SELECT cle FROM cadastre.{TABLE}")) == len(parameters())
    finally:
        write_table(database, visibility)
