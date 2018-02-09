from __code import config
import getpass
import glob
import os
from ipywidgets import widgets
from IPython.core.display import display
from IPython.core.display import HTML


class System(object):

    working_dir = ''
    start_path = ''

    @classmethod
    def select_working_dir(cls, debugger_folder='', system_folder=''):

        username = getpass.getuser()

        debugging = config.debugging
        debugger_username = config.debugger_username

        found_a_folder = False
        if debugger_folder == '':
            for _folder in config.debugger_folder:
                if os.path.exists(_folder):
                    debugger_folder = _folder
                    found_a_folder = True
                    break
            
        if not found_a_folder:
            debugger_folder = './'

        if debugging and (username == debugger_username):
            print("** Using Debugging Mode! **")

            # check that in debugging mode, on analysis machine, default folder exists
            import socket

            if socket.gethostname() == config.analysis_machine:
                if not os.path.exists(debugger_folder):
                    debugging = False

            start_path = debugger_folder
        else:
            if system_folder == '':
                start_path = config.system_folder
            else:
                start_path = system_folder
            import warnings
            warnings.filterwarnings('ignore')

        cls.start_path = start_path
        list_folders = sorted(glob.glob(start_path + '*'))
        short_list_folders = [os.path.basename(_folder) for _folder in list_folders if os.path.isdir(_folder)]
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

        help_ui = widgets.Button(description="HELP",
                                 button_style='info')
        help_ui.on_click(cls.select_ipts_help)

        top_hbox = widgets.HBox([widgets.Label("IPTS-"),
                                 widgets.Text(value="",
                                              layout=widgets.Layout(width='10%')),
                                 widgets.Label("DOES NOT EXIST!",
                                               layout=widgets.Layout(width='20%'))])
        cls.result_label = top_hbox.children[2]
        cls.result_label.add_class("result_label")
        or_label = widgets.Label("OR")
        bottom_hbox = widgets.HBox([widgets.Label("Select Folder",
                                           layout=widgets.Layout(width="20%")),
                             widgets.Select(options=user_list_folders,
                                            value=default_value,
                                            layout=widgets.Layout(height='300px')),
                             ])
        cls.user_list_folders = user_list_folders
        box = widgets.VBox([top_hbox, or_label, bottom_hbox, help_ui])
        display(box)

        cls.working_dir_ui = bottom_hbox.children[1]
        cls.manual_ipts_entry_ui = top_hbox.children[1]
        cls.manual_ipts_entry_ui.observe(cls.check_ipts_input, names='value')

    @classmethod
    def select_ipts_help(cls, value):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov")

    @classmethod
    def check_ipts_input(cls, value):
        ipts = value['new']
        full_ipts = 'IPTS-{}'.format(ipts)
        if os.path.exists(os.path.join(cls.start_path, full_ipts)):
            display(HTML("""
                       <style>
                       .result_label {
                          font-style: bold;
                          color: green;
                          font-size: 18px;
                       }
                       </style>
                       """))
            cls.result_label.value = "OK!"
            #select IPTS folder defined
            cls.working_dir_ui.value = full_ipts

        else:
            display(HTML("""
                       <style>
                       .result_label {
                          font-style: bold;
                          color: red;
                          font-size: 18px;
                       }
                       </style>
                       """))
            cls.result_label.value = "DOES NOT EXIST!"

    @classmethod
    def get_working_dir(cls):
        return os.path.join(cls.start_path, cls.working_dir_ui.value)
