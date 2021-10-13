from skimage import transform
import numpy as np
import pyqtgraph as pg

from .get import Get


class DisplayImages:

    def __init__(self, parent=None, recalculate_image=False):
        self.parent = parent
        self.recalculate_image = recalculate_image

        self.images()
        # self.display_grid()

    def get_image_selected(self, recalculate_image=False):
        slider_index = self.parent.ui.file_slider.value()
        if recalculate_image:
            angle = self.parent.rotation_angle
            # rotate all images
            self.parent.data_dict['data'] = [transform.rotate(_image, angle) for _image in self.parent.data_dict_raw['data']]

        _image = self.parent.data_dict['data'][slider_index]
        return _image

    def images(self):
        _image = self.get_image_selected(recalculate_image=self.recalculate_image)
        _view = self.parent.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

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


class DisplayScalePyqtUi:

    def __init__(self, parent=None):
        self.parent = parent

    def run(self, view=None, save_it=True):

        if view is None:
            view = self.parent.ui.image_view

            try:
                if view:
                    pass
            except:
                return

        if self.parent.scale_pyqt_ui:
            view.removeItem(self.parent.scale_pyqt_ui)
            view.removeItem(self.parent.scale_legend_pyqt_ui)

        if not self.parent.ui.scale_checkbox.isChecked():
            return

        # scale
        thickness = self.parent.ui.scale_thickness.value()
        size = self.parent.ui.scale_size_spinbox.value()

        pos = []
        adj = []

        x0 = self.parent.ui.scale_position_x.value()
        y0 = self.parent.ui.scale_position_y.maximum() - self.parent.ui.scale_position_y.value()

        one_edge = [x0, y0]
        if self.parent.ui.scale_horizontal_orientation.isChecked():
            other_edge = [x0+size, y0]
            angle = 0
            legend_x0 = x0
            legend_y0 = y0
        else:
            other_edge = [x0, y0 + size]
            angle = 90
            legend_x0 = x0
            legend_y0 = y0 + int(size)

        pos.append(one_edge)
        pos.append(other_edge)
        adj.append([0, 1])

        pos = np.array(pos)
        adj = np.array(adj)

        o_get = Get(parent=self.parent)
        line_color = np.array(o_get.color(color_type='rgba', source='scale'))
        line_color[4] = thickness
        list_line_color = list(line_color)
        line_color = tuple(list_line_color)
        lines = np.array([line_color for n in np.arange(len(pos))],
                         dtype=[('red', np.ubyte), ('green', np.ubyte),
                                ('blue', np.ubyte), ('alpha', np.ubyte),
                                ('width', float)])

        scale = pg.GraphItem()
        view.addItem(scale)

        scale.setData(pos=pos,
                      adj=adj,
                      pen=lines,
                      symbol=None,
                      pxMod=False)

        if save_it:
            self.parent.scale_pyqt_ui = scale

        # legend
        o_get = Get(parent=self.parent)
        legend = o_get.scale_legend()
        color = o_get.color(source='scale', color_type='html')
        text = pg.TextItem(html='<div style="text-align=center"><span style="color: ' + color + ';">' + \
                                legend + '</span></div>',
                           angle=angle)
        view.addItem(text)

        text.setPos(legend_x0, legend_y0)
        if save_it:
            self.parent.scale_legend_pyqt_ui = text


class DisplayMetadataPyqtUi:

    def __init__(self, parent=None):
        self.parent = parent

    def run(self, view=None, save_it=True):

        if view is None:
            view = self.parent.ui.image_view

        try:
            if view:
                pass
        except:
            return

        if self.parent.metadata_pyqt_ui:
            view.removeItem(self.parent.metadata_pyqt_ui)

        if self.parent.graph_pyqt_ui:
            view.removeItem(self.parent.graph_pyqt_ui)

        if not self.parent.ui.metadata_checkbox.isChecked():
            return

        font_size = self.parent.ui.font_size_slider.value()
        x0 = self.parent.ui.metadata_position_x.value()
        y0 = self.parent.ui.metadata_position_y.maximum() - self.parent.ui.metadata_position_y.value()
        o_get = Get(parent=self.parent)
        metadata_text = o_get.metadata_text()
        color = o_get.color(source='metadata', color_type='html')

        text = pg.TextItem(html='<div style="text-align:center"> ' +
                                '<font size="' + str(font_size) + '"> ' +
                                '<span style="color: ' + color + '"' +
                                '>' + metadata_text + '</span></div>')

        view.addItem(text)
        text.setPos(x0, y0)
        if save_it:
            self.parent.metadata_pyqt_ui = text

        graph_font_size = self.parent.ui.graph_font_size_slider.value()
        if self.parent.ui.enable_graph_checkbox.isChecked():

            o_get = Get(parent=self.parent)
            data = o_get.metadata_column()
            _view_box = pg.ViewBox(enableMouse=False)
            # _view_box.setBackgroundColor((100, 100, 100, 100))
            graph = pg.PlotItem(viewBox=_view_box)

            units = self.parent.ui.manual_metadata_units.text()
            if units:
                y_axis_label = '<html><font color="{}" size="{}">{} ({})</font></html>'.format(color,
                                                                                               graph_font_size,
                                                                                               self.parent.ui.manual_metadata_name.text(),
                                                                                               units)
            else:
                y_axis_label = '<html><font color="{}" size="{}">{}</font></html>'.format(color,
                                                                                          graph_font_size,
                                                                                          self.parent.ui.manual_metadata_name.text())

            x_axis_label = '<p><font color="{}" size="{}">File Index</font></p>'.format(color, graph_font_size)

            graph.setLabel('left', text=y_axis_label)
            graph.setLabel('bottom', text=x_axis_label)

            _size = self.parent.ui.metadata_graph_size_slider.value()
            graph.setFixedWidth(_size)
            graph.setFixedHeight(_size)
            o_get = Get(parent=self.parent)
            color_pen = o_get.color(source='graph', color_type='rgb_color')
            graph.plot(data, pen=color_pen)

            # highlight current file
            current_index = self.parent.ui.file_slider.value()
            _pen = pg.mkPen((255, 0, 0), width=4)

            graph.plot(x=[current_index], y=[data[current_index]],
                       pen=_pen,
                       symboBrush=(255, 0, 0),
                       symbolPen='w')
            _inf_line = pg.InfiniteLine(current_index, pen=_pen)
            graph.addItem(_inf_line)

            x0 = self.parent.ui.graph_position_x.value()
            y0 = self.parent.ui.graph_position_y.maximum() - self.parent.ui.graph_position_y.value()

            view.addItem(graph)
            graph.setPos(x0, y0)

            if save_it:
                self.parent.graph_pyqt_ui = graph
