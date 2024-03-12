from PyQt5.QtWidgets import *
import sys

from PaperManagementApp import PaperManagementApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaperManagementApp()
    window.show()
    sys.exit(app.exec_())
