import pyqtgraph as pg
import numpy as np


class GuideAndProfileRoisHandler:
    __profile = None

    def __init__(self, parent=None, row=-1):
        self.parent = parent
        self.row = row
        if self.row == -1:
            self.row = 0

    def add(self):
        self._define_guide()
        self._define_profile()
        self.parent.list_profile_pyqt_roi.insert(self.row, self.__profile)

    def update(self):
        self._define_profile()
        self.parent.ui.image_view.removeItem(self.parent.list_profile_pyqt_roi[self.row])
        self.parent.list_profile_pyqt_roi[self.row] = self.__profile

    def _define_guide(self):
        """define the guide"""
        guide_roi = pg.RectROI([self.parent.default_guide_roi['x0'], self.parent.default_guide_roi['y0']],
                               [self.parent.default_guide_roi['width'], self.parent.default_guide_roi['height']],
                               pen=self.parent.default_guide_roi['color_activated'])
        guide_roi.addScaleHandle([1, 1], [0, 0])
        guide_roi.addScaleHandle([0, 0], [1, 1])
        guide_roi.sigRegionChanged.connect(self.parent.guide_changed)
        self.parent.ui.image_view.addItem(guide_roi)
        self.parent.list_guide_pyqt_roi.insert(self.row, guide_roi)

    def _define_profile(self):
        # profile
        # [x0, y0, width, height] = self.parent.get_item_row(row=self.row)
        _profile_width = self.parent.get_profile_width(row=self.row)
        is_x_profile_direction = self.parent.ui.profile_direction_x_axis.isChecked()
        # delta_profile = (_profile_width - 1) / 2.

        profile_dimension = self.parent.get_profile_dimensions(row=self.row)
        x_left = profile_dimension.x_left
        x_right = profile_dimension.x_right
        y_top = profile_dimension.y_top
        y_bottom = profile_dimension.y_bottom

        if is_x_profile_direction:

            pos = []
            pos.append([x_left, y_top])
            pos.append([x_right, y_top])
            adj = []
            adj.append([0, 1])

            if y_top != y_bottom:  # height == 1
                pos.append([x_left, y_bottom])
                pos.append([x_right, y_bottom])
                adj.append([2, 3])

            adj = np.array(adj)
            pos = np.array(pos)

        else:  # y-profile direction

            pos = []
            pos.append([x_left, y_top])
            pos.append([x_left, y_bottom])
            adj = []
            adj.append([0, 1])

            if y_top != y_bottom:  # height == 1
                pos.append([x_right, y_top])
                pos.append([x_right, y_bottom])
                adj.append([2, 3])

            adj = np.array(adj)
            pos = np.array(pos)

        line_color = self.parent.profile_color
        _list_line_color = list(line_color)
        line_color = tuple(_list_line_color)
        lines = np.array([line_color for n in np.arange(len(pos))],
                         dtype=[('red', np.ubyte), ('green', np.ubyte),
                                ('blue', np.ubyte), ('alpha', np.ubyte),
                                ('width', float)])

        profile = pg.GraphItem()
        self.parent.ui.image_view.addItem(profile)
        profile.setData(pos=pos,
                        adj=adj,
                        pen=lines,
                        symbol=None,
                        pxMode=False)

        self.__profile = profile
