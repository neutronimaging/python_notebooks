import pyqtgraph as pg
from pyqtgraph.dockarea import *
import numpy as np
import os
import numbers

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from neutronbraggedge.experiment_handler import *

from __code.ui_resonance_imaging_experiment_vs_theory import Ui_MainWindow as UiMainWindow


class ImageWindow(QMainWindow):

    pen_color = ['b','g','r','c','m','y','k','w']
    pen_symbol = ['o','s','t','d','+'] 
    
    stack = []
    integrated_stack = []
    working_folder = ''
    x_axis = {'label': 'File Index', 'type': 'file_index', 'data': []}
    y_axis = {'label': 'Mean Counts', 'data': []}
    elements_to_plot = {} # ex U, U235...etc to plot
    spectra_file = ''
    
    def __init__(self, parent=None, stack=[], working_folder='', o_reso=None):
        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Select Rotation Angle for All Images")

        self.stack = np.array(stack)
        self.integrated_stack = self.stack.sum(axis=0)
        self.working_folder = working_folder
        self.o_reso = o_reso
        
        self.initialize_pyqtgraph()
        self.init_label()
        self.init_list_of_things_to_plot()

        self.display_image()
        self.update_x_axis()
        self.roi_changed()
        
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
        try:
            self.legend.scene().removeItem(self.legend)
        except:
            pass
        self.legend = self.counts_vs_index.addLegend()        
        self.counts_vs_index.plot(x_axis_data, y_axis_data, name='Experimental')
        
        self.counts_vs_index.setLabel('bottom', x_axis_label)
        self.counts_vs_index.setLabel('left', y_axis_label)
        
        # plot all elements
        elements_to_plot = self.elements_to_plot
        _index_pen_color = 0
        _index_pen_symbol = 0
        for _label in elements_to_plot.keys():
            _x_axis_data = elements_to_plot[_label]['x_axis']
            _y_axis_data = elements_to_plot[_label]['y_axis']
            self.counts_vs_index.plot(_x_axis_data, _y_axis_data, name=_label, 
                                      pen=self.pen_color[_index_pen_color],
                                     penSymbol = self.pen_symbol[_index_pen_symbol])
            _index_pen_color += 1
            if _index_pen_color >= len(self.pen_color):
                _index_pen_color = 0
                _index_pen_symbol += 1
                
            if _index_pen_symbol == len(self.pen_symbol):
                _index_pen_color = 0
                _index_pen_symbol = 0
                
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

        vertical_layout = QtGui.QVBoxLayout()
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
        
        # enable or not list of element to display
        if x_axis_selected == 'file_index':
            list_status = False
        else:
            list_status = True
        self.ui.list_to_plot_widget.setEnabled(list_status)

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
            self.x_axis['data'] = np.arange(len(self.stack))
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
        if spectra_file:
            self.ui.time_spectra_file.setText(os.path.basename(spectra_file))
            self.spectra_file = spectra_file
            self.update_x_axis()
            self.plot()

    def init_list_of_things_to_plot(self):
        list_things_to_plot = []
        stack = self.o_reso.stack
        list_layers = stack.keys()
        for _layer in list_layers:
            list_things_to_plot.append(_layer)
            list_elements = stack[_layer]['elements']
            for _element in list_elements:
                list_things_to_plot.append(_layer + ' -> ' + _element)
                list_isotopes = stack[_layer][_element]['isotopes']['list']
                for _isotope in list_isotopes:
                    list_things_to_plot.append(_layer + ' -> ' + _element + ' -> ' + _isotope)
                    
        self.ui.list_to_plot_widget.addItems(list_things_to_plot)
        
    def done_button_clicked(self):
        self.close()

    def plot_selection_changed(self, item):
        _elements_to_plot = {}
        
        x_axis_selected = self.get_x_axis_selected()
        if x_axis_selected == 'file_index':
            self.elements_to_plot = _elements_to_plot
            return

        # retrieve data to display
        for _item in self.ui.list_to_plot_widget.selectedIndexes():
            _row_selected = _item.row()
            _text = self.ui.list_to_plot_widget.item(_row_selected).text()
            _layer_element_isotope = self.__parse_layer_element_isotope(_text)
            
            _layer = _layer_element_isotope['layer']
            _element = _layer_element_isotope['element']
            _isotope = _layer_element_isotope['isotope']
            
            if _element == '':
                transmission = self.o_reso.stack_signal[_layer]['transmission']
                x_axis_ev = self.o_reso.stack_signal[_layer]['energy_eV']
            elif _isotope == '':
                transmission = self.o_reso.stack_signal[_layer][_element]['transmission']
                x_axis_ev = self.o_reso.stack_signal[_layer][_element]['energy_eV']
            else:
                transmission = self.o_reso.stack_signal[_layer][_element][_isotope]['transmission']
                x_axis_ev = self.o_reso.stack_signal[_layer][_element][_isotope]['energy_eV']
            
            _elements_to_plot[_text] = {}
            _elements_to_plot[_text]['y_axis'] = transmission
            
            x_axis = []
            if x_axis_selected == 'lambda':
                x_axis = self.o_reso.convert_x_axis(array=x_axis_ev, from_units='ev', to_units='angstroms')
            elif x_axis_selected == 'tof':
                detector_offset = float(self.ui.detector_offset_value.text())
                distance_source_detector = float(self.ui.distance_source_detector_value.text())
                x_axis = self.o_reso.convert_x_axis(array=x_axis_ev, from_units='ev', to_units='s',
                                              delay_us = detector_offset,
                                              source_to_detector_m = distance_source_detector)
            _elements_to_plot[_text]['x_axis'] = x_axis
            
        self.elements_to_plot = _elements_to_plot
        self.plot()
        
    def __parse_layer_element_isotope(self, text):
        ''' this will create a dictionary of each data to plot
        '''
        _dict = {'layer': '',
                'element': '',
                'isotope': ''}
        
        parse_text = text.split(' -> ')
        _dict['layer'] = parse_text[0]
        if len(parse_text) >= 2:
            _dict['element'] = parse_text[1]
        if len(parse_text) >= 3:
            _dict['isotope'] = parse_text[2]
        
        return _dict
        
    def closeEvent(self, event=None):
        pass
    
