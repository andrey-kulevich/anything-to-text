import requests
import json
import os
import sys
from threading import Timer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import webbrowser


class Repeat(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


language_map = {
    "rus": "Russian",
    "eng": "English",
    "ara": "Arabic"
}


class SettingsWindow(QtWidgets.QDialog):
    app_settings = None
    app_path = ''

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.timer = None
        self.setWindowTitle("Anything To Text: Settings")
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)

        # place the window in center
        qt_rectangle = self.frameGeometry()
        center_point = QtWidgets.QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        if getattr(sys, 'frozen', False):
            self.app_path = os.path.dirname(sys.executable)
        elif __file__:
            self.app_path = os.path.dirname(__file__)
        # import the settings
        with open(os.path.join(self.app_path, 'settings.json'), 'r') as openfile:
            self.app_settings = json.load(openfile)

        user_data_res = requests.get(self.app_settings['server']['base_path'] + 'get_user', 
                                     headers={'auth': self.app_settings['server']['user']['att_token']}).json()
        self.app_settings['server']['user'] = user_data_res['user']

        self.layout = QtWidgets.QVBoxLayout()

        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.save_settings)
        self.buttonBox.rejected.connect(lambda: self.hide())

        extract_lang_combobox_label = QtWidgets.QLabel("Language of extraction")
        self.layout.addWidget(extract_lang_combobox_label)
        self.extract_lang_combobox = QtWidgets.QComboBox()
        self.extract_lang_combobox.addItems(["English", "Russian", "Arabic"])
        self.extract_lang_combobox.currentIndexChanged.connect(self.set_extract_lang)
        self.extract_lang_combobox.setCurrentText(language_map[self.app_settings['app']['extract_lang']])
        self.layout.addWidget(self.extract_lang_combobox)

        self.extract_lang_checkbox = QtWidgets.QCheckBox("Define extraction language automatically")
        self.extract_lang_checkbox.toggled.connect(self.set_default_extract_lang)
        self.extract_lang_checkbox.setChecked(self.app_settings['app']['default_extract_lang'])
        self.layout.addWidget(self.extract_lang_checkbox)

        lang_to_combobox_label = QtWidgets.QLabel("Language to which you want to translate")
        self.layout.addWidget(lang_to_combobox_label)
        self.lang_to_combobox = QtWidgets.QComboBox()
        self.lang_to_combobox.addItems(["Russian", "English", "Arabic"])
        self.lang_to_combobox.currentIndexChanged.connect(self.set_lang_to)
        self.lang_to_combobox.setCurrentText(language_map[self.app_settings['app']['translate_to_lang']])
        self.layout.addWidget(self.lang_to_combobox)

        self.login_button = QtWidgets.QPushButton(
            'Login with Google'
            if self.app_settings['server']['user']['name'] is None
            else 'Logged in as %s' % (self.app_settings['server']['user']['name'])
        )
        self.login_button.clicked.connect(self.start_login_loop)
        self.layout.addWidget(self.login_button)

        statistics_label = QtWidgets.QLabel(
            "<b>Statistics:</b><br>"
            "Free extractions remaining: <b>%s</b><br>"
            "Screenshots made: <b>%d</b><br>"
            "Number of text extractions: <b>%d</b><br>"
            "Number of translates: <b>0</b>" 
            % (self.app_settings['server']['user']['free_use_count'], 
               self.app_settings['server']['user']['screenshots_made'],
               self.app_settings['server']['user']['extraction_count'])
        )
        self.layout.addWidget(statistics_label)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def start_login_loop(self):
        start_auth_res = requests.get(self.app_settings['server']['base_path'] + 'login').json()
        webbrowser.open(start_auth_res['login_url'])
        timeout = 60

        def check_login(timeout):
            if timeout == 0:
                self.timer.cancel()
            timeout = timeout - 1
            check_auth_res = requests.get(
                self.app_settings['server']['base_path'] + 'check_login',
                params={'anon_token': start_auth_res['anon_token']}).json()
            if check_auth_res['authorized'] is True:
                self.app_settings['server']['user'] = check_auth_res['user']
                with open('settings.json', 'w') as openfile:
                    json.dump(self.app_settings, openfile, indent=4)
                self.login_button.setText('Logged in as %s' % (check_auth_res['user']['name']))
                self.timer.cancel()

        self.timer = Repeat(1.0, lambda: check_login(timeout))
        self.timer.start()

    def save_settings(self):
        with open(os.path.join(self.app_path, 'settings.json'), 'w') as openfile:
            json.dump(self.app_settings, openfile, indent=4)
        self.hide()

    def set_lang_to(self):
        self.app_settings['app']['translate_to_lang'] = self.lang_to_combobox.currentText().lower()[0:3]

    def set_extract_lang(self):
        self.app_settings['app']['extract_lang'] = self.extract_lang_combobox.currentText().lower()[0:3]

    def set_default_extract_lang(self):
        self.app_settings['app']['default_extract_lang'] = self.extract_lang_checkbox.isChecked()
