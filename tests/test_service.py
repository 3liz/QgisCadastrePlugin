""" Cadastre tests
"""
from qgis.server import QgsServerInterface

from .core.client import Client

# XXX Do not mix server test and desktop tests
#def test_service_exists(qgis_server_iface: QgsServerInterface):
#    """  Test that the cadastre service is registered
#    """
#    registry = qgis_server_iface.serviceRegistry()
#    service = registry.getService('CADASTRE')
#    assert service is not None


