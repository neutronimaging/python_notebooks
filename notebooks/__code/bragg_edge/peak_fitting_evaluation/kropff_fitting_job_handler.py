from lmfit import Model, Parameter
from copy import deepcopy
import numpy as np

from __code.bragg_edge.fitting_functions import kropff_high_lambda, kropff_low_lambda, kropff_bragg_peak_tof
from __code.bragg_edge.bragg_edge_peak_fitting_gui_utility import GuiUtility


class KropffFittingJobHandler:
    """https://lmfit.github.io/lmfit-py/examples/example_Model_interface.html"""

    def __init__(self, parent=None):
        self.parent = parent

        self.xaxis_to_fit = None
        self.list_yaxis_to_fit = None

    def prepare(self, kropff_tooldbox='high'):
        """
        :param kropff_tooldbox: 'high', 'low', 'bragg_peak'
        """
        if kropff_tooldbox == 'bragg_peak':
            fitting_range = [self.parent.kropff_fitting_range['low'][0],
                             self.parent.kropff_fitting_range['high'][1]]
        else:
            fitting_range = self.parent.kropff_fitting_range[kropff_tooldbox]
        # fitting_range = self.parent.kropff_fitting_range[kropff_tooldbox]

        xaxis = self.parent.fitting_input_dictionary['xaxis']['lambda'][0]
        [left_xaxis_index, right_xaxis_index] = self.parent.bragg_edge_range
        full_fitting_xaxis = xaxis[left_xaxis_index: right_xaxis_index]
        # self.xaxis_to_fit = full_fitting_xaxis[fitting_range[0]: fitting_range[1] + 1] * 1e-6  # to convert in s
        self.xaxis_to_fit = full_fitting_xaxis[fitting_range[0]: fitting_range[1] + 1]

        list_yaxis_to_fit = []
        for _key in self.parent.fitting_input_dictionary['rois'].keys():
            _yaxis = self.parent.fitting_input_dictionary['rois'][_key]['profile']
            full_fitting_yaxis = _yaxis[left_xaxis_index: right_xaxis_index]
            list_yaxis_to_fit.append(full_fitting_yaxis[fitting_range[0]: fitting_range[1] + 1])
        self.list_yaxis_to_fit = list_yaxis_to_fit

    def run_kropff_high_lambda(self, update_table_ui=False):
        gmodel = Model(kropff_high_lambda, missing='drop', independent_vars=['lda'])

        lda = self.xaxis_to_fit
        o_gui = GuiUtility(parent=self.parent)

        a0_init = float(str(self.parent.kropff_high_lda_a0_init.text()))
        b0_init = float(str(self.parent.kropff_high_lda_b0_init.text()))
        for _index, yaxis in enumerate(self.list_yaxis_to_fit):
            yaxis = -np.log(yaxis)
            _result = gmodel.fit(yaxis, lda=lda, a0=a0_init, b0=b0_init)
            a0 = _result.params['a0'].value
            a0_error = _result.params['a0'].stderr
            b0 = _result.params['b0'].value
            b0_error = _result.params['b0'].stderr

            yaxis_fitted = kropff_high_lambda(self.xaxis_to_fit, a0, b0)

            result_dict = {'a0'          : a0,
                           'b0'          : b0,
                           'a0_error'    : a0_error,
                           'b0_error'    : b0_error,
                           'xaxis_to_fit': lda,
                           'yaxis_fitted': yaxis_fitted}

            self.parent.fitting_input_dictionary['rois'][_index]['fitting']['kropff']['high'] = deepcopy(result_dict)

            if update_table_ui:
                o_gui.update_kropff_high_lambda_table_ui(row=_index,
                                                         a0=a0,
                                                         b0=b0,
                                                         a0_error=a0_error,
                                                         b0_error=b0_error)

    def run_kropff_low_lambda(self, update_table_ui=False):
        gmodel = Model(kropff_low_lambda, missing='drop', independent_vars=['lda'])

        lda = self.xaxis_to_fit
        o_gui = GuiUtility(parent=self.parent)

        ahkl_init = float(str(self.parent.kropff_low_lda_ahkl_init.text()))
        bhkl_init = float(str(self.parent.kropff_low_lda_bhkl_init.text()))

        for _row, yaxis in enumerate(self.list_yaxis_to_fit):

            _entry = self.parent.fitting_input_dictionary['rois'][_row]['fitting']['kropff']['high']
            a0 = float(_entry['a0'])
            b0 = float(_entry['b0'])

            yaxis = -np.log(yaxis)
            _result = gmodel.fit(yaxis, lda=lda,
                                 a0=Parameter('a0', value=a0, vary=False),
                                 b0=Parameter('b0', value=b0, vary=False),
                                 ahkl=ahkl_init,
                                 bhkl=bhkl_init)

            ahkl = _result.params['ahkl'].value
            ahkl_error = _result.params['ahkl'].stderr
            bhkl = _result.params['bhkl'].value
            bhkl_error = _result.params['bhkl'].stderr

            yaxis_fitted = kropff_low_lambda(lda,
                                             a0, b0, ahkl, bhkl)

            result_dict = {'ahkl'        : ahkl,
                           'bhkl'        : bhkl,
                           'ahkl_error'  : ahkl_error,
                           'bhkl_error'  : bhkl_error,
                           'xaxis_to_fit': lda,
                           'yaxis_fitted': yaxis_fitted}

            self.parent.fitting_input_dictionary['rois'][_row]['fitting']['kropff']['low'] = deepcopy(result_dict)

            if update_table_ui:
                o_gui.update_kropff_low_lambda_table_ui(row=_row,
                                                        ahkl=ahkl,
                                                        bhkl=bhkl,
                                                        ahkl_error=ahkl_error,
                                                        bhkl_error=bhkl_error)

    def run_bragg_peak(self, update_table_ui=False, list_row_to_fit=None):
        gmodel = Model(kropff_bragg_peak_tof, nan_policy='propagate', independent_vars=['lda'])

        lda = self.xaxis_to_fit
        o_gui = GuiUtility(parent=self.parent)

        ldahkl_init = float(str(self.parent.ui.kropff_bragg_peak_ldahkl_init.text()))
        tau_init = float(str(self.parent.kropff_bragg_peak_tau_init.text()))
        sigma_init = float(self.parent.kropff_bragg_peak_sigma_comboBox.currentText())

        for _row, yaxis in enumerate(self.list_yaxis_to_fit):

            if not list_row_to_fit is None:
                if _row not in list_row_to_fit:
                    continue

            _entry_high = self.parent.fitting_input_dictionary['rois'][_row]['fitting']['kropff']['high']
            a0 = float(_entry_high['a0'])
            b0 = float(_entry_high['b0'])

            _entry_low = self.parent.fitting_input_dictionary['rois'][_row]['fitting']['kropff']['low']
            ahkl = float(_entry_low['ahkl'])
            bhkl = float(_entry_low['bhkl'])

            yaxis = -np.log(yaxis)

            _result = gmodel.fit(yaxis,
                                 lda=lda,
                                 a0=Parameter('a0', value=a0, vary=False),
                                 b0=Parameter('b0', value=b0, vary=False),
                                 ahkl=Parameter('ahkl', value=ahkl, vary=False),
                                 bhkl=Parameter('bhkl', value=bhkl, vary=False),
                                 ldahkl=ldahkl_init,
                                 sigma=sigma_init,
                                 tau=tau_init)

            ldahkl = _result.params['ldahkl'].value
            ldahkl_error = _result.params['ldahkl'].stderr
            sigma = _result.params['sigma'].value
            sigma_error = _result.params['sigma'].stderr
            tau = _result.params['tau'].value
            tau_error = _result.params['tau'].stderr

            yaxis_fitted = kropff_bragg_peak_tof(self.xaxis_to_fit,
                                                 a0, b0, ahkl, bhkl,
                                                 ldahkl, sigma, tau)

            result_dict = {'ldahkl'      : ldahkl,
                           'ldahkl_error': ldahkl_error,
                           'sigma'       : sigma,
                           'sigma_error' : sigma_error,
                           'tau'         : tau,
                           'tau_error'   : tau_error,
                           'xaxis_to_fit': lda,
                           'yaxis_fitted': yaxis_fitted}

            self.parent.fitting_input_dictionary['rois'][_row]['fitting']['kropff']['bragg_peak'] = deepcopy(
                    result_dict)

            if update_table_ui:
                o_gui.update_kropff_bragg_edge_table_ui(row=_row,
                                                        ldahkl=ldahkl,
                                                        ldahkl_error=ldahkl_error,
                                                        tau=tau,
                                                        tau_error=tau_error,
                                                        sigma=sigma,
                                                        sigma_error=sigma_error)
