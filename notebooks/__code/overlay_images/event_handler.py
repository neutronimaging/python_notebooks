import numpy as np


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

