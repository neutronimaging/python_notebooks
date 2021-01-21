import numpy as np
import pyqtgraph as pg


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def update_views(self, row_selected=0):

        self.update_view(image_view=self.parent.ui.high_resolution_image_view,
                         histogram_level=self.parent.high_histogram_level,
                         live_image=self.parent.current_high_resolution_live_image,
                         data=self.parent.o_norm_high_res.data['sample']['data'][row_selected])


        self.update_view(image_view=self.parent.ui.low_resolution_image_view,
                         histogram_level=self.parent.low_histogram_level,
                         live_image=self.parent.current_low_resolution_live_image,
                         data=self.parent.o_norm_low_res.data['sample']['data'][row_selected])

    def update_view(self, image_view=None, histogram_level=None, live_image=None, data=None):
        # high resolution
        _high_res_view = image_view.getView()
        _high_res_view_box = _high_res_view.getViewBox()
        _high_state = _high_res_view_box.getState()

        first_update = False
        if histogram_level is None:
            first_update = True
        histo_widget = image_view.getHistogramWidget()
        histogram_level = histo_widget.getLevels()

        _high_res_image = np.transpose(data)
        image_view.setImage(_high_res_image)
        live_image = _high_res_image

        _high_res_view_box.setState(_high_state)
        if not first_update:
            histo_widget.setLevels(histogram_level[0],
                                   histogram_level[1])

    def update_target(self, image_resolution='high_res', target_index='1', image_view=None):

        if not (self.parent.markers[image_resolution][target_index]['target_ui'] is None):
            image_view.removeItem(self.parent.markers[image_resolution][target_index]['target_ui'])

        width = self.parent.markers['width']
        height = self.parent.markers['height']

        pos = []
        adj = []

        x = self.parent.markers['high_res']['1']['x']
        y = self.parent.markers['high_res']['1']['y']
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

        line_color = self.parent.markers['target']['color']
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
