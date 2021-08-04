from qtpy.QtGui import QGuiApplication
from qtpy.QtWidgets import QMenu
from qtpy import QtGui
import numpy as np
import logging
import pyqtgraph as pg

from __code._utilities.list_widget import ListWidget
from __code._utilities.status_message import StatusMessageStatus, show_status_message
from __code.extract_evenly_spaced_files.manual_mode_interface_handler import Interface as ManualModeInterface
from __code.extract_evenly_spaced_files.load import load_file
from __code._utilities.math import mean_square_error
from __code.extract_evenly_spaced_files import MAX_STATISTICS_ERROR_ALLOWED


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

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
            _data = load_file(file=_file)
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

        if len(self.parent.basename_list_of_files_that_will_be_extracted) != len(self.parent.full_raw_list_of_files):
            replace_with_action = menu.addAction("Replace with ...")

        action = menu.exec_(QtGui.QCursor.pos())

        if action == remove_action:
            self.remove_this_file_clicked()
        elif action == replace_with_action:
            o_interface = ManualModeInterface(parent=self.parent)

        QtGui.QGuiApplication.processEvents()

    def remove_this_file_clicked(self):
        o_list = ListWidget(ui=self.parent.ui.list_of_files_listWidget)
        index_file_selected = o_list.get_current_row()

        del self.parent.basename_list_of_files_that_will_be_extracted[index_file_selected]
        del self.parent.list_data[index_file_selected]
        self.parent.ui.list_of_files_listWidget.clear()
        self.parent.ui.list_of_files_listWidget.addItems(self.parent.basename_list_of_files_that_will_be_extracted)

        o_list.select_element(row=index_file_selected-1)
        self.update_manual_interface()

    def update_manual_ui(self):
        self.update_manual_interface(update_replace_by_list=False)

    def update_manual_interface(self, update_replace_by_list=True):
        if self.parent.manual_interface_id is None:
            return

        self.parent.manual_interface_id.update_current_image_name()
        if update_replace_by_list:
            self.parent.manual_interface_id.update_replace_by_list()
        self.parent.manual_interface_id.display_before_image()
        self.parent.manual_interface_id.display_after_image()

    def update_statistics(self):
        logging.info(f"Updating statistics ...")
        show_status_message(parent=self.parent,
                            message="Updating statistics ...",
                            status=StatusMessageStatus.working)
        QGuiApplication.processEvents()

        list_data = self.parent.list_data

        list_image_1 = list_data[1:]
        list_image_2 = list_data[0:-1]

        list_err = []
        for image1, image2 in zip(list_image_1, list_image_2):
            err = mean_square_error(image1, image2)
            list_err.append(err)

        self.parent.list_statistics_error_value = list_err
        if self.parent.max_statistics_error_value == -1:
            self.parent.max_statistics_error_value = np.max(list_err)

        self.plot_statistics()

        logging.info(f"Statistics plot done!")
        show_status_message(parent=self.parent,
                            message="Updated statistics!",
                            status=StatusMessageStatus.ready,
                            duration_s=5)
        QGuiApplication.processEvents()

    def plot_statistics(self):
        # self.parent.ui.statistics_plot.clear()
        list_err = self.parent.list_statistics_error_value
        if list_err is None:
            return

        self.parent.ui.statistics_plot.plot(list_err, symbol='o', pen='w')

        o_list = ListWidget(ui=self.parent.ui.list_of_files_listWidget)
        index_file_selected = o_list.get_current_row()
        self.parent.ui.statistics_plot.plot([index_file_selected],
                                            [list_err[index_file_selected]],
                                            pen=(200, 200, 200),
                                            symbolBrush=(255,0,0),
                                            symbolPen='w')


    def init_plot_statistics_threshold(self):
        max_value = self.parent.max_statistics_error_value

        self.parent.threshold_line = pg.InfiniteLine(pos=max_value,
                                                     angle=0,
                                                     label="Max threshold",
                                                     movable=True)
        self.parent.ui.statistics_plot.addItem(self.parent.threshold_line)
        self.parent.threshold_line.sigPositionChanged.connect(
                self.parent.statistics_max_threshold_moved)

    def statistics_max_threshold_moved(self):
        self.parent.max_statistics_error_value = self.parent.threshold_line.value()
        self.update_list_of_files_listWidget()

    def update_list_of_files_listWidget(self):
        list_err = self.parent.list_statistics_error_value
        max_statistics_error_value = self.parent.max_statistics_error_value

        # find where the err is above the threshold
        err_above_threshold = [i for i, x in enumerate(list_err) if x > max_statistics_error_value]

        logging.info(f"index of files with errors above threshold: {err_above_threshold}")

        for _row in np.arange(len(list_err)):
            _item = self.parent.ui.list_of_files_listWidget.item(_row)
            _item.setBackground(QtGui.QColor(255, 255, 255, 0))

        for _row in err_above_threshold:
            _item = self.parent.ui.list_of_files_listWidget.item(_row)
            _item.setBackground(QtGui.QColor(255, 0, 0, 100))
