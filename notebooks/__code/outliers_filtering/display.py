import numpy as np


class Display:

    def __init__(self, parent=None):
        self.parent = parent

    def raw_image(self, data):
        _view = self.parent.ui.raw_image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        self.parent.state_of_raw = _state

        first_update = False
        if self.parent.raw_histogram_level == []:
            first_update = True
        _histo_widget = self.parent.ui.raw_image_view.getHistogramWidget()
        self.parent.raw_histogram_level = _histo_widget.getLevels()

        _image = np.transpose(data)
        self.parent.ui.raw_image_view.setImage(_image)
        _view_box.setState(_state)

        self.parent.live_raw_image = _image
        self.parent.raw_image_size = np.shape(_image)

        if not first_update:
            _histo_widget.setLevels(self.parent.raw_histogram_level[0],
                                    self.parent.raw_histogram_level[1])

        # histogram
        self.parent.ui.raw_histogram_plot.clear()
        min = 0
        max = np.max(_image)
        y, x = np.histogram(_image, bins=np.linspace(min, max+1, self.parent.nbr_histo_bins))
        self.parent.ui.raw_histogram_plot.plot(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 150))

    def filtered_image(self, data):
        _view = self.parent.ui.filtered_image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        self.parent.state_of_raw = _state

        first_update = False
        if self.parent.raw_histogram_level == []:
            first_update = True
        _histo_widget = self.parent.ui.filtered_image_view.getHistogramWidget()
        self.parent.raw_histogram_level = _histo_widget.getLevels()

        _image = np.transpose(data)
        self.parent.ui.filtered_image_view.setImage(_image)
        # _view_box.setState(_state)

        self.parent.live_filtered_image = _image

        if not first_update:
            _histo_widget.setLevels(self.parent.raw_histogram_level[0],
                                    self.parent.raw_histogram_level[1])

        # histogram
        self.parent.ui.filtered_histogram_plot.clear()
        min = 0
        max = np.max(_image)
        y, x = np.histogram(_image, bins=np.linspace(min, max + 1, self.parent.nbr_histo_bins))
        self.parent.ui.filtered_histogram_plot.plot(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 150))
