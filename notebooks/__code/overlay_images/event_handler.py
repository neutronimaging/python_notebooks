import numpy as np
import pyqtgraph as pg
from PIL import Image
from qtpy import QtGui

from __code._utilities.table_handler import TableHandler


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def update_views(self, row_selected=0):

        self.update_view(image_resolution='high_res',
                         data=self.parent.o_norm_high_res.data['sample']['data'][row_selected])

        self.update_view(image_resolution='low_res',
                         data=self.parent.o_norm_low_res.data['sample']['data'][row_selected])

        if self.parent.resize_and_overlay_images:
            self.update_overlay_view(row_selected=row_selected)

    def update_overlay_view(self, row_selected=0):
        self.parent.image_view['overlay'].clear()
        _image = np.transpose(self.parent.resize_and_overlay_images[row_selected])
        self.parent.image_view['overlay'].setImage(_image)
        self.parent.current_live_image['overlay'] = _image

    def update_view(self, image_resolution='high_res', data=None):

        image_view = self.parent.image_view[image_resolution]
        histogram_level = self.parent.histogram_level[image_resolution]

        # high resolution
        _res_view = image_view.getView()
        _res_view_box = _res_view.getViewBox()
        _state = _res_view_box.getState()

        first_update = False
        if histogram_level is None:
            first_update = True
        histo_widget = image_view.getHistogramWidget()
        histogram_level = histo_widget.getLevels()
        self.parent.histogram_level[image_resolution] = histogram_level

        _image = np.transpose(data)
        image_view.setImage(_image)
        self.parent.current_live_image[image_resolution] = _image

        _res_view_box.setState(_state)
        if not first_update:
            histo_widget.setLevels(histogram_level[0],
                                   histogram_level[1])

    def update_target(self, image_resolution='high_res', target_index='1'):

        image_view = self.parent.image_view[image_resolution]

        if not (self.parent.markers[image_resolution][target_index]['target_ui'] is None):
            image_view.removeItem(self.parent.markers[image_resolution][target_index]['target_ui'])

        width = self.parent.markers['width']
        height = self.parent.markers['height']

        pos = []
        adj = []

        x = self.parent.markers[image_resolution][target_index]['x']
        y = self.parent.markers[image_resolution][target_index]['y']
        target_length = self.parent.markers['target']['length']
        target_border = self.parent.markers['target']['border']

        pos.append([np.int(x + width / 2), y + target_border])
        pos.append([np.int(x + width / 2), y + target_border + target_length])
        adj.append([0, 1])

        pos.append([np.int(x + width / 2), y + height - target_length - target_border])
        pos.append([np.int(x + width / 2), y + height - target_border])
        adj.append([2, 3])

        pos.append([x + target_border, np.int(y + height / 2)])
        pos.append([x + target_border + target_length, np.int(y + height / 2)])
        adj.append([4, 5])

        pos.append([x + width - target_border - target_length, np.int(y + height / 2)])
        pos.append([x + width - target_border, np.int(y + height / 2)])
        adj.append([6, 7])

        pos = np.array(pos)
        adj = np.array(adj)

        line_color = self.parent.markers['target']['color'][target_index]
        lines = np.array([line_color for _ in np.arange(len(pos))],
                         dtype=[('red', np.ubyte), ('green', np.ubyte),
                                ('blue', np.ubyte), ('alpha', np.ubyte),
                                ('width', float)])
        line_view_binning = pg.GraphItem()
        image_view.addItem(line_view_binning)
        line_view_binning.setData(pos=pos,
                                  adj=adj,
                                  pen=lines,
                                  symbol=None,
                                  pxMode=False)
        self.parent.markers[image_resolution][target_index]['target_ui'] = line_view_binning

    def get_marker_index_parameters(self, region_index='1'):
        region = {'high_res': {'x': self.parent.markers['high_res'][region_index]['x'],
                               'y': self.parent.markers['high_res'][region_index]['y']},
                  'low_res': {'x': self.parent.markers['low_res'][region_index]['x'],
                               'y': self.parent.markers['low_res'][region_index]['y']},
                  }
        return region

    def overlay_stack_of_images_clicked(self):
        region1 = self.get_marker_index_parameters(region_index='1')
        region2 = self.get_marker_index_parameters(region_index='2')

        x_2_h = region2['high_res']['x']
        x_1_h = region1['high_res']['x']
        y_2_h = region2['high_res']['y']
        y_1_h = region1['high_res']['y']
        distance_h = np.sqrt(np.power(x_2_h - x_1_h, 2) + np.power(y_2_h - y_1_h, 2))

        x_2_l = region2['low_res']['x']
        x_1_l = region1['low_res']['x']
        y_2_l = region2['low_res']['y']
        y_1_l = region1['low_res']['y']
        distance_l = np.sqrt(np.power(x_2_l - x_1_l, 2) + np.power(y_2_l - y_1_l, 2))

        scaling_factor = distance_h / distance_l
        self.parent.ui.scaling_factor_lineEdit.setText("{:.2f}".format(scaling_factor))

        [image_height, image_width] = np.shape(self.parent.o_norm_low_res.data['sample']['data'][0])
        new_image_height = np.int(image_height * scaling_factor)
        new_image_width = np.int(image_width * scaling_factor)

        self.parent.eventProgress.setMaximum(len(self.parent.o_norm_high_res.data['sample']['data']))
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)
        QtGui.QGuiApplication.processEvents()

        # resize low resolution images
        # position the high resolution image inside
        x_2_l_scaled = x_2_l * scaling_factor
        x_1_l_scaled = x_1_l * scaling_factor
        y_2_l_scaled = y_2_l * scaling_factor
        y_1_l_scaled = y_1_l * scaling_factor

        x_1_h = region1['high_res']['x']
        y_1_h = region1['high_res']['y']

        x_index_array_resized_array = np.int(x_1_l * scaling_factor - x_1_h)
        y_index_array_resized_array = np.int(y_1_l * scaling_factor - y_1_h)
        self.parent.ui.xoffset_lineEdit.setText(str(x_index_array_resized_array))
        self.parent.ui.yoffset_lineEdit.setText(str(y_index_array_resized_array))

        resize_and_overlay_images = []
        high_res_images = self.parent.o_norm_high_res.data['sample']['data']
        for _row, _low_res_image in enumerate(self.parent.o_norm_low_res.data['sample']['data']):
            new_image = np.array(Image.fromarray(_low_res_image).resize((new_image_width, new_image_height)))
            if _row == 0:
                self.parent.rescaled_low_res_height, self.parent.rescaled_low_res_width = np.shape(new_image)

            # add high resolution image
            new_image[y_index_array_resized_array: y_index_array_resized_array + image_height,
            x_index_array_resized_array: x_index_array_resized_array + image_width] = high_res_images[_row]
            resize_and_overlay_images.append(new_image)
            self.parent.eventProgress.setValue(_row+1)
            QtGui.QGuiApplication.processEvents()

        self.parent.resize_and_overlay_images = resize_and_overlay_images
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()

        self.parent.update_overlay_preview(row_selected=row_selected)
        self.parent.ui.tabWidget.setTabEnabled(1, True)
        self.parent.eventProgress.setVisible(False)

        message = "Overlay created using a scaling factor of {:.2f}!".format(scaling_factor)
        self.parent.ui.statusbar.showMessage(message, 10000)  # 10s
        self.parent.ui.statusbar.setStyleSheet("color: green")

    def check_offset_manual_button_status(self):
        self.check_xoffset_manual_button_status()


    def check_xoffset_manual_button_status(self):
        status_minus_button = True
        status_minus_minus_button = True
        status_plus_button = True
        status_plus_plus_button = True

        xoffset_value = np.int(str(self.parent.ui.xoffset_lineEdit.text()))
        if xoffset_value == 0:
            status_minus_button = False
            status_minus_minus_button = False
        elif xoffset_value < self.parent.DOUBLE_OFFSET:
            status_minus_minus_button = False
        elif xoffset_value == (self.parent.rescaled_low_res_width - self.parent.high_res_image_width):
            status_plus_button = False
            status_plus_plus_button = False
        elif xoffset_value > (self.parent.rescaled_low_res_width -
                              self.parent.high_res_image_width - self.parent.DOUBLE_OFFSET)):
            status_plus_plus_button = False

