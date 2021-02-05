import numpy as np
import pyqtgraph as pg
from PIL import Image
from qtpy import QtGui
import copy

from __code._utilities.table_handler import TableHandler
from __code.overlay_images.get import Get


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
        image_view = self.parent.image_view['overlay']
        histogram_level = self.parent.histogram_level['overlay']

        _res_view = image_view.getView()
        _res_view_box = _res_view.getViewBox()
        _state = _res_view_box.getState()

        first_update = False
        if histogram_level is None:
            first_update = True
        histo_widget = image_view.getHistogramWidget()
        histogram_level = histo_widget.getLevels()
        self.parent.histogram_level['overlay'] = histogram_level

        # _image = np.transpose(self.parent.resize_and_overlay_images[row_selected])

        hres_image = self.parent.resize_hres_lres_images['hres'][row_selected]
        lres_image = self.parent.resize_hres_lres_images['lres'][row_selected]
        # [image_height, image_width] = np.shape(self.parent.o_norm_low_res.data['sample']['data'][0])

        if self.parent.ui.transparency_checkBox.isChecked():
            transparency = np.float(self.parent.transparency) / 100
            image = transparency * hres_image + (1 - transparency) * lres_image
        else:
            image = self.parent.resize_and_overlay_images[row_selected]

        image = np.transpose(image)

        self.parent.image_view['overlay'].setImage(image)
        self.parent.current_live_image['overlay'] = image

        _res_view_box.setState(_state)
        if not first_update:
            histo_widget.setLevels(histogram_level[0],
                                   histogram_level[1])

    def update_view(self, image_resolution='high_res', data=None):

        image_view = self.parent.image_view[image_resolution]
        histogram_level = self.parent.histogram_level[image_resolution]

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

    def update_profile_markers_and_target(self, with_profile=False):
        image_view = self.parent.image_view['overlay']

        if with_profile:

            if not (self.parent.markers['overlay']['1']['target_ui'] is None):
                image_view.removeItem(self.parent.markers['overlay']['1']['target_ui'])

            width = self.parent.markers['width']
            height = self.parent.markers['height']
            length = self.parent.markers['overlay']['1']['length']

            if self.parent.markers['overlay']['1']['ui']:
                image_view.addItem(self.parent.markers['overlay']['1']['ui'])

            else:
                x = self.parent.markers['overlay']['1']['x']
                y = self.parent.markers['overlay']['1']['y']
                image_view = self.parent.image_view['overlay']

                pen = QtGui.QPen()
                pen.setColor(QtGui.QColor(255, 0, 255, 255))
                pen.setWidthF(0.05)

                ui = pg.ROI([x, y], [width, height], scaleSnap=True, pen=pen)
                image_view.addItem(ui)
                ui.sigRegionChanged.connect(self.parent.profile_region_moved)

                self.parent.markers['overlay']['1']['ui'] = ui

            pos = []
            adj = []

            x = self.parent.markers['overlay']['1']['x']
            y = self.parent.markers['overlay']['1']['y']
            # target_length = self.parent.markers['target']['length']
            # target_border = self.parent.markers['target']['border']

            pos.append([np.int(x + width / 2), y - length - np.int(height/2)])
            pos.append([np.int(x + width / 2), y + length + np.int(height/2)])
            adj.append([0, 1])

            pos.append([x - length - np.int(width/2), np.int(y + height / 2)])
            pos.append([x + length + np.int(width/2), np.int(y + height / 2)])
            adj.append([2, 3])

            pos = np.array(pos)
            adj = np.array(adj)

            line_color = self.parent.markers['target']['color']['vertical']
            lines = np.array([line_color for _ in np.arange(len(adj))],
                             dtype=[('red', np.ubyte), ('green', np.ubyte),
                                    ('blue', np.ubyte), ('alpha', np.ubyte),
                                    ('width', float)])
            lines[0] = self.parent.markers['target']['color']['horizontal']

            line_view_binning = pg.GraphItem()
            image_view.addItem(line_view_binning)
            line_view_binning.setData(pos=pos,
                                      adj=adj,
                                      pen=lines,
                                      symbol=None,
                                      pxMode=False)
            self.parent.markers['overlay']['1']['target_ui'] = line_view_binning
        else:
            if self.parent.markers['overlay']['1']['target_ui']:
                image_view.removeItem(self.parent.markers['overlay']['1']['ui'])
                image_view.removeItem(self.parent.markers['overlay']['1']['target_ui'])

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
        resize_and_overlay_modes = []
        high_res_images = self.parent.o_norm_high_res.data['sample']['data']

        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)

        resize_hres_images = []
        resize_lres_images = []

        for _row, _low_res_image in enumerate(self.parent.o_norm_low_res.data['sample']['data']):
            new_image = np.array(Image.fromarray(_low_res_image).resize((new_image_width, new_image_height)))
            resize_lres_images.append(copy.deepcopy(new_image))

            high_res_image = self.get_full_high_res_image(high_res_images[_row],
                                                          image_height, image_width,
                                                          new_image_height, new_image_width,
                                                          x_index_array_resized_array,
                                                          y_index_array_resized_array)
            resize_hres_images.append(high_res_image)

            if _row == 0:
                self.parent.rescaled_low_res_height, self.parent.rescaled_low_res_width = np.shape(new_image)
            resize_and_overlay_modes.append("Auto")
            o_table.set_item_with_str(row=_row, column=2, cell_str="Auto")

            # add high resolution image
            new_working_image = copy.deepcopy(new_image)
            new_working_image[y_index_array_resized_array: y_index_array_resized_array + image_height,
            x_index_array_resized_array: x_index_array_resized_array + image_width] = high_res_images[_row]

            resize_and_overlay_images.append(new_working_image)
            self.parent.eventProgress.setValue(_row+1)
            QtGui.QGuiApplication.processEvents()

        self.parent.resize_hres_lres_images = {'lres': resize_lres_images,
                                               'hres': resize_hres_images}

        self.parent.resize_and_overlay_images = resize_and_overlay_images
        self.parent.resize_and_overlay_modes = resize_and_overlay_modes

        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()

        self.parent.update_overlay_preview(row_selected=row_selected)
        self.parent.ui.tabWidget.setTabEnabled(1, True)
        self.parent.eventProgress.setVisible(False)
        self.check_offset_manual_button_status()

        message = "Overlay created using a scaling factor of {:.2f}!".format(scaling_factor)
        self.parent.ui.statusbar.showMessage(message, 10000)  # 10s
        self.parent.ui.statusbar.setStyleSheet("color: green")

    def manual_overlay_of_selected_image_only(self):
        scaling_factor = np.float(str(self.parent.ui.scaling_factor_lineEdit.text()))

        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()
        self.parent.resize_and_overlay_modes[row_selected] = "Manual"
        o_table.set_item_with_str(row=row_selected, column=2, cell_str="Manual")

        [image_height, image_width] = np.shape(self.parent.o_norm_low_res.data['sample']['data'][0])
        new_image_height = np.int(image_height * scaling_factor)
        new_image_width = np.int(image_width * scaling_factor)
        x_index_array_resized_array = np.int(str(self.parent.ui.xoffset_lineEdit.text()))
        y_index_array_resized_array = np.int(str(self.parent.ui.yoffset_lineEdit.text()))

        resize_and_overlay_images = self.parent.resize_and_overlay_images
        _high_res_image = self.parent.o_norm_high_res.data['sample']['data'][row_selected]
        _low_res_image = self.parent.o_norm_low_res.data['sample']['data'][row_selected]
        new_image = np.array(Image.fromarray(_low_res_image).resize((new_image_width, new_image_height)))
        # self.parent.rescaled_low_res_height, self.parent.rescaled_low_res_width = np.shape(new_image)

        self.parent.resize_hres_lres_images['hres'][row_selected] = copy.deepcopy(new_image)
        high_res_image = self.get_full_high_res_image(_high_res_image, image_height, image_width, new_image_height,
                                                      new_image_width, x_index_array_resized_array,
                                                      y_index_array_resized_array)
        self.parent.resize_hres_lres_images['lres'][row_selected] = high_res_image

        # image for none transparency mode
        new_working_image = copy.deepcopy(new_image)
        new_working_image[y_index_array_resized_array: y_index_array_resized_array + image_height,
            x_index_array_resized_array: x_index_array_resized_array + image_width] = _high_res_image
        resize_and_overlay_images[row_selected] = new_working_image
        QtGui.QGuiApplication.processEvents()

        self.parent.resize_and_overlay_images = resize_and_overlay_images
        self.parent.update_overlay_preview(row_selected=row_selected)

    def get_full_high_res_image(self, _high_res_image,
                                image_height, image_width,
                                new_image_height, new_image_width,
                                x_index_array_resized_array,
                                y_index_array_resized_array):
        high_res_image = np.ones((new_image_height, new_image_width))
        high_res_image[y_index_array_resized_array: y_index_array_resized_array + image_height,
        x_index_array_resized_array: x_index_array_resized_array + image_width] = \
            _high_res_image
        return high_res_image

    def manual_overlay_stack_of_images_clicked(self):
        scaling_factor = np.float(str(self.parent.ui.scaling_factor_lineEdit.text()))

        [image_height, image_width] = np.shape(self.parent.o_norm_low_res.data['sample']['data'][0])
        new_image_height = np.int(image_height * scaling_factor)
        new_image_width = np.int(image_width * scaling_factor)

        self.parent.eventProgress.setMaximum(len(self.parent.o_norm_high_res.data['sample']['data']))
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)
        QtGui.QGuiApplication.processEvents()

        x_index_array_resized_array = np.int(str(self.parent.ui.xoffset_lineEdit.text()))
        y_index_array_resized_array = np.int(str(self.parent.ui.yoffset_lineEdit.text()))

        resize_and_overlay_images = []
        resize_and_overlay_modes = []
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)

        resize_hres_images = []
        resize_lres_images = []

        high_res_images = self.parent.o_norm_high_res.data['sample']['data']
        for _row, _low_res_image in enumerate(self.parent.o_norm_low_res.data['sample']['data']):
            new_image = np.array(Image.fromarray(_low_res_image).resize((new_image_width, new_image_height)))

            resize_lres_images.append(copy.deepcopy(new_image))
            if _row == 0:
                self.parent.rescaled_low_res_height, self.parent.rescaled_low_res_width = np.shape(new_image)
            resize_and_overlay_modes.append("Manual")
            o_table.set_item_with_str(row=_row, column=2, cell_str="Manual")

            high_res_image = self.get_full_high_res_image(high_res_images[_row],
                                                          image_height,
                                                          image_width,
                                                          new_image_height,
                                                          new_image_width,
                                                          x_index_array_resized_array,
                                                          y_index_array_resized_array)
            resize_hres_images.append(high_res_image)

            # add high resolution image
            new_working_image = copy.deepcopy(new_image)
            new_working_image[y_index_array_resized_array: y_index_array_resized_array + image_height,
                      x_index_array_resized_array: x_index_array_resized_array + image_width] = high_res_images[_row]
            resize_and_overlay_images.append(new_working_image)
            self.parent.eventProgress.setValue(_row+1)
            QtGui.QGuiApplication.processEvents()

        self.parent.resize_and_overlay_images = resize_and_overlay_images
        self.parent.resize_and_overlay_modes = resize_and_overlay_modes

        self.parent.resize_hres_lres_images = {'lres': resize_lres_images,
                                               'hres': resize_hres_images}

        row_selected = o_table.get_row_selected()

        self.parent.update_overlay_preview(row_selected=row_selected)
        self.parent.ui.tabWidget.setTabEnabled(1, True)
        self.parent.eventProgress.setVisible(False)

        message = "Overlay created using manual settings!".format(scaling_factor)
        self.parent.ui.statusbar.showMessage(message, 10000)  # 10s
        self.parent.ui.statusbar.setStyleSheet("color: green")

    def check_offset_manual_button_status(self):
        self.check_xoffset_manual_button_status()
        self.check_yoffset_manual_button_status()

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
                              self.parent.high_res_image_width - self.parent.DOUBLE_OFFSET):
            status_plus_plus_button = False

        self.parent.ui.xoffset_minus_minus_pushButton.setEnabled(status_minus_minus_button)
        self.parent.ui.xoffset_minus_pushButton.setEnabled(status_minus_button)
        self.parent.ui.xoffset_plus_pushButton.setEnabled(status_plus_button)
        self.parent.ui.xoffset_plus_plus_pushButton.setEnabled(status_plus_plus_button)

    def check_yoffset_manual_button_status(self):
        status_minus_button = True
        status_minus_minus_button = True
        status_plus_button = True
        status_plus_plus_button = True

        yoffset_value = np.int(str(self.parent.ui.yoffset_lineEdit.text()))
        if yoffset_value == 0:
            status_minus_button = False
            status_minus_minus_button = False
        elif yoffset_value < self.parent.DOUBLE_OFFSET:
            status_minus_minus_button = False
        elif yoffset_value == (self.parent.rescaled_low_res_height - self.parent.high_res_image_height):
            status_plus_button = False
            status_plus_plus_button = False
        elif yoffset_value > (self.parent.rescaled_low_res_height -
                              self.parent.high_res_image_height - self.parent.DOUBLE_OFFSET):
            status_plus_plus_button = False

        self.parent.ui.yoffset_minus_minus_pushButton.setEnabled(status_minus_minus_button)
        self.parent.ui.yoffset_minus_pushButton.setEnabled(status_minus_button)
        self.parent.ui.yoffset_plus_pushButton.setEnabled(status_plus_button)
        self.parent.ui.yoffset_plus_plus_pushButton.setEnabled(status_plus_plus_button)

    def update_profile_plots(self):
        _with_profile = self.parent.ui.profile_tool_checkBox.isChecked()
        if not _with_profile:
            return

        o_get = Get(parent=self.parent)
        overlay_1_dict = o_get.marker_location(image_resolution='overlay', target_index='1')

        width = self.parent.markers['width']
        height = self.parent.markers['height']
        length = self.parent.markers['overlay']['1']['length']

        center_x = overlay_1_dict['x'] + np.int(width/2)
        center_y = overlay_1_dict['y'] + np.int(height/2)

        # scaling_factor = np.float(str(self.parent.ui.scaling_factor_lineEdit.text()))
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()

        # [image_height, image_width] = np.shape(self.parent.o_norm_low_res.data['sample']['data'][0])
        # new_image_height = np.int(image_height * scaling_factor)
        # new_image_width = np.int(image_width * scaling_factor)

        # _high_res_image = self.parent.o_norm_high_res.data['sample']['data'][row_selected]
        # _low_res_image = self.parent.o_norm_low_res.data['sample']['data'][row_selected]

        x_index_array_resized_array = np.int(str(self.parent.ui.xoffset_lineEdit.text()))
        y_index_array_resized_array = np.int(str(self.parent.ui.yoffset_lineEdit.text()))

        # low_res_image = self.parent.np.array(Image.fromarray(_low_res_image).resize((new_image_width,
        #                                                                              new_image_height)))
        low_res_image = self.parent.resize_hres_lres_images['lres'][row_selected]
        high_res_image = self.parent.resize_hres_lres_images['hres'][row_selected]

        # high_res_image = np.ones((new_image_height, new_image_width))
        # high_res_image[y_index_array_resized_array: y_index_array_resized_array + image_height,
        #                x_index_array_resized_array: x_index_array_resized_array + image_width] = _high_res_image

        # horizontal profile
        from_x = center_x - length
        to_x = center_x + length
        horizontal_profile_low_res = low_res_image[center_y, from_x:to_x]
        horizontal_profile_high_res = high_res_image[center_y, from_x:to_x]
        x_axis = np.arange(from_x, to_x)

        self.parent.horizontal_profile_plot.axes.clear()
        self.parent.horizontal_profile_plot.draw()
        self.parent.horizontal_profile_plot.axes.plot(x_axis, horizontal_profile_high_res,
                                                      '-b', label='high resolution')
        self.parent.horizontal_profile_plot.axes.plot(x_axis, horizontal_profile_low_res,
                                                      '--b', label='low resolution')
        self.parent.horizontal_profile_plot.axes.legend()
        self.parent.horizontal_profile_plot.draw()

        # vertical profile
        from_y = center_y - length
        to_y = center_y + length
        vertical_profile_low_res = low_res_image[from_y:to_y, center_x]
        vertical_profile_high_res = high_res_image[from_y:to_y, center_x]
        y_axis = np.arange(from_y, to_y)

        self.parent.vertical_profile_plot.axes.clear()
        self.parent.vertical_profile_plot.draw()
        self.parent.vertical_profile_plot.axes.plot(y_axis, vertical_profile_high_res,
                                                    '-r', label='high resolution')
        self.parent.vertical_profile_plot.axes.plot(y_axis, vertical_profile_low_res,
                                                    '--r', label='low resolution')
        self.parent.vertical_profile_plot.axes.legend()
        self.parent.vertical_profile_plot.draw()

    def transparency_widgets_status(self):
        transparency_checkbox_status = self.parent.ui.transparency_checkBox.isChecked()
        list_ui = [self.parent.ui.low_resolution_label,
                   self.parent.ui.high_resolution_label,
                   self.parent.ui.transparency_slider]
        for _ui in list_ui:
            _ui.setEnabled(transparency_checkbox_status)

    def save_overlay_parameters(self):
        sf = str(self.parent.ui.scaling_factor_lineEdit.text())
        xoffset = str(self.parent.ui.xoffset_lineEdit.text())
        yoffset = str(self.parent.ui.yoffset_lineEdit.text())
        self.parent.parameters_used_on_all_images = {'scaling_factor': sf,
                                                     'xoffset': xoffset,
                                                     'yoffset': yoffset}
        self.parent.ui.export_pushButton.setEnabled(True)

    def check_export_button_status(self):
        export_button_status = self._can_we_enable_export_button()
        self.parent.ui.export_pushButton.setEnabled(export_button_status)

    def _can_we_enable_export_button(self):
        sf = str(self.parent.ui.scaling_factor_lineEdit.text())
        if not (sf == self.parent.parameters_used_on_all_images['scaling_factor']):
            return False
        xoffset = str(self.parent.ui.xoffset_lineEdit.text())
        if not (xoffset == self.parent.parameters_used_on_all_images['xoffset']):
            return False
        yoffset = str(self.parent.ui.yoffset_lineEdit.text())
        if not (yoffset == self.parent.parameters_used_on_all_images['yoffset']):
            return False

        return True
