from qtpy.QtQml import qmlRegisterType

from .procedure_model import ProcedureModel

MODULE_NAME = "ape.procedure"


def register_types():
    qmlRegisterType(ProcedureModel, MODULE_NAME, 1, 0, ProcedureModel.__name__)
