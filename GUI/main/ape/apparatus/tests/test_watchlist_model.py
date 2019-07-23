import pytest
from PyQt5.QtTest import QSignalSpy  # TODO: missing in qtpy
from qtpy.QtCore import QModelIndex, Signal, QObject

from GUI.main.ape.apparatus.app_image_data import AppImageData
from GUI.main.ape.apparatus import WatchlistModel


@pytest.fixture
def simple_data():
    root = AppImageData(name="root")
    return [
        AppImageData(name="passage", value=433.01, parent=root),
        AppImageData(name="meal", value="I5CYyp", parent=root),
        AppImageData(name="garage", value=161, parent=root),
    ]


def create_interface(watched):
    class InterfaceMock(QObject):
        watchedChanged = Signal()
        itemUpdated = Signal(str)

        def __init__(self, parent=None):
            super(InterfaceMock, self).__init__(parent)
            self._watched = watched

        @property
        def watched(self):
            return self._watched

    return InterfaceMock()


def test_creating_model_from_empty_watchlist_works():
    model = WatchlistModel()
    model.appInterface = create_interface([])

    assert model.rowCount(QModelIndex()) == 0
    assert model.columnCount(QModelIndex()) == 2


def test_creating_model_from_simple_data_works(simple_data):
    model = WatchlistModel()
    model.appInterface = create_interface(simple_data)

    assert model.rowCount(QModelIndex()) == 3
    assert model.columnCount(QModelIndex()) == 2
    index = model.index(0, 0, QModelIndex())
    assert model.rowCount(index) == 0
    assert index.data(model.KeyRole) == 'passage'
    assert float(index.data(model.ValueRole)) == pytest.approx(433.01)
    index = model.index(2, 0, QModelIndex())
    assert index.data(model.KeyRole) == 'garage'
    assert index.data(model.ValueRole) == '161'


def test_item_updated_triggers_data_changed(simple_data):
    model = WatchlistModel()
    interface = create_interface(simple_data)
    model.appInterface = interface
    spy = QSignalSpy(model.dataChanged)

    index = model.index(2, 0, QModelIndex())
    interface.itemUpdated.emit('garage')

    assert len(spy) == 1
    assert spy[0] == [index, index, []]


def test_watchlist_model_implementation(simple_data, qtmodeltester):
    model = WatchlistModel()
    qtmodeltester.data_display_may_return_none = True

    model.appInterface = create_interface(simple_data)

    qtmodeltester.check(model)
