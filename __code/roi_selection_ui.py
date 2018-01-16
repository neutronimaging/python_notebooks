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

from __code.ui_roi_selection  import Ui_MainWindow as UiMainWindow


class Interface(QMainWindow):

    live_data = []
    o_norm = None
    roi_column_width = 70
    integrated_image = None

    list_roi = {} #  'row": {'x0':None, 'y0': None, 'x1': None, 'y1': None}
    default_roi = {'x0': 0, 'y0': 0, 'x1': 50, 'y1': 50, 'id': None}

    def __init__(self, parent=None, o_norm=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        if o_norm:
            self.o_norm = o_norm

        #self.list_files = self.o_norm.data['sample']['file_name']
        #self.list_data = self.o_norm.data['sample']['data']

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.init_statusbar()
        self.setWindowTitle("Background ROI Selection Tool")

        self.ui.image_view = pg.ImageView()
        self.ui.image_view.ui.roiBtn.hide()
        self.ui.image_view.ui.menuBtn.hide()

        top_layout = QtGui.QVBoxLayout()
        top_layout.addWidget(self.ui.image_view)
        self.ui.widget.setLayout(top_layout)
        self.init_widgets()
        self.integrate_images()
        self.display_image()

    def init_widgets(self):
        nbr_columns = self.ui.table_roi.columnCount()
        for _col in range(nbr_columns):
            self.ui.table_roi.setColumnWidth(_col, self.roi_column_width)

    def init_statusbar(self):
        self.eventProgress = QtGui.QProgressBar(self.ui.statusbar)
        self.eventProgress.setMinimumSize(20, 14)
        self.eventProgress.setMaximumSize(540, 100)
        self.eventProgress.setVisible(False)
        self.ui.statusbar.addPermanentWidget(self.eventProgress)

    def apply_clicked(self):
        # do stuff
        self.close()

    def cancel_clicked(self):
        self.close()

    def integrate_images(self):
        self.integrated_image = np.mean(self.o_norm.data['sample']['data'], axis=0)

    def display_image(self):
        self.ui.image_view.setImage(self.integrated_image)

    def remove_row_entry(self, row):
        _roi_id = self.list_roi[row]['id']
        self.ui.image_view.removeItem(_roi_id)
        del self.list_roi[row]

        #rename row
        new_list_roi = {}
        new_row_index = 0
        for _previous_row_index in self.list_roi.keys():
            new_list_roi[new_row_index] = self.list_roi[_previous_row_index]
            new_row_index += 1
        self.list_roi = new_list_roi

    def remove_roi_button_clicked(self):

        self.ui.table_roi.blockSignals(True)

        _selection = self.ui.table_roi.selectedRanges()
        row = _selection[0].topRow()
        old_nbr_row = self.ui.table_roi.rowCount()

        # remove entry from list of roi
        self.remove_row_entry(row)

        # update table of rois
        self.update_table_roi_ui()
        self.ui.table_roi.blockSignals(False)
        self.check_add_remove_button_widgets_status()

        # update selection
        new_nbr_row = self.ui.table_roi.rowCount()
        if new_nbr_row == 0:
            return

        if row == (old_nbr_row-1):
            row = new_nbr_row - 1

        _new_selection = QtGui.QTableWidgetSelectionRange(row, 0, row, 3)
        self.ui.table_roi.setRangeSelected(_new_selection, True)


    def clear_table(self):
        nbr_row = self.ui.table_roi.rowCount()
        for _row in np.arange(nbr_row):
            self.ui.table_roi.removeRow(0)

    def update_table_roi_ui(self):
        """Using list_roi as reference, repopulate the table_roi_ui"""
        self.ui.table_roi.blockSignals(True)
        list_roi = self.list_roi

        self.clear_table()

        _index_row = 0
        for _roi_key in list_roi.keys():
            _roi = list_roi[_roi_key]

            self.ui.table_roi.insertRow(_index_row)

            _item = QtGui.QTableWidgetItem(str(_roi['x0']))
            self.ui.table_roi.setItem(_index_row, 0, _item)

            _item = QtGui.QTableWidgetItem(str(_roi['y0']))
            self.ui.table_roi.setItem(_index_row, 1, _item)

            _item = QtGui.QTableWidgetItem(str(_roi['x1']))
            self.ui.table_roi.setItem(_index_row, 2, _item)

            _item = QtGui.QTableWidgetItem(str(_roi['y1']))
            self.ui.table_roi.setItem(_index_row, 3, _item)

            _index_row += 1

        self.ui.table_roi.blockSignals(False)

    def update_table_roi(self, item):
        """Using the table_roi_ui as reference, will update the list_roi dictionary"""
        nbr_row = self.ui.table_roi.rowCount()
        list_roi = {}
        for _row in np.arange(nbr_row):
            _roi = {}

            _roi['x0'] = self._get_item_value(_row, 0)
            _roi['x1'] = self._get_item_value(_row, 1)
            _roi['y0'] = self._get_item_value(_row, 2)
            _roi['y1'] = self._get_item_value(_row, 3)

            list_roi[_row] = _roi

        self.list_roi = list_roi

    def _get_item_value(self, row, column):
        _item = self.ui.table_roi.item(row, column)
        if _item:
            return str(_item.text())
        else:
            return ''

    def roi_manually_moved(self):
        list_roi = self.list_roi

        for _row in list_roi.keys():

            _roi = list_roi[_row]

            roi_id = _roi['id']
            region = roi_id.getArraySlice(self.integrated_image, self.ui.image_view.imageItem)

            x0 = region[0][0].start
            x1 = region[0][0].stop
            y0 = region[0][1].start
            y1 = region[0][1].stop

            _roi['x0'] = x0
            _roi['x1'] = x1
            _roi['y0'] = y0
            _roi['y1'] = y1

            list_roi[_row] = _roi

        self.list_roi = list_roi
        self.update_table_roi_ui()

    def clear_roi_on_image_view(self):
        list_roi = self.list_roi

        for _row in list_roi.keys():

            _roi = list_roi[_row]
            roi_id = _roi['id']
            self.ui.image_view.removeItem(roi_id)

    def add_roi_button_clicked(self):
        self.clear_roi_on_image_view()

        self.ui.table_roi.blockSignals(True)
        _selection = self.ui.table_roi.selectedRanges()
        if _selection:
            row = _selection[0].topRow()
        else:
            row = 0

        # init new row with default value
        self.ui.table_roi.insertRow(row)
        _default_roi = self.default_roi

        _item = QtGui.QTableWidgetItem(str(_default_roi['x0']))
        self.ui.table_roi.setItem(row, 0, _item)

        _item = QtGui.QTableWidgetItem(str(_default_roi['y0']))
        self.ui.table_roi.setItem(row, 1, _item)

        _item = QtGui.QTableWidgetItem(str(_default_roi['x1']))
        self.ui.table_roi.setItem(row, 2, _item)

        _item = QtGui.QTableWidgetItem(str(_default_roi['y1']))
        self.ui.table_roi.setItem(row, 3, _item)

        # save new list_roi dictionary
        nbr_row = self.ui.table_roi.rowCount()
        list_roi = OrderedDict()
        for _row in np.arange(nbr_row):
            _roi = {}

            _x0 = self._get_item_value(_row, 0)
            _roi['x0'] = _x0

            _y0 = self._get_item_value(_row, 1)
            _roi['y0'] = _y0

            _x1 = self._get_item_value(_row, 2)
            _roi['x1'] = _x1

            _y1 = self._get_item_value(_row, 3)
            _roi['y1'] = _y1

            x0_int = int(_x0)
            y0_int = int(_y0)
            width_int = np.abs(x0_int - int(_x1))
            height_int = np.abs(y0_int - int(_y1))

            _color = QtGui.QColor(62, 13, 244)
            _pen = QtGui.QPen()
            _pen.setColor(_color)
            _pen.setWidth(0.6)
            _roi_id = pg.ROI([x0_int, y0_int], [width_int, height_int], pen=_pen, scaleSnap=True)
            _roi_id.addScaleHandle([1,1], [0,0])
            self.ui.image_view.addItem(_roi_id)
            # add connection to roi
            _roi_id.sigRegionChanged.connect(self.roi_manually_moved)

            _roi['id'] = _roi_id

            list_roi[_row] = _roi

        self.list_roi = list_roi

        self.ui.table_roi.blockSignals(False)

        self.check_add_remove_button_widgets_status()

        if not _selection:
            _new_selection = QtGui.QTableWidgetSelectionRange(0, 0, 0, 3)
            self.ui.table_roi.setRangeSelected(_new_selection, True)

    def check_add_remove_button_widgets_status(self):
        nbr_row = self.ui.table_roi.rowCount()
        if nbr_row > 0:
            self.ui.remove_roi_button.setEnabled(True)
        else:
            self.ui.remove_roi_button.setEnabled(False)

    def closeEvent(self, eventhere=None):
        print("Leaving Parameters Selection UI")



