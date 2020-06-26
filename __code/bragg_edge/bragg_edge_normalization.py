import ipywe.fileselector
import random
import os
import glob
from pathlib import Path
from IPython.core.display import HTML
from IPython.display import display
import numpy as np
from plotly.offline import iplot
import plotly.graph_objs as go
from ipywidgets import widgets

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from neutronbraggedge.experiment_handler import *
from NeuNorm.normalization import Normalization
from NeuNorm.roi import ROI

from __code import file_handler
from __code.bragg_edge.bragg_edge import BraggEdge as BraggEdgeParent
from __code.file_folder_browser import FileFolderBrowser


class BraggEdge(BraggEdgeParent):

    def load_data(self, folder_selected):
        self.o_norm = Normalization()
        self.load_files(data_type='sample', folder=folder_selected)

        # define time spectra file
        folder = os.path.dirname(self.o_norm.data['sample']['file_name'][0])
        self.list_files = self.o_norm.data['sample']['file_name']
        spectra_file = glob.glob(os.path.join(folder, '*_Spectra.txt'))
        if spectra_file:
            self.spectra_file = spectra_file[0]
            display(HTML('<span style="font-size: 15px; color:blue"> Spectra File automatically located: ' + \
                         self.spectra_file + '</span>'))

        else:
            #ask for spectra file
            self.select_time_spectra_file()

    def select_time_spectra_file(self):
        self.working_dir = os.path.dirname(self.list_files[0])

        self.time_spectra_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Time Spectra File ...',
                                                                    start_dir=self.working_dir,
                                                                    next=self.save_time_spectra,
                                                                    filters={'spectra_file': "_Spectra.txt"},
                                                                    multiple=False)

        self.time_spectra_ui.show()
        self.cancel_button = widgets.Button(description="or Do Not Select any Time Spectra",
                                            button_style="info",
                                            layout=widgets.Layout(width='100%'))
        display(self.cancel_button)
        self.cancel_button.on_click(self.cancel_time_spectra_selection)

    def save_time_spectra(self, file):
        BraggEdgeParent.save_time_spectra(self, file)
        self.cancel_button.close()

    def cancel_time_spectra_selection(self, value):
        self.time_spectra_ui.remove()
        self.cancel_button.close()
        display(HTML('<span style="font-size: 20px; color:blue">NO Spectra File loaded! </span>'))

    def load_files(self, data_type='sample', folder=None):

        self.starting_dir = os.path.dirname(folder)
        list_files = glob.glob(os.path.join(folder, '*.fits'))

        if list_files == []:
            list_files = glob.glob(os.path.join(folder, '*.tif*'))

        else:  # fits
            # keep only files of interest
            list_files = [file for file in list_files if not "_SummedImg.fits" in file]
            list_files = [file for file in list_files if ".fits" in file]

        # sort list of files
        list_files.sort()

        self.o_norm.load(file=list_files, notebook=True, data_type=data_type)

        display(HTML('<span style="font-size: 15px; color:blue">' + str(len(list_files)) + \
                     ' files have been loaded as ' + data_type + '</span>'))

    def select_ob_folder(self):
        select_data = ipywe.fileselector.FileSelectorPanel(instruction='Select OB Folder ...',
                                                            start_dir=self.starting_dir,
                                                            next=self.load_ob,
                                                            type='directory',
                                                            multiple=False)
        select_data.show()

    def load_ob(self, folder_selected):
        self.load_files(data_type='ob', folder=folder_selected)
        self.check_data_array_sizes()

    def check_data_array_sizes(self):
        len_ob = len(self.o_norm.data['ob']['file_name'])
        len_sample = len(self.o_norm.data['sample']['file_name'])

        if len_ob == len_sample:
            display(HTML('<span style="font-size: 15px; color:green"> Sample and OB have the same size!</span>'))
            return

        if len_ob < len_sample:
            self.o_norm.data['sample']['data'] = self.o_norm.data['sample']['data'][0:len_ob]
            self.o_norm.data['sample']['file_name'] = self.o_norm.data['sample']['file_name'][0:len_ob]
            display(HTML('<span style="font-size: 15px; color:green"> Truncated Sample array to match OB!</span>'))
        else:
            self.o_norm.data['ob']['data'] = self.o_norm.data['ob']['data'][0:len_sample]
            self.o_norm.data['ob']['file_name'] = self.o_norm.data['ob']['file_name'][0:len_sample]
            display(HTML('<span style="font-size: 15px; color:green"> Truncated OB array to match Sample!</span>'))

    def load_time_spectra(self):
        _tof_handler = TOF(filename=self.spectra_file)
        _exp = Experiment(tof=_tof_handler.tof_array,
                          distance_source_detector_m=np.float(self.dSD_ui.value),
                          detector_offset_micros=np.float(self.detector_offset_ui.value))

        nbr_sample = len(self.o_norm.data['sample']['file_name'])

        self.lambda_array = _exp.lambda_array[0: nbr_sample] * 1e10 # to be in Angstroms
        self.tof_array = _tof_handler.tof_array[0: nbr_sample]

    def how_many_data_to_use_to_select_sample_roi(self):
        nbr_images = len(self.o_norm.data['sample']['data'])
        init_value = np.int(nbr_images/10)
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

    def get_image_to_use_for_display(self):
        nbr_data_to_use = np.int(self.number_of_data_to_use_ui.value)
        _data = self.o_norm.data['sample']['data']

        nbr_images = len(_data)
        list_of_indexes_to_keep = random.sample(list(range(nbr_images)), nbr_data_to_use)

        final_array = []
        for _index in list_of_indexes_to_keep:
            final_array.append(_data[_index])
        final_image = np.mean(final_array, axis=0)
        self.final_image = final_image
        return final_image

    def normalization(self, list_rois=None):
        if list_rois is None:
            self.o_norm.normalization()
        else:
            list_o_roi = []
            for key in list_rois.keys():
                roi = list_rois[key]
                _x0 = roi['x0']
                _y0 = roi['y0']
                _x1 = roi['x1']
                _y1 = roi['y1']

                list_o_roi.append(ROI(x0=_x0,
                                      y0=_y0,
                                      x1=_x1,
                                      y1=_y1))

            self.o_norm.normalization(roi=list_o_roi, notebook=True)
        display(HTML('<span style="font-size: 15px; color:green"> Normalization DONE! </span>'))

    def export_normalized_data(self):
        self.o_folder = FileFolderBrowser(working_dir=self.working_dir,
                                          next_function=self.export_normalized_data_step2,
                                          ipts_folder=self.ipts_folder)
        self.o_folder.select_output_folder_with_new(instruction="Select where to create the normalized data ...")

    def export_normalized_data_step2(self, output_folder):
        self.o_folder.list_output_folders_ui.shortcut_buttons.close()

        normalized_export_folder = str(Path(output_folder) / (self.starting_dir + '_normalized'))
        file_handler.make_or_reset_folder(normalized_export_folder)

        self.o_norm.export(folder=normalized_export_folder)
        display(HTML('<span style="font-size: 15px; color:green"> Created the normalized data in the folder ' +
                     normalized_export_folder + '</span>'))
        if self.spectra_file:
            file_handler.copy_files_to_folder(list_files=[self.spectra_file],
                                              output_folder=normalized_export_folder)
            display(HTML('<span style="font-size: 15px; color:green"> Copied time spectra file to same folder </span>'))

    def calculate_counts_vs_file_index_of_regions_selected(self, list_roi=None):

        self.list_roi = list_roi
        normalized_data = self.o_norm.get_normalized_data()

        nbr_data = len(normalized_data)
        box_ui = widgets.HBox([widgets.Label("Calculate Counts vs lambda",
                                             layout=widgets.Layout(width='20%')),
                               widgets.IntProgress(min=0,
                                                   max=nbr_data,
                                                   value=0,
                                                   layout=widgets.Layout(width='50%'))])
        progress_bar = box_ui.children[1]
        display(box_ui)

        counts_vs_file_index = []
        for _index, _data in enumerate(normalized_data):

            if len(list_roi) == 0:
                _array_data = _data

            else:
                _array_data = []
                for _roi in list_roi.keys():

                    x0 = np.int(list_roi[_roi]['x0'])
                    y0 = np.int(list_roi[_roi]['y0'])
                    x1 = np.int(list_roi[_roi]['x1'])
                    y1 = np.int(list_roi[_roi]['y1'])

                    _array_data.append(np.nanmean(_data[y0:y1, x0:x1]))

            counts_vs_file_index.append(np.nanmean(_array_data))

            progress_bar.value = _index+1

        self.counts_vs_file_index = counts_vs_file_index
        box_ui.close()

    def plot(self):

        trace = go.Scatter(
            x=self.lambda_array,
            y=self.counts_vs_file_index,
            mode='markers')

        layout = go.Layout(
            height=500,
            title="Counts vs TOF (of entire images, or of selected region if any)",
            xaxis=dict(
                title="Lambda (Angstroms)"
            ),
            yaxis=dict(
                title="Average Counts"
            ),
        )

        data = [trace]
        figure = go.Figure(data=data, layout=layout)

        iplot(figure)

    def select_output_data_folder(self):
        o_folder = FileFolderBrowser(working_dir=self.working_dir,
                                     next_function=self.export_data)
        o_folder.select_output_folder(instruction="Select where to create the ascii file...")
        # self.select_folder(message='Select where to output the data',
        #                    next_function=self.export_data)

    def make_output_file_name(self, output_folder='', input_folder=''):
        file_name = os.path.basename(input_folder) + "_counts_vs_lambda_tof.txt"
        return os.path.join(os.path.abspath(output_folder), file_name)

    def export_data(self, output_folder):
        input_folder = os.path.dirname(self.o_norm.data['sample']['file_name'][0])
        ob_folder = os.path.dirname(self.o_norm.data['ob']['file_name'][0])
        output_file_name = self.make_output_file_name(output_folder=output_folder,
                                                      input_folder=input_folder)

        lambda_array = self.lambda_array
        counts_vs_file_index = self.counts_vs_file_index
        tof_array = self.tof_array

        metadata = ["# input folder: {}".format(input_folder)]
        metadata.append("# ob folder: {}".format(ob_folder))

        list_roi = self.list_roi
        if len(list_roi) == 0:
            metadata.append("# Entire sample selected")
        else:
            for index, key in enumerate(list_roi.keys()):
                roi = list_roi[key]
                _x0 = roi['x0']
                _y0 = roi['y0']
                _x1 = roi['x1']
                _y1 = roi['y1']
                metadata.append("# ROI {}: x0={}, y0={}, x1={}, y1={}".format(index,
                                                                              _x0,
                                                                              _y0,
                                                                              _x1,
                                                                              _y1))
        metadata.append("#")
        metadata.append("# tof (micros), lambda (Angstroms), Average counts")

        data = []
        for _t, _l, _c in zip(tof_array, lambda_array, counts_vs_file_index):
            data.append("{}, {}, {}".format(_t, _l, _c))

        file_handler.make_ascii_file(metadata=metadata,
                                     data=data,
                                     output_file_name=output_file_name,
                                     dim='1d')

        if os.path.exists(output_file_name):
            display(HTML('<span style="font-size: 20px; color:blue">Ascii file ' + output_file_name + ' has been ' +
                         'created  </span>'))
        else:
            display(HTML('<span style="font-size: 20px; color:red">Error exporting Ascii file ' + output_file_name +
                         '</span>'))

    def select_output_table_folder(self):
        o_folder = FileFolderBrowser(working_dir=self.working_dir,
                                     next=self.export_table)
        o_folder.select_output_folder()

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
            _bragg_edges = np.float(bragg_edges[_index])
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
        folder_widget = ipywe.fileselector.FileSelectorPanel(instruction='select {} folder'.format(message),
                                                             start_dir=self.working_dir,
                                                             next=next_function,
                                                             type='directory',
                                                             multiple=False)
        folder_widget.show()
