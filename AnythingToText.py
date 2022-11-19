import io
import pathlib
import subprocess
import os
import platform
import pyperclip
import pytesseract
import requests
from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
# from win10toast import ToastNotifier


class AnythingToText(QtWidgets.QWidget):
    coordinates_label = None
    start, end = QtCore.QPoint(), QtCore.QPoint()
    active_mouse_events = True

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.setWindowTitle("Anything To Text")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Dialog)
        self.setWindowState(self.windowState() | Qt.WindowFullScreen)
        self.screen = QtWidgets.QApplication.screenAt(QtGui.QCursor.pos()).grabWindow(0)
        palette = QtGui.QPalette()
        palette.setBrush(self.backgroundRole(), QtGui.QBrush(self.screen))
        self.setPalette(palette)
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.coordinates_label = QtWidgets.QLabel(self)
        self.coordinates_label.setStyleSheet("color: #fff;")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.destroy()
        return super().keyPressEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QtGui.QColor(0, 0, 0, 100))
        painter.drawRect(0, 0, self.width(), self.height())
        if self.start == self.end:
            return super().paintEvent(event)
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 2))
        painter.setBrush(painter.background())
        painter.drawRect(QtCore.QRect(self.start, self.end))
        self.coordinates_label.setGeometry(QtCore.QRect(self.end.x(), self.end.y(), 70, 20))
        self.coordinates_label.setText(str(abs(self.start.x() - self.end.x())) + ", "
                                       + str(abs(self.start.y() - self.end.y())))
        return super().paintEvent(event)

    def mousePressEvent(self, event):
        if self.active_mouse_events:
            self.start = self.end = event.pos()
            self.update()
            return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.active_mouse_events:
            self.end = event.pos()
            self.update()
            return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.start == self.end:
            return super().mouseReleaseEvent(event)
        QtWidgets.QApplication.processEvents()
        scale = int(self.screen.size().width()) / int(self.size().width())
        shot = self.screen.copy(
            min(self.start.x() * scale, self.end.x() * scale),
            min(self.start.y() * scale, self.end.y() * scale),
            abs(self.start.x() * scale - self.end.x() * scale),
            abs(self.start.y() * scale - self.end.y() * scale),
        )
        settings_button = QtWidgets.QPushButton(self)
        settings_button.setIcon(QtGui.QIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__) + "/img/gear.png"))))
        settings_button.setGeometry(QtCore.QRect(self.end.x() - 245, self.end.y() + 3, 35, 25))

        def open_settings():
            self.parent().open_settings()
            self.destroy()

        settings_button.clicked.connect(open_settings)
        copy_img_button = QtWidgets.QPushButton("Copy image", self)
        copy_img_button.setGeometry(QtCore.QRect(self.end.x() - 215, self.end.y() + 3, 110, 25))
        copy_img_button.clicked.connect(lambda: self.copy_screenshot_to_clipboard(shot))
        copy_text_button = QtWidgets.QPushButton("Extract text", self)
        copy_text_button.setGeometry(QtCore.QRect(self.end.x() - 110, self.end.y() + 3, 110, 25))
        copy_text_button.clicked.connect(lambda: self.extract_text(shot))
        settings_button.show()
        copy_img_button.show()
        copy_text_button.show()
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.active_mouse_events = False

    def copy_screenshot_to_clipboard(self, img):
        """
        copy screenshot to clipboard
        """
        platform_name = platform.uname().system
        if platform_name == "Linux":
            pass
        elif platform_name == "Darwin":
            img.save('temp.png')
            subprocess.run(["osascript", "-e", "set the clipboard to (read (POSIX file \""
                            + str(pathlib.Path().absolute()) + "/temp.png\") as JPEG picture)"])
            os.remove('temp.png')
            subprocess.run(["osascript", "-e", "display notification \"Screenshot is copied to clipboard!\" with "
                                               "title \"Anything To Text\""])
        elif platform_name == "Windows":
            import ctypes
            user32 = ctypes.windll.user32
            user32.OpenClipboard(None)
            user32.EmptyClipboard()
            user32.SetClipboardData(8, img)
            user32.CloseClipboard()
            # toaster = ToastNotifier()
            # toaster.show_toast("Success", "Screenshot is copied to clipboard")
        self.destroy()

    def extract_text(self, img):
        """
        extract text from given image
        """
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        pil_img = Image.open(io.BytesIO(buffer.data()))
        buffer.close()

        try:
            result = pytesseract.image_to_string(pil_img)
            # result = requests.post(url='some url', headers={}, auth={})
        except RuntimeError as error:
            print(f"ERROR: An error occurred when trying to process the image: {error}")
            return

        if result:
            pyperclip.copy(result)
            platform_name = platform.uname().system
            if platform_name == "Linux":
                pass
            elif platform_name == "Darwin":
                subprocess.run(["osascript", "-e", "display notification \"Text is copied to clipboard!\" with "
                                                   "title \"Anything To Text\""])
            elif platform_name == "Windows":
                pass
                # toaster = ToastNotifier()
                # toaster.show_toast("Success", "Text is copied to clipboard")
            print(f'INFO: Copied "{result}" to the clipboard')
        else:
            print(f"INFO: Unable to read text from image, did not copy")
        self.destroy()
