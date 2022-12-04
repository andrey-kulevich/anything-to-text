import pathlib
import subprocess
import os
import sys
import platform
import pyperclip
import requests
import json
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
# from win10toast import ToastNotifier


class AnythingToText(QtWidgets.QWidget):
    coordinates_label = None
    start, end = QtCore.QPoint(), QtCore.QPoint()
    active_mouse_events = True
    app_settings = None
    app_path = ''

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

        self.spinnerLabel = QtWidgets.QLabel(self)
        self.spinner = QtGui.QMovie(os.path.join(os.path.dirname(__file__) + "/img/spinner.gif"))
        self.spinner.setScaledSize(QtCore.QSize(70, 70))
        self.spinnerLabel.setMovie(self.spinner)

        # import the settings
        if getattr(sys, 'frozen', False):
            self.app_path = os.path.dirname(sys.executable)
        elif __file__:
            self.app_path = os.path.dirname(__file__)
        settings_path = os.path.join(self.app_path, 'settings.json')
        if os.path.isfile(settings_path) is True:
            with open(settings_path, 'r') as openfile:
                self.app_settings = json.load(openfile)
        else:
            # create settings file if it does not exist
            print('bla')
            self.app_settings = {
                "server": {
                    "base_path": "https://att.proekt-obroten.su/api/",
                    "user": {
                        "email": None,
                        "ga_token": None,
                        "name": None,
                        "photo_url": None,
                        "uid": None
                    }
                },
                "app": {
                    "extract_lang": "eng",
                    "default_extract_lang": True,
                    "translate_to_lang": "rus",
                    "free_extracts_remaining": 10
                }
            }
            with open(settings_path, 'w') as openfile:
                json.dump(self.app_settings, openfile, indent=4)

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
        settings_button.setGeometry(QtCore.QRect(self.end.x() - 350, self.end.y() + 3, 35, 25))

        def open_settings():
            self.parent().open_settings()
            self.destroy()

        settings_button.clicked.connect(open_settings)
        copy_img_button = QtWidgets.QPushButton("Copy image", self)
        copy_img_button.setGeometry(QtCore.QRect(self.end.x() - 320, self.end.y() + 3, 110, 25))
        copy_img_button.clicked.connect(lambda: self.copy_screenshot_to_clipboard(shot))
        translate_button = QtWidgets.QPushButton("Translate text", self)
        translate_button.setGeometry(QtCore.QRect(self.end.x() - 215, self.end.y() + 3, 110, 25))
        translate_button.clicked.connect(lambda: self.copy_screenshot_to_clipboard(shot))
        copy_text_button = QtWidgets.QPushButton("Extract text", self)
        copy_text_button.setGeometry(QtCore.QRect(self.end.x() - 110, self.end.y() + 3, 110, 25))
        copy_text_button.clicked.connect(lambda: self.extract_text(shot))
        settings_button.show()
        copy_img_button.show()
        copy_text_button.show()
        translate_button.show()
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
        if self.app_settings['server']['user']['ga_token'] is not None \
                or self.app_settings['app']['free_extracts_remaining'] > 0:
            buffer = QtCore.QBuffer()
            buffer.open(QtCore.QBuffer.ReadWrite)
            img.save(buffer, "PNG")
            buffer.close()

            self.spinnerLabel.setGeometry(QtCore.QRect(
                ((self.start.x() + self.end.x()) / 2) - 35, ((self.start.y() + self.end.y()) / 2) - 35, 70, 70))
            self.spinner.start()

            request = ExtractionRequest(self)
            request.runSignal.connect(self.finish_extraction)
            request.run(self.app_settings, buffer.data())
        else:
            alert_dialog = QtWidgets.QDialog(self, Qt.WindowFlags())
            alert_dialog.setWindowTitle('Login alert')
            layout = QtWidgets.QVBoxLayout()
            message = QtWidgets.QLabel("Your limit of text extractions is over.\nPlease login to get unlimited access")
            layout.addWidget(message)
            message.show()
            alert_dialog.setLayout(layout)
            alert_dialog.show()

    def finish_extraction(self, res):
        self.spinner.stop()
        if res.status_code == 200 and 'extracted_text' in res.json():
            extracted_text = res.json()['extracted_text']
            pyperclip.copy(extracted_text)
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
            print('INFO: Copied to the clipboard: ' + extracted_text)

            if self.app_settings['server']['user']['ga_token'] is None:
                with open(os.path.join(self.app_path, 'settings.json'), 'w') as openfile:
                    self.app_settings['app']['free_extracts_remaining'] -= 1
                    json.dump(self.app_settings, openfile, indent=4)
        else:
            print(f"INFO: Unable to read text from image, did not copy")
        self.destroy()


class ExtractionRequest(QtCore.QObject):
    runSignal = QtCore.pyqtSignal(object)

    def run(self, settings, img):
        threading.Thread(target=lambda: self.thread_function(settings, img)).start()

    def thread_function(self, settings, img):
        res = None
        if settings['app']['default_extract_lang'] is False:
            res = requests.post(
                settings['server']['base_path'] + 'anything_to_text',
                files={'image': img},
                params={'lang': settings['app']['extract_lang']},
                headers={'Authorization': settings['server']['user']['ga_token']}
            )
        else:
            res = requests.post(
                settings['server']['base_path'] + 'anything_to_text',
                files={'image': img},
                headers={'Authorization': settings['server']['user']['ga_token']}
            )
        self.runSignal.emit(res)

