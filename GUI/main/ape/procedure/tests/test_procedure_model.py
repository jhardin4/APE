from collections import OrderedDict

from qtpy.QtCore import QObject, Signal, QModelIndex, Qt

import pytest

from GUI.main.ape.procedure import ProcedureModel


def create_interface(eprocs):
    class InterfaceMock(QObject):
        eprocsChanged = Signal()

        def __init__(self, parent=None):
            super(InterfaceMock, self).__init__(parent)
            self._eprocs = eprocs

        @property
        def eprocs(self):
            return self._eprocs

    return InterfaceMock()


@pytest.fixture
def basic_eprocs():
    eprocs = OrderedDict()
    eprocs["shoot"] = ["robbery", "real", "balance"]
    eprocs["picture"] = ["anywhere", "letter"]
    return eprocs


def test_creating_procedure_model_from_interface_works(basic_eprocs):
    model = ProcedureModel()

    model.appInterface = create_interface(basic_eprocs)

    assert model.rowCount(QModelIndex()) == 2
    assert model.columnCount() == 1
    index = model.index(0, 0)
    assert index.data(Qt.DisplayRole) == 'shoot'
    index = model.index(1, 0)
    assert index.data(Qt.DisplayRole) == 'picture'
    child_index = model.index(0, 0, index)
    assert child_index.data(Qt.DisplayRole) == 'anywhere'
    child_index = model.index(1, 0, index)
    assert child_index.data(Qt.DisplayRole) == 'letter'


def test_getting_procedure_name_from_valid_index_returns_name(basic_eprocs):
    model = ProcedureModel()
    model.appInterface = create_interface(basic_eprocs)

    index = model.index(0, 0, model.index(0, 0))
    name = model.getProcedureName(index)

    assert name == ['shoot', 'robbery']


def test_getting_procedure_name_from_top_level_index_returns_empty_string(basic_eprocs):
    model = ProcedureModel()
    model.appInterface = create_interface(basic_eprocs)

    index = model.index(0, 0)
    name = model.getProcedureName(index)

    assert name == []


def test_getting_procedure_name_from_invalid_index_returns_empty_string():
    model = ProcedureModel()

    assert model.getProcedureName(QModelIndex()) == []
