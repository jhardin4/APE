import pytest
from PyQt5.QtTest import QSignalSpy  # TODO: missing in qtpy
from qtpy.QtCore import QModelIndex, Signal, QObject

from GUI.main.ape.apparatus import AppImageTreeModel
from GUI.main.ape.apparatus.app_image_data import AppImageData


@pytest.fixture
def empty_app_image():
    return {'devices': {}, 'information': {}, 'eproclist': [], 'proclog': []}


@pytest.fixture
def simple_app_image():
    return {
        'devices': {'jealous': 23, 'director': "foo"},
        'information': {'chest': {'polish': 331.11}},
        'eproclist': [],
        'proclog': [],
    }


def create_interface(app_image):
    class InterfaceMock(QObject):
        appImageChanged = Signal()
        itemUpdated = Signal(str)

        def __init__(self, parent=None):
            super(InterfaceMock, self).__init__(parent)
            self._app_image = AppImageData.from_dict(app_image, 'root')

        @property
        def app_image(self):
            return self._app_image

    return InterfaceMock()


def test_creating_model_from_empty_app_image_works(empty_app_image):
    model = AppImageTreeModel()
    model.appInterface = create_interface(empty_app_image)

    assert model.rowCount(QModelIndex()) == 4
    assert model.columnCount(QModelIndex()) == 3
    index = model.index(0, 0, QModelIndex())
    assert model.rowCount(index) == 0
    assert index.data(model.NameRole) == 'devices'
    assert index.data(model.ValueRole == '')


def test_creating_model_from_simple_app_image_works(simple_app_image):
    model = AppImageTreeModel()
    model.appInterface = create_interface(simple_app_image)

    assert model.rowCount(QModelIndex()) == 4
    assert model.columnCount(QModelIndex()) == 3
    index = model.index(0, 0, QModelIndex())
    assert model.rowCount(index) == 2
    assert index.data(model.NameRole) == 'devices'
    assert index.data(model.ValueRole == '')
    index = model.index(0, 0, index)
    assert model.rowCount(index) == 0
    assert index.data(model.NameRole) == 'jealous'
    assert index.data(model.ValueRole) == '23'
    index = model.index(2, 0, QModelIndex())
    assert model.rowCount(index) == 0
    assert index.data(model.NameRole) == 'eproclist'
    assert index.data(model.ValueRole) == '[]'


def test_item_updated_triggers_data_changed(simple_app_image):
    model = AppImageTreeModel()
    interface = create_interface(simple_app_image)
    model.appInterface = interface
    spy = QSignalSpy(model.dataChanged)

    index = model.index(0, 0, model.index(0, 0))
    interface.itemUpdated.emit('devices/jealous')

    assert len(spy) == 1
    assert spy[0] == [index, index, []]


def test_app_image_tree_model_implementation(simple_app_image, qtmodeltester):
    model = AppImageTreeModel()
    qtmodeltester.data_display_may_return_none = True

    model.appInterface = create_interface(simple_app_image)

    qtmodeltester.check(model)
