from IPython.core.display import HTML
from IPython.core.display import display

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui, QtWidgets
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtWidgets import QApplication, QMainWindow

from __code.ui_registration_profile import Ui_MainWindow as UiMainWindowProfile



class RegistrationProfileUi(QMainWindow):

    def __init__(self, parent=None, data_dict=None):

        QMainWindow.__init__(self, parent=None)
        self.ui = UiMainWindowProfile()
        self.ui.setupUi(self)
        self.setWindowTitle("Registration Profile Tool")

        if self.parent:
            self.data_dict = self.parent.data_dict
        elif data_dict:
            display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
                (maybe hidden behind this browser!)</span>'))
            self.data_dict = self.data_dict
        else:
            raise ValueError("please provide data_dict")







    def closeEvent(self, c):
        if self.parent:
            self.parent.registration_profile_ui = None