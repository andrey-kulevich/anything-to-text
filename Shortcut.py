from pynput import keyboard
from PyQt5 import QtCore


class ShortCutListener(QtCore.QObject):
    COMBINATIONS = [
        {keyboard.Key.ctrl, keyboard.Key.f1}
    ]
    runSignal = QtCore.pyqtSignal()
    current = set()
    listener = None

    def run(self):
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def stop(self):
        keyboard.Listener.stop()

    def execute(self):
        self.runSignal.emit()

    def on_press(self, key):
        if any([key in COMBO for COMBO in self.COMBINATIONS]):
            self.current.add(key)
            if any(all(k in self.current for k in COMBO) for COMBO in self.COMBINATIONS):
                self.execute()

    def on_release(self, key):
        if any([key in COMBO for COMBO in self.COMBINATIONS]):
            self.current.remove(key)

