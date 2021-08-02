from qtpy.QtGui import QGuiApplication
import numpy as np

from NeuNorm.normalization import Normalization

from __code._utilities.list_widget import ListWidget


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def load_files(self):
        list_files = self.parent.list_of_files_that_will_be_extracted
        nbr_files = len(list_files)

        self.parent.eventProgress.setMaximum(nbr_files-1)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        list_data = list()

        for _index, _file in enumerate(list_files):

            o_norm = Normalization()
            o_norm.load(file=_file, notebook=False)
            _data = o_norm.data['sample']['data']
            list_data.append(_data)

            self.parent.eventProgress.setValue(_index+1)
            QGuiApplication.processEvents()

        self.parent.list_data = list_data
        self.parent.eventProgress.setVisible(False)
    QGuiApplication.processEvents()

    def select_first_file(self):
        o_list = ListWidget(ui=self.parent.ui.list_of_files_listWidget)
        o_list.select_element(row=0)

    def image_selected_changed(self):
        o_list = ListWidget(ui=self.parent.ui.list_of_files_listWidget)
        index_file_selected = o_list.get_current_row()
        data = self.parent.list_data[index_file_selected]
        self.parent.ui.image_view.setImage(np.transpose(data))
