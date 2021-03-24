import numpy as np


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def display_setup_image(self):
        setup_image = self.parent.o_corrector.integrated_data
        self.parent.setup_live_image = setup_image
        _image = np.transpose(setup_image)
        self.parent.setup_image_view.setImage(_image)

    def chips_index_changed(self):
        new_index = self.parent.ui.index_to_correct_comboBox.currentIndex()
