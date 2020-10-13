from IPython.core.display import HTML
import os
import random
import numpy as np
from IPython.display import display
import pyqtgraph as pg
from qtpy.QtWidgets import QMainWindow
from qtpy import QtGui

from neutronbraggedge.experiment_handler import *

from __code.bragg_edge.bragg_edge_normalization import BraggEdge as BraggEdgeParent
from __code.bragg_edge.peak_fitting_interface_initialization import Initialization
from __code.bragg_edge.bragg_edge_peak_fitting_gui_utility import GuiUtility
from __code import load_ui
from __code.utilities import find_nearest_index
from __code.table_handler import TableHandler
from __code.bragg_edge.kropff_fitting_job_handler import KropffFittingJobHandler
from __code.bragg_edge.march_dollase_fitting_job_handler import MarchDollaseFittingJobHandler
from __code.bragg_edge.kropff import Kropff
from __code.bragg_edge.march_dollase import MarchDollase
from __code.bragg_edge.export_handler import ExportHandler
from __code.bragg_edge.import_handler import ImportHandler
from __code.bragg_edge.bragg_edge_selection_tab import BraggEdgeSelectionTab
from __code.bragg_edge.get import Get
from __code.bragg_edge.peak_fitting_initialization import PeakFittingInitialization
from __code._utilities.array import exclude_y_value_when_error_is_nan

DEBUGGING = True


class BraggEdge(BraggEdgeParent):

    def load_ob(self, folder_selected):
        self.load_files(data_type='ob', folder=folder_selected)
        self.check_data_array_sizes()
        self.divide_normalized_data_by_OB_white_beam()

    def divide_normalized_data_by_OB_white_beam(self):
        norm_data = self.o_norm.data['ob']['data']
        self.white_beam_ob = np.mean(norm_data, 0)


