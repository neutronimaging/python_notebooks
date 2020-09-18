import numpy as np
import matplotlib
import os
import copy
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from qtpy.QtWidgets import QProgressBar, QVBoxLayout
from qtpy import QtGui
import pyqtgraph as pg

from __code.table_handler import TableHandler
from __code.bragg_edge.mplcanvas import MplCanvas
from __code.bragg_edge.bragg_edge_peak_fitting_gui_utility import GuiUtility


class Initialization:

	distance_detector_sample = 1300  # m
	detector_offset = 6500  # micros

	march_dollase_history_state = list()
	march_dollase_history_init = [np.NaN, np.NaN]
	march_dollase_history_state.append([False, False, False, True, False, False, True])
	march_dollase_history_state.append([False, False, False, False, True, True, False])
	march_dollase_history_state.append([True, True, True, False, False, False, False])
	march_dollase_history_state.append([False, False, False, True, True, True, True])
	march_dollase_history_state.append([True, True, True, False, False, False, False])
	march_dollase_history_state.append([True, True, True, True, True, True, True])

	def __init__(self, parent=None, tab='all'):
		self.parent = parent

		self.block_signals(True)
		self.pyqtgraph_image_view()
		self.pyqtgraph_profile()
		self.matplotlib()

		if tab == 'all':
			self.normalize_images_by_white_beam()
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

	def normalize_images_by_white_beam(self):
		white_beam_ob = self.parent.o_bragg.white_beam_ob
		list_data = self.parent.o_norm.data['sample']['data']
		for _index_data, _data in enumerate(list_data):
			normalized_data = _data / white_beam_ob
			self.parent.o_norm.data['sample']['data'][_index_data] = normalized_data

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

		self.parent.march_dollase_plot = _matplotlib(parent=self.parent,
		                                             widget=self.parent.ui.march_dollase_graph_widget)

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
		o_high = TableHandler(table_ui=self.parent.ui.high_lda_tableWidget)
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
		o_low = TableHandler(table_ui=self.parent.ui.low_lda_tableWidget)
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

		self.parent.march_dollase_history_state_full_reset = copy.deepcopy(self.march_dollase_history_state)

		# init widgets
		_file_path = os.path.dirname(__file__)
		up_arrow_file = os.path.abspath(os.path.join(_file_path, '../static/up_arrow_black.png'))
		self.parent.ui.march_dollase_user_input_up.setIcon(QtGui.QIcon(up_arrow_file))

		down_arrow_file = os.path.abspath(os.path.join(_file_path, '../static/down_arrow_black.png'))
		self.parent.ui.march_dollase_user_input_down.setIcon(QtGui.QIcon(down_arrow_file))

		o_gui = GuiUtility(parent=self.parent)
		o_gui.fill_march_dollase_table(list_state=self.march_dollase_history_state,
		                               initial_parameters=self.parent.march_dollase_fitting_initial_parameters)

		self.parent.march_dollase_fitting_history_table = self.march_dollase_history_state
		self.parent.march_dollase_fitting_history_table_default_new_row = copy.deepcopy(
				self.march_dollase_history_state[0])

		column_names = [u'x\u2080; y\u2080; width; height',
		                u'd_spacing', u'sigma', u'alpha',
		                u'A\u2081', u'A\u2082',
		                u'A\u2085', u'A\u2086',
		                u'd_spacing_error', u'sigma_error', u'alpha_error',
		                u'A\u2081_error',
		                u'A\u2082_error',
						u'A\u2085_error', u'A\u2086_error',
		                ]
		column_sizes = [150, 100, 100, 100, 100, 100, 100, 100,
		                     100, 100, 100, 100, 100, 100, 100]
		o_march = TableHandler(table_ui=self.parent.ui.march_dollase_result_table)
		for _col_index, _col_name in enumerate(column_names):
			o_march.insert_column(_col_index)
		o_march.set_column_names(column_names=column_names)
		o_march.set_column_sizes(column_sizes=column_sizes)

		state_advanced_columns = not self.parent.ui.march_dollase_advanced_mode_checkBox.isChecked()
		o_gui.set_columns_hidden(table_ui=self.parent.ui.march_dollase_user_input_table,
		                         list_of_columns=[5, 6],
		                         state=state_advanced_columns)

		# table
		self.parent.ui.march_dollase_user_input_table.verticalHeader().setVisible(True)
		self.parent.ui.march_dollase_result_table.verticalHeader().setVisible(True)
		self.parent.ui.march_dollase_result_table.horizontalHeader().setVisible(True)

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

		self.parent.ui.kropff_high_lda_a0_init.setText(str(self.parent.fitting_parameters_init['kropff']['a0']))
		self.parent.ui.kropff_high_lda_b0_init.setText(str(self.parent.fitting_parameters_init['kropff']['b0']))
		self.parent.ui.kropff_low_lda_ahkl_init.setText(str(self.parent.fitting_parameters_init['kropff']['ahkl']))
		self.parent.ui.kropff_low_lda_bhkl_init.setText(str(self.parent.fitting_parameters_init['kropff']['bhkl']))
		self.parent.ui.kropff_bragg_peak_ldahkl_init.setText(str(self.parent.fitting_parameters_init['kropff'][
			                                                         'ldahkl']))
		self.parent.ui.kropff_bragg_peak_tau_init.setText(str(self.parent.fitting_parameters_init['kropff']['tau']))
		# list_sigma = self.parent.fitting_parameters_init['kropff']['sigma']
		# list_sigma = [str(_value) for _value in list_sigma]
		# str_list_sigma = ", ".join(list_sigma)
		# self.parent.ui.kropff_bragg_peak_sigma_init.setText(str_list_sigma)

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
