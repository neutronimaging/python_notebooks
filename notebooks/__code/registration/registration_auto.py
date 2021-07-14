from skimage.feature import register_translation
from qtpy import QtGui


class RegistrationAuto:

    registered_parameters = {}

    def __init__(self, parent=None, reference_image=[], floating_images=[]):
        self.parent = parent
        self.reference_image = reference_image
        self.list_images = floating_images

    def auto_align(self):
        _ref_image = self.reference_image
        _list_images = self.list_images

        nbr_images = len(_list_images)
        self.parent.eventProgress.setMaximum(nbr_images)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        for _row,_image in enumerate(_list_images):
            [yoffset, xoffset], error, diffphase = register_translation(_ref_image,
                                                                        _image)
            if not _row == self.parent.reference_image_index:
                self.parent.set_item(row=_row, col=1, value=xoffset)
                self.parent.set_item(row=_row, col=2, value=yoffset)

            self.parent.eventProgress.setValue(_row+1)
            QtGui.QApplication.processEvents()

        self.parent.eventProgress.setVisible(False)
