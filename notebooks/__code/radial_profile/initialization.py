from qtpy.QtWidgets import QProgressBar, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QWidget, QSpacerItem, QSizePolicy
from qtpy import QtCore
import pyqtgraph as pg
import numpy as np

from __code._utilities.parent import Parent
from __code.radial_profile.event_handler import EventHandler


class Initialization(Parent):

    def pyqtgraph(self):
        self.parent.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.image_view.ui.roiBtn.hide()
        self.parent.ui.image_view.ui.menuBtn.hide()

        bottom_layout = QHBoxLayout()

        # file index slider
        label_1 = QLabel("File Index")
        self.parent.ui.slider = QSlider(QtCore.Qt.Horizontal)
        self.parent.ui.slider.setMaximum(len(self.parent.list_images) - 1)
        self.parent.ui.slider.setMinimum(0)
        self.parent.ui.slider.valueChanged.connect(self.parent.file_index_changed)

        # spacer
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        bottom_layout.addWidget(label_1)
        bottom_layout.addWidget(self.parent.ui.slider)
        bottom_layout.addItem(spacer)

        bottom_widget = QWidget()
        bottom_widget.setLayout(bottom_layout)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.parent.ui.image_view)
        vertical_layout.addWidget(bottom_widget)

        self.parent.ui.widget.setLayout(vertical_layout)

        # profile
        self.parent.ui.profile_plot = pg.PlotWidget()
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.parent.ui.profile_plot)
        self.parent.ui.widget_profile.setLayout(vertical_layout)

    def crosshair(self):
        x0 = float(str(self.parent.ui.circle_x.text()))
        y0 = float(str(self.parent.ui.circle_y.text()))

        self.parent.vLine = pg.InfiniteLine(pos=x0, angle=90, movable=True)
        self.parent.hLine = pg.InfiniteLine(pos=y0, angle=0, movable=True)

        self.parent.vLine.sigDragged.connect(self.parent.manual_circle_center_changed)
        self.parent.hLine.sigDragged.connect(self.parent.manual_circle_center_changed)

        self.parent.ui.image_view.addItem(self.parent.vLine, ignoreBounds=False)
        self.parent.ui.image_view.addItem(self.parent.hLine, ignoreBounds=False)

    def widgets(self):
        # self.parent.ui.circle_y.setText(str(int(self.parent.width / 2)))
        self.parent.ui.circle_y.setText(str(600))

        self.parent.ui.circle_x.setText(str(int(self.parent.height / 2)))
        # self.parent.ui.lineEdit.setText(str(self.parent.grid_size))

        self.parent.ui.guide_red_slider.setValue(self.parent.guide_color_slider['red'])
        self.parent.ui.guide_green_slider.setValue(self.parent.guide_color_slider['green'])
        self.parent.ui.guide_blue_slider.setValue(self.parent.guide_color_slider['blue'])
        self.parent.ui.guide_alpha_slider.setValue(self.parent.guide_color_slider['alpha'])

        self.parent.ui.sector_from_value.setText(str(self.parent.sector_range['from']))
        self.parent.ui.sector_to_value.setText(str(self.parent.sector_range['to']))

        self.parent.ui.sector_from_units.setText(u"\u00B0")
        self.parent.ui.sector_to_units.setText(u"\u00B0")

        self.parent.ui.from_angle_slider.setValue(self.parent.sector_range['from'])
        self.parent.ui.to_angle_slider.setValue(self.parent.sector_range['to'])

        self.parent.sector_radio_button_changed()

        # defines the maximum value of the radius slider
        o_event = EventHandler(parent=self.parent)
        max_radius = o_event.retrieve_max_radius_possible()
        self.parent.ui.max_radius_slider.setMaximum(max_radius)
        self.parent.ui.max_radius_slider.setValue(int(max_radius/2))

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)
