import pytest
from qtpy.QtCore import QModelIndex, Signal, QObject

from GUI.main.ape.apparatus import AppImageTreeModel
from GUI.main.ape.apparatus.app_image_data import AppImageData, AppImageDataWalker


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

    model.refresh()

    assert model.rowCount(QModelIndex()) == 4
    assert model.columnCount(QModelIndex()) == 2
    index = model.index(0, 0, QModelIndex())
    assert model.rowCount(index) == 0
    assert index.data(model.NameRole) == 'devices'
    assert index.data(model.ValueRole == '')


def test_creating_model_from_simple_app_image_works(simple_app_image):
    model = AppImageTreeModel()
    model.appInterface = create_interface(simple_app_image)

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
    assert index.data(model.ValueRole) == '[]'


def test_app_image_tree_model_implementation(simple_app_image, qtmodeltester):
    model = AppImageTreeModel()
    qtmodeltester.data_display_may_return_none = True

    model.appInterface = create_interface(simple_app_image)
    model.refresh()
    qtmodeltester.check(model)


def test_app_image_data_walker_walks_over_item_tree_bfs(simple_app_image):
    data = AppImageData.from_dict(simple_app_image, 'root')

    unfolded = [image.name for image in AppImageDataWalker(data)]

    assert unfolded == [
        'root',
        'devices',
        'jealous',
        'director',
        'information',
        'chest',
        'polish',
        'eproclist',
        'proclog',
    ]


def test_app_image_data_walker_walks_over_item_tree_dfs(simple_app_image):
    data = AppImageData.from_dict(simple_app_image, 'root')

    unfolded = [image.name for image in AppImageDataWalker(data, dfs=True)]

    assert unfolded == [
        'jealous',
        'director',
        'devices',
        'polish',
        'chest',
        'information',
        'eproclist',
        'proclog',
        'root',
    ]
