from IPython.core.display import HTML
from IPython.display import display
import pyqtgraph as pg
import numpy as np
import os

try:
    # from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    # from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from NeuNorm.normalization import Normalization

from __code.ui_panoramic_stitching import Ui_MainWindow as UiMainWindow
from __code.file_folder_browser import FileFolderBrowser
from __code._panoramic_stitching.gui_initialization import GuiInitialization
from __code._panoramic_stitching.utilities import Utilities
from __code._panoramic_stitching.stiching import Stitching


class InterfaceHandler(FileFolderBrowser):

    def __init__(self, working_dir=''):
        super(InterfaceHandler, self).__init__(working_dir=working_dir)

    def load(self):
        list_images = self.list_images_ui.selected
        o_norm = Normalization()
        o_norm.load(file=list_images, notebook=True)
        self.o_norm = o_norm


class Interface(QMainWindow):

    # master_dict = OrderedDict(['full_file_name1': {'associated_with_file_index': 0,
    #                                                'reference_roi': {'x0':100, 'y0':100', 'width':300, 'height':300},
    #                                                'target_roi': {'x0':100, 'y0': 100', 'width': 450', 'height':450'},
    #                                                'status': ''},
    #                            'full_file_name2': ... }
    master_dict = {}
    tableWidget_columns_size = [400, 400, 500]
    histogram_level = {'reference': [],
                       'target': []}
    pyqtgraph_image_view = {'reference': None,
                            'data': None}
    live_rois_id = {'reference': None,
                    'target': None}
    list_reference = []
    list_target = []

    # the target box will be x and y times the size of the reference box
    target_box_size_coefficient = {'x': 1.5,
                                   'y': 1.5}

    def __init__(self, parent=None, o_norm=None, configuration=''):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        self.o_norm = o_norm

        self.list_files = self.o_norm.data['sample']['file_name']
        self.basename_list_files = [os.path.basename(_file) for _file in self.list_files]

        self.list_data = self.o_norm.data['sample']['data']

        # have a format {'files': [], 'data': [], 'basename_files': []}
        # self.list_reference = self.get_list_files(start_index=0, end_index=-1)
        # self.list_target = self.get_list_files(start_index=1)
        self.list_reference = self.get_list_files()
        self.list_target = self.get_list_files()
        self.working_dir = os.path.dirname(self.list_files[0])

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Panoramic Stitching")

        o_initialization = GuiInitialization(parent=self,
                                             configuration=configuration)
        o_initialization.all()
        self.check_status_of_stitching_button()

    def get_list_files(self, start_index=0, end_index=None):
        if end_index is None:
            end_index = len(self.list_files)+1

        _list = {'files': self.list_files[start_index: end_index],
                 'data': self.list_data[start_index: end_index],
                 'basename_files': []}
        _list['basename_files'] = [os.path.basename(_file) for _file in _list['files']]
        return _list

    # event handler

    def reference_roi_changed(self):
        self.save_roi_changed(data_type='reference')

    def target_roi_changed(self):
        self.save_roi_changed(data_type='target')

    def save_roi_changed(self, data_type='reference'):
        roi_id = self.live_rois_id[data_type]
        o_utilities = Utilities(parent=self)
        view = o_utilities.get_view(data_type=data_type)
        image = o_utilities.get_image(data_type=data_type)
        row_selected = o_utilities.get_row_selected()

        region = roi_id.getArraySlice(np.transpose(image),
                                      view.imageItem)
        x0 = region[0][0].start
        x1 = region[0][0].stop
        y0 = region[0][1].start
        y1 = region[0][1].stop

        x0 = np.min([x0, x1])
        y0 = np.min([y0, y1])

        width = np.max([x0, x1]) - x0
        height = np.max([y0, y1]) - y0

        o_utilities.set_roi_to_master_dict(row=row_selected,
                                           data_type=data_type,
                                           x0=x0,
                                           y0=y0,
                                           width=width,
                                           height=height)

        # we need to make sure the target roi has the proper size
        if data_type == 'reference':
            o_utilities.set_roi_to_master_dict(row=row_selected,
                                               data_type='target',
                                               width=self.target_box_size_coefficient['x']*width,
                                               height=self.target_box_size_coefficient['y']*height)
            self.display_target_data(data=o_utilities.get_image(data_type='target'))

        self.check_status_of_stitching_button()

    def table_widget_selection_changed(self):
        o_utilities = Utilities(parent=self)
        row_selected = o_utilities.get_reference_selected(key='index')

        # +1 because the target file starts at the second file
        target_file_index_selected = o_utilities.get_target_index_selected_from_row(row=row_selected)
        reference_file_index_selected = o_utilities.get_reference_index_selected_from_row(row=row_selected)

        reference_data = self.list_reference['data'][reference_file_index_selected]
        target_data = self.list_target['data'][target_file_index_selected]

        self.display_reference_data(data=reference_data)
        self.display_target_data(data=target_data)

    def display_reference_data(self, data=[]):
        self.display_data(data_type='reference', data=data)

    def display_target_data(self, data=[]):
        self.display_data(data_type='target', data=data)

    def display_data(self, data_type='reference', data=[]):

        ui = self.pyqtgraph_image_view[data_type]

        roi_id = self.live_rois_id[data_type]
        if roi_id:
            ui.removeItem(roi_id)

        histogram_level = self.histogram_level[data_type]

        _view = ui.getView()
        _view_box = _view.getViewBox()
        # self._view_box = _view_box
        _state = _view_box.getState()

        first_update = False
        if histogram_level == []:
            first_update = True
        _histo_widget = ui.getHistogramWidget()
        self.histogram_level[data_type] = _histo_widget.getLevels()

        data = np.transpose(data)
        ui.setImage(data)
        self.display_roi(data_type=data_type)

        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.histogram_level[data_type][0],
                                    self.histogram_level[data_type][1])

    def display_roi(self, data_type='reference'):
        o_utilities = Utilities(parent=self)
        _row = o_utilities.get_row_selected()
        file_dict = self.master_dict[_row]

        _roi_key = "{}_roi".format(data_type)
        x0 = file_dict[_roi_key]['x0']
        y0 = file_dict[_roi_key]['y0']
        width = file_dict[_roi_key]['width']
        height = file_dict[_roi_key]['height']

        ui = self.pyqtgraph_image_view[data_type]
        color = QtGui.QColor(62, 13, 244)
        _pen = QtGui.QPen()
        _pen.setColor(color)
        _pen.setWidth(0.02)
        _roi_id = pg.ROI([x0, y0], [width, height], pen=_pen, scaleSnap=True)
        if data_type == 'reference':
            _roi_id.addScaleHandle([1, 1], [0, 0])
            _roi_id.addScaleHandle([0, 0], [1, 1])
            method = self.reference_roi_changed
        else:
            method = self.target_roi_changed

        ui.addItem(_roi_id)
        _roi_id.sigRegionChanged.connect(method)
        self.live_rois_id[data_type] = _roi_id

    def check_status_of_stitching_button(self):
        """enable the button if all the target files have been selected at least once"""
        o_utilities = Utilities(parent=self)
        o_utilities.reset_all_status()

        nbr_row = self.ui.tableWidget.rowCount()
        list_target_file = set()
        for _row in np.arange(nbr_row):
            _reference_file = o_utilities.get_reference_file_selected_for_this_row(_row)
            _target_file = o_utilities.get_target_file_selected_for_this_row(_row)

            if _reference_file == _target_file:
                o_utilities.set_status_of_this_row_to_message(row=_row,
                                                              message='Reference and target MUST be different files!')
                continue

            if _target_file in list_target_file:
                o_utilities.set_status_of_this_row_to_message(row=_row,
                                                              message="Already used!")
            list_target_file.add(_target_file)

        if len(list_target_file) == len(self.list_target['files'])-1:
            enabled_button = True
            statusbar_message = ""
        else:
            enabled_button = False
            statusbar_message = "Make sure all files are used as reference"

        self.ui.statusbar.showMessage(statusbar_message)
        self.ui.run_stitching_button.setEnabled(enabled_button)

    def table_widget_reference_image_changed(self, index):
        self.table_widget_selection_changed()
        self.check_status_of_stitching_button()

    def table_widget_target_image_changed(self, index):
        self.table_widget_selection_changed()
        self.check_status_of_stitching_button()

    def run_stitching_button_clicked(self):
        self.eventProgress.setVisible(True)
        o_stitch = Stitching(parent=self)
        o_stitch.run()

    def left_button_pressed(self):
        o_utilities = Utilities(parent=self)
        o_utilities.button_pressed(button_ui=self.ui.left_button)

    def left_button_released(self):
        o_utilities = Utilities(parent=self)
        o_utilities.button_released(button_ui=self.ui.left_button)

    def apply_clicked(self):
        # do stuff
        self.close()

    def cancel_clicked(self):
        self.close()

    def display_image(self, image):
        self.ui.image_view.setImage(image)

    def closeEvent(self, eventhere=None):
        print("Leaving Panoramic Stitching UI")



