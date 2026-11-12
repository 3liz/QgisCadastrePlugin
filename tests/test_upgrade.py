""" Message after an update of the plugin: the SQL commands creating the indexes of the fiche """

import pytest

import cadastre.upgrade

from cadastre.cadastre_database import CadastreDatabase
from cadastre.upgrade import indexes_sql, release_notes, upgrade_message, version_tuple

from .test_import_data import TEST_SCHEMA
from .test_majic_data import database, fetch  # noqa: F401


def test_version_tuple():
    """ Released versions are compared as numbers, a development version is ignored """
    assert version_tuple("2.5.2") == (2, 5, 2)
    assert version_tuple("v2.10.0") == (2, 10, 0)
    assert version_tuple("2.10.0") > version_tuple("2.5.2")  # type: ignore[operator]
    assert version_tuple("master") is None
    assert version_tuple("") is None
    assert version_tuple(None) is None


def test_upgrade_message():
    """ The message is displayed after an update from an older version only """
    message = upgrade_message("", "2.5.2")
    assert message is not None
    assert "idx_pev_local10" in message and "idx_lotslocaux_local00" in message
    assert upgrade_message("2.4.1", "2.5.2") is not None
    assert upgrade_message("2.4.1", "2.6.0") is not None
    # First installation, update from a version which displayed it, development version
    assert upgrade_message(None, "2.5.2") is None
    assert upgrade_message("2.5.2", "2.6.0") is None
    assert upgrade_message("", "master") is None
    assert upgrade_message("", "2.5.1") is None


def test_upgrade_messages(monkeypatch: pytest.MonkeyPatch):
    """ The messages of the versions since the previous one are displayed, the oldest first """
    monkeypatch.setattr(
        cadastre.upgrade,
        "UPGRADE_MESSAGES",
        {(2, 7): lambda: "<p>B</p>", (2, 5, 2): lambda: "<p>A</p>", (3, 0): lambda: "<p>C</p>"},
    )
    message = upgrade_message("2.4.1", "2.8.0")
    assert message is not None
    assert message.index("<p>A</p>") < message.index("<p>B</p>")
    assert "<p>C</p>" not in message
    assert "<h4>Version 2.7</h4>" in message
    message = upgrade_message("2.6.0", "3.0.0")
    assert message is not None
    assert "<p>A</p>" not in message and "<p>B</p>" in message and "<p>C</p>" in message


def test_release_notes():
    """ The release notes of the menu: the changelog if packaged, the link, and all the update messages """
    url = "https://docs.3liz.org/QgisCadastrePlugin/changelog/"
    text = release_notes("2.5.2", None, url)
    assert f'<a href="{url}">' in text
    assert "idx_pev_local10" in text
    text = release_notes("2.5.2", "Version 2.5.2:\n* Fix A\n* Fix B", url)
    assert "<b>Version 2.5.2:</b>" in text and "<li>Fix A</li><li>Fix B</li>" in text
    # A version older than the messages, a development version with all the messages
    assert "idx_pev_local10" not in release_notes("2.5.1", None, url)
    assert "idx_pev_local10" in release_notes("master", None, url)


def test_indexes_sql():
    """ The indexes of the tables of the fiche only, without the spatial indexes """
    sql = indexes_sql(postgis=True)
    assert "SET search_path = cadastre;" in sql
    assert "CREATE INDEX IF NOT EXISTS idx_pev_local10 ON pev (local10);" in sql
    assert "gist" not in sql and "geo_" not in sql
    assert sql.splitlines()[-1].startswith("ANALYZE local00")
    sql = indexes_sql(postgis=False)
    assert "search_path" not in sql
    assert sql.splitlines()[-1] == "ANALYZE;"


def test_indexes_sql_postgis(database: CadastreDatabase):  # noqa: F811
    """ The commands for PostgreSQL create a missing index and keep the existing ones """
    fetch(f"DROP INDEX {TEST_SCHEMA}.idx_pev_local10")
    # SET LOCAL in a transaction, so that the search_path of the connection is not changed
    sql = indexes_sql(postgis=True).replace("SET search_path = cadastre;", f"SET LOCAL search_path = {TEST_SCHEMA};")
    fetch(f"BEGIN; {sql} COMMIT;")
    rows = fetch(f"SELECT indexname FROM pg_indexes WHERE schemaname = '{TEST_SCHEMA}' AND tablename = 'pev'")
    assert ["idx_pev_local10"] in rows
