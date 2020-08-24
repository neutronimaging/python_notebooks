import numpy as np
import matplotlib
import os
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from qtpy.QtWidgets import QProgressBar, QVBoxLayout, QHBoxLayout
from qtpy import QtGui, QtCore
from qtpy.QtWidgets import QCheckBox, QTextEdit, QVBoxLayout, QWidget
import pyqtgraph as pg
from collections import OrderedDict

from __code.table_handler import TableHandler
from __code.bragg_edge.mplcanvas import MplCanvas


class Initialization:

	distance_detector_sample = 1300  # m
	detector_offset = 6500  # micros

	march_dollase_history = OrderedDict()
	march_dollase_history[0] = {'state': [False, False, False, True, False, False, True],
	                            'value': [np.NaN, 3.5, 4.5, np.NaN, np.NaN, np.NaN, np.NaN]}
	march_dollase_history[1] = {'state': [False, False, False, False, True, True, False]}
	march_dollase_history[2] = {'state': [True, True, True, False, False, False, False]}
	march_dollase_history[3] = {'state': [False, False, False, True, True, True, True]}
	march_dollase_history[4] = {'state': [True, True, True, False, False, False, False]}
	march_dollase_history[5] = {'state': [True, True, True, True, True, True, True]}
	march_dollase_row_height = {0: 110,
	                            'other': 60}

	def __init__(self, parent=None, tab='all'):
		self.parent = parent

		self.block_signals(True)
		self.pyqtgraph_image_view()
		self.pyqtgraph_profile()
		self.matplotlib()

		if tab == 'all':
			self.save_image_size()
			self.roi_setup()
			self.widgets()

		self.labels()
		self.text_fields()
		self.statusbar()
		self.pyqtgraph_fitting()
		self.kropff_fitting_table()
		self.march_dollase()

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

	def matplotlib(self):

		def _matplotlib(parent=None, widget=None):
			sc = MplCanvas(parent, width=5, height=4, dpi=100)
			# sc.axes.plot([0,1,2,3,4,5], [10, 1, 20 ,3, 40, 50])
			toolbar = NavigationToolbar(sc, parent)
			layout = QVBoxLayout()
			layout.addWidget(toolbar)
			layout.addWidget(sc)
			widget.setLayout(layout)
			return sc

		self.parent.kropff_high_plot = _matplotlib(parent=self.parent,
		                                           widget=self.parent.ui.high_widget)
		self.parent.kropff_low_plot = _matplotlib(parent=self.parent,
		                                           widget=self.parent.ui.low_widget)
		self.parent.kropff_bragg_peak_plot = _matplotlib(parent=self.parent,
		                                           widget=self.parent.ui.bragg_peak_widget)

	def pyqtgraph_fitting(self):
		# fitting view
		self.parent.ui.fitting = pg.PlotWidget(title="Fitting")
		fitting_layout = QVBoxLayout()
		fitting_layout.addWidget(self.parent.ui.fitting)
		self.parent.ui.fitting_widget.setLayout(fitting_layout)

	def kropff_fitting_table(self):
		## Kropff
		# high lambda
		column_names = [u'x\u2080; y\u2080; width; height', u'a\u2080', u'b\u2080', u'a\u2080_error',
		                u'b\u2080_error']
		column_sizes = [150, 100, 100, 100, 100]
		o_high = TableHandler(table_ui=self.parent.ui.high_tof_tableWidget)
		for _col_index, _col_name in enumerate(column_names):
			o_high.insert_column(_col_index)
		o_high.set_column_names(column_names=column_names)
		o_high.set_column_sizes(column_sizes=column_sizes)

		# low lambda
		column_names = [u'x\u2080; y\u2080; width; height',
		                u'a_hkl', u'b_hkl',
		                u'a_hkl_error',
		                u'b_hkl_error']
		column_sizes = [150, 100, 100, 100, 100]
		o_low = TableHandler(table_ui=self.parent.ui.low_tof_tableWidget)
		for _col_index, _col_name in enumerate(column_names):
			o_low.insert_column(_col_index)
		o_low.set_column_names(column_names=column_names)
		o_low.set_column_sizes(column_sizes=column_sizes)

		# bragg edge
		column_names = ['x0; y0; width; height', 't_hkl', 'tau', 'sigma',
		                't_hkl_error', 'tau_error', 'sigma_error']
		column_sizes = [150, 100, 100, 100, 100, 100, 100]
		o_bragg = TableHandler(table_ui=self.parent.ui.bragg_edge_tableWidget)
		for _col_index, _col_name in enumerate(column_names):
			o_bragg.insert_column(_col_index)
		o_bragg.set_column_names(column_names=column_names)
		o_bragg.set_column_sizes(column_sizes=column_sizes)

	def march_dollase(self):
		# init widgets
		_file_path = os.path.dirname(__file__)
		up_arrow_file = os.path.abspath(os.path.join(_file_path, '../static/up_arrow_black.png'))
		self.parent.ui.march_dollase_user_input_up.setIcon(QtGui.QIcon(up_arrow_file))

		down_arrow_file = os.path.abspath(os.path.join(_file_path, '../static/down_arrow_black.png'))
		self.parent.ui.march_dollase_user_input_down.setIcon(QtGui.QIcon(down_arrow_file))

		# init history table
		march_dollase_history = self.march_dollase_history
		nbr_column = len(march_dollase_history[0]['state'])
		for _row in march_dollase_history.keys():
			self.parent.ui.marche_dollase_user_input_table.insertRow(_row)

			row_height = self.march_dollase_row_height[0] if _row == 0 else self.march_dollase_row_height['other']
			self.parent.ui.marche_dollase_user_input_table.setRowHeight(_row, row_height)

			for _col in np.arange(nbr_column):
				_state_col = march_dollase_history[_row]['state'][_col]
				_widget = QWidget()
				verti_layout = QVBoxLayout()

				hori_layout = QHBoxLayout()
				_checkbox = QCheckBox()
				_checkbox.setChecked(_state_col)
				hori_layout.addStretch()
				hori_layout.addWidget(_checkbox)
				hori_layout.addStretch()
				new_widget = QWidget()
				new_widget.setLayout(hori_layout)
				verti_layout.addWidget(new_widget)

				if (_row == 0) and (not _state_col):  # add init value if working with first row and state is
					# False
					_input = QTextEdit()
					_input.setText(str(march_dollase_history[_row]['value'][_col]))
					verti_layout.addWidget(_input)
				_widget.setLayout(verti_layout)
				self.parent.ui.marche_dollase_user_input_table.setCellWidget(_row, _col, _widget)

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

		self.parent.ui.kropff_high_tof_a0_init.setText(str(self.parent.fitting_parameters_init['kropff']['a0']))
		self.parent.ui.kropff_high_tof_b0_init.setText(str(self.parent.fitting_parameters_init['kropff']['b0']))
		self.parent.ui.kropff_low_tof_ahkl_init.setText(str(self.parent.fitting_parameters_init['kropff']['ahkl']))
		self.parent.ui.kropff_low_tof_bhkl_init.setText(str(self.parent.fitting_parameters_init['kropff']['bhkl']))
		self.parent.ui.kropff_bragg_peak_tofhkl_init.setText(str(self.parent.fitting_parameters_init['kropff'][
			                                                         'tofhkl']))
		self.parent.ui.kropff_bragg_peak_tau_init.setText(str(self.parent.fitting_parameters_init['kropff']['tau']))
		list_sigma = self.parent.fitting_parameters_init['kropff']['sigma']
		list_sigma = [str(_value) for _value in list_sigma]
		str_list_sigma = ", ".join(list_sigma)
		self.parent.ui.kropff_bragg_peak_sigma_init.setText(str_list_sigma)

		kropff_list_sigma = self.parent.fitting_parameters_init['kropff']['sigma']
		str_kropff_list_sigma = [str(value) for value in kropff_list_sigma]
		self.parent.ui.kropff_bragg_peak_sigma_comboBox.addItems(str_kropff_list_sigma)

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
