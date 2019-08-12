import logging

from qtpy.QtCore import Signal, Property, Slot

from GUI.main.ape.apparatus.app_image_data import AppImageData
from .app_interface_object import AppInterfaceObject

logger = logging.getLogger('ToolPathPlot')


class ToolPathPlot(AppInterfaceObject):
    toolpathsChanged = Signal()

    def __init__(self, parent=None):
        super(ToolPathPlot, self).__init__(parent)

        self._toolpaths = []

    @Slot()
    def refresh(self):
        if not self._app_interface:
            logger.debug("Cannot refresh without an appInterface")
            return

        self._toolpaths = []
        data: AppImageData = self._app_interface.app_image
        path = data.get_key('information/ProcedureData/Toolpath_Generate/toolpath')

        if path is not None and isinstance(path.value, list):
            self._toolpaths = list(range(len(path.value)))
        self.toolpathsChanged.emit()

    @Property(list, notify=toolpathsChanged)
    def toolpaths(self):
        return self._toolpaths
