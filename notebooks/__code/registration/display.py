import numpy as np

from __code.registration.get import Get


class Display:

    def __init__(self, parent=None):
        self.parent = parent

    def image(self):

        o_get = Get(parent=self.parent)

        # if more than one row selected !
        if self.parent.ui.selection_groupBox.isVisible():
            # if all selected
            if self.parent.ui.selection_all.isChecked():
                _image = o_get.image_selected()
            else:  # display selected images according to slider position

                # retrieve slider infos
                slider_index = self.parent.ui.opacity_selection_slider.sliderPosition() / 100

                from_index = int(slider_index)
                to_index = int(slider_index + 1)

                if from_index == slider_index:
                    _image = self.parent.data_dict['data'][from_index]
                else:
                    _from_image = self.parent.data_dict['data'][from_index]

                    _to_image = self.parent.data_dict['data'][to_index]

                    _from_coefficient = np.abs(to_index - slider_index)
                    _to_coefficient = np.abs(slider_index - from_index)
                    _image = _from_image * _from_coefficient + _to_image * _to_coefficient

        else:  # only 1 row selected
            _image = o_get.image_selected()

        if _image is None:  # display only reference image
            self.display_only_reference_image()
            return

        self.parent.ui.selection_reference_opacity_groupBox.setVisible(True)

        _view = self.parent.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.parent.histogram_level is None:
            first_update = True
        _histo_widget = self.parent.ui.image_view.getHistogramWidget()
        self.parent.histogram_level = _histo_widget.getLevels()

        _opacity_coefficient = self.parent.ui.opacity_slider.value()  # betwween 0 and 100
        _opacity_image = _opacity_coefficient / 100.
        _image = np.transpose(_image) * _opacity_image

        _opacity_selected = 1 - _opacity_image
        _reference_image = np.transpose(self.parent.reference_image) * _opacity_selected

        _final_image = _reference_image + _image
        self.parent.ui.image_view.setImage(_final_image)
        self.parent.live_image = _final_image
        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.parent.histogram_level[0],
                                    self.parent.histogram_level[1])

    def display_only_reference_image(self):

        self.parent.ui.selection_reference_opacity_groupBox.setVisible(False)

        _view = self.parent.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.parent.histogram_level is None:
            first_update = True
        _histo_widget = self.parent.ui.image_view.getHistogramWidget()
        self.parent.histogram_level = _histo_widget.getLevels()

        _image = np.transpose(self.parent.reference_image)
        self.parent.ui.image_view.setImage(_image)
        self.parent.live_image = _image
        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.parent.histogram_level[0], self.parent.histogram_level[1])