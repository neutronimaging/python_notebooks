import numpy as np


class Profile:

    def __init__(self, parent=None):
        self.parent = parent

    def horizontal_profile_changed(self):
        roi_id = self.parent.horizontal_profile['id']
        horizontal_roi_dimensions = Profile.get_x_y_width_height_of_roi(roi_id=roi_id)
        profile_to_plot = self.get_profile_to_plot(x=horizontal_roi_dimensions['x'],
                                                   y=horizontal_roi_dimensions['y'],
                                                   width=horizontal_roi_dimensions['width'],
                                                   height=horizontal_roi_dimensions['height'])

    def vertical_profile_changed(self):
        roi_id = self.parent.vertical_profile['id']
        vertical_roi_dimensions = Profile.get_x_y_width_height_of_roi(roi_id=roi_id)
        profile_to_plot = self.get_profile_to_plot(x=vertical_roi_dimensions['x'],
                                                   y=vertical_roi_dimensions['y'],
                                                   width=vertical_roi_dimensions['width'],
                                                   height=vertical_roi_dimensions['height'])


    def get_profile_to_plot(self, x=None, y=None, width=None, height=None, profile_type='horizontal'):
        current_live_image = self.parent.current_live_image
        profile_2d = current_live_image[y: y+height, x: x+width]
        if profile_type == 'horizontal':
            dim_to_keep = 1
        else:
            dim_to_keep = 0
        return np.mean(profile_2d, keepdims=dim_to_keep)

    @staticmethod
    def get_x_y_width_height_of_roi(roi_id=None):
        x, y = roi_id.pos()
        width, height = roi_id.size()
        return {'x'     : np.int(x),
                'y'     : np.int(y),
                'width' : np.int(width),
                'height': np.int(height)}
