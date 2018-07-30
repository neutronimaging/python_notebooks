from IPython.core.display import HTML
from IPython.display import display
import numpy as np

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow, QTableWidgetItem
except ImportError:
    from PyQt5.QtWidgets import QFileDialog, QTreeWidgetItem, QTableWidgetItem
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from __code.ui_addie  import Ui_MainWindow as UiMainWindow



class Interface(QMainWindow):

    item_dict = {'ui': None,
                 'name': '',
                 'state': True,
                 'table_columns': []}

    tree_dict_state = {}
    tree_column = 0

    h1_header_item = ["Title", "Sample", "Vanadium"]
    h2_header_item = ["", "Backgrounda", "Material", "Packing Fraction", "Geometry",
                      "Backgrounda", "Material", "Packing Fraction", "Geometry"]
    h3_header_item = ["", "Runs", "Background Runs", "", "", "Shape", "Radius", "Height",
                      "Runs", "Background Runs", "", "", "Shape", "Radius", "Height"]

    dft_width = 90
    h3_width = np.ones(len(h3_header_item)) * dft_width
        # [dft_width, dft_width, dft_width, dft_width, dft_width, dft_width, dft_width, dft_width,
        #         dft_width, dft_width, dft_width, dft_width, dft_width, dft_width, dft_width]
    h2_width = [h3_width[0], h3_width[1], h3_width[2]+h3_width[3], h3_width[4], h3_width[5]+h3_width[6]+h3_width[7],
                h3_width[1], h3_width[2] + h3_width[3], h3_width[4], h3_width[5] + h3_width[6] + h3_width[7]]
    h1_width = [h2_width[0], h2_width[1]+h2_width[2]+h2_width[3]+h2_width[4], h2_width[1]+h2_width[2]+h2_width[3]+h2_width[4]]



    def __init__(self, parent=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Template Addie")

        self.init_tree()
        self.init_widgets()
        self.init_tables()

    def init_table_col_width(self, table_width=[], table_ui=None):
        for _col in np.arange(table_ui.columnCount()):
            table_ui.setColumnWidth(_col, table_width[_col])

    def init_table_header(self, table_ui=None, list_items=None):
        table_ui.setColumnCount(len(list_items))
        for _index, _text in enumerate(list_items):
            item = QTableWidgetItem(_text)
            table_ui.setHorizontalHeaderItem(_index, item)

    def init_tables(self):

        # h1 header
        self.init_table_header(table_ui=self.ui.h1_table, list_items=self.h1_header_item)

        # h2 header
        self.init_table_header(table_ui=self.ui.h2_table, list_items=self.h2_header_item)

        # h3 header
        self.init_table_header(table_ui=self.ui.h3_table, list_items=self.h3_header_item)

        # h1 table
        self.init_table_col_width(table_width=self.h1_width, table_ui=self.ui.h1_table)

        # h2 table
        self.init_table_col_width(table_width=self.h2_width, table_ui=self.ui.h2_table)

        # h3 table
        self.init_table_col_width(table_width=self.h3_width, table_ui=self.ui.h3_table)


    def init_widgets(self):
        pass

    def init_tree(self):
        # fill the self.ui.treeWidget
        self.addItems(self.ui.treeWidget.invisibleRootItem())
        self.ui.treeWidget.itemChanged.connect(self.tree_item_changed)

    def get_item_name(self, item):

        print("item is : {}".format(item))

        for _key in self.tree_dict_state.keys():
            print("self.tree_dict_state[_key]['ui']: {}".format(self.tree_dict_state[_key]['ui']))
            if item == self.tree_dict_state[_key]['ui']:
                return _key
        return None

    def tree_item_changed(self, item, _):
        print("name of item is: {}".format(self.get_item_name(item)))

    def addItems(self, parent):

        title = self.addChild(parent, "Title", "title", [0])

        sample = self.addParent(parent, "Sample", 'sample', [1,2,3])
        self.addChild(sample, "Runs", "sample_runs", [1])
        sample_background = self.addParent(sample, "Background", "sample_background", [2,3])
        self.addChild(sample_background, "Runs", "sample_background_runs", [2])
        self.addChild(sample_background, "Background Runs", "sample_background_background_runs", [3])

        self.addChild(sample, "Packing Fraction", "sample_packging_fraction", [4])
        sample_geometry = self.addParent(sample, "Geometry", "sample_geometry", [5,6,7])
        self.addChild(sample_geometry, "Shape", "sample_geometry_shape", [5])
        self.addChild(sample_geometry, "Radius", "sample_geometry_radius", [6])
        self.addChild(sample_geometry, "Height", "sample_geometry_height", [7])


        # vanadium = self.addParent(parent, column, "Vanadium", "vanadium", [4,5,6])
        # vanadium_runs = self.addChild(vanadium, column, "Runs", "run")
        # vanadium_background = self.addChild(vanadium, column, "Background", "background")

    def addParent(self, parent, title, name, table_columns=[]):
        item = QTreeWidgetItem(parent, [title])
        item.setData(self.tree_column, QtCore.Qt.UserRole, '')
        item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        item.setCheckState(self.tree_column, QtCore.Qt.Checked)
        item.setExpanded(True)

        self.tree_dict_state[name] = self.item_dict.copy()
        self.tree_dict_state[name]['ui'] = item
        self.tree_dict_state[name]['table_columns'] = table_columns

        return item

    def addChild(self, parent, title, name, table_columns=[]):
        item = QTreeWidgetItem(parent, [title])
        item.setData(self.tree_column, QtCore.Qt.UserRole, '')
        item.setCheckState(self.tree_column, QtCore.Qt.Checked)

        self.tree_dict_state[name] = self.item_dict.copy()
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



