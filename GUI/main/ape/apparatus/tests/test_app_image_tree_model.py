import pytest
from qtpy.QtCore import QModelIndex, Signal, QObject

from GUI.main.ape.apparatus import AppImageTreeModel


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


def create_loader(app_image):
    class Loader(QObject):
        dataChanged = Signal()

        @property
        def data(self):
            return app_image

    return Loader()


def test_creating_model_from_empty_app_image_works(empty_app_image):
    model = AppImageTreeModel()
    model.loader = create_loader(empty_app_image)

    model.refresh()

    assert model.rowCount(QModelIndex()) == 4
    assert model.columnCount(QModelIndex()) == 2
    index = model.index(0, 0, QModelIndex())
    assert model.rowCount(index) == 0
    assert index.data(model.NameRole) == 'devices'
    assert index.data(model.ValueRole == '')


def test_creating_model_from_simple_app_image_works(simple_app_image):
    model = AppImageTreeModel()
    model.loader = create_loader(simple_app_image)

    model.refresh()

    assert model.rowCount(QModelIndex()) == 4
    assert model.columnCount(QModelIndex()) == 2
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
    assert index.data(model.ValueRole) == ''


def test_app_image_tree_model_implementation(simple_app_image, qtmodeltester):
    model = AppImageTreeModel()
    qtmodeltester.data_display_may_return_none = True

    model.loader = create_loader(simple_app_image)
    model.refresh()
    qtmodeltester.check(model)
