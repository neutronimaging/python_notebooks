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

    item_dict = {'ui': None,
                 'name': '',
                 'state': True,
                 'table_columns': []}

    tree_dict_state = {}

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
        self.ui.treeWidget.itemChanged.connect(self.tree_item_changed)

    def tree_item_changed(self, item, _):
        print(item.checkState(0))

    def addItems(self, parent):
        column = 0
        sample = self.addParent(parent, column, "Sample", 'sample', [1,2,3])
        sample_runs = self.addChild(sample, column, "Runs", "sample_runs", [1])
        sample_background = self.addParent(sample, column, "Background", "sample_background", [2,3])
        sample_background_runs = self.addChild(sample_background, column, "Runs", "sample_background_runs", [2])
        sample_background_background_runs = self.addChild(sample_background, column, "Background Runs", "sample_background_background_runs", [3])

        # vanadium = self.addParent(parent, column, "Vanadium", "vanadium", [4,5,6])
        # vanadium_runs = self.addChild(vanadium, column, "Runs", "run")
        # vanadium_background = self.addChild(vanadium, column, "Background", "background")

    def addParent(self, parent, column, title, name, table_columns=[]):
        item = QTreeWidgetItem(parent, [title])
        item.setData(column, QtCore.Qt.UserRole, '')
        item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        item.setCheckState(column, QtCore.Qt.Checked)
        item.setExpanded(True)

        self.tree_dict_state[name] = self.item_dict
        self.tree_dict_state[name]['ui'] = item
        self.tree_dict_state[name]['table_columns'] = table_columns

        return item

    def addChild(self, parent, column, title, name, table_columns=[]):
        item = QTreeWidgetItem(parent, [title])
        item.setData(column, QtCore.Qt.UserRole, '')
        item.setCheckState(column, QtCore.Qt.Checked)

        self.tree_dict_state[name] = self.item_dict
        self.tree_dict_state[name]['ui'] = item
        self.tree_dict_state[name]['table_columns'] = table_columns

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



