from collections import OrderedDict

import pytest
from qtpy.QtCore import QModelIndex

from GUI.main.ape.procedure import RequirementsModel


@pytest.fixture
def simple_dict():
    return {"receive": "belt", "opposite": 847.53, "blood": 192}


def test_creating_requirements_model_from_simple_dictionary_works(simple_dict):
    model = RequirementsModel()
    model.requirements = OrderedDict(simple_dict)

    assert model.rowCount(QModelIndex()) == 3
    assert model.columnCount(QModelIndex()) == 2
    index = model.index(0, 0)
    assert index.data(RequirementsModel.KeyRole) == "receive"
    assert index.data(RequirementsModel.ValueRole) == "belt"
    index = model.index(1, 0)
    assert index.data(RequirementsModel.KeyRole) == "opposite"
    assert index.data(RequirementsModel.ValueRole) == pytest.approx(847.53)


def test_requirements_model_implementation(simple_dict, qtmodeltester):
    model = RequirementsModel()
    qtmodeltester.data_display_may_return_none = True

    model.requirements = OrderedDict(simple_dict)
    qtmodeltester.check(model)
