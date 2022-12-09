from AnythingToText import *
from SettingsWindow import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from Shortcut import ShortCutListener


class MainWindow(QtWidgets.QWidget):
    screenshot_app = None
    settings_window = None
    keyboard_manager = None

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

        self.keyboard_manager = ShortCutListener(self)
        self.keyboard_manager.runSignal.connect(self.do_screenshot)
        self.keyboard_manager.run()

        if getattr(sys, 'frozen', False):
            self.app_path = os.path.dirname(sys.executable)
        elif __file__:
            self.app_path = os.path.dirname(__file__)
        settings_path = os.path.join(self.app_path, 'settings.json')

        # create settings file if it does not exist
        if os.path.isfile(settings_path) is False:
            app_settings = {
                "server": {
                    "base_path": "https://att.proekt-obroten.su/api/",
                    "user": {
                        "uid": None, 
                        "email": None, 
                        "name": None, 
                        "photo_url": None, 
                        "att_token": None,
                        "free_use_count": "15",
                        "screenshots_made": 0, 
                        "extraction_count": 0
                    }
                },
                "app": {
                    "extract_lang": "eng",
                    "default_extract_lang": False,
                    "translate_to_lang": "ara"
                }
            }
            with open(settings_path, 'w') as openfile:
                json.dump(app_settings, openfile, indent=4)

        # get temp temp token if user is unauthorized and does not have it
        app_settings = None
        with open(os.path.join(self.app_path, 'settings.json'), 'r') as openfile:
            app_settings = json.load(openfile)
        if app_settings['server']['user']['att_token'] is None:
            temp_auth_res = requests.get(app_settings['server']['base_path'] + 'login').json()
            with open(os.path.join(self.app_path, 'settings.json'), 'w') as openfile:
                app_settings['server']['user']['att_token'] = temp_auth_res['anon_token']
                json.dump(app_settings, openfile, indent=4)

    def do_screenshot(self):
        self.screenshot_app = AnythingToText(self)
        self.screenshot_app.show()

    def open_settings(self):
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self)
        self.settings_window.show()

    def quit_app(self):
        self.keyboard_manager.stop()
        QtWidgets.QApplication.quit()
