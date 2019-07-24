import pytest
from qtpy.QtCore import QModelIndex, Signal, QObject

from GUI.main.ape.apparatus.proclog_model import ProclogModel


def create_interface(proclog):
    class InterfaceMock(QObject):
        proclogChanged = Signal()

        def __init__(self, parent=None):
            super(InterfaceMock, self).__init__(parent)
            self._proclog = proclog

        @property
        def proclog(self):
            return self._proclog

    return InterfaceMock()


@pytest.fixture
def simple_data():
    return [
        ['->', {'name': 'forest', 'information': {}}],
        [
            '->',
            '->',
            {
                'name': 'escape',
                'information': {'spot': '', "care": ['detail', 'bargain']},
            },
        ],
        ['->', {'name': 'curve', 'information': {}}],
    ]


def test_creting_proclog_model_from_simple_data_works(simple_data):
    model = ProclogModel()

    model.appInterface = create_interface(simple_data)

    assert model.rowCount(QModelIndex()) == 2
    assert model.columnCount(QModelIndex()) == 1
    index = model.index(0, 0, QModelIndex())
    assert model.rowCount(index) == 1
    assert model.data(index, ProclogModel.NameRole) == 'forest'
    item_index = model.index(0, 0, index)
    assert model.rowCount(item_index) == 1
    assert model.data(item_index, ProclogModel.NameRole) == 'escape'
    data_index = model.index(0, 0, item_index)
    assert model.rowCount(data_index) == 2
    assert model.data(model.index(0, 0, data_index), ProclogModel.NameRole) == 'spot'
    assert (
        model.data(model.index(1, 0, data_index), ProclogModel.ValueRole)
        == "['detail', 'bargain']"
    )


def test_proclog_model_implementation(simple_data, qtmodeltester):
    model = ProclogModel()
    qtmodeltester.data_display_may_return_none = 0

    model.appInterface = create_interface(simple_data)

    qtmodeltester.check(model)
