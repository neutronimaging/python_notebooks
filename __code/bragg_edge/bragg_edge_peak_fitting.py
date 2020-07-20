from IPython.core.display import HTML
import os
import random
import numpy as np
from IPython.display import display
import pyqtgraph as pg
from qtpy.QtWidgets import QMainWindow
from qtpy import QtGui
from collections import OrderedDict

from neutronbraggedge.experiment_handler import *

from __code.bragg_edge.bragg_edge_normalization import BraggEdge as BraggEdgeParent
from __code.bragg_edge.peak_fitting_interface_initialization import Initialization
from __code.bragg_edge.bragg_edge_peak_fitting_gui_utility import GuiUtility
from __code.selection_region_utilities import SelectionRegionUtilities
from __code import load_ui
from __code.utilities import find_nearest_index
from __code.table_handler import TableHandler
from __code.bragg_edge.fitting_job_handler import FittingJobHandler
from __code.bragg_edge.kropff import Kropff
from __code.bragg_edge.export_handler import ExportHandler
from __code.bragg_edge.import_handler import ImportHandler
from __code.bragg_edge.get import Get
from __code.bragg_edge.peak_fitting_initialization import PeakFittingInitialization

DEBUGGING = True


class BraggEdge(BraggEdgeParent):
   pass


class Interface(QMainWindow):

    bragg_edge_range = [5, 20]
    selection_roi_rgb = (62, 13, 244)
    roi_settings = {'color': QtGui.QColor(selection_roi_rgb[0],
                                          selection_roi_rgb[1],
                                          selection_roi_rgb[2]),
                    'width': 0.01,
                    'position': [10, 10]}
    shrinking_roi_rgb = (13, 214, 244)
    shrinking_roi_settings = {'color': QtGui.QColor(shrinking_roi_rgb[0],
                                                    shrinking_roi_rgb[1],
                                                    shrinking_roi_rgb[2]),
                              'width': 0.01,
                              'dashes_pattern': [4, 2]}
    fit_rgb = (0, 255, 0)

    shrinking_roi_id = None
    shrinking_roi = {'x0': None,
                     'y0': None,
                     'width': None,
                     'height': None}
    previous_roi_selection = {'width': None,
                              'height': None}
    image_size = {'width': None,
                  'height': None}
    roi_id = None
    xaxis_label = {'index': "File index",
                   'tof': u"TOF (\u00B5s)",
                   'lambda': u"\u03BB (\u212B)"}
    fitting_rois = {'kropff': {'step1': None,
                               'step2': None,
                               'step3': None,
                               },
                    }

    is_file_imported = False # True only when the import button has been used
    bragg_edge_range_ui = None

    kropff_fitting_range = {'high': [None, None],
                            'low': [None, None],
                            'bragg_peak': [None, None]}
    fitting_peak_ui = None  # vertical line in fitting view (tab 2)

    # fitting_input_dictionary = {'xaxis': {'index': ([], 'File index'),
    #                                       'lambda': ([], 'lambda (Angstroms)'),
    #                                       'tof': ([], 'TOF (micros)')},
    #                             'rois': {0: {'x0': None,
    #                                          'y0': None,
    #                                          'width': None,
    #                                          'height': None,
    #                                          'profile': [],
    #                                          'fitting': {'kropff': {'high': {'a0': None,
    #                                                                          'b0': None,
    #                                                                          'a0_error': None,
    #                                                                          'b0_error': None,
    #                                                                          'yaxis_fitted': [],
    #                                                                          'xaxis_to_fit': [],
    #                                                                          },
    #                                                                  'low': {'ahkl': None,
    #                                                                          'bhkl': None,
    #                                                                          'ahkl_error': None,
    #                                                                          'bhkl_error': None},
    #                                                                  'bragg_peak: {'lambda_hkl': None,
    #                                                                                'tau': None,
    #                                                                                'sigma': None,
    #                                                                                'lambda_hkl_error': None,
    #                                                                                'tau_error': None,
    #                                                                                'sigma_error': None},
    #                                                                 },
    #                                                      'TBD' : {},
    #                                                     },
    #                                          },
    #                                      },
    #                             'fit_infos': {'high_lambda': {},         # do we have a range selected
    #                                           'low_lambda': {},
    #                                           'bragg_peak': {},
    #                                           },
    #                             }

    ## list of width and height after importing a file (will be used in the profile slider (top right))
    # dict_rois_imported = {0: {'width': None, 'height': None},
    #                       1: {'width': None, 'height': None},
    #                       }

    def __init__(self, parent=None, working_dir="", o_bragg=None, spectra_file=None):

        if o_bragg:
            # self.working_dir = o_bragg.working_dir
            self.o_norm = o_bragg.o_norm
            self.working_dir = self.retrieve_working_dir()
            self.o_bragg = o_bragg
            show_selection_tab = True
            # default_tab = 0
            enabled_export_button = True
            self.index_array = np.arange(len(self.o_norm.data['sample']['file_name']))
        else:
            self.working_dir = working_dir
            show_selection_tab = False
            # default_tab = 1
            enabled_export_button = False

        if spectra_file:
            self.spectra_file = spectra_file

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        super(Interface, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_bragg_edge_peak_fitting.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Peak Fitting Tool")

        if show_selection_tab:
            # initialization
            o_init = Initialization(parent=self)
            o_init.display(image=self.get_live_image())
            self.load_time_spectra()
            self.roi_moved()
        else:
            o_init = Initialization(parent=self, tab='2')
            self.disable_left_part_of_selection_tab()
            self.ui.tabWidget.setEnabled(False)

        self.ui.tabWidget.setTabEnabled(1, False)
        # self.ui.tabWidget.setCurrentIndex(default_tab)
        self.ui.actionExport.setEnabled(enabled_export_button)
        self.update_selection_roi_slider_changed()

    def retrieve_working_dir(self):
        o_norm = self.o_norm
        file_path = o_norm.data['sample']['file_name'][0]
        return os.path.dirname(file_path)

    def load_time_spectra(self):
        self.tof_handler = TOF(filename=self.spectra_file)
        self.tof_array_s = self.tof_handler.tof_array
        self.update_time_spectra()

    def update_time_spectra(self):
        try:
            distance_source_detector_m = np.float(self.ui.distance_detector_sample.text())
            self.ui.statusbar.showMessage("", 100)  # 10s
        except ValueError:
            self.ui.statusbar.showMessage("distance source detector input is WRONG", 120000)  # 2mn
            self.ui.statusbar.setStyleSheet("color: red")
            return

        try:
            detector_offset_micros = np.float(self.ui.detector_offset.text())
            self.ui.statusbar.showMessage("", 100)  # 10s
        except ValueError:
            self.ui.statusbar.showMessage("detector offset input is WRONG", 120000)  # 2mn
            self.ui.statusbar.setStyleSheet("color: red")
            return

        _exp = Experiment(tof=self.tof_array_s,
                          distance_source_detector_m=distance_source_detector_m,
                          detector_offset_micros=detector_offset_micros)
        self.lambda_array = _exp.lambda_array * 1e10  # to be in Angstroms

    def get_live_image(self):
        if DEBUGGING:
            final_array = self.o_norm.data['sample']['data']
        else:
            nbr_data_to_use = np.int(self.number_of_data_to_use_ui.value)

            _data = self.o_norm.data['sample']['data']

            nbr_images = len(_data)
            list_of_indexes_to_keep = random.sample(list(range(nbr_images)), nbr_data_to_use)

            final_array = []
            for _index in list_of_indexes_to_keep:
                final_array.append(_data[_index])

        final_image = np.mean(final_array, axis=0)
        self.final_image = final_image
        return final_image

    @staticmethod
    def check_size(x_axis=None, y_axis=None):
        size_x = len(x_axis)
        size_y = len(y_axis)
        min_len = np.min([size_x, size_y])
        return x_axis[:min_len], y_axis[:min_len]

    def roi_moved(self):
        self.update_selection_profile_plot()
        self.update_all_size_widgets_infos()
        self.update_roi_defined_by_profile_of_bin_size_slider()

    def new_dimensions_within_error_range(self):
        """this method is used to check if the ROI sizes changed. We need an error uncertainties as sometimes
        the region varies by + or - 1 pixel when moving it around"""
        error = 1    # # of pixel

        roi_id = self.roi_id
        region = roi_id.getArraySlice(self.final_image,
                                      self.ui.image_view.imageItem)
        x0 = region[0][0].start
        x1 = region[0][0].stop
        y0 = region[0][1].start
        y1 = region[0][1].stop

        new_width = x1-x0-1
        new_height = y1-y0-1

        if ((np.abs(new_width - np.int(self.ui.roi_width.text())) <= error) and
            (np.abs(new_height) - np.int(self.ui.roi_height.text())) <= error):
            return True

        return False

    def update_all_size_widgets_infos(self):

        if self.ui.square_roi_radiobutton.isChecked():
            return

        roi_id = self.roi_id
        region = roi_id.getArraySlice(self.final_image,
                                      self.ui.image_view.imageItem)
        x0 = region[0][0].start
        x1 = region[0][0].stop
        y0 = region[0][1].start
        y1 = region[0][1].stop

        new_width = x1-x0-1
        new_height = y1-y0-1

        # if new width and height is the same as before, just skip that step
        if self.new_dimensions_within_error_range():
            return

        self.ui.roi_width.setText(str(new_width))
        self.ui.roi_height.setText(str(new_height))
        self.ui.profile_of_bin_size_width.setText(str(new_width))
        self.ui.profile_of_bin_size_height.setText(str(new_height))

        max_value = np.min([new_width, new_height])
        self.ui.profile_of_bin_size_slider.setValue(max_value)
        self.ui.profile_of_bin_size_slider.setMaximum(max_value)

    def get_shrinking_roi_dimension(self):
        coordinates = self.get_coordinates_of_new_inside_selection_box()
        return [coordinates['x0'],
                coordinates['y0'],
                coordinates['x0'] + coordinates['width'],
                coordinates['y0'] + coordinates['height']]

    def update_selection_profile_plot(self):

        if self.is_file_imported:
            self.update_selection_plot()
            self.update_vertical_line_in_profile_plot()

        else:
            o_get = Get(parent=self)
            x_axis, x_axis_label = o_get.x_axis()
            self.ui.profile.clear()

            # large selection region
            [x0, y0, x1, y1, _, _] = o_get.selection_roi_dimension()
            profile = o_get.profile_of_roi(x0, y0, x1, y1)
            x_axis, y_axis = Interface.check_size(x_axis=x_axis,
                                                  y_axis=profile)
            self.ui.profile.plot(x_axis, y_axis, pen=(self.selection_roi_rgb[0],
                                                      self.selection_roi_rgb[1],
                                                      self.selection_roi_rgb[2]))

            # shrinkable region
            shrinking_roi = self.get_coordinates_of_new_inside_selection_box()
            x0 = shrinking_roi['x0']
            y0 = shrinking_roi['y0']
            x1 = shrinking_roi['x1']
            y1 = shrinking_roi['y1']
            profile = o_get.profile_of_roi(x0, y0, x1, y1)
            x_axis, y_axis = Interface.check_size(x_axis=x_axis,
                                                  y_axis=profile)
            self.ui.profile.plot(x_axis, y_axis, pen=(self.shrinking_roi_rgb[0],
                                                      self.shrinking_roi_rgb[1],
                                                      self.shrinking_roi_rgb[2]))
            self.ui.profile.setLabel("bottom", x_axis_label)
            self.ui.profile.setLabel("left", 'Mean counts')

            # vertical line showing peak to fit
            bragg_edge_range = [x_axis[self.bragg_edge_range[0]],
                                x_axis[self.bragg_edge_range[1]]]

            self.bragg_edge_range_ui = pg.LinearRegionItem(values=bragg_edge_range,
                                                           orientation=None,
                                                           brush=None,
                                                           movable=True,
                                                           bounds=None)
            self.bragg_edge_range_ui.sigRegionChanged.connect(self.bragg_edge_range_changed)
            self.bragg_edge_range_ui.setZValue(-10)
            self.ui.profile.addItem(self.bragg_edge_range_ui)

    def bragg_edge_range_changed(self):
        [left_range, right_range] = list(self.bragg_edge_range_ui.getRegion())
        o_get = Get(parent=self)
        x_axis, _ = o_get.x_axis()

        left_index = find_nearest_index(array=x_axis, value=left_range)
        right_index = find_nearest_index(array=x_axis, value=right_range)

        self.bragg_edge_range = [left_index, right_index]

    def reset_profile_of_bin_size_slider(self):
        max_value = np.min([np.int(str(self.ui.profile_of_bin_size_width.text())),
                            np.int(str(self.ui.profile_of_bin_size_height.text()))])
        self.ui.profile_of_bin_size_slider.setMaximum(max_value)
        self.ui.profile_of_bin_size_slider.setValue(max_value)

    def update_selection(self, new_value=None, mode='square'):
        if self.roi_id is None:
            return

        try:
            region = self.roi_id.getArraySlice(self.final_image, self.ui.image_view.imageItem)
        except TypeError:
            return

        x0 = region[0][0].start
        y0 = region[0][1].start
        self.selection_x0y0 = [x0, y0]

        # remove old one
        self.ui.image_view.removeItem(self.roi_id)

        _pen = QtGui.QPen()
        _pen.setColor(self.roi_settings['color'])
        _pen.setWidth(self.roi_settings['width'])
        self.roi_id = pg.ROI([x0, y0],
                             [new_value, new_value],
                             pen=_pen,
                             scaleSnap=True)

        self.ui.image_view.addItem(self.roi_id)
        self.roi_id.sigRegionChanged.connect(self.roi_moved)

        if mode == 'square':
            self.ui.roi_width.setText(str(new_value))
            self.ui.roi_height.setText(str(new_value))
            self.reset_profile_of_bin_size_slider()
            self.update_profile_of_bin_size_infos()
        else:
            self.roi_id.addScaleHandle([1, 1], [0, 0])

        self.update_selection_profile_plot()
        self.update_roi_defined_by_profile_of_bin_size_slider()

    def update_selection_roi_slider_changed(self):
        value = self.ui.roi_size_slider.value()
        self.selection_roi_slider_changed(value)

    def selection_roi_slider_changed(self, new_value):
        if self.ui.square_roi_radiobutton.isChecked():
            mode = 'square'
        else:
            mode = 'free'
        self.update_selection(new_value=new_value,
                              mode=mode)

    def update_profile_of_bin_size_infos(self):
        _width = np.int(self.ui.roi_width.text())
        _height = np.int(self.ui.roi_height.text())
        self.ui.profile_of_bin_size_width.setText(str(_width))
        self.ui.profile_of_bin_size_height.setText(str(_height))
        self.ui.profile_of_bin_size_slider.setValue(np.min([_width, _height]))

    def distance_detector_sample_changed(self):
        self.update_time_spectra()
        self.update_selection_profile_plot()

    def detector_offset_changed(self):
        self.update_time_spectra()
        self.update_selection_profile_plot()

    def selection_axis_changed(self):
        self.update_selection_profile_plot()

    def update_dict_profile_to_fit(self):
        [left_range, right_range] = self.bragg_edge_range

        [x0, y0, x1, y1] = self.get_shrinking_roi_dimension()
        o_get = Get(parent=self)
        profile = o_get.profile_of_roi(x0=x0, y0=y0,
                                       x1=x1, y1=y1)

        yaxis = profile[left_range: right_range]

        all_x_axis = o_get.all_x_axis()
        index_array = all_x_axis['index'][0]
        tof_array = all_x_axis['tof'][0]
        lambda_array = all_x_axis['lambda'][0]

        index_selected = index_array[left_range: right_range]
        tof_selected = tof_array[left_range: right_range]
        lambda_selected = lambda_array[left_range: right_range]

        profile_to_fit = {'yaxis': yaxis,
                          'xaxis': {'index': index_selected,
                                    'tof': tof_selected,
                                    'lambda': lambda_selected},
                          }
        self.dict_profile_to_fit = profile_to_fit

    def fit_that_selection_pushed_by_program(self, initialize_region=True):
        o_get = Get(parent=self)
        x_axis = o_get.all_x_axis()
        dict_regions = o_get.all_russian_doll_region_full_infos()

        o_init = PeakFittingInitialization(parent=self)
        fitting_input_dictionary = o_init.fitting_input_dictionary(nbr_rois=len(dict_regions))
        self.append_dict_regions_to_fitting_input_dictionary(dict_regions, fitting_input_dictionary)

        fitting_input_dictionary['xaxis'] = x_axis
        # fitting_input_dictionary['rois'] = dict_regions

        self.fitting_input_dictionary = fitting_input_dictionary

        o_kropff = Kropff(parent=self)
        o_kropff.reset_all_table()
        # self.reset_all_kropff_fitting_table()

        if initialize_region:
            self.initialize_default_peak_regions()
        self.ui.tabWidget.setTabEnabled(1, True)
        self.select_first_row_of_all_fitting_table()

    def append_dict_regions_to_fitting_input_dictionary(self, dict_regions, fitting_input_dictionary):
        for _row in dict_regions.keys():
            _entry = dict_regions[_row]
            for _key in _entry.keys():
                fitting_input_dictionary['rois'][_row][_key] = _entry[_key]

    def fit_that_selection_pushed(self):
        """this will create the fitting_input_dictionary and initialize the table"""
        self.fit_that_selection_pushed_by_program(initialize_region=True)

    def initialize_default_peak_regions(self):
        [left_range, right_range] = self.bragg_edge_range
        xaxis_dict = self.fitting_input_dictionary['xaxis']
        xaxis_index, _ = xaxis_dict['index']
        [left_xaxis_index, right_xaxis_index] = self.bragg_edge_range
        xaxis = xaxis_index[left_xaxis_index: right_xaxis_index]
        left_index = find_nearest_index(array=xaxis, value=left_range)
        right_index = find_nearest_index(array=xaxis, value=right_range)

        # kropff tab
        for _key in self.kropff_fitting_range.keys():
            self.kropff_fitting_range[_key] = [left_index, right_index]

        # TBD tab
        pass

    def profile_of_bin_size_slider_changed_after_import(self, new_value):
        dict_rois_imported = self.dict_rois_imported
        new_width = dict_rois_imported[new_value]['width']
        new_height = dict_rois_imported[new_value]['height']
        self.ui.profile_of_bin_size_height.setText(new_height)
        self.ui.profile_of_bin_size_width.setText(new_width)
        self.update_selection_plot()
        self.update_vertical_line_in_profile_plot()

    def profile_of_bin_size_slider_changed(self, new_value):
        try:
            self.update_dict_profile_to_fit()
            if self.ui.square_roi_radiobutton.isChecked():
                new_width = new_value
                new_height = new_value
            else:
                initial_roi_width = np.int(str(self.ui.roi_width.text()))
                initial_roi_height = np.int(str(self.ui.roi_height.text()))
                if initial_roi_width == initial_roi_height:
                    new_width = new_value
                    new_height = new_value
                elif initial_roi_width < initial_roi_height:
                    new_width = new_value
                    delta = initial_roi_width - new_width
                    new_height = initial_roi_height - delta
                else:
                    new_height = new_value
                    delta = initial_roi_height - new_height
                    new_width = initial_roi_width - delta

            self.ui.profile_of_bin_size_width.setText(str(new_width))
            self.ui.profile_of_bin_size_height.setText(str(new_height))
            self.update_roi_defined_by_profile_of_bin_size_slider()
            self.update_selection_profile_plot()
        except AttributeError:
            pass

    def update_roi_defined_by_profile_of_bin_size_slider(self):
        coordinates_new_selection = self.get_coordinates_of_new_inside_selection_box()
        self.shrinking_roi = coordinates_new_selection
        x0 = coordinates_new_selection['x0']
        y0 = coordinates_new_selection['y0']
        width = coordinates_new_selection['width']
        height = coordinates_new_selection['height']

        # remove old selection
        if self.shrinking_roi_id:
            self.ui.image_view.removeItem(self.shrinking_roi_id)

        # plot new box
        _pen = QtGui.QPen()
        _pen.setDashPattern(self.shrinking_roi_settings['dashes_pattern'])
        _pen.setColor(self.shrinking_roi_settings['color'])
        _pen.setWidth(self.shrinking_roi_settings['width'])

        self.shrinking_roi_id = pg.ROI([x0, y0],
                                       [width, height],
                                       pen=_pen,
                                       scaleSnap=True,
                                       movable=False)
        self.ui.image_view.addItem(self.shrinking_roi_id)

    def get_coordinates_of_new_inside_selection_box(self):
        # get width and height defined in fitting labels (top right)
        width_requested = np.int(str(self.ui.profile_of_bin_size_width.text()))
        height_requested = np.int(str(self.ui.profile_of_bin_size_height.text()))

        # retrieve x0, y0, width and height of full selection
        region = self.roi_id.getArraySlice(self.final_image, self.ui.image_view.imageItem)
        x0 = region[0][0].start
        y0 = region[0][1].start
        # [x0, y0] = self.selection_x0y0
        width_full_selection = np.int(str(self.ui.roi_width.text()))
        height_full_selection = np.int(str(self.ui.roi_height.text()))

        delta_width = width_full_selection - width_requested
        delta_height = height_full_selection - height_requested

        new_x0 = x0 + np.int(delta_width / 2)
        new_y0 = y0 + np.int(delta_height / 2)

        return {'x0': new_x0, 'y0': new_y0,
                'x1': new_x0 + width_requested + 1, 'y1': new_y0 + height_requested + 1,
                'width': width_requested, 'height': height_requested}

    def add_profile_to_dict_of_all_regions(self, dict_regions=None):
        for _key in dict_regions.keys():
            current_region = dict_regions[_key]
            x0 = current_region['x0']
            y0 = current_region['y0']
            width = current_region['width']
            height = current_region['height']
            o_get = Get(parent=self)
            profile = o_get.profile_of_roi(x0=x0, y0=y0,
                                           x1=x0 + width,
                                           y1=y0 + height)
            current_region['profile'] = profile

    def select_first_row_of_all_fitting_table(self):
        self.ui.high_lambda_tableWidget.selectRow(0)
        self.ui.low_lambda_tableWidget.selectRow(0)
        self.ui.bragg_edge_tableWidget.selectRow(0)

    def fitting_axis_changed(self):
        self.update_fitting_plot()

    def high_lambda_table_clicked(self):
        self.update_fitting_plot()

    def low_lambda_table_clicked(self):
        self.update_fitting_plot()

    def bragg_peak_table_clicked(self):
        self.update_fitting_plot()

    def update_fitting_plot(self):
        self.ui.fitting.clear()
        o_get = Get(parent=self)
        part_of_fitting_dict = o_get.part_of_fitting_selected()
        name_of_page = part_of_fitting_dict['name_of_page']
        table_ui = part_of_fitting_dict['table_ui']

        o_table = TableHandler(table_ui=table_ui)
        row_selected = o_table.get_row_selected()

        x_axis_selected = o_get.x_axis_checked()

        selected_roi = self.fitting_input_dictionary['rois'][row_selected]
        xaxis_dict = self.fitting_input_dictionary['xaxis']

        [left_xaxis_index, right_xaxis_index] = self.bragg_edge_range

        yaxis = selected_roi['profile']
        xaxis_index, xaxis_label = xaxis_dict[x_axis_selected]

        xaxis = xaxis_index[left_xaxis_index: right_xaxis_index]
        yaxis = yaxis[left_xaxis_index: right_xaxis_index]

        self.ui.fitting.setLabel("bottom", xaxis_label)
        self.ui.fitting.setLabel("left", 'Mean counts')
        self.ui.fitting.plot(xaxis, yaxis, pen=(self.selection_roi_rgb[0],
                                                self.selection_roi_rgb[1],
                                                self.selection_roi_rgb[2]))

        peak_range_index = self.kropff_fitting_range[name_of_page]
        if peak_range_index[0] is None:
            peak_range = self.bragg_edge_range
        else:
            peak_range = [xaxis[peak_range_index[0]], xaxis[peak_range_index[1]]]

        if self.fitting_peak_ui:
            self.ui.fitting.removeItem(self.fitting_peak_ui)
        self.fitting_peak_ui = pg.LinearRegionItem(values=peak_range,
                                                   orientation=None,
                                                   brush=None,
                                                   movable=True,
                                                   bounds=None)
        self.fitting_peak_ui.sigRegionChanged.connect(self.fitting_range_changed)
        self.fitting_peak_ui.setZValue(-10)
        self.ui.fitting.addItem(self.fitting_peak_ui)

        o_gui = GuiUtility(parent=self)
        algo_name = o_gui.get_tab_selected(self.ui.tab_algorithm).lower()

        if Interface.key_path_exists_in_dictionary(dictionary=self.fitting_input_dictionary,
                tree_key = ['rois', row_selected, 'fitting', algo_name, name_of_page, 'xaxis_to_fit']):

            # show fit only if lambda scale selected
            if x_axis_selected == 'lambda':
                _entry = self.fitting_input_dictionary['rois'][row_selected]['fitting'][algo_name][name_of_page]
                xaxis = _entry['xaxis_to_fit']
                yaxis = _entry['yaxis_fitted']
                self.ui.fitting.plot(xaxis, yaxis, pen=(self.fit_rgb[0], self.fit_rgb[1], self.fit_rgb[2]))

        if peak_range_index[0] is None:
            self.fitting_range_changed()

    @staticmethod
    def key_path_exists_in_dictionary(dictionary=None, tree_key=None):
        """this method checks if full key path in the dictionary exists"""
        top_dictionary = dictionary
        for _key in tree_key:
            if top_dictionary.get(_key, None) is None:
                return False
            top_dictionary = top_dictionary.get(_key)
        return True

    def fitting_range_changed(self):
        [left_range, right_range] = list(self.fitting_peak_ui.getRegion())
        xaxis_dict = self.fitting_input_dictionary['xaxis']
        o_get = Get(parent=self)
        x_axis_selected = o_get.x_axis_checked()
        xaxis_index, _ = xaxis_dict[x_axis_selected]

        [left_xaxis_index, right_xaxis_index] = self.bragg_edge_range
        xaxis = xaxis_index[left_xaxis_index: right_xaxis_index]

        left_index = find_nearest_index(array=xaxis, value=left_range)
        right_index = find_nearest_index(array=xaxis, value=right_range)

        part_of_fitting_dict = o_get.part_of_fitting_selected()
        name_of_page = part_of_fitting_dict['name_of_page']

        self.kropff_fitting_range[name_of_page] = [left_index, right_index]

    def switching_master_tab_clicked(self, tab_index):
        if tab_index == 1:
            self.ui.working_folder_value.setText(self.working_dir)

    def update_selection_plot(self):
        # o_init = PeakFittingInitialization(parent=self)
        # self.fitting_input_dictionary = o_init.fitting_input_dictionary()

        self.ui.profile.clear()
        o_get = Get(parent=self)
        x_axis, x_axis_label = o_get.x_axis()
        max_value = self.ui.profile_of_bin_size_slider.maximum()
        roi_selected = max_value - self.ui.profile_of_bin_size_slider.value()

        y_axis = self.fitting_input_dictionary['rois'][roi_selected]['profile']

        self.ui.profile.plot(x_axis, y_axis, pen=(self.shrinking_roi_rgb[0],
                                                  self.shrinking_roi_rgb[1],
                                                  self.shrinking_roi_rgb[2]))
        self.ui.profile.setLabel("bottom", x_axis_label)
        self.ui.profile.setLabel("left", 'Mean counts')

        # full region
        y_axis = self.fitting_input_dictionary['rois'][0]['profile']
        self.ui.profile.plot(x_axis, y_axis, pen=(self.selection_roi_rgb[0],
                                                  self.selection_roi_rgb[1],
                                                  self.selection_roi_rgb[2]))

    def update_profile_of_bin_slider_widget(self):
        self.change_profile_of_bin_slider_signal()
        fitting_input_dictionary = self.fitting_input_dictionary
        dict_rois_imported = OrderedDict()
        nbr_key = len(fitting_input_dictionary['rois'].keys())
        for _index, _key in enumerate(fitting_input_dictionary['rois'].keys()):
            dict_rois_imported[nbr_key - 1 - _index] = {'width': fitting_input_dictionary['rois'][_key]['width'],
                                                        'height': fitting_input_dictionary['rois'][_key]['height']}
        self.dict_rois_imported = dict_rois_imported
        self.ui.profile_of_bin_size_slider.setRange(0, len(dict_rois_imported)-1)
        # self.ui.profile_of_bin_size_slider.setMinimum(0)
        # self.ui.profile_of_bin_size_slider.setMaximum(len(dict_rois_imported)-1)
        self.ui.profile_of_bin_size_slider.setSingleStep(1)
        self.ui.profile_of_bin_size_slider.setValue(len(dict_rois_imported)-1)
        self.update_profile_of_bin_slider_labels()

    def update_profile_of_bin_slider_labels(self):
        slider_value = self.ui.profile_of_bin_size_slider.value()
        self.profile_of_bin_size_slider_changed_after_import(slider_value)

    def change_profile_of_bin_slider_signal(self):
        self.ui.profile_of_bin_size_slider.valueChanged.disconnect()
        self.ui.profile_of_bin_size_slider.valueChanged.connect(self.profile_of_bin_size_slider_changed_after_import)

    def update_vertical_line_in_profile_plot(self):
        o_get = Get(parent=self)
        x_axis, x_axis_label = o_get.x_axis()

        bragg_edge_range = [x_axis[self.bragg_edge_range[0]],
                            x_axis[self.bragg_edge_range[1]]]

        if self.bragg_edge_range_ui:
            self.ui.profile.removeItem(self.bragg_edge_range_ui)
        self.bragg_edge_range_ui = pg.LinearRegionItem(values=bragg_edge_range,
                                                       orientation=None,
                                                       brush=None,
                                                       movable=True,
                                                       bounds=None)
        self.bragg_edge_range_ui.sigRegionChanged.connect(self.bragg_edge_range_changed)
        self.bragg_edge_range_ui.setZValue(-10)
        self.ui.profile.addItem(self.bragg_edge_range_ui)

    # event handler
    def import_button_clicked(self):
        o_import = ImportHandler(parent=self)
        o_import.run()

    def full_reset_of_ui(self):
        o_table = TableHandler(table_ui=self.ui.high_lambda_tableWidget)
        o_table.remove_all_rows()

        o_table = TableHandler(table_ui=self.ui.low_lambda_tableWidget)
        o_table.remove_all_rows()

        o_table = TableHandler(table_ui=self.ui.bragg_edge_tableWidget)
        o_table.remove_all_rows()

    def block_table_ui(self, flag):
        list_ui = [self.ui.high_lambda_tableWidget,
                   self.ui.low_lambda_tableWidget,
                   self.ui.bragg_edge_tableWidget]
        for _ui in list_ui:
            _ui.blockSignals(flag)

    def is_fit_infos_loaded(self):
        if 'fit_infos' in self.fitting_input_dictionary.keys():
            return True
        return False

    def disable_left_part_of_selection_tab(self):
        self.ui.groupBox.setEnabled(False)
        self.ui.image_view.setEnabled(False)
        self.ui.splitter.setSizes([0, 400])

    def export_button_clicked(self):
        o_export = ExportHandler(parent=self)
        o_export.configuration()

    def roi_radiobuttons_changed(self):
        if self.ui.square_roi_radiobutton.isChecked():
            slider_visible = True
            new_width = np.min([np.int(str(self.ui.roi_width.text())),
                                np.int(str(self.ui.roi_height.text()))])
            mode = 'square'
        else:
            slider_visible = False
            new_width = np.int(str(self.ui.roi_width.text()))
            self.selection_roi_slider_changed(new_width)
            mode = 'free'

        self.update_selection(new_value=new_width,
                              mode=mode)

        self.ui.roi_size_slider.setVisible(slider_visible)

    def kropff_toolbox_changed(self, new_index):
        self.update_fitting_plot()

    def kropff_fit_high_lambda_region_clicked(self):
        self.switch_fitting_axis_to_lambda()
        o_fit = FittingJobHandler(parent=self)
        o_fit.prepare(kropff_tooldbox='high')
        o_fit.run_kropff_high_lambda(update_table_ui=True)
        self.update_fitting_plot()
        o_gui = GuiUtility(parent=self)
        o_gui.check_status_of_kropff_fitting_buttons()

    def kropff_fit_low_lambda_region_clicked(self):
        self.switch_fitting_axis_to_lambda()
        o_fit = FittingJobHandler(parent=self)
        o_fit.prepare(kropff_tooldbox='low')
        o_fit.run_kropff_low_lambda(update_table_ui=True)
        self.update_fitting_plot()
        o_gui = GuiUtility(parent=self)
        o_gui.check_status_of_kropff_fitting_buttons()

    def kropff_fit_bragg_peak_region_clicked(self):
        self.switch_fitting_axis_to_lambda()
        o_fit = FittingJobHandler(parent=self)
        o_fit.prepare(kropff_tooldbox='bragg_peak')
        o_fit.run_bragg_peak_lambda(update_table_ui=True)
        self.update_fitting_plot()

    def switch_fitting_axis_to_lambda(self):
        self.ui.fitting_lambda_radiobutton.setChecked(True)
        self.fitting_axis_changed()

    def cancel_clicked(self):
        self.close()

    def apply_clicked(self):
        # FIXME
        self.close()
