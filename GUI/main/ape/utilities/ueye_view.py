import logging

from qtpy.QtCore import QThread, Signal, Property, Qt, QRect, QMutex
from qtpy.QtGui import QImage, QPainter
from qtpy.QtQuick import QQuickPaintedItem

from Devices.Drivers.camera import UEye, pue, CameraException

logger = logging.getLogger("UpdateTread")


class UpdateThread(QThread):
    pixmapReady = Signal(QImage)
    stopped = Signal()
    errored = Signal(str)

    def __init__(self, cam_id, image_width, image_height):
        super(UpdateThread, self).__init__()
        self._width = 640
        self._height = 480
        self._stopped = False
        self._update_mutex = QMutex()

        self._cam_id = cam_id
        self._image_width = image_width
        self._image_height = image_height

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
        try:
            import cv2
        except ImportError as e:
            self.errored.emit(str(e))
            self.stopped.emit()
            return
        try:
            ueye = UEye(self._cam_id, self._image_width, self._image_height)
        except CameraException as e:
            self.errored.emit(str(e))
            self.stopped.emit()
            return
        self._ueye.start_video_capture()

        while True:
            try:
                self._update_mutex.lock()
                if self._stopped:
                    ueye.close()
                    del ueye
                    self.stopped.emit()
                    return
            finally:
                self._update_mutex.unlock()

            frame = ueye.get_video_frame()
            if frame is None:
                ueye.close()
                del ueye
                self.stopped.emit()
                return

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
    camIdChanged = Signal(int)
    imageWidthChanged = Signal(int)
    imageHeightChanged = Signal(int)

    def __init__(self, parent=None):
        super(UEyeView, self).__init__(parent)
        self._frame_image = QImage()
        self._running = False
        self._update_thread = None
        self._cam_id = 0
        self._image_width = 2048
        self._image_height = 1088

        self.destroyed.connect(lambda: self._stop_thread)

    def _on_camera_stopped(self):
        self._stop_thread()

    def _on_camera_errored(self, msg):
        logger.error(f"Error loading camera {msg}")
        self._running = False
        self.runningChanged.emit(self._running)

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

    @Property(int, notify=camIdChanged)
    def camId(self):
        return self._cam_id

    @camId.setter
    def camId(self, value):
        if value == self._cam_id:
            return
        self._cam_id = value
        self.camIdChanged.emit(value)

    @Property(int, notify=imageWidthChanged)
    def imageWidth(self):
        return self._image_width

    @imageWidth.setter
    def imageWidth(self, value):
        if value == self._image_width:
            return
        self._image_width = value
        self.imageWidthChanged.emit(value)

    @Property(int, notify=imageHeightChanged)
    def imageHeight(self):
        return self._image_height

    @imageHeight.setter
    def imageHeight(self, value):
        if value == self._image_height:
            return
        self._image_height = value
        self.imageHeightChanged.emit(value)

    @Property(bool, constant=True)
    def driverLoaded(self):
        return pue is not None

    def _start_thread(self):
        if self._update_thread:
            return
        self._update_thread = UpdateThread(
            self._cam_id, self._image_width, self._image_height
        )
        self._update_thread.pixmapReady.connect(self._update_pixmap)
        self._update_thread.stopped.connect(self._on_camera_stopped)
        self._update_thread.errored.connect(self._on_camera_errored)
        self._update_size()
        self._update_thread.start()

    def _stop_thread(self):
        if not self._update_thread:
            return
        self._update_thread.stop()
        self._update_thread.pixmapReady.disconnect(self._update_pixmap)
        self._update_thread.stopped.disconnect(self._on_camera_stopped)
        self._update_thread.errored.disconnect(self._on_camera_errored)
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
