from IPython.core.display import HTML
from IPython.core.display import display

import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.dockarea import *

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

    does_top_parent_exist = False

    data_dict = None
    table_column_width = [350, 100, 100, 100, 100]

    # reference file
    reference_image_index = 0
    reference_image = []
    reference_image_short_name = ''
    color_reference_background = QtGui.QColor(50, 250, 50)

    # image display
    histogram_level = []
    live_image = []

    roi = {'vertical': {'x0': 100,
                        'y0': 100,
                        'width': 5,
                        'height': 200,
                        'max_width': 20,
                        'max_height': 500,
                        'color': QtGui.QColor(62, 13, 244),
                        },
           'horizontal': {'x0': 200,
                          'y0': 200,
                        'width': 200,
                        'height': 5,
                        'max_width': 500,
                        'max_height': 20,
                        'color': QtGui.QColor(13, 62, 150),
                          },
           'width': 0.05,
           }

    def __init__(self, parent=None, data_dict=None):

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindowProfile()
        self.ui.setupUi(self)
        self.setWindowTitle("Registration Profile Tool")

        self.init_widgets()
        self.init_pyqtgraph()
        self.init_statusbar()

        self.parent = parent
        if parent:
            self.data_dict = self.parent.data_dict
            self.does_top_parent_exist = True
        elif data_dict:
            display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
                (maybe hidden behind this browser!)</span>'))
            self.data_dict = data_dict
        else:
            raise ValueError("please provide data_dict")

        self.init_reference_image()
        self.init_table()
        self.init_slider()

        self._display_selected_row()
        self._check_widgets()

    ## Initialization

    def init_slider(self):
        self.ui.file_slider.setMaximum(len(self.data_dict['data'])-1)

    def init_statusbar(self):
        self.eventProgress = QtGui.QProgressBar(self.ui.statusbar)
        self.eventProgress.setMinimumSize(300, 20)
        self.eventProgress.setMaximumSize(300, 20)
        self.eventProgress.setVisible(True)
        self.ui.statusbar.addPermanentWidget(self.eventProgress)

    def init_widgets(self):
        # no need to show save and close if not called from parent UI
        if self.parent is None:
            self.ui.save_and_close_button.setVisible(False)

        # table columns
        self.ui.tableWidget.blockSignals(True)
        nbr_columns = self.ui.tableWidget.columnCount()
        for _col in range(nbr_columns):
            self.ui.tableWidget.setColumnWidth(_col, self.table_column_width[_col])
        self.ui.tableWidget.blockSignals(False)

    def init_pyqtgraph(self):
        area = DockArea()
        area.setVisible(True)
        d1 = Dock("Registered Image", size=(600, 600))
        d2 = Dock("Horizontal Profile", size=(300, 200))
        d3 = Dock("Vertical Profile", size=(300, 200))
        d4 = Dock("Peaks Position", size=(600, 600))

        area.addDock(d2, 'top')
        area.addDock(d1, 'left', d2)
        area.addDock(d4, 'above', d1)
        area.addDock(d3, 'bottom', d2)
        area.moveDock(d1, 'above', d4)

        # registered image ara (left dock)
        self.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.image_view.ui.menuBtn.hide()
        self.ui.image_view.ui.roiBtn.hide()
        d1.addWidget(self.ui.image_view)

        # vertical rois
        _color = self.roi['vertical']['color']
        _pen = QtGui.QPen()
        _pen.setColor(_color)
        _pen.setWidthF(self.roi['width'])
        _x0 = self.roi['vertical']['x0']
        _y0 = self.roi['vertical']['y0']
        _width = self.roi['vertical']['width']
        _height = self.roi['vertical']['height']
        _roi_id = pg.ROI([_x0, _y0], [_width, _height], pen=_pen, scaleSnap=True)
        _roi_id.addScaleHandle([1, 1], [0, 0])
        _roi_id.addScaleHandle([0, 0], [1, 1])
        self.ui.image_view.addItem(_roi_id)
        _roi_id.sigRegionChanged.connect(self.vertical_roi_moved)
        self.vertical_profile = _roi_id
        self.ui.image_view.addItem(self.vertical_profile)

        # horizontal rois
        _color = self.roi['horizontal']['color']
        _pen = QtGui.QPen()
        _pen.setColor(_color)
        _pen.setWidthF(self.roi['width'])
        _x0 = self.roi['horizontal']['x0']
        _y0 = self.roi['horizontal']['y0']
        _width = self.roi['horizontal']['width']
        _height = self.roi['horizontal']['height']
        _roi_id = pg.ROI([_x0, _y0], [_width, _height], pen=_pen, scaleSnap=True)
        _roi_id.addScaleHandle([1, 1], [0, 0])
        _roi_id.addScaleHandle([0, 0], [1, 1])
        self.ui.image_view.addItem(_roi_id)
        _roi_id.sigRegionChanged.connect(self.horizontal_roi_moved)
        self.horizontal_profile = _roi_id
        self.ui.image_view.addItem(self.horizontal_profile)

        # horizontal profile area
        self.ui.hori_profile = pg.PlotWidget()
        self.ui.hori_profile.plot()
        d2.addWidget(self.ui.hori_profile)

        # vertical profile area
        self.ui.verti_profile = pg.PlotWidget()
        self.ui.verti_profile.plot()
        d3.addWidget(self.ui.verti_profile)

        # all peaks position
        self.ui.peaks = pg.PlotWidget(title='Vertical and Horizontal Peaks')
        self.ui.peaks.plot()
        d4.addWidget(self.ui.peaks)

        # set up layout
        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(area)

        self.ui.pyqtgraph_widget.setLayout(vertical_layout)

    def init_reference_image(self):
        if self.does_top_parent_exist:
            self.reference_image_index = self.parent.reference_image_index
            self.reference_image = self.parent.reference_image
            self.reference_image_short_name = self.parent.reference_image_short_name
        else:
            self.reference_image = self.data_dict['data'][self.reference_image_index]
            self.reference_image_short_name = os.path.basename(self.data_dict['file_name'][self.reference_image_index])

    def init_table(self):
        data_dict = self.data_dict
        _list_files = data_dict['file_name']
        _short_list_files = [os.path.basename(_file) for _file in _list_files]

        self.ui.tableWidget.blockSignals(True)
        for _row, _file in enumerate(_short_list_files):
            self.ui.tableWidget.insertRow(_row)
            self.__set_item(_row, 0, _file)
            self.__set_item(_row, 1, 'N/A')
            self.__set_item(_row, 2, 'N/A')
            self.__set_item(_row, 3, 'N/A')
            self.__set_item(_row, 4, 'N/A')

        # select first row by default
        self._select_table_row(0)

        self.ui.tableWidget.blockSignals(False)

    def _check_widgets(self):
        """check status of all widgets when new image selected
        Any interaction with the UI (slider, next and prev button) will update the
        table first and then this method will take care of the rest
        """
        selected_row = self._get_selected_row()

        # if reference image selected, no need to show slider on the side
        if selected_row == self.reference_image_index:
            opacity_slider_status = False
        else:
            opacity_slider_status = True
        self.ui.selection_reference_opacity_groupBox.setVisible(opacity_slider_status)

        # if first image selected, prev button should be disabled
        if selected_row == 0:
            prev_button_status = False
        else:
            prev_button_status = True
        self.ui.previous_image_button.setEnabled(prev_button_status)

        # if last image selected, next button should be disabled
        nbr_row = self.ui.tableWidget.rowCount()
        if selected_row == (nbr_row-1):
            next_button_status = False
        else:
            next_button_status = True
        self.ui.next_image_button.setEnabled(next_button_status)

        self.ui.file_slider.setValue(selected_row)

    def _select_table_row(self, row):
        self.ui.tableWidget.blockSignals(True)

        nbr_col = self.ui.tableWidget.columnCount()
        nbr_row = self.ui.tableWidget.rowCount()

        # clear previous selection
        full_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row-1, nbr_col-1)
        self.ui.tableWidget.setRangeSelected(full_range, False)

        # select file of interest
        selection_range = QtGui.QTableWidgetSelectionRange(row, 0, row, nbr_col-1)
        self.ui.tableWidget.setRangeSelected(selection_range, True)

        self.ui.tableWidget.showRow(row)
        self.ui.tableWidget.blockSignals(False)

    def __set_item(self, row=0, col=0, value=''):
        item = QtGui.QTableWidgetItem(str(value))
        self.ui.tableWidget.setItem(row, col, item)
        if row == self.reference_image_index:
            item.setBackground(self.color_reference_background)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def _get_selected_row(self):
        """table only allows selection of one row at a time, so top and bottom row are the same"""
        table_selection = self.ui.tableWidget.selectedRanges()
        table_selection = table_selection[0]
        top_row = table_selection.topRow()
        return top_row

    def _display_selected_row(self):
        selected_row = self._get_selected_row()
        _image = self.data_dict['data'][selected_row]

        # save and load histogram for consistancy between images
        _view = self.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()
        first_update = False
        if self.histogram_level == []:
            first_update = True
        _histo_widget = self.ui.image_view.getHistogramWidget()
        self.histogram_level = _histo_widget

        ## display here according to transparency
        if selected_row != self.reference_image_index:
            _opacity_coefficient = self.ui.opacity_slider.value()  # betwween 0 and 100
            _opacity_image = _opacity_coefficient / 100.
            _image = np.transpose(_image) * _opacity_image

            _opacity_selected = 1 - _opacity_image
            _reference_image = np.transpose(self.reference_image) * _opacity_selected

            _final_image = _reference_image + _image

        else:
            _final_image = self.reference_image
            _final_image = np.transpose(_final_image)

        self.ui.image_view.setImage(_final_image)
        self.live_image = _final_image

        _view_box.setState(_state)
        if not first_update:
            _histo_widget.setLevels(self.histogram_level[0],
                                    self.histogram_level[1])

    ## Event Handler

    def vertical_roi_moved(self):
        """when the vertical roi is moved, we need to make sure the width stays within the max we defined
        and we need refresh the peak calculation"""
        region = self.vertical_profile.getArraySlice(self.live_image, self.ui.image_view.imageItem)

        x0 = region[0][0].start
        x1 = region[0][0].stop
        y0 = region[0][1].start
        y1 = region[0][1].stop

        width = np.abs(x1-x0)
        height = np.abs(y1-y0)

    def horizontal_roi_moved(self):
        """when the horizontal roi is moved, we need to make sure the height stays within the max we defined
        and we need to refresh the peak calculation"""
        region = self.horizontal_profile.getArraySlice(self.live_image, self.ui.image_view.imageItem)

        x0 = region[0][0].start
        x1 = region[0][0].stop
        y0 = region[0][1].start
        y1 = region[0][1].stop

        width = np.abs(x1-x0)
        height = np.abs(y1-y0)

    def calculate_markers_button_clicked(self):
        pass

    def help_button_clicked(self):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/registration/")

    def slider_file_changed(self, value):
        self._select_table_row(value)
        self._check_widgets()
        self._display_selected_row()

    def previous_image_button_clicked(self):
        row_selected = self._get_selected_row()
        self._select_table_row(row_selected-1)
        self._check_widgets()
        self._display_selected_row()

    def next_image_button_clicked(self):
        row_selected = self._get_selected_row()
        self._select_table_row(row_selected+1)
        self._check_widgets()
        self._display_selected_row()

    def registered_all_images_button_clicked(self):
        print("registered all images")

    def cancel_button_clicked(self):
        if self.parent:
            self.parent.registration_profile_ui = None
        self.close()

    def save_and_close_button_clicked(self):
        """save registered images back to the main UI"""
        self.cancel_button_clicked()

    def opacity_slider_moved(self, _):
        self._display_selected_row()

    def table_row_clicked(self):
        self._check_widgets()
        self._display_selected_row()

    def closeEvent(self, c):
        if self.parent:
            self.parent.registration_profile_ui = None
        self.close()