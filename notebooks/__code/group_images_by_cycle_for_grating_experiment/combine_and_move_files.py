import os
from IPython.core.display import display, HTML
from ipywidgets import widgets
import shutil
from collections import OrderedDict

from __code.file_handler import make_or_reset_folder
from .utilities import combine_images


class CombineAndMoveFiles:

    def __init__(self, parent=None, output_folder=None, debug=False):
        self.parent = parent
        self.output_folder = output_folder
        self.parent.output_folder = output_folder
        self.debug = debug

    def run(self):

        if not self.output_folder:
            return

        debug = self.debug
        output_folder = self.output_folder

        output_folder_basename = os.path.basename(self.parent.folder_selected) + "_sorted_for_grating_reconstruction"
        output_folder = os.path.join(output_folder, output_folder_basename)
        output_folder = os.path.abspath(output_folder)

        # add data type file extension
        data_type = self.parent.sample_or_ob_radio_buttons.value
        output_folder = output_folder + f"_{data_type}"

        self.parent.output_folder = output_folder
        make_or_reset_folder(output_folder)

        dictionary_of_groups_old_names = self.parent.make_dictionary_of_groups_old_names()
        self.parent.dictionary_of_groups_old_names = dictionary_of_groups_old_names

        dict_old_files = dictionary_of_groups_old_names
        dict_new_files = self.parent.dictionary_of_groups_new_names

        list_keys = list(dict_old_files.keys())
        size_outer_loop = len(list_keys)
        size_inner_loop = len(dict_old_files[list_keys[0]])

        hbox1 = widgets.HBox([widgets.HTML("Groups",
                                           layout=widgets.Layout(width="100px")),
                              widgets.IntProgress(min=0,
                                                  max=size_outer_loop - 1,
                                                  value=0,
                                                  layout=widgets.Layout(width="300px"))])
        outer_progress_ui = hbox1.children[1]
        hbox2 = widgets.HBox([widgets.HTML("Files",
                                           layout=widgets.Layout(width="100px")),
                              widgets.IntProgress(min=0,
                                                  max=size_inner_loop - 1,
                                                  value=0,
                                                  layout=widgets.Layout(width="300px"))])
        inner_progress_ui = hbox2.children[1]

        vbox = widgets.VBox([hbox1, hbox2])
        display(vbox)

        for _outer_index, _key in enumerate(dict_old_files.keys()):
            if debug: print(f"outer_index: {_outer_index}")
            _old_name_list = dict_old_files[_key]
            _new_name_list = dict_new_files[_key]
            inner_progress_ui.value = 0
            outer_progress_ui.value = _outer_index
            for _inner_index, (_old, _new) in enumerate(zip(_old_name_list, _new_name_list)):

                new_full_file_name = os.path.join(output_folder, _new)
                if debug: print(f"old full file name -> {_old}")
                if debug: print(f"new full file name -> {_new}")
                if len(_old) > 1:
                    combine_images(output_folder=output_folder,
                                   list_images=_old,
                                   new_file_name=_new)
                else:
                    shutil.copy(_old[0], new_full_file_name)
                inner_progress_ui.value = _inner_index

        vbox.close()

        message = f"Folder {output_folder} has been created!"
        display(HTML('<span style="font-size: 15px">' + message + '</span>'))
