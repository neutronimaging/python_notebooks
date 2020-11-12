import copy


class TOFEventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def tab_changed(self, new_tab_index=-1):
        if new_tab_index == 1:
            self.parent.coarse_alignment_table_combobox_changed()

    def update_working_images(self):
        if self.parent.ui.raw_image_radioButton.isChecked():
            coarse_images_dictionary = copy.deepcopy(self.parent.integrated_images)
        else:
            coarse_images_dictionary = copy.deepcopy(self.parent.best_contrast_images)

        self.parent.coarse_images_dictionary = coarse_images_dictionary
