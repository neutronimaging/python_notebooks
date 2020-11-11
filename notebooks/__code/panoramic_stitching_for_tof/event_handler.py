from collections import OrderedDict
import copy


class TOFEventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def tab_changed(self, new_tab_index=-1):
        pass

    def update_working_images(self):
        data_dictionary = OrderedDict()
        if self.parent.ui.raw_image_radioButton.isChecked():
            for _folder in self.parent.integrated_images.keys():
                data_dictionary[_folder] = self.parent.integrated_images[_folder]
        else:
            data_dictionary = copy.deepcopy(self.parent.best_contrast_images)

        self.parent.data_dictionary = data_dictionary
