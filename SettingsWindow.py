import io
import pathlib
import subprocess
import os
import requests
import json
from threading import Timer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import webbrowser

class Repeat(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class SettingsWindow(QtWidgets.QDialog):
    app_settings = None

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.setWindowTitle("Anything To Text: Settings")
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)

        # place the window in center
        qt_rectangle = self.frameGeometry()
        center_point = QtWidgets.QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        # import the settings
        with open('settings.json', 'r') as openfile:
            self.app_settings = json.load(openfile)

        self.layout = QtWidgets.QVBoxLayout()

        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.save_settings)
        self.buttonBox.rejected.connect(lambda: self.hide())

        lang_to_combobox_label = QtWidgets.QLabel("Language to which you want to translate")
        self.layout.addWidget(lang_to_combobox_label)

        self.lang_to_combobox = QtWidgets.QComboBox()
        self.lang_to_combobox.addItems(["Russian", "English", "Arabic"])
        self.lang_to_combobox.currentIndexChanged.connect(self.set_lang_to)
        self.layout.addWidget(self.lang_to_combobox)

        self.login_button = QtWidgets.QPushButton(
            'Login with Google' 
            if self.app_settings['server']['user']['ga_token'] is None 
            else 'Logged in as %s' %(self.app_settings['server']['user']['name'])
        )
        self.login_button.clicked.connect(self.start_login_loop)
        self.layout.addWidget(self.login_button)

        statistics_label = QtWidgets.QLabel(
            "<b>Statistics:</b><br>"
            "Free extractions remaining: <b>%d</b><br>"
            "Screenshots made: <b>123</b><br>"
            "Number of text extractions: <b>123</b><br>"
            "Number of translates: <b>123</b>" % (10)
        )
        self.layout.addWidget(statistics_label)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def start_login_loop(self):
        start_auth_res = requests.get(self.app_settings['server']['base_path'] + 'login').json()
        webbrowser.open(start_auth_res['login_url'])
        def check_login():
            check_auth_res = requests.get(
                self.app_settings['server']['base_path'] + 'check_login', 
                params={'anon_token': start_auth_res['anon_token']}).json()
            if check_auth_res['authorized'] is True:
                self.app_settings['server']['user'] = check_auth_res['user']
                with open('settings.json', 'w') as openfile:
                    json.dump(self.app_settings, openfile, indent=4)
                self.login_button.setText('Logged in as %s' %(check_auth_res['user']['name']))
                self.timer.cancel()
        self.timer = Repeat(1.0, check_login)
        self.timer.start()

    def save_settings(self):
        with open('settings.json', 'w') as openfile:
            json.dump(self.app_settings, openfile, indent=4)
        self.hide()

    def set_lang_to(self):
        self.app_settings['app']['translate_to_lang'] = self.lang_to_combobox.currentText()

