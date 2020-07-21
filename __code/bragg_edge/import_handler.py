from pathlib import Path
from qtpy.QtWidgets import QFileDialog
import numpy as np
from collections import OrderedDict

from __code.file_handler import make_ascii_file, read_bragg_edge_fitting_ascii_format
from __code.bragg_edge.peak_fitting_initialization import PeakFittingInitialization
from __code.bragg_edge.fitting_functions import kropff_high_tof, kropff_low_tof, kropff_bragg_peak_tof
from __code.bragg_edge.bragg_edge_peak_fitting_gui_utility import GuiUtility


class ImportHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):
        working_dir = str(Path(self.parent.working_dir).parent)
        ascii_file = QFileDialog.getOpenFileName(self.parent,
                                                 caption="Select ASCII file",
                                                 directory=working_dir,
                                                 filter="ASCII (*.txt)")

        if ascii_file[0]:
            self.parent.full_reset_of_ui()
            self.parent.block_table_ui(True)

            self.parent.is_file_imported = True
            result_of_import = read_bragg_edge_fitting_ascii_format(full_file_name=str(ascii_file[0]))
            self.parent.bragg_edge_range = result_of_import['metadata']['bragg_edge_range']
            self.parent.ui.distance_detector_sample.setText(result_of_import['metadata']['distance_detector_sample'])
            self.parent.ui.detector_offset.setText(result_of_import['metadata']['detector_offset'])
            self.create_fitting_input_dictionary_from_imported_ascii_file(result_of_import)
            self.parent.tof_array_s = self.parent.fitting_input_dictionary['xaxis']['tof'][0] * 1e-6
            self.parent.lambda_array = self.parent.fitting_input_dictionary['xaxis']['lambda'][0]
            self.parent.index_array = self.parent.fitting_input_dictionary['xaxis']['index'][0]

            self.parent.ui.statusbar.showMessage("{} has been imported!".format(ascii_file), 10000)  # 10s
            self.parent.ui.statusbar.setStyleSheet("color: green")

            self.parent.disable_left_part_of_selection_tab()
            self.parent.ui.info_message_about_cyan.setVisible(False)
            self.parent.update_profile_of_bin_slider_widget()
            self.parent.update_selection_plot()
            self.parent.update_vertical_line_in_profile_plot()

            self.parent.ui.tabWidget.setTabEnabled(1, self.parent.is_fit_infos_loaded())
            self.parent.ui.tabWidget.setEnabled(True)
            self.parent.ui.actionExport.setEnabled(True)

            if result_of_import.get('metadata').get('fitting_procedure_started', False):
                self.parent.fit_that_selection_pushed_by_program(initialize_region=False)

            self.parent.block_table_ui(False)
            self.parent.update_fitting_plot()

            o_gui = GuiUtility(parent=self.parent)
            o_gui.check_status_of_kropff_fitting_buttons()

    def create_fitting_input_dictionary_from_imported_ascii_file(self, result_of_import):
        metadata = result_of_import['metadata']
        self.parent.kropff_fitting_range['high'] = metadata['kropff_high']
        self.parent.kropff_fitting_range['low'] = metadata['kropff_low']
        self.parent.kropff_fitting_range['bragg_peak'] = metadata['kropff_bragg_peak']

        self.parent.working_dir = metadata['base_folder']
        self.parent.bragg_edge_range = metadata['bragg_edge_range']

        columns_roi = metadata['columns']

        o_init = PeakFittingInitialization(parent=self.parent)
        self.parent.fitting_input_dictionary = o_init.fitting_input_dictionary(nbr_rois=len(columns_roi))

        data = result_of_import['data']
        tof_array = np.array(data['tof'])
        index_array = np.array(data['index'])
        lambda_array = np.array(data['lambda'])
        rois_dictionary = OrderedDict()

        tof_array_of_peak_selected = tof_array[self.parent.bragg_edge_range[0]:
                                               self.parent.bragg_edge_range[1]]

        for col in np.arange(3, len(columns_roi) + 3):
            str_col = str(col)
            col_index = col-3

            # high lambda
            self.parent.fitting_input_dictionary['rois'][col_index]['profile'] = np.array(data[str_col])
            self.parent.fitting_input_dictionary['rois'][col_index]['x0'] = columns_roi[str_col]['x0']
            self.parent.fitting_input_dictionary['rois'][col_index]['y0'] = columns_roi[str_col]['y0']
            self.parent.fitting_input_dictionary['rois'][col_index]['width'] = columns_roi[str_col]['width']
            self.parent.fitting_input_dictionary['rois'][col_index]['height'] = columns_roi[str_col]['height']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['high']['a0'] = \
                columns_roi[str_col]['kropff']['a0']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['high']['b0'] = \
                columns_roi[str_col]['kropff']['b0']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['high']['a0_error'] = \
                columns_roi[str_col]['kropff']['a0_error']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['high']['b0_error'] = \
                columns_roi[str_col]['kropff']['b0_error']

            xaxis_to_fit = tof_array_of_peak_selected[self.parent.kropff_fitting_range['high'][0]:
                                                      self.parent.kropff_fitting_range['high'][1]]
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['high']['xaxis_to_fit'] = \
            xaxis_to_fit
            yaxis_fitted = kropff_high_tof(xaxis_to_fit,
                                           np.float(columns_roi[str_col]['kropff']['a0']),
                                           np.float(columns_roi[str_col]['kropff']['b0']))
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['high']['yaxis_fitted'] = \
                yaxis_fitted

            # low lambda
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['low']['ahkl'] = \
                columns_roi[str_col]['kropff']['ahkl']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['low']['bhkl'] = \
                columns_roi[str_col]['kropff']['bhkl']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['low']['ahkl_error'] = \
                columns_roi[str_col]['kropff']['ahkl_error']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['low']['bhkl_error'] = \
                columns_roi[str_col]['kropff']['bhkl_error']

            xaxis_to_fit = tof_array_of_peak_selected[self.parent.kropff_fitting_range['low'][0]:
                                                      self.parent.kropff_fitting_range['low'][1]]
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['low']['xaxis_to_fit'] = \
            xaxis_to_fit
            yaxis_fitted = kropff_low_tof(xaxis_to_fit,
                                             np.float(columns_roi[str_col]['kropff']['a0']),
                                             np.float(columns_roi[str_col]['kropff']['b0']),
                                             np.float(columns_roi[str_col]['kropff']['ahkl']),
                                             np.float(columns_roi[str_col]['kropff']['bhkl']))
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['low']['yaxis_fitted'] = \
                yaxis_fitted

            # # Bragg peak
            # self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['bragg_peak']['lambdahkl'] = \
            #     columns_roi[str_col]['kropff']['lambdahkl']
            # self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['bragg_peak']['tau'] = \
            #     columns_roi[str_col]['kropff']['tau']
            # self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['bragg_peak']['sigma'] = \
            #     columns_roi[str_col]['kropff']['sigma']
            # self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['bragg_peak']['lambdahkl_error'] = \
            #     columns_roi[str_col]['kropff']['lambdahkl_error']
            # self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['bragg_peak']['tau_error'] = \
            #     columns_roi[str_col]['kropff']['tau_error']
            # self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['bragg_peak']['sigma_error']\
            #     = \
            #     columns_roi[str_col]['kropff']['sigma_error']
            #
            # xaxis_to_fit = lambda_array_of_peak_selected[self.parent.kropff_fitting_range['bragg_peak'][0]:
            #                                              self.parent.kropff_fitting_range['bragg_peak'][1]]
            # self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['bragg_peak']['xaxis_to_fit']\
            #     = \
            # xaxis_to_fit
            # yaxis_fitted = kropff_low_lambda(xaxis_to_fit,
            #                                  columns_roi[str_col]['kropff']['a0'],
            #                                  columns_roi[str_col]['kropff']['b0'],
            #                                  columns_roi[str_col]['kropff']['ahkl'],
            #                                  columns_roi[str_col]['kropff']['bhkl'],
            #                                  columns_roi[str_col]['kropff']['lambdahkl'],
            #                                  columns_roi[str_col]['kropff']['sigma'],
            #                                  columns_roi[str_col]['kropff']['tau'])
            # self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['bragg_peak']['yaxis_fitted']\
            #     = \
            #     yaxis_fitted

        xaxis_dictionary = {'index': (index_array, self.parent.xaxis_label['index']),
                            'lambda': (lambda_array, self.parent.xaxis_label['lambda']),
                            'tof': (tof_array, self.parent.xaxis_label['tof'])}
        self.parent.fitting_input_dictionary['xaxis'] = xaxis_dictionary
