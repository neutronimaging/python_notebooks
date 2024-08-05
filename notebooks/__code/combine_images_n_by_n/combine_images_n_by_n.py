from scipy.stats.mstats import gmean
from ipywidgets import widgets
from IPython.core.display import display, HTML
import numpy as np
from pathlib import Path, PurePath
import os
import glob
import random

from NeuNorm.normalization import Normalization

from __code.file_folder_browser import FileFolderBrowser
from __code import file_handler
from __code.ipywe import fileselector, myfileselector
from __code._utilities.string import get_beginning_common_part_of_string_from_list
from __code._utilities.file import make_or_increment_folder_name


FILE_PREFIX = "image"

RENAMING_OPTIONS = ['use image_####.ext format',
                    'use <original_name>_####.ext format',
                    're-use name of first image of group']


class CombineImagesNByN(object):
    working_dir = ''

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

        self.combine_method = None
        self.folder_widget = None
        self.bin_size_ui = None
        self.bin_size_label = None
        self.output_folder_widget = None
        self.timespectra_file_name = None

    def select_images(self):
        o_file_browser = FileFolderBrowser(working_dir=self.working_dir,
                                           next_function=self.post_select_images)
        self.list_files_selected = o_file_browser.select_images_with_search(instruction="Select images to combine",
                                                                            multiple_flag=True,
                                                                            filters={"TIFF": "*.tif*",
                                                                                     "FITS": "*.fits"})

    def post_select_images(self, list_of_images):
        if list_of_images:
            self.input_folder_selected = os.path.dirname(list_of_images[0])
            self.base_working_dir = str(PurePath(Path(self.input_folder_selected).parent).name)
            self.list_files = list_of_images

    # def select_folder(self):
    #         self.folder_widget = fileselector.FileSelectorPanel(instruction='select folder with images to combine',
    #                                                             start_dir=self.working_dir,
    #                                                             type='directory',
    #                                                             next=self.post_select_folder,
    #                                                             multiple=False)
    #         self.folder_widget.show()
    #
    # def post_select_folder(self, folder_selected):
    #     self.input_folder_selected = folder_selected
    #     self._retrieve_number_of_files()
    #     self._check_if_working_with_time_spectra()

    # def _retrieve_number_of_files(self):
    #     self.base_working_dir = str(PurePath(Path(self.input_folder_selected).parent).name)
    #     [self.list_files, _] = file_handler.retrieve_list_of_most_dominant_extension_from_folder(
    #             folder=self.input_folder_selected)

    def _check_if_working_with_time_spectra(self):
        input_folder = self.input_folder_selected
        list_files = glob.glob(input_folder + '/*')
        for _file in list_files:
            if "_Spectra.txt" in _file:
                self.timespectra_file_name = _file

    @staticmethod
    def extract_index(full_file_name):
        basename = os.path.basename(full_file_name)
        base, ext = os.path.splitext(basename)
        split_by = base.split("_")
        return split_by[-1]

    def sort_by_index(self):
        list_files = self.list_files
        dict_list_files_by_index = {}
        for _file in list_files:
            _index = CombineImagesNByN.extract_index(_file)
            dict_list_files_by_index[_index] = _file

        list_index = list(dict_list_files_by_index.keys())
        list_index.sort()

        list_files_sorted_by_index = [dict_list_files_by_index[_key] for _key in list_index]
        return list_files_sorted_by_index

    def sorting_the_files(self):
        random_file = random.randint(0, len(self.list_files))
        template_file_name = os.path.basename(self.list_files[random_file])
        base_name, ext = os.path.splitext(template_file_name)
        split_name = base_name.split("_")
        base_name_before_index = "_".join(split_name[:-1])
        index = split_name[-1]

        # tab 1 - full name
        list_files_base_name_only = [os.path.basename(_file) for _file in self.list_files]
        vertical_layout_tab1 = widgets.VBox([widgets.HTML(value=f"<b>{base_name}</b>{ext}",
                                                          layout=widgets.Layout(width='100%')),
                                             widgets.Select(options=list_files_base_name_only,
                                                            layout=widgets.Layout(width='100%',
                                                                                  height='700px')),
                                             ])

        # tab 2 - file_index
        self.list_files_by_index = self.sort_by_index()
        list_files_by_index_base_name_only = [os.path.basename(_file) for _file in self.list_files_by_index]
        vertical_layout_tab2 = widgets.VBox([widgets.HTML(value=f"{base_name_before_index}_<b>{index}</b>{ext}",
                                                          layout=widgets.Layout(width='100%')),
                                             widgets.Select(options=list_files_by_index_base_name_only,
                                                            layout=widgets.Layout(width='100%',
                                                                                  height='700px')),
                                             ])

        # main tab
        tab = widgets.Tab()
        tab.children = [vertical_layout_tab1, vertical_layout_tab2]
        tab.set_title(0, 'by Full Name')
        tab.set_title(1, 'by File Index')
        tab.layout = widgets.Layout(height='800px')
        display(tab)
        self.sorting_tab = tab

    def how_to_combine(self):
        # saving first the sorted list of files
        if self.sorting_tab.selected_index == 0:
            self.list_files_sorted = self.list_files
        else:
            self.list_files_sorted = self.list_files_by_index

        _file = open("__docs/combine_images/geometric_mean.png", 'rb')
        _geo_image = _file.read()
        geo_box = widgets.HBox([widgets.Label("Geometric Mean",
                                              layout=widgets.Layout(width='20%')),
                                widgets.Image(value=_geo_image,
                                              format='png')])
        _file = open("__docs/combine_images/algebric_mean.png", 'rb')
        _alge_image = _file.read()
        alge_box = widgets.HBox([widgets.Label("Arithmetic Mean",
                                              layout=widgets.Layout(width='20%')),
                                widgets.Image(value=_alge_image,
                                              format='png')])

        self.combine_method = widgets.RadioButtons(options=['add', 'arithmetic mean', 'geometric mean', 'median'],
                                                   value='arithmetic mean')

        vertical = widgets.VBox([alge_box, geo_box, self.combine_method])
        display(vertical)

    def how_many_files(self):
        nbr_files = len(self.list_files_sorted)
        if nbr_files > 30:
            nbr_files = 30
        radio_list_string = [str(_index) for _index in np.arange(2, nbr_files + 1)]

        vertical_layout = widgets.VBox([widgets.Dropdown(options=radio_list_string,
                                                         value=radio_list_string[0]),
                                        widgets.Label("",
                                                      layout=widgets.Layout(width='100%'))])
        display(vertical_layout)

        self.bin_size_ui = vertical_layout.children[0]
        self.bin_size_label = vertical_layout.children[1]

        self.bin_size_ui.observe(self.update_how_many_files, names='value')
        self.update_how_many_files()

    def _get_number_of_files_will_be_created(self, bin_value=2):
        return int(len(self.list_files_sorted)/bin_value)

    def update_how_many_files(self, bin_value_object=None):
        if bin_value_object:
            bin_value = int(bin_value_object['new'])
            nbr_images = self._get_number_of_files_will_be_created(bin_value=bin_value)
        else:
            nbr_images = self._get_number_of_files_will_be_created()
        message = "You are about to create {} files out of {} files selected.".format(nbr_images,
                                                                                      len(self.list_files_sorted))
        self.bin_size_label.value = message

    def select_output_folder(self):
        # self.output_folder_widget = fileselector.FileSelectorPanel(instruction='select where to create the ' + \
        #                                                                        'combined image ...',
        #                                                            start_dir=self.working_dir,
        #                                                            newdir_toolbar_button=True,
        #                                                            next=self.merging,
        #                                                            type='directory')
        
        self.output_folder_widget = myfileselector.FileSelectorPanelWithJumpFolders(
            instruction='select folder with images to combine',
            start_dir=self.working_dir,
            type='directory',
            next=self.merging,
            multiple=False,
            newdir_toolbar_button=True,
            ipts_folder=self.working_dir,
            show_jump_to_home=True,
            show_jump_to_share=True)

    def __get_formated_merging_algo_name(self):
        _algo = self.combine_method.value
        if _algo =='arithmetic mean':
            return 'arithmetic_mean'
        elif _algo == 'geometric mean':
            return 'geometric_mean'
        elif _algo == 'median':
            return 'median'
        elif _algo == 'add':
            return 'add'
        else:
            raise NotImplementedError(f"Algorithm {_algo} not implemented yet!")

    @staticmethod
    def files_shared_same_base_name(list_files):
        list_base_file_name = []
        for _file in list_files:
            split_base_name = _file.split("_")
            list_base_file_name.append("_".join(split_base_name[:-1]))

        set_list = set(list_base_file_name)
        if len(set_list) > 1:
            return False

        return True

    def create_list_of_files_to_merge(self):
        """
        create the dictionaries of groups, good and bad ones
        a group is bad when outside of the index part, the base file name changes within the group
            ex:   102020_cool_05_sample_0001.tiff
                  102020_heat_05_sample_0002.tiff
        """
        bin_value = int(self.bin_size_ui.value)
        self.bin_value = bin_value
        list_files = self.list_files_sorted
        nbr_files = len(list_files)

        dict_list_files = {}
        bad_dict_list_files = {}
        global_index = 0
        bad_global_index = 0
        for _index in np.arange(0, nbr_files, bin_value):
            # make sure we don't go over board
            right_threshold = _index + bin_value
            if right_threshold > nbr_files:
                break

            _working_list_files = list_files[_index: _index+bin_value]
            if CombineImagesNByN.files_shared_same_base_name(_working_list_files):
                dict_list_files[global_index] = _working_list_files
                global_index += 1
            else:
                bad_dict_list_files[bad_global_index] = _working_list_files
                bad_global_index += 1

        self.dict_list_files = dict_list_files
        self.bad_dict_list_files = bad_dict_list_files

    def get_merging_algorithm(self):
        # get merging algorithm
        merging_algo = self.combine_method.value
        if merging_algo == 'arithmetic mean':
            return CombineImagesNByN.arithmetic_mean
        elif merging_algo == 'geometric mean':
            return CombineImagesNByN.geo_mean
        elif merging_algo == 'median':
            return CombineImagesNByN.median
        elif merging_algo == 'add':
            return CombineImagesNByN.add

        raise NotImplementedError(f"merging algo {merging_algo} not implemented!")

    def get_merging_algorithm_name(self):
        merging_algo = self.combine_method.value
        if merging_algo == 'arithmetic mean':
            return 'arithmetic_mean'
        elif merging_algo == 'geometric mean':
            return 'geometric_mean'
        elif merging_algo == 'median':
            return 'median'
        elif merging_algo == 'add':
            return 'add'

        raise NotImplementedError(f"merging algo {merging_algo} not implemented!")

    def preview_result(self):
        how_to_rename_layout = widgets.VBox([widgets.Label("How to name output files:",
                                                           layout=widgets.Layout(width='100%')),
                                             widgets.RadioButtons(options=RENAMING_OPTIONS,
                                                                  layout=widgets.Layout(width='100%'),
                                                                  value=RENAMING_OPTIONS[-1])])
        display(how_to_rename_layout)
        self.how_to_rename_ui = how_to_rename_layout.children[1]

        self.create_list_of_files_to_merge()
        self.create_dictionary_of_new_file_names()

        # tab1
        list_groups = list(self.dict_list_files.keys())
        self.group_dropdown = widgets.Dropdown(options=list_groups,
                                               description="Groups")
        self.list_files_per_group = widgets.Select(options=self.dict_list_files[list_groups[0]],
                                                   description="Files",
                                                   layout=widgets.Layout(width='100%',
                                                                         height='400px'))

        new_file_name_label = widgets.Label("Output file name:",
                                            layout=widgets.Layout(width='150px',
                                                                  height='80px'))
        self.new_file_name = widgets.Label(self.dict_list_new_files[0],
                                           layout=widgets.Layout(width='400px',
                                                                 height='80px'))
        hori1 = widgets.HBox([new_file_name_label, self.new_file_name])

        vbox1 = widgets.VBox([self.group_dropdown,
                             self.list_files_per_group,
                             hori1],
                            layout=widgets.Layout(height="600px"))

        accordion_widgets = [vbox1]

        # tab2
        if len(self.bad_dict_list_files.keys()) > 0:
            list_groups = list(self.bad_dict_list_files.keys())
            self.bad_group_dropdown = widgets.Dropdown(options=list_groups,
                                                       description="Bad Groups")
            self.bad_list_files_per_group = widgets.Select(options=self.bad_dict_list_files[list_groups[0]],
                                                       description="Files",
                                                       layout=widgets.Layout(width='100%',
                                                                             height='500px'))
            vbox2 = widgets.VBox([self.bad_group_dropdown,
                                 self.bad_list_files_per_group],
                                layout=widgets.Layout(height="600px"))
            self.bad_group_dropdown.observe(self.bad_group_changed, names='value')
            accordion_widgets.append(vbox2)

        accordion = widgets.Accordion(children=accordion_widgets)
        accordion.set_title(0, 'Good groups')

        if len(self.bad_dict_list_files.keys()) > 0:
            accordion.set_title(1, 'Groups with errors')

        display(accordion)

        self.group_dropdown.observe(self.group_changed, names='value')
        self.how_to_rename_ui.observe(self.how_to_name_output_changed, names='value')
        self.update_combined_file_name_widget()

    def create_dictionary_of_new_file_names(self):
        """
        go through the list of keys, groups (0, 1, 2...), take the first 2 files of each group
        and isolate the common part of the base name, and then save it in a new dictionary using the same key

        ex: file1 = '/Volumes/G-DRIVE/IPTS/IPTS-1234/CT-scans_1/20211005_1C30_6C10_150_tomo_0010_000_000_001.tiff'
            file2 = '/Volumes/G-DRIVE/IPTS/IPTS-1234/CT-scans_1/20211005_1C30_6C10_150_tomo_0010_000_000_002.tiff

        common part will be

        20211005_1C30_6C10_150_tomo_0010_000_000
        """
        dict_list_files = self.dict_list_files
        dict_list_new_files = {}

        renaming_option = self.how_to_rename_ui.value
        if renaming_option == RENAMING_OPTIONS[0]:
            # using image_####.ext

            for _key in dict_list_files.keys():
                new_file_name = 'image_{:04d}.tiff'.format(_key)
                dict_list_new_files[_key] = new_file_name

        elif renaming_option == RENAMING_OPTIONS[1]:
            # using base original name

            for _key in dict_list_files.keys():
                list_files = dict_list_files[_key]
                base_list_files = [os.path.basename(_file) for _file in list_files]
                _common_part = get_beginning_common_part_of_string_from_list(list_of_text=base_list_files)
                new_file_name = _common_part + '_{:03d}.tiff'.format(_key)
                dict_list_new_files[_key] = new_file_name

        elif renaming_option == RENAMING_OPTIONS[2]:
            # using first image name of group

            for _key in dict_list_files.keys():
                list_files = dict_list_files[_key]
                base_file_name = os.path.basename(list_files[0])
                dict_list_new_files[_key] = base_file_name

        self.dict_list_new_files = dict_list_new_files

    def update_combined_file_name_widget(self):
        group_selected = self.group_dropdown.value
        self.create_dictionary_of_new_file_names()
        output_file_name = self.dict_list_new_files[group_selected]
        self.new_file_name.value = output_file_name

    def keep_file_name_changed(self, value):
        self.update_combined_file_name_widget()

    def how_to_name_output_changed(self, value):
        self.update_combined_file_name_widget()

    def group_changed(self, value):
        new_group = value['new']
        new_list_files = self.dict_list_files[new_group]
        self.list_files_per_group.options = new_list_files
        self.update_combined_file_name_widget()

    def bad_group_changed(self, value):
        new_group = value['new']
        new_bad_list_files = self.bad_dict_list_files[new_group]
        self.bad_list_files_per_group.options = new_bad_list_files

    def merging(self, output_folder):
        """combine images using algorithm provided"""

        # self.create_list_of_files_to_merge()
        dict_list_files = self.dict_list_files

        nbr_of_files_to_create = len(dict_list_files.keys())
        algorithm = self.get_merging_algorithm()

        horizontal_layout = widgets.HBox([widgets.Label("Merging Progress",
                                                        layout=widgets.Layout(width='20%')),
                                          widgets.IntProgress(max=len(dict_list_files.keys()),
                                                              value=0,
                                                              layout=widgets.Layout(width='50%'))])
        global_slider = horizontal_layout.children[1]
        display(horizontal_layout)

        algo_name = self.get_merging_algorithm_name()
        output_folder_name = CombineImagesNByN.__create_output_folder_name(
                output_folder=output_folder,
                base_file_name=self.base_working_dir,
                bin_value=self.bin_value,
                algo_name=algo_name)
        output_folder_name = make_or_increment_folder_name(folder_name=output_folder_name)

        output_timespectra_file_name = os.path.join(output_folder_name,
                                                    CombineImagesNByN.__create_timestamp_file_name())
        CombineImagesNByN.combine_timespectra(input_timespectra_file_name=self.timespectra_file_name,
                                              output_timespectra_file_name=output_timespectra_file_name,
                                              bin_value=self.bin_value,
                                              merging_algorithm=algorithm)

        for _key in dict_list_files.keys():
            list_files = dict_list_files[_key]
            o_load = Normalization()
            o_load.load(file=list_files, notebook=False)
            _data = o_load.data['sample']['data']
            metadata = o_load.data['sample']['metadata']

            combined_data = CombineImagesNByN.merging_algorithm(algorithm, _data)
            del o_load

            output_file_name = self.dict_list_new_files[_key]

            o_save = Normalization()
            o_save.load(data=combined_data)
            o_save.data['sample']['metadata'] = [metadata[0]]
            o_save.data['sample']['file_name'] = [output_file_name]
            o_save.export(folder=output_folder_name, data_type='sample')
            del o_save

            global_slider.value += 1

        global_slider.close()

        display(HTML('<span style="font-size: 20px; color:blue">' + str(nbr_of_files_to_create) +
                     ' files have been created in ' + output_folder_name + '</span>'))
        if self.timespectra_file_name:
            display(HTML('<span style="font-size: 20px; color:blue"> A new _Spectra.txt file has been created: ' \
                         + output_timespectra_file_name + '</span>'))

    @staticmethod
    def combine_timespectra(input_timespectra_file_name=None,
                            output_timespectra_file_name=None,
                            bin_value=2,
                            merging_algorithm=None):
        if input_timespectra_file_name is None:
            return

        data = np.genfromtxt(input_timespectra_file_name, delimiter='\t')
        nbr_rows, nbr_columns = np.shape(data)

        time_axis_binned = []
        count_axis_binned = []

        for index in np.arange(0, nbr_rows, bin_value):
            right_threshold = index + bin_value
            if right_threshold >= nbr_rows:
                break

            working_time_axis_to_bin = data[index: index + bin_value, 0]
            working_count_axis_to_bin = data[index: index + bin_value, 1]

            time_axis_binned.append(
                CombineImagesNByN.merging_algorithm(CombineImagesNByN.arithmetic_mean,
                                                    working_time_axis_to_bin))
            count_axis_binned.append(CombineImagesNByN.merging_algorithm(merging_algorithm,
                                                                         working_count_axis_to_bin))

        new_timespectra = list(zip(time_axis_binned, count_axis_binned))
        np.savetxt(output_timespectra_file_name, new_timespectra, delimiter="\t")

    @staticmethod
    def __create_output_folder_name(output_folder="./", base_file_name='', bin_value=2, algo_name='add'):
        output_folder = os.path.abspath(output_folder)
        output_folder_name = os.path.join(output_folder, "{}_files_combined_by_{:d}_{}".format(base_file_name,
                                                                                               bin_value,
                                                                                               algo_name))
        return output_folder_name

    @staticmethod
    def __create_merged_file_name(index=0):
        """Create the new base name using a combine name of all the input file
        """
        return FILE_PREFIX + '_{:03d}.tiff'.format(index)

    @staticmethod
    def __create_timestamp_file_name():
        return FILE_PREFIX + '_Spectra.txt'

    @staticmethod
    def add(data_array):
        return np.sum(data_array, axis=0)

    @staticmethod
    def arithmetic_mean(data_array):
        return np.mean(data_array, axis=0)

    @staticmethod
    def geo_mean(data_array):
        return gmean(data_array, axis=0)

    @staticmethod
    def median(data_array):
        return np.median(data_array, axis=0)

    @staticmethod
    def merging_algorithm(function_, *args):
        return function_(*args)
