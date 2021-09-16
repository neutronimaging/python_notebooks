from lmfit import Model
import numpy as np
from qtpy.QtWidgets import QApplication
import logging

from __code.bragg_edge.fitting_functions import march_dollase_basic_fit, march_dollase_advanced_fit
from __code.bragg_edge.get import Get


class MarchDollaseFittingJobHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def is_advanced_mode(self):
        if self.parent.ui.march_dollase_advanced_mode_checkBox.isChecked():
            return True
        else:
            return False

    def initialize_d_spacing(self):
        d_spacing = self.get_d_spacing()
        self.parent.march_dollase_fitting_initial_parameters['d_spacing'] = d_spacing

    def initialize_fitting_input_dictionary(self):
        """
        This method uses the first row of the history to figure out which parameter need to be initialized
        """
        nbr_column = self.parent.ui.march_dollase_user_input_table.columnCount()
        list_name_of_parameters = []
        for _col in np.arange(nbr_column):
            _item = self.parent.ui.march_dollase_user_input_table.horizontalHeaderItem(_col).text()
            list_name_of_parameters.append(_item)

        march_dollase_fitting_history_table = self.parent.march_dollase_fitting_history_table
        [d_spacing_flag, sigma_flag, alpha_flag, a1_flag, a2_flag, a5_flag, a6_flag] = \
            march_dollase_fitting_history_table[0]

        d_spacing = self.get_d_spacing()
        sigma = self.get_sigma()
        alpha = self.get_alpha()

        self.parent.march_dollase_fitting_initial_parameters['d_spacing'] = d_spacing
        fitting_input_dictionary = self.parent.fitting_input_dictionary

        for _row in fitting_input_dictionary['rois'].keys():

            if not d_spacing_flag:
                fitting_input_dictionary['rois'][_row]['fitting']['march_dollase']['d_spacing'] = d_spacing

            if not sigma_flag:
                fitting_input_dictionary['rois'][_row]['fitting']['march_dollase']['sigma'] = sigma

            if not alpha_flag:
                fitting_input_dictionary['rois'][_row]['fitting']['march_dollase']['alpha'] = alpha

            # {'left_part': {'lambda_x_axis': [],
            #                'y_axis': [],
            #               },
            #  'right_part': {'lambda_x_axis': [],
            #                 'y_axis': [],
            #                },
            #  'center_part': {'lambda_x_axis': [],
            #                  'y_axis': [],
            #                  }
            #  }
            self.left_center_right_axis = self.isolate_left_center_right_axis(row=_row)
            if self.is_advanced_mode():

                a2 = self.get_a2(advanced_mode=self.is_advanced_mode())
                fitting_input_dictionary['rois'][_row]['fitting']['march_dollase']['a2'] = a2

                a5 = self.get_a5()
                fitting_input_dictionary['rois'][_row]['fitting']['march_dollase']['a5'] = a5

                a6 = self.get_a6()
                fitting_input_dictionary['rois'][_row]['fitting']['march_dollase']['a6'] = a6

                a1 = self.get_a1(advanced_mode=self.is_advanced_mode())
                fitting_input_dictionary['rois'][_row]['fitting']['march_dollase']['a1'] = a1

            else:

                a1 = self.get_a1(advanced_mode=self.is_advanced_mode())
                fitting_input_dictionary['rois'][_row]['fitting']['march_dollase']['a1'] = a1

                a2 = self.get_a2(advanced_mode=self.is_advanced_mode())
                fitting_input_dictionary['rois'][_row]['fitting']['march_dollase']['a2'] = a2

    def isolate_left_center_right_axis(self, row=-1):
        bragg_edge_range = self.parent.fitting_input_dictionary['bragg_edge_range']
        [global_left_index, global_right_index] = [np.int(bragg_edge_range[0]),
                                                   np.int(bragg_edge_range[1])]
        # get full x-axis (lambda)
        full_lambda_x_axis = self.parent.fitting_input_dictionary['xaxis']['lambda'][0]
        lambda_x_axis = full_lambda_x_axis[global_left_index: global_right_index]

        # get full y_axis (average transmission)
        full_y_axis = self.parent.fitting_input_dictionary['rois'][row]['profile']
        y_axis = full_y_axis[global_left_index: global_right_index]

        [left_index, right_index] = self.parent.march_dollase_fitting_range_selected

        return {'left_part'  : {'lambda_x_axis': lambda_x_axis[0: left_index],
                                'y_axis'       : y_axis[0: left_index]},
                'center_part': {'lambda_x_axis': lambda_x_axis[left_index: right_index],
                                'y_axis'       : y_axis[left_index: right_index]},
                'right_part' : {'lambda_x_axis': lambda_x_axis[right_index:],
                                'y_axis'       : y_axis[right_index:]}}

    def get_a1(self, advanced_mode=True):
        if advanced_mode:
            intercept = self.a2_intercept
            a2 = self.a2
            a6 = self.a6
            return intercept + a2 * a6
        else:
            all_fitting_axis_dictionary = self.left_center_right_axis
            y_axis = all_fitting_axis_dictionary['left_part']['y_axis']
            a1 = np.mean(y_axis)
            self.a1 = a1
            return a1

    def get_a2(self, advanced_mode=True):
        all_fitting_axis_dictionary = self.left_center_right_axis
        if advanced_mode:
            x_axis = all_fitting_axis_dictionary['left_part']['lambda_x_axis']
            y_axis = all_fitting_axis_dictionary['left_part']['y_axis']

            [slope, interception] = np.polyfit(x_axis, y_axis, 1)

            self.a2 = slope  # saving it to calculate a6
            self.a2_intercept = interception  # saving it to calculate a1
            return slope

        else:
            _mean_left_part_side = self.a1
            y_axis = all_fitting_axis_dictionary['right_part']['y_axis']
            _mean_right_part_side = np.mean(y_axis)
            a2 = np.abs(_mean_right_part_side - _mean_left_part_side)
            return a2

    def get_a5(self):
        all_fitting_axis_dictionary = self.left_center_right_axis

        x_axis = all_fitting_axis_dictionary['right_part']['lambda_x_axis']
        y_axis = all_fitting_axis_dictionary['right_part']['y_axis']

        [slope, _] = np.polyfit(x_axis, y_axis)
        self.a5 = slope
        return slope

    def get_a6(self):
        all_fitting_axis_dictionary = self.left_center_right_axis

        x_axis = all_fitting_axis_dictionary['right_part']['lambda_x_axis']
        y_axis = all_fitting_axis_dictionary['right_part']['y_axis']

        a6 = x_axis - (2. * y_axis) / (self.a5 - self.a2)
        self.a6 = a6
        return a6

    def get_sigma(self):
        return self.parent.march_dollase_fitting_initial_parameters['sigma']

    def get_alpha(self):
        return self.parent.march_dollase_fitting_initial_parameters['alpha']

    def get_d_spacing(self):
        """
        calculates the d_spacing using the lambda range selection and using the central lambda
        2* d_spacing = lambda
        """
        logging.info("> march_dollase_fitting_job_handler | get_d_spacing")
        lambda_axis = self.parent.fitting_input_dictionary['xaxis']['lambda']
        logging.info(f"-> lambda_axis: {lambda_axis}")

        bragg_edge_range = self.parent.march_dollase_fitting_range_selected
        logging.info(f"-> bragg_edge_range: {bragg_edge_range}")

        from_lambda = np.float(lambda_axis[0][np.int(bragg_edge_range[0])])
        to_lambda = np.float(lambda_axis[0][np.int(bragg_edge_range[1])])

        average_lambda = np.mean([from_lambda, to_lambda])
        d_spacing = average_lambda / 2.

        return d_spacing

    def prepare(self):
        self.initialize_fitting_input_dictionary()
        fitting_input_dictionary = self.parent.fitting_input_dictionary
        march_dollase_fitting_history_table = self.parent.march_dollase_fitting_history_table

        _is_advanced_mode = self.is_advanced_mode()
        if _is_advanced_mode:
            gmodel = Model(march_dollase_advanced_fit, missing='drop')
        else:
            # gmodel = Model(march_dollase_basic_fit, missing='drop')
            gmodel = Model(march_dollase_basic_fit, nan_policy='propagate')

        march_dollase_fitting_history_table = self.parent.march_dollase_fitting_history_table
        nbr_row_in_fitting_scenario = len(march_dollase_fitting_history_table)

        self.parent.ui.eventProgress.setValue(0)
        nbr_roi_row = len(fitting_input_dictionary['rois'].keys())
        self.parent.ui.eventProgress.setMaximum(nbr_roi_row)
        self.parent.ui.eventProgress.setVisible(True)

        def set_params(params_object, name_of_parameter, dict_entry, parameter_flag):
            params_object.add(name_of_parameter,
                              value=np.float(dict_entry[name_of_parameter]),
                              vary=parameter_flag)

        def record_result_into_dict(entry_dict, result_object, name_of_parameter, parameter_flag):
            if parameter_flag:
                print(f"-> name_of_parameter: {name_of_parameter}")
                [value, error] = result_object.get_value_err(tag=name_of_parameter)
                entry_dict[name_of_parameter] = value
                entry_dict[name_of_parameter + "_error"] = error
                print(f"   - value: {value}")
                print(f"   - error: {error}")

        for _roi_row in np.arange(nbr_roi_row):
            _entry = fitting_input_dictionary['rois'][_roi_row]['fitting']['march_dollase']

            o_get = Get(parent=self.parent)
            xaxis = o_get.x_axis_data(x_axis_selected='lambda')
            yaxis = o_get.y_axis_data_of_selected_row(_roi_row)

            for _history_row, _row_entry in enumerate(march_dollase_fitting_history_table):

                [d_spacing_flag, sigma_flag, alpha_flag,
                 a1_flag, a2_flag, a5_flag, a6_flag] = _row_entry

                if _is_advanced_mode:
                    a5_flag = _entry['a5']
                    a6_flag = _entry['a6']

                params = gmodel.make_params()

                set_params(params, 'd_spacing', _entry, d_spacing_flag)
                set_params(params, 'sigma', _entry, sigma_flag)
                set_params(params, 'alpha', _entry, alpha_flag)
                set_params(params, 'a1', _entry, a1_flag)
                set_params(params, 'a2', _entry, a2_flag)

                if _is_advanced_mode:
                    set_params(params, 'a5', _entry, a5_flag)
                    set_params(params, 'a6', _entry, a6_flag)

                print("Parameters pre-initialized:")
                if not d_spacing_flag:
                    print(f"- d_spacing: {_entry['d_spacing']}")
                if not sigma_flag:
                    print(f"- sigma: {_entry['sigma']}")
                if not alpha_flag:
                    print(f"- alpha: {_entry['alpha']}")
                if not a1_flag:
                    print(f"- a1: {_entry['a1']}")
                if not a2_flag:
                    print(f"- a2: {_entry['a2']}")

                # try:
                result = gmodel.fit(yaxis, params, t=xaxis)
                # except ValueError:
                # 	print(f"we are having an error row:{_roi_row}")

                print(f"in _history_row: {_history_row}")

                o_result = ResultValueError(result=result)
                record_result_into_dict(_entry, o_result, 'd_spacing', d_spacing_flag)
                record_result_into_dict(_entry, o_result, 'sigma', sigma_flag)
                record_result_into_dict(_entry, o_result, 'alpha', alpha_flag)
                record_result_into_dict(_entry, o_result, 'a1', a1_flag)
                record_result_into_dict(_entry, o_result, 'a2', a2_flag)

                if _is_advanced_mode:
                    record_result_into_dict(_entry, o_result, 'a5', a5_flag)
                    record_result_into_dict(_entry, o_result, 'a6', a6_flag)

            break  # for debugging only (stop only after first row)

            self.parent.ui.eventProgress.setValue(_roi_row + 1)
            QApplication.processEvents()

        self.parent.ui.eventProgress.setVisible(False)
        self.parent.fitting_procedure_started['march-dollase'] = True


class ResultValueError(object):

    def __init__(self, result=None):
        self.result = result

    def get_value_err(self, tag=''):
        value = self.result.params[tag].value
        error = self.result.params[tag].stderr
        return [value, error]
