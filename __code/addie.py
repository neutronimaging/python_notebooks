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

        # self.init_widgets()
        self.init_tables()
        self.init_tree()

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
        # self.addItems(self.ui.treeWidget.invisibleRootItem())
        self.addItems(self.ui.treeWidget.invisibleRootItem())
        self.ui.treeWidget.itemChanged.connect(self.tree_item_changed)

    def get_item_name(self, item):
        td = self.tree_dict

        for _key_h1 in td.keys():

            if item == td[_key_h1]['ui']:
                return _key_h1

            if td[_key_h1]['children']:

                for _key_h2 in td[_key_h1]['children'].keys():

                    if item == td[_key_h1]['children'][_key_h2]['ui']:
                        return _key_h2

                    if td[_key_h1]['children'][_key_h2]['children']:

                        for _key_h3 in td[_key_h1]['children'][_key_h2]['children'].keys():

                            if item == td[_key_h1]['children'][_key_h2]['children'][_key_h3]['ui']:
                                return _key_h3

        return None

    def tree_item_changed(self, item, _):
        """this will change the way the big table will look like by hidding or showing columns"""
        print("name of item is: {}".format(self.get_item_name(item)))
        h_columns_affected = self.get_h_columns_from_item_name(item_name=self.get_item_name(item))

        import pprint
        pprint.pprint(h_columns_affected)

        self.change_state_children(list_ui=h_columns_affected['list_tree_ui'],
                                   list_parent_ui=h_columns_affected['list_parent_ui'],
                                   state=item.checkState(0))

    def change_state_children(self, list_ui=[], list_parent_ui=[], state=0):
        """
        Will transfer the state of the parent to the children

        :param list_ui:
        :parem list_parent_ui:
        :param state:
        :return:
        """

        self.ui.treeWidget.blockSignals(True)

        for _ui in list_ui:
            _ui.setCheckState(0, state)

        # if the leaf is enabled, we need to make sure all the parents are enabled as well.
        if state == QtCore.Qt.Checked:
            for _ui in list_parent_ui:
                _ui.setCheckState(0, state)

        self.ui.treeWidget.blockSignals(False)

    def get_h_columns_from_item_name(self, item_name=None):
        if item_name == None:
            return

        h_columns_affected = {'h1': [],
                              'h2': [],
                              'h3': [],
                              'list_tree_ui': [],
                              'list_parent_ui': []}

        h1_columns = []
        h2_columns = []
        h3_columns = []
        list_tree_ui = []
        list_parent_ui = []

        h1_global_counter = 0
        h2_global_counter = 0
        h3_global_counter = 0

        td = self.tree_dict
        for h1_global_counter, _key_h1 in enumerate(td.keys()):

            if item_name == _key_h1:
                # get all h2 and h3 of this h1

                if td[_key_h1]['children']:

                    for _key_h2 in td[_key_h1]['children']:

                        if td[_key_h1]['children'][_key_h2]['children']:

                            list_tree_ui.append(td[_key_h1]['children'][_key_h2]['ui'])
                            for _key_h3 in td[_key_h1]['children'][_key_h2]['children'].keys():
                                h3_columns.append(h3_global_counter)
                                list_tree_ui.append(td[_key_h1]['children'][_key_h2]['children'][_key_h3]['ui'])
                                h3_global_counter += 1

                        else:

                            h2_columns.append(h2_global_counter)
                            list_tree_ui.append(td[_key_h1]['children'][_key_h2]['ui'])
                            h3_columns.append(h3_global_counter)

                            h2_global_counter += 1
                            h3_global_counter += 1

                    return {'h1': [h1_global_counter],
                            'h2': h2_columns,
                            'h3': h3_columns,
                            'list_tree_ui': list_tree_ui,
                            'list_parent_ui': list_parent_ui}

                else:

                    list_tree_ui.append(td[_key_h1]['ui'])
                    return {'h1': [h1_global_counter],
                            'h2': [h2_global_counter],
                            'h3': [h3_global_counter],
                            'list_tree_ui': list_tree_ui,
                            'list_parent_ui': list_parent_ui}

            else:
                # start looking into the h2 layer if it has children

                if td[_key_h1]['children']:

                    for _key_h2 in td[_key_h1]['children'].keys():

                        if item_name == _key_h2:
                            # get all h3 for this h2 and we are done

                            if td[_key_h1]['children'][_key_h2]['children']:
                                # if key_h2 has children

                                # list all h3 leaves for this h2
                                for _key_h3 in td[_key_h1]['children'][_key_h2]['children'].keys():
                                    h3_columns.append(h3_global_counter)
                                    list_tree_ui.append(td[_key_h1]['children'][_key_h2]['children'][_key_h3]['ui'])
                                    h3_global_counter += 1

                            else:
                                h3_columns = [h3_global_counter]

                            list_tree_ui.append(td[_key_h1]['children'][_key_h2]['ui'])
                            list_parent_ui.append(td[_key_h1]['ui'])
                            return {'h1': [],
                                    'h2': [h2_global_counter],
                                    'h3': h3_columns,
                                    'list_tree_ui': list_tree_ui,
                                    'list_parent_ui': list_parent_ui}

                        else:
                            # we did not find the item name yet

                            # start looking into all the h2 children (if any)
                            if td[_key_h1]['children'][_key_h2]['children']:

                                # loop through all the h3 and look for item_name. If found
                                # we are done
                                for _key_h3 in td[_key_h1]['children'][_key_h2]['children'].keys():

                                    if item_name == _key_h3:
                                        # we found the item name at the h3 layer,
                                        # no leaf below, so we are done

                                        list_parent_ui.append(td[_key_h1]['ui'])
                                        list_parent_ui.append(td[_key_h1]['children'][_key_h2]['ui'])
                                        return {'h1': [],
                                                'h2': [],
                                                'h3': [h3_global_counter],
                                                'list_tree_ui': list_tree_ui,
                                                'list_parent_ui': list_parent_ui}

                                    else:

                                        h3_global_counter += 1

                                h2_global_counter += 1

                            else:
                                # no children, we just keep going to the next h2 (and h3)

                                h2_global_counter += 1
                                h3_global_counter += 1

                else:
                    # no children and item_name has not been found yet, so
                    # just keep going and move on to the next h1
                    h2_global_counter += 1
                    h3_global_counter += 1

        return {'h1': h1_columns,
                'h2': h2_columns,
                'h3': h3_columns,
                'list_tree_ui': list_tree_ui,
                'list_parent_ui': list_parent_ui}

    def addItems(self, parent):
        td = self.tree_dict
        absolute_parent = parent
        local_parent = None
        for _key_h1 in td.keys():

            # if there are children, we need to use addParent
            if td[_key_h1]['children']:

                _h1_parent = self.addParent(absolute_parent,
                                       td[_key_h1]['name'],
                                       _key_h1)
                td[_key_h1]['ui'] = _h1_parent

                for _key_h2 in td[_key_h1]['children'].keys():

                    # if there are children, we need to use addParent
                    if td[_key_h1]['children'][_key_h2]['children']:

                        _h2_parent = self.addParent(_h1_parent,
                                                    td[_key_h1]['children'][_key_h2]['name'],
                                                    _key_h2)
                        td[_key_h1]['children'][_key_h2]['ui'] = _h2_parent

                        for _key_h3 in td[_key_h1]['children'][_key_h2]['children']:
                            _h3_child = self.addChild(_h2_parent,
                                                      td[_key_h1]['children'][_key_h2]['children'][_key_h3]['name'],
                                                      _key_h3)
                            td[_key_h1]['children'][_key_h2]['children'][_key_h3]['ui'] = _h3_child

                    else: # key_h2 has no children, it's a leaf
                        _h3_child = self.addChild(_h1_parent,
                                                  td[_key_h1]['children'][_key_h2]['name'],
                                                  _key_h2)
                        td[_key_h1]['children'][_key_h2]['ui'] = _h3_child

            else: #_key_h1 has no children, using addChild
                _child = self.addChild(absolute_parent,
                                       td[_key_h1]['name'],
                                       _key_h1)
                td[_key_h1]['ui'] = _child

    def addParent(self, parent, title, name):
        item = QTreeWidgetItem(parent, [title])
        item.setData(self.tree_column, QtCore.Qt.UserRole, '')
        item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        item.setCheckState(self.tree_column, QtCore.Qt.Checked)
        item.setExpanded(True)
        return item

    def addChild(self, parent, title, name):
        item = QTreeWidgetItem(parent, [title])
        item.setData(self.tree_column, QtCore.Qt.UserRole, '')
        item.setCheckState(self.tree_column, QtCore.Qt.Checked)
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



