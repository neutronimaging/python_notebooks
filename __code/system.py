from __code import config
import getpass
import glob
import os
from ipywidgets import widgets
from IPython.core.display import display


class System(object):

    working_dir = ''
    start_path = ''

    @classmethod
    def select_working_dir(cls, debugger_folder=''):

        username = getpass.getuser()

        debugging = config.debugging
        debugger_username = config.debugger_username

        if debugger_folder == '':
            debugger_folder = config.debugger_folder

        if debugging and (username == debugger_username):
            print("** Using Debugging Mode! **")

            # check that in debugging mode, on analysis machine, default folder exists
            import socket

            if socket.gethostname() == config.analysis_machine:
                if not os.path.exists(debugger_folder):
                    debugging = False

            start_path = debugger_folder
        else:
            start_path = config.system_folder

        cls.start_path = start_path
        list_folders = sorted(glob.glob(start_path + '*'))
        short_list_folders = [os.path.basename(_folder) for _folder in list_folders]
        #short_list_folders = sorted(short_list_folders)

        # if user mode, only display folder user can access
        default_value = ''
        if not debugging:
            user_list_folders = [os.path.basename(_folder) for _folder in list_folders if os.access(_folder, os.R_OK)]
            if len(user_list_folders) > 0:
                default_value = user_list_folders[0]
        else:  # debugging
            user_list_folders = short_list_folders
            default_value = config.project_folder
            if not (default_value in user_list_folders):
                if len(user_list_folders) > 0:
                    default_value = user_list_folders[0]

        hbox = widgets.HBox([widgets.Label("Select Working Folder",
                                           layout=widgets.Layout(width="20%")),
                             widgets.Select(options=user_list_folders,
                                            value=default_value),
                             ])
        display(hbox)

        cls.working_dir_ui = hbox.children[1]


    @classmethod
    def get_working_dir(cls):
        return os.path.join(cls.start_path, cls.working_dir_ui.value)
