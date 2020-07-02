import numpy as np

from qtpy.QtWidgets import QProgressBar, QVBoxLayout
from qtpy import QtGui

# try:
# 	from PyQt4.QtGui import QFileDialog
# 	from PyQt4 import QtCore, QtGui
# 	from PyQt4.QtGui import QMainWindow
# except ImportError:
# 	from PyQt5.QtWidgets import QFileDialog
# 	from PyQt5 import QtCore, QtGui
# 	from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg



class Initialization:

	distance_detector_sample = 1300  # m
	detector_offset = 6500  # micros

	def __init__(self, parent=None):
		self.parent = parent

		self.save_image_size()
		self.statusbar()
		self.pyqtgraph()
		self.widgets()
		self.roi_setup()

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

	def pyqtgraph(self):
		# image view
		self.parent.ui.image_view = pg.ImageView()
		self.parent.ui.image_view.ui.roiBtn.hide()
		self.parent.ui.image_view.ui.menuBtn.hide()
		image_layout = QVBoxLayout()
		image_layout.addWidget(self.parent.ui.image_view)
		self.parent.ui.image_widget.setLayout(image_layout)

		# profile view
		self.parent.ui.profile = pg.PlotWidget(title="Profile of ROI selected")
		profile_layout = QVBoxLayout()
		profile_layout.addWidget(self.parent.ui.profile)
		self.parent.ui.profile_widget.setLayout(profile_layout)

		# fitting view
		self.parent.ui.fitting = pg.PlotWidget(title="Fitting")
		fitting_layout = QVBoxLayout()
		fitting_layout.addWidget(self.parent.ui.fitting)
		self.parent.ui.fitting_widget.setLayout(fitting_layout)

	def widgets(self):
		self.parent.ui.splitter.setSizes([500, 400])
		self.parent.ui.distance_detector_sample.setText(str(self.distance_detector_sample))
		self.parent.ui.detector_offset.setText(str(self.detector_offset))

		# labels
		self.parent.ui.detector_offset_units.setText(u"\u03BCs")
		self.parent.ui.selection_tof_radiobutton.setText(u"TOF (\u03BCs)")
		self.parent.ui.fitting_tof_radiobutton.setText(u"TOF (\u03BCs)")
		self.parent.ui.selection_lambda_radiobutton.setText(u"\u03BB (\u212B)")
		self.parent.ui.fitting_lambda_radiobutton.setText(u"\u03BB (\u212B)")

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
		width = self.parent.ui.roi_size_slider.value()
		_color = QtGui.QColor(self.parent.roi_settings['color'][0],
		                      self.parent.roi_settings['color'][1],
		                      self.parent.roi_settings['color'][2])

		_pen = QtGui.QPen()
		_pen.setColor(_color)
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
