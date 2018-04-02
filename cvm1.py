#!/usr/bin/env python

from PySide.QtCore import *
from PySide.QtGui import *
import cv2
import sys

CASCADE_FILE = 'haarcascade_frontalface_default.xml'

class MainWindow(QWidget):

    frame_changed = Signal(object)

    def __init__(self):
        QWidget.__init__(self)
        self.video_width = 320
        self.video_height = 240
        self.face_rect = None

        self.face_detector = FaceDetector()
        self.frame_changed.connect(self.face_detector.detect)
        self.face_detector.on_detect.connect(self.update_face_rect)

        self.fps_counter = FpsCounter()
        self.fps_counter.on_count.connect(self.update_status)
        self.frame_changed.connect(self.fps_counter.count_frame)

        self.setup_ui()
        self.face_detector.start()
        self.fps_counter.start()

    def closeEvent(self, event):
        self.face_detector.terminate()
        self.fps_counter.terminate()
        event.accept()

    def setup_ui(self):
        self.image_label = QLabel()
        self.setFixedWidth(self.video_width)
        self.setFixedHeight(self.video_height)

        self.blank = QPixmap(self.video_width, self.video_height)
        self.blank.fill(QColor(0,0,0))
        self.image_label.setPixmap(self.blank)

        self.status_label = QLabel("Initializing camera...")

        self.detect_button = QPushButton("Detect Face")
        self.detect_button.setCheckable(True)
        self.detect_button.toggled.connect(self.face_detector.activate)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.status_label)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.detect_button)
        buttons_layout.addWidget(self.quit_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(buttons_layout)

        self.setWindowTitle("Face Detection")
        self.setLayout(main_layout)
        self.show()

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.setup_camera)
        self.timer.start(10)

    def setup_camera(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.video_width)
        self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.video_height)

        self.timer = QTimer()
        self.timer.timeout.connect(self.display_camera_stream)
        self.timer.start(50)

    def display_camera_stream(self):
        val, frame = self.capture.read()

        frame = cv2.flip(frame, 1)
        self.frame_changed.emit(frame)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if self.face_rect is not None:
            x, y, w, h = self.face_rect
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(image))

    @Slot(object)
    def update_face_rect(self, rect):
        self.face_rect = rect

    @Slot(str)
    def update_status(self, msg):
        self.status_label.setText(msg)

class FaceDetector(QThread):

    on_detect = Signal(object)

    def __init__(self):
        QThread.__init__(self)
        self.stopped = True
        self.processing = False
        self.face_cascade = cv2.CascadeClassifier(CASCADE_FILE)

    @Slot()
    def activate(self, val):
        self.stopped = not val
        self.on_detect.emit(None)

    @Slot(object)
    def detect(self, frame):
        if not self.stopped and not self.processing:
            self.processing = True
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 2)
            self.on_detect.emit(faces[0] if len(faces) else None)
            self.processing = False

class FpsCounter(QThread):

    on_count = Signal(str)

    def __init__(self):
        QThread.__init__(self)
        self.num_frames = 0
        self.mutex = QMutex()
        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)
        self.timer.start(1000)

    @Slot()
    def count_frame(self):
        self.mutex.lock()
        self.num_frames += 1
        self.mutex.unlock()

    @Slot()
    def timeout(self):
        self.mutex.lock()
        self.on_count.emit("Camera: %d fps" % self.num_frames)
        self.num_frames = 0
        self.mutex.unlock()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    app.exec_()