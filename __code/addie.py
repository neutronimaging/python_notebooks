from IPython.core.display import HTML
from IPython.display import display

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog, QTreeWidgetItem
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from __code.ui_addie  import Ui_MainWindow as UiMainWindow



class Interface(QMainWindow):

    def __init__(self, parent=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Template Addie")

        self.init_tree()

    def init_tree(self):
        # fill the self.ui.treeWidget
        self.addItems(self.ui.treeWidget.invisibleRootItem())

    def addItems(self, parent):
        column = 0
        sample = self.addParent(parent, column, "Sample", "Sample text")
        vanadium = self.addParent(parent, column, "Vanadium", "Vanadium text")

        self.addChild(sample, column, "Runs", "run")
        self.addChild(sample, column, "Background", "backgorund")

        self.addChild(vanadium, column, "Runs", "run")
        self.addChild(vanadium, column, "Background", "backgorund")


    def addParent(self, parent, column, title, data):
        item = QTreeWidgetItem(parent, [title])
        item.setData(column, QtCore.Qt.UserRole, data)
        item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        item.setExpanded(True)
        return item

    def addChild(self, parent, column, title, data):
        item = QTreeWidgetItem(parent, [title])
        item.setData(column, QtCore.Qt.UserRole, data)
        item.setCheckState(column, QtCore.Qt.Unchecked)
        return item

    def init_widgets(self):
        pass

    def apply_clicked(self):
        # do stuff
        self.close()

    def cancel_clicked(self):
        self.close()

    def closeEvent(self, eventhere=None):
        print("Leaving Parameters Selection UI")



