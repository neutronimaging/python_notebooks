#from IPython.core.display import HTML
#from IPython.display import display
import os
from os.path import expanduser
import numpy as np
from collections import OrderedDict
import pickle
from collections import OrderedDict
import pprint

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4.QtCore import QObject
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow, QTableWidgetItem, QMenu, QDialog
except ImportError:
    try:
        from PyQt5.QtWidgets import QFileDialog, QTreeWidgetItem, QTableWidgetItem
        from PyQt5 import QtCore, QtGui
        from PyQt5.QtCore import QObject
        from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QDialog, QAction
    except ImportError:
        raise ImportError("Requires PyQt5 or PyQt4.")

from __code.ui_addie  import Ui_MainWindow as UiMainWindow
from __code.ui_addie_save_config import Ui_Dialog as UiDialogSave

user_home = expanduser("~")
CONFIG_FILE = os.path.join(user_home, '.addie_config.cfg')


class Interface(QMainWindow):

    config_dict = {} # various configurations defined by the user (last 5)
    active_config_name = ''

    # list of config previously saved by user and display when doing right click in table
    list_config_displayed = []

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

    # to find which h1 column goes with wich h2 and which h3
    table_columns_links = {'h1': [],
                           'h2': [],
                           'h3': [],
                           }

    default_width = 90

    table_width = {'h1': [],
                   'h2': [],
                   'h3': []}


    def __init__(self, parent=None):

        # display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
        #     (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Template Addie")

        # self.init_widgets()
        self.init_tables()
        self.init_tree()
        self.init_signals()

        # import pprint
        # pprint.pprint(self.table_columns_links)

    def init_signals(self):
        self.h1_header_table.sectionResized.connect(self.resizing_h1)
        self.h2_header_table.sectionResized.connect(self.resizing_h2)
        self.h3_header_table.sectionResized.connect(self.resizing_h3)

        self.ui.h1_table.horizontalScrollBar().valueChanged.connect(self.scroll_h1_table)
        self.ui.h2_table.horizontalScrollBar().valueChanged.connect(self.scroll_h2_table)
        self.ui.h3_table.horizontalScrollBar().valueChanged.connect(self.scroll_h3_table)

    def load_this_config(self, key=''):
        if key == '':
            return

        #FIXME
        return

        config_to_load = self.config_dict[key]['table']

        h1_dict = config_to_load['h1']
        h2_dict = config_to_load['h2']
        h3_dict = config_to_load['h3']

        print(config_to_load)

        self.block_table_ui()

        for _col in h1_dict:
            _visible = h1_dict[_col]['visible']
            _width = h1_dict[_col]['width']

        for _col in h2_dict:
            _visible = h2_dict[_col]['visible']
            _width = h2_dict[_col]['width']
            self.set_size_and_visibility_column(h2=_col, width=_width, visibility=_visible)

        for _col in h3_dict:
            _visible = h3_dict[_col]['visible']
            _width = h3_dict[_col]['width']
            self.set_size_and_visibility_column(h3=_col, width=_width, visibility=_visible)

        self.block_table_ui(unblock_all=True)


    def h3_table_right_click(self, position):
        o_h3_table = H3TableHandler(parent=self)
        o_h3_table.right_click()


    def scroll_h1_table(self, value):
        self.ui.h2_table.horizontalScrollBar().setValue(value)
        self.ui.h3_table.horizontalScrollBar().setValue(value)

    def scroll_h2_table(self, value):
        self.ui.h1_table.horizontalScrollBar().setValue(value)
        self.ui.h3_table.horizontalScrollBar().setValue(value)

    def scroll_h3_table(self, value):
        self.ui.h1_table.horizontalScrollBar().setValue(value)
        self.ui.h2_table.horizontalScrollBar().setValue(value)

    def block_table_ui(self, block_all=True,
                       unblock_all=False,
                       block_h1=False,
                       block_h2=False,
                       block_h3=False):

        if block_all:
            block_h1 = True
            block_h2 = True
            block_h3 = True

        if unblock_all:
            block_h1 = False
            block_h2 = False
            block_h3 = False

        if block_h1:
            self.h1_header_table.sectionResized.disconnect(self.resizing_h1)
        else:
            self.h1_header_table.sectionResized.connect(self.resizing_h1)

        if block_h2:
            self.h2_header_table.sectionResized.disconnect(self.resizing_h2)
        else:
            self.h2_header_table.sectionResized.connect(self.resizing_h2)

        if block_h3:
            self.h3_header_table.sectionResized.disconnect(self.resizing_h3)
        else:
            self.h3_header_table.sectionResized.connect(self.resizing_h3)

    def resizing_h1(self, index_column, old_size, new_size):
        # print("resizing h1 column {}".format(index_column))

        self.block_table_ui()

        h2_children = self.get_h2_children_from_h1(h1=index_column)
        # print("h2 children: {}".format(h2_children))

        last_h2_visible = self.get_last_h2_visible(list_h2=h2_children)
        # print("last h2 visible: {}".format(last_h2_visible))

        list_h3 = self.get_h3_children_from_h2(h2=last_h2_visible)
        # print("h3 children: {}".format(list_h3))

        last_h3_visible = self.get_last_h3_visible(list_h3=list_h3)
        # print("Last h3 visible: {}".format(last_h3_visible))

        size_diff = new_size - old_size

        # add this size_diff to last_h2 and last_h3
        last_h2_visible_size = self.get_size_column(h2=last_h2_visible)
        self.set_size_column(h2=last_h2_visible, width=last_h2_visible_size+size_diff)
        last_h3_visible_size = self.get_size_column(h3=last_h3_visible)
        self.set_size_column(h3=last_h3_visible, width=last_h3_visible_size+size_diff)

        self.block_table_ui(unblock_all=True)
        # print("")

    def resizing_h2(self, index_column, old_size, new_size):
        # print("resizing h2 column {}".format(index_column))

        self.block_table_ui()

        h1_parent = self.get_h1_parent_from_h2(h2=index_column)
        # print("h1_parent: {}".format(h1_parent))

        h3_children = self.get_h3_children_from_h2(h2=index_column)
        # print("h3 children: {}".format(h3_children))

        last_h3_visible = self.get_last_h3_visible(list_h3=h3_children)
        # print("last h3 visible is {}".format(last_h3_visible))

        size_diff = new_size - old_size

        # add this size_diff to parent and last h3
        parent_size = self.get_size_column(h1=h1_parent)
        self.set_size_column(h1=h1_parent, width=parent_size+size_diff)
        last_h3_visible_size = self.get_size_column(h3=last_h3_visible)
        self.set_size_column(h3=last_h3_visible, width=last_h3_visible_size+size_diff)

        self.block_table_ui(unblock_all=True)

    def resizing_h1_using_all_visible_h2(self, h1=None):
        '''automatically resize the h1 using all its h2 visible '''
        h2_children = self.get_h2_children_from_h1(h1=h1)
        list_visible_h2 = self.get_all_h2_visible(list_h2=h2_children)

        if list_visible_h2 is None:
            return

        full_size_h2 = 0
        for _h2 in list_visible_h2:
            full_size_h2 += self.get_size_column(h2=_h2)

        self.ui.h1_table.setColumnWidth(h1, full_size_h2)

    def resizing_h3(self, index_column, old_size, new_size):
        # print("resizing h3 column {}".format(index_column))

        self.block_table_ui()

        [h1_parent, h2_parent] = self.get_h1_h2_parent_from_h3(h3=index_column)
        # print("h1_parent, h2_parent: {},{}".format(h1_parent, h2_parent))

        size_diff = new_size - old_size

        # get h2 and h1 size and resize them
        h1_parent_size = self.get_size_column(h1=h1_parent)
        self.set_size_column(h1=h1_parent, width=h1_parent_size+size_diff)
        h2_parent_size = self.get_size_column(h2=h2_parent)
        self.set_size_column(h2=h2_parent, width=h2_parent_size+size_diff)

        self.block_table_ui(unblock_all=True)

    def resizing_h2_using_all_visible_h3(self, h2=None):
        '''automatically resizing the h2 using all its h3 visible'''
        h3_children = self.get_h3_children_from_h2(h2=h2)
        list_visible_h3 = self.get_all_h3_visible(list_h3=h3_children)

        if list_visible_h3 is None:
            return

        full_size_h3 = 0
        for _h3 in list_visible_h3:
            full_size_h3 += self.get_size_column(h3=_h3)

        self.ui.h2_table.setColumnWidth(h2, full_size_h3)

    # Utilites

    def is_h_visible(self, h1=None, h2=None, h3=None):
        table_ui = self.get_table_ui(h1=h1, h2=h2, h3=h3)
        master_h = self.get_master_h(h1=h1, h2=h2, h3=h3)
        return not table_ui.isColumnHidden(master_h)

    def get_table_ui(self, h1=None, h2=None, h3=None):
        '''h1, h2 or h3 are column indexes'''
        if not h1 is None:
            table_ui = self.ui.h1_table
        elif not h2 is None:
            table_ui = self.ui.h2_table
        elif not h3 is None:
            table_ui = self.ui.h3_table
        else:
            table_ui = None
        return table_ui

    def get_master_h(self, h1=None, h2=None, h3=None):
        '''return the only defined column index from h1, h2 or h3 table'''
        if not h1 is None:
            return h1
        elif not h2 is None:
            return h2
        elif not h3 is None:
            return h3
        else:
            return None

    def get_size_column(self, h1=None, h2=None, h3=None):
        table_ui = self.get_table_ui(h1=h1, h2=h2, h3=h3)
        h = self.get_master_h(h1=h1, h2=h2, h3=h3)
        return table_ui.columnWidth(h)

    def set_size_column(self, h1=None, h2=None, h3=None, width=None):
        if width is None:
            return

        table_ui = self.get_table_ui(h1=h1, h2=h2, h3=h3)
        h = self.get_master_h(h1=h1, h2=h2, h3=h3)
        table_ui.setColumnWidth(h, width)

    def set_visibility_column(self, h1=None, h2=None, h3=None, visibility=True):
        table_ui = self.get_table_ui(h1=h1, h2=h2, h3=h3)
        h = self.get_master_h(h1=h1, h2=h2, h3=h3)
        table_ui.setColumnHidden(h, not visibility)

    def set_size_and_visibility_column(self, h1=None, h2=None, h3=None, width=None, visibility=True):
        self.set_size_column(h1=h1, h2=h2, h3=h3, width=width)
        self.set_visibility_column(h1=h1, h2=h2, h3=h3, visibility=visibility)

    def get_h2_children_from_h1(self, h1=-1):
        if h1 == -1:
            return None

        table_columns_links = self.table_columns_links
        list_h2_values = table_columns_links['h2']

        return list_h2_values[h1]

    def get_all_h2_visible(self, list_h2=[]):
        '''return the list of all the visible h2 from the list of h2 given'''
        if list_h2 == []:
            return None

        list_h2_visible = [_h2 for _h2 in list_h2 if not self.ui.h2_table.isColumnHidden(_h2)]
        return list_h2_visible

    def get_last_h2_visible(self, list_h2=[]):
        if list_h2 == []:
            return None

        for _h2 in list_h2[::-1]:
            if self.ui.h2_table.isColumnHidden(_h2):
                continue
            else:
                return _h2

        return None

    def get_all_h3_visible(self, list_h3=[]):
        '''return the list of all the visible h3 from the list of h3 given'''
        if list_h3 == []:
            return None

        list_h3_visible = [_h3 for _h3 in list_h3 if not self.ui.h3_table.isColumnHidden(_h3)]
        return list_h3_visible

    def get_last_h3_visible(self, list_h3=[]):
        if list_h3 == []:
            return None

        for _h3 in list_h3[::-1]:
            if self.ui.h3_table.isColumnHidden(_h3):
                continue
            else:
                return _h3

        return None

    def get_h3_children_from_h2(self, h2=-1):
        if h2 == -1:
            return None

        table_columns_links = self.table_columns_links
        list_h3_values = table_columns_links['h3']
        list_h2_values = table_columns_links['h2']

        index_h2 = -1
        index_h1 = 0
        for h2_values in list_h2_values:
            if h2 in h2_values:
                index_h2 = h2_values.index(h2)
                break
            index_h1 += 1

        if index_h2 == -1:
            return []

        return list_h3_values[index_h1][index_h2]

    def get_h1_parent_from_h2(self, h2=-1):
        if h2 == -1:
            return None

        table_columns_links = self.table_columns_links
        list_h2_values = table_columns_links['h2']

        h1_parent_index = 0
        for h2_values in list_h2_values:
            if h2 in h2_values:
                return h1_parent_index
            h1_parent_index += 1

        return None

    def get_h1_h2_parent_from_h3(self, h3=-1):
        if h3 == -1:
            return [None, None]

        table_columns_links = self.table_columns_links
        list_h3_values = table_columns_links['h3']

        h1_parent_index = 0
        h2_parent_index = 0

        for h3_values in list_h3_values:
            for local_h3 in h3_values:
                if h3 in local_h3:
                    return [h1_parent_index, h2_parent_index]
                h2_parent_index += 1
            h1_parent_index += 1

        return [None, None]

    def resizing_table(self, tree_dict={}):
        '''updating the size of the columns using visibility of the various elements of the tree'''
        if tree_dict == {}:
            return

        self.block_table_ui()

        # if user disabled or enabled at the h1 level, nothing to do as all the columns will be automatically
        # resized the right way
        h1 = tree_dict['h1']
        h2 = tree_dict['h2']
        h3 = tree_dict['h3']
        if not h1 == []:
            pass

        # if user clicked at the h2 level
        elif not h2 == []:

            h2 = h2[0]

            h1_parent = self.get_h1_parent_from_h2(h2=h2)
            is_h1_parent_visible = self.is_h_visible(h1=h1_parent)

            if is_h1_parent_visible:
                # resize h2 using all visible h3
                self.resizing_h2_using_all_visible_h3(h2=h2)

                # if h1 parent is visible, re-sized h1 parent using all visible h2
                self.resizing_h1_using_all_visible_h2(h1=h1_parent)

            else:
                # if h1 parent is not visible, done !
                pass

        # if user clicked at the h3 level
        elif not h3 == []:

            h3 = h3[0]

            [h1_parent, h2_parent] = self.get_h1_h2_parent_from_h3(h3=h3)
            is_h2_parent_visible = self.is_h_visible(h2=h2_parent)

            if is_h2_parent_visible:
                # if we have more h3 siblings visible
                # - we need to resize h2_parent using visible h3 siblings
                # - we need to resize h1_parent using all visible h2
                self.resizing_h2_using_all_visible_h3(h2=h2_parent)
                self.resizing_h1_using_all_visible_h2(h1=h1_parent)

            else:
                # if there are no more h3 siblings then
                #      if h1_parent visible -> resize h1_parent using all h2 visible
                #      if h1_parent not visible -> Done !
                h2 = h2_parent

                h1_parent = self.get_h1_parent_from_h2(h2=h2)
                is_h1_parent_visible = self.is_h_visible(h1=h1_parent)

                if is_h1_parent_visible:
                    # if h1 parent is visible, resized h1 parent using all visible h2
                    self.resizing_h1_using_all_visible_h2(h1=h1_parent)

                else:
                    # if h1 parent is not visible, done !
                    pass

        self.block_table_ui(unblock_all=True)


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

                        for _ in np.arange(nbr_h3):
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

        self.h1_header_table = self.ui.h1_table.horizontalHeader()
        self.h2_header_table = self.ui.h2_table.horizontalHeader()
        self.h3_header_table = self.ui.h3_table.horizontalHeader()

        self.make_tree_of_column_references()

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
        # print("name of item is: {}".format(self.get_item_name(item)))

        self.h1_header_table.blockSignals(True)
        self.h2_header_table.blockSignals(True)
        self.h3_header_table.blockSignals(True)

        h_columns_affected = self.get_h_columns_from_item_name(item_name=self.get_item_name(item))

        # import pprint
        # pprint.pprint(h_columns_affected)

        self.change_state_tree(list_ui=h_columns_affected['list_tree_ui'],
                               list_parent_ui=h_columns_affected['list_parent_ui'],
                               state=item.checkState(0))

        self.update_table_columns_visibility()
        self.resizing_table(tree_dict=h_columns_affected)
        
        self.h1_header_table.blockSignals(False)
        self.h2_header_table.blockSignals(False)
        self.h3_header_table.blockSignals(False)

    def make_all_columns_visible(self):
        """Make all columns of all table visible"""
        self.make_table_columns_visible(table_ui=self.ui.h1_table)
        self.make_table_columns_visible(table_ui=self.ui.h2_table)
        self.make_table_columns_visible(table_ui=self.ui.h3_table)

    def make_table_columns_visible(self, table_ui=None):
        """Make all columns of the given table ui visible"""
        nbr_col_h1 = table_ui.columnCount()
        for _col in np.arange(nbr_col_h1):
            table_ui.setColumnHidden(_col, False)

    def update_table_columns_visibility(self):
        # will update the table by hiding or not the columns

        def set_column_visibility(column=-1, table_ui=None, visible=0):
            table_ui.setColumnHidden(column, not visible)

        def get_boolean_state(key=None):
            status = key['state']
            if status == QtCore.Qt.Checked:
                return True
            else:
                return False

        h2_counter = 0
        h3_counter = 0

        td = self.tree_dict
        for h1_counter, _key_h1 in enumerate(td.keys()):

            _h1_boolean_status = get_boolean_state(td[_key_h1])
            set_column_visibility(column=h1_counter,
                                  table_ui=self.ui.h1_table,
                                  visible=_h1_boolean_status)

            if td[_key_h1]['children']:

                for _key_h2 in td[_key_h1]['children'].keys():

                    _h2_boolean_status = get_boolean_state(td[_key_h1]['children'][_key_h2])
                    set_column_visibility(column=h2_counter,
                                          table_ui=self.ui.h2_table,
                                          visible=_h2_boolean_status)

                    if td[_key_h1]['children'][_key_h2]['children']:

                        for _key_h3 in td[_key_h1]['children'][_key_h2]['children'].keys():

                            _h3_boolean_status = get_boolean_state(td[_key_h1]['children'][_key_h2]['children'][_key_h3])
                            set_column_visibility(column=h3_counter,
                                                  table_ui=self.ui.h3_table,
                                                  visible=_h3_boolean_status)
                            h3_counter += 1

                    else:

                        set_column_visibility(column=h3_counter,
                                              table_ui=self.ui.h3_table,
                                              visible=_h2_boolean_status)
                        h3_counter += 1

                    h2_counter += 1

            else:

                # h2 and h3 should have the same status as h1
                set_column_visibility(column=h2_counter,
                                      table_ui=self.ui.h2_table,
                                      visible=_h1_boolean_status)
                set_column_visibility(column=h3_counter,
                                      table_ui=self.ui.h3_table,
                                      visible=_h1_boolean_status)

                h2_counter += 1
                h3_counter += 1

    def change_state_tree(self, list_ui=[], list_parent_ui=[], state=0):
        """
        Will transfer the state of the parent to the children. We also need to make sure that if all the children
        are disabled, the parent gets disable as well.

        :param list_ui:
        :param list_parent_ui:
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

        self.update_full_tree_status()
        self.ui.treeWidget.blockSignals(False)

    def update_full_tree_status(self):
        """this will update the tree_dict dictionary with the status of all the leaves"""
        td = self.tree_dict

        # clean tree
        # if all h3 of an h2 are disabled, h2 should be disabled
        # if all h2 of a h1 are disabled, h1 should be disabled
        for _key_h1 in td.keys():

            if td[_key_h1]['children']:

                all_h2_disabled = True

                for _key_h2 in td[_key_h1]['children'].keys():

                    if td[_key_h1]['children'][_key_h2]['children']:

                        all_h3_disabled = True
                        for _key_h3 in td[_key_h1]['children'][_key_h2]['children'].keys():

                            if td[_key_h1]['children'][_key_h2]['children'][_key_h3]['ui'].checkState(0):
                                all_h3_disabled = False
                                all_h2_disabled = False
                                break

                        if all_h3_disabled:
                            # we need to make sure the h2 is disabled as well
                            td[_key_h1]['children'][_key_h2]['ui'].setCheckState(0, QtCore.Qt.Unchecked)

                    else:

                        if td[_key_h1]['children'][_key_h2]['ui'].checkState(0):
                            all_h2_disabled = False

                if all_h2_disabled:
                    # we need to make sure the h1 is disabled as well then
                    td[_key_h1]['ui'].setCheckState(0, QtCore.Qt.Unchecked)


        # record full tree state
        for _key_h1 in td.keys():

            td[_key_h1]['state'] = td[_key_h1]['ui'].checkState(0)

            if td[_key_h1]['children']:

                for _key_h2 in td[_key_h1]['children'].keys():

                    td[_key_h1]['children'][_key_h2]['state'] = td[_key_h1]['children'][_key_h2]['ui'].checkState(0)

                    if td[_key_h1]['children'][_key_h2]['children']:

                        for _key_h3 in td[_key_h1]['children'][_key_h2]['children'].keys():

                            td[_key_h1]['children'][_key_h2]['children'][_key_h3]['state'] = \
                            td[_key_h1]['children'][_key_h2]['children'][_key_h3]['ui'].checkState(0)

        self.tree_dict = td

    def make_tree_of_column_references(self):
        """
        table_columns_links = {'h1': [], 'h2': [], 'h3': []}

        h1 = [0, 1, 2]  # number of h1 columns
        h2 = [[0], [1,2,3], [4]] link of h2 columns with h1
        h3 = [ [[0]], [[1,2], [3,4], [5]], [[6,7,8]] ]

        :return:
        None
        """

        h1 = []
        h2 = []
        h3 = []

        h2_index=0
        h3_index=0

        td = self.tree_dict
        for h1_index, _key_h1 in enumerate(td.keys()):

            h1.append(h1_index)


            if td[_key_h1]['children']:

                _h2 = []
                _h3_h2 = []
                for _key_h2 in td[_key_h1]['children']:

                    if td[_key_h1]['children'][_key_h2]['children']:

                        _h3_h3 = []
                        for _key_h3 in td[_key_h1]['children'][_key_h2]['children']:

                            _h3_h3.append(h3_index)
                            h3_index += 1

                        _h3_h2.append(_h3_h3)

                    else:
                        # h2 does not have any h3 children
                        _h3_h2.append([h3_index])
                        h3_index += 1

                    _h2.append(h2_index)
                    h2_index += 1

                h3.append(_h3_h2)
                h2.append(_h2)

            else:
            # h1 does not have any h2 children

                h2.append([h2_index])
                h3.append([[h3_index]])
                h2_index += 1
                h3_index += 1

        self.table_columns_links = {'h1': h1,
                                    'h2': h2,
                                    'h3': h3,
                                    }

    def get_h_columns_from_item_name(self, item_name=None):
        # h_columns_affected = {'h1': [],
        #                       'h2': [],
        #                       'h3': [],
        #                       'list_tree_ui': [],
        #                       'list_parent_ui': []}

        if item_name == None:
            return

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
        pass
        #print("Leaving Parameters Selection UI")


class SaveConfigInterface(QDialog):

    # config_dict = {}

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

        QDialog.__init__(self, parent=grand_parent)
        self.ui = UiDialogSave()
        self.ui.setupUi(self)

        self.ui.save_as_value.setPlaceholderText("undefined")

    # def create_config_dict(self, name=''):
    #     if name == '':
    #         name = 'undefined'
    #
    #     o_current_table_config = TableConfig(parent=self.parent)
    #     current_config = o_current_table_config.get_current_config()
    #
    #     inside_dict = OrderedDict()
    #     inside_dict['table'] = current_config
    #     inside_dict['active'] = True
    #
    #     # retrieve previous config file
    #     previous_config_dict = self.parent.config_dict
    #     if previous_config_dict == {}:
    #         # first time
    #         new_full_config = OrderedDict()
    #         new_full_config[name] = inside_dict
    #     else:
    #         self.deactivate_all_config()
    #         old_full_config = self.parent.config_dict
    #         list_keys = old_full_config.keys()
    #         old_full_config[name] = inside_dict
    #         new_full_config = old_full_config
    #
    #     self.config_dict = new_full_config

    # def deactivate_all_config(self):
    #     old_full_config = self.parent.config_dict
    #     for _key in old_full_config:
    #         old_full_config[_key]['active'] = False
    #     self.parent.config_dict = old_full_config
    #
    # def export_config(self):
    #     config_dict = self.config_dict
    #     with open(CONFIG_FILE, 'wb') as handle:
    #         full_config = {}
    #         full_config['configurations'] = config_dict
    #         pickle.dump(full_config,
    #                     handle,
    #                     protocol=pickle.HIGHEST_PROTOCOL)

    def get_defined_name_config(self):
        return str(self.ui.save_as_value.text())

    def ok_clicked(self):
        name_config = self.get_defined_name_config()
        if name_config:
            self.parent.save_as_config_name_selected(name=name_config)
            # self.create_config_dict(name=name_config)
            # self.export_config()
            self.grand_parent.ui.statusbar.showMessage("New configuration saved ({})".format(name_config), 8000)
            self.grand_parent.ui.statusbar.setStyleSheet("color: green")
            self.close()

    def cancel_clicked(self):
        self.close()

class ConfigHandler:
    '''This class takes care of the config dictionary manipulations'''

    @staticmethod
    def activate_this_config(key="", config={}):
        for _key in config:
            if _key == key:
                config[_key]['active'] = True
                break
        return config

    @staticmethod
    def deactivate_all_config(config={}):
        for _key in config:
            config[_key]['active'] = False
        return config

    @staticmethod
    def lazy_export_config(config_dict={}):
        with open(CONFIG_FILE, 'wb') as handle:
            full_config = {}
            full_config['configurations'] = config_dict
            pickle.dump(full_config,
                        handle,
                        protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def remove_this_config(key="", config={}):
        new_config = OrderedDict()
        for _key in config:
            if _key == key:
                pass
            else:
                new_config[_key] = config[_key]
        return new_config

class H3TableHandler:

    # object that takes care of handling the config object
    o_save_config = None
    config_dict = {}

    def __init__(self, parent=None):
        self.parent = parent

    def retrieve_previous_configurations(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'rb') as handle:
                _cfg = pickle.load(handle)

                try:
                    config_dict = _cfg['configurations']
                except KeyError:
                    return

            self.parent.config_dict = config_dict

    def save_as_config(self):
        o_save_config = SaveConfigInterface(parent=self,
                                            grand_parent=self.parent)
        o_save_config.show()
        self.o_save_config = o_save_config

    def save_as_config_name_selected(self, name=''):
        self.create_config_dict(name=name)
        self.export_config()

    def create_config_dict(self, name=''):
        if name == '':
            name = 'undefined'

        o_current_table_config = TableConfig(parent=self.parent)
        current_config = o_current_table_config.get_current_config()

        inside_dict = OrderedDict()
        inside_dict['table'] = current_config
        inside_dict['active'] = True

        # retrieve previous config file
        previous_config_dict = self.parent.config_dict
        if previous_config_dict == {}:
            # first time
            new_full_config = OrderedDict()
            new_full_config[name] = inside_dict
        else:
            self.deactivate_all_config()
            old_full_config = self.parent.config_dict
            list_keys = old_full_config.keys()
            old_full_config[name] = inside_dict
            new_full_config = old_full_config

        self.config_dict = new_full_config

    def deactivate_all_config(self):
        old_full_config = self.parent.config_dict
        for _key in old_full_config:
            old_full_config[_key]['active'] = False
        self.parent.config_dict = old_full_config

    def export_config(self):
        config_dict = self.config_dict
        with open(CONFIG_FILE, 'wb') as handle:
            full_config = {}
            full_config['configurations'] = config_dict
            pickle.dump(full_config,
                        handle,
                        protocol=pickle.HIGHEST_PROTOCOL)

    def save_config(self):
        pass
        # retrieve the active name
        # save using name

    def reset_table(self):
        pass

    def right_click(self):

        self.retrieve_previous_configurations()
        previous_config = self.parent.config_dict
        # print("previous config in right click")
        # print(previous_config)

        if previous_config == {}:
            list_configs = []
        else:
            list_configs = previous_config.keys()

        top_menu = QMenu(self.parent)

        menu = top_menu.addMenu("Menu")
        config = menu.addMenu("Configuration ...")

        _save = config.addAction("Save")

        _save_as = config.addAction("Save As ...")

        list_signal_config_files = []
        list_signal_remove_config = []
        list_config_displayed = []

        save_state = False
        if not list_configs == []:
            config.addSeparator()
            for _label in list_configs:

                this_one_is_active = False

                if previous_config[_label]['active']:
                    self.parent.active_config_name = _label
                    _full_label = u"\u2713 " + _label
                    save_state = True
                    this_one_is_active = True

                else:
                    _full_label = u"\u200b   \u200b " + _label

                list_config_displayed.append(_label)
                temp = config.addMenu(_full_label)
                if not this_one_is_active:
                    temp_select = temp.addAction("Select")
                    list_signal_config_files.append(temp_select)

                temp_remove = temp.addAction("Remove")
                list_signal_remove_config.append(temp_remove)

        # disable "save" button if we don't have any config activated
        _save.setEnabled(save_state)

        self.parent.list_config_displayed = list_config_displayed
        menu.addSeparator()
        _reset = menu.addAction("Full Reset Table/Tree")

        action = menu.exec_(QtGui.QCursor.pos())

        if action == _save_as:
            self.save_as_config()
            return

        elif action == _save:
            #FIXME
            return

        elif action == _reset:
            self.reset_table()
            return

        if not (list_signal_config_files == []):

            for _index, _signal in enumerate(list_signal_config_files):
                if action == _signal:
                    self.activate_this_config(config=list_config_displayed[_index])

        if not (list_signal_remove_config == []):

            for _index, _signal in enumerate(list_signal_remove_config):
                if action == _signal:
                    self.remove_this_config(config=list_config_displayed[_index])

    def remove_this_config(self, config):
        config_dict = ConfigHandler.remove_this_config(config=self.parent.config_dict,
                                                       key=config)
        self.parent.config_dict = config_dict
        # import pprint
        # pprint.pprint(config_dict)
        ConfigHandler.lazy_export_config(config_dict=config_dict)

    def activate_this_config(self, config):
        config_dict = ConfigHandler.deactivate_all_config(config=self.parent.config_dict)
        config_dict = ConfigHandler.activate_this_config(config=config_dict,
                                                         key=config)
        self.parent.config_dict = config_dict
        ConfigHandler.lazy_export_config(config_dict=config_dict)
        self.parent.load_this_config(key=config)

class TableConfig:
    '''This class will look at the h1, h2 and h3 table to create the config use width and visibility of each column'''

    def __init__(self, parent=None):
        self.parent = parent

    def get_current_config(self):
        current_config_dict = {}
        current_config_dict['h1'] = self.__get_current_table_config(table='h1')
        current_config_dict['h2'] = self.__get_current_table_config(table='h2')
        current_config_dict['h3'] = self.__get_current_table_config(table='h3')
        return current_config_dict

    def __get_current_table_config(self, table='h1'):

        if table == 'h1':
            table_ui = self.parent.ui.h1_table
        elif table == 'h2':
            table_ui = self.parent.ui.h2_table
        else:
            table_ui = self.parent.ui.h3_table

        nbr_column = table_ui.columnCount()
        _dict = {}
        for _col in np.arange(nbr_column):
            _width = table_ui.columnWidth(_col)
            _visible = not table_ui.isColumnHidden(_col)
            _dict[_col] = {'width': _width,
                           'visible': _visible}

        return _dict








