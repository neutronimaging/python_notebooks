import numpy as np
from qtpy.QtWidgets import QHBoxLayout, QCheckBox, QLineEdit, QVBoxLayout, QWidget, QLabel

from __code.table_handler import TableHandler


class GuiUtility:
    cell_str_format = "{:.3f}"
    cell_str_format_2 = "{:f}"

    def __init__(self, parent=None):
        self.parent = parent

    def get_tab_selected(self, tab_ui=None):
        tab_index = tab_ui.currentIndex()
        return tab_ui.tabText(tab_index)

    def get_rows_of_table_selected(self, table_ui=None):
        o_table = TableHandler(table_ui=table_ui)
        return o_table.get_rows_of_table_selected()

    def select_rows_of_table(self, table_ui=None, list_of_rows=None):
        if list_of_rows is None:
            return
        o_table = TableHandler(table_ui=table_ui)
        o_table.select_rows(list_of_rows=list_of_rows)

    def get_toolbox_selected(self, toolbox_ui=None):
        toolbox_index = toolbox_ui.currentIndex()
        return toolbox_ui.itemText(toolbox_index)

    def update_kropff_high_lambda_table_ui(self, row=0, a0=None, b0=None, a0_error=None, b0_error=None):
        table_ui = self.parent.ui.high_lda_tableWidget
        table_ui.item(row, 1).setText(self.cell_str_format.format(a0))
        table_ui.item(row, 2).setText(self.cell_str_format.format(b0))
        table_ui.item(row, 3).setText(self.cell_str_format.format(a0_error))
        table_ui.item(row, 4).setText(self.cell_str_format.format(b0_error))

    def update_kropff_low_lambda_table_ui(self, row=0, ahkl=None, bhkl=None, ahkl_error=None, bhkl_error=None):
        table_ui = self.parent.ui.low_lda_tableWidget
        table_ui.item(row, 1).setText(self.cell_str_format.format(ahkl))
        table_ui.item(row, 2).setText(self.cell_str_format.format(bhkl))
        table_ui.item(row, 3).setText(self.cell_str_format.format(ahkl_error))
        table_ui.item(row, 4).setText(self.cell_str_format.format(bhkl_error))

    def update_kropff_bragg_edge_table_ui(self, row=0, ldahkl=None, ldahkl_error=None,
                                          tau=None, tau_error=None,
                                          sigma=None, sigma_error=None):

        ldahkl_error = np.NaN if ldahkl_error is None else ldahkl_error
        tau_error = np.NaN if tau_error is None else tau_error
        sigma_error = np.NaN if sigma_error is None else sigma_error

        table_ui = self.parent.ui.bragg_edge_tableWidget
        table_ui.item(row, 1).setText(self.cell_str_format_2.format(ldahkl))
        table_ui.item(row, 2).setText(self.cell_str_format_2.format(tau))
        table_ui.item(row, 3).setText(self.cell_str_format_2.format(sigma))
        table_ui.item(row, 4).setText(self.cell_str_format_2.format(ldahkl_error))
        table_ui.item(row, 5).setText(self.cell_str_format_2.format(tau_error))
        table_ui.item(row, 6).setText(self.cell_str_format_2.format(sigma_error))

    def check_status_of_kropff_fitting_buttons(self):
        pass

    # enabled_low_lambda_button = False
    # enabled_bragg_peak_button = False
    #
    # # can we enabled the low lambda button
    # if self.parent.fitting_input_dictionary['rois'][0]['fitting']['kropff']['high']['a0']:
    # 	enabled_low_lambda_button = True
    #
    # if self.parent.fitting_input_dictionary['rois'][0]['fitting']['kropff']['low']['ahkl']:
    # 	enabled_bragg_peak_button = True

    def get_kropff_fit_parameter_selected(self, fit_region='high'):
        """
        return the name of the button checked in the requested tab (kropff fit)
        for example: a0 if high lambda and first radioButton checked
        :param fit_region: name of the region ('high', 'low' or 'bragg_peak')
        :return:
        """
        list_fit_parameters_radio_button = {'high'      : {'ui'  : [self.parent.ui.kropff_a0_radioButton,
                                                                    self.parent.ui.kropff_b0_radioButton],
                                                           'name': ['a0', 'b0']},
                                            'low'       : {'ui'  : [self.parent.ui.kropff_ahkl_radioButton,
                                                                    self.parent.ui.kropff_bhkl_radioButton],
                                                           'name': ['ahkl', 'bhkl']},
                                            'bragg_peak': {'ui'  : [self.parent.ui.kropff_lda_hkl_radioButton,
                                                                    self.parent.ui.kropff_tau_radioButton,
                                                                    self.parent.ui.kropff_sigma_radioButton],
                                                           'name': ['ldahkl', 'tau', 'sigma'],
                                                           },
                                            }

        for _index, _ui in enumerate(list_fit_parameters_radio_button[fit_region]['ui']):
            if _ui.isChecked():
                return list_fit_parameters_radio_button[fit_region]['name'][_index]

        return None

    def get_kropff_fit_graph_ui(self, fit_region='high'):
        list_ui = {'high'      : self.parent.kropff_high_plot,
                   'low'       : self.parent.kropff_low_plot,
                   'bragg_peak': self.parent.kropff_bragg_peak_plot}
        return list_ui[fit_region]

    def get_table_str_item(self, table_ui=None, row=0, column=0):
        item = table_ui.item(row, column)
        if item:
            return str(item.text())
        else:
            return ""

    def fill_march_dollase_table(self, list_state=None, initial_parameters=None):

        table_ui = self.parent.ui.march_dollase_user_input_table
        o_table = TableHandler(table_ui=table_ui)
        o_table.remove_all_rows()

        if not list_state:
            return

        march_dollase_row_height = {0      : 110,
                                    'other': 60}

        nbr_column = len(list_state[0])
        for _row in np.arange(len(list_state)):
            self.parent.ui.march_dollase_user_input_table.insertRow(_row)

            row_height = march_dollase_row_height[0] if _row == 0 else march_dollase_row_height['other']
            table_ui.setRowHeight(_row, row_height)

            for _col in np.arange(nbr_column):
                _state_col = list_state[_row][_col]
                _widget = QWidget()
                verti_layout = QVBoxLayout()

                hori_layout = QHBoxLayout()
                _checkbox = QCheckBox()
                _checkbox.setChecked(_state_col)
                _checkbox.stateChanged.connect(lambda state=0, row=_row, column=_col:
                                               self.parent.march_dollase_table_state_changed(state=state,
                                                                                             row=row,
                                                                                             column=column))
                hori_layout.addStretch()
                hori_layout.addWidget(_checkbox)
                hori_layout.addStretch()
                new_widget = QWidget()
                new_widget.setLayout(hori_layout)
                verti_layout.addWidget(new_widget)

                if _row == 0:
                    parameter_key = self.parent.march_dollase_list_columns[_col]

                    if (_col == 1) or (_col == 2):
                        _input = QLineEdit()
                        _input.returnPressed.connect(lambda column=_col:
                                                     self.parent.march_dollase_table_init_value_changed(column=column))
                        _input.setText(str(initial_parameters[parameter_key]))
                        verti_layout.addWidget(_input)
                        _input.setVisible(not _state_col)

                    elif (_col == 0):
                        _label = QLabel()
                        try:
                            str_format = "{:0.6f}".format(float(initial_parameters[parameter_key]))
                        except ValueError:
                            str_format = initial_parameters[parameter_key]

                        _label.setText(str_format)
                        verti_layout.addWidget(_label)
                        _label.setVisible(not _state_col)

                    else:
                        _label = QLabel()
                        _label.setText("Row dependent")
                        verti_layout.addWidget(_label)
                        _label.setVisible(not _state_col)

                _widget.setLayout(verti_layout)
                table_ui.setCellWidget(_row, _col, _widget)

    def set_columns_hidden(self, table_ui=None, list_of_columns=None, state=True):
        for _col in list_of_columns:
            table_ui.setColumnHidden(_col, state)
