from __code._utilities.parent import Parent


class EventHandler(Parent):

    def update_prepare_data_plot(self):
        pass

    def prepare_data_file_index_slider_changed(self, slider_value=None):
        if slider_value is None:
            slider_value = self.parent.ui.file_index_horizontalSlider.value()

        self.parent.ui.file_index_value_label.setText(str(slider_value))
