import logging
from qtpy.QtGui import QGuiApplication
import numpy as np
import pyqtgraph as pg
from qtpy import QtGui

from __code._utilities.list_widget import ListWidget
from __code._utilities.status_message import StatusMessageStatus, show_status_message
from __code._utilities.math import mean_square_error


class Statistics:

    def __init__(self, parent=None):
        self.parent = parent

    def full_update(self):
        self.parent.ui.setEnabled(False)
        self.parent.ui.statistics_plot.clear()
        self.update_statistics()
        self.update_list_of_files_listWidget()
        self.parent.ui.statistics_plot.addItem(self.parent.threshold_line)
        self.parent.ui.setEnabled(True)

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
                                            symbolBrush=(255, 0, 0),
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
