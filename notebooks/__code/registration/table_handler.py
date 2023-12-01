from qtpy.QtWidgets import QTableWidgetSelectionRange

from __code.registration.event_handler import EventHandler
from __code.registration.display import Display
from __code.registration.check import Check
from __code.registration.marker_handler import MarkerHandler
from __code.registration.get import Get


class TableHandler:
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def table_row_clicked(self, row=-1):
        self.parent.ui.file_slider.blockSignals(True)
        if row == -1:
            row = self.parent.ui.tableWidget.currentRow()
        else:
            self.parent.ui.file_slider.setValue(row)

        o_event = EventHandler(parent=self.parent)

        o_event.modified_images(list_row=[row])

        o_display = Display(parent=self.parent)
        o_display.image()

        # self.parent.check_selection_slider_status()

        o_event.profile_line_moved()

        # self.parent.check_selection_slider_status()

        o_check = Check(parent=self.parent)
        o_check.status_next_prev_image_button()
        o_check.registration_tool_widgets()
        o_check.selection_slider_status()

        o_marker = MarkerHandler(parent=self.parent)
        o_marker.display_markers(all=True)

        self.parent.ui.file_slider.blockSignals(False)

    def select_row_in_table(self, row=0, user_selected_row=True):

        if not user_selected_row:
            self.parent.ui.tableWidget.blockSignals(True)

        nbr_col = self.parent.ui.tableWidget.columnCount()
        nbr_row = self.parent.ui.tableWidget.rowCount()

        # clear previous selection
        full_range = QTableWidgetSelectionRange(0, 0, nbr_row-1, nbr_col-1)
        self.parent.ui.tableWidget.setRangeSelected(full_range, False)

        # select file of interest
        selection_range = QTableWidgetSelectionRange(row, 0, row, nbr_col-1)
        self.parent.ui.tableWidget.setRangeSelected(selection_range, True)

        self.parent.ui.tableWidget.showRow(row)

        if not user_selected_row:
            self.parent.ui.tableWidget.blockSignals(False)

    def change_slider(self, offset=+1):
        self.parent.ui.file_slider.blockSignals(True)

        current_slider_value = self.ui.file_slider.value()

        new_row_selected = current_slider_value + offset

        self.select_row_in_table(row=new_row_selected, user_selected_row=False)
        self.parent.ui.file_slider.setValue(new_row_selected)

        o_check = Check(parent=self.parent)
        o_check.status_next_prev_image_button()

        o_display = Display(parent=self.parent)
        o_display.image()

        o_event = EventHandler(parent=self.parent)
        o_event.profile_line_moved()

        self.parent.ui.file_slider.blockSignals(False)

    def table_cell_modified(self, row=-1, column=-1):
        o_get = Get(parent=self.parent)
        list_row_selected = o_get.list_row_selected()
        o_event = EventHandler(parent=self.parent)
        o_event.modified_images(list_row=list_row_selected)

        o_display = Display(parent=self.parent)
        o_display.image()

        o_event.profile_line_moved()
