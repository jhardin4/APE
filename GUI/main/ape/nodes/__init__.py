# -*- coding: utf-8 -*-
from qtpy.QtQml import qmlRegisterType

from .appa_node import AppaNode
from .launcher import Launcher

MODULE_NAME = "ape.nodes"


def register_types():
    qmlRegisterType(AppaNode, MODULE_NAME, 1, 0, AppaNode.__name__)
    qmlRegisterType(Launcher, MODULE_NAME, 1, 0, Launcher.__name__)
