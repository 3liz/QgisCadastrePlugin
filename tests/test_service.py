""" Cadastre tests
"""
import pytest

from qgis.server import QgsServerInterface

from cadastre.cadastre_common_base import SensitiveData
from cadastre.server.cadastre_service import sensitive_data

from .core.client import Client

# XXX Do not mix server test and desktop tests
#def test_service_exists(qgis_server_iface: QgsServerInterface):
#    """  Test that the cadastre service is registered
#    """
#    registry = qgis_server_iface.serviceRegistry()
#    service = registry.getService('CADASTRE')
#    assert service is not None




@pytest.mark.parametrize(
    "params, full",
    [
        ({}, False),
        ({"ADVANCED": "f"}, False),
        ({"ADVANCED": "false"}, False),
        ({"ADVANCED": "t"}, True),
        ({"ADVANCED": "TRUE"}, True),
        ({"ADVANCED": "1"}, True),
    ],
)
def test_sensitive_data(params: dict[str, str], full: bool):
    """ ADVANCED gives access to all the sensitive data, nothing by default """
    expected = SensitiveData.full() if full else SensitiveData()
    assert sensitive_data(params) == expected
