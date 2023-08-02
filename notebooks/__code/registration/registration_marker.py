from qtpy.QtWidgets import QDialog, QApplication
from qtpy import QtGui, QtCore
from qtpy.QtWidgets import QTableWidget, QTableWidgetItem, QMenu, QApplication
import os
import numpy as np

from __code import load_ui
from __code._utilities.table_handler import TableHandler
from __code.registration.marker_default_settings import MarkerDefaultSettings

TABLE_NBR_COLUMNS = 4


class RegistrationMarkersLauncher:

    parent = None

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.registration_markers_ui == None:
            markers_ui = RegistrationMarkers(parent=parent)
            markers_ui.show()
            self.parent.registration_markers_ui = markers_ui
            self.parent.registration_markers_ui.init_widgets()
            #self.parent.display_markers(all=True)
        else:
            self.parent.registration_markers_ui.activateWindow()
            self.parent.registration_markers_ui.setFocus()


class RegistrationMarkers(QDialog):
    """dialog ui that will allow to add or remove markers
    This UI will also allow to change the color of the marker and to change
    their position linearly when selecting 2 of them (gradual increase between the 2)
    """

    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)
        self.parent = parent

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_registration_markers.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.nbr_files = len(self.parent.data_dict['file_name'])

    def tab_changed(self, tab_index):
        self.cell_clicked(str(tab_index+1))

    def resizing_column(self, index_column, old_size, new_size):
        """let's collect the size of the column in the current tab and then
        resize all the other columns of the other table"""

        _current_tab = self.ui.tabWidget.currentIndex()
        _tab_title = self.ui.tabWidget.tabText(_current_tab)

        _live_table_ui = self.parent.markers_table[_tab_title]['ui']
        nbr_column = _live_table_ui.columnCount()
        table_column_width = []
        for _col in np.arange(nbr_column):
            _width = _live_table_ui.columnWidth(_col)
            table_column_width.append(_width)

        self.parent.markers_table_column_width = table_column_width

        for _key in self.parent.markers_table.keys():
            _table_ui = self.parent.markers_table[_key]['ui']
            if not (_table_ui == _live_table_ui):
                for _col, _size in enumerate(self.parent.markers_table_column_width):
                    _table_ui.setColumnWidth(_col, self.parent.markers_table_column_width[_col])

    def init_widgets(self):
        if self.parent.markers_table == {}:
            self.add_marker_button_clicked()
        else:
            self.populate_using_markers_table()

    def update_markers_table_entry(self, marker_name='1', file=''):
        markers = self.parent.markers_table[marker_name]['data'][file]
        table_ui = self.parent.markers_table[marker_name]['ui']
        nbr_row = table_ui.rowCount()
        table_ui.blockSignals(True)

        x = str(markers['x'])
        y = str(markers['y'])

        for _row in np.arange(nbr_row):
            _file_name_of_row = str(table_ui.item(_row, 0).text())
            if _file_name_of_row == file:
                table_ui.item(_row, 1).setText(x)
                table_ui.item(_row, 2).setText(y)
                table_ui.item(_row, 3).setText("")

        table_ui.blockSignals(False)

    def populate_using_markers_table(self):
        for _key_tab_name in self.parent.markers_table:

            _table = QTableWidget(self.nbr_files, TABLE_NBR_COLUMNS)
            _table.setHorizontalHeaderLabels(["File Name", "X", "Y", "Status"])
            _table.setAlternatingRowColors(True)
            _table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            _table.customContextMenuRequested.connect(self.table_right_click)

            for _col, _size in enumerate(self.parent.markers_table_column_width):
                _table.setColumnWidth(_col, self.parent.markers_table_column_width[_col])

            _table.horizontalHeader().sectionResized.connect(self.resizing_column)
            _table.cellClicked.connect(lambda row=0, column=0, tab_index=_key_tab_name: self.table_row_clicked(
                    row, column, tab_index))
            _table.itemSelectionChanged.connect(lambda key_tab_name=_key_tab_name:
                                                self.cell_clicked(key_tab_name=_key_tab_name))

            _data_dict = self.parent.markers_table[_key_tab_name]['data']
            for _row, _file in enumerate(self.parent.data_dict['file_name']):
                _short_file = os.path.basename(_file)
                x = _data_dict[_short_file]['x']
                y = _data_dict[_short_file]['y']
                self.__populate_table_row(_table, _row, _short_file, x, y)

            _table.itemChanged.connect(self.table_cell_modified)
            self.parent.markers_table[_key_tab_name]['ui'] = _table
            _ = self.ui.tabWidget.addTab(_table, _key_tab_name)
            self.parent.display_markers(all=False)

    def get_current_active_tab(self):
        tab_index = self.ui.tabWidget.currentIndex()
        key_tab_name = str(tab_index + 1)
        return key_tab_name

    def get_row_selected_of_current_active_tab(self):
        key_tab_name = self.get_current_active_tab()
        table_ui = self.parent.markers_table[key_tab_name]['ui']
        o_table = TableHandler(table_ui=table_ui)
        row_selected = o_table.get_row_selected()
        return row_selected

    def cell_clicked(self, key_tab_name):
        """
        activate the same row in the main table
        """
        if self.parent.markers_table.get(key_tab_name, None):
            table_ui = self.parent.markers_table[key_tab_name]['ui']
            o_table = TableHandler(table_ui=table_ui)
            row_selected = o_table.get_row_selected()

            main_table_ui = self.parent.tableWidget
            o_main_table = TableHandler(table_ui=main_table_ui)
            o_main_table.select_rows(list_of_rows=[row_selected])
            self.parent.table_row_clicked()

    def table_row_clicked(self, row, column, tab_index):
        print(f"table row clicked: {row =}, {column =} and {tab_index =}")

    def __populate_table_row(self, table_ui, row, file, x, y):
        # file name
        _item = QTableWidgetItem(file)
        table_ui.setItem(row, 0, _item)
        _item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

        # x
        _item = QTableWidgetItem(str(x))
        table_ui.setItem(row, 1, _item)

        # y
        _item = QTableWidgetItem(str(y))
        table_ui.setItem(row, 2, _item)

        # status
        _item = QTableWidgetItem(str(""))
        table_ui.setItem(row, 3, _item)

    def get_marker_name(self):
        markers_table = self.parent.markers_table
        keys = markers_table.keys()
        _marker_name = "1"
        if keys is None:
            return _marker_name

        while True:
            if _marker_name in markers_table:
                _marker_name = str(int(_marker_name)+1)
            else:
                return _marker_name

    def save_column_size(self):
        # using first table
        for _key in self.parent.markers_table.keys():
            _table_ui = self.parent.markers_table[_key]['ui']
            nbr_column = _table_ui.columnCount()
            table_column_width = []
            for _col in np.arange(nbr_column):
                _width = _table_ui.columnWidth(_col)
                table_column_width.append(_width)
            break
            self.parent.markers_table_column_width = table_column_width

    def save_current_table(self):
        _current_tab = self.ui.tabWidget.currentIndex()
        _tab_title = self.ui.tabWidget.tabText(_current_tab)

        # retrieve master markers dictionary
        markers_table = self.parent.markers_table
        # current table ui
        table_ui = markers_table[_tab_title]['ui']
        table_data = markers_table[_tab_title]['data']

        nbr_row = table_ui.rowCount()
        for _row in np.arange(nbr_row):
            file_name = str(table_ui.item(_row, 0).text())
            x = int(str(table_ui.item(_row, 1).text()))
            y = int(str(table_ui.item(_row, 2).text()))

            table_data[file_name]['x'] = x
            table_data[file_name]['y'] = y

        markers_table[_tab_title]['data'] = table_data
        self.parent.markers_table = markers_table

    def get_current_marker_name(self):
        _current_tab = self.ui.tabWidget.currentIndex()
        _tab_title = self.ui.tabWidget.tabText(_current_tab)
        return _tab_title

    def get_current_table_ui(self):
        _current_tab = self.ui.tabWidget.currentIndex()
        _tab_title = self.ui.tabWidget.tabText(_current_tab)
        markers_table = self.parent.markers_table
        table_ui = markers_table[_tab_title]['ui']
        return table_ui

    def copy_cell(self, row_selected=-1, column_selected=-1):
        table_ui = self.get_current_table_ui()
        cell_value = str(table_ui.item(row_selected, column_selected).text())
        self.parent.marker_table_buffer_cell = cell_value

    def paste_cell(self, top_row_selected=-1, bottom_row_selected=-1, column_selected=-1):
        cell_contain_to_copy = self.parent.marker_table_buffer_cell
        table_ui = self.get_current_table_ui()
        markers_table = self.parent.markers_table
        marker_name = self.get_current_marker_name()
        if column_selected == 1:
            marker_axis = 'x'
        else:
            marker_axis = 'y'
        for _row in np.arange(top_row_selected, bottom_row_selected+1):
            _file = str(table_ui.item(_row, 0).text())
            markers_table[marker_name]['data'][_file][marker_axis] = cell_contain_to_copy
            table_ui.item(_row, column_selected).setText(str(cell_contain_to_copy))

        self.parent.markers_table = markers_table

    def get_columns_selected(self):
        """return the left and right columns selected"""
        table_ui = self.get_current_table_ui()
        table_selection = table_ui.selectedRanges()
        if table_selection == []:
            return [-1, -1]

        table_selection = table_selection[0]
        left_column_selected = table_selection.leftColumn()
        right_column_selected = table_selection.rightColumn()
        return [left_column_selected, right_column_selected]

    def get_rows_selected(self):
        """return the top and the bottom rows selected"""
        table_ui = self.get_current_table_ui()
        table_selection = table_ui.selectedRanges()
        if table_selection == []:
            return [-1, -1]

        table_selection = table_selection[0]
        top_row_selected = table_selection.topRow()
        bottom_row_selected = table_selection.bottomRow()
        return [top_row_selected, bottom_row_selected]

    # Event handler =================================

    def table_right_click(self, position):
        """display context menu when user click the x or y column of the marker table.
        also do not allow to copy when more than 1 column and 1 row have been selected"""

        [left_column_selected, right_column_selected] = self.get_columns_selected()
        # if left_column_selected == 0:
        #     return

        if left_column_selected == -1:
            # no selection
            return

        # elif (right_column_selected - left_column_selected) > 0:
        #     return

        [top_row_selected, bottom_row_selected] = self.get_rows_selected()
        if top_row_selected == -1:
            # no selection
            return

        # initialize actions
        copy_cell = None
        paste_cell = None

        menu = QMenu(self)
        if left_column_selected in [1, 2]:

            if bottom_row_selected == top_row_selected:
                copy_cell = menu.addAction("Copy")

            if not (self.parent.marker_table_buffer_cell is None):
                paste_cell = menu.addAction("Paste")

            menu.addSeparator()

        self.start_marker = menu.addAction("Set marker interpolation initial position")
        self.end_marker = menu.addAction("Set marker interpolation final position and process intermediate markers")

        if self.parent.markers_initial_position['row'] is None:
            self.end_marker.setEnabled(False)
        else:
            self.end_marker.setEnabled(True)

        action = menu.exec_(QtGui.QCursor.pos())

        if action == copy_cell:
            self.copy_cell(row_selected=top_row_selected,
                           column_selected=left_column_selected)

        elif action == paste_cell:
            self.paste_cell(top_row_selected=top_row_selected,
                            bottom_row_selected=bottom_row_selected,
                            column_selected=left_column_selected)

        elif action == self.start_marker:
            self.start_marker_initialized()

        elif action == self.end_marker:
            self.end_marker_initialized()

    def start_marker_initialized(self):
        row_selected = self.get_row_selected_of_current_active_tab()
        tab_selected = self.get_current_active_tab()
        self.parent.markers_initial_position['row'] = row_selected
        self.parent.markers_initial_position['tab_name'] = tab_selected
        o_table = TableHandler(table_ui=self.parent.markers_table[tab_selected]['ui'])
        o_table.set_item_with_str(row=row_selected, column=3, cell_str="Interpolation starting position")

    def end_marker_initialized(self):
        tab_selected = self.get_current_active_tab()
        o_table = TableHandler(table_ui=self.parent.markers_table[tab_selected]['ui'])
        from_row = self.parent.markers_initial_position['row']
        to_row = o_table.get_row_selected()

        starting_row_selected = self.parent.markers_initial_position['row']
        o_table.set_item_with_str(row=starting_row_selected,
                                  column=3,
                                  cell_str="")

        xoffset_from = int(o_table.get_item_str_from_cell(row=from_row,
                                                          column=1))
        yoffset_from = int(o_table.get_item_str_from_cell(row=from_row,
                                                          column=2))

        xoffset_to = int(o_table.get_item_str_from_cell(row=to_row,
                                                        column=1))
        yoffset_to = int(o_table.get_item_str_from_cell(row=to_row,
                                                        column=2))

        nbr_rows_between = np.abs(to_row - from_row) - 1
        if nbr_rows_between >= 1:

            delta_xoffset = (xoffset_to - xoffset_from) / (nbr_rows_between + 1)
            delta_yoffset = (yoffset_to - yoffset_from) / (nbr_rows_between + 1)

            coeff = 1
            for _row in np.arange(from_row+1, to_row):
                xoffset_value = int(np.round(xoffset_from + coeff * delta_xoffset))
                o_table.set_item_with_str(row=_row,
                                          column=1,
                                          cell_str=str(xoffset_value))

                yoffset_value = int(np.round(yoffset_from + coeff * delta_yoffset))
                o_table.set_item_with_str(row=_row,
                                          column=2,
                                          cell_str=str(yoffset_value))
                coeff += 1

        self.parent.markers_initial_position['row'] = None
        self.save_current_table()

    def remove_marker_button_clicked(self):
        _current_tab = self.ui.tabWidget.currentIndex()
        _tab_title = self.ui.tabWidget.tabText(_current_tab)

        self.parent.markers_table.pop(_tab_title)
        self.ui.tabWidget.removeTab(_current_tab)
        self.parent.close_all_markers()
        self.parent.display_markers(all=True)

    def get_current_selected_color(self):
        color = self.ui.marker_color_widget.currentText()
        return (MarkerDefaultSettings.color[color], color)

    def add_marker_button_clicked(self):
        table = QTableWidget(self.nbr_files, TABLE_NBR_COLUMNS)
        table.setHorizontalHeaderLabels(["File Name", "X", "Y"])
        table.setAlternatingRowColors(True)
        table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.table_right_click)

        #table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # QtCore.QObject.connect(_table, QtCore.SIGNAL(_fromUtf8("customContextMenuRequested(QPoint)")),
        #                        self.table_right_click)

        for _col, _size in enumerate(self.parent.markers_table_column_width):
            table.setColumnWidth(_col, self.parent.markers_table_column_width[_col])

        table.horizontalHeader().sectionResized.connect(self.resizing_column)
        table.horizontalHeader().setStretchLastSection(True)
        new_marker_name = self.get_marker_name()
        _ = self.ui.tabWidget.addTab(table, new_marker_name)

        _marker_dict = {}
        _marker_dict['ui'] = table

        (_qpen, _color_name) = self.get_current_selected_color()
        _marker_dict['color'] = {}
        _marker_dict['color']['qpen'] = _qpen
        _marker_dict['color']['name'] = _color_name

        _data_dict = {}
        for _row, _file in enumerate(self.parent.data_dict['file_name']):
            _short_file = os.path.basename(_file)
            x = self.parent.o_MarkerDefaultSettings.x
            y = self.parent.o_MarkerDefaultSettings.y
            self.__populate_table_row(table, _row, _short_file, x, y)
            _data_dict[_short_file] = {'x': x, 'y': y, 'marker_ui': None, 'label_ui': None}

        _marker_dict['data'] = _data_dict

        # activate last index
        number_of_tabs = self.ui.tabWidget.count()
        self.ui.tabWidget.setCurrentIndex(number_of_tabs - 1)
        table.itemChanged.connect(self.table_cell_modified)
        table.itemSelectionChanged.connect(lambda key_tab_name=new_marker_name:
                                                self.cell_clicked(key_tab_name=new_marker_name))
        self.parent.markers_table[new_marker_name] = _marker_dict
        self.parent.display_markers(all=False)

    def marker_color_changed(self, color):
        _current_tab = self.ui.tabWidget.currentIndex()
        _tab_title = self.ui.tabWidget.tabText(_current_tab)
        new_color = MarkerDefaultSettings.color[color]
        self.parent.markers_table[_tab_title]['color']['qpen'] = new_color
        self.parent.markers_table[_tab_title]['color']['name'] = color
        self.parent.display_markers_of_tab(marker_name=_tab_title)

    def table_cell_modified(self):
        self.save_current_table()
        self.parent.display_markers(all=False)

    def marker_tab_changed(self, tab_index):
        # first time, markers_table is still empty
        try:
            self.parent.markers_table[str(tab_index+1)]
            color = self.parent.markers_table[str(tab_index+1)]['color']['name']
            index_color = self.ui.marker_color_widget.findText(color)
            self.ui.marker_color_widget.setCurrentIndex(index_color)
            self.parent.display_markers()
        except KeyError:
            pass

    def run_registration_button_clicked(self):
        step = 1
        self.parent.eventProgress.setMinimum(1)
        self.parent.eventProgress.setMaximum(8)
        self.parent.eventProgress.setValue(step)
        self.parent.eventProgress.setVisible(True)
        QApplication.processEvents()

        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        markers_table = self.parent.markers_table

        # init dictionary
        markers_list = {}
        step += 1
        self.parent.eventProgress.setValue(step)
        for _marker in markers_table.keys():
            _list_files = markers_table[_marker]['data']
            for _file in _list_files:
                markers_list[_file] = {'x': [], 'y': []}
            break

        # calculate mean marker Position for all images

        step += 1
        self.parent.eventProgress.setValue(step)
        QApplication.processEvents()
        for _marker in markers_table.keys():
            _list_files = markers_table[_marker]['data']
            for _file in _list_files:
                markers_list[_file]['x'].append(markers_table[_marker]['data'][_file]['x'])
                markers_list[_file]['y'].append(markers_table[_marker]['data'][_file]['y'])

        step += 1
        self.parent.eventProgress.setValue(step)
        QApplication.processEvents()
        for _file in markers_list.keys():
            markers_list[_file]['mean_x'] = np.mean(markers_list[_file]['x'])
            markers_list[_file]['mean_y'] = np.mean(markers_list[_file]['y'])

        # calculate ref_x and ref_y (position of mean x and mean y of reference image)
        ref_x = markers_list[self.parent.reference_image_short_name]['mean_x']
        ref_y = markers_list[self.parent.reference_image_short_name]['mean_y']

        # calculate for all the other files, the x and y offset to apply and fill the master
        # table automatically
        step += 1
        self.parent.eventProgress.setValue(step)
        QApplication.processEvents()
        for _index, _file in enumerate(self.parent.data_dict['file_name']):
            _short_file = os.path.basename(_file)

            mean_x = markers_list[_short_file]['mean_x']
            x_offset = ref_x - mean_x

            mean_y = markers_list[_short_file]['mean_y']
            y_offset = ref_y - mean_y

            self.parent.ui.tableWidget.item(_index, 1).setText(str(x_offset))
            self.parent.ui.tableWidget.item(_index, 2).setText(str(y_offset))

        step += 1
        self.parent.eventProgress.setValue(step)
        QApplication.processEvents()
        self.parent.modified_images(all_row=True)

        step += 1
        self.parent.eventProgress.setValue(step)
        QApplication.processEvents()
        self.parent.display_image()

        step += 1
        self.parent.eventProgress.setValue(step)
        QApplication.processEvents()
        self.parent.profile_line_moved()

        QApplication.restoreOverrideCursor()
        self.parent.eventProgress.setVisible(False)

    def closeEvent(self, c):
        self.save_column_size()
        self.parent.close_all_markers()
        self.parent.set_widget_status(list_ui=[self.parent.ui.auto_registration_button],
                           enabled=True)
        self.parent.registration_markers_ui = None
