import numpy as np
from lmfit import Model, Parameter
import copy
from qtpy import QtGui
import logging

# from ibeatles.utilities.status_message_config import StatusMessageStatus, show_status_message
# import ibeatles.utilities.error as fitting_error
# from ibeatles.fitting.kropff.get import Get
# from ibeatles.fitting import KropffTabSelected
# from ibeatles.utilities.array_utilities import find_nearest_index
# from ibeatles.fitting.kropff.checking_fitting_conditions import CheckingFittingConditions
# from ibeatles.fitting.kropff import ERROR_TOLERANCE

from __code.timepix3_histo_hdf5_mcp_detector.fitting_functions import kropff_high_lambda, kropff_low_lambda, \
    kropff_bragg_peak_tof
import __code.timepix3_histo_hdf5_mcp_detector.error as fitting_error
from __code.timepix3_histo_hdf5_mcp_detector import FittingRegions


class FitRegions:

    def __init__(self, a0=None, b0=None,
                 ahkl=None, bhkl=None,
                 lambdahkl=None, tau=None, sigma=None,
                 x_axis_to_fit=None, y_axis_to_fit=None,
                 left_peak_index=0,
                 right_peak_index=0,
                 left_edge_index=0,
                 right_edge_index=0):
        self.a0 = a0
        self.b0 = b0
        self.ahkl = ahkl
        self.bhkl = bhkl
        self.lambdahkl = lambdahkl
        self.tau = tau
        self.sigma = sigma
        self.left_peak_index = left_peak_index
        self.right_peak_index = right_peak_index
        self.left_edge_index = left_edge_index
        self.right_edge_index = right_edge_index

        self.fit_dict = {'a0': {'value': None,
                                'error': None},
                         'b0': {'value': None,
                                'error': None},
                         'ahkl': {'value': None,
                                  'error': None},
                         'bhkl': {'value': None,
                                  'error': None},
                         'lambdahkl': {'value': None,
                                       'error': None},
                         'tau': {'value': None,
                                 'error': None},
                         'sigma': {'value': None,
                                   'error': None},
                         FittingRegions.high_lambda: None,
                         FittingRegions.low_lambda: None,
                         FittingRegions.bragg_peak: None,
                         }

        self.x_axis_to_fit = x_axis_to_fit
        self.y_axis_to_fit = y_axis_to_fit

    #     self.parent = parent
    #     self.grand_parent = grand_parent
    #     self.o_get = Get(parent=parent)
    #     self.table_dictionary = self.grand_parent.kropff_table_dictionary

    def all_regions(self):
        type_error = ""

        # o_event = KropffBraggPeakThresholdCalculator(parent=self.parent,
        #                                              grand_parent=self.grand_parent)
        # o_event.save_all_profiles()

        # o_display = Display(parent=self.parent,
        #                     grand_parent=self.grand_parent)
        # o_display.display_bragg_peak_threshold()

        try:
            self.high_lambda()
            self.low_lambda()
            self.bragg_peak()
        except fitting_error.HighLambdaFittingError as err:
            type_error = err
        except fitting_error.LowLambdaFittingError as err:
            type_error = err
        except fitting_error.BraggPeakFittingError as err:
            type_error = err

    # @staticmethod
    # def error_outside_of_tolerance(list_error):
    #     for _error in list_error:
    #         if not _error:
    #             return True
    #
    #         if _error > ERROR_TOLERANCE:
    #             return True
    #     return False

    def high_lambda(self):
        logging.info(f"fitting high lambda:")
        gmodel = Model(kropff_high_lambda, missing='drop', independent_vars=['lda'])

        a0 = self.a0
        b0 = self.b0

        right_edge_index = self.right_edge_index
        right_peak_index = self.right_peak_index

        xaxis = copy.deepcopy(self.x_axis_to_fit)[right_edge_index: right_peak_index]
        yaxis = copy.deepcopy(self.y_axis_to_fit)[right_edge_index: right_peak_index]
        yaxis = -np.log(yaxis)

        logging.info(f"{xaxis =}")

        try:
            _result = gmodel.fit(yaxis, lda=xaxis, a0=a0, b0=b0)
        except ValueError:
            raise ValueError("high lambda fitting failed!")
        except TypeError:
            raise TypeError("high lambda fitting failed!")

        a0_value = _result.params['a0'].value
        a0_error = _result.params['a0'].stderr
        b0_value = _result.params['b0'].value
        b0_error = _result.params['b0'].stderr

        logging.info(f"\t{a0_value =}")
        logging.info(f"\t{a0_error =}")
        logging.info(f"\t{b0_value =}")
        logging.info(f"\t{b0_error =}")

        yaxis_fitted = kropff_high_lambda(xaxis, a0_value, b0_value)

        self.fit_dict['a0'] = {'value': a0_value,
                               'error': a0_error}
        self.fit_dict['b0'] = {'value': b0_value,
                               'error': b0_error}
        self.fit_dict[FittingRegions.high_lambda] = {'xaxis': xaxis,
                                                     'yaxis': yaxis_fitted}

    def low_lambda(self):
        logging.info(f"fitting low lambda:")
        gmodel = Model(kropff_low_lambda, missing='drop', independent_vars=['lda'])

        ahkl = self.ahkl
        bhkl = self.bhkl

        left_edge_index = self.left_edge_index
        left_peak_index = self.left_peak_index

        xaxis = copy.deepcopy(self.x_axis_to_fit)[left_peak_index: left_edge_index]
        yaxis = copy.deepcopy(self.y_axis_to_fit)[left_peak_index: left_edge_index]
        yaxis = -np.log(yaxis)

        logging.info(f"{xaxis =}")

        try:
            _result = gmodel.fit(yaxis,
                                 lda=xaxis,
                                 a0=Parameter('a0', value=self.fit_dict['a0']['value'], vary=False),
                                 b0=Parameter('b0', value=self.fit_dict['b0']['value'], vary=False),
                                 ahkl=ahkl,
                                 bhkl=bhkl)
        except ValueError:
            raise ValueError("low lambda fitting failed!")

        ahkl_value = _result.params['ahkl'].value
        ahkl_error = _result.params['ahkl'].stderr
        bhkl_value = _result.params['bhkl'].value
        bhkl_error = _result.params['bhkl'].stderr

        logging.info(f"\t{ahkl_value =}")
        logging.info(f"\t{ahkl_error =}")
        logging.info(f"\t{bhkl_value =}")
        logging.info(f"\t{bhkl_error =}")

        yaxis_fitted = kropff_low_lambda(xaxis,
                                         self.fit_dict['a0']['value'],
                                         self.fit_dict['b0']['value'],
                                         ahkl_value, bhkl_value)

        self.fit_dict['ahkl'] = {'value': ahkl_value,
                                 'error': ahkl_error}
        self.fit_dict['bhkl'] = {'value': bhkl_value,
                                 'error': bhkl_error}
        self.fit_dict[FittingRegions.low_lambda] = {'xaxis': xaxis,
                                                    'yaxis': yaxis_fitted}

    def bragg_peak(self):
        self.bragg_peak_fix_lambda()

        # if self.parent.kropff_lambda_settings['state'] == 'fix':
        #     self.bragg_peak_fix_lambda()
        # else:
        #     self.bragg_peak_range_lambda()

    # def bragg_peak_range_lambda(self):
    #     """we need to try to fit until the fit worked or we exhausted the full range defined"""
    #     logging.info("Fitting bragg peak with a range of lambda_hkl:")
    #     gmodel = Model(kropff_bragg_peak_tof, nan_policy='propagate', independent_vars=['lda'])
    #
    #     # lambda_hkl = self.o_get.lambda_hkl()
    #     tau = self.o_get.tau()
    #     sigma = self.o_get.sigma()
    #
    #     table_dictionary = self.table_dictionary
    #     fit_conditions = self.parent.kropff_bragg_peak_good_fit_conditions
    #     o_checking = CheckingFittingConditions(fit_conditions=fit_conditions)
    #
    #     lambda_hkl_range = np.arange(self.parent.kropff_lambda_settings['range'][0],
    #                                  self.parent.kropff_lambda_settings['range'][1],
    #                                  self.parent.kropff_lambda_settings['range'][2])
    #     logging.info(f"-> lambda_hkl_range: {lambda_hkl_range}")
    #
    #     self.parent.eventProgress.setMaximum(len(table_dictionary.keys()))
    #     self.parent.eventProgress.setValue(0)
    #     self.parent.eventProgress.setVisible(True)
    #     QtGui.QGuiApplication.processEvents()
    #
    #     for _index, _key in enumerate(table_dictionary.keys()):
    #
    #         # if row is locked, continue
    #         if table_dictionary[_key]['lock']:
    #             self.parent.eventProgress.setValue(_index)
    #             QtGui.QGuiApplication.processEvents()
    #             continue
    #
    #         if table_dictionary[_key]['rejected']:
    #             self.parent.eventProgress.setValue(_index)
    #             QtGui.QGuiApplication.processEvents()
    #             continue
    #
    #         table_entry = table_dictionary[_key]
    #
    #         xaxis = copy.deepcopy(table_entry['xaxis'])
    #
    #         a0 = table_entry['a0']['val']
    #         b0 = table_entry['b0']['val']
    #         ahkl = table_entry['ahkl']['val']
    #         bhkl = table_entry['bhkl']['val']
    #
    #         yaxis = copy.deepcopy(table_entry['yaxis'])
    #         yaxis = -np.log(yaxis)
    #
    #         for _lambda_hkl in lambda_hkl_range:
    #
    #             _result = gmodel.fit(yaxis,
    #                                  lda=xaxis,
    #                                  a0=Parameter('a0', value=a0, vary=False),
    #                                  b0=Parameter('b0', value=b0, vary=False),
    #                                  ahkl=Parameter('ahkl', value=ahkl, vary=False),
    #                                  bhkl=Parameter('bhkl', value=bhkl, vary=False),
    #                                  ldahkl=_lambda_hkl,
    #                                  sigma=sigma,
    #                                  tau=tau)
    #
    #             ldahkl_error = _result.params['ldahkl'].stderr
    #             sigma_error = _result.params['sigma'].stderr
    #             tau_error = _result.params['tau'].stderr
    #             ldahkl_value = _result.params['ldahkl'].value
    #             sigma_value = _result.params['sigma'].value
    #             tau_value = _result.params['tau'].value
    #             yaxis_fitted = kropff_bragg_peak_tof(xaxis, a0, b0, ahkl, bhkl, ldahkl_value, sigma_value, tau_value)
    #
    #             if o_checking.is_fitting_ok(l_hkl_error=ldahkl_error,
    #                                         t_error=tau_error,
    #                                         sigma_error=sigma_error):
    #                 break
    #
    #             self.parent.eventProgress.setValue(_index)
    #             QtGui.QGuiApplication.processEvents()
    #
    #         table_dictionary[_key]['lambda_hkl'] = {'val': ldahkl_value,
    #                                                 'err': ldahkl_error}
    #         table_dictionary[_key]['tau'] = {'val': tau_value,
    #                                          'err': tau_error}
    #         table_dictionary[_key]['sigma'] = {'val': sigma_value,
    #                                            'err': sigma_error}
    #         table_dictionary[_key]['fitted'][KropffTabSelected.bragg_peak] = {'xaxis': xaxis,
    #                                                                           'yaxis': yaxis_fitted}
    #         self.parent.eventProgress.setVisible(False)

    def bragg_peak_fix_lambda(self):
        logging.info("Fitting bragg peak with a fixed initial lambda_hkl:")

        gmodel = Model(kropff_bragg_peak_tof, nan_policy='propagate', independent_vars=['lda'])

        lambda_hkl = self.lambdahkl
        tau = self.tau
        sigma = self.sigma

        left_peak_index = self.left_edge_index
        right_peak_index = self.right_edge_index

        xaxis = copy.deepcopy(self.x_axis_to_fit)[left_peak_index: right_peak_index+1]
        yaxis = copy.deepcopy(self.y_axis_to_fit)[left_peak_index: right_peak_index+1]
        yaxis = -np.log(yaxis)

        logging.info(f"{xaxis =}")

        a0 = self.fit_dict['a0']['value']
        b0 = self.fit_dict['b0']['value']
        ahkl = self.fit_dict['ahkl']['value']
        bhkl = self.fit_dict['bhkl']['value']

        _result = gmodel.fit(yaxis,
                             lda=xaxis,
                             a0=Parameter('a0', value=a0, vary=False),
                             b0=Parameter('b0', value=b0, vary=False),
                             ahkl=Parameter('ahkl', value=ahkl, vary=False),
                             bhkl=Parameter('bhkl', value=bhkl, vary=False),
                             ldahkl=lambda_hkl,
                             sigma=sigma,
                             tau=tau)

        ldahkl_value = _result.params['ldahkl'].value
        ldahkl_error = _result.params['ldahkl'].stderr
        sigma_value = _result.params['sigma'].value
        sigma_error = _result.params['sigma'].stderr
        tau_value = _result.params['tau'].value
        tau_error = _result.params['tau'].stderr

        logging.info(f"\t{ldahkl_value =}")
        logging.info(f"\t{ldahkl_error =}")
        logging.info(f"\t{sigma_value =}")
        logging.info(f"\t{sigma_error =}")
        logging.info(f"\t{tau_value =}")
        logging.info(f"\t{tau_error =}")

        yaxis_fitted = kropff_bragg_peak_tof(xaxis, a0, b0, ahkl, bhkl, ldahkl_value, sigma_value, tau_value)

        self.fit_dict['lambdahkl'] = {'value': ldahkl_value,
                                      'error': ldahkl_error}
        self.fit_dict['sigma'] = {'value': sigma_value,
                                  'error': sigma_error}
        self.fit_dict['tau'] = {'value': tau_value,
                                'error': tau_error}
        self.fit_dict[FittingRegions.bragg_peak] = {'xaxis': xaxis,
                                                    'yaxis': yaxis_fitted}
