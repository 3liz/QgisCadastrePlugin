""" Cadastre tests
"""


def test_service_exists(client):
    """  Test that the cadastre service is registered
    """
    plugin = client.getplugin('cadastre')
    assert plugin is not None

    registry = plugin.serverIface.serviceRegistry()
    service = registry.getService('cadastre')
    assert service is not None


