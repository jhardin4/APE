# -*- coding: utf-8 -*-
from qtpy.QtCore import QObject, Signal, Property


class Calculator(QObject):

    aChanged = Signal(float)
    bChanged = Signal(float)
    sumChanged = Signal(float)

    def __init__(self, parent=None):
        super(Calculator, self).__init__(parent)

        self._a = 0.0
        self._b = 0.0
        self._sum = 0.0

        self.aChanged.connect(lambda _: self._calculate())
        self.bChanged.connect(lambda _: self._calculate())

    @Property(float, notify=aChanged)
    def a(self):
        return self._a

    @a.setter
    def a(self, value):
        if value == self._a:
            return
        self._a = value
        self.aChanged.emit(value)

    @Property(float, notify=bChanged)
    def b(self):
        return self._b

    @b.setter
    def b(self, value):
        if value == self._b:
            return
        self._b = value
        self.bChanged.emit(value)

    @Property(float, notify=sumChanged)
    def sum(self):
        return self._sum

    def _calculate(self):
        self._sum = self._a + self._b
        self.sumChanged.emit(self._sum)
