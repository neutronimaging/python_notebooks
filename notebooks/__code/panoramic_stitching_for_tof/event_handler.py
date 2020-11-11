from collections import OrderedDict
import copy
import os


class TOFEventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def tab_changed(self, new_tab_index=-1):
        pass

    def update_working_images(self):
        coarse_images_dictionary = OrderedDict()
        if self.parent.ui.raw_image_radioButton.isChecked():
            for _folder in self.parent.integrated_images.keys():
                coarse_images_dictionary[os.path.basename(_folder)] = self.parent.integrated_images[_folder]
        else:
            coarse_images_dictionary = copy.deepcopy(self.parent.best_contrast_images)

        self.parent.coarse_images_dictionary = coarse_images_dictionary
