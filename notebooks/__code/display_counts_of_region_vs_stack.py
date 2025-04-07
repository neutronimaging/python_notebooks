import pyqtgraph as pg
from pyqtgraph.dockarea import *
import numpy as np
import os
import numbers

from qtpy.QtWidgets import QFileDialog, QMainWindow, QVBoxLayout
from qtpy import QtGui

#from neutronbraggedge.experiment_handler import *
from NeuNorm.normalization import Normalization
from neutronbraggedge.experiment_handler import *

from __code import load_ui
from __code.ui_display_counts_of_region_vs_stack import Ui_MainWindow as UiMainWindow
from __code import ipywe

class DisplayCountsVsStack(object):

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_input_folder(self):
        self.input_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Input Folder',
                                                               type='directory',
                                                               start_dir=self.working_dir,
                                                               multiple=False)
        self.input_folder_ui.show()


class ImageWindow(QMainWindow):

    stack = []
    integrated_stack = []
    working_folder = ''
    x_axis = {'label': 'File Index', 'type': 'file_index', 'data': []}
    y_axis = {'label': 'Mean Counts', 'data': []}
    spectra_file = ''
    
    def __init__(self, parent=None, display_counts_vs_stack=None):

        self.o_display_counts_vs_stack = display_counts_vs_stack
        self.working_folder = self.o_display_counts_vs_stack.input_folder_ui.selected
        self.load_data()

        QMainWindow.__init__(self, parent=parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    os.path.join('ui',
                                                 'ui_display_counts_of_region_vs_stack.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Select ROI to display profile over all images.")

        #self.stack = np.array(stack)
        [self.nbr_files, height, width] = np.shape(self.stack)
        self.integrated_stack = self.stack.sum(axis=0)

        self.initialize_pyqtgraph()
        self.init_label()

        self.display_image()
        self.update_x_axis()
        self.roi_changed()

    def load_data(self):
        working_folder = self.working_folder
        o_norm = Normalization()
        o_norm.load(folder=working_folder, notebook=True)
        self.stack = np.array(o_norm.data['sample']['data'])

    def update_plot(self):
        self.update_x_axis()
        self.plot()
        
    def init_label(self):
        _tof_label = u"TOF (\u00B5s)"
        self.ui.tof_radio_button.setText(_tof_label)
        _lambda_label = u"lambda (\u212B)"
        self.ui.lambda_radio_button.setText(_lambda_label)
        _offset_label = u"\u00B5s"
        self.ui.detector_offset_units.setText(_offset_label)

    def display_image(self):
        self.ui.image_view.setImage(self.integrated_stack)

    def plot(self):
        x_axis_data = self.x_axis['data']
        x_axis_label = self.x_axis['label']
        
        y_axis_data = self.y_axis['data']
        y_axis_label = self.y_axis['label']
        
        x_axis_data = x_axis_data[0: len(y_axis_data)]
        
        self.counts_vs_index.clear()
        self.counts_vs_index.plot(x_axis_data, y_axis_data)
        
        self.counts_vs_index.setLabel('bottom', x_axis_label)
        self.counts_vs_index.setLabel('left', y_axis_label)
        
    def initialize_pyqtgraph(self):
        area = DockArea()
        area.setVisible(True)
        d1 = Dock("Image Integrated Preview", size=(200, 300))
        d2 = Dock("Counts vs Image Index of Selection", size=(200, 100))

        area.addDock(d1, 'top')
        area.addDock(d2, 'bottom')

        preview_widget = pg.GraphicsLayoutWidget()
        pg.setConfigOptions(antialias=True)

        # image view
        self.ui.image_view = pg.ImageView()
        self.ui.image_view.ui.menuBtn.hide()
        self.ui.image_view.ui.roiBtn.hide()

        # default ROI
        self.ui.roi = pg.ROI(
            [0, 0], [20, 20], pen=(62, 13, 244), scaleSnap=True)  #blue
        self.ui.roi.addScaleHandle([1, 1], [0, 0])
        self.ui.image_view.addItem(self.ui.roi)
        self.ui.roi.sigRegionChanged.connect(self.roi_changed)
        d1.addWidget(self.ui.image_view)

        self.counts_vs_index = pg.PlotWidget(title='')
        self.counts_vs_index.plot()
        d2.addWidget(self.counts_vs_index)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(area)

        self.ui.widget.setLayout(vertical_layout)

    def roi_changed(self):
        region = self.ui.roi.getArraySlice(self.integrated_stack,
                                           self.ui.image_view.imageItem)
        x0 = region[0][0].start
        x1 = region[0][0].stop - 1
        y0 = region[0][1].start
        y1 = region[0][1].stop - 1

        mean_selection = [_data[x0:x1, y0:y1].mean() for _data in self.stack]
        self.y_axis['data'] = mean_selection
        self.plot()

    # x_axis
    def get_x_axis_selected(self):
        if self.ui.file_index_ratio_button.isChecked():
            return 'file_index'
        elif self.ui.tof_radio_button.isChecked():
            return 'tof'
        else:
            return 'lambda'

    def update_x_axis(self):
        x_axis_selected = self.get_x_axis_selected()
        b_enable_only_file_index_button = False
        
        spectra_file = self.spectra_file
        if not os.path.exists(spectra_file):
            x_axis_selected = 'file_index'
            b_enable_only_file_index_button = True

        distance_source_detector = self.ui.distance_source_detector_value.text()
        if not distance_source_detector:
            x_axis_selected = 'file_index'
            b_enable_only_file_index_button = True

        elif not isinstance(float(distance_source_detector), numbers.Number):
            x_axis_selected = 'file_index'
            b_enable_only_file_index_button = True
            
        detector_offset = str(self.ui.detector_offset_value.text())
        if not detector_offset:
            x_axis_selected = 'file_index'
            b_enable_only_file_index_button = True
        elif not isinstance(float(detector_offset), numbers.Number):
            x_axis_selected = 'file_index'
            b_enable_only_file_index_button = True
            
        self.radio_buttons_status(b_enable_only_file_index_button = b_enable_only_file_index_button)
            
        self.x_axis['type'] = x_axis_selected
        if x_axis_selected == 'file_index':
            self.x_axis['data'] = np.arange(self.nbr_files)
            self.x_axis['label'] = 'File Index'
        else:
            _tof_handler = TOF(filename=spectra_file)
            if x_axis_selected == 'tof':
                self.x_axis['data'] = _tof_handler.tof_array
                self.x_axis['label'] = u'TOF (\u00B5s)'
            else:
                _exp = Experiment(tof = _tof_handler.tof_array, 
                                  distance_source_detector_m = float(distance_source_detector),
                                  detector_offset_micros= float(detector_offset))
                self.x_axis['data'] = _exp.lambda_array * 1e10
                self.x_axis['label'] = u'\u03BB (\u212B)'

    def radio_buttons_status(self, b_enable_only_file_index_button=False):
        self.ui.tof_radio_button.setEnabled(not b_enable_only_file_index_button)
        self.ui.lambda_radio_button.setEnabled(not b_enable_only_file_index_button)
        if b_enable_only_file_index_button:
            self.ui.file_index_ratio_button.setChecked(True)
                
    def radio_button_clicked(self):
        self.update_plot()
                
    def distance_source_detector_validated(self):
        self.update_plot()

    def detector_offset_validated(self):
        self.update_plot()

    def time_spectra_file_browse_button_clicked(self):
        spectra_file = QFileDialog.getOpenFileName(
                        caption='Select Time Spectra',
                        directory=self.working_folder,
                        filter='txt (*_Spectra.txt);;All (*.*)')
        spectra_file = spectra_file[0]
        if spectra_file:
            self.ui.time_spectra_file.setText(os.path.basename(spectra_file))
            self.spectra_file = spectra_file
            self.update_x_axis()
            self.plot()

    def done_button_clicked(self):
        self.close()

    def closeEvent(self, event=None):
        pass
