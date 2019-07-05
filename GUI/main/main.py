# -*- coding: utf-8 -*-
import logging
import os
import sys
import signal
import argparse

from qtpy.QtGui import QGuiApplication
from qtpy.QtCore import QObject, QTimer
from qtpy.QtQml import QQmlApplicationEngine

PROJECT_PATH = os.path.dirname(os.path.realpath(__name__))


class APE(QObject):
    def __init__(self, live, parent=None):
        super(APE, self).__init__(parent)

        self._engine = QQmlApplicationEngine()
        self._engine.addImportPath(PROJECT_PATH)
        if live:
            from livecoding import start_livecoding_gui

            qml_main = os.path.join(PROJECT_PATH, "live.qml")
            start_livecoding_gui(
                self._engine, PROJECT_PATH, __file__, live_qml=qml_main
            )  # live_qml is optional and can be used to customize the live coding environment
        else:
            import ape
            import ape.nodes

            ape.register_types()
            ape.nodes.register_types()
            qml_main = os.path.join(PROJECT_PATH, "main.qml")
            self._engine.load(qml_main)

        self._start_check_timer()

    def _start_check_timer(self):
        self._timer = QTimer()
        self._timer.timeout.connect(lambda: None)
        self._timer.start(100)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda *args: QGuiApplication.quit())

    parser = argparse.ArgumentParser(
        description="""
            Example App
            """
    )
    parser.add_argument(
        "-l",
        "--live",
        help="The live coding version of this application",
        action="store_true",
    )
    parser.add_argument(
        "-d", "--debug", help="Enable debug messages", action="store_true"
    )
    args = parser.parse_args()

    # enable application debug logging
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    app = QGuiApplication(sys.argv)

    gui = APE(live=args.live)

    sys.exit(app.exec_())
