import os
from ipywidgets import widgets
from IPython.core.display import display, HTML
import numpy as np

from NeuNorm.normalization import Normalization

from __code import file_handler
from __code.ipywe import fileselector


class MathImages(object):
    working_dir = ''

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_files(self):
        self.files_list_widget = fileselector.FileSelectorPanel(instruction='select images to operate on',
                                                                start_dir=self.working_dir,
                                                                multiple=True)
        self.files_list_widget.show()

    def select_target_image(self):
        self.target_file = fileselector.FileSelectorPanel(instruction='select images to use in operation',
                                                          start_dir=self.working_dir,
                                                          multiple=False)
        self.target_file.show()

    def which_math(self):
        self.math_method = widgets.RadioButtons(options=['substract',
                                                         'add'],
                                                value='substract')
        display(self.math_method)

    def recap(self):
        self.record_widgets_values()
        self.check_operation()

    def record_widgets_values(self):
        self.math = self.math_method.value
        self.list_files = self.files_list_widget.selected
        self.target_file = self.target_file.selected

    def check_operation(self):
        math = self.math
        list_files = self.list_files
        target_file = self.target_file

        display(HTML('<span style="font-size: 20px; color:blue">You are about to ' + math \
                      + ' ' + '</span><span style="font-size: 20px; color:green">' + os.path.basename(target_file) +
                     ' from the ' + str(len(list_files)) +
                     ' </span><span style="font-size: 20px; color:blue">files you selected!</span>'))

    def select_output_folder(self):
        self.output_folder_widget = fileselector.FileSelectorPanel(instruction='select where to create the ' + \
                                                                               'new images ...',
                                                                   start_dir=self.working_dir,
                                                                   next=self.do_the_math,
                                                                   type='directory')

        self.output_folder_widget.show()

    def do_the_math(self, output_folder):
        output_folder = os.path.abspath(output_folder)
        math = self.math
        list_files = self.list_files
        target_file = self.target_file

        o_load = Normalization()
        o_load.load(file=list_files, notebook=True)
        data = o_load.data['sample']['data']

        o_target = Normalization()
        o_target.load(file=target_file, notebook=False)
        target_data = o_target.data['sample']['data']

        if math == 'add':
            algorithm = self.__add
        elif math == 'substract':
            algorithm = self.__substract

        final_array = algorithm(data, target_data)

        del data
        del target_data

        # export
        o_export = Normalization()
        o_export.load(data=final_array, notebook=True)

        input_folder = os.path.basename(os.path.dirname(self.list_files[0]))
        new_output_folder = self.make_new_output_folder(input_folder=input_folder,
                                                        output_folder=output_folder,
                                                        math=math)
        o_export.export(new_output_folder, data_type='sample')
        del o_export

        display(HTML('<span style="font-size: 20px; color:blue">Files have been created in'
                     ' the folder ' + new_output_folder + '</span>'))

    def __add(self, data_array, target_array):
        return np.add(data_array, target_array)

    def __substract(self, data_array, target_array):
        return np.subtract(data_array, target_array)

    def __math_algorithm(self, function_, *args):
        return function_(*args)

    def make_new_output_folder(self, input_folder='', output_folder='', math='add'):
        new_output_folder = os.path.join(output_folder, input_folder + "_" + math)
        file_handler.make_folder(new_output_folder)
        return new_output_folder
