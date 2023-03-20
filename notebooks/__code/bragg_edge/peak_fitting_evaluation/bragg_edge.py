import random
import os
import glob
from IPython.core.display import HTML
from IPython.display import display
import numpy as np
from collections import OrderedDict
from plotly.offline import iplot
import plotly.graph_objs as go
from ipywidgets import widgets
import pyqtgraph as pg

from qtpy.QtWidgets import QMainWindow
from qtpy import QtGui, QtCore

from __code import load_ui

from neutronbraggedge.experiment_handler import *
from neutronbraggedge.braggedge import BraggEdge as BraggEdgeLibrary
from neutronbraggedge.material_handler.retrieve_material_metadata import RetrieveMaterialMetadata
from NeuNorm.normalization import Normalization

from __code.ipywe import fileselector
from __code import file_handler
from __code.ui_roi_selection import Ui_MainWindow as UiMainWindow


class BraggEdge:

    list_of_elements = ['Fe']
    data = []
    spectra_file = None

    label_width = '15%'

    def __init__(self, working_dir='./'):
        self.working_dir = working_dir
        self.ipts_folder = working_dir

    def full_list_elements(self):
        retrieve_material = RetrieveMaterialMetadata(material='all')
        self.list_returned = retrieve_material.full_list_material()

        box4 = widgets.HBox([widgets.Label("List of elements",
                                           layout=widgets.Layout(width=self.label_width)),
                             widgets.Select(options=self.list_returned,
                                          layout=widgets.Layout(width='20%'))])

        box5 = widgets.HBox([widgets.Label("Nbr Bragg Edges",
                                           layout=widgets.Layout(width=self.label_width)),
                             widgets.IntText(8,
                                            layout=widgets.Layout(width='20%'))])

        vertical_box = widgets.VBox([box4, box5])
        display(vertical_box)

        self.list_elements_ui = box4.children[1]
        self.nbr_bragg_edges_ui = box5.children[1]

    def list_elements(self):
        retrieve_material = RetrieveMaterialMetadata(material='all')
        self.list_returned = retrieve_material.full_list_material()

        # import pprint
        # pprint.pprint(list_returned)

        box4 = widgets.HBox([widgets.Label("List of elements",
                                           layout=widgets.Layout(width=self.label_width)),
                             widgets.Text(','.join(self.list_of_elements),
                                          layout=widgets.Layout(width='20%'))])

        box5 = widgets.HBox([widgets.Label("Nbr Bragg Edges",
                                           layout=widgets.Layout(width=self.label_width)),
                             widgets.Text(str(8),
                                          layout=widgets.Layout(width='20%'))])

        vertical_box = widgets.VBox([box4, box5])
        display(vertical_box)

        self.list_elements_ui = box4.children[1]
        self.nbr_bragg_edges_ui = box5.children[1]

    def exp_setup(self):

        box2 = widgets.HBox([widgets.Label("dSD (m)",
                                           layout=widgets.Layout(width=self.label_width)),
                             widgets.Text(str(16.08),
                                          layout=widgets.Layout(width='20%'))])

        box3 = widgets.HBox([widgets.Label("detector offset (microS)",
                                           layout=widgets.Layout(width=self.label_width)),
                             widgets.Text(str(3700),
                                          layout=widgets.Layout(width='20%'))])

        vertical_box = widgets.VBox([box2, box3])
        display(vertical_box)

        self.dSD_ui = box2.children[1]
        self.detector_offset_ui = box3.children[1]

    def list_powder_bragg_edges(self):

        list_of_elements_selected = self.list_elements_ui.value
        list_of_elements = list_of_elements_selected.split(',')
        list_of_elements = [_element.strip() for _element in list_of_elements]
        number_of_bragg_edges = int(self.nbr_bragg_edges_ui.value)

        _handler = BraggEdgeLibrary(material=list_of_elements,
                                    number_of_bragg_edges=number_of_bragg_edges)
        self.bragg_edges = _handler.bragg_edges
        self.hkl = _handler.hkl
        self.handler = _handler

        print(_handler)

    def select_working_folder(self):
        select_data = fileselector.FileSelectorPanel(instruction='Select Data Folder ...',
                                                     start_dir=self.working_dir,
                                                     next=self.load_data,
                                                     type='directory',
                                                     multiple=False)
        select_data.show()

    def load_data(self, folder_selected):
        list_files = glob.glob(os.path.join(folder_selected, '*.fits'))

        if list_files == []:
            list_files = glob.glob(os.path.join(folder_selected, '*.tif*'))

        else: #fits
            # keep only files of interest
            list_files = [file for file in list_files if not "_SummedImg.fits" in file]
            list_files = [file for file in list_files if ".fits" in file]

        # sort list of files
        list_files.sort()

        o_norm = Normalization()
        o_norm.load(file=list_files, notebook=True)

        self.data = o_norm.data['sample']['data']
        self.list_files = o_norm.data['sample']['file_name']

        display(HTML('<span style="font-size: 20px; color:blue">' + str(len(list_files)) + \
                     ' files have been loaded</span>'))

        # define time spectra file
        folder = os.path.dirname(self.list_files[0])
        spectra_file = glob.glob(os.path.join(folder, '*_Spectra.txt'))
        if spectra_file:
            self.spectra_file = spectra_file[0]
            display(HTML('<span style="font-size: 20px; color:blue"> Spectra File automatically located: ' + \
                         self.spectra_file + '</span>'))

        else:
            #ask for spectra file
            self.select_time_spectra_file()

    def load_time_spectra(self):
        _tof_handler = TOF(filename=self.spectra_file)
        _exp = Experiment(tof=_tof_handler.tof_array,
                          distance_source_detector_m=float(self.dSD_ui.value),
                          detector_offset_micros=float(self.detector_offset_ui.value))
        self.lambda_array = _exp.lambda_array * 1e10  # to be in Angstroms
        self.tof_array = _tof_handler.tof_array

    def save_time_spectra(self, file):
        self.spectra_file = file
        display(HTML('<span style="font-size: 20px; color:blue"> Spectra File : ' + \
                     self.spectra_file + '</span>'))

    def select_time_spectra_file(self):
        self.working_dir = os.path.dirname(self.list_files[0])

        self.time_spectra_ui = fileselector.FileSelectorPanel(instruction='Select Time Spectra File ...',
                                                              start_dir=self.working_dir,
                                                              next=self.save_time_spectra,
                                                              filters={'spectra_file': "_Spectra.txt"},
                                                              multiple=False)
        self.time_spectra_ui.show()

    def select_just_time_spectra_file(self):
        self.time_spectra_ui = fileselector.FileSelectorPanel(instruction='Select Time Spectra File ...',
                                                              start_dir=self.working_dir,
                                                              filters={'spectra_file': "*_Spectra.txt"},
                                                              multiple=False)
        self.time_spectra_ui.show()

    def how_many_data_to_use_to_select_sample_roi(self):
        nbr_images = len(self.data)
        init_value = int(nbr_images/10)
        if init_value == 0:
            init_value = 1
        box1 = widgets.HBox([widgets.Label("Nbr of images to use:",
                                           layout=widgets.Layout(width='15')),
                             widgets.IntSlider(value=init_value,
                                               max=nbr_images,
                                               min=1,
                                               layout=widgets.Layout(width='50%'))])
        box2 = widgets.Label("(The more you select, the longer it will take to display the preview!)")
        vbox = widgets.VBox([box1, box2])
        display(vbox)
        self.number_of_data_to_use_ui = box1.children[1]

    def define_sample_roi(self):
        nbr_data_to_use = int(self.number_of_data_to_use_ui.value)
        nbr_images = len(self.data)
        list_of_indexes_to_keep = random.sample(list(range(nbr_images)), nbr_data_to_use)
        final_array = []
        for _index in list_of_indexes_to_keep:
            final_array.append(self.data[_index])
        final_image = np.mean(final_array, axis=0)
        self.final_image = final_image

    def define_integrated_sample_to_use(self):
        nbr_data_to_use = int(self.number_of_data_to_use_ui.value)
        nbr_images = len(self.data)
        list_of_indexes_to_keep = random.sample(list(range(nbr_images)), nbr_data_to_use)
        final_array = []
        for _index in list_of_indexes_to_keep:
            final_array.append(self.data[_index])
        final_image = np.mean(final_array, axis=0)
        self.final_image = final_image

    def calculate_counts_vs_file_index_of_regions_selected(self, list_roi=[]):

        counts_vs_file_index = []
        for _data in self.data:

            _array_data = []

            for _roi in list_roi.keys():

                x0 = int(list_roi[_roi]['x0'])
                y0 = int(list_roi[_roi]['y0'])
                x1 = int(list_roi[_roi]['x1'])
                y1 = int(list_roi[_roi]['y1'])

                _array_data.append(np.mean(_data[y0:y1, x0:x1]))

            counts_vs_file_index.append(np.mean(_array_data))

        self.counts_vs_file_index = counts_vs_file_index

    def plot(self):

        bragg_edges = self.bragg_edges
        hkl = self.hkl
        lambda_array = self.lambda_array
        sum_cropped_data = self.final_image

        # format hkl labels
        _hkl_formated = {}
        for _material in hkl:
            _hkl_string = []
            for _hkl in hkl[_material]:
                _hkl_s = ",".join(str(x) for x in _hkl)
                _hkl_s = _material + "\n" + _hkl_s
                _hkl_string.append(_hkl_s)
            _hkl_formated[_material] = _hkl_string

        trace = go.Scatter(
            x=self.lambda_array,
            y=self.counts_vs_file_index,
            mode='markers')

        layout = go.Layout(
            width=1000,
            height=500,
            title="Sum Counts vs TOF",
            xaxis=dict(
                title="Lambda (Angstroms)"
            ),
            yaxis=dict(
                title="Sum Counts"
            ),
        )

        max_x = 6
        y_off = 1

        data = [trace]
        figure = go.Figure(data=data, layout=layout)

        for y_index, _material in enumerate(bragg_edges):
            for _index, _value in enumerate(bragg_edges[_material]):
                if _value > max_x:
                    continue
                bragg_line = {"type": "line",
                              'x0': _value,
                              'x1': _value,
                              'yref': "paper",
                              'y0': 0,
                              'y1': 1,
                              'line': {
                                  'color': 'rgb(255, 0, 0)',
                                  'width': 1
                              }}
                figure.add_shape(bragg_line)
                # layout.shapes.append(bragg_line)
                y_off = 1 - 0.25 * y_index

                # add labels to plots
                _annot = dict(
                    x=_value,
                    y=y_off,
                    text=_hkl_formated[_material][_index],
                    yref="paper",
                    font=dict(
                        family="Arial",
                        size=16,
                        color="rgb(150,50,50)"
                    ),
                    showarrow=True,
                    arrowhead=3,
                    ax=0,
                    ay=-25)

                figure.add_annotation(_annot)

        # figure = go.Figure(data=data, layout=layout)
        iplot(figure)

    def select_output_folder(self):
        self.select_folder(message='output',
                           next_function=self.export_table)

    def export_table(self, output_folder):
        material = self.handler.material[0]
        lattice = self.handler.lattice[material]
        crystal_structure = self.handler.crystal_structure[material]
        metadata = ["# material: {}".format(material),
                    "# crystal structure: {}".format(crystal_structure),
                    "# lattice: {} Angstroms".format(lattice),
                    "#",
                    "# hkl, d(angstroms), BraggEdge"]
        data = []
        bragg_edges = self.bragg_edges[material]
        hkl = self.hkl[material]
        for _index in np.arange(len(bragg_edges)):
            _hkl_str = [str(i) for i in hkl[_index]]
            _hkl = "".join(_hkl_str)
            _bragg_edges = float(bragg_edges[_index])
            _d = _bragg_edges/2.
            _row = "{}, {}, {}".format(_hkl, _d, _bragg_edges)
            data.append(_row)

        output_file_name = os.path.join(output_folder, 'bragg_edges_of_{}.txt'.format(material))

        file_handler.make_ascii_file(metadata=metadata,
                                     data=data,
                                     dim='1d',
                                     output_file_name=output_file_name)

        display(HTML('<span style="font-size: 20px; color:blue">File created : ' + \
                     output_file_name + '</span>'))

    def select_folder(self, message="", next_function=None):
        folder_widget = fileselector.FileSelectorPanel(instruction='select {} folder'.format(message),
                                                       start_dir=self.working_dir,
                                                       next=next_function,
                                                       type='directory',
                                                       multiple=False)
        folder_widget.show()


