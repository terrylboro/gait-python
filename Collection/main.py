from PyQt5.QtWidgets import *
import sys
from MainWifiWindow import MainWifiWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWifiWindow()
    window.show()
    sys.exit(app.exec_())
