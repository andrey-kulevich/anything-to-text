import io
import pathlib
import subprocess
import os
import requests
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


class SettingsWindow(QtWidgets.QDialog):
    app_settings = None

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.setWindowTitle("Anything To Text: Settings")

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

        lang_from_checkbox_label = QtWidgets.QLabel("Language from which you want to translate")
        self.layout.addWidget(lang_from_checkbox_label)

        self.lang_from_checkbox = QtWidgets.QComboBox()
        self.lang_from_checkbox.addItems(["English", "Russian", "German"])
        self.lang_from_checkbox.currentIndexChanged.connect(self.set_lang_from)
        self.layout.addWidget(self.lang_from_checkbox)

        lang_to_checkbox_label = QtWidgets.QLabel("Language to which you want to translate")
        self.layout.addWidget(lang_to_checkbox_label)

        self.lang_to_checkbox = QtWidgets.QComboBox()
        self.lang_to_checkbox.addItems(["Russian", "English", "German"])
        self.lang_to_checkbox.currentIndexChanged.connect(self.set_lang_to)
        self.layout.addWidget(self.lang_to_checkbox)

        self.logout_button = QtWidgets.QPushButton('Login with Google')
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

    def set_lang_from(self):
        self.app_settings['app']['translate_from_lang'] = self.lang_from_checkbox.currentText()

    def set_lang_to(self):
        self.app_settings['app']['translate_to_lang'] = self.lang_to_checkbox.currentText()

