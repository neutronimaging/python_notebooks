import numpy as np

from __code._utilities.table_handler import TableHandler
from __code.panoramic_stitching.get import Get

COLOR_WORKING_ROW = 'red'
COLOR_NONE_WORKING_ROW = 'black'


class Profile:

    def __init__(self, parent=None):
        self.parent = parent

    def horizontal_profile_changed(self):
        roi_id = self.parent.horizontal_profile['id']
        horizontal_roi_dimensions = Profile.get_x_y_width_height_of_roi(roi_id=roi_id)
        self.plot_profile(x=horizontal_roi_dimensions['x'],
                          y=horizontal_roi_dimensions['y'],
                          width=horizontal_roi_dimensions['width'],
                          height=horizontal_roi_dimensions['height'],
                          profile_type='horizontal')

    def vertical_profile_changed(self):
        roi_id = self.parent.vertical_profile['id']
        vertical_roi_dimensions = Profile.get_x_y_width_height_of_roi(roi_id=roi_id)
        self.plot_profile(x=vertical_roi_dimensions['x'],
                          y=vertical_roi_dimensions['y'],
                          width=vertical_roi_dimensions['width'],
                          height=vertical_roi_dimensions['height'],
                          profile_type='vertical')

    def plot_profile(self, x=None, y=None, width=None, height=None, profile_type='horizontal'):
        if profile_type == 'horizontal':
            plot_ui = self.parent.horizontal_profile_plot
            dim_to_keep = 0
        else:
            plot_ui = self.parent.vertical_profile_plot
            dim_to_keep = 1
        plot_ui.axes.cla()

        o_get = Get(parent=self.parent)
        folder_selected = o_get.get_combobox_folder_selected()

        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()

        data_dictionary = self.parent.data_dictionary[folder_selected]
        offset_dictionary = self.parent.offset_dictionary[folder_selected]

        image_height = self.parent.image_height
        image_width = self.parent.image_width

        for _file_index, _file in enumerate(data_dictionary.keys()):

            # no need to display profile if image is not visible
            if not offset_dictionary[_file]['visible']:
                continue

            if row_selected == _file_index:
                color = COLOR_WORKING_ROW
            else:
                color = COLOR_NONE_WORKING_ROW

            left_of_image = offset_dictionary[_file]['xoffset']
            top_of_image = offset_dictionary[_file]['yoffset']

            # image is on the right of profile
            if left_of_image > (x + width):
                continue

            # image is on the left of profile
            if (left_of_image + image_width) < x:
                continue

            # image is above profile
            if (top_of_image + image_height) < y:
                continue

            # image is below profile
            if top_of_image > (y + height):
                continue

            # find part of profile that is inside image
            x_left_for_profile = np.max([x, left_of_image]) - left_of_image
            x_right_for_profile = np.min([x + width, left_of_image + image_width]) - left_of_image

            y_top_for_profile = np.max([y, top_of_image]) - top_of_image
            y_bottom_for_profile = np.min([y + height, top_of_image + image_height]) - top_of_image

            x_axis_of_profile = np.arange(x_left_for_profile, x_right_for_profile) + left_of_image
            y_axis_of_profile = data_dictionary[_file].data[
                                y_top_for_profile:y_bottom_for_profile,
                                x_left_for_profile:x_right_for_profile,
                                ]

            y_axis = np.mean(y_axis_of_profile, axis=dim_to_keep)
            #
            plot_ui.axes.plot(x_axis_of_profile, y_axis, color=color)
            # plot_ui.axes.set_xlabel("Pixel")
            # plot_ui.axes.set_ylabel("Average counts")

        plot_ui.draw()

    @staticmethod
    def get_x_y_width_height_of_roi(roi_id=None):
        x, y = roi_id.pos()
        width, height = roi_id.size()
        return {'x'     : np.int(x),
                'y'     : np.int(y),
                'width' : np.int(width),
                'height': np.int(height)}
