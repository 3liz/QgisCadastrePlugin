__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


from qgis.core import QgsMapLayer, QgsProject

import cadastre.cadastre_common_base as common_utils


class CadastreCommon:
    """Aliases to the functions of cadastre_common_base, kept for compatibility."""

    # Bind as class properties for compatibility
    hasSpatialiteSupport = common_utils.hasSpatialiteSupport
    openFile = common_utils.openFile

    # Bind as class properties for compatibility
    @staticmethod
    def getLayerFromLegendByTableProps(*args, **kwargs) -> QgsMapLayer:
        return common_utils.getLayerFromLegendByTableProps(QgsProject.instance(), *args, **kwargs)

    getConnectionParameterFromDbLayer = common_utils.getConnectionParameterFromDbLayer
    setSearchPath = common_utils.setSearchPath
    fetchDataFromSqlQuery = common_utils.fetchDataFromSqlQuery
    getConnectorFromUri = common_utils.getConnectorFromUri

    # Bind as class properties for compatibility
    postgisToSpatialite = common_utils.postgisToSpatialite
    postgisToSpatialiteLocal10 = common_utils.postgisToSpatialiteLocal10

    # Bind as class properties for compatibility
    getCompteCommunalFromParcelleId = common_utils.getCompteCommunalFromParcelleId
    getProprietaireComptesCommunaux = common_utils.getProprietaireComptesCommunaux
    getItemHtml = common_utils.getItemHtml
