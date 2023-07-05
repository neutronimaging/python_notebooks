import os
import numpy as np
import ipywidgets as widgets
from IPython.display import display, HTML

from __code.ipywe import fileselector
from __code._utilities.folder import make_or_reset_folder
from __code import file_handler


class Main:

    list_shapes = None

    def __init__(self, working_data=None, list_images=None, working_metadata=None):
        self.working_data = working_data
        self.list_images = list_images
        self.working_metadata = working_metadata
        self.working_dir = os.path.dirname(os.path.dirname(list_images[0]))

    def calculate_available_shapes(self):
        list_shapes = list()
        for _data in self.working_data:
            list_shapes.append(np.shape(_data))
        self.list_shapes = set(list_shapes)

    def display_available_shapes(self):
        self.calculate_available_shapes()

        self.dict_shapes = {}
        for _shape in self.list_shapes:
            _height, _width = _shape
            self.dict_shapes[f"{_height}, {_width}"] = _shape

        vertical_layout = widgets.VBox([widgets.Label("Available shapes (height, width)"),
                                        widgets.RadioButtons(options=self.dict_shapes.keys())])
        display(vertical_layout)
        self.shape_dropdown_ui = vertical_layout.children[1]

    def select_output_folder(self):

        display(HTML(
            '<span style="font-size: 20px; color:blue">Select where you want to create the corrected images new folder!</span>'))

        self.output_folder_ui = fileselector.FileSelectorPanel(instruction='Select Output Folder ...',
                                                               start_dir=self.working_dir,
                                                               type='directory',
                                                               next=self.export)

        self.output_folder_ui.show()

    def export(self, output_folder):

        w = widgets.IntProgress()
        w.max = len(self.list_images)
        display(w)

        source_folder_name = os.path.basename(os.path.dirname(self.list_images[0]))
        format_selected = self.shape_dropdown_ui.value

        height, width = self.dict_shapes[format_selected]
        new_output_folder = os.path.join(output_folder, f"{source_folder_name}_height{height}px_width{width}px")

        make_or_reset_folder(new_output_folder)

        for _index, _data in enumerate(self.working_data):

            _file_name = self.list_images[_index]
            _metadata = self.working_metadata[_index]

            _local_height, _local_width = np.shape(_data)

            new_image = np.zeros((height, width))

            image_height = np.min([height, _local_height])
            image_width = np.min([width, _local_width])

            new_image[:image_height, :image_width] = _data[:image_height, :image_width]

            base_filename = os.path.basename(_file_name)
            full_new_output_filename = os.path.join(new_output_folder, base_filename)

            file_handler.make_tiff(data=new_image,
                                   # metadata=_metadata,
                                   filename=full_new_output_filename)

            w.value = _index + 1

        w.close()
        display(HTML('<span style="font-size: 20px; color=blue">Images created in ' + new_output_folder + '</span>'))
