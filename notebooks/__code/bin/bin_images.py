import numpy as np
import os
from IPython.core.display import HTML
from ipywidgets import widgets
from IPython.core.display import display

from NeuNorm.normalization import Normalization

from __code.ipywe import fileselector
from __code.ipywe.myfileselector import FileSelectorPanelWithJumpFolders
from __code import utilities, file_handler


class BinHandler:

    working_dir = ''
    images_ui = None
    data = []
    list_file_names = []
    image_dimension = {'height': np.NaN,
                       'width': np.NaN}

    def __init__(self, working_dir=''):
        self.working_dir = working_dir
        self.output_folder_ui = None

    def select_images(self):
        _instruction = 'Select images to bin'
        self.images_ui = fileselector.FileSelectorPanel(instruction=_instruction,
                                                              start_dir=self.working_dir,
                                                              multiple=True,
                                                              next=self.load)
        self.images_ui.show()

    def get_list_images(self):
        return self.images_ui.selected

    def load(self, list_images):
        #list_images = self.get_list_images()
        self.list_file_names = list_images
        self.o_norm = Normalization()
        self.o_norm.load(file=list_images, notebook=True)
        self.data = self.o_norm.data['sample']['data']
        self.__calculate_image_dimension()

    def __calculate_image_dimension(self):
        _image_0 = self.data[0]
        [self.image_dimension['height'], self.image_dimension['width']] = np.shape(_image_0)

    def __bin_parameter_changed(self, sender):

        new_width_bin = int(self.bin_width_para.value)
        self.bin_width_value = new_width_bin

        new_height_bin = int(self.bin_height_para.value)
        self.bin_height_value = new_height_bin

        old_width = self.image_dimension['width']
        old_height = self.image_dimension['height']

        new_width = int(old_width / new_width_bin)
        new_height = int(old_height / new_height_bin)

        self.right_widgets.children[1].value = "Width: {} pixels".format(new_width)
        self.right_widgets.children[2].value = "Height: {} pixels".format(new_height)

    def select_bin_parameter(self):
        _width = self.image_dimension['width']
        _height = self.image_dimension['height']
        left_widgets = widgets.VBox([widgets.HTML(value="<b>Current Image Size:</b>",
                                                  layout=widgets.Layout(width='250px')),
                                     widgets.Label("Width: {} pixels".format(_width),
                                                   layout=widgets.Layout(width='100%')),
                                     widgets.Label("Height: {} pixels".format(_height),
                                                   layout=widgets.Layout(width='100%'))])

        options_list = [str(_) for _ in np.arange(2, 21)]
        self.bin_width_para = widgets.Dropdown(options=options_list,
                                               value='2',
                                               description="width:",
                                               continuous_update=False,
                                               layout=widgets.Layout(width='80%'))
        self.bin_width_para.observe(self.__bin_parameter_changed)

        self.bin_height_para = widgets.Dropdown(options=options_list,
                                                value='2',
                                                description="height:",
                                                continuous_update=False,
                                                layout=widgets.Layout(width='80%'))
        self.bin_height_para.observe(self.__bin_parameter_changed)

        center_widgets = widgets.VBox([widgets.HTML("<b>Bin Parameter:</b>",
                                                    layout=widgets.Layout(width='250px')),
                                       self.bin_width_para,
                                       self.bin_height_para])

        self.right_widgets = widgets.VBox([widgets.HTML("<b>New Image Size:</b>",
                                                   layout=widgets.Layout(width='250px')),
                                      widgets.Label("Width: {} pixels".format(250),
                                                    layout=widgets.Layout(width='100%')),
                                      widgets.Label("Height: {} pixels".format(250),
                                                    layout=widgets.Layout(width='100%'))])

        self.__bin_parameter_changed(None)

        full_widget = widgets.HBox([left_widgets,
                                    center_widgets,
                                    self.right_widgets])

        display(full_widget)

    def select_export_folder(self):
        self.output_folder_ui = FileSelectorPanelWithJumpFolders(instruction='Select output folder...',
                                                                 start_dir=self.working_dir,
                                                                 multiple=False,
                                                                 next=self.export,
                                                                 type='directory',
                                                                 show_jump_to_home=True,
                                                                 show_jump_to_share=True)
        # self.output_folder_ui.show()

    def rebin_data(self, data=[]):
        width_bin = self.bin_width_value
        height_bin = self.bin_height_value

        height = self.image_dimension['height']
        width = self.image_dimension['width']

        # checking if last bin size match other bins
        new_height = height
        _nbr_height_bin = int(np.floor(height / height_bin))
        if not (np.mod(height, height_bin) == 0):
            new_height = int(_nbr_height_bin * height_bin)
        new_height = int(new_height)

        new_width = width
        _nbr_width_bin = int(np.floor(width / width_bin))
        if not (np.mod(width, width_bin) == 0):
            new_width = int(_nbr_width_bin * width_bin)
        new_width = int(new_width)

        _new_data = data[0: new_height, 0: new_width]
        _new_data = _new_data.reshape(_nbr_height_bin, height_bin, _nbr_width_bin, width_bin)
        data_rebinned = _new_data.mean(axis=3).mean(axis=1)

        return data_rebinned

    def get_input_folder(self):
        list_files = self.list_file_names
        _file0 = list_files[0]
        full_dir_name = os.path.dirname(_file0)
        return os.path.basename(full_dir_name)

    def export(self, output_folder):

        input_folder = self.get_input_folder()
        # output_folder = os.path.abspath(os.path.join(self.output_folder_ui.selected,
        #                                              "{}_rebin_by_{}".format(input_folder, self.bin_value)))
        bin_string = f"{self.bin_height_value}height_{self.bin_width_value}width"
        output_folder = os.path.abspath(os.path.join(output_folder, "{}_rebin_by_{}".format(input_folder, bin_string)))
        utilities.make_dir(dir=output_folder, overwrite=False)

        w = widgets.IntProgress()
        w.max = len(self.list_file_names)
        display(w)

        for _index, _file in enumerate(self.list_file_names):
            basename = os.path.basename(_file)
            _base, _ext = os.path.splitext(basename)
            output_file_name = os.path.join(output_folder, _base + '.tiff')
            _rebin_data = self.rebin_data(self.data[_index])
            file_handler.make_tiff(filename=output_file_name, data=_rebin_data)

            w.value = _index + 1

        display(HTML('<span style="font-size: 20px; color:blue">File created in ' + \
                     output_folder + '</span>'))
