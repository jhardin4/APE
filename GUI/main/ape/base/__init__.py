from qtpy.QtQml import qmlRegisterSingletonType

from .resource_paths import ResourcePaths

MODULE_NAME = 'ape.base'


def register_types():
    qmlRegisterSingletonType(
        ResourcePaths,
        MODULE_NAME,
        1,
        0,
        ResourcePaths.__name__,
        ResourcePaths.qml_singleton_provider,
    )
