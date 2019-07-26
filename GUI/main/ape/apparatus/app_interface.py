import logging

from qtpy.QtWidgets import QInputDialog, QLineEdit
from qtpy.QtCore import QObject, Signal, Property, Slot, QUrl

import GUI.TemplateGUIs as tGUIs

from .app_image_data import AppImageData, AppImageDataWalker
from ..nodes import GuiNode

logger = logging.getLogger('AppInterface')


class AppInterface(QObject):

    _gui_node: GuiNode
    guiNodeChanged = Signal()
    appImageChanged = Signal()
    proclogChanged = Signal()
    watchedChanged = Signal()
    itemUpdated = Signal(str)

    def __init__(self, parent=None):
        super(AppInterface, self).__init__(parent)

        self._gui_node = None
        self._app_image = AppImageData(name='root')
        self._watched = []
        self._proclog = []

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
    def refreshAppImage(self):
        if not self._gui_node:
            logger.warning('Cannot refresh without guiNode')
            return

        logger.debug('starting serial clone of devices and information')
        self._app_image.clear()
        devices = self._gui_node.apparatus.serialClone(address=['devices'])
        device_data = AppImageData.from_dict(devices, 'devices')
        device_data.parent = self._app_image
        self._app_image['devices'] = device_data
        information = self._gui_node.apparatus.serialClone(address=['information'])
        information_data = AppImageData.from_dict(information, 'information')
        information_data.parent = self._app_image
        self._app_image['information'] = information_data
        logger.debug(f'serial clone completed {self._app_image}')

        self.appImageChanged.emit()

    @property
    def app_image(self):
        return self._app_image

    @Slot()
    def refreshProclog(self):
        if not self._gui_node:
            logger.warning('Cannot refresh without guiNode')
            return

        logger.debug('starting serial clone of proclog')
        self._proclog = self._gui_node.apparatus.serialClone(address=['proclog'])
        logger.debug(f'serial clone of proclog completed {self._proclog}')

        self.proclogChanged.emit()

    @property
    def proclog(self):
        return self._proclog

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

    @Slot()
    def disconnectAll(self):
        if not self._gui_node:
            logger.warning('Cannot disconnectAll without guiNode')
            return

        self._gui_node.apparatus.Disconnect_All()

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

    @Property(list, notify=watchedChanged)
    def watched(self):
        return self._watched

    @watched.setter
    def watched(self, value):
        if value == self._watched:
            return
        self._watched = value
        self.watchedChanged.emit()

    def append_watched(self, item):
        item.watch = True
        self._watched.append(item)
        self.watchedChanged.emit()

    def remove_watched(self, item):
        item.watch = False
        popped = False
        for i, entry in enumerate(self._watched):
            if entry is item:
                self._watched.pop(i)
                popped = True
                break
        if popped:
            self.watchedChanged.emit()

    def clear_watched(self):
        for item in self._watched:
            item.watch = False
        self._watched = []
        self.watchedChanged.emit()

    @Slot(str)
    def fetchValue(self, key):
        if not self._gui_node:
            logger.warning('Cannot fetch value without guiNode')
            return

        item = self._app_image.get_key(key)
        if item is None:
            logger.warning('cannot update key {}: not found'.format(key))
            return

        logger.debug('updating key {}'.format(key))
        value = self._gui_node.apparatus.getValue(key.split('/'))
        item.value = value
        logger.debug('update complete: {}'.format(value))
        self.itemUpdated.emit(item.key)

    @Slot()
    def fetchWatched(self):
        for watched in self._watched:
            self.fetchValue(watched.key)

    @Slot(QUrl)
    def saveAs(self, url):
        if not self._gui_node:
            logger.warning('Cannot save without guiNode')
            return

        filename = url.toLocalFile()
        self._gui_node.apparatus.logApparatus(filename)

    @Slot(QUrl)
    def importFrom(self, url):
        if not self._gui_node:
            logger.warning('Cannot import without guiNode')
            return

        filename = url.toLocalFile()
        self._gui_node.apparatus.importApparatus(filename)

    @Slot(str, 'QVariant')
    def setValue(self, key, value):
        if not self._gui_node:
            logger.warning('Cannot set value without guiNode')
            return

        self._gui_node.apparatus.setValue(key.split('/'), value)
        self.itemUpdated.emit(key)

    @Slot(str)
    def createAppEntry(self, key):
        if not self._gui_node:
            logger.warning('Cannot create app entry without guiNode')
            return

        self._gui_node.apparatus.createAppEntry(key.split('/'))

    @Slot(str)
    def removeAppEntry(self, key):
        if not self._gui_node:
            logger.warning('Cannot remove app entry without guiNode')
            return

        self._gui_node.apparatus.removeAppEntry(key.split('/'))
