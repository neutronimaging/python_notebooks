from ipywidgets import widgets
from IPython.core.display import display, HTML

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

        # ----
        self.save_changes = widgets.Button(description="Save Changes",
                                           disabled=True,
                                           button_style='Success',
                                           icon='floppy-o')

        vertical_layout = widgets.VBox([password,
                                        widgets.HTML("<hr>"),
                                        self.debugging_mode,
                                        widgets.HTML("<br>"),
                                        self.debugging_folder_label,
                                        self.debugging_folder,
                                        widgets.HTML("<hr>"),
                                        self.save_changes])


        display(vertical_layout)



    def password_entered(self, value):
        new_password = value['new']
        if new_password == PASSWORD:
            disabled = False
        else:
            disabled = True
        self.update_widgets(disabled=disabled)

    def update_widgets(self, disabled=True):
        list_ui = [ self.debugging_mode,
                    self.save_changes,
                    self.debugging_folder
                    ]
        for _ui in list_ui:
            _ui.disabled = disabled
