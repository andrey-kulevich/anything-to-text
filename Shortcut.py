from pynput import keyboard
import pyautogui
import time
from PyQt5 import QtCore
import threading

from AnythingToText import AnythingToText

class ShortCutListener(QtCore.QObject):
    COMBINATIONS = [
        {keyboard.Key.ctrl, keyboard.Key.f1}
    ]
    runSignal = QtCore.pyqtSignal()
    current = set()


    def run(self):
        threading.Thread(target=self.thread_function).start()


    def codenames_capture():
        pyautogui.hotkey('ctrl', 'c')       # press ctrl + c
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'n')       # press ctrl + n
        time.sleep(0.1)
        pyautogui.press('enter')            # press enter
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')       # press ctrl + v
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'alt', 'i')# press ctrl + alt + i
        time.sleep(0.1)
        pyautogui.write('300')              # type 300 (pixel size)
        time.sleep(0.1)
        pyautogui.press('enter')            # press enter
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'shift', 's') # press ctrl + shift + s
        time.sleep(0.1)
        pyautogui.press('tab')              # press tab (move to next field)
        time.sleep(0.1)
        pyautogui.press('j')                # press j (to select jpg)
        time.sleep(0.1)
        pyautogui.press('enter')            # press enter
        time.sleep(0.1)
        pyautogui.press('enter')            # press enter
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'w')       # press ctrl + w
        time.sleep(0.1)
        pyautogui.press('right')            # press right arrow
        time.sleep(0.1)
        pyautogui.press('enter')            # press enter
        time.sleep(0.1)

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

    def thread_function(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()