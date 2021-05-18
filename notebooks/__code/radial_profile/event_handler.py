import numpy as np
import pyqtgraph as pg

from __code._utilities.parent import Parent
from __code.radial_profile.display import Display


class EventHandler(Parent):

    def file_index_changed(self):
        file_index = self.parent.ui.slider.value()
        live_image = self.parent.get_selected_image(file_index)

        _view = self.parent.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.parent.histogram_level == []:
            first_update = True
        _histo_widget = self.parent.ui.image_view.getHistogramWidget()
        self.parent.histogram_level = _histo_widget.getLevels()

        _image = np.transpose(live_image)
        self.parent.ui.image_view.setImage(_image)
        self.parent.live_image = _image
        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.parent.histogram_level[0], self.parent.histogram_level[1])

    def guide_color_changed(self):
        red = self.parent.ui.guide_red_slider.value()
        green = self.parent.ui.guide_green_slider.value()
        blue = self.parent.ui.guide_blue_slider.value()
        alpha = self.parent.ui.guide_alpha_slider.value()
        self.parent.guide_color_slider['red'] = red
        self.parent.guide_color_slider['green'] = green
        self.parent.guide_color_slider['blue'] = blue
        self.parent.guide_color_slider['alpha'] = alpha
        self.circle_center_changed()

        self.parent.ui.image_view.removeItem(self.parent.line_view_binning)

        o_display = Display(parent=self.parent)
        o_display.grid()

    def circle_center_changed(self):
        if self.parent.ui.sector_full_circle.isChecked():
            if self.parent.sector_g:
                self.parent.ui.image_view.removeItem(self.parent.sector_g)
            return

        x0 = float(self.parent.ui.circle_x.text())
        y0 = float(self.parent.ui.circle_y.text())
        from_angle = np.float(str(self.parent.ui.sector_from_value.text()))
        to_angle = np.float(str(self.parent.ui.sector_to_value.text()))

        self.calculate_corners_angles()
        self.update_angle_label_position()

        [y1, x1] = self.calculate_sector_xy_position(angle=from_angle, x0=x0, y0=y0)
        [y2, x2] = self.calculate_sector_xy_position(angle=to_angle, x0=x0, y0=y0)

        pos = np.array([[x0, y0], [x1, y1], [x2, y2]])
        adj = np.array([[0, 1], [1, 2], [2, 0]])

        symbols = ['+', 'o', 'o']

        lines = np.array([(255, 0, 0, 255, 2), (255, 0, 0, 0, 1), (255, 0, 0, 255, 2)],
                         dtype=[('red', np.ubyte), ('green', np.ubyte), ('blue', np.ubyte), ('alpha', np.ubyte),
                                ('width', float)])

        if self.parent.sector_g:
            self.parent.ui.image_view.removeItem(self.parent.sector_g)
        self.parent.sector_g = pg.GraphItem()
        self.parent.ui.image_view.addItem(self.parent.sector_g)
        self.parent.sector_g.setData(pos=pos, adj=adj, pen=lines, size=1, symbol=symbols, pxMode=False)
        
    def update_angle_label_position(self):
        x0 = np.int(str(self.parent.ui.circle_x.text()))
        y0 = np.int(str(self.parent.ui.circle_y.text()))

        # add angle 0, 90, 180 and 270 labels
        if self.parent.angle_0 is None:
            self.parent.angle_0 = pg.TextItem(text=u'0\u00b0', anchor=(0, 1))
            self.parent.angle_90 = pg.TextItem(text=u'90\u00b0', anchor=(0, 1))
            self.parent.angle_180 = pg.TextItem(text=u'180\u00b0', anchor=(0, 0))
            self.parent.angle_270 = pg.TextItem(text=u'270\u00b0', anchor=(1, 1))

            self.parent.ui.image_view.addItem(self.parent.angle_0)
            self.parent.ui.image_view.addItem(self.parent.angle_90)
            self.parent.ui.image_view.addItem(self.parent.angle_180)
            self.parent.ui.image_view.addItem(self.parent.angle_270)

        self.parent.angle_0.setPos(np.int(x0), 0)
        self.parent.angle_90.setPos(self.parent.height, y0)
        self.parent.angle_180.setPos(x0, self.parent.width)
        self.parent.angle_270.setPos(0, y0)
        
    def calculate_sector_xy_position(self, angle=0, x0=0, y0=0):
        x = np.NaN
        y = np.NaN

        angle_top_right = self.parent.corners['top_right']
        angle_bottom_right = self.parent.corners['bottom_right']
        angle_bottom_left = self.parent.corners['bottom_left']
        angle_top_left = self.parent.corners['top_left']

        # print("angle_top_right: {}".format(angle_top_right))
        # print("angle_bottom_right: {}".format(angle_bottom_right))
        # print("angle_bottom_left: {}".format(angle_bottom_left))
        # print("angle_top_left: {}".format(angle_top_left))

        if (angle_top_right <= angle) and \
                (angle <= angle_bottom_right):
            # right

            # get x
            x = self.parent.height

            # get y
            _angle = np.abs(90 - angle)

            if angle == 90:
                y = 0
            else:
                angle_rad = np.deg2rad(_angle)
                y = np.tan(angle_rad) * (self.parent.height - x0)

            if angle <= 90:
                y = y0 - y
            else:
                y = y0 + y

        elif angle_bottom_right < angle < angle_bottom_left:
            # bottom

            # get y
            y = self.parent.width

            # get x
            _angle = np.abs(180 - angle)

            if angle == 180:
                x = 0
            else:
                angle_rad = np.deg2rad(_angle)
                x = (y - y0) * np.tan(angle_rad)

            if angle <= 180:
                x = x0 + x
            else:
                x = x0 - x

        elif angle_bottom_left <= angle <= angle_top_left:
            # left

            # get x
            x = 0

            # get y
            _angle = np.abs(270 - angle)

            if angle == 270:
                y = 0
            else:
                angle_rad = np.deg2rad(_angle)
                y = np.tan(angle_rad) * x0

            if angle <= 270:
                y = y0 + y
            else:
                y = y0 - y

        else:
            # top

            # get y
            y = 0

            # get x
            b_right_part = True
            if angle > angle_top_left:
                angle = np.abs(360 - angle)
                b_right_part = False

            if angle == 0:
                x = 0
            else:
                angle_rad = np.deg2rad(angle)
                x = y0 * np.tan(angle_rad)

            if b_right_part:
                x = x0 + x
            else:
                x = x0 - x

        return [y, x]
    
    def calculate_corners_angles(self):
        '''top vertical being angle 0'''

        x0 = float(str(self.parent.ui.circle_x.text()))
        y0 = float(str(self.parent.ui.circle_y.text()))

        width = self.parent.width
        height = self.parent.height
        #        width = self.parent.height
        #        height = self.parent.width

        theta_tr = np.NaN  # angle top right
        theta_br = np.NaN  # bottom right
        theta_bl = np.NaN  # bottom left
        theta_tl = np.NaN  # top left

        theta_tr = np.arctan((width - x0) / y0)
        theta_tr_deg = np.rad2deg(theta_tr)

        theta_br = np.pi - np.arctan((width - x0) / (height - y0))
        theta_br_deg = np.rad2deg(theta_br)

        theta_bl = np.pi + np.arctan(x0 / (height - y0))
        theta_bl_deg = np.rad2deg(theta_bl)

        theta_tl = 2 * np.pi - np.arctan(x0 / y0)
        theta_tl_deg = np.rad2deg(theta_tl)

        self.parent.corners['top_right'] = theta_tr_deg
        self.parent.corners['bottom_right'] = theta_br_deg
        self.parent.corners['bottom_left'] = theta_bl_deg
        self.parent.corners['top_left'] = theta_tl_deg
        
    def sector_radio_button_changed(self):
        is_full_circle = self.parent.ui.sector_full_circle.isChecked()
        if is_full_circle:
            _status_sector = False
            self.remove_angle_label()
        else:
            _status_sector = True
            self.update_angle_label_position()

        self.parent.ui.sector_from_label.setEnabled(_status_sector)
        self.parent.ui.sector_from_value.setEnabled(_status_sector)
        self.parent.ui.sector_from_units.setEnabled(_status_sector)
        self.parent.ui.sector_to_label.setEnabled(_status_sector)
        self.parent.ui.sector_to_value.setEnabled(_status_sector)
        self.parent.ui.sector_to_units.setEnabled(_status_sector)
        self.parent.ui.from_angle_slider.setEnabled(_status_sector)
        self.parent.ui.to_angle_slider.setEnabled(_status_sector)
        self.parent.sector_changed()

    def remove_angle_label(self):
        if self.parent.angle_0:
            self.parent.ui.image_view.removeItem(self.parent.angle_0)

        if self.parent.angle_90:
            self.parent.ui.image_view.removeItem(self.parent.angle_90)

        if self.parent.angle_180:
            self.parent.ui.image_view.removeItem(self.parent.angle_180)

        if self.parent.angle_270:
            self.parent.ui.image_view.removeItem(self.parent.angle_270)

        self.parent.angle_0 = None
        self.parent.angle_90 = None
        self.parent.angle_180 = None
        self.parent.angle_270 = None
