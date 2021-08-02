from qtpy.QtGui import QGuiApplication
import numpy as np
import logging

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

        _view = self.parent.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.parent.histogram_level is None:
            first_update = True
        _histo_widget = self.parent.ui.image_view.getHistogramWidget()
        self.parent.histogram_level = _histo_widget.getLevels()

        self.parent.ui.image_view.setImage(np.transpose(data))
        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.parent.histogram_level[0],
                                    self.parent.histogram_level[1])

    def update_replace_by_list(self):
        logging.info("> update replace by list")
        o_list = ListWidget(ui=self.parent.ui.list_of_files_listWidget)
        full_list_of_files = self.parent.full_raw_list_of_files
        index_file_selected = o_list.get_current_row()
        extracting_value = self.parent.extracting_value
        self.parent.ui.replace_by_comboBox.clear()

        logging.info(f"-> index_file_selected: {index_file_selected}")
        logging.info(f"-> extracting_value: {extracting_value}")
        logging.info(f"-> full_list_of_files: {full_list_of_files}")

        if extracting_value == 1:
            self.parent.ui.replace_by_comboBox.setEnabled(False)
            self.parent.ui.or_label.setEnabled(False)
            return

        index_file_selected_in_full_list = index_file_selected * extracting_value
        logging.info(f"-> index_file_selected_in_full_list: {index_file_selected_in_full_list}")
        if index_file_selected == 0:
            list_of_option_of_files_to_replace_with = \
            full_list_of_files[index_file_selected_in_full_list + 1: index_file_selected_in_full_list + extracting_value]
        elif index_file_selected == (o_list.get_number_elements() - 1):
            list_of_option_of_files_to_replace_with = \
            full_list_of_files[index_file_selected_in_full_list - extracting_value + 1:
                               index_file_selected_in_full_list]
        else:
            list_of_option_of_files_to_replace_with = []
            for _file in full_list_of_files[index_file_selected_in_full_list + 1 - extracting_value:
            index_file_selected_in_full_list]:
                    list_of_option_of_files_to_replace_with.append(_file)

            for _file in full_list_of_files[index_file_selected_in_full_list + 1: index_file_selected_in_full_list +
                                                                     extracting_value]:
                    list_of_option_of_files_to_replace_with.append(_file)

        self.parent.ui.replace_by_comboBox.addItems(list_of_option_of_files_to_replace_with)
