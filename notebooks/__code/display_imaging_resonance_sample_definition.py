import numpy as np
import os
import numbers

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from __code.ui_resonance_imaging_layers_input import Ui_MainWindow as UiSampleMainWindow
from ImagingReso.resonance import Resonance


class SampleWindow(QMainWindow):
    
    debugging = False
    stack = {} # used to initialize ImagingReso
    
    def __init__(self, parent=None, debugging=False):
        QMainWindow.__init__(self, parent=parent)
        self.ui = UiSampleMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Define Sample Layers")
    
        self.debugging = debugging
        
        self.initialize_ui()
        self.__debugging()
        
    def __debugging(self):
        '''Fill the table for debugging only!'''
        if not self.debugging:
            return
        
        _debug_table = [['Gadnium','Gd','1','0.075','']]

        for _row_index,_row in enumerate(_debug_table):
            for _col_index, _entry in enumerate(_row):
                _item = QtGui.QTableWidgetItem(_entry)
                self.ui.layer_table.setItem(_row_index, _col_index, _item)
        
    def initialize_ui(self):
        self.ui.check_groupBox.setVisible(False)
        
        _column_width = [300, 100, 100, 100, 100]
        for _index, _width in enumerate(_column_width):
            self.ui.layer_table.setColumnWidth(_index, _width)
            self.ui.example_table.setColumnWidth(_index, _width)
            
        _column_width = [80, 90, 90, 100]
        for _index, _width in enumerate(_column_width):
            self.ui.element_table.setColumnWidth(_index, _width)
        
    def validate_table_input_clicked(self):
        # block element table signal
        self.ui.element_table.blockSignals(True)

        # disable top part (no more changes allowed)
        self.ui.layer_groupBox.setEnabled(False)
        
        # collect table input
        nbr_row = self.ui.layer_table.rowCount()
        _table_dictionary = {}
        for _row_index in range(nbr_row):
            _dict = {}
            _layer_name = self.get_table_item(_row_index, 0)
            if _layer_name == '':
                break
            _dict['elements'] = self.format_string_to_array(string=self.get_table_item(_row_index, 1), data_type='str')
            _dict['stoichiometric_ratio'] = self.format_string_to_array(string=self.get_table_item(_row_index, 2), data_type='float')
            _dict['thickness'] = {'value': float(self.get_table_item(_row_index, 3)),
                                  'units': 'mm'}
            if self.get_table_item(_row_index, 4):
                _dict['density'] = {'value': float(self.get_table_item(_row_index, 4)),
                                    'units': 'g/cm3'}
            _table_dictionary[_layer_name] = _dict
        self.stack = _table_dictionary

        E_min = float(str(self.ui.Emin_lineEdit.text()))
        E_max = float(str(self.ui.Emax_lineEdit.text()))
        delta_E = float(str(self.ui.deltaE_lineEdit.text()))

        o_reso = Resonance(stack=self.stack, energy_min=E_min, energy_max=E_max, energy_step=delta_E)
        self.o_reso = o_reso
        
        self.fill_check_groupBox()
        self.ui.check_groupBox.setVisible(True)        
        self.ui.element_table.blockSignals(False)
        self.ui.ok_button.setEnabled(True)
        
    def format_string_to_array(self, string='', data_type='str'):
        _parsed_string = string.split(',')
        result = []
        for _entry in _parsed_string:
            if data_type == 'str':
                result.append(str(_entry))
            elif data_type == 'float':
                result.append(float(_entry))
            else:
                raise ValueError("data_type not supported!")
        return result
    
    def get_table_item(self, row, col):
        _item = self.ui.layer_table.item(row, col)
        if _item is None:
            return ''
        _text = _item.text().strip()
        return _text

    def fill_check_groupBox(self):
        # fill layer's name
        _stack = self.o_reso.stack
        layers_name = list(_stack.keys())
        self.ui.layer_name_combobox.clear()
        self.ui.layer_name_combobox.addItems(layers_name)
        
    def element_combobox_clicked(self, element_selected):
        if element_selected == '':
            return
        
        self.ui.element_table.blockSignals(True)

        layer_selected = self.ui.layer_name_combobox.currentText()
        if layer_selected == '':
            return
        if element_selected == '':
            return
        
        _entry = self.stack[layer_selected][element_selected]
        number_of_atoms = float(self.stack[layer_selected]['atoms_per_cm3'][element_selected])
        self.ui.element_number_of_atoms.setText("{:6.3e}".format(number_of_atoms))
        density = str(self.stack[layer_selected][element_selected]['density']['value'])
        self.ui.element_density.setText("{:6.3e}".format(float(density)))
        molar_mass = str(self.stack[layer_selected][element_selected]['molar_mass']['value'])
        self.ui.element_molar_mass.setText("{:6.3e}".format(float(molar_mass)))
        
        self.fill_isotopes_table(element_selected)
        self.ui.element_table.blockSignals(False)
        
    def fill_isotopes_table(self, element_selected=''):
        self.clear_isotopes_table()
        layer_selected = self.ui.layer_name_combobox.currentText()
        element_selected = self.ui.element_name_combobox.currentText()
        _entry = self.stack[layer_selected][element_selected]['isotopes']
        list_iso = _entry['list']
        list_density = _entry['density']['value']
        list_iso_ratio = _entry['isotopic_ratio']
        list_mass = _entry['mass']['value']
        
        nbr_iso = len(list_iso)
        for _row in range(nbr_iso):
            self.ui.element_table.insertRow(_row)

            # iso name
            _item = QtGui.QTableWidgetItem(list_iso[_row])
            _item.setFlags(QtCore.Qt.NoItemFlags)
            _color = QtGui.QColor(200,200,200)
            _item.setBackgroundColor(_color)
            self.ui.element_table.setItem(_row, 0, _item)

            # density
            _item = QtGui.QTableWidgetItem("{:6.3e}".format(list_density[_row]))
            _item.setBackgroundColor(_color)
            _item.setFlags(QtCore.Qt.NoItemFlags)
            self.ui.element_table.setItem(_row, 1, _item)
            
            # iso. ratio
            _item = QtGui.QTableWidgetItem("{:6.3e}".format(list_iso_ratio[_row]))
            self.ui.element_table.setItem(_row, 2, _item)
            
            # molar mass
            _item = QtGui.QTableWidgetItem("{:6.3e}".format(list_mass[_row]))
            _item.setBackgroundColor(_color)
            _item.setFlags(QtCore.Qt.NoItemFlags)
            self.ui.element_table.setItem(_row, 3, _item)

        self.calculate_sum_iso_ratio()
            
    def clear_isotopes_table(self):
        nbr_row = self.ui.element_table.rowCount()
        for _row in range(nbr_row):
            self.ui.element_table.removeRow(0)

    def calculate_sum_iso_ratio(self):
        nbr_row = self.ui.element_table.rowCount()
        total_iso_ratio = 0
        for _row in range(nbr_row):
            _item = self.ui.element_table.item(_row, 2)
            try:
                _iso_ratio = float(self.ui.element_table.item(_row, 2).text())
            except:
                _iso_ratio = np.NaN
                _item = QtGui.QTableWidgetItem("NaN")
                self.ui.element_table.setItem(_row, 2, _item)
            total_iso_ratio += _iso_ratio
        self.ui.total_iso_ratio.setText("{:.2f}".format(total_iso_ratio))

        # will use this flag to allow new isotopic ratio entries
        if np.isnan(total_iso_ratio):
            return False
        return True
            
    def layer_combobox_clicked(self, layer_selected):
        if layer_selected == '':
            return
        list_elements = self.stack[layer_selected]['elements']
        # block element table signal
        self.ui.element_table.blockSignals(True)
      
        # fill list of elements for this layer
        self.ui.element_name_combobox.clear()
        self.ui.element_name_combobox.addItems(list_elements)
        
        # fill info for this layer
        _layer = self.stack[layer_selected]
        thickness = str(_layer['thickness']['value'])
        self.ui.layer_thickness.setText(thickness)
        density = str(_layer['density']['value'])
        self.ui.layer_density.setText(density)
        
        self.ui.element_table.blockSignals(False)

    def element_table_edited(self, row, col):
        if col == 2:
            calculation_status = self.calculate_sum_iso_ratio()
            if calculation_status:
                self.define_new_isotopic_ratio()
                
    def define_new_isotopic_ratio(self):
        layer_selected = self.ui.layer_name_combobox.currentText()
        element_selected = self.ui.element_name_combobox.currentText()
        _entry = self.stack[layer_selected][element_selected]['isotopes']
        list_isotopes = _entry['list']
 

        nbr_row = self.ui.element_table.rowCount()
        list_isotopic_ratio = []
        for _row in range(nbr_row):
            _iso_ratio = float(self.ui.element_table.item(_row, 2).text())
            list_isotopic_ratio.append(_iso_ratio)
        
        self.o_reso.set_isotopic_ratio(compound=layer_selected, 
                                       element=element_selected, 
                                       list_ratio=list_isotopic_ratio)
        
        self.layer_combobox_clicked(layer_selected)
        self.element_combobox_clicked(element_selected)
        
    def ok_button_clicked(self):
#        global global_o_reso
#        global_o_reso = self.o_reso
        self.close()
        
