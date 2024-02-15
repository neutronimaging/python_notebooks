import numpy as np
from skimage import transform
import pyqtgraph as pg


class DisplayImages:

    def __init__(self, parent=None, recalculate_image=False):
        self.parent = parent
        self.recalculate_image = recalculate_image

        self.display_images()
        self.display_grid()

    def get_image_selected(self, recalculate_image=False):
        slider_index = self.parent.ui.file_slider.value()
        if recalculate_image:
            angle = self.parent.rotation_angle
            # rotate all images
            self.parent.data_dict['data'] = [transform.rotate(_image, angle) for _image in
                                             self.parent.data_dict_raw['data']]

        _image = self.parent.data_dict['data'][slider_index]
        return _image

    def get_image_filename(self):
        slider_index = self.parent.ui.file_slider.value()
        return self.parent.list_filenames[slider_index]

    def display_images(self):
        _image = self.get_image_selected(recalculate_image=self.recalculate_image)
        _view = self.parent.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        _file_name = self.get_image_filename()
        self.parent.ui.filename.setText(_file_name)

        first_update = False
        if self.parent.histogram_level == []:
            first_update = True
        _histo_widget = self.parent.ui.image_view.getHistogramWidget()
        self.parent.histogram_level = _histo_widget.getLevels()

        _image = np.transpose(_image)
        self.parent.ui.image_view.setImage(_image)
        self.parent.live_image = _image
        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.parent.histogram_level[0], self.parent.histogram_level[1])

    def calculate_matrix_grid(self, grid_size=1, height=1, width=1):
        """calculate the matrix that defines the vertical and horizontal lines
        that allow pyqtgraph to display the grid"""

        pos_adj_dict = {}

        # pos - each matrix defines one side of the line
        pos = []
        adj = []

        # vertical lines
        x = 0
        index = 0
        while (x <= width):
            one_edge = [x, 0]
            other_edge = [x, height]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index + 1])
            x += grid_size
            index += 2

        # vertical lines
        y = 0
        while (y <= height):
            one_edge = [0, y]
            other_edge = [width, y]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index + 1])
            y += grid_size
            index += 2

        pos_adj_dict['pos'] = np.array(pos)
        pos_adj_dict['adj'] = np.array(adj)

        return pos_adj_dict

    def display_grid(self):
        # remove previous grid if any
        if self.parent.grid_view['item']:
            self.parent.ui.image_view.removeItem(self.parent.grid_view['item'])

        # if we want a grid
        if self.parent.ui.grid_display_checkBox.isChecked():
            grid_size = self.parent.ui.grid_size_slider.value()
            [height, width] = np.shape(self.parent.live_image)

            pos_adj_dict = self.calculate_matrix_grid(grid_size=grid_size,
                                                      height=height,
                                                      width=width)
            pos = pos_adj_dict['pos']
            adj = pos_adj_dict['adj']

            line_color = self.parent.grid_view['color']
            _transparency_value = 255 - (float(str(self.parent.ui.transparency_slider.value())) / 100) * 255
            _list_line_color = list(line_color)
            _list_line_color[3] = _transparency_value
            line_color = tuple(_list_line_color)
            lines = np.array([line_color for n in np.arange(len(pos))],
                             dtype=[('red', np.ubyte), ('green', np.ubyte),
                                    ('blue', np.ubyte), ('alpha', np.ubyte),
                                    ('width', float)])

            grid = pg.GraphItem()
            self.parent.ui.image_view.addItem(grid)
            grid.setData(pos=pos,
                         adj=adj,
                         pen=lines,
                         symbol=None,
                         pxMode=False)
            self.parent.grid_view['item'] = grid
