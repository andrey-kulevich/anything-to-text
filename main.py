import io
import pathlib
import sys
import subprocess
import os
import platform
import pyperclip
import pytesseract
from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


class AnythingToText(QtWidgets.QWidget):
    coordinates_label = None
    start, end = QtCore.QPoint(), QtCore.QPoint()
    active_mouse_events = True

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.setWindowTitle("TextShot")
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
            QtWidgets.QApplication.quit()
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
        copy_img_button = QtWidgets.QPushButton("Copy image", self)
        copy_img_button.setGeometry(QtCore.QRect(self.end.x() - 220, self.end.y() + 3, 110, 25))
        copy_img_button.clicked.connect(lambda: copy_screenshot_to_clipboard(shot))
        copy_text_button = QtWidgets.QPushButton("Extract text", self)
        copy_text_button.setGeometry(QtCore.QRect(self.end.x() - 110, self.end.y() + 3, 110, 25))
        copy_text_button.clicked.connect(lambda: extract_text(shot))
        copy_img_button.show()
        copy_text_button.show()
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.active_mouse_events = False


def copy_screenshot_to_clipboard(img):
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
    elif platform_name == "Windows":
        import ctypes
        user32 = ctypes.windll.user32
        user32.OpenClipboard(None)
        user32.EmptyClipboard()
        user32.SetClipboardData(8, img)
        user32.CloseClipboard()
    QtWidgets.QApplication.quit()


def extract_text(img):
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
    except RuntimeError as error:
        print(f"ERROR: An error occurred when trying to process the image: {error}")
        return

    if result:
        pyperclip.copy(result)
        print(f'INFO: Copied "{result}" to the clipboard')
    else:
        print(f"INFO: Unable to read text from image, did not copy")
    QtWidgets.QApplication.quit()


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(Qt.AA_DisableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    try:
        pytesseract.get_tesseract_version()
    except EnvironmentError:
        print("ERROR: Tesseract is either not installed or cannot be reached.\n"
              "Have you installed it and added the install directory to your system path?")
        sys.exit()

    window = QtWidgets.QMainWindow()
    snipper = AnythingToText(window)
    snipper.show()
    sys.exit(app.exec_())
