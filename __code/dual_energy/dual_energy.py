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
from __code import load_ui

from __code.dual_energy.interface_initialization import Initialization
from __code.dual_energy.selection_tab import SelectionTab
from __code.dual_energy.get import Get

from __code.bragg_edge.bragg_edge_peak_fitting_gui_utility import GuiUtility
from __code.utilities import find_nearest_index
from __code.table_handler import TableHandler
from __code.bragg_edge.kropff_fitting_job_handler import KropffFittingJobHandler
from __code.bragg_edge.march_dollase_fitting_job_handler import MarchDollaseFittingJobHandler
from __code.bragg_edge.kropff import Kropff
from __code.bragg_edge.march_dollase import MarchDollase
from __code.bragg_edge.export_handler import ExportHandler
from __code.bragg_edge.import_handler import ImportHandler
from __code.bragg_edge.bragg_edge_selection_tab import BraggEdgeSelectionTab
from __code.bragg_edge.peak_fitting_initialization import PeakFittingInitialization
from __code._utilities.array import exclude_y_value_when_error_is_nan

DEBUGGING = True


class DualEnergy(BraggEdgeParent):

    def load_ob(self, folder_selected):
        self.load_files(data_type='ob', folder=folder_selected)
        self.check_data_array_sizes()


class Interface(QMainWindow):

    live_image = None  # image displayed on the left (integrated sample images)

    profile_selection_range = [5, 20]   # in index units, the min and max ROI ranges in the right plot (profile plot)
    profile_selection_range_ui = None   # ROI ui of profile

    # # relative index of the bragg peak only part (kropff and March-Dollase)
    # bragg_peak_selection_range = [np.NaN, np.NaN]

    index_array = None
    tof_array_s = None
    lambda_array = None

    bin_size_value = {'index': 50,
                      'tof': np.NaN,
                      'lambda': np.NaN}

    selection_roi_rgb = (62, 13, 244)
    roi_settings = {'color': QtGui.QColor(selection_roi_rgb[0],
                                          selection_roi_rgb[1],
                                          selection_roi_rgb[2]),
                    'border_width': 0.01,
                    'position': [10, 10]}

    bin_roi_rgb = (50, 50, 50, 200)
    bin_line_settings = {'color': QtGui.QColor(bin_roi_rgb[0],
                                               bin_roi_rgb[1],
                                               bin_roi_rgb[2],
                                               bin_roi_rgb[3]),
                         'width': 0.005}

    list_bin_positions = {'index': [],
                          'tof': [],
                          'lambda': []}
    list_bin_ui = []

    previous_roi_selection = {'width': 50,
                              'height': 50}
    # shrinking_roi_rgb = (13, 214, 244)
    # shrinking_roi_settings = {'color': QtGui.QColor(shrinking_roi_rgb[0],
    #                                                 shrinking_roi_rgb[1],
    #                                                 shrinking_roi_rgb[2]),
    #                           'width': 0.01,
    #                           'dashes_pattern': [4, 2]}
    # fit_rgb = (0, 255, 0)
    #
    # shrinking_roi_id = None
    # shrinking_roi = {'x0': None,
    #                  'y0': None,
    #                  'width': None,
    #                  'height': None}
    # previous_roi_selection = {'width': None,
    #                           'height': None}
    # image_size = {'width': None,
    #               'height': None}
    # roi_id = None
    xaxis_label = {'index': "File index",
                   'tof': u"TOF (\u00B5s)",
                   'lambda': u"\u03BB (\u212B)"}
    xaxis_units = {'index': "File #",
                   'tof': u"\u00B5s",
                   'lambda': u"\u212B"}

    # fitting_rois = {'kropff': {'step1': None,
    #                            'step2': None,
    #                            'step3': None,
    #                            },
    #                 }
    #
    # is_file_imported = False # True only when the import button has been used
    # bragg_edge_range_ui = None
    #
    # kropff_fitting_range = {'high': [None, None],
    #                         'low': [None, None],
    #                         'bragg_peak': [None, None]}
    # fitting_peak_ui = None  # vertical line in fitting view (tab 2)
    #
    # fitting_procedure_started = {'march-dollase': False,
    #                              'kropff': False}
    #
    # # x0, y0, x1, y1, width, height
    # roi_dimension_from_config_file = [None, None, None, None, None, None]

    def __init__(self, parent=None, working_dir="", o_dual=None, spectra_file=None):

        if o_dual:
            self.o_norm = o_dual.o_norm
            self.working_dir = self.retrieve_working_dir()
            self.o_dual = o_dual
            self.index_array = np.arange(len(self.o_norm.data['sample']['file_name']))
        else:
            self.working_dir = working_dir
            # show_selection_tab = False
            # enabled_export_button = False

        if spectra_file:
            self.spectra_file = spectra_file

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that popped up \
            (maybe hidden behind this browser!)</span>'))

        super(Interface, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_dual_energy.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Dual Energy Analysis")

        o_init = Initialization(parent=self)
        o_init.display(image=self.get_live_image())
        self.load_time_spectra()
        self.roi_moved()
        o_selection = SelectionTab(parent=self)
        o_selection.calculate_bin_size_in_all_units()
        o_selection.make_list_of_bins()

        #     self.roi_moved()
        # else:
        #     o_init = Initialization(parent=self, tab='2')
        #     self.disable_left_part_of_selection_tab()
        #     self.ui.tabWidget.setEnabled(False)
        #
        # self.ui.tabWidget.setTabEnabled(1, False)
        # # self.ui.tabWidget.setCurrentIndex(default_tab)
        # self.ui.actionExport.setEnabled(enabled_export_button)
        #
        # o_selection = BraggEdgeSelectionTab(parent=self)
        # o_selection.update_selection_roi_slider_changed()

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
        self.live_image = final_image
        return final_image

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

    def switching_master_tab_clicked(self, tab_index):
        pass
        # if tab_index == 1:
        #     self.ui.working_folder_value.setText(self.working_dir)

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



    ### clean implementation after this
    def profile_selection_range_changed(self):
        """this method converts the ROI left and right position in current x-axis units to index units """
        [left_range, right_range] = list(self.profile_selection_range_ui.getRegion())
        o_get = Get(parent=self)
        x_axis, _ = o_get.x_axis()

        left_index = find_nearest_index(array=x_axis, value=left_range)
        right_index = find_nearest_index(array=x_axis, value=right_range)

        self.profile_selection_range = [left_index, right_index]

    # events triggered by
    def roi_moved(self):
        o_selection = SelectionTab(parent=self)
        o_selection.calculate_bin_size_in_all_units()
        o_selection.make_list_of_bins()
        o_selection.update_selection_profile_plot()

    # event handler
    def import_button_clicked(self):
        o_import = ImportHandler(parent=self)
        o_import.run()

    def selection_axis_changed(self):
        o_selection = SelectionTab(parent=self)
        o_selection.update_selection_profile_plot()
        o_selection.update_bin_size_widgets()

    def export_button_clicked(self):
        o_export = ExportHandler(parent=self)
        o_export.configuration()

    def distance_detector_sample_changed(self):
        self.update_time_spectra()
        o_selection = SelectionTab(parent=self)
        o_selection.calculate_bin_size_in_all_units()
        o_selection.make_list_of_bins()
        o_selection.update_selection_profile_plot()

    def detector_offset_changed(self):
        self.update_time_spectra()
        o_selection = SelectionTab(parent=self)
        o_selection.calculate_bin_size_in_all_units()
        o_selection.make_list_of_bins()
        o_selection.update_selection_profile_plot()

    def bin_size_returned_pressed(self):
        o_selection = SelectionTab(parent=self)
        o_selection.calculate_bin_size_in_all_units()
        o_selection.make_list_of_bins()
        o_selection.update_selection_profile_plot()

    def cancel_clicked(self):
        self.close()

    def apply_clicked(self):
        # FIXME
        self.close()
