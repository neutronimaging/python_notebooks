from ipywidgets import widgets
from IPython.core.display import display
import os

from .config import password_to_unlock_config as PASSWORD
from .config import debugger_folder as list_debugging_folder
from .config import debugging
from .config import percentage_of_images_to_use_for_roi_selection as PERCENTAGE_OF_IMAGES
from __code._utilities.file import read_ascii, make_ascii_file_from_string

THIS_FILE_PATH = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(THIS_FILE_PATH, 'config.py')


class SuperUser:

    def __init__(self):
        self.launch_ui()

    def launch_ui(self):

        password = widgets.Password(value="",
                                    placeholder='Enter password',
                                    description='Password',
                                    diabled=False)
        password.observe(self.password_entered, names='value')

        # ----

        # debugging mode
        self.debugging_mode = widgets.Checkbox(value=debugging,
                                               description="Debugging Mode",
                                               disabled=True)

        self.debugging_folder_label = widgets.HTML("List of folders to look for when running in <b>debugging</b> mode.")
        self.debugging_folder = widgets.Select(options=list_debugging_folder,
                                               value=list_debugging_folder[0],
                                               disabled=True,
                                               description="Folders:",
                                               layout=widgets.Layout(height="200px",
                                                                     width="400px"))

        # list of debugging folders
        self.remove_entry = widgets.Button(description="Remove Selected Entry",
                                           disabled=True,
                                           button_style="",
                                           icon='minus-square',
                                           layout=widgets.Layout(width="400px"))
        self.remove_entry.on_click(self.remove_entry_clicked)

        self.new_entry_text = widgets.Text(value="",
                                           description="New folder",
                                           disabled=True)
        self.add_entry = widgets.Button(description="",
                                        disabled=True,
                                        button_style="",
                                        icon="plus-square",
                                        layout=widgets.Layout(width="95px"))
        self.add_entry.on_click(self.add_entry_clicked)
        hori_layout_percentage = widgets.HBox([self.new_entry_text, self.add_entry])

        # percentage of images to use for roi selection
        self.percentage_roi_label = widgets.HTML("Percentage of images to use for ROI selection",
                                                 disabled=True)
        percentage_of_images = PERCENTAGE_OF_IMAGES * 100
        self.percentage_roi_value = widgets.FloatText(value=percentage_of_images,
                                                      disabled=True,
                                                      layout=widgets.Layout(width="50px"))
        self.percentage_units = widgets.HTML("%",
                                             disabled=True)
        hori_layout = widgets.HBox([self.percentage_roi_label,
                                    self.percentage_roi_value,
                                    self.percentage_units])

        # ----
        self.save_changes = widgets.Button(description="Save Changes",
                                           disabled=True,
                                           button_style='Success',
                                           layout=widgets.Layout(width="400px"),
                                           icon='floppy-o')
        self.save_changes.on_click(self.save_button_clicked)

        vertical_layout = widgets.VBox([password,
                                        widgets.HTML("<hr>"),
                                        self.debugging_mode,
                                        widgets.HTML("<br>"),
                                        self.debugging_folder_label,
                                        self.debugging_folder,
                                        self.remove_entry,
                                        hori_layout_percentage,
                                        widgets.HTML("<br>"),
                                        hori_layout,
                                        widgets.HTML("<hr>"),
                                        self.save_changes])

        display(vertical_layout)

        self.update_widgets()

    def remove_entry_clicked(self, state):
        value = self.debugging_folder.value
        options = self.debugging_folder.options
        options_to_keep = []
        for _option in options:
            if value == _option:
                continue
            else:
                options_to_keep.append(_option)
        self.debugging_folder.options = options_to_keep

    def add_entry_clicked(self, state):
        entry_to_add = self.new_entry_text.value
        options = list(self.debugging_folder.options)

        if entry_to_add in options:
            self.new_entry_text.value = ""
            return

        if os.path.exists(entry_to_add):
            options.append(entry_to_add)
        self.debugging_folder.options = options
        self.new_entry_text.value = ""

    def password_entered(self, value):
        new_password = value['new']
        if new_password == PASSWORD:
            disabled = False
        else:
            disabled = True
        self.update_widgets(disabled=disabled)

    def update_widgets(self, disabled=True):
        list_ui = [self.debugging_mode,
                   self.save_changes,
                   self.debugging_folder,
                   self.remove_entry,
                   self.add_entry,
                   self.new_entry_text,
                   self.percentage_roi_label,
                   self.percentage_roi_value,
                   self.percentage_units,
                   ]
        for _ui in list_ui:
            _ui.disabled = disabled

    def save_button_clicked(self, value):
        debugging_mode = self.debugging_mode.value

        list_folders = self.debugging_folder.options
        str_list_folders = [f"{_folder}" for _folder in list_folders]
        str_list_folders_formatted = f"{str_list_folders}"

        percentage_roi_selection = self.percentage_roi_value.value / 100.

        ascii = read_ascii(CONFIG_FILE)
        ascii_split = ascii.split("\n")

        ascii_after = []
        for _line in ascii_split:
            if "debugging = " in _line:
                ascii_after.append(f"debugging = {debugging_mode}")
            elif "debugger_folder = " in _line:
                ascii_after.append(f"debugger_folder = {str_list_folders_formatted}")
            elif "percentage_of_images_to_use_for_roi_selection = " in _line:
                ascii_after.append(f"percentage_of_images_to_use_for_roi_selection = {percentage_roi_selection}")
            else:
                ascii_after.append(_line)

        ascii_after_formatted = "\n".join(ascii_after)
        make_ascii_file_from_string(text=ascii_after_formatted,
                                    filename=CONFIG_FILE)