class Interface(QMainWindow):

    fitting_parameters_init = {'kropff': {'a0': 1,
                                          'b0': 1,
                                          'ahkl': 1,
                                          'bhkl': 1,
                                          'ldahkl': 1e-8,
                                          'tau': 1,
                                          'sigma': [1e-7, 1e-6, 1e-5]}}

    bragg_edge_range = [5, 20]

    # relative index of the bragg peak only part (kropff and March-Dollase)
    bragg_peak_selection_range = [np.NaN, np.NaN]

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

    fitting_procedure_started = {'march-dollase': False,
                                 'kropff': False}

    # x0, y0, x1, y1, width, height
    roi_dimension_from_config_file = [None, None, None, None, None, None]

    # fitting_input_dictionary = {'xaxis': {'index': ([], 'File index'),
    #                                       'lambda': ([], 'lambda (Angstroms)'),
    #                                       'tof': ([], 'TOF (micros)')},
    #                             'bragg_edge_range': [200, 500],
    #                             'bragg_peak_selection_range': [20, 30],  # only the bragg peak using relative peak
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
    #                                                                  'bragg_peak: {'ldahkl': None,
    #                                                                                'tau': None,
    #                                                                                'sigma': None,
    #                                                                                'ldahkl_error': None,
    #                                                                                'tau_error': None,
    #                                                                                'sigma_error': None},
    #                                                                 },
    #                                                      'march_dollase' : {'d_spacing': None,
    #                                                                         'd_spacing_error': None,
    #                                                                         'alpha': None,
    #                                                                         'alpha_error': None,
    #                                                                         'sigma': None,
    #                                                                         'sigma_error': None,
    #                                                                         'a1': None,
    #                                                                         'a1_error': None,
    #                                                                         'a2': None,
    #                                                                         'a2_error': None,
    #                                                                         'a5': None,
    #                                                                         'a5_error': None,
    #                                                                         'a6': None,
    #                                                                         'a6_error': None,
    #                                                                         },
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

    march_dollase_fitting_peak_ui = None   # ROI of march dollase peak region
    march_dollase_fitting_history_table = None
    march_dollase_fitting_initial_parameters = {'d_spacing': np.NaN,
                                                'sigma': 3.5,
                                                'alpha': 4.5,
                                                'a1': "row dependent",
                                                'a2': "row dependent",
                                                'a5': "row dependent",
                                                'a6': "row dependent"}
    march_dollase_fitting_history_table_default_new_row = None
    march_dollase_fitting_range_selected = None

    march_dollase_list_columns = ['d_spacing', 'sigma', 'alpha', 'a1', 'a2', 'a5', 'a6',
                                  'd_spacing_error', 'sigma_error', 'alpha_error',
                                  'a1_error', 'a2_error', 'a5_error', 'a6_error']

    # matplotlib canvas
    kropff_high_plot = None
    kropff_low_plot = None
    kropff_bragg_peak_plot = None
    march_dollase_plot = None

    def __init__(self, parent=None, working_dir="", o_bragg=None, spectra_file=None):

        if o_bragg:
            # self.working_dir = o_bragg.working_dir
            self.o_norm = o_bragg.o_norm
            self.working_dir = self.retrieve_working_dir()
            self.o_bragg = o_bragg
            show_selection_tab = True
            enabled_export_button = False
            self.index_array = np.arange(len(self.o_norm.data['sample']['file_name']))
        else:
            self.working_dir = working_dir
            show_selection_tab = False
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

        o_selection = BraggEdgeSelectionTab(parent=self)
        o_selection.update_selection_roi_slider_changed()

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

    def roi_moved(self):
        o_selection = BraggEdgeSelectionTab(parent=self)
        o_selection.update_selection_profile_plot()
        o_selection.update_all_size_widgets_infos()
        o_selection.update_roi_defined_by_profile_of_bin_size_slider()

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

    def selection_roi_slider_changed(self, new_value):
        if self.ui.square_roi_radiobutton.isChecked():
            mode = 'square'
        else:
            mode = 'free'
        o_selection = BraggEdgeSelectionTab(parent=self)
        o_selection.update_selection(new_value=new_value,
                                     mode=mode)

    def update_profile_of_bin_size_infos(self):
        _width = np.int(self.ui.roi_width.text())
        _height = np.int(self.ui.roi_height.text())
        self.ui.profile_of_bin_size_width.setText(str(_width))
        self.ui.profile_of_bin_size_height.setText(str(_height))
        self.ui.profile_of_bin_size_slider.setValue(np.min([_width, _height]))

    def distance_detector_sample_changed(self):
        self.update_time_spectra()
        o_selection = BraggEdgeSelectionTab(parent=self)
        o_selection.update_selection_profile_plot()

    def detector_offset_changed(self):
        self.update_time_spectra()
        o_selection = BraggEdgeSelectionTab(parent=self)
        o_selection.update_selection_profile_plot()

    def selection_axis_changed(self):
        o_selection = BraggEdgeSelectionTab(parent=self)
        o_selection.update_selection_profile_plot()

    def update_dict_profile_to_fit(self):
        [left_range, right_range] = self.bragg_edge_range

        o_selection = BraggEdgeSelectionTab(parent=self)
        [x0, y0, x1, y1] = o_selection.get_shrinking_roi_dimension()
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
        o_init.set_top_keys_values(fitting_input_dictionary,
                                   {'xaxis': x_axis,
                                    'bragg_edge_range': self.bragg_edge_range})
        self.append_dict_regions_to_fitting_input_dictionary(dict_regions, fitting_input_dictionary)

        # fitting_input_dictionary['xaxis'] = x_axis
        # fitting_input_dictionary['bragg_edge_range'] = self.bragg_edge_range

        self.fitting_input_dictionary = fitting_input_dictionary

        o_kropff = Kropff(parent=self)
        o_kropff.reset_all_table()

        # o_march = MarchDollase(parent=self)
        # o_march.reset_table()

        if initialize_region:
            self.initialize_default_peak_regions()
        else:
            if self.fitting_procedure_started['kropff']:
                o_kropff.fill_table_with_fitting_information()
        # o_march.fill_tables_with_fitting_information()

        # if initialize_region:
        #     o_march_fitting = MarchDollaseFittingJobHandler(parent=self)
        #     o_march_fitting.initialize_fitting_input_dictionary()

        self.ui.tabWidget.setTabEnabled(1, True)
        self.ui.actionExport.setEnabled(True)
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

        o_selection = BraggEdgeSelectionTab(parent=self)
        o_selection.update_selection_plot()

        self.update_vertical_line_in_profile_plot()
        self.update_kropff_fit_table_graph(fit_region='high')
        self.update_kropff_fit_table_graph(fit_region='low')
        self.update_kropff_fit_table_graph(fit_region='bragg_peak')

    def profile_of_bin_size_slider_changed(self, new_value):
        o_selection = BraggEdgeSelectionTab(parent=self)
        o_selection.profile_of_bin_size_slider_changed(new_value=new_value)

    def update_roi_defined_by_profile_of_bin_size_slider(self):
        o_selection = BraggEdgeSelectionTab(parent=self)
        o_selection.update_roi_defined_by_profile_of_bin_size_slider()

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
        self.ui.high_lda_tableWidget.selectRow(0)
        self.ui.low_lda_tableWidget.selectRow(0)
        self.ui.bragg_edge_tableWidget.selectRow(0)
        self.ui.march_dollase_result_table.selectRow(0)

    def fitting_axis_changed(self):
        self.update_fitting_plot()
        self.fitting_range_changed()

    def high_lambda_table_clicked(self):
        self.update_fitting_plot()
        # self.fitting_range_changed()

    def low_lambda_table_clicked(self):
        self.update_fitting_plot()
        # self.fitting_range_changed()

    def bragg_peak_table_clicked(self):
        self.update_fitting_plot()

    def update_fitting_plot(self):
        o_gui = GuiUtility(parent=self)
        algorithm_tab_selected = o_gui.get_tab_selected(tab_ui=self.ui.tab_algorithm)

        if algorithm_tab_selected == 'Kropff':
            o_kropff = Kropff(parent=self)
            o_kropff.update_fitting_plot()

        elif algorithm_tab_selected == 'March-Dollase':
            o_march = MarchDollase(parent=self)
            o_march.update_fitting_plot()

    def fitting_range_changed(self):
        o_gui = GuiUtility(parent=self)
        algorithm_tab_selected = o_gui.get_tab_selected(tab_ui=self.ui.tab_algorithm)

        if algorithm_tab_selected == 'Kropff':
            self.kropff_fitting_range_changed()
        elif algorithm_tab_selected == 'March-Dollase':
            self.march_dollase_fitting_range_changed()

    def kropff_fitting_range_changed(self):
        [global_left_range, global_right_range] = self.bragg_edge_range

        if not self.fitting_peak_ui:
            return

        [left_range, right_range] = list(self.fitting_peak_ui.getRegion())
        xaxis_dict = self.fitting_input_dictionary['xaxis']
        o_get = Get(parent=self)
        x_axis_selected = o_get.x_axis_checked()
        xaxis_index, _ = xaxis_dict[x_axis_selected]

        [left_xaxis_index, right_xaxis_index] = self.bragg_edge_range
        xaxis = xaxis_index[left_xaxis_index: right_xaxis_index]

        left_index = find_nearest_index(array=xaxis, value=left_range)
        right_index = find_nearest_index(array=xaxis, value=right_range)

        global_left_index = find_nearest_index(array=xaxis, value=global_left_range)
        global_left_index = 0 # for debugging
        global_right_index = find_nearest_index(array=xaxis, value=global_right_range)

        self.kropff_fitting_range['high'] = [right_index, global_right_index]
        self.kropff_fitting_range['low'] = [global_left_index, left_index]
        self.kropff_fitting_range['bragg_peak'] = [left_index, right_index]
        self.bragg_peak_selection_range = [left_index, right_index]

        print(f"left: {global_left_index}", end=" | ")

        o_kropff = Kropff(parent=self)
        o_kropff.update_roi_labels()

    def switching_master_tab_clicked(self, tab_index):
        if tab_index == 1:
            self.ui.working_folder_value.setText(self.working_dir)

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
        o_table = TableHandler(table_ui=self.ui.high_lda_tableWidget)
        o_table.remove_all_rows()

        o_table = TableHandler(table_ui=self.ui.low_lda_tableWidget)
        o_table.remove_all_rows()

        o_table = TableHandler(table_ui=self.ui.bragg_edge_tableWidget)
        o_table.remove_all_rows()

        o_table = TableHandler(table_ui=self.ui.march_dollase_result_table)
        o_table.remove_all_rows()

    def block_table_ui(self, flag):
        list_ui = [self.ui.high_lda_tableWidget,
                   self.ui.low_lda_tableWidget,
                   self.ui.bragg_edge_tableWidget,
                   self.ui.march_dollase_result_table]
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

        o_selection = BraggEdgeSelectionTab(parent=self)
        o_selection.update_selection(new_value=new_width,
                                     mode=mode)

        self.ui.roi_size_slider.setVisible(slider_visible)

    def kropff_toolbox_changed(self, new_index):
        self.update_fitting_plot()

    def fit_kropff_button_pushed(self):
        self.ui.eventProgress.setMaximum(4)
        self.ui.eventProgress.setValue(1)
        self.ui.eventProgress.setVisible(True)
        QtGui.QGuiApplication.processEvents()

        self.kropff_fit_high_lambda_region_clicked()
        self.ui.eventProgress.setValue(2)
        QtGui.QGuiApplication.processEvents()

        self.kropff_fit_low_lambda_region_clicked()
        self.ui.eventProgress.setValue(3)
        QtGui.QGuiApplication.processEvents()

        self.kropff_fit_bragg_peak_region_clicked()
        self.ui.eventProgress.setValue(4)
        QtGui.QGuiApplication.processEvents()

        self.ui.eventProgress.setVisible(False)
        self.ui.statusbar.setStyleSheet("color: blue")
        self.ui.statusbar.showMessage("Fitting Done!", 1000)  # 10s

        self.fitting_procedure_started['kropff'] = True

    def kropff_fit_high_lambda_region_clicked(self):
        self.switch_fitting_axis_to('lambda')
        o_fit = KropffFittingJobHandler(parent=self)
        o_fit.prepare(kropff_tooldbox='high')
        o_fit.run_kropff_high_lambda(update_table_ui=True)
        self.update_fitting_plot()
        self.update_kropff_fit_table_graph(fit_region='high')

    def kropff_fit_low_lambda_region_clicked(self):
        self.switch_fitting_axis_to('lambda')
        o_fit = KropffFittingJobHandler(parent=self)
        o_fit.prepare(kropff_tooldbox='low')
        o_fit.run_kropff_low_lambda(update_table_ui=True)
 #       self.update_fitting_plot()
        self.update_kropff_fit_table_graph(fit_region='low')

    def kropff_fit_bragg_peak_region_clicked(self):
        self.kropff_fit_bragg_peak_region_of_selected_rows()

    def kropff_fit_bragg_peak_region_of_selected_rows(self, list_row_to_fit=None):
        self.switch_fitting_axis_to('lambda')
        o_fit = KropffFittingJobHandler(parent=self)
        o_fit.prepare(kropff_tooldbox='bragg_peak')
        o_fit.run_bragg_peak(update_table_ui=True, list_row_to_fit=list_row_to_fit)
  #      self.update_fitting_plot()
        self.update_kropff_fit_table_graph(fit_region='bragg_peak')

    def update_kropff_fit_table_graph(self, fit_region='high'):
        """
        update the plot of the fit parameters selected
        :param fit_region: 'high', 'low' or 'bragg_peak'
        """
        o_gui = GuiUtility(parent=self)
        fit_parameter_selected = o_gui.get_kropff_fit_parameter_selected(fit_region=fit_region)
        parameter_array = []
        parameter_error_array = []
        fitting_input_dictionary = self.fitting_input_dictionary
        for _index in fitting_input_dictionary['rois'].keys():
            _parameter = fitting_input_dictionary['rois'][_index]['fitting']['kropff'][fit_region][fit_parameter_selected]
            _error = fitting_input_dictionary['rois'][_index]['fitting']['kropff'][fit_region]["{}_error".format(fit_parameter_selected)]
            parameter_array.append(_parameter)
            parameter_error_array.append(_error)
        plot_ui = o_gui.get_kropff_fit_graph_ui(fit_region=fit_region)
        x_array = np.arange(len(parameter_array))

        cleaned_parameter_array, cleaned_parameter_error_array = \
            exclude_y_value_when_error_is_nan(parameter_array,
                                              parameter_error_array)

        plot_ui.axes.cla()
        if fit_region == 'bragg_peak':
            plot_ui.axes.set_yscale("log")
        plot_ui.axes.errorbar(x_array,
                              cleaned_parameter_array,
                              cleaned_parameter_error_array,
                              marker='s')
        plot_ui.axes.set_xlabel("Row # (see Table tab)")
        plot_ui.draw()

    def kropff_bragg_peak_selection_mode_changed(self):
        if self.ui.kropff_bragg_peak_single_selection.isChecked():
            self.ui.bragg_edge_tableWidget.setSelectionMode(1)
        else:
            self.ui.bragg_edge_tableWidget.setSelectionMode(2)
        self.update_fitting_plot()

    def switch_fitting_axis_to(self, button_name='tof'):
        if button_name == 'tof':
            self.ui.fitting_tof_radiobutton.setChecked(True)
        elif button_name == 'lambda':
            self.ui.fitting_lambda_radiobutton.setChecked(True)
        else:
            self.ui.fitting_index_radiobutton.setChecked(True)
        self.fitting_axis_changed()

    def update_kropff_high_plot(self):
        self.update_kropff_fit_table_graph(fit_region='high')

    def update_kropff_low_plot(self):
        self.update_kropff_fit_table_graph(fit_region='low')

    def update_kropff_bragg_peak_plot(self):
        self.update_kropff_fit_table_graph(fit_region='bragg_peak')

    def kropff_bragg_peak_right_click(self, position):
        o_kropff = Kropff(parent=self)
        o_kropff.bragg_peak_right_click(position=position)

    def march_dollase_table_state_changed(self, state=None, row=None, column=None):
        o_march = MarchDollase(parent=self)
        if row == 0:
            _widget = self.ui.march_dollase_user_input_table.cellWidget(row, column).children()[-1]
            if (column == 1) or (column == 2):
                _textedit = _widget
                _textedit.setText(o_march.get_initial_parameter_value(column=column))
                _textedit.setVisible(not state)
            elif column == 0:
                _label = _widget
                _label.setText("{:0.6f}".format(np.float(o_march.get_initial_parameter_value(column=column))))
                _label.setVisible(not state)
            else:
                _label = _widget
                _label.setText("Row dependent")
                _label.setVisible(not state)

        o_march.save_table_history_and_initial_parameters()

    def march_dollase_table_init_value_changed(self, column):
        o_march = MarchDollase(parent=self)
        o_march.save_table_history_and_initial_parameters()

    def march_dollase_table_clicked(self, row, column):
        o_march = MarchDollase(parent=self)
        o_march.table_clicked(row=row, column=column)

    def march_dollase_move_row_up_clicked(self):
        o_march = MarchDollase(parent=self)
        o_march.move_row_up()

    def march_dollase_move_row_down_clicked(self):
        o_march = MarchDollase(parent=self)
        o_march.move_row_down()

    def march_dollase_table_right_clicked(self):
        o_march = MarchDollase(parent=self)
        o_march.table_right_clicked()

    def march_dollase_advanced_mode_clicked(self):
        o_march = MarchDollase(parent=self)
        o_march.advanced_mode_clicked()
        o_fit = MarchDollaseFittingJobHandler(parent=self)
        o_fit.initialize_fitting_input_dictionary()
        o_march.fill_history_table_with_fitting_information()

    def march_dollase_item_to_plot_changed(self):
        pass

    def tab_algorithm_changed(self, tab_index):
        self.update_fitting_plot()
        self.march_dollase_fitting_range_changed()

    def march_dollase_fit_button_clicked(self):
        o_fit = MarchDollaseFittingJobHandler(parent=self)
        o_fit.prepare()

    def march_dollase_result_table_clicked(self):
        self.update_fitting_plot()

    def march_dollase_result_selection_mode_clicked(self):
        if self.ui.march_dollase_result_single_selection.isChecked():
            self.ui.march_dollase_result_table.setSelectionMode(1)
        else:
            self.ui.march_dollase_result_table.setSelectionMode(2)
        self.update_fitting_plot()

    def march_dollase_toolbox_changed(self, index):
        self.update_fitting_plot()

    def march_dollase_fitting_range_changed(self):
        o_march = MarchDollase(parent=self)
        o_march.update_roi_labels()

        o_fit = MarchDollaseFittingJobHandler(parent=self)
        o_fit.initialize_d_spacing()
        o_march.fill_history_table_with_fitting_information()

    def march_dollase_result_table_right_clicked(self, point):
        o_march = MarchDollase(parent=self)
        o_march.result_table_right_click()

    def cancel_clicked(self):
        self.close()

    def apply_clicked(self):
        # FIXME
        self.close()
