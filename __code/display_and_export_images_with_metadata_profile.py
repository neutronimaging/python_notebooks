import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from ipywidgets.widgets import interact
from ipywidgets import widgets
import numpy as np
import os
import ipywe.fileselector
from IPython.core.display import display, HTML

from NeuNorm.normalization import Normalization
from __code import file_handler


class DisplayExportScreenshots(object):

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_input_folder(self):
        self.folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Input Folder ...',
                                                              start_dir=self.working_dir,
                                                              type='directory',
                                                              multiple=False)

        self.folder_ui.show()

    def select_metadata_file(self):
        self.metadata_file_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Metadata File (created by file_name_and_metadata_vs_time_stamp.ipynb ...',
                                                              start_dir=self.working_dir,
                                                              multiple=False)
        self.metadata_file_ui.show()

    def display(self):

        self.__check_inputs()
        self.__load()
        self.__preview()



    def __check_inputs(self):
        # images
        image_folder = self.folder_ui.selected

        list_images = file_handler.retrieve_list_of_most_dominand_extension_from_folder(folder=image_folder)
        list_images = list_images[0]
        self.nbr_images = len(list_images)

        # entry from file
        file_name_vs_metadata_name = self.metadata_file_ui.selected
        self.file_name_vs_metadata = pd.read_csv(file_name_vs_metadata_name)
        self.metadata_name = list(self.file_name_vs_metadata.columns.values)[2]
        nbr_metadata = len(self.file_name_vs_metadata[self.file_name_vs_metadata.columns[0]])

        assert self.nbr_images == nbr_metadata

        self.list_images = list_images

    def __load(self):
        o_load = Normalization()
        o_load.load(file=self.list_images, notebook=True)
        self.images_array = o_load.data['sample']['data']
        self.images_list = o_load.data['sample']['file_name']

    def __preview(self):
        metadata_profile = {}

        _metadata_array = np.array(self.file_name_vs_metadata['Metadata'])
        _time_array = np.array(self.file_name_vs_metadata['time'])

        for _index, _file in enumerate(np.array(self.file_name_vs_metadata['file_name'])):
            metadata_profile[_file] = {}
            metadata_profile[_file]['metadata'] = _metadata_array[_index]
            metadata_profile[_file]['time'] = _time_array[_index]

        self.metadata_profile = metadata_profile
        self.metadata_array = _metadata_array
        self.time_array = _time_array

        def plot_images_and_profile(file_index=0):
            fig = plt.figure(figsize=(15, 10))
            gs = gridspec.GridSpec(1, 2)

            _short_file = os.path.basename(self.images_list[file_index])
            _time = metadata_profile[_short_file]['time']
            #_metadata = metadata_profile[_short_file]['metadata']

            ax_img = plt.subplot(gs[0, 0])
            ax_img.imshow(self.images_array[file_index])
            plt.title("{}".format(_short_file))

            ax_plot = plt.subplot(gs[0, 1])
            ax_plot.plot(_time_array, _metadata_array, '*')
            ax_plot.axvline(x=_time, color='r')
            plt.xlabel('Time (s)')
            plt.ylabel(self.metadata_name)
            plt.show()

        preview = interact(plot_images_and_profile,
                           file_index=widgets.IntSlider(min=0,
                                                        max=self.nbr_images - 1,
                                                        description='Image Index',
                                                        continuous_update=False))

    def select_export_folder(self):
        self.output_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select output Folder ...',
                                                                     start_dir=self.working_dir,
                                                                     type='directory')
        self.output_folder_ui.show()

    def export(self):
        output_folder = self.output_folder_ui.selected

        input_folder_basename = os.path.basename(self.folder_ui.selected)
        output_folder = os.path.join(output_folder, input_folder_basename + '_vs_metadata_screenshots')
        if os.path.exists(output_folder):
            import shutil
            shutil.rmtree(output_folder)
        os.makedirs(output_folder)

        def plot_images_and_profile(file_index=0):

            fig = plt.figure(figsize=(15, 10))
            gs = gridspec.GridSpec(1, 2)

            _short_file = os.path.basename(self.images_list[file_index])
            _time = self.metadata_profile[_short_file]['time']
            _metadata = self.metadata_profile[_short_file]['metadata']

            ax_img = plt.subplot(gs[0, 0])
            ax_img.imshow(self.images_array[file_index])
            plt.title("{}".format(_short_file))

            ax_plot = plt.subplot(gs[0, 1])
            ax_plot.plot(self.time_array, self.metadata_array, '*')
            ax_plot.axvline(x=_time, color='r')
            plt.xlabel('Time (s)')
            plt.ylabel(self.metadata_name)

            output_file_name = os.path.abspath(os.path.join(output_folder, _short_file + '.png'))
            plt.savefig(output_file_name)

            plt.close(fig)

        box = widgets.HBox([widgets.Label("Exporting Images:",
                                          layout=widgets.Layout(width='20%')),
                            widgets.IntProgress(min=0,
                                                max=self.nbr_images - 1,
                                                layout=widgets.Layout(width='50%'))])
        progress_bar = box.children[1]
        display(box)

        for _index in np.arange(self.nbr_images):
            plot_images_and_profile(file_index=_index)
            progress_bar.value = _index + 1

        box.close()
        display(HTML('<span style="font-size: 20px; color:blue">Images created in ' + output_folder + '</span>'))
