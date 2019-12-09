import logging

from qtpy.QtCore import QObject, QTimer, Qt, QCoreApplication, QEventLoop
from MultiProcess.zmqNode import zmqNode

logger = logging.getLogger('QZmqNode')


class QZmqNode(QObject, zmqNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def listen_all(self):
        for connection in list(self.connections.keys()):
            self.listen(name=connection)
        if self.listening:
            self.timer_listen = QTimer()
            self.timer_listen.setInterval(int(self.heart_beat * 1000))
            self.timer_listen.setSingleShot(True)
            self.timer_listen.timeout.connect(self.listen_all, Qt.QueuedConnection)
            self.timer_listen.start()
        elif self.timer_listen:
            self.timer_listen.stop()
            self.timer_listen = None

    def listen(self, name=''):
        super(QZmqNode, self).listen(name)
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    def disconnect(self, name=''):
        zmqNode.disconnect(self, name)
