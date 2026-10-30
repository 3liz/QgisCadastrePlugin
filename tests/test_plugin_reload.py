""" Load and unload the plugin several times, like the Plugin Reloader does """

from typing import Any

from qgis.core import QgsApplication, QgsProject
from qgis.gui import QgisInterface
from qgis.PyQt import sip
from qgis.PyQt.QtCore import QCoreApplication, QEvent
from qgis.PyQt.QtWidgets import QToolBar

from cadastre.cadastre_menu import CadastreMenu


def delete_later_objects():
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_reload(qgis_iface: QgisInterface, plugin: Any):
    main_window = qgis_iface.mainWindow()
    project = QgsProject.instance()
    registry = QgsApplication.processingRegistry()

    # The plugin loaded for the other tests has its own processing provider
    registry.removeProvider(plugin.provider)
    receivers = (
        project.receivers(project.layersRemoved),
        qgis_iface.receivers(qgis_iface.newProjectCreated),
    )

    old_docks = []
    try:
        for _ in range(3):
            menu = CadastreMenu(qgis_iface)
            menu.initGui()
            old_docks.append(menu.cadastre_search_dialog)
            menu.unload()
            delete_later_objects()

        menu = CadastreMenu(qgis_iface)
        menu.initGui()

        # Only one of each
        cadastre_menus = [a for a in main_window.menuBar().actions() if a.text() == "&Cadastre"]
        assert len(cadastre_menus) == 1
        assert len(main_window.findChildren(QToolBar, "cadastreToolbar")) == 1
        assert registry.providerById("cadastre") is not None

        # Previous search panels are deleted
        assert all(sip.isdeleted(dock) for dock in old_docks)
        assert not sip.isdeleted(menu.cadastre_search_dialog)

        # Signals are connected once
        assert project.receivers(project.layersRemoved) == receivers[0] + 1
        assert qgis_iface.receivers(qgis_iface.newProjectCreated) == receivers[1] + 1

        dock = menu.cadastre_search_dialog
        dock_receivers = dock.receivers(dock.visibilityChanged)
        menu.unload()

        # QGIS hides the dock widget when it is removed: the deleted search action must not be updated
        assert dock.receivers(dock.visibilityChanged) == dock_receivers - 1
        menu.updateSearchButton()
        delete_later_objects()

        # Everything has been removed
        assert not [a for a in main_window.menuBar().actions() if a.text() == "&Cadastre"]
        assert not main_window.findChildren(QToolBar, "cadastreToolbar")
        assert registry.providerById("cadastre") is None
        assert project.receivers(project.layersRemoved) == receivers[0]
        assert qgis_iface.receivers(qgis_iface.newProjectCreated) == receivers[1]
    finally:
        # Restore the processing provider for the other tests
        plugin.initProcessing()
