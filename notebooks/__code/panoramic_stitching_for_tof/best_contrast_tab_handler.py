import numpy as np


class BestContrastTabHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def display_selected_folder(self):
        folder_name = self.parent.ui.list_folders_combobox.currentText()
        image = self.parent.integrated_images[folder_name].data

        _view = self.parent.ui.image_view_best_contrast.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.parent.histogram_level_best_contrast is None:
            first_update = True
        _histo_widget = self.parent.ui.image_view_best_contrast.getHistogramWidget()
        self.parent.histogram_level_best_contrast = _histo_widget.getLevels()

        _image = np.transpose(image)
        self.parent.ui.image_view_best_contrast.setImage(_image)
        self.parent.current_live_image_best_contrast = _image
        # _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.parent.histogram_level_best_contrast[0],
                                    self.parent.histogram_level_best_contrast[1])
