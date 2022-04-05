from IPython.core.display import HTML
from IPython.display import display
import numpy as np
from collections import OrderedDict

import pyqtgraph as pg

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from __code.ui_file_metadata_display  import Ui_MainWindow as UiMainWindow


class Interface(QMainWindow):

    exp_dict = None
    roi_column_width = [50, 120, 120]
    working_range_of_images = []
    working_range = [0,0]

    def __init__(self, parent=None, exp_dict=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that popped up \
            (maybe hidden behind this browser!)</span>'))

        self.exp_dict = exp_dict

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.init_statusbar()
        self.setWindowTitle("Display Images for Selected Metadata Range")

        self.ui.image_view = pg.ImageView()
        self.ui.image_view.ui.roiBtn.hide()
        self.ui.image_view.ui.menuBtn.hide()

        top_layout = QtGui.QVBoxLayout()
        top_layout.addWidget(self.ui.image_view)
        self.ui.widget.setLayout(top_layout)
        self.init_widgets()

        # self.integrate_images()
        # self.display_image()
        self.init_table()
        self.init_display()

    def init_display(self):
        row_counts = self.ui.tableWidget.rowCount()
        if row_counts > 0:
            nbr_column = self.ui.tableWidget.columnCount()
            _selection_range = QtGui.QTableWidgetSelectionRange(0, 0, 0, nbr_column-1)
            self.ui.tableWidget.setRangeSelected(_selection_range, True)
            self.refresh_pyqtgraph()

    def init_table(self):
        """fill the table using information from experiment dictionary"""
        exp_dict = self.exp_dict

        for _group_index in exp_dict.keys():
            _item = exp_dict[_group_index]

            _T = _item['T']
            _P = _item['P']

            self.__insert_row(row=int(_group_index), T=_T, P=_P)

    def _set_item_value(self, row=0, column=0, value=-1):
        _item = QtGui.QTableWidgetItem(str(value))
        self.ui.tableWidget.setItem(row, column, _item)

    def __insert_row(self, row=0, T='N/A', P='N/A'):
        self.ui.tableWidget.insertRow(row)
        self._set_item_value(row, 0, str(row))
        self._set_item_value(row, 1, T)
        self._set_item_value(row, 2, P)

    def init_widgets(self):
        # set up width of columns in main table
        nbr_columns = self.ui.tableWidget.columnCount()
        for _col in range(nbr_columns):
            self.ui.tableWidget.setColumnWidth(_col, self.roi_column_width[_col])

    def table_widget_selection_changed(self):
        selection = self.ui.tableWidget.selectedRanges()[0]
        from_group = selection.topRow()
        to_group = selection.bottomRow()

        exp_dict = self.exp_dict

        working_range_of_images = []
        for row in np.arange(from_group, to_group+1):
            group = str(row)
            _data = exp_dict[group]['working_image']['image']
            working_range_of_images.append(_data)

        self.working_range = [from_group, to_group]
        self.working_range_of_images = working_range_of_images
        self.reset_slider()

    def reset_slider(self):
        _working_range = self.working_range
        self.ui.group_slider.setValue(0)
        self.ui.group_slider.setRange(_working_range[0], _working_range[1])
        self.refresh_pyqtgraph()

    def init_statusbar(self):
        self.eventProgress = QtGui.QProgressBar(self.ui.statusbar)
        self.eventProgress.setMinimumSize(20, 14)
        self.eventProgress.setMaximumSize(540, 100)
        self.eventProgress.setVisible(False)
        self.ui.statusbar.addPermanentWidget(self.eventProgress)

    def slider_moved(self, value):
        self.refresh_pyqtgraph(slider_value=value)

    def refresh_pyqtgraph(self, slider_value=-1):
        if slider_value == -1:
            slider_value = self.ui.group_slider.value()
        slider_min = self.ui.group_slider.minimum()
        index = slider_value - slider_min
        self.ui.image_view.setImage(np.transpose(self.working_range_of_images[index]))

        # update labels on top of image display
        _current_dict = self.exp_dict[str(slider_value)]
        _T = _current_dict['T']
        _P = _current_dict['P']

        self.ui.para_1_value.setText(_T)
        self.ui.para_2_value.setText(_P)

    def clear_table(self):
        nbr_row = self.ui.table_roi.rowCount()
        for _row in np.arange(nbr_row):
            self.ui.table_roi.removeRow(0)

    def _get_item_value(self, row, column):
        _item = self.ui.table_roi.item(row, column)
        if _item:
            return str(_item.text())
        else:
            return ''

    def export_button_clicked(self):
        # pop up select folder dialog box

        # retrieve selection infos

        pass

    def close_clicked(self):
        self.close()

    def closeEvent(self, eventhere=None):
        pass

