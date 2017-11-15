import ipywe.fileselector
import numpy as np
import os
from NeuNorm.normalization import Normalization

import __code.file_handler as file_handler

from IPython.core.display import display
from ipywidgets import widgets

class NormalizationPerRange(object):

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_input_folder(self):
        self.input_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Input Folder',
                                                                    type='directory',
                                                                    start_dir=self.working_dir,
                                                                    multiple=False)
        self.input_folder_ui.show()

    def load_stack(self):
        self.o_norm = Normalization()
        self.working_folder = self.input_folder_ui.selected
        self.o_norm.load(folder=self.working_folder, notebook=True)

    def select_range(self):
        self.range_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Left Image',
                                                        start_dir=self.working_folder,
                                                        multiple=True)
        self.range_ui.show()

    def load_and_calculate_mean_frame(self):
        self.o_range = Normalization()
        self.o_range.load(file=self.range_ui.selected, notebook=True)

        self.mean_frame = np.mean(self.o_range.data['sample']['data'], axis=0)

    def define_contrast_enhancement_factor(self):
        self.f_ui = widgets.FloatSlider(value=0.75,
                                   min=0,
                                   max=1,
                                   step=0.01,
                                   description='Factor f',
                                   readout_format='.2f')
        display(self.f_ui)

    def calculate_contrast_enhancement_images(self):
        self.short_list_files = [os.path.basename(_file) for _file in self.o_norm.data['sample']['file_name']]
        data = self.o_norm.data['sample']['data']
        self.factor = self.f_ui.value

        w = widgets.IntProgress()
        w.max = len(self.short_list_files) - 1
        display(w)

        self.data_enhanced = []
        for index, _data in enumerate(data):
            _new_data = _data - self.factor * self.mean_frame
            self.data_enhanced.append(_new_data)
            w.value = index + 1

    def select_export_folder(self):
        self.export_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Export Folder',
                                                                start_dir=self.working_dir,
                                                                type='directory',
                                                                multiple=False)
        self.export_folder_ui.show()

    def define_output_folder_name(self):
        default_output_folder = os.path.basename(self.input_folder_ui.selected) + \
                                '_enhanced_f_{}'.format(self.factor)
        hbox = widgets.HBox([widgets.Label("Output Folder Name",
                                           layout=widgets.Layout(width='15%')),
                             widgets.Text(value=default_output_folder,
                                          layout=widgets.Layout(width='50%'))])
        self.output_folder_ui = hbox.children[1]
        display(hbox)

    def export(self):
        export_folder = os.path.join(self.export_folder_ui.selected,
                                     self.output_folder_ui.value)
        file_handler.make_or_reset_folder(export_folder)

        o_export = Normalization()
        o_export.load(data=self.data_enhanced, notebook=True)
        o_export.data['sample']['file_name'] = self.short_list_files
        o_export.export(folder=export_folder,
                        data_type='sample',
                        file_type='tif')
