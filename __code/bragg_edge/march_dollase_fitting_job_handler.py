from lmfit import Model
import numpy as np
from qtpy.QtWidgets import QApplication

from __code.bragg_edge.fitting_functions import march_dollase_basic_fit, march_dollase_advanced_fit


class MarchDollaseFittingJobHandler:

	def __init__(self, parent=None):
		self.parent = parent

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
		first_row_of_history = march_dollase_fitting_history_table[0]

		fitting_input_dictionary = self.parent.fitting_input_dictionary
		for _row in fitting_input_dictionary['rois'].keys():

			for _name_of_parameter, _parameter_state in zip(list_name_of_parameters, first_row_of_history):

				if _parameter_state is False:  # we need to get an initial value to this parameter
					_value = self.get_initial_parameter_value(name_of_parameter=_name_of_parameter)
				else:
					_value = np.NaN

				fitting_input_dictionary['rois'][_row]['march_dollase'][_name_of_parameter] = _value

	def get_initial_parameter_value(self, name_of_parameter):
		return 10

	def prepare(self):

		print(f"before ->")
		print(f"self.parent.fitting_input_dictionary['rois'][0]['marche_dollase']: "
		      f"{self.parent.fitting_input_dictionary['rois'][0]['marche_dollase']}")
		self.initialize_fitting_input_dictionary()
		print(f"after ->")
		print(f"self.parent.fitting_input_dictionary['rois'][0]['marche_dollase']: "
		      f"{self.parent.fitting_input_dictionary['rois'][0]['marche_dollase']}")
		# fitting_input_dictionary = self.parent.fitting_input_dictionary

		_is_advanced_mode = self.parent.ui.march_dollase_advanced_mode_checkBox.isChecked()
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
			pass














			self.parent.ui.eventProgress.setValue(_row + 1)
			QApplication.processEvents()

		self.parent.ui.eventProgress.setVisible(False)
