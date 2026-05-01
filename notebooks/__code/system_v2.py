"""Instrument/IPTS working-directory selection utilities.

This module provides a widget-driven selector for MARS and VENUS IPTS folders,
plus an offline mode that bypasses widgets and sets a fixed working directory.
"""

import getpass
import glob
import os
import logging

from IPython.display import HTML, display
from ipywidgets import widgets

from __code import LOGGER_FILE
from __code._utilities.file import append_to_file
from __code._utilities.time import get_current_time_in_special_file_name_format

INSTRUMENT_TO_START_PATH = {
    "MARS": "/HFIR/CG1D/",
    "VENUS": "/SNS/VENUS/",
}

def initialize_logging():
    LOG_PATH = "/SNS/VENUS/shared/log/"
    file_name, _ = os.path.splitext(os.path.basename(__file__))
    user_name = os.getlogin()  # add user name to the log file name
    log_file_name = os.path.join(LOG_PATH, f"{file_name}_{user_name}.log")
    logging.basicConfig(
        filename=log_file_name,
        filemode="w",
        format="[%(levelname)s] - %(asctime)s - %(message)s",
        level=logging.INFO,
    )
    logging.info(f"*** Starting a new script {file_name} ***")


class System:
    """Stateful selector for instrument and IPTS working directory.

    Class attributes store the active selection and widget references so other
    notebook cells can query the selected working directory.
    """

    working_dir = ""
    start_path = ""
    verbose = False

    @classmethod
    def select_working_dir(
        cls,
        instrument="VENUS",
        ipts_number=None,
        notebook="N/A",
        offline=False,
        default_working_dir="~/",
        verbose=True,
        instruments=None,
    ):
        """Display the instrument/IPTS selector UI and initialize defaults.

        Parameters
        ----------
        instrument : str
            Default instrument to select ("MARS" or "VENUS").
        ipts_number : str | int | None
            Optional IPTS numeric identifier to preselect as "IPTS-<number>"
            if that folder is available to the current user.
        notebook : str
            Notebook name written to the usage log.
        offline : bool
            When True, skip widget creation and set ``working_dir`` directly.
        default_working_dir : str
            Folder to use in offline mode. ``~/`` by default.
        verbose : bool
            If True, record in the log file information about the selected working directory.
        instruments : list[str] | None
            Optional list of instruments to display. If None, all instruments are shown.
            If a single instrument is provided, the selector widget is replaced by a label.
        """
        if verbose:
            cls.verbose = True
            initialize_logging()
        
        if offline:
            cls.working_dir = os.path.expanduser(default_working_dir)
            cls.start_path = ""
            display(
                HTML(
                    '<span style="font-size: 15px; color:blue">offline mode enabled, working dir set to -> '
                    + cls.working_dir
                    + "</span>"
                )
            )
            cls.log_use(notebook=notebook)
            return

        cls.working_dir = ""

        try:
            display(
                HTML(
                    """
                       <style>
                       .result_label {
                          font-style: bold;
                          color: red;
                          font-size: 18px;
                       }
                       </style>
                       """
                )
            )

            all_instruments = sorted(INSTRUMENT_TO_START_PATH.keys())
            if instruments is not None:
                full_list_instruments = [i for i in instruments if i in all_instruments]
                if not full_list_instruments:
                    full_list_instruments = all_instruments
            else:
                full_list_instruments = all_instruments

            if instrument in full_list_instruments:
                default_instrument = instrument
            else:
                default_instrument = full_list_instruments[0]

            start_path = cls.get_start_path(instrument=default_instrument)
            cls.start_path = start_path
            if verbose:
                logging.info(f"Default instrument: {default_instrument}")
                logging.info(f"Start path for IPTS folders: {start_path}")

            if len(full_list_instruments) == 1:
                cls.instrument_ui = widgets.Select(
                    options=full_list_instruments, value=default_instrument, layout=widgets.Layout(width="20%")
                )
                select_instrument_ui = widgets.HBox(
                    [
                        widgets.HTML("<b>Instrument:</b>"),
                        widgets.Label(default_instrument),
                    ]
                )
            else:
                select_instrument_ui = widgets.HBox(
                    [
                        widgets.HTML("<b>Select Instrument</b>", layout=widgets.Layout(width="20%")),
                        widgets.Select(
                            options=full_list_instruments, value=default_instrument, layout=widgets.Layout(width="20%")
                        ),
                    ]
                )
                cls.instrument_ui = select_instrument_ui.children[1]
                cls.instrument_ui.observe(cls.check_instrument_input, names="value")

            help_ui = widgets.Button(description="HELP", button_style="info")
            help_ui.on_click(cls.select_ipts_help)

            top_hbox = widgets.HBox(
                [
                    widgets.HTML("<b>IPTS-</b>"),
                    widgets.Text(value="", layout=widgets.Layout(width="10%")),
                    widgets.Label("DOES NOT EXIST!", layout=widgets.Layout(width="20%")),
                ]
            )
            cls.result_label = top_hbox.children[2]
            cls.ipts_number = top_hbox.children[1]
            cls.result_label.add_class("result_label")
            or_label = widgets.Label("OR")

            list_and_default_folders = cls.get_list_folders(start_path=start_path)
            if verbose:
                logging.info(f"All IPTS folders found: {list_and_default_folders['user_list_folders']}")
                
            user_list_folders = list_and_default_folders["user_list_folders"]
            if verbose:
                logging.info(f"User-readable IPTS folders found: {user_list_folders}")
            default_value = list_and_default_folders["default_value"]
            if verbose:
                logging.info(f"Default IPTS folder to select: {default_value}")

            bottom_hbox = widgets.HBox(
                [
                    widgets.HTML("<b>Select Folder</b>", layout=widgets.Layout(width="20%")),
                    widgets.Select(
                        options=user_list_folders, value=default_value, layout=widgets.Layout(height="300px")
                    ),
                ]
            )
            cls.user_list_folders = user_list_folders
            box = widgets.VBox([select_instrument_ui, top_hbox, or_label, bottom_hbox, help_ui])
            display(box)

            cls.working_dir_ui = bottom_hbox.children[1]
            cls.working_dir_ui.observe(cls.check_working_dir_selection, names="value")
            cls.manual_ipts_entry_ui = top_hbox.children[1]
            cls.manual_ipts_entry_ui.observe(cls.check_ipts_input, names="value")

            cls.result_label.value = ""
            cls.sync_manual_ipts_entry_with_selection()

            if ipts_number is not None:
                full_ipts_folder = f"IPTS-{ipts_number}"
                if full_ipts_folder in cls.working_dir_ui.options:
                    cls.working_dir_ui.value = full_ipts_folder
                    cls.ipts_number.value = str(ipts_number)

        except Exception:
            cls.working_dir = os.path.expanduser("~")
            display(
                HTML('<span style="font-size: 15px; color:blue">working dir set to -> ' + cls.working_dir + "</span>")
            )

        cls.log_use(notebook=notebook)

    @classmethod
    def log_use(cls, notebook="N/A"):
        """Append a notebook usage entry to the shared logger file."""
        if os.path.exists(os.path.dirname(LOGGER_FILE)):
            username = getpass.getuser()
            date = get_current_time_in_special_file_name_format()
            data = [f"{date}: {username} started using {notebook}"]
            append_to_file(data=data, output_file_name=LOGGER_FILE)

    @classmethod
    def get_list_folders(cls, start_path=""):
        """Return readable IPTS folders under ``start_path``.

        Only directories named ``IPTS-*`` with read access are included.
        """
        list_folders = sorted(glob.glob(os.path.join(start_path, "*")), reverse=True)

        # Only display IPTS folders that the current user can read.
        user_list_folders = [
            os.path.basename(_folder)
            for _folder in list_folders
            if os.path.isdir(_folder) and os.path.basename(_folder).startswith("IPTS-") and os.access(_folder, os.R_OK)
        ]

        default_value = user_list_folders[0] if user_list_folders else ""
        return {"user_list_folders": user_list_folders, "default_value": default_value}

    @classmethod
    def get_instrument_selected(cls):
        """Return the currently selected instrument from the UI."""
        return cls.instrument_ui.value

    @classmethod
    def get_ipts_selected(cls):
        """Return selected IPTS number (without the ``IPTS-`` prefix)."""
        return cls.working_dir_ui.value.split("-", 1)[-1]

    @classmethod
    def get_start_path(cls, instrument="VENUS"):
        """Map an instrument name to its base filesystem path."""
        return INSTRUMENT_TO_START_PATH.get(instrument, INSTRUMENT_TO_START_PATH["VENUS"])

    @classmethod
    def select_ipts_help(cls, value):
        """Open the online help page for IPTS selection."""
        import webbrowser

        webbrowser.open("https://neutronimaging.pages.ornl.gov/tutorial/notebooks/select_ipts/")

    @classmethod
    def check_instrument_input(cls, value_dict):
        """Refresh IPTS list when the instrument selection changes."""
        instrument = value_dict["new"]

        start_path = cls.get_start_path(instrument=instrument)
        cls.start_path = start_path
        list_and_default_folders = cls.get_list_folders(start_path=start_path)

        user_list_folders = list_and_default_folders["user_list_folders"]
        default_value = list_and_default_folders["default_value"]

        cls.working_dir_ui.options = user_list_folders
        cls.ipts_number.value = ""
        cls.result_label.value = ""
        if default_value:
            cls.working_dir_ui.value = default_value
        cls.sync_manual_ipts_entry_with_selection()

    @classmethod
    def check_working_dir_selection(cls, value_dict):
        """Sync IPTS number text field after list selection changes."""
        _ = value_dict
        cls.sync_manual_ipts_entry_with_selection()

    @classmethod
    def sync_manual_ipts_entry_with_selection(cls):
        """Mirror selected IPTS folder value into the manual IPTS text box."""
        selected_folder = cls.working_dir_ui.value
        if isinstance(selected_folder, str) and selected_folder.startswith("IPTS-"):
            cls.ipts_number.value = selected_folder.split("-", 1)[-1]
        else:
            cls.ipts_number.value = ""
        if cls.verbose:
            logging.info(f"Selected IPTS folder: {selected_folder}")
            logging.info(f"Manual IPTS entry synced to: {cls.ipts_number.value}")

    @classmethod
    def check_ipts_input(cls, value):
        """Validate manual IPTS entry and select it if accessible."""
        ipts = value["new"]
        full_ipts = f"IPTS-{ipts}"
        ipts_path = os.path.join(cls.start_path, full_ipts)
        if os.path.isdir(ipts_path) and os.access(ipts_path, os.R_OK):
            cls.result_label.value = "OK"
            if full_ipts in cls.working_dir_ui.options:
                cls.working_dir_ui.value = full_ipts
        else:
            cls.result_label.value = "DOES NOT EXIST!"
        if cls.verbose:
            logging.info(f"Manual IPTS entry changed to: {ipts}")
            logging.info(f"Constructed IPTS path: {ipts_path}")
            logging.info(f"IPTS path exists: {os.path.isdir(ipts_path)}")
            logging.info(f"IPTS path is readable: {os.access(ipts_path, os.R_OK)}")

    @classmethod
    def get_working_dir(cls):
        """Return explicit offline working dir or current UI-derived path."""
        if cls.working_dir:
            return cls.working_dir
        return os.path.join(cls.start_path, cls.working_dir_ui.value)