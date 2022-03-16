from qtpy.QtWidgets import QApplication
import numpy as np
from pathlib import Path

from NeuNorm.normalization import Normalization

from __code._utilities.metadata_handler import MetadataHandler


class Load:

    def __init__(self, parent=None):
        self.parent = parent

    def data(self):
        list_of_images = self.parent.list_of_images
        file_extension = Path(list_of_images[0]).suffix[1:]

        data_dict = {}
        acquisition_time_of_first_image = -1

        self.parent.eventProgress.setMaximum(len(list_of_images))
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        for _index, _file in enumerate(list_of_images):
            o_norm = Normalization()
            o_norm.load(file=_file,
                        auto_gamma_filter=False,
                        manual_gamma_filter=False)
            data = np.squeeze(o_norm.data['sample']['data'][0])
            time_stamp = MetadataHandler.get_time_stamp(file_name=_file, ext=file_extension)
            if acquisition_time_of_first_image == -1:
                acquisition_time_of_first_image = time_stamp
                time_stamp = 0
            else:
                time_stamp -= acquisition_time_of_first_image

            data_dict[_index] = {'data': data,
                                 'time_offset': time_stamp}

            self.parent.eventProgress.setValue(_index)
            QApplication.processEvents()

        self.parent.data_dict = data_dict
        self.parent.eventProgress.setVisible(False)
        QApplication.processEvents()
