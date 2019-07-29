# -*- coding: utf-8 -*-
import logging
import os
import signal
import sys
import traceback

from qtpy.QtWidgets import QApplication
from qtpy.QtCore import QObject, QTimer, Signal
from qtpy.QtQml import QQmlApplicationEngine

PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))


class AppHelper(QObject):
    aboutToQuit = Signal()

    def __init__(self, parent=None):
        super(AppHelper, self).__init__(parent)


class MainGui(QObject):
    def __init__(self, live, parent=None):
        super(MainGui, self).__init__(parent)
        sys.excepthook = self._log_error

        self._engine = QQmlApplicationEngine()
        self._engine.addImportPath(PROJECT_PATH)
        self._app_helper = AppHelper()
        self._engine.rootContext().setContextProperty("appHelper", self._app_helper)

        if live:
            from livecoding import start_livecoding_gui

            qml_main = os.path.join(PROJECT_PATH, "live.qml")
            start_livecoding_gui(
                self._engine, PROJECT_PATH, main_file=sys.argv[0], live_qml=qml_main
            )  # live_qml is optional and can be used to customize the live coding environment
        else:
            from .ape import base
            from .ape import nodes
            from .ape import apparatus
            from .ape import procedure
            from .ape import utilities

            base.register_types()
            nodes.register_types()
            apparatus.register_types()
            procedure.register_types()
            utilities.register_types()
            qml_main = os.path.join(PROJECT_PATH, "main.qml")
            self._engine.load(qml_main)

        self._start_check_timer()

    def _start_check_timer(self):
        self._timer = QTimer()
        self._timer.timeout.connect(lambda: None)
        self._timer.start(100)

    def shutdown(self):
        self._app_helper.aboutToQuit.emit()
        QApplication.quit()

    @staticmethod
    def _log_error(etype, evalue, etraceback):
        tb = ''.join(traceback.format_exception(etype, evalue, etraceback))
        logging.fatal("An unexpected error occurred:\n{}\n\n{}\n".format(evalue, tb))

    @staticmethod
    def start(live=False):
        os.environ['QML_DISABLE_DISTANCEFIELD'] = '1'

        app = QApplication(sys.argv)
        app.setApplicationName("APE Main GUI")

        gui = MainGui(live=live)
        signal.signal(signal.SIGINT, lambda *args: gui.shutdown())

        sys.exit(app.exec_())
