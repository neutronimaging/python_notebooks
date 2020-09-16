import numpy as np
import pyqtgraph as pg
from qtpy import QtGui
from collections import OrderedDict

from __code._utilities.array import check_size
from __code.dual_energy.get import Get
from __code.utilities import find_nearest_index


class SelectionTab:

	def __init__(self, parent=None):
		self.parent = parent

	def update_selection_profile_plot(self):
		o_get = Get(parent=self.parent)
		x_axis, x_axis_label = o_get.x_axis()
		self.parent.ui.profile.clear()

		# large selection region
		[x0, y0, x1, y1, _, _] = o_get.selection_roi_dimension()
		profile = o_get.profile_of_roi(x0, y0, x1, y1)
		x_axis, y_axis = check_size(x_axis=x_axis,
		                            y_axis=profile)
		self.parent.ui.profile.plot(x_axis, y_axis, pen=(self.parent.selection_roi_rgb[0],
		                                          self.parent.selection_roi_rgb[1],
		                                          self.parent.selection_roi_rgb[2]))

		self.parent.ui.profile.setLabel("bottom", x_axis_label)
		self.parent.ui.profile.setLabel("left", 'Mean transmission')

		# vertical line showing peak to fit
		profile_selection_range = [x_axis[self.parent.profile_selection_range[0]],
		                           x_axis[self.parent.profile_selection_range[1]]]

		self.parent.profile_selection_range_ui = pg.LinearRegionItem(values=profile_selection_range,
		                                                             orientation=None,
		                                                             brush=None,
		                                                             movable=True,
		                                                             bounds=None)
		self.parent.profile_selection_range_ui.sigRegionChanged.connect(self.parent.profile_selection_range_changed)
		self.parent.profile_selection_range_ui.setZValue(-10)
		self.parent.ui.profile.addItem(self.parent.profile_selection_range_ui)

		_pen = QtGui.QPen()
		_pen.setColor(self.parent.bin_line_settings['color'])
		_pen.setWidth(self.parent.bin_line_settings['width'])

		if self.parent.list_bin_ui:
			for _bin_ui in self.parent.list_bin_ui:
				self.parent.ui.profile.removeItem(_bin_ui)
			self.parent.list_bin_ui = []

		if self.parent.list_bin_positions:
			current_axis_name = o_get.x_axis_name_checked()
			for bin in self.parent.list_bin_positions[current_axis_name]:
				if current_axis_name == 'tof':
					bin *= 1e6
				_bin_ui = pg.InfiniteLine(bin,
				                          movable=False,
				                          pen=_pen)
				self.parent.ui.profile.addItem(_bin_ui)
				self.parent.list_bin_ui.append(bin)

	def update_bin_size_widgets(self):
		o_get = Get(parent=self.parent)
		x_axis_units = o_get.x_axis_units()
		current_axis_name = o_get.x_axis_name_checked()

		# update units
		self.parent.ui.selection_bin_size_units.setText(x_axis_units)

		bin_size_value = self.parent.bin_size_value[current_axis_name]
		if current_axis_name == 'tof':
			bin_size_value *= 1e6
		elif current_axis_name == 'lambda':
			bin_size_value = "{:2f}".format(bin_size_value)
		self.parent.ui.selection_bin_size_value.setText(str(bin_size_value))

	def calculate_bin_size_in_all_units(self):
		current_value = np.float(self.parent.ui.selection_bin_size_value.text())
		o_get = Get(parent=self.parent)
		current_axis_name = o_get.x_axis_name_checked()

		tof_array_s = self.parent.tof_array_s
		lambda_array = self.parent.lambda_array

		if current_axis_name == 'index':
			current_value = np.int(current_value)
			bin_index = current_value
			bin_tof = tof_array_s[current_value]
			bin_lambda = lambda_array[current_value]
		elif current_axis_name == 'tof':
			bin_index = find_nearest_index(array=tof_array_s,
			                               value=current_value*1e-6)
			bin_tof = current_value
			bin_lambda = lambda_array[bin_index]
		elif current_axis_name == 'lambda':
			bin_index = find_nearest_index(array=lambda_array,
			                               value=current_value)
			bin_tof = tof_array_s[bin_index]
			bin_lambda = current_value

		self.parent.bin_size_value = {'index': bin_index,
		                              'tof': bin_tof,
		                              'lambda': bin_lambda}

	def make_list_of_bins(self):
		[from_index, to_index] = self.parent.profile_selection_range

		list_bin = {'index': [],
		            'tof': [],
		            'lambda': []}

		# index scale
		index_bin_size = self.parent.bin_size_value['index']
		left_bin_value = from_index
		right_bin_value = from_index + index_bin_size
		list_bin['index'] = [left_bin_value]
		while right_bin_value <= to_index:
			list_bin['index'].append(right_bin_value)
			right_bin_value += index_bin_size

		# tof scale
		tof_array_s = self.parent.tof_array_s
		list_bin['tof'] = tof_array_s[list_bin['index']]

		# lambda scale
		lambda_array = self.parent.lambda_array
		list_bin['lambda'] = lambda_array[list_bin['index']]

		self.parent.list_bin_positions = list_bin

	def update_all_size_widgets_infos(self):

		if self.parent.ui.square_roi_radiobutton.isChecked():
			return

		roi_id = self.parent.roi_id
		region = roi_id.getArraySlice(self.parent.final_image,
		                              self.parent.ui.image_view.imageItem)
		x0 = region[0][0].start
		x1 = region[0][0].stop
		y0 = region[0][1].start
		y1 = region[0][1].stop

		new_width = x1 - x0 - 1
		new_height = y1 - y0 - 1

		# if new width and height is the same as before, just skip that step
		if self.parent.new_dimensions_within_error_range():
			return

		self.parent.ui.roi_width.setText(str(new_width))
		self.parent.ui.roi_height.setText(str(new_height))
		self.parent.ui.profile_of_bin_size_width.setText(str(new_width))
		self.parent.ui.profile_of_bin_size_height.setText(str(new_height))

		max_value = np.min([new_width, new_height])
		self.parent.ui.profile_of_bin_size_slider.setValue(max_value)
		self.parent.ui.profile_of_bin_size_slider.setMaximum(max_value)

	def get_shrinking_roi_dimension(self):
		coordinates = self.get_coordinates_of_new_inside_selection_box()
		return [coordinates['x0'],
		        coordinates['y0'],
		        coordinates['x0'] + coordinates['width'],
		        coordinates['y0'] + coordinates['height']]

	def get_coordinates_of_new_inside_selection_box(self):
		# retrieve x0, y0, width and height of full selection
		region = self.parent.roi_id.getArraySlice(self.parent.final_image, self.parent.ui.image_view.imageItem)
		x0 = region[0][0].start
		y0 = region[0][1].start
		# [x0, y0] = self.parentselection_x0y0
		width_full_selection = np.int(str(self.parent.ui.roi_width.text()))
		height_full_selection = np.int(str(self.parent.ui.roi_height.text()))
	
		delta_width = width_full_selection - width_requested
		delta_height = height_full_selection - height_requested
	
		new_x0 = x0 + np.int(delta_width / 2)
		new_y0 = y0 + np.int(delta_height / 2)
	
		return {'x0'   : new_x0, 'y0': new_y0,
		        'x1'   : new_x0 + width_requested + 1, 'y1': new_y0 + height_requested + 1,
		        'width': width_requested, 'height': height_requested}



	def update_selection(self, new_value=None, mode='square'):
		if self.parent.roi_id is None:
			return

		try:
			region = self.parent.roi_id.getArraySlice(self.parent.final_image,
			                                          self.parent.ui.image_view.imageItem)
		except TypeError:
			return

		x0 = region[0][0].start
		y0 = region[0][1].start
		self.parent.selection_x0y0 = [x0, y0]

		# remove old one
		self.parent.ui.image_view.removeItem(self.parent.roi_id)

		_pen = QtGui.QPen()
		_pen.setColor(self.parent.roi_settings['color'])
		_pen.setWidth(self.parent.roi_settings['width'])
		self.parent.roi_id = pg.ROI([x0, y0],
		                     [new_value, new_value],
		                     pen=_pen,
		                     scaleSnap=True)

		self.parent.ui.image_view.addItem(self.parent.roi_id)
		self.parent.roi_id.sigRegionChanged.connect(self.parent.roi_moved)

		if mode == 'square':
			self.parent.ui.roi_width.setText(str(new_value))
			self.parent.ui.roi_height.setText(str(new_value))
			self.parent.reset_profile_of_bin_size_slider()
			self.parent.update_profile_of_bin_size_infos()
		else:
			self.parent.roi_id.addScaleHandle([1, 1], [0, 0])

		self.update_selection_profile_plot()
		self.update_roi_defined_by_profile_of_bin_size_slider()

	def update_selection_plot(self):
		self.parent.ui.profile.clear()
		o_get = Get(parent=self.parent)
		x_axis, x_axis_label = o_get.x_axis()
		max_value = self.parent.ui.profile_of_bin_size_slider.maximum()
		roi_selected = max_value - self.parent.ui.profile_of_bin_size_slider.value()

		y_axis = self.parent.fitting_input_dictionary['rois'][roi_selected]['profile']

		self.parent.ui.profile.plot(x_axis, y_axis, pen=(self.parent.shrinking_roi_rgb[0],
		                                          self.parent.shrinking_roi_rgb[1],
		                                          self.parent.shrinking_roi_rgb[2]))
		self.parent.ui.profile.setLabel("bottom", x_axis_label)
		self.parent.ui.profile.setLabel("left", 'Mean transmission')

		# full region
		y_axis = self.parent.fitting_input_dictionary['rois'][0]['profile']
		self.parent.ui.profile.plot(x_axis, y_axis, pen=(self.parent.selection_roi_rgb[0],
		                                          self.parent.selection_roi_rgb[1],
		                                          self.parent.selection_roi_rgb[2]))


	def profile_of_bin_size_slider_changed(self, new_value):
		try:
			self.parent.update_dict_profile_to_fit()
			if self.parent.ui.square_roi_radiobutton.isChecked():
				new_width = new_value
				new_height = new_value
			else:
				initial_roi_width = np.int(str(self.parent.ui.roi_width.text()))
				initial_roi_height = np.int(str(self.parent.ui.roi_height.text()))
				if initial_roi_width == initial_roi_height:
					new_width = new_value
					new_height = new_value
				elif initial_roi_width < initial_roi_height:
					new_width = new_value
					delta = initial_roi_width - new_width
					new_height = initial_roi_height - delta
				else:
					new_height = new_value
					delta = initial_roi_height - new_height
					new_width = initial_roi_width - delta

			self.parent.ui.profile_of_bin_size_width.setText(str(new_width))
			self.parent.ui.profile_of_bin_size_height.setText(str(new_height))
			self.update_roi_defined_by_profile_of_bin_size_slider()
			self.update_selection_profile_plot()
		except AttributeError:
			pass

	def update_roi_defined_by_profile_of_bin_size_slider(self):
		coordinates_new_selection = self.get_coordinates_of_new_inside_selection_box()
		self.parent.shrinking_roi = coordinates_new_selection
		x0 = coordinates_new_selection['x0']
		y0 = coordinates_new_selection['y0']
		width = coordinates_new_selection['width']
		height = coordinates_new_selection['height']

		# remove old selection
		if self.parent.shrinking_roi_id:
			self.parent.ui.image_view.removeItem(self.parent.shrinking_roi_id)

		# plot new box
		_pen = QtGui.QPen()
		_pen.setDashPattern(self.parent.shrinking_roi_settings['dashes_pattern'])
		_pen.setColor(self.parent.shrinking_roi_settings['color'])
		_pen.setWidth(self.parent.shrinking_roi_settings['width'])

		self.parent.shrinking_roi_id = pg.ROI([x0, y0],
		                               [width, height],
		                               pen=_pen,
		                               scaleSnap=True,
		                               movable=False)
		self.parent.ui.image_view.addItem(self.parent.shrinking_roi_id)

	def update_profile_of_bin_slider_widget(self):
		self.parent.change_profile_of_bin_slider_signal()
		fitting_input_dictionary = self.parent.fitting_input_dictionary
		dict_rois_imported = OrderedDict()
		nbr_key = len(fitting_input_dictionary['rois'].keys())
		for _index, _key in enumerate(fitting_input_dictionary['rois'].keys()):
			dict_rois_imported[nbr_key - 1 - _index] = {'width' : fitting_input_dictionary['rois'][_key]['width'],
			                                            'height': fitting_input_dictionary['rois'][_key]['height']}
		self.parent.dict_rois_imported = dict_rois_imported
		self.parent.ui.profile_of_bin_size_slider.setRange(0, len(dict_rois_imported) - 1)
		# self.parent.ui.profile_of_bin_size_slider.setMinimum(0)
		# self.parent.ui.profile_of_bin_size_slider.setMaximum(len(dict_rois_imported)-1)
		self.parent.ui.profile_of_bin_size_slider.setSingleStep(1)
		self.parent.ui.profile_of_bin_size_slider.setValue(len(dict_rois_imported) - 1)
		self.parent.update_profile_of_bin_slider_labels()

	def update_selection_roi_slider_changed(self):
	    value = self.parent.ui.roi_size_slider.value()
	    self.parent.selection_roi_slider_changed(value)