class Interface(QMainWindow):

    roi_width = 0.01
    roi_selected = {} #nice formatting of list_roi for outside access

    live_data = []
    o_norm = None
    roi_column_width = 70
    integrated_image = None
    integrated_image_size = {'width': -1, 'height': -1}

    list_roi = {} #  'row": {'x0':None, 'y0': None, 'x1': None, 'y1': None}
    default_roi = {'x0': 0, 'y0': 0, 'x1': 50, 'y1': 50, 'id': None}

    def __init__(self, parent=None, data=None, instruction="", next=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that popped up \
            (maybe hidden behind this browser!)</span>'))

        self.live_data = data
        self.next = next

        super(QMainWindow, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_roi_selection.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

        # QMainWindow.__init__(self, parent=parent)
        # self.ui = UiMainWindow()
        # self.ui.setupUi(self)

        self.init_statusbar()
        self.setWindowTitle("Background ROI Selection Tool")

        self.ui.image_view = pg.ImageView()
        self.ui.image_view.ui.roiBtn.hide()
        self.ui.image_view.ui.menuBtn.hide()

        top_layout = QtGui.QVBoxLayout()
        top_layout.addWidget(self.ui.image_view)
        self.ui.widget.setLayout(top_layout)
        self.init_widgets(instruction=instruction)
        self.integrate_images()
        self.display_image()

    def init_widgets(self, instruction=""):
        nbr_columns = self.ui.table_roi.columnCount()
        for _col in range(nbr_columns):
            self.ui.table_roi.setColumnWidth(_col, self.roi_column_width)

        if instruction == "":
            self.ui.instruction.setVisible(False)
        else:
            self.ui.instruction.setText(instruction)

    def init_statusbar(self):
        self.eventProgress = QtGui.QProgressBar(self.ui.statusbar)
        self.eventProgress.setMinimumSize(20, 14)
        self.eventProgress.setMaximumSize(540, 100)
        self.eventProgress.setVisible(False)
        self.ui.statusbar.addPermanentWidget(self.eventProgress)

    # def __get_recap(self, data_array):
    #     if data_array:
    #         [height, width] = np.shape(data_array[0])
    #         nbr_sample = len(data_array)
    #     else:
    #         nbr_sample = '0'
    #         [height, width] = ['N/A', 'N/A']
    #
    #     return [nbr_sample, height, width]

    # def __built_html_table_row_3_columns(self, name, nbr, height, width):
    #     _html = '<tr><td>' + str(name) + '</td><td>' + str(nbr) + '</td><td>' + str(height) + \
    #     '*' + str(width) + '</td></tr>'
    #     return _html
    #
    # def recap(self):
    #     """Display nbr of files loaded and size. This can be used to figure why a normalization failed"""
    #     [nbr_sample, height_sample, width_sample] = self.__get_recap(self.o_norm.data['sample']['data'])
    #     [nbr_ob, height_ob, width_ob] = self.__get_recap(self.o_norm.data['ob']['data'])
    #     [nbr_df, height_df, width_df] = self.__get_recap(self.o_norm.data['df']['data'])
    #
    #     html =  '<table><tr><td width="30%"><strong>Type</strong></td><td><strong>Number</strong></td><td>' + \
    #             '<strong>Size (height*width)</strong></td></tr>'
    #     html += self.__built_html_table_row_3_columns('sample', nbr_sample, height_sample, width_sample)
    #     html += self.__built_html_table_row_3_columns('ob', nbr_ob, height_ob, width_ob)
    #     html += self.__built_html_table_row_3_columns('df', nbr_df, height_df, width_df)
    #     html += '</table>'
    #     display(HTML(html))

    def integrate_images(self):
        self.integrated_image = self.live_data
        [_height, _width] = np.shape(self.integrated_image)
        self.integrated_image_size['height'] = _height
        self.integrated_image_size['width'] = _width

    def _clean_image(self, image):
        _result_inf = np.where(np.isinf(image))
        image[_result_inf] = np.NaN
        return image

    def display_image(self):
        _image = np.transpose(self.live_data)
        _image = self._clean_image(_image)
        self.ui.image_view.setImage(_image)

    def remove_row_entry(self, row):
        _roi_id = self.list_roi[row]['id']
        self.ui.image_view.removeItem(_roi_id)
        del self.list_roi[row]

        #rename row
        new_list_roi = {}
        new_row_index = 0
        for _previous_row_index in self.list_roi.keys():
            new_list_roi[new_row_index] = self.list_roi[_previous_row_index]
            new_row_index += 1
        self.list_roi = new_list_roi

    def remove_roi_button_clicked(self):

        self.ui.table_roi.blockSignals(True)

        _selection = self.ui.table_roi.selectedRanges()
        row = _selection[0].topRow()
        old_nbr_row = self.ui.table_roi.rowCount()

        # remove entry from list of roi
        self.remove_row_entry(row)

        # update table of rois
        self.update_table_roi_ui()
        self.ui.table_roi.blockSignals(False)
        self.check_add_remove_button_widgets_status()

        # update selection
        new_nbr_row = self.ui.table_roi.rowCount()
        if new_nbr_row == 0:
            return

        if row == (old_nbr_row-1):
            row = new_nbr_row - 1

        _new_selection = QtGui.QTableWidgetSelectionRange(row, 0, row, 3)
        self.ui.table_roi.setRangeSelected(_new_selection, True)

    def clear_table(self):
        nbr_row = self.ui.table_roi.rowCount()
        for _row in np.arange(nbr_row):
            self.ui.table_roi.removeRow(0)

    def update_table_roi_ui(self):
        """Using list_roi as reference, repopulate the table_roi_ui"""

        self.ui.table_roi.blockSignals(True)
        list_roi = self.list_roi

        self.clear_table()

        _index_row = 0
        for _roi_key in list_roi.keys():
            _roi = list_roi[_roi_key]

            self.ui.table_roi.insertRow(_index_row)

            self._set_item_value(_index_row, 0, _roi['x0'])
            # _item = QtGui.QTableWidgetItem(str(_roi['x0']))
            # self.ui.table_roi.setItem(_index_row, 0, _item)

            self._set_item_value(_index_row, 1, _roi['y0'])
            # _item = QtGui.QTableWidgetItem(str(_roi['y0']))
            # self.ui.table_roi.setItem(_index_row, 1, _item)

            self._set_item_value(_index_row, 2, _roi['x1'])
            # _item = QtGui.QTableWidgetItem(str(_roi['x1']))
            # self.ui.table_roi.setItem(_index_row, 2, _item)

            self._set_item_value(_index_row, 3, _roi['y1'])
            # _item = QtGui.QTableWidgetItem(str(_roi['y1']))
            # self.ui.table_roi.setItem(_index_row, 3, _item)

            _index_row += 1

        self.ui.table_roi.blockSignals(False)
        #self.ui.table_roi.itemChanged['QTableWidgetItem*'].connect(self.update_table_roi)

    def _set_item_value(self, row=0, column=0, value=-1):
        _item = QtGui.QTableWidgetItem(str(value))
        self.ui.table_roi.setItem(row, column, _item)

    def check_roi_validity(self, value, x_axis=True):
        """Make sure the ROI selected or defined stays within the image size"""
        min_value = 0

        value = int(value)

        if x_axis:
            max_value = self.integrated_image_size['width']
        else:
            max_value = self.integrated_image_size['height']

        if value < 0:
            return min_value

        if value > max_value:
            return max_value

        return value

    def update_table_roi(self, item):
        """Using the table_roi_ui as reference, will update the list_roi dictionary"""
        self.ui.table_roi.blockSignals(True)

        nbr_row = self.ui.table_roi.rowCount()
        new_list_roi = OrderedDict()
        old_list_roi = self.list_roi
        for _row in np.arange(nbr_row):
            _roi = {}

            # checking that x0, y0, x1 and y1 stay within the range of the image
            _x0 = self.check_roi_validity(self._get_item_value(_row, 0))
            _y0 = self.check_roi_validity(self._get_item_value(_row, 1), x_axis=False)

            _x1 = self.check_roi_validity(self._get_item_value(_row, 2))
            _y1 = self.check_roi_validity(self._get_item_value(_row, 3), x_axis=False)

            # updating table content (in case some of the roi were out of scope
            self._set_item_value(_row, 0, _x0)
            self._set_item_value(_row, 1, _y0)
            self._set_item_value(_row, 2, _x1)
            self._set_item_value(_row, 3, _y1)

            _roi['x0'] = _x0
            _roi['y0'] = _y0
            _roi['x1'] = _x1
            _roi['y1'] = _y1
            _roi['id'] = old_list_roi[_row]['id']

            new_list_roi[_row] = _roi

        self.list_roi = new_list_roi
        self.update_image_view_item()
        self.ui.table_roi.blockSignals(False)

    def update_image_view_item(self):
        self.clear_roi_on_image_view()

        list_roi = self.list_roi
        for _row in list_roi.keys():
            _roi = list_roi[_row]

            _x0 = int(_roi['x0'])
            _y0 = int(_roi['y0'])
            _x1 = int(_roi['x1'])
            _y1 = int(_roi['y1'])

            _width = np.abs(_x1 - _x0)
            _height = np.abs(_y1 - _y0)

            _roi_id = self.init_roi(x0=_x0, y0=_y0,
                                    width=_width, height=_height)
            _roi['id'] = _roi_id

            list_roi[_row] = _roi

        self.list_roi = list_roi

    def _get_item_value(self, row, column):
        _item = self.ui.table_roi.item(row, column)
        if _item:
            return str(_item.text())
        else:
            return ''

    def roi_manually_moved(self):
        list_roi = self.list_roi

        for _row in list_roi.keys():

            _roi = list_roi[_row]

            roi_id = _roi['id']
            region = roi_id.getArraySlice(self.integrated_image, self.ui.image_view.imageItem)

            x0 = region[0][0].start
            x1 = region[0][0].stop
            y0 = region[0][1].start
            y1 = region[0][1].stop

            _roi['x0'] = x0
            _roi['x1'] = x1
            _roi['y0'] = y0
            _roi['y1'] = y1

            list_roi[_row] = _roi

        self.list_roi = list_roi
        self.update_table_roi_ui()

    def clear_roi_on_image_view(self):
        list_roi = self.list_roi

        for _row in list_roi.keys():

            _roi = list_roi[_row]
            roi_id = _roi['id']
            self.ui.image_view.removeItem(roi_id)

    def add_roi_button_clicked(self):
        self.clear_roi_on_image_view()

        self.ui.table_roi.blockSignals(True)
        _selection = self.ui.table_roi.selectedRanges()
        if _selection:
            row = _selection[0].topRow()
        else:
            row = 0

        # init new row with default value
        self.ui.table_roi.insertRow(row)
        _default_roi = self.default_roi

        _item = QtGui.QTableWidgetItem(str(_default_roi['x0']))
        self.ui.table_roi.setItem(row, 0, _item)

        _item = QtGui.QTableWidgetItem(str(_default_roi['y0']))
        self.ui.table_roi.setItem(row, 1, _item)

        _item = QtGui.QTableWidgetItem(str(_default_roi['x1']))
        self.ui.table_roi.setItem(row, 2, _item)

        _item = QtGui.QTableWidgetItem(str(_default_roi['y1']))
        self.ui.table_roi.setItem(row, 3, _item)

        # save new list_roi dictionary
        nbr_row = self.ui.table_roi.rowCount()
        list_roi = OrderedDict()
        for _row in np.arange(nbr_row):
            _roi = {}

            _x0 = self._get_item_value(_row, 0)
            _roi['x0'] = int(_x0)

            _y0 = self._get_item_value(_row, 1)
            _roi['y0'] = int(_y0)

            _x1 = self._get_item_value(_row, 2)
            _roi['x1'] = int(_x1)

            _y1 = self._get_item_value(_row, 3)
            _roi['y1'] = int(_y1)

            x0_int = int(_x0)
            y0_int = int(_y0)
            width_int = np.abs(x0_int - int(_x1))
            height_int = np.abs(y0_int - int(_y1))

            _roi_id = self.init_roi(x0=x0_int, y0=y0_int,
                                    width=width_int, height=height_int)
            _roi['id'] = _roi_id
            list_roi[_row] = _roi

        self.list_roi = list_roi

        self.ui.table_roi.blockSignals(False)

        self.check_add_remove_button_widgets_status()

        if not _selection:
            _new_selection = QtGui.QTableWidgetSelectionRange(0, 0, 0, 3)
            self.ui.table_roi.setRangeSelected(_new_selection, True)

    def init_roi(self, x0=0, y0=0, width=0, height=0):
        _color = QtGui.QColor(62, 13, 244)
        _pen = QtGui.QPen()
        _pen.setColor(_color)
        _pen.setWidthF(self.roi_width)
        _roi_id = pg.ROI([x0, y0], [width, height], pen=_pen, scaleSnap=True)
        _roi_id.addScaleHandle([1, 1], [0, 0])
        _roi_id.addScaleHandle([0, 0], [1, 1])
        self.ui.image_view.addItem(_roi_id)
        # add connection to roi
        _roi_id.sigRegionChanged.connect(self.roi_manually_moved)
        return _roi_id

    def check_add_remove_button_widgets_status(self):
        nbr_row = self.ui.table_roi.rowCount()
        if nbr_row > 0:
            self.ui.remove_roi_button.setEnabled(True)
        else:
            self.ui.remove_roi_button.setEnabled(False)

    def format_roi(self):
        roi_selected = {}
        for _key in self.list_roi.keys():
            _roi = self.list_roi[_key]
            x0 = _roi['x0']
            y0 = _roi['y0']
            x1 = _roi['x1']
            y1 = _roi['y1']
            new_entry = {'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1}
            roi_selected[_key] = new_entry

        self.roi_selected = roi_selected

    def apply_clicked(self):
        self.update_table_roi(None) #check ROI before leaving application
        self.format_roi()
        self.close()

    def cancel_clicked(self):
        self.close()

    def closeEvent(self, eventhere=None):
        if self.next:
            self.next()
