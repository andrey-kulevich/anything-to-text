import sys
from MainWindow import *


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(Qt.AA_DisableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    screenshot_app = MainWindow(window)
    screenshot_app.show()
    sys.exit(app.exec_())
