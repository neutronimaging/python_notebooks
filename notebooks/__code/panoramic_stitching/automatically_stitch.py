import numpy as np
from qtpy import QtGui

from __code.panoramic_stitching.get import Get


class AutomaticallyStitch:

    # get offset values of current group selected
    # collect metadata values for each image and calculate xoffset and yoffset in pixel versus motor value
    # loop through the other groups and calculate xoffset and yoffset using local motor value

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):
        nbr_group = len(self.parent.data_dictionary.keys())
        self.parent.eventProgress.setMaximum(nbr_group-1)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        o_get = Get(parent=self.parent)
        group_selected = o_get.get_combobox_folder_selected()

        # first calculate the long and lift position versus pixel coefficient from the ref. group
        group_reference_offset_dictionary = self.parent.offset_dictionary[group_selected]
        group_reference_data_dictionary = self.parent.data_dictionary[group_selected]
        list_files = group_reference_offset_dictionary.keys()

        list_pixel_vs_motor_long_axis_value = []
        list_pixel_vs_motor_lift_axis_value = []

        for _file_index, _file in enumerate(list_files):
            long_axis_value = group_reference_data_dictionary[_file].metadata['MotLongAxis.RBV']
            lift_axis_value = group_reference_data_dictionary[_file].metadata['MotLiftTable.RBV']

            if _file_index == 0:
                long_axis_reference_value = long_axis_value
                lift_axis_reference_value = lift_axis_value

                list_pixel_vs_motor_long_axis_value.append(0)
                list_pixel_vs_motor_lift_axis_value.append(0)
                continue

            xoffset = group_reference_offset_dictionary[_file]['xoffset']
            yoffset = group_reference_offset_dictionary[_file]['yoffset']

            diff_long_axis = long_axis_value - long_axis_reference_value
            diff_lift_axis = lift_axis_value - lift_axis_reference_value

            if diff_long_axis == 0:
                pixel_vs_motor_long_axis_value = 0
            else:
                pixel_vs_motor_long_axis_value = xoffset / diff_long_axis

            if diff_lift_axis == 0:
                pixel_vs_motor_lift_axis_value = 0
            else:
                pixel_vs_motor_lift_axis_value = yoffset / diff_lift_axis

            list_pixel_vs_motor_long_axis_value.append(pixel_vs_motor_long_axis_value)
            list_pixel_vs_motor_lift_axis_value.append(pixel_vs_motor_lift_axis_value)

        # loop through all the groups and apply correction
        for _group_index, _group in enumerate(self.parent.offset_dictionary.keys()):

            # current group is the reference group
            if _group == group_selected:
                continue

            group_offset_dictionary = self.parent.offset_dictionary[_group]
            data_dictionary = self.parent.data_dictionary[_group]

            list_files = list(self.parent.data_dictionary[_group].keys())
            long_axis_value_image_reference = 0
            lift_axis_value_image_reference = 0

            # get xoffset and yofffset pixel/motor position of each image of reference group
            for _file_index, _file in enumerate(list_files):

                if _file_index == 0:
                    long_axis_value_image_reference = data_dictionary[_file].metadata['MotLongAxis.RBV']
                    lift_axis_value_image_reference = data_dictionary[_file].metadata['MotLiftTable.RBV']
                    continue

                long_axis_value = data_dictionary[_file].metadata['MotLongAxis.RBV'] - long_axis_value_image_reference
                lift_axis_value = data_dictionary[_file].metadata['MotLiftTable.RBV'] - lift_axis_value_image_reference

                xoffset_of_this_file = np.int(long_axis_value * list_pixel_vs_motor_long_axis_value[_file_index])
                yoffset_of_this_file = np.int(lift_axis_value * list_pixel_vs_motor_lift_axis_value[_file_index])

                group_offset_dictionary[_file]['xoffset'] = xoffset_of_this_file
                group_offset_dictionary[_file]['yoffset'] = yoffset_of_this_file

            self.parent.eventProgress.setValue(_group_index+1)
            QtGui.QGuiApplication.processEvents()

        self.parent.eventProgress.setVisible(False)
