from ipywidgets import widgets
from IPython.core.display import display, HTML
import numpy as np
import os

from NeuNorm.normalization import Normalization

from __code.file_handler import ListMostDominantExtension, make_or_reset_folder
from __code.ipywe import fileselector


class FromAttenuationToConcentration(object):

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_folder(self):
        self.folder_list_widget = fileselector.FileSelectorPanel(instruction='Select data folder',
                                                                 start_dir=self.working_dir,
                                                                 next=self.load_data,
                                                                 type='directory')
        self.folder_list_widget.show()

    def load_data(self, folder):
        self.input_folder = folder
        o_list_dominand = ListMostDominantExtension(working_dir = folder)
        o_list_dominand.calculate()
        self.list_files = o_list_dominand.get_files_of_selected_ext().list_files

        o_norm = Normalization()
        o_norm.load(file=self.list_files, notebook=True)

        self.list_data = o_norm.data['sample']['data']

    def define_conversion_formula(self):

        self.box = widgets.HBox([widgets.Label("A(x,y) = "),
                            widgets.Text("0.052",
                                         layout=widgets.Layout(width='10%')),
                            widgets.Dropdown(options=["+", "-"],
                                             layout=widgets.Layout(width='5%'),
                                             value="+"),
                            widgets.Text("2.55e-5",
                                         layout=widgets.Layout(width='10%')),
                            widgets.Label(" * H(x,Y)")])

        display(self.box)

    def converting_data(self):

        try:
            a = float(self.box.children[1].value)
            b = float(self.box.children[3].value)
            symbol = self.box.children[2].value

            coeff = 1
            if symbol == '+':
                coeff = -1

            progress_bar = widgets.IntProgress()
            progress_bar.max = len(self.list_data)
            display(progress_bar)

            list_concentration = []
            for _index, _data in enumerate(self.list_data):
                _list_concentration = coeff * (a - _data) / b
                list_concentration.append(_list_concentration)
                progress_bar.value = _index+1

            self.list_concentration = list_concentration
            progress_bar.close()

        except:
            display(HTML('<span style="font-size: 20px; color:red">Make sure the coefficient are floats!</span>'))

    def select_output_folder(self):
        self.output_folder_list_widget = fileselector.FileSelectorPanel(instruction='Select where new folder will be created',
                                                                        start_dir=self.working_dir,
                                                                        next=self.export_data,
                                                                        type='directory')
        self.output_folder_list_widget.show()

    def create_concentration_list_of_file_names(self):
        """will use the original list of files and create the new file name that add the word "concentration" in it """
        list_files = self.list_files
        base_list_files = ["concentration_{}".format(os.path.basename(_file)) for _file in list_files]

        return base_list_files

    def export_data(self, output_dir):
        o_norm = Normalization()
        o_norm.load(data=self.list_concentration)

        new_list_files = self.create_concentration_list_of_file_names()
        o_norm.data['sample']['file_name'] = new_list_files

        new_folder_name = os.path.basename(self.input_folder) + "_concentration"
        new_output_dir = os.path.join(output_dir, new_folder_name)

        make_or_reset_folder(new_output_dir)

        o_norm.export(folder=new_output_dir,
                      data_type='sample',
                      file_type='tif')

        display(HTML('<span style="font-size: 20px; color:blue">Files have been created in ' + new_output_dir + \
                     '</span>'))
