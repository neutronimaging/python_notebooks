import numpy as np


class Display:

    def __init__(self, parent=None):
        self.parent = parent

    def update_image_view(self, slider_value=0):
        data = self.parent.data_dict[slider_value]['data']
        data = np.transpose(data)
        self.parent.ui.image_view.setImage(data)
