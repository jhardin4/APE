from qtpy.QtCore import QObject, Signal, Property, Slot

from ..apparatus import AppInterface


class AppInterfaceObject(QObject):
    appInterfaceChanged = Signal()

    def __init__(self, parent=None):
        super(AppInterfaceObject, self).__init__(parent)
        self._app_interface = None

    @Property(AppInterface, notify=appInterfaceChanged)
    def appInterface(self):
        return self._app_interface

    @appInterface.setter
    def appInterface(self, new_interface):
        if new_interface == self._app_interface:
            return
        old_interface = self._app_interface
        self._app_interface = new_interface
        self.appInterfaceChanged.emit()

        if old_interface:
            old_interface.appImageChanged.disconnect(self.refresh)
        if new_interface:
            new_interface.appImageChanged.connect(self.refresh)
            self.refresh()

    @Slot()
    def refresh(self):
        pass
