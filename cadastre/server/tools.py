__copyright__ = 'Copyright 2021, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'

import configparser

from pathlib import Path

from qgis.core import Qgis, QgsMessageLog


def version() -> str:
    """ Returns the plugin current version. """
    file_path = Path(__file__).parent.parent.joinpath('metadata.txt')
    config = configparser.ConfigParser()
    try:
        config.read(file_path, encoding='utf8')
    except UnicodeDecodeError:
        # Issue LWC https://github.com/3liz/lizmap-web-client/issues/1908
        # Maybe a locale issue ?
        # Do not use logger here, circular import
        # noinspection PyTypeChecker
        QgsMessageLog.logMessage(
            "Error, an UnicodeDecodeError occurred while reading the metadata.txt. Is the locale "
            "correctly set on the server ?",
            "cadastre", Qgis.Critical)
        return 'NULL'
    else:
        return config["general"]["version"]
