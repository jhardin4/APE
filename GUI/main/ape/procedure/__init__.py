from qtpy.QtQml import qmlRegisterType

from .procedure_model import ProcedureModel
from .requirements_model import RequirementsModel
from .procedure_interface import ProcedureInterface

MODULE_NAME = "ape.procedure"


def register_types():
    qmlRegisterType(ProcedureModel, MODULE_NAME, 1, 0, ProcedureModel.__name__)
    qmlRegisterType(RequirementsModel, MODULE_NAME, 1, 0, RequirementsModel.__name__)
    qmlRegisterType(ProcedureInterface, MODULE_NAME, 1, 0, ProcedureInterface.__name__)
