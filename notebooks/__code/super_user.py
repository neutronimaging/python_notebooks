from ipywidgets import widgets
from IPython.core.display import display, HTML
import os

from .config import password_to_unlock_config as PASSWORD
from .config import debugger_folder as list_debugging_folder


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

        self.debugging_mode = widgets.Checkbox(value=False,
                                               description="Debugging Mode",
                                               disabled=True)

        self.debugging_folder_label = widgets.HTML("List of folders to look for when running in <b>debugging</b> mode.")
        self.debugging_folder = widgets.Select(options=list_debugging_folder,
                                               value=list_debugging_folder[0],
                                               disabled=True,
                                               description="Folders:",
                                               layout=widgets.Layout(height="200px",
                                                                     width="400px"))

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
        hori_layout = widgets.HBox([self.new_entry_text, self.add_entry])

        # ----
        self.save_changes = widgets.Button(description="Save Changes",
                                           disabled=True,
                                           button_style='Success',
                                           layout=widgets.Layout(width="400px"),
                                           icon='floppy-o')

        vertical_layout = widgets.VBox([password,
                                        widgets.HTML("<hr>"),
                                        self.debugging_mode,
                                        widgets.HTML("<br>"),
                                        self.debugging_folder_label,
                                        self.debugging_folder,
                                        self.remove_entry,
                                        hori_layout,
                                        widgets.HTML("<hr>"),
                                        self.save_changes])

        display(vertical_layout)

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
                   ]
        for _ui in list_ui:
            _ui.disabled = disabled
