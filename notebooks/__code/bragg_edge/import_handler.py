from pathlib import Path
from qtpy.QtWidgets import QFileDialog
import numpy as np
from collections import OrderedDict

from __code.file_handler import read_bragg_edge_fitting_ascii_format
from __code.bragg_edge.peak_fitting_initialization import PeakFittingInitialization
from __code.bragg_edge.fitting_functions import kropff_high_lambda, kropff_low_lambda, kropff_bragg_peak_tof
from __code.bragg_edge.bragg_edge_peak_fitting_gui_utility import GuiUtility
from __code.bragg_edge.bragg_edge_selection_tab import BraggEdgeSelectionTab
from __code.bragg_edge.kropff import Kropff
from __code.bragg_edge.march_dollase import MarchDollase


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
            self.save_initial_roi_dimension_from_config_file(result_of_import['metadata']['columns']['3'])
            self.save_march_dollase_parameters(result_of_import['metadata'])
            self.parent.bragg_edge_range = result_of_import['metadata']['bragg_edge_range']
            self.parent.bragg_peak_selection_range = result_of_import['metadata']['bragg_peak_selection_range']

            self.update_selection_tab(result_of_import=result_of_import)
            self.update_interface(result_of_import=result_of_import)

            self.parent.ui.statusbar.showMessage("{} has been imported!".format(ascii_file[0]), 10000)  # 10s
            self.parent.ui.statusbar.setStyleSheet("color: green")

            o_selection = BraggEdgeSelectionTab(parent=self.parent)
            o_selection.update_profile_of_bin_slider_widget()
            o_selection.update_selection_plot()

            self.parent.ui.tabWidget.setTabEnabled(1, self.parent.is_fit_infos_loaded())
            self.parent.ui.tabWidget.setEnabled(True)
            self.parent.ui.actionExport.setEnabled(True)

            self.parent.fitting_procedure_started['kropff'] = result_of_import.get('metadata').get('kropff fitting '
                                                                                                   'procedure '
                                                                                                   'started', False)
            self.parent.fitting_procedure_started['march-dollase'] = result_of_import.get('metadata').get(
                    'march-dollase fitting procedure started', False)

            o_kropff = Kropff(parent=self.parent)
            o_kropff.reset_all_table()

            o_march = MarchDollase(parent=self.parent)
            o_march.reset_table()

            if result_of_import.get('metadata').get('kropff fitting procedure started', False):
                # fill tables with minimum contains
                o_kropff.fill_table_with_fitting_information()

            if result_of_import.get('metadata').get('march-dollase fitting procedure started', False):
                # fill tables with minimum contains
                o_march.fill_tables_with_fitting_information()
            o_march.fill_history_table_with_fitting_information()

            self.parent.select_first_row_of_all_fitting_table()

            # self.parent.initialize_default_peak_regions()

            self.parent.block_table_ui(False)
            self.parent.update_vertical_line_in_profile_plot()
            self.parent.update_fitting_plot()
            self.parent.kropff_fitting_range_changed()

            o_gui = GuiUtility(parent=self.parent)
            o_gui.check_status_of_kropff_fitting_buttons()

    def update_interface(self, result_of_import=None):
            self.create_fitting_input_dictionary_from_imported_ascii_file(result_of_import=result_of_import)
            self.parent.tof_array_s = self.parent.fitting_input_dictionary['xaxis']['tof'][0] * 1e-6
            self.parent.lambda_array = self.parent.fitting_input_dictionary['xaxis']['lambda'][0]
            self.parent.index_array = self.parent.fitting_input_dictionary['xaxis']['index'][0]

    def update_selection_tab(self, result_of_import=None):
        self.parent.ui.distance_detector_sample.setText(result_of_import['metadata']['distance_detector_sample'])
        self.parent.ui.detector_offset.setText(result_of_import['metadata']['detector_offset'])
        self.parent.disable_left_part_of_selection_tab()
        self.parent.ui.info_message_about_cyan.setVisible(False)

    def save_march_dollase_parameters(self, metadata_dict):
        march_dollase_history_table = metadata_dict['march-dollase history table']
        march_dollase_history_init = metadata_dict['march-dollase history init']

        march_dollase_fitting_history_table = []
        for _row_index in march_dollase_history_table.keys():
            str_flag = march_dollase_history_table[_row_index]
            list_flag = str_flag.split(",")
            list_flag = [_value.strip() for _value in list_flag]

            _row_flag = []
            for _value in list_flag:
                _flag = True if _value == "True" else False
                _row_flag.append(_flag)
            march_dollase_fitting_history_table.append(_row_flag)

        march_dollase_fitting_initial_parameters = {'sigma': march_dollase_history_init['sigma'],
                                                    'alpha': march_dollase_history_init['alpha'],
                                                    'd_spacing': np.NaN,
                                                    'a1': np.NaN,
                                                    'a2': np.NaN,
                                                    'a5': np.NaN,
                                                    'a6': np.NaN}

        self.parent.march_dollase_fitting_history_table = march_dollase_fitting_history_table
        self.parent.march_dollase_fitting_initial_parameters = march_dollase_fitting_initial_parameters
        self.parent.march_dollase_fitting_range_selected = metadata_dict['march-dollase bragg peak selection range']

    def save_initial_roi_dimension_from_config_file(self, column_3_dict):
        """column_3_dict = {'x0': value, 'y0': value, 'width': value, 'height': value}"""
        self.parent.roi_dimension_from_config_file = [column_3_dict['x0'],
                                                      column_3_dict['y0'],
                                                      None, None,
                                                      column_3_dict['width'],
                                                      column_3_dict['height']]

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
        self.parent.fitting_input_dictionary['bragg_edge_range'] = metadata['bragg_edge_range']

        data = result_of_import['data']
        tof_array = np.array(data['tof'])
        index_array = np.array(data['index'])
        lambda_array = np.array(data['lambda'])
        rois_dictionary = OrderedDict()

        lda_array_of_peak_selected = lambda_array[self.parent.bragg_edge_range[0]:
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

            xaxis_to_fit = lda_array_of_peak_selected[self.parent.kropff_fitting_range['high'][0]:
                                                      self.parent.kropff_fitting_range['high'][1]]
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['high']['xaxis_to_fit'] = \
            xaxis_to_fit

            kropff_a0 = np.NaN if columns_roi[str_col]['kropff']['a0'] == 'None' else float(columns_roi[str_col][
                                                                                                'kropff']['a0'])
            kropff_b0 = np.NaN if columns_roi[str_col]['kropff']['b0'] == 'None' else float(columns_roi[str_col][
                                                                                                'kropff']['b0'])
            yaxis_fitted = kropff_high_lambda(xaxis_to_fit,
                                              kropff_a0,
                                              kropff_b0)
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

            xaxis_to_fit = lda_array_of_peak_selected[self.parent.kropff_fitting_range['low'][0]:
                                                      self.parent.kropff_fitting_range['low'][1]]
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['low']['xaxis_to_fit'] = \
            xaxis_to_fit

            kropff_ahkl = np.NaN if columns_roi[str_col]['kropff']['ahkl'] == 'None' else float(columns_roi[str_col][
                                                                                                'kropff']['ahkl'])
            kropff_bhkl = np.NaN if columns_roi[str_col]['kropff']['bhkl'] == 'None' else float(columns_roi[str_col][
                                                                                                'kropff']['bhkl'])

            yaxis_fitted = kropff_low_lambda(xaxis_to_fit,
                                             kropff_a0,
                                             kropff_b0,
                                             kropff_ahkl,
                                             kropff_bhkl)
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['low']['yaxis_fitted'] = \
                yaxis_fitted

            # Bragg peak
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['bragg_peak']['ldahkl'] = \
                columns_roi[str_col]['kropff']['ldahkl']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['bragg_peak']['tau'] = \
                columns_roi[str_col]['kropff']['tau']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['bragg_peak']['sigma'] = \
                columns_roi[str_col]['kropff']['sigma']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['bragg_peak']['ldahkl_error']\
                = columns_roi[str_col]['kropff']['ldahkl_error']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['bragg_peak']['tau_error'] = \
                columns_roi[str_col]['kropff']['tau_error']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['bragg_peak']['sigma_error']\
                = \
                columns_roi[str_col]['kropff']['sigma_error']

            xaxis_to_fit = lda_array_of_peak_selected[self.parent.kropff_fitting_range['bragg_peak'][0]:
                                                      self.parent.kropff_fitting_range['bragg_peak'][1]]
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['bragg_peak']['xaxis_to_fit']\
                = \
            xaxis_to_fit

            kropff_tau = np.NaN if columns_roi[str_col]['kropff']['tau'] == 'None' else float(columns_roi[
                                                                                                     str_col][
                                                                                                     'kropff']['tau'])
            kropff_ldahkl = np.NaN if columns_roi[str_col]['kropff']['ldahkl'] == 'None' else float(columns_roi[
                                                                                                     str_col][
                                                                                                     'kropff'][
                                                                                                           'ldahkl'])
            kropff_sigma = np.NaN if columns_roi[str_col]['kropff']['sigma'] == 'None' else float(columns_roi[
                                                                                                     str_col][
                                                                                                     'kropff'][
                                                                                                         'sigma'])

            yaxis_fitted = kropff_bragg_peak_tof(xaxis_to_fit,
                                                 kropff_a0,
                                                 kropff_b0,
                                                 kropff_ahkl,
                                                 kropff_bhkl,
                                                 kropff_ldahkl,
                                                 kropff_sigma,
                                                 kropff_tau)
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['kropff']['bragg_peak']['yaxis_fitted']\
                = \
                yaxis_fitted

            # March_dollase
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['march_dollase']['d_spacing'] = \
                columns_roi[str_col]['march_dollase']['d_spacing']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['march_dollase']['sigma'] = \
                columns_roi[str_col]['march_dollase']['sigma']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['march_dollase']['alpha'] = \
                columns_roi[str_col]['march_dollase']['alpha']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['march_dollase']['a1'] = \
                columns_roi[str_col]['march_dollase']['a1']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['march_dollase']['a2'] = \
                columns_roi[str_col]['march_dollase']['a2']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['march_dollase']['a5'] = \
                columns_roi[str_col]['march_dollase']['a5']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['march_dollase']['a6'] = \
                columns_roi[str_col]['march_dollase']['a6']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['march_dollase']['d_spacing_error'] = \
                columns_roi[str_col]['march_dollase']['d_spacing_error']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['march_dollase']['sigma_error'] = \
                columns_roi[str_col]['march_dollase']['sigma_error']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['march_dollase']['alpha_error'] = \
                columns_roi[str_col]['march_dollase']['alpha_error']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['march_dollase']['a1_error'] = \
                columns_roi[str_col]['march_dollase']['a1_error']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['march_dollase']['a2_error'] = \
                columns_roi[str_col]['march_dollase']['a2_error']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['march_dollase']['a5_error'] = \
                columns_roi[str_col]['march_dollase']['a5_error']
            self.parent.fitting_input_dictionary['rois'][col_index]['fitting']['march_dollase']['a6_error'] = \
                columns_roi[str_col]['march_dollase']['a6_error']

        xaxis_dictionary = {'index': (index_array, self.parent.xaxis_label['index']),
                            'lambda': (lambda_array, self.parent.xaxis_label['lambda']),
                            'tof': (tof_array, self.parent.xaxis_label['tof'])}
        self.parent.fitting_input_dictionary['xaxis'] = xaxis_dictionary
        self.parent.fitting_input_dictionary['bragg_edge_range_selected'] = result_of_import['metadata']['bragg_edge_range']
