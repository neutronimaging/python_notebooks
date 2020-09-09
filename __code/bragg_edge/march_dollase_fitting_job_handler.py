from lmfit import Model
import numpy as np
from qtpy.QtWidgets import QApplication

from __code.bragg_edge.fitting_functions import march_dollase_basic_fit, march_dollase_advanced_fit


class MarchDollaseFittingJobHandler:

	def __init__(self, parent=None):
		self.parent = parent

	def is_advanced_mode(self):
		if self.parent.ui.march_dollase_advanced_mode_checkBox.isChecked():
			return True
		else:
			return False

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

		d_spacing = self.get_initial_parameter_value(name_of_parameter='d_spacing')
		sigma = self.get_initial_parameter_value(name_of_parameter='sigma')
		alpha = self.get_initial_parameter_value(name_of_parameter='alpha')

		self.parent.march_dollase_fitting_initial_parameters['d-spacing'] = d_spacing
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
			#  'inflection_point': {'x': np.NaN,
			#                       'y': np.NaN,
			#                      },
			# }
			inflection_dict = self.isolate_left_and_right_part_of_inflection_point(row=_row)

			if self.is_advanced_mode():

				if not a2_flag:
					a2 = self.get_a2(row=_row,
					                 advanced_mode=self.is_advanced_mode(),
					                 inflection_dict=inflection_dict)
					fitting_input_dictionary['rois'][_row]['fitting']['march_dollase']['a2'] = a2







		import pprint
		pprint.pprint(fitting_input_dictionary['rois'][0]['fitting']['march_dollase'])

	def isolate_left_and_right_part_of_inflection_point(self, row=-1):
		bragg_edge_range = self.parent.fitting_input_dictionary['bragg_edge_range']
		left_index = np.int(bragg_edge_range[0])
		right_index = np.int(bragg_edge_range[1])

		# get full x_axis (lambda)
		full_lambda_x_axis = self.parent.fitting_input_dictionary['xaxis']['lambda'][0]
		lambda_x_axis = full_lambda_x_axis[left_index: right_index]

		# get full y_axis (average transmission)
		full_y_axis = self.parent.fitting_input_dictionary['rois'][row]['profile']
		y_axis = full_y_axis[left_index: right_index]

		# for now inflection is only calculated by using center of selection
		# FIXME

		inflection_point_index = np.int(len(lambda_x_axis) / 2.)
		return {'left_part': {'lambda_x_axis': lambda_x_axis[0: inflection_point_index],
		                      'y_axis': y_axis[0: inflection_point_index]},
		        'right_part': {'lambda_x_axis': lambda_x_axis[inflection_point_index: ],
		                       'y_axis': y_axis[inflection_point_index: ]},
		        'inflection_point': {'y': y_axis[inflection_point_index],
		                             'lambda_x': lambda_x_axis[inflection_point_index]}}

	def get_a2(self, row=-1, advanced_mode=True, inflection_dict=None):
		if advanced_mode:
			x_axis = inflection_dict['left_part']['lambda_x_axis']
			y_axis = inflection_dict['left_part']['y_axis']

			nbr_data = len(x_axis)
			return np.NaN





	def get_initial_parameter_value(self, name_of_parameter=None, row=-1):
		if name_of_parameter == 'd_spacing':
			return self.get_d_spacing()
		if name_of_parameter == 'sigma':
			return self.parent.march_dollase_fitting_initial_parameters['sigma']
		if name_of_parameter == 'alpha':
			return self.parent.march_dollase_fitting_initial_parameters['alpha']
		if name_of_parameter == 'a1':
			return self.calculate_a1(row=row)
		if name_of_parameter == 'a2':
			return -1
		if name_of_parameter == 'a5':
			return -1
		if name_of_parameter == 'a6':
			return -1
		return None

	def calculate_a1(self, row=-1):
		if self.is_advanced_mode():
			pass
		else:
			pass

	def get_d_spacing(self):
		"""
	    calculates the d-spacing using the lambda range selection and using the central lambda
	    2* d_spacing = lambda
		"""
		lambda_axis = self.parent.fitting_input_dictionary['xaxis']['lambda']
		bragg_edge_range = self.parent.fitting_input_dictionary['bragg_edge_range']

		from_lambda = np.float(lambda_axis[0][np.int(bragg_edge_range[0])])
		to_lambda = np.float(lambda_axis[0][np.int(bragg_edge_range[1])])

		average_lambda = np.mean([from_lambda, to_lambda])
		d_spacing = average_lambda / 2.

		return d_spacing

	def prepare(self):

		self.initialize_fitting_input_dictionary()
		# fitting_input_dictionary = self.parent.fitting_input_dictionary

		_is_advanced_mode = self.is_advanced_mode()
		if _is_advanced_mode:
			gmodel = Model(march_dollase_advanced_fit, missing='drop')
		else:
			gmodel = Model(march_dollase_basic_fit, missing='drop')

		march_dollase_fitting_history_table = self.parent.march_dollase_fitting_history_table
		nbr_row_in_fitting_scenario = len(march_dollase_fitting_history_table)

		self.parent.ui.eventProgress.setValue(0)
		self.parent.ui.eventProgress.setMaximum(nbr_row_in_fitting_scenario)
		self.parent.ui.eventProgress.setVisible(True)

		for _row, _row_entry in enumerate(march_dollase_fitting_history_table):





			self.parent.ui.eventProgress.setValue(_row + 1)
			QApplication.processEvents()

		self.parent.ui.eventProgress.setVisible(False)
		self.parent.fitting_procedure_started['march-dollase'] = True
