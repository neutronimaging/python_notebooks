from IPython.core.display import HTML
from IPython.display import display
import numpy as np
from collections import OrderedDict

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow, QTableWidgetItem
except ImportError:
    from PyQt5.QtWidgets import QFileDialog, QTreeWidgetItem, QTableWidgetItem
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from __code.ui_addie  import Ui_MainWindow as UiMainWindow


class Interface(QMainWindow):

    item_dict = {'ui': None,
                 'name': '',
                 'state': True,
                 'table_row_column': []}

    tree_dict_state = {}
    tree_column = 0

    leaf = {'ui': None,
            'name': ''}

    tree_dict = OrderedDict()
    tree_dict['title'] = {'ui': None,
                          'name': "Title",
                           'children': None}

    sample_children_1 = OrderedDict()
    sample_children_1['sample_runs'] = {'ui': None,
                                        'name': "Runs",
                                        'children': None}

    sample_children_2 = OrderedDict()
    sample_children_2['sample_background_runs'] = {'ui': None,
                                                   'name': "Runs",
                                                   'children': None}
    sample_children_2['sample_background_background'] = {'ui': None,
                                                        'name': "Background",
                                                        'children': None}
    sample_children_1['sample_background'] = {'ui': None,
                                              'name': "Background",
                                              'children': sample_children_2}

    sample_children_1['sample_material'] = {'ui': None,
                                            'name': "Material",
                                            'children': None}

    sample_children_1['sample_packing_fraction'] = {'ui': None,
                                                    'name': "Packing Fraction",
                                                    'children': None}

    sample_children_2 = OrderedDict()
    sample_children_2['sample_geometry_shape'] = {'ui': None,
                                                  'name': "Shape",
                                                  'children': None}
    sample_children_2['sample_geometry_radius'] = {'ui': None,
                                                   'name': "Radius",
                                                   'children': None}
    sample_children_2['sample_geometry_Height'] = {'ui': None,
                                                   'name': "Height",
                                                   'children': None}
    sample_children_1['sample_geometry'] = {'ui': None,
                                            'name': "Geometry",
                                            'children': sample_children_2}

    sample_children_1['sample_absolute_correction'] = {'ui': None,
                                                       'name': "Abs. Correction",
                                                       'children': None}

    sample_children_1['sample_multi_scattering_correction'] = {'ui': None,
                                                               'name': "Mult. Scattering Correction",
                                                               'children': None}
    sample_children_1['sample_inelastic_correction'] = {'ui': None,
                                                        'name': "Inelastic Correction",
                                                        'children': None}

    tree_dict['sample'] = {'ui': None,
                           'name': "Sample",
                           'children': sample_children_1}

    vanadium_children_1 = OrderedDict()
    vanadium_children_1['vanadium_runs'] = {'ui': None,
                                        'name': "Runs",
                                        'children': None}

    vanadium_children_2 = OrderedDict()
    vanadium_children_2['vanadium_background_runs'] = {'ui': None,
                                                   'name': "Runs",
                                                   'children': None}
    vanadium_children_2['vanadium_background_background'] = {'ui': None,
                                                         'name': "Background",
                                                         'children': None}
    vanadium_children_1['vanadium_background'] = {'ui': None,
                                              'name': "Background",
                                              'children': vanadium_children_2}

    vanadium_children_1['vanadium_material'] = {'ui': None,
                                            'name': "Material",
                                            'children': None}

    vanadium_children_1['vanadium_packing_fraction'] = {'ui': None,
                                                    'name': "Packing Fraction",
                                                    'children': None}

    vanadium_children_2 = OrderedDict()
    vanadium_children_2['vanadium_geometry_shape'] = {'ui': None,
                                                  'name': "Shape",
                                                  'children': None}
    vanadium_children_2['vanadium_geometry_radius'] = {'ui': None,
                                                   'name': "Radius",
                                                   'children': None}
    vanadium_children_2['vanadium_geometry_Height'] = {'ui': None,
                                                   'name': "Height",
                                                   'children': None}
    vanadium_children_1['vanadium_geometry'] = {'ui': None,
                                            'name': "Geometry",
                                            'children': vanadium_children_2}

    vanadium_children_1['vanadium_absolute_correction'] = {'ui': None,
                                                       'name': "Abs. Correction",
                                                       'children': None}

    vanadium_children_1['vanadium_multi_scattering_correction'] = {'ui': None,
                                                               'name': "Mult. Scattering Correction",
                                                               'children': None}
    vanadium_children_1['vanadium_inelastic_correction'] = {'ui': None,
                                                        'name': "Inelastic Correction",
                                                        'children': None}

    tree_dict['vanadium'] = {'ui': None,
                             'name': "Vanadium",
                             'children': vanadium_children_1}

    table_headers = {'h1': [],
                     'h2': [],
                     'h3': [],
                     }

    default_width = 90

    table_width = {'h1': [],
                   'h2': [],
                   'h3': []}


    def __init__(self, parent=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Template Addie")

        # self.init_tree()
        # self.init_widgets()
        self.init_tables()

    def init_headers(self):
        td = self.tree_dict

        table_headers = {'h1': [], 'h2': [], 'h3': []}
        for _key_h1 in td.keys():
            table_headers['h1'].append(td[_key_h1]['name'])
            if td[_key_h1]['children']:
                for _key_h2 in td[_key_h1]['children'].keys():
                    table_headers['h2'].append(td[_key_h1]['children'][_key_h2]['name'])
                    if td[_key_h1]['children'][_key_h2]['children']:
                        for _key_h3 in td[_key_h1]['children'][_key_h2]['children'].keys():
                            table_headers['h3'].append(td[_key_h1]['children'][_key_h2]['children'][_key_h3]['name'])
                    else:
                        table_headers['h3'].append('')
            else:
                table_headers['h2'].append('')
                table_headers['h3'].append('')

        self.table_headers = table_headers

    def init_table_col_width(self, table_width=[], table_ui=None):
        for _col in np.arange(table_ui.columnCount()):
            table_ui.setColumnWidth(_col, table_width[_col])

    def init_table_header(self, table_ui=None, list_items=None):
        table_ui.setColumnCount(len(list_items))
        for _index, _text in enumerate(list_items):
            item = QTableWidgetItem(_text)
            table_ui.setHorizontalHeaderItem(_index, item)

    def init_table_dimensions(self):
        td = self.tree_dict

        table_width = {'h1': [], 'h2': [], 'h3': []}

        # check all the h1 headers
        for _key_h1 in td.keys():

            # if h1 header has children
            if td[_key_h1]['children']:

                absolute_nbr_h3_for_this_h1 = 0

                # loop through list of h2 header for this h1 header
                for _key_h2 in td[_key_h1]['children'].keys():

                    # if h2 has children, just count how many children
                    if td[_key_h1]['children'][_key_h2]['children']:
                        nbr_h3 = len(td[_key_h1]['children'][_key_h2]['children'])

                        for _i in np.arange(nbr_h3):
                            table_width['h3'].append(self.default_width)

                        ## h2 header will be as wide as the number of h3 children
                        table_width['h2'].append(nbr_h3 * self.default_width)

                        ## h1 header will be += the number of h3 children
                        absolute_nbr_h3_for_this_h1 += nbr_h3

                    # if h2 has no children
                    else:

                        ## h2 header is 1 wide
                        table_width['h2'].append(self.default_width)
                        table_width['h3'].append(self.default_width)

                        ## h2 header will be += 1
                        absolute_nbr_h3_for_this_h1 += 1

                table_width['h1'].append(absolute_nbr_h3_for_this_h1 * self.default_width)

            # if h1 has no children
            else:
                # h1, h2 and h3 are 1 wide
                table_width['h1'].append(self.default_width)
                table_width['h2'].append(self.default_width)
                table_width['h3'].append(self.default_width)

        self.table_width = table_width

    def init_tables(self):

        # set h1, h2 and h3 headers
        self.init_headers()
        self.init_table_header(table_ui=self.ui.h1_table, list_items=self.table_headers['h1'])
        self.init_table_header(table_ui=self.ui.h2_table, list_items=self.table_headers['h2'])
        self.init_table_header(table_ui=self.ui.h3_table, list_items=self.table_headers['h3'])

        # set h1, h2 and h3 width
        self.init_table_dimensions()
        self.init_table_col_width(table_width=self.table_width['h1'], table_ui=self.ui.h1_table)
        self.init_table_col_width(table_width=self.table_width['h2'], table_ui=self.ui.h2_table)
        self.init_table_col_width(table_width=self.table_width['h3'], table_ui=self.ui.h3_table)


    def init_widgets(self):
        pass

    def init_tree(self):
        # fill the self.ui.treeWidget
        self.addItems(self.ui.treeWidget.invisibleRootItem())
        self.ui.treeWidget.itemChanged.connect(self.tree_item_changed)

    def get_item_name(self, item):
        for _key in self.tree_dict_state.keys():
            # print("self.tree_dict_state[_key]['ui']: {}".format(self.tree_dict_state[_key]['ui']))
            if item == self.tree_dict_state[_key]['ui']:
                return _key
        return None

    def tree_item_changed(self, item, _):
        print("name of item is: {}".format(self.get_item_name(item)))


    def addItems(self, parent):

        title = self.addChild(parent, "Title", "title", [0,0])

        sample = self.addParent(parent, "Sample", 'sample', [1,2,3])
        self.addChild(sample, "Runs", "sample_runs", [1])
        sample_background = self.addParent(sample, "Background", "sample_background", [2,3])
        self.addChild(sample_background, "Runs", "sample_background_runs", [2])
        self.addChild(sample_background, "Background Runs", "sample_background_background_runs", [3])

        self.addChild(sample, "Packing Fraction", "sample_packging_fraction", [4])
        sample_geometry = self.addParent(sample, "Geometry", "sample_geometry", [5,6,7])
        self.addChild(sample_geometry, "Shape", "sample_geometry_shape", [5])
        self.addChild(sample_geometry, "Radius", "sample_geometry_radius", [6])
        self.addChild(sample_geometry, "Height", "sample_geometry_height", [7])

        vanadium = self.addParent(parent, "vanadium", 'vanadium', [1,2,3])
        self.addChild(vanadium, "Runs", "vanadium_runs", [1])
        vanadium_background = self.addParent(vanadium, "Background", "vanadium_background", [2,3])
        self.addChild(vanadium_background, "Runs", "vanadium_background_runs", [2])
        self.addChild(vanadium_background, "Background Runs", "vanadium_background_background_runs", [3])

        self.addChild(vanadium, "Packing Fraction", "vanadium_packging_fraction", [4])
        vanadium_geometry = self.addParent(vanadium, "Geometry", "vanadium_geometry", [5,6,7])
        self.addChild(vanadium_geometry, "Shape", "vanadium_geometry_shape", [5])
        self.addChild(vanadium_geometry, "Radius", "vanadium_geometry_radius", [6])
        self.addChild(vanadium_geometry, "Height", "vanadium_geometry_height", [7])


    def addParent(self, parent, title, name, table_row_column=[]):
        item = QTreeWidgetItem(parent, [title])
        item.setData(self.tree_column, QtCore.Qt.UserRole, '')
        item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        item.setCheckState(self.tree_column, QtCore.Qt.Checked)
        item.setExpanded(True)

        self.tree_dict_state[name] = self.item_dict.copy()
        self.tree_dict_state[name]['ui'] = item
        self.tree_dict_state[name]['table_row_column'] = table_row_column

        return item

    def addChild(self, parent, title, name, table_row_column=[]):
        item = QTreeWidgetItem(parent, [title])
        item.setData(self.tree_column, QtCore.Qt.UserRole, '')
        item.setCheckState(self.tree_column, QtCore.Qt.Checked)

        self.tree_dict_state[name] = self.item_dict.copy()
        self.tree_dict_state[name]['ui'] = item
        self.tree_dict_state[name]['table_row_column'] = table_row_column

        return item

    def init_widgets(self):
        pass

    def apply_clicked(self):
        # do stuff
        self.close()

    def cancel_clicked(self):
        self.close()

    def closeEvent(self, eventhere=None):
        print("Leaving Parameters Selection UI")



