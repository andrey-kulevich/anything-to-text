import io
import pathlib
import subprocess
import os
import requests
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import webbrowser


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
        self.lang_to_combobox.addItems(["Russian", "English", "German"])
        self.lang_to_combobox.currentIndexChanged.connect(self.set_lang_to)
        self.layout.addWidget(self.lang_to_combobox)

        self.logout_button = QtWidgets.QPushButton('Login with Google')
        self.logout_button.clicked.connect(lambda: webbrowser.open('https://stackoverflow.com'))
        self.layout.addWidget(self.logout_button)

        statistics_label = QtWidgets.QLabel(
            "<b>Statistics:</b><br>"
            "Free extractions remaining: <b>%d</b><br>"
            "Screenshots made: <b>123</b><br>"
            "Number of text extractions: <b>123</b><br>"
            "Number of translates: <b>123</b>" % (self.app_settings['app']['free_extracts_remaining'])
        )
        self.layout.addWidget(statistics_label)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def save_settings(self):
        with open('settings.json', 'w') as openfile:
            json.dump(self.app_settings, openfile, indent=4)
        self.hide()

    def set_lang_to(self):
        self.app_settings['app']['translate_to_lang'] = self.lang_to_combobox.currentText()

