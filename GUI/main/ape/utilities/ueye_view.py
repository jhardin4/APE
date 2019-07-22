from qtpy.QtCore import QThread, Signal, Property, Qt, QRect, QMutex
from qtpy.QtGui import QImage, QPainter
from qtpy.QtQuick import QQuickPaintedItem

import cv2


class UpdateThread(QThread):
    pixmapReady = Signal(QImage)

    def __init__(self):
        super(UpdateThread, self).__init__()
        self._width = 640
        self._height = 480
        self._stopped = False
        self._update_mutex = QMutex()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._update_mutex.lock()
        self._width = value
        self._update_mutex.unlock()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._update_mutex.lock()
        self._height = value
        self._update_mutex.unlock()

    def stop(self):
        self._update_mutex.lock()
        self._stopped = True
        self._update_mutex.unlock()

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            try:
                self._update_mutex.lock()
                if self._stopped:
                    del cap
                    return
            finally:
                self._update_mutex.unlock()
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(
                    rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888
                )
                try:
                    self._update_mutex.lock()
                    p = convert_to_qt_format.scaled(
                        self._width, self._height, Qt.KeepAspectRatio
                    )
                finally:
                    self._update_mutex.unlock()
                self.pixmapReady.emit(p)


class UEyeView(QQuickPaintedItem):
    runningChanged = Signal(bool)

    def __init__(self, parent=None):
        super(UEyeView, self).__init__(parent)
        self._frame_image = QImage()
        self._running = False
        self._update_thread = None

        self.destroyed.connect(lambda: self._stop_thread)

    @Property(bool, notify=runningChanged)
    def running(self):
        return self._running

    @running.setter
    def running(self, value):
        if value == self._running:
            return
        self._running = value

        if self._running:
            self._start_thread()
        else:
            self._stop_thread()

        self.runningChanged.emit(value)

    def _start_thread(self):
        if self._update_thread:
            return
        self._update_thread = UpdateThread()
        self._update_thread.pixmapReady.connect(self._update_pixmap)
        self._update_size()
        self._update_thread.start()

    def _stop_thread(self):
        if not self._update_thread:
            return
        self._update_thread.stop()
        self._update_thread.pixmapReady.disconnect(self._update_pixmap)
        self._update_thread = None

    def geometryChanged(self, new_geometry, old_geometry):
        super(UEyeView, self).geometryChanged(new_geometry, old_geometry)
        if self._update_thread:
            self._update_size()

    def paint(self, painter: QPainter):
        bounding_rect = QRect(0, 0, self.width(), self.height())
        if not self._frame_image.isNull():
            draw_rect = self._frame_image.rect()
            draw_rect.moveCenter(bounding_rect.center())
            painter.drawImage(draw_rect, self._frame_image, self._frame_image.rect())

    def _update_pixmap(self, image):
        self._frame_image = image
        self.update()

    def _update_size(self):
        self._update_thread.width = self.width()
        self._update_thread.height = self.height()
