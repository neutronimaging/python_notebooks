import numpy as np
import pyqtgraph as pg
from qtpy.QtGui import QPen, QColor

COLOR_CONTOUR = QColor(255, 0, 0, 100)


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
        self.display_chip_border(chip_index=new_index)

    def display_chip_border(self, chip_index=0):
        if self.parent.contour_id:
            self.parent.setup_image_view.removeItem(self.parent.contour_id)

        image_height = self.parent.image_size.height
        image_width = self.parent.image_size.width

        contour_width = np.int(image_width / 2)
        contour_height = np.int(image_height / 2)
        if chip_index == 0:
            x0, y0 = 0, 0
        elif chip_index == 1:
            x0 = np.int(image_width/2)
            y0 = 0
        elif chip_index == 2:
            x0 = 0
            y0 = np.int(image_height/2)
        else:
            x0 = np.int(image_width/2)
            y0 = np.int(image_height/2)

        _pen = QPen()
        _pen.setColor(COLOR_CONTOUR)
        _pen.setWidthF(0.01)
        _roi_id = pg.ROI([x0, y0],
                         [contour_width, contour_height],
                         pen=_pen,
                         scaleSnap=True,
                         movable=False)

        self.parent.setup_image_view.addItem(_roi_id)
        self.parent.contour_id = _roi_id
