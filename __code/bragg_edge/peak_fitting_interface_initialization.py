try:
	from PyQt4.QtGui import QFileDialog
	from PyQt4 import QtCore, QtGui
	from PyQt4.QtGui import QMainWindow
except ImportError:
	from PyQt5.QtWidgets import QFileDialog
	from PyQt5 import QtCore, QtGui
	from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg


class Initialization:

	def __init__(self, parent=None):
		self.parent = parent

	def init_statusbar(self):
		self.parent.eventProgress = QtGui.QProgressBar(self.parent.ui.statusbar)
		self.parent.eventProgress.setMinimumSize(20, 14)
		self.parent.eventProgress.setMaximumSize(540, 100)
		self.parent.eventProgress.setVisible(False)
		self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

	def init_pyqtgraph(self):
		# image view
		self.parent.ui.image_view = pg.ImageView()
		self.parent.ui.image_view.ui.roiBtn.hide()
		self.parent.ui.image_view.ui.menuBtn.hide()
		image_layout = QtGui.QVBoxLayout()
		image_layout.addWidget(self.parent.ui.image_view)
		self.parent.ui.image_widget.setLayout(image_layout)

		# profile view
		self.parent.ui.profile = pg.PlotWidget(title="Profile of ROI selected")
		profile_layout = QtGui.QVBoxLayout()
		profile_layout.addWidget(self.parent.ui.profile)
		self.parent.ui.profile_widget.setLayout(profile_layout)

		
