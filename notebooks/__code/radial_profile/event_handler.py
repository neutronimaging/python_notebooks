from __code._utilities.parent import Parent


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

    def guide_color_changed(self, index):
        red = self.parent.ui.guide_red_slider.value()
        green = self.parent.ui.guide_green_slider.value()
        blue = self.parent.ui.guide_blue_slider.value()
        alpha = self.parent.ui.guide_alpha_slider.value()
        self.parent.guide_color_slider['red'] = red
        self.parent.guide_color_slider['green'] = green
        self.parent.guide_color_slider['blue'] = blue
        self.parent.guide_color_slider['alpha'] = alpha
        self.parent.circle_center_changed()

        self.parent.ui.image_view.removeItem(self.parent.line_view_binning)
        self.parent.display_grid()