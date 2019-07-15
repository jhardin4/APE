import logging

from qtpy.QtWidgets import QInputDialog, QLineEdit
from qtpy.QtCore import QObject, Signal, Property, Slot, QUrl

import Procedures
import GUI.TemplateGUIs as tGUIs

from .app_image_data import AppImageData, AppImageDataWalker
from ..nodes import GuiNode

logger = logging.getLogger('AppInterface')


class AppInterface(QObject):

    _gui_node: GuiNode
    guiNodeChanged = Signal()
    appImageChanged = Signal()
    eprocsChanged = Signal()
    watchedChanged = Signal()

    def __init__(self, parent=None):
        super(AppInterface, self).__init__(parent)

        self._gui_node = None
        self._app_image = AppImageData(name='root')
        self._eprocs = {}
        self._watched = []

    @Property(GuiNode, notify=guiNodeChanged)
    def guiNode(self):
        return self._gui_node

    @guiNode.setter
    def guiNode(self, value):
        if value == self._gui_node:
            return
        self._gui_node = value
        self.guiNodeChanged.emit()

    @Slot()
    def refresh(self):
        if not self._gui_node:
            logger.warning('Cannot refresh without guiNode')
            return

        logger.debug('starting serial clone')
        data = self._gui_node.apparatus.serialClone()
        self._app_image = AppImageData.from_dict(data, 'root')

        logger.debug(f'serial clone completed {self._app_image}')

        self.appImageChanged.emit()

    @property
    def app_image(self):
        return self._app_image

    @property
    def eprocs(self):
        return self._eprocs

    @Slot(str, str, result=int)
    def findAndReplace(self, find, replace):
        count = 0
        for item in AppImageDataWalker(self._app_image):
            if item.value == find:
                item.value = replace
                count += 1
        self.appImageChanged.emit()
        return count

    @Slot(bool)
    def connectAll(self, simulation):
        if not self._gui_node:
            logger.warning('Cannot connectAll without guiNode')
            return

        self._gui_node.apparatus.Connect_All(simulation=simulation)
        for device in self._app_image['devices'].values():
            device.set_key('Connected', True)
        self.appImageChanged.emit()

    @Slot()
    def disconnectAll(self):
        if not self._gui_node:
            logger.warning('Cannot disconnectAll without guiNode')
            return

        self._gui_node.apparatus.Disconnect_All()
        for device in self._app_image['devices'].values():
            device.set_key('Connected', False)
        self.appImageChanged.emit()

    @Slot()
    def refreshEprocs(self):
        if not self._gui_node:
            logger.warning('Cannot fetch eprocs without guiNode')
            return

        logger.debug('fetching EProcs')
        epl_dict = {}
        epl = self._gui_node.executor.getDevices('procexec')
        for device in epl:
            eprocs = self._gui_node.executor.getEprocs(device, 'procexec')
            epl_dict[device] = eprocs
        logger.debug(f'Eprocs fetched {epl_dict}')
        self._eprocs = epl_dict
        self.eprocsChanged.emit()

    @Slot(str, str, result=list)
    def getRequirements(self, device, procedure):
        if not self._gui_node:
            logger.warning('Cannot fetch requirements without guiNode')
            return

        name = f'{device}_{procedure}'
        if name in dir(Procedures):
            f = getattr(Procedures, name)(
                self._gui_node.apparatus, self._gui_node.executor
            )
            return [{'key': k, "value": v} for k, v in f.requirements.items()]
        else:
            reqs = self._gui_node.executor.getRequirements(
                device, procedure, 'procexec'
            )
            return [{'key': k, 'value': ''} for k in reqs]

    @Slot()
    @Slot(bool)
    def startTemplate(self, simulation=True):
        if not self._gui_node:
            logger.warning('Cannot start template without guiNode')
            return

        # Get list of templates
        files = dir(tGUIs)
        GUIlist = []
        for name in files:
            if '__' not in name:
                GUIlist.append(name)
        # Ask user to select template
        message = 'Name of the Template to be used.'
        d = 0
        options = GUIlist
        tName, ok = QInputDialog.getItem(None, 'Input', message, options, d, False)
        if not ok:
            return
        try:
            tGUI = getattr(tGUIs, tName)
            args, kwargs = tGUI()
        except AttributeError:
            message = 'That template was not found.'
            tName, ok = QInputDialog.getText(None, 'Input', message, QLineEdit.Normal)
            args = ()
            kwargs = dict()
        self._gui_node.apparatus.applyTemplate(tName, args=args, kwargs=kwargs)
        self.refresh()

    @Property(list, notify=watchedChanged)
    def watched(self):
        return self._watched

    @watched.setter
    def watched(self, value):
        if value == self._watched:
            return
        self._watched = value
        self.watchedChanged.emit()

    @Slot(str)
    def updateValue(self, key):
        if not self._gui_node:
            logger.warning('Cannot update value guiNode')
            return

        item = self._app_image.get_key(key)
        if item is None:
            logger.warning('cannot update key {}: not found'.format(key))
            return

        logger.debug('updating key {}'.format(key))
        value = self._gui_node.apparatus.getValue(key.split('/'))
        item.value = value
        logger.debug('update complete: {}'.format(value))

    @Slot()
    def updateWatched(self):
        for watched in self._watched:
            self.updateValue(watched['key'])

    @Slot(QUrl)
    def saveAs(self, url):
        pass
