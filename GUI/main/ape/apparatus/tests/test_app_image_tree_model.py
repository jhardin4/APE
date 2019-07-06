import pytest
from PyQt5.QtCore import QModelIndex

from GUI.main.ape.apparatus import AppImageTreeModel


@pytest.fixture
def simple_app_image():
    return {
        'devices': {'jealous': 23, 'director': "foo"},
        'information': {'chest': {'polish': 331.11}},
        'eproclist': {'spin': "QT7C"},
        'proclog': {},
    }


@pytest.fixture
def gui_node(simple_app_image):
    class Apparatus:
        def serialClone(self):
            return simple_app_image

    class GuiNode:
        def __init__(self):
            self.apparatus = Apparatus()

    return GuiNode()


def test_creating_model_from_simple_app_image_works(gui_node):
    model = AppImageTreeModel()
    model.guiNode = gui_node

    model.refresh()

    assert model.rowCount(QModelIndex()) == 4
    assert model.columnCount(QModelIndex()) == 2
    index = model.index(0, 0, QModelIndex())
    assert model.rowCount(index) == 2
    assert model.data(index, model.NameRole) == 'devices'
    assert model.data(index, model.ValueRole == '')
    index = model.index(0, 0, index)
    assert model.rowCount(index) == 0
    assert model.data(index, model.NameRole) == 'jealous'
    assert model.data(index, model.ValueRole) == '23'


def test_app_image_tree_model_implementation(gui_node, qtmodeltester):
    model = AppImageTreeModel()
    qtmodeltester.data_display_may_return_none = True

    model.guiNode = gui_node
    qtmodeltester.check(model)
