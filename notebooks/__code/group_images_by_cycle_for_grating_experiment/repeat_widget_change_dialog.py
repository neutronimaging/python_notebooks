from qtpy.QtWidgets import QMainWindow
from qtpy.QtGui import QIcon
from qtpy import QtCore, QtGui
import os
import numpy as np

from __code import load_ui
from __code.group_images_by_cycle_for_grating_experiment.excel_table_handler import ExcelTableHandler as TableHandler
from __code.group_images_by_cycle_for_grating_experiment import IndexOfColumns


class RepeatWidgetChangeDialog(QMainWindow):

    def __init__(self, parent=None, input_row=0, input_column=0):

        self.grand_parent = parent
        self.input_row = input_row
        self.input_column = input_column
        super(RepeatWidgetChangeDialog, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_grating_excel_widget_dialog.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

        self.init_widgets()

    def init_widgets(self):
        
        statis_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
        self.do_not_repeat_released_file = os.path.join(statis_file_path, "do_not_repeat_button_released.png")
        self.do_not_repeat_pressed_file = os.path.join(statis_file_path, "do_not_repeat_button_pressed.png")
        self.repeat_released_file = os.path.join(statis_file_path, "repeat_button_released.png")
        self.repeat_pressed_file = os.path.join(statis_file_path, "repeat_button_pressed.png")

        no_repeat_icon = QIcon(self.do_not_repeat_released_file)
        self.ui.do_not_repeat_pushButton.setIcon(no_repeat_icon)
        self.ui.do_not_repeat_pushButton.setIconSize(QtCore.QSize(204, 198))

        repeat_icon = QIcon(self.repeat_released_file)
        self.ui.repeat_pushButton.setIcon(repeat_icon)
        self.ui.repeat_pushButton.setIconSize(QtCore.QSize(204, 198))

    def do_not_repeat_pressed(self):
        no_repeat_icon = QIcon(self.do_not_repeat_pressed_file)
        self.ui.do_not_repeat_pushButton.setIcon(no_repeat_icon)
        self.close()

    def do_not_repeat_released(self):
        no_repeat_icon = QIcon(self.do_not_repeat_released_file)
        self.ui.do_not_repeat_pushButton.setIcon(no_repeat_icon)

    def repeat_pressed(self):
        repeat_icon = QIcon(self.repeat_pressed_file)
        self.ui.repeat_pushButton.setIcon(repeat_icon)
        self.repeat_widget_value_in_all_rows()
        self.close()

    def repeat_released(self):
        repeat_icon = QIcon(self.repeat_released_file)
        self.ui.repeat_pushButton.setIcon(repeat_icon)

    def repeat_widget_value_in_all_rows(self):
        input_row = self.input_row
        input_column = self.input_column

        o_table = TableHandler(table_ui=self.grand_parent.ui.tableWidget)
        nbr_row = o_table.row_count()
        o_table.define_row_for_getter(row=input_row)
        if input_column == IndexOfColumns.period:
            widget_value = o_table.get_period()
            for _row in np.arange(nbr_row):
                o_table.define_row_for_setter(_row)
                o_table.set_period(widget_value, new=False)
        elif input_column == IndexOfColumns.images_per_step:
            widget_value = o_table.get_images_per_step()
            for _row in np.arange(nbr_row):
                o_table.define_row_for_setter(_row)
                o_table.set_images_per_step(widget_value, new=False)
        elif input_column == IndexOfColumns.fit_procedure:
            widget_value_index = o_table.get_fit_procedure_index()
            for _row in np.arange(nbr_row):
                o_table.define_row_for_setter(_row)
                o_table.set_fit_procedure(widget_value_index, new=False)
        elif input_column == IndexOfColumns.gamma_filter_data_ob:
            widget_value_index = o_table.get_gamma_filter_data_ob_index()
            for _row in np.arange(nbr_row):
                o_table.define_row_for_setter(_row)
                o_table.set_gamma_filter_data_ob(widget_value_index, new=False)
        elif input_column == IndexOfColumns.gamma_filter_dc:
            widget_value_index = o_table.get_gamma_filter_dc_index()
            for _row in np.arange(nbr_row):
                o_table.define_row_for_setter(_row)
                o_table.set_gamma_filter_dc(widget_value_index, new=False)
        elif input_column == IndexOfColumns.dc_outlier_removal:
            widget_value_index = o_table.get_dc_outlier_removal_index()
            for _row in np.arange(nbr_row):
                o_table.define_row_for_setter(_row)
                o_table.set_dc_outlier_removal(widget_value_index, new=False)
