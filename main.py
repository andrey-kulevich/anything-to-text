import sys
from MainWindow import *
import pytesseract


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
    screenshot_app = MainWindow(window)
    screenshot_app.show()
    sys.exit(app.exec_())
