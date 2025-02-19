import numpy as np


class Check:

    def __init__(self, parent=None):
        self.parent = parent

    def status_next_prev_image_button(self):
        """this will enable or not the prev or next button placed next to the slider file image"""
        current_slider_value = self.parent.ui.file_slider.value()
        min_slider_value = self.parent.ui.file_slider.minimum()
        max_slider_value = self.parent.ui.file_slider.maximum()

        _prev = True
        _next = True

        if current_slider_value == min_slider_value:
            _prev = False
        elif current_slider_value == max_slider_value:
            _next = False

        self.parent.ui.previous_image_button.setEnabled(_prev)
        self.parent.ui.next_image_button.setEnabled(_next)

    def registration_tool_widgets(self):
        """if the registration tool is active, and the reference image is the only row selected,
        disable the widgets"""
        if self.parent.registration_tool_ui:
            self.parent.registration_tool_ui.update_status_widgets()

    def selection_slider_status(self):
        """
        if there is more than one row selected, we need to display the left slider but also
        we need to disable the next, prev buttons and file index slider
        """
        selection = self.parent.ui.tableWidget.selectedRanges()
        if selection:

            list_file_index_widgets = [self.parent.ui.previous_image_button,
                                       self.parent.ui.file_slider,
                                       self.parent.ui.next_image_button]

            top_row = selection[0].topRow()
            bottom_row = selection[0].bottomRow()
            if np.abs(bottom_row - top_row) >= 1:  # show selection images widgets
                self.parent.ui.selection_groupBox.setVisible(True)
                self.parent.ui.top_row_label.setText("Row {}".format(top_row + 1))
                self.parent.ui.bottom_row_label.setText("Row {}".format(bottom_row + 1))
                self.parent.ui.opacity_selection_slider.setMinimum(top_row * 100)
                self.parent.ui.opacity_selection_slider.setMaximum(bottom_row * 100)
                self.parent.ui.opacity_selection_slider.setSliderPosition(top_row * 100)
                _file_index_status = False
            else:
                self.parent.ui.selection_groupBox.setVisible(False)
                _file_index_status = True

            for _widget in list_file_index_widgets:
                _widget.setVisible(_file_index_status)
