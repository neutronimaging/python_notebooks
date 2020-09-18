import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from ipywidgets.widgets import interact
import numpy as np
import os
import ipywe.fileselector
from ipywidgets import widgets
from IPython.core.display import display, HTML
import pytz
import datetime

from NeuNorm.normalization import Normalization

from __code.metadata_handler import MetadataHandler
from __code import file_handler


class CreateListFileName(object):

    def __init__(self, working_dir='', verbose=False):
        self.working_dir = working_dir
        self.verbose = verbose

    def select_image_folder(self):
        self.folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Raw Image Folder ...',
                                                              start_dir=self.working_dir,
                                                              type='directory')
        self.folder_ui.show()

        display(HTML(
            '<span style="font-size: 20px; color:blue">If working with FITS, make sure you are working with the raw data set from raw folder!</span>'))

    def retrieve_time_stamp(self):

        self.image_folder = self.folder_ui.selected
        [list_files, ext] = file_handler.retrieve_list_of_most_dominant_extension_from_folder(folder=self.image_folder)
        self.list_files = list_files

        if ext.lower() in ['.tiff', '.tif']:
            ext = 'tif'
        elif ext.lower() == '.fits':
            ext = 'fits'
        else:
            raise ValueError

        box = widgets.HBox([widgets.Label("Retrieving Time Stamp",
                                          layout = widgets.Layout(width='20%')),
                            widgets.IntProgress(min=0,
                                                max=len(list_files),
                                                value=0,
                                                layout=widgets.Layout(width='50%'))
                            ])
        progress_bar = box.children[1]
        display(box)

        list_time_stamp = []
        list_time_stamp_user_format = []
        for _index, _file in enumerate(list_files):
            _time_stamp = MetadataHandler.get_time_stamp(file_name=_file, ext=ext)
            # _time_stamp = self._convert_epics_timestamp_to_rfc3339_timestamp(_time_stamp)
            list_time_stamp.append(_time_stamp)

            _user_format = MetadataHandler.convert_to_human_readable_format(_time_stamp)
            list_time_stamp_user_format.append(_user_format)
            progress_bar.value = _index+1

        self.list_time_stamp = list_time_stamp
        self.list_time_stamp_user_format = list_time_stamp_user_format
        box.close()

    def load(self):
        o_norm = Normalization()
        o_norm.load(file=self.list_files, notebook=True)
        self.images_array = o_norm.data['sample']['data']

    def preview(self):
        #figure, axis = plt.subplots()

        [height, width] = np.shape(self.images_array[0])
        text_y = 0.1 * height
        text_x = 0.6 * width

        def display_selected_image(index, text_x, text_y, pre_text, post_text, color):

            font = {'family': 'serif',
                    'color': color,
                    'weight': 'normal',
                    'size': 16}

            fig = plt.figure(figsize=(15, 10))
            gs = gridspec.GridSpec(1, 1)
            ax = plt.subplot(gs[0, 0])
            im=ax.imshow(self.images_array[index], interpolation='nearest')
            plt.title("image index {}".format(index))
            plt.text(text_x, text_y, "{} {:.2f}{}".format(pre_text,
                                                         self.list_time_offset[index],
                                                         post_text),
                     fontdict=font)
            fig.colorbar(im)
            plt.show()

            return {'text_x': text_x, 'text_y': text_y,
                    'pre_text': pre_text, 'post_text': post_text,
                    'color': color}

        self.preview = interact(display_selected_image,
                                index=widgets.IntSlider(min=0,
                                                        max=len(self.list_files),
                                                        continuous_update=False),
                                text_x=widgets.IntSlider(min=0,
                                                         max=width,
                                                         value=text_x,
                                                         description='Text x_offset',
                                                         continuous_update=False),
                                text_y=widgets.IntSlider(min=0,
                                                         max=height,
                                                         value=text_y,
                                                         description='Text y_offset',
                                                         continuous_upadte=False),
                                pre_text=widgets.Text(value='Time Offset',
                                                      description='Pre text'),
                                post_text=widgets.Text(value='(s)',
                                                       description='Post text'),
                                color=widgets.RadioButtons(options=['red', 'blue', 'white', 'black', 'yellow'],
                                                           value='red',
                                                           description='Text Color'))

    def sort_files_using_time_stamp(self):
        """Using the time stamp information, all the files will be sorted in ascending order of time stamp"""

        file_list = np.array(self.list_files)
        time_stamp = np.array(self.list_time_stamp)
        time_stamp_user_format = np.array(self.list_time_stamp_user_format)

        # sort according to time_stamp array
        sort_index = np.argsort(time_stamp)

        # using same sorting index of the other list
        self.list_files = file_list[sort_index]
        self.list_time_stamp = time_stamp[sort_index]
        self.list_time_stamp_user_format = time_stamp_user_format[sort_index]

    def export(self, output_folder):
        self.retrieve_time_stamp()
        self.sort_files_using_time_stamp()

        # calculate time offset relative to first image (earlier file)
        time_stamp_0 = self.list_time_stamp[0]
        self.list_time_offset = [t - time_stamp_0 for t in self.list_time_stamp]

        try:
            os.path.exists(output_folder)
        except:
            display(HTML('<span>Make sure you selected an export folder!</span>'))
            return

        input_folder_basename = os.path.basename(os.path.abspath(self.image_folder))
        output_file = os.path.abspath(os.path.join(output_folder, input_folder_basename +
                                                   '_timestamp_infos.txt'))
        if os.path.exists(output_file):
            os.remove(output_file)

        metadata = '#filename, timestamp(s), timestamp_user_format, timeoffset(s)\n'
        text = metadata

        file_list = self.list_files
        time_stamp = self.list_time_stamp
        time_stamp_user_format = self.list_time_stamp_user_format
        time_offset = self.list_time_offset

        for _index, _file in enumerate(file_list):
            text += "{}, {}, {}, {}\n".format(os.path.abspath(_file), time_stamp[_index],
                                              time_stamp_user_format[_index],
                                              time_offset[_index])

        with open(output_file, 'w') as f:
            f.write(text)

        display(HTML('<span>File Created: ' + os.path.basename(output_file) + '</span>'))

    def select_export_folder(self, ipts_folder='./'):

        def display_file_selector_from_shared(ev):
            start_dir = os.path.join(ipts_folder, 'shared')
            self.output_folder_ui.remove()
            self.display_file_selector(start_dir=start_dir)

        def display_file_selector_from_home(ev):
            import getpass
            _user = getpass.getuser()
            start_dir = os.path.join('/SNS/users', _user)
            self.output_folder_ui.remove()
            self.display_file_selector(start_dir=start_dir)

        ipts = os.path.basename(self.working_dir)

        button_layout = widgets.Layout(width='30%',
                                       border='1px solid gray')

        hbox = widgets.HBox([widgets.Button(description="Jump to {} Shared Folder".format(ipts),
                                            button_style='success',
                                            layout=button_layout),
                             widgets.Button(description="Jump to My Home Folder",
                                            button_style='success',
                                            layout=button_layout)])
        go_to_shared_button_ui = hbox.children[0]
        go_to_home_button_ui = hbox.children[1]

        go_to_shared_button_ui.on_click(display_file_selector_from_shared)
        go_to_home_button_ui.on_click(display_file_selector_from_home)

        display(hbox)

        self.display_file_selector()

    def display_file_selector(self, start_dir=''):
        self.output_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Output Folder',
                                                                     start_dir=start_dir,
                                                                     multiple=False,
                                                                     next=self.export,
                                                                     type='directory')
        self.output_folder_ui.show()

