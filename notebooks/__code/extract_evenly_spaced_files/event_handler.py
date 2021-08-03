from qtpy.QtGui import QGuiApplication
from qtpy.QtWidgets import QMenu
from qtpy import QtGui
import numpy as np
import logging
import os
# from PIL import Image
import matplotlib.image as mpimg

from NeuNorm.normalization import Normalization

from __code._utilities.list_widget import ListWidget
from __code._utilities.file import get_file_extension
from __code._utilities.status_message import StatusMessageStatus, show_status_message


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def load_file(self, file=None):
        ext = get_file_extension(filename=file)

        if ext.lower() in ['jpg', 'jpeg']:
            _data = mpimg.imread(file)
            # with Image.open(file) as im:   # BUG that crashes the UI
            #    _data = np.asarray(im.convert('L'))/255.

        else:
            o_norm = Normalization()
            o_norm.load(file=file, notebook=False)
            _data = o_norm.data['sample']['data'][0]

        logging.info(f"np.shape(_data): {np.shape(_data)}")
        return _data

    def load_files(self):
        logging.info("loading files ...")
        show_status_message(parent=self.parent,
                            message="Loading ...",
                            status=StatusMessageStatus.working)
        list_files = self.parent.list_of_files_that_will_be_extracted
        nbr_files = len(list_files)

        self.parent.eventProgress.setMaximum(nbr_files-1)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        list_data = list()
        for _index, _file in enumerate(list_files):
            # logging.info(f"-> loading file: {_file}")
            _data = self.load_file(file=_file)
            list_data.append(_data)

            self.parent.eventProgress.setValue(_index+1)
            QGuiApplication.processEvents()

        self.parent.list_data = list_data
        self.parent.eventProgress.setVisible(False)

        logging.info(f"file loaded! np.shape(list_data): {np.shape(self.parent.list_data)}")
        show_status_message(parent=self.parent,
                            message="Done loading!",
                            status=StatusMessageStatus.ready,
                            duration_s=5)
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

    def list_files_right_click(self):
        menu = QMenu(self.parent)
        remove_action = menu.addAction("Remove")
        replace_with_action = menu.addAction("Replace with ...")

        action = menu.exec_(QtGui.QCursor.pos())

        if action == remove_action:
            pass
        elif action == replace_with_action:
            pass

        QtGui.QGuiApplication.processEvents()

    def update_replace_by_list(self):
        o_list = ListWidget(ui=self.parent.ui.list_of_files_listWidget)
        full_list_of_files = self.parent.full_raw_list_of_files
        index_file_selected = o_list.get_current_row()
        extracting_value = self.parent.extracting_value
        self.parent.ui.replace_by_comboBox.clear()

        if extracting_value == 1:
            self.parent.ui.replace_by_comboBox.setEnabled(False)
            self.parent.ui.or_label.setEnabled(False)
            return

        index_file_selected_in_full_list = index_file_selected * extracting_value
        logging.info(f"-> index_file_selected_in_full_list: {index_file_selected_in_full_list}")
        if index_file_selected == 0:
            list_of_option_of_files_to_replace_with = \
            full_list_of_files[index_file_selected_in_full_list: index_file_selected_in_full_list + extracting_value]
        elif index_file_selected == (o_list.get_number_elements() - 1):
            list_of_option_of_files_to_replace_with = \
            full_list_of_files[index_file_selected_in_full_list - extracting_value:
                               index_file_selected_in_full_list]
        else:
            list_of_option_of_files_to_replace_with = []
            for _file in full_list_of_files[index_file_selected_in_full_list + 1 - extracting_value:
            index_file_selected_in_full_list]:
                    list_of_option_of_files_to_replace_with.append(_file)

            for _file in full_list_of_files[index_file_selected_in_full_list: index_file_selected_in_full_list +
                                                                     extracting_value]:
                    list_of_option_of_files_to_replace_with.append(_file)

        self.parent.ui.replace_by_comboBox.addItems(list_of_option_of_files_to_replace_with)

        # select current file as default (mid point in the list)
        nbr_option = len(list_of_option_of_files_to_replace_with)
        mid_point = int(nbr_option/2)
        self.parent.ui.replace_by_comboBox.setCurrentIndex(mid_point)

    def remove_this_file_clicked(self):
        o_list = ListWidget(ui=self.parent.ui.list_of_files_listWidget)
        index_file_selected = o_list.get_current_row()

        del self.parent.basename_list_of_files_that_will_be_extracted[index_file_selected]
        del self.parent.list_data[index_file_selected]
        self.parent.ui.list_of_files_listWidget.clear()
        self.parent.ui.list_of_files_listWidget.addItems(self.parent.basename_list_of_files_that_will_be_extracted)

        o_list.select_element(row=index_file_selected-1)
        self.update_replace_by_list()

    def replace_by_list_changed(self):
        new_file = self.parent.ui.replace_by_comboBox.currentText()

        new_data = self.load_file(file=new_file)

        o_list = ListWidget(ui=self.parent.ui.list_of_files_listWidget)
        index_file_selected = o_list.get_current_row()
        self.parent.basename_list_of_files_that_will_be_extracted[index_file_selected] = \
            os.path.basename(new_file)

        self.parent.ui.list_of_files_listWidget.clear()
        self.parent.ui.list_of_files_listWidget.addItems(self.parent.basename_list_of_files_that_will_be_extracted)

        self.parent.list_data[index_file_selected] = new_data
        o_list.select_element(row=index_file_selected)

