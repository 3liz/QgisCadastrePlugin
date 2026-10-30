from pathlib import Path

import pytest

from qgis.core import QgsProviderRegistry, QgsSettings
from qgis.utils import spatialite_connect

from cadastre.cadastre_common_base import hasSpatialiteSupport
from cadastre.dialogs.database_widget import DatabaseWidget

SCHEMA = "cadastre_widget_test"


def pg_connection():
    # Do not keep the connection object, it is invalidated when connections are reloaded
    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    return metadata.findConnection("test_database")


@pytest.fixture()
def drop_schema():
    yield
    if SCHEMA in pg_connection().schemas():
        pg_connection().dropSchema(SCHEMA, True)


def test_no_database_type():
    widget = DatabaseWidget()

    assert widget.db_type is None
    assert widget.liDbConnection.count() == 0
    assert widget.database() is None
    assert not widget.liDbSchema.isEnabled()


def test_postgis():
    widget = DatabaseWidget()
    databases = []
    widget.databaseChanged.connect(databases.append)

    widget.liDbType.setCurrentIndex(1)

    assert widget.db_type == "postgis"
    assert widget.liDbConnection.currentText() == "test_database"
    assert widget.liDbSchema.isEnabled()
    assert "public" in [widget.liDbSchema.itemText(i) for i in range(widget.liDbSchema.count())]

    widget.liDbSchema.setCurrentIndex(widget.liDbSchema.findText("public"))
    database = widget.database()
    assert database is not None
    assert database.db_type == "postgis"
    assert database.connection_name == "test_database"
    assert database.schema == "public"
    assert databases[-1].schema == "public"

    # No creation tools by default
    assert widget.btDbCreateSchema.isHidden()
    assert widget.btCreateNewSpatialiteDb.isHidden()


def test_create_schema(drop_schema):
    widget = DatabaseWidget(creation_enabled=True)
    widget.liDbType.setCurrentIndex(1)
    assert not widget.btDbCreateSchema.isHidden()
    assert widget.btCreateNewSpatialiteDb.isHidden()

    databases = []
    widget.databaseChanged.connect(databases.append)
    widget.inDbCreateSchema.setText(SCHEMA)
    widget.btDbCreateSchema.click()

    assert SCHEMA in pg_connection().schemas()
    assert widget.liDbSchema.currentText() == SCHEMA
    assert widget.inDbCreateSchema.text() == ""
    assert databases[-1].schema == SCHEMA


@pytest.fixture()
def restore_settings():
    settings = QgsSettings()
    keys = ("cadastre/databaseType", "cadastre/connection", "cadastre/schema")
    values = {key: settings.value(key) for key in keys}
    yield
    for key, value in values.items():
        if value is None:
            settings.remove(key)
        else:
            settings.setValue(key, value)


def test_settings(drop_schema, restore_settings):
    pg_connection().createSchema(SCHEMA)
    widget = DatabaseWidget()
    widget.liDbType.setCurrentIndex(1)
    widget.liDbSchema.setCurrentIndex(widget.liDbSchema.findText(SCHEMA))
    widget.store_settings()

    other = DatabaseWidget()
    other.load_settings()

    assert other.db_type == "postgis"
    assert other.liDbConnection.currentText() == "test_database"
    assert other.database().schema == SCHEMA


@pytest.mark.skipif(not hasSpatialiteSupport(), reason="No Spatialite support")
def test_spatialite(tmp_path: Path):
    path = tmp_path / "widget test.sqlite"
    con = spatialite_connect(str(path), isolation_level=None)
    con.cursor().execute("SELECT InitSpatialMetadata(1)")
    con.close()

    settings = QgsSettings()
    key = "/SpatiaLite/connections/widget test.sqlite/sqlitepath"
    settings.setValue(key, str(path))
    try:
        widget = DatabaseWidget(creation_enabled=True)
        widget.liDbType.setCurrentIndex(widget.liDbType.findText("Spatialite"))
        widget.liDbConnection.setCurrentIndex(widget.liDbConnection.findText("widget test.sqlite"))

        assert not widget.btCreateNewSpatialiteDb.isHidden()
        assert widget.btDbCreateSchema.isHidden()
        assert not widget.liDbSchema.isEnabled()

        database = widget.database()
        assert database is not None
        assert database.db_type == "spatialite"
        assert database.schema == ""
        assert not database.structure().has_structure
        widget.close_connection()
    finally:
        settings.remove("/SpatiaLite/connections/widget test.sqlite")
