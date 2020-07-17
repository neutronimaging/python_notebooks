import numpy as np
import os

from qtpy.QtWidgets import QProgressBar, QVBoxLayout
from qtpy import QtGui
import pyqtgraph as pg

from __code.table_handler import TableHandler


class Initialization:

	distance_detector_sample = 1300  # m
	detector_offset = 6500  # micros

	def __init__(self, parent=None, tab='all'):
		self.parent = parent

		self.block_signals(True)
		self.pyqtgraph_image_view()
		self.pyqtgraph_profile()

		if tab == 'all':
			self.save_image_size()
			self.roi_setup()
			self.widgets()

		self.labels()
		self.text_fields()
		self.statusbar()
		self.pyqtgraph_fitting()
		self.fitting_table()

		self.block_signals(False)

	def block_signals(self, flag):
		list_ui = [self.parent.ui.profile_of_bin_size_slider]
		for _ui in list_ui:
			_ui.blockSignals(flag)

	def save_image_size(self):
		_image = self.parent.get_live_image()
		[height, width] = np.shape(_image)
		self.parent.image_size['width'] = width
		self.parent.image_size['height'] = height

	def statusbar(self):
		self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
		self.parent.eventProgress.setMinimumSize(20, 14)
		self.parent.eventProgress.setMaximumSize(540, 100)
		self.parent.eventProgress.setVisible(False)
		self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

	def pyqtgraph_image_view(self):
		# image view
		self.parent.ui.image_view = pg.ImageView()
		self.parent.ui.image_view.ui.roiBtn.hide()
		self.parent.ui.image_view.ui.menuBtn.hide()
		image_layout = QVBoxLayout()
		image_layout.addWidget(self.parent.ui.image_view)
		self.parent.ui.image_widget.setLayout(image_layout)

	def pyqtgraph_profile(self):
		# profile view
		self.parent.ui.profile = pg.PlotWidget(title="Profile of ROI selected")
		profile_layout = QVBoxLayout()
		profile_layout.addWidget(self.parent.ui.profile)
		self.parent.ui.profile_widget.setLayout(profile_layout)

	def pyqtgraph_fitting(self):
		# fitting view
		self.parent.ui.fitting = pg.PlotWidget(title="Fitting")
		fitting_layout = QVBoxLayout()
		fitting_layout.addWidget(self.parent.ui.fitting)
		self.parent.ui.fitting_widget.setLayout(fitting_layout)

	def fitting_table(self):
		## Kropff
		# high lambda
		column_names = [u'x\u2080; y\u2080; width; height', u'a\u2080', u'b\u2080', u'a\u2080_error',
		                u'b\u2080_error']
		column_sizes = [150, 100, 100, 100, 100]
		o_high = TableHandler(table_ui=self.parent.ui.high_lambda_tableWidget)
		for _col_index, _col_name in enumerate(column_names):
			o_high.insert_column(_col_index)
		o_high.set_column_names(column_names=column_names)
		o_high.set_column_sizes(column_sizes=column_sizes)

		# low lambda
		column_names = [u'x\u2080; y\u2080; width; height', u'a\u2095\u2096\u2097', u'b\u2095\u2096\u2097',
		                u'a\u2095\u2096\u2097_error',
		                u'b\u2095\u2096\u2097_error']
		column_sizes = [150, 100, 100, 100, 100]
		o_low = TableHandler(table_ui=self.parent.ui.low_lambda_tableWidget)
		for _col_index, _col_name in enumerate(column_names):
			o_low.insert_column(_col_index)
		o_low.set_column_names(column_names=column_names)
		o_low.set_column_sizes(column_sizes=column_sizes)

		# bragg edge
		column_names = ['x0; y0; width; height', 'param1', 'error1']
		column_sizes = [150, 100, 100]
		o_bragg = TableHandler(table_ui=self.parent.ui.bragg_edge_tableWidget)
		for _col_index, _col_name in enumerate(column_names):
			o_bragg.insert_column(_col_index)
		o_bragg.set_column_names(column_names=column_names)
		o_bragg.set_column_sizes(column_sizes=column_sizes)

	def labels(self):
		# labels
		self.parent.ui.detector_offset_units.setText(u"\u03BCs")
		self.parent.ui.selection_tof_radiobutton.setText(u"TOF (\u03BCs)")
		self.parent.ui.fitting_tof_radiobutton.setText(u"TOF (\u03BCs)")
		self.parent.ui.selection_lambda_radiobutton.setText(u"\u03BB (\u212B)")
		self.parent.ui.fitting_lambda_radiobutton.setText(u"\u03BB (\u212B)")

	def text_fields(self):
		self.parent.ui.distance_detector_sample.setText(str(self.distance_detector_sample))
		self.parent.ui.detector_offset.setText(str(self.detector_offset))

	def widgets(self):
		self.parent.ui.splitter.setSizes([500, 400])

		self.parent.ui.roi_size_slider.setMinimum(1)
		max_value = np.min([self.parent.image_size['width'], self.parent.image_size['height']])
		self.parent.ui.roi_size_slider.setMaximum(max_value)
		default_roi_size = np.int(max_value/3)
		self.parent.ui.roi_size_slider.setValue(default_roi_size)
		self.parent.ui.roi_width.setText(str(default_roi_size))
		self.parent.ui.roi_height.setText(str(default_roi_size))
		self.parent.ui.profile_of_bin_size_width.setText(str(default_roi_size))
		self.parent.ui.profile_of_bin_size_height.setText(str(default_roi_size))
		self.parent.ui.profile_of_bin_size_slider.setMaximum(default_roi_size)
		self.parent.ui.profile_of_bin_size_slider.setValue(default_roi_size)

	def roi_setup(self):
		[x0, y0] = self.parent.roi_settings['position']
		self.parent.selection_x0y0 = [x0, y0]
		width = self.parent.ui.roi_size_slider.value()
		self.parent.previous_roi_selection['width'] = width
		self.parent.previous_roi_selection['height'] = width
		_pen = QtGui.QPen()
		_pen.setColor(self.parent.roi_settings['color'])
		_pen.setWidth(self.parent.roi_settings['width'])
		self.parent.roi_id = pg.ROI([x0, y0],
		                            [width, width],
		                            pen=_pen,
		                            scaleSnap=True)
		self.parent.ui.image_view.addItem(self.parent.roi_id)
		self.parent.roi_id.sigRegionChanged.connect(self.parent.roi_moved)

	def display(self, image=None):
		self.parent.live_image = image
		_image = np.transpose(image)
		_image = self._clean_image(_image)
		self.parent.ui.image_view.setImage(_image)

	def _clean_image(self, image):
		_result_inf = np.where(np.isinf(image))
		image[_result_inf] = np.NaN
		return image
