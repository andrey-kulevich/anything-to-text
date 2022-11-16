from AnythingToText import *
from SettingsWindow import *


class MainWindow(QtWidgets.QWidget):
    screenshot_app = None
    settings_window = None

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__) + "/img/icon.png")))
        show_action = QtWidgets.QAction("Make screenshot", self)
        quit_action = QtWidgets.QAction("Quit", self)
        settings_action = QtWidgets.QAction("Settings", self)
        show_action.triggered.connect(self.do_screenshot)
        settings_action.triggered.connect(self.open_settings)
        quit_action.triggered.connect(QtWidgets.QApplication.quit)
        tray_menu = QtWidgets.QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(settings_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def do_screenshot(self):
        self.screenshot_app = AnythingToText(self)
        self.screenshot_app.show()

    def open_settings(self):
        self.settings_window = SettingsWindow(self)
        self.settings_window.show()
