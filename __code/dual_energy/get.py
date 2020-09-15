import numpy as np

from __code.bragg_edge.get import Get as BraggEdgeGet
from __code.bragg_edge.bragg_edge_peak_fitting_gui_utility import GuiUtility


class Get(BraggEdgeGet):

	def __init__(self, parent=None):
		self.parent = parent

		self.x_axis_choice_ui = {'index': self.parent.ui.selection_index_radiobutton,
		                         'tof'   : self.parent.ui.selection_tof_radiobutton,
		                         'lambda': self.parent.ui.selection_lambda_radiobutton}

	def x_axis(self):
		list_ui = self.x_axis_choice_ui
		if list_ui['index'].isChecked():
			return self.specified_x_axis(xaxis='index')
		elif list_ui['tof'].isChecked():
			return self.specified_x_axis(xaxis='tof')
		else:
			return self.specified_x_axis(xaxis='lambda')

	def selection_roi_dimension(self):
		roi_id = self.parent.roi_id

		if roi_id:
			region = roi_id.getArraySlice(self.parent.live_image,
			                              self.parent.ui.image_view.imageItem)
			x0 = region[0][0].start
			x1 = region[0][0].stop
			y0 = region[0][1].start
			y1 = region[0][1].stop
			width = np.int(x1 - x0)
			height = np.int(y1 - y0)

		else:
			x0, y0, x1, y1, width, height = self.parent.roi_dimension_from_config_file

		return [x0, y0, x1, y1, width, height]
