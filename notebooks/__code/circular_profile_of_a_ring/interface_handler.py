import os
from qtpy.QtWidgets import QMainWindow
import pyqtgraph as pg
from qtpy.QtWidgets import QVBoxLayout
import numpy as np

from __code import load_ui
from __code.decorators import wait_cursor
from __code._utilities.math import get_distance_between_two_points


class InterfaceHandler:

    def __init__(self, working_dir=None, o_norm=None):
        o_interface = Interface(data=o_norm.data['sample']['data'],
                                working_dir=working_dir)
        o_interface.show()


class Interface(QMainWindow):

    histogram_level = None
    current_live_image = None

    guide_color_slider = {'red': 255,
                          'green': 0,
                          'blue': 255,
                          'alpha': 255}
    line_view_binning = None

    def __init__(self, parent=None, data=None, working_dir=None):

        self.data = data
        [self.height, self.width] = np.shape(data[0])
        self.working_dir = working_dir

        super(Interface, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_circular_profile_of_a_ring.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Circular Profile of a Ring")

        self.init_widgets()
        self.slider_image_changed(new_index=0)
        self.init_crosshair()
        self.display_grid()

    def init_crosshair(self):
        x0 = float(str(self.ui.circle_x.text()))
        y0 = float(str(self.ui.circle_y.text()))

        self.vLine = pg.InfiniteLine(pos=x0, angle=90, movable=True)
        self.hLine = pg.InfiniteLine(pos=y0, angle=0, movable=True)

        self.vLine.sigDragged.connect(self.manual_circle_center_changed)
        self.hLine.sigDragged.connect(self.manual_circle_center_changed)

        self.ui.image_view.addItem(self.vLine, ignoreBounds=False)
        self.ui.image_view.addItem(self.hLine, ignoreBounds=False)

    def init_widgets(self):
        self.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.image_view.ui.roiBtn.hide()
        self.ui.image_view.ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.ui.image_view)
        self.ui.widget.setLayout(image_layout)

        self.ui.splitter.setSizes([500, 200])

        nbr_files = len(self.data)
        self.ui.image_slider.setMaximum(nbr_files-1)

        self.ui.circle_y.setText(str("{:.2f}".format(self.width / 2)))
        self.ui.circle_x.setText(str("{:.2f}".format(self.height / 2)))

        self.ui.guide_red_slider.setValue(self.guide_color_slider['red'])
        self.ui.guide_green_slider.setValue(self.guide_color_slider['green'])
        self.ui.guide_blue_slider.setValue(self.guide_color_slider['blue'])
        self.ui.guide_alpha_slider.setValue(self.guide_color_slider['alpha'])

        # ring settings
        max_ring_value = self.width
        default_inner_ring_value = np.int(self.width/2)
        default_ring_thickness = 20
        self.ui.ring_inner_radius_slider.setMaximum(max_ring_value*100)  # *100 because slider is int
        self.ui.ring_inner_radius_slider.setValue(default_inner_ring_value*100)
        self.ui.ring_inner_radius_doubleSpinBox.setMaximum(max_ring_value)
        self.ui.ring_inner_radius_doubleSpinBox.setSingleStep(0.01)
        self.ui.ring_inner_radius_doubleSpinBox.setValue(default_inner_ring_value)
        self.ui.ring_thickness_slider.setMaximum(max_ring_value*100)
        self.ui.ring_thickness_slider.setValue(default_ring_thickness*100)
        self.ui.ring_thickness_doubleSpinBox.setMaximum(max_ring_value)
        self.ui.ring_thickness_doubleSpinBox.setValue(default_ring_thickness)

    def display_grid(self):
        [width, height] = [self.width, self.height]
        # bin_size = float(str(self.ui.lineEdit.text()))
        bin_size = self.ui.grid_size_slider.value()
        x0 = 0
        y0 = 0

        # pos_adj_dict = {}

        nbr_height_bins = np.float(height) / np.float(bin_size)
        real_height = y0 + np.int(nbr_height_bins) * np.int(bin_size)

        nbr_width_bins = np.float(width) / np.float(bin_size)
        read_width = x0 + np.int(nbr_width_bins) * np.int(bin_size)

        # pos (each matrix is one side of the lines)
        pos = []
        adj = []

        # vertical lines
        x = x0
        index = 0
        while x <= x0 + width:
            one_edge = [x, y0]
            other_edge = [x, real_height]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index + 1])
            x += bin_size
            index += 2

        # horizontal lines
        y = y0
        while y <= y0 + height:
            one_edge = [x0, y]
            other_edge = [read_width, y]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index + 1])
            y += bin_size
            index += 2

        pos = np.array(pos)
        adj = np.array(adj)

        line_color = (self.guide_color_slider['red'],
                      self.guide_color_slider['green'],
                      self.guide_color_slider['blue'],
                      self.guide_color_slider['alpha'], 0.5)
        lines = np.array([line_color for n in np.arange(len(pos))],
                         dtype=[('red', np.ubyte), ('green', np.ubyte),
                                ('blue', np.ubyte), ('alpha', np.ubyte),
                                ('width', float)])

        line_view_binning = pg.GraphItem()
        self.ui.image_view.addItem(line_view_binning)
        line_view_binning.setData(pos=pos,
                                  adj=adj,
                                  pen=lines,
                                  symbol=None,
                                  pxMode=False)

        self.line_view_binning = line_view_binning

    def grid_size_changed(self):
        self.ui.image_view.removeItem(self.line_view_binning)
        self.display_grid()

    def display_ring(self):
        x_central_pixel = np.float(str(self.ui.circle_x.text()))
        y_central_pixel = np.float(str(self.ui.circle_y.text()))

        ring_radius = self.ui.ring_inner_radius_doubleSpinBox.value()
        ring_thickness = self.ui.ring_thickness_doubleSpinBox.value()

        image_width = self.width
        image_height = self.height

        pixel_mask = np.zeros((image_height, image_width))
        for pixel_y in np.arange(image_height):
            for pixel_x in np.arange(image_width):
                distance_center_to_xypixel = get_distance_between_two_points(from_pixel={'x': x_central_pixel,
                                                                                         'y': y_central_pixel},
                                                                             to_pixel={'x': pixel_x,
                                                                                       'y': pixel_y})






    # Event handler
    def manual_circle_center_changed(self):
        new_x0 = np.float(self.vLine.value())
        self.ui.circle_x.setText("{:.2f}".format(new_x0))

        new_y0 = np.float(self.hLine.value())
        self.ui.circle_y.setText("{:.2f}".format(new_y0))

    def help_button_clicked(self):
        pass

    @wait_cursor
    def guide_color_changed(self, index_position):
        red = self.ui.guide_red_slider.value()
        green = self.ui.guide_green_slider.value()
        blue = self.ui.guide_blue_slider.value()
        alpha = self.ui.guide_alpha_slider.value()
        self.guide_color_slider['red'] = red
        self.guide_color_slider['green'] = green
        self.guide_color_slider['blue'] = blue
        self.guide_color_slider['alpha'] = alpha
        # self.circle_center_changed()

        self.ui.image_view.removeItem(self.line_view_binning)
        self.display_grid()

    @wait_cursor
    def guide_color_clicked(self):
        self.guide_color_changed(-1)

    @wait_cursor
    def guide_color_released(self):
        self.guide_color_changed(-1)

    @wait_cursor
    def grid_slider_moved(self, index):
        self.grid_size_changed()

    @wait_cursor
    def grid_slider_pressed(self):
        self.grid_size_changed()

    def export_profiles_clicked(self):
        pass

    def cancel_clicked(self):
        pass

    def calculate_profiles_clicked(self):
        pass

    def slider_image_changed(self, new_index=0):
        _view = self.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.histogram_level is None:
            first_update = True
        _histo_widget = self.ui.image_view.getHistogramWidget()
        self.histogram_level = _histo_widget.getLevels()

        data = self.data[new_index]
        _image = np.transpose(data)
        self.ui.image_view.setImage(_image)
        self.current_live_image = _image

        _view_box.setState(_state)
        if not first_update:
            _histo_widget.setLevels(self.histogram_level[0],
                                    self.histogram_level[1])

    def ring_settings_thickness_slider_changed(self, slider_value):
        self.ui.ring_thickness_doubleSpinBox.setValue(slider_value/100)
        self.display_ring()

    def ring_settings_thickness_double_spin_box_changed(self, spin_box_value):
        self.ui.ring_thickness_slider.setValue(np.int(spin_box_value*100))
        self.display_ring()

    def ring_settings_inner_radius_slider_changed(self, slider_value):
        self.ui.ring_inner_radius_doubleSpinBox.setValue(slider_value/100)
        self.display_ring()

    def ring_settings_inner_radius_double_spin_box_changed(self, spin_box_value):
        self.ui.ring_inner_radius_slider.setValue(np.int(spin_box_value*100))
        self.display_ring()
