"""Import the fictitious test data of the plugin, to generate the documentation of the database with SchemaSpy.

Run by `make schemaspy` in the service schemaspy-import of docker-compose.yml: the structure of the schema
cadastre is created by the import of the plugin itself, with the EDIGEO and MAJIC data of the tests
(commune 13029, the MAJIC data are FICTITIOUS). SchemaSpy then documents this schema.
"""

import shutil
import sys
import tempfile

from pathlib import Path

from qgis.core import QgsApplication, QgsProviderRegistry

# Name of the QGIS connection to the database of docker-compose.yml, and schema documented by SchemaSpy
CONNECTION = "schemaspy"
URI = "host=db port=5432 dbname=gis user=docker password=docker"
SCHEMA = "cadastre"
# Data of the tests of the plugin
FIXTURES = Path("/src/tests/fixtures")
INSEE = "13029"


def import_data():
    """Import the EDIGEO and MAJIC test data of the plugin in the schema SCHEMA, replacing it"""
    # Imported here, the plugin needs a QgsApplication
    from cadastre.cadastre_database import CadastreDatabase
    from cadastre.cadastre_import import ImportOptions, cadastreImport
    from cadastre.definitions import MAXIMUM_YEAR
    from cadastre.feedback import CadastreFeedback

    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    # The user and the password are only stored with saveUsername and savePassword
    metadata.saveConnection(
        metadata.createConnection(URI, {"saveUsername": True, "savePassword": True}), CONNECTION
    )
    connection = metadata.findConnection(CONNECTION)
    connection.executeSql(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE")
    connection.createSchema(SCHEMA)

    # The import writes next to the source files: they are copied in a temporary directory
    with tempfile.TemporaryDirectory() as tmp:
        majic = shutil.copytree(FIXTURES / "majic" / INSEE, Path(tmp) / "majic")
        edigeo = shutil.copytree(FIXTURES / "edigeo" / INSEE, Path(tmp) / "edigeo")
        options = ImportOptions(
            database=CadastreDatabase.from_connection("postgis", CONNECTION, SCHEMA),
            data_version=str(MAXIMUM_YEAR),
            data_year=str(MAXIMUM_YEAR),
            lot="1",
            departement="13",
            direction="2",
            majic_source_dir=str(majic),
            edigeo_source_dir=str(edigeo),
            edigeo_source_proj="EPSG:2154",
            edigeo_target_proj="EPSG:2154",
        )
        if not cadastreImport(options, CadastreFeedback()).run():
            sys.exit("The import of the test data failed")
    print(f"Test data imported in the schema {SCHEMA}")


if __name__ == "__main__":
    app = QgsApplication([], False)
    app.initQgis()
    import_data()
    app.exitQgis()
