import glob
from ipywidgets import widgets
import ipywe.fileselector
import ipywidgets as ipyw
import os
import time
import numpy as np
from collections import defaultdict
from IPython.core.display import HTML
from IPython.display import display
import pandas as pd

from __code.file_handler import make_ascii_file_from_string


class ConfigLoader(object):

    config_dict = {}

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_config_file(self):
        hbox = widgets.HBox([widgets.Label("Configuration File Selected:",
                                           layout=widgets.Layout(width='20%')),
                             widgets.Label("N/A",
                                           layout=widgets.Layout(width='80%'))])
        self.config_selected_label = hbox.children[1]
        display(hbox)

        self.config_file_ui = MyFileSelectorPanel(instruction='Select Configuration File (*.config)',
                                                  next=self.load_config,
                                                  start_dir=self.working_dir)
        self.config_file_ui.show()

    def load_config(self, config_file_name):
        self.config_selected_label.value = config_file_name
        try:
            pd_config = pd.read_csv(config_file_name, sep=' ')
        except:
            display(HTML("Error loading config file {}!".format(config_file_name)))
            return

        list_para_name = pd_config['instrument_name']
        list_para_value = pd_config['TOPAZ']

        config_dict = dict(zip(list_para_name, list_para_value))
        # adding config_name tag that contains the name of the loaded config name
        [config_dict['config_name'], _] = os.path.splitext(os.path.basename(config_file_name))
        self.config_dict = config_dict


class ConfigParser(object):


    def __init__(self, config_file=''):
        if config_file:
            self.parse_config(config_file = config_file)

    def parse_config(self, config_file=''):
        pass

class MyFileSelectorPanel:
    """Files and directories selector"""

    # If ipywidgets version 5.3 or higher is used, the "width="
    # statement should change the width of the file selector. "width="
    # doesn't appear to work in earlier versions.
    select_layout = ipyw.Layout(width="750px")
    select_multiple_layout = ipyw.Layout(width="750px",
                                         display="flex", flex_flow="column")
    button_layout = ipyw.Layout(margin="5px 40px")
    toolbar_button_layout = ipyw.Layout(margin="5px 10px", width="100px")
    toolbar_box_layout = ipyw.Layout(border='1px solid lightgrey', padding='3px', margin='5px 50px 5px 5px')
    label_layout = ipyw.Layout(width="250px")
    layout = ipyw.Layout()

    def js_alert(self, m):
        js = "<script>alert('%s');</script>" % m
        display(HTML(js))
        return

    def __init__(
            self,
            instruction,
            start_dir=".", type='file', next=None,
            multiple=False, newdir_toolbar_button=False):
        """
        Create FileSelectorPanel instance
        Parameters
        ----------
        instruction : str
            instruction to users for file/dir selection
        start_dir : str
            starting directory path
        type : str
            type of selection. "file" or "directory"
        multiple: bool
            if True, multiple files/dirs can be selected
        next : function
            callback function to execute after the selection is selected
        newdir_toolbar_button : bool
            If true, a button to create new directory is added to the toolbar
        """
        if type not in ['file', 'directory']:
            raise ValueError("type must be either file or directory")
        self.instruction = instruction
        self.type = type
        self.multiple = multiple
        self.newdir_toolbar_button = newdir_toolbar_button
        self.createPanel(os.path.abspath(start_dir))
        self.next = next
        return

    def activate_status(self, is_disabled=True):
        self.button_layout.disabled = is_disabled
        self.ok.disabled = is_disabled
        self.jumpto_input.disabled = is_disabled
        self.enterdir.disabled = is_disabled
        self.jumpto_button.disabled = is_disabled
        self.select.disabled = is_disabled

    def createPanel(self, curdir):
        wait = ipyw.HTML("Please wait...")
        display(wait)

        self.curdir = curdir
        explanation = ipyw.Label(self.instruction, layout=self.label_layout)
        # toolbar
        # "jump to"
        self.jumpto_input = jumpto_input = ipyw.Text(
            value=curdir, placeholder="", description="Location: ", layout=ipyw.Layout(width='300px'))
        jumpto_button = ipyw.Button(description="Jump", layout=self.toolbar_button_layout)
        jumpto_button.on_click(self.handle_jumpto)
        jumpto = ipyw.HBox(children=[jumpto_input, jumpto_button], layout=self.toolbar_box_layout)
        self.jumpto_button = jumpto_button
        if self.newdir_toolbar_button:
            # "new dir"
            self.newdir_input = newdir_input = ipyw.Text(
                value="", placeholder="new dir name", description="New subdir: ",
                layout=ipyw.Layout(width='180px'))
            newdir_button = ipyw.Button(description="Create", layout=self.toolbar_button_layout)
            newdir_button.on_click(self.handle_newdir)
            newdir = ipyw.HBox(children=[newdir_input, newdir_button], layout=self.toolbar_box_layout)
            toolbar = ipyw.HBox(children=[jumpto, newdir])
        else:
            toolbar = ipyw.HBox(children=[jumpto])
        # entries in this starting dir
        entries_files = sorted(os.listdir(curdir))
        entries_paths = [os.path.join(curdir, e) for e in entries_files]
        entries_ftime = create_file_times(entries_paths)
        entries = create_nametime_labels(entries_files, entries_ftime)
        self._entries = entries = [' .', ' ..', ] + entries
        if self.multiple:
            value = []
            self.select = ipyw.SelectMultiple(
                value=value, options=entries,
                description="Select",
                layout=self.select_multiple_layout)
        else:
            value = entries[0]
            self.select = ipyw.Select(
                value=value, options=entries,
                description="Select",
                layout=self.select_layout)
        """When ipywidgets 7.0 is released, the old way that the select or select multiple 
           widget was set up (see below) should work so long as self.select_layout is changed
           to include the display="flex" and flex_flow="column" statements. In ipywidgets 6.0,
           this doesn't work because the styles of the select and select multiple widgets are
           not the same.

        self.select = widget(
            value=value, options=entries,
            description="Select",
            layout=self.select_layout) """
        # enter directory button
        self.enterdir = ipyw.Button(description='Enter directory', layout=self.button_layout)
        self.enterdir.on_click(self.handle_enterdir)
        # select button
        self.ok = ipyw.Button(description='Select', layout=self.button_layout)
        self.ok.on_click(self.validate)
        buttons = ipyw.HBox(children=[self.enterdir, self.ok])
        lower_panel = ipyw.VBox(children=[self.select, buttons],
                                layout=ipyw.Layout(border='1px solid lightgrey', margin='5px', padding='10px'))
        self.panel = ipyw.VBox(children=[explanation, toolbar, lower_panel], layout=self.layout)
        wait.close()
        return

    def handle_jumpto(self, s):
        v = self.jumpto_input.value
        if not os.path.isdir(v): return
        self.remove()
        self.createPanel(v)
        self.show()
        return

    def handle_newdir(self, s):
        v = self.newdir_input.value
        path = os.path.join(self.curdir, v)
        try:
            os.makedirs(path)
        except:
            return
        self.remove()
        self.createPanel(path)
        self.show()
        return

    def handle_enterdir(self, s):
        v = self.select.value
        v = del_ftime(v)
        if self.multiple:
            if len(v) != 1:
                self.js_alert("Please select a directory")
                return
            v = v[0]
        p = os.path.abspath(os.path.join(self.curdir, v))
        if os.path.isdir(p):
            self.remove()
            self.createPanel(p)
            self.show()
        return

    def validate(self, s):
        v = self.select.value
        v = del_ftime(v)
        # build paths
        if self.multiple:
            vs = v
            paths = [os.path.join(self.curdir, v) for v in vs]
        else:
            path = os.path.join(self.curdir, v)
            paths = [path]
        # check type
        if self.type == 'file':
            for p in paths:
                if not os.path.isfile(p):
                    self.js_alert("Please select file(s)")
                    return
        else:
            assert self.type == 'directory'
            for p in paths:
                if not os.path.isdir(p):
                    self.js_alert("Please select directory(s)")
                    return
        # set output
        if self.multiple:
            self.selected = paths
        else:
            self.selected = paths[0]
        # clean up
        #self.remove()
        # next step
        if self.next:
            self.next(self.selected)
        return

    def show(self):
        display(HTML("""
        <style type="text/css">
        .jupyter-widgets select option {font-family: "Lucida Console", Monaco, monospace;}
        div.output_subarea {padding: 0px;}
        div.output_subarea > div {margin: 0.4em;}
        </style>
        """))
        display(self.panel)

    def remove(self):
        close(self.panel)

def close(w):
    "recursively close a widget"
    if hasattr(w, 'children'):
        for c in w.children:
            close(c)
            continue
    w.close()
    return

def create_file_times(paths):
    """returns a list of file modify time"""
    ftimes = []
    for f in paths:
        try:
            if os.path.isdir(f):
                ftimes.append("Directory")
            else:
                ftime_sec = os.path.getmtime(f)
                ftime_tuple = time.localtime(ftime_sec)
                ftime = time.asctime(ftime_tuple)
                ftimes.append(ftime)
        except OSError:
            ftimes.append("Unknown or Permission Denied")
    return ftimes

def create_nametime_labels(entries, ftimes):
    if not entries:
        return []
    max_len = max(len(e) for e in entries)
    n_spaces = 5
    fmt_str = ' %-' + str(max_len + n_spaces) + "s|" + ' ' * n_spaces + '%s'
    label_list = [fmt_str % (e, f) for e, f in zip(entries, ftimes)]
    return label_list

def del_ftime(file_label):
    """file_label is either a str or a tuple of strings"""
    if isinstance(file_label, tuple):
        return tuple(del_ftime(s) for s in file_label)
    else:
        file_label_new = file_label.strip()
        if file_label_new != "." and file_label_new != "..":
            file_label_new = file_label_new.split("|")[0].rstrip()
    return (file_label_new)


class ConfigDict(object):
    # for config file output

    config = {'instrument_name': 'TOPAZ',
              'calibration_file_1': '',
              'calibration_file_2': 'None',
              'z_offset': 0.0,
              'x_offset': 0.0,
              'data_directory': '',
              'output_directory': '',
              'use_monitor_counts': False,
              'min_tof': 1000,
              'max_tof': 16600,
              'monitor_index': 0,
              'min_monitor_tof': 800,
              'max_monitor_tof': 12500,
              'read_UB': True,
              'UB_filename': '',
              'cell_type': 'Monoclinic',
              'centering': 'P',
              'num_peaks_to_find': 300,
              'min_d': 5,
              'max_d': 25,
              'tolerance': 0.12,
              'integrate_predicted_peaks': True,
              'min_pred_wl': 0.5,
              'max_pred_wl': 3.4,
              'min_pred_dspacing': 0.5,
              'max_pred_dspacing': 11.0,
              'use_sphere_integration': False,
              'use_ellipse_integration': False,
              'use_fit_peaks_integration': False,
              'use_cylindrical_integration': False,
              'peak_radius': 0.130,
              'bkg_inner_radius': 0.14,
              'bkg_outer_radius': 0.15,
              'integrate_if_edge_peak': True,
              'ellipse_region_radius': 0.20,
              'ellipse_size_specified': True,
              'rebin_step': -0.004,
              'preserve_events': True,
              'use_ikeda_carpenter': False,
              'n_bad_edge_pixels': 0,
              'cylinder_radius': 0.05,
              'cylinder_length': 0.30,
              'exp_name': '',
              'reduce_one_run_script': 'ReduceSCD_OneRun_xz_offset.py',
              'run_nums': '',
              'slurm_queue_name': 'None',
              'max_processes': 8,
              'config_name': 'tmp.config',
              }

    def __init__(self, config_dict={}):
        self.config_dict = config_dict

    def get_parameter_value(self, parameter):
        para_type = type(self.config[parameter])
        if self.config_dict[parameter]:
            config_para = self.config_dict[parameter]
            if isinstance(config_para, bool):
                if config_para in ["True", "true"]:
                    return True
                else:
                    return False
            return para_type(config_para)
        else:
            return self.config[parameter]


class TopazConfigGenerator(object):

    ikeda_flag_ui = None
    v_box = None
    fit_peaks_vertical_layout = None
    reduce_ui = None
    reduce_label_ui = None

    reduce_one_run_script = 'N/A'

    left_column_width = '15%'

    # for config file output
    config = {'instrument_name': 'TOPAZ',
              'calibration_file_1': '',
              'calibration_file_2': 'None',
              'z_offset': 0.0,
              'x_offset': 0.0,
              'data_directory': '',
              'output_directory': '',
              'use_monitor_counts': False,
              'min_tof': 1000,
              'max_tof': 16600,
              'monitor_index': 0,
              'min_monitor_tof': 800,
              'max_monitor_tof': 12500,
              'read_UB': True,
              'UB_filename': '',
              'cell_type': 'Monoclinic',
              'centering': 'P',
              'num_peaks_to_find': 300,
              'min_d': 5,
              'max_d': 25,
              'tolerance': 0.12,
              'integrate_predicted_peaks': True,
              'min_pred_wl': 0.5,
              'max_pred_wl': 3.4,
              'min_pred_dspacing': 0.5,
              'max_pred_dspacing': 11.0,
              'use_sphere_integration': False,
              'use_ellipse_integration': False,
              'use_fit_peaks_integration': False,
              'use_cylindrical_integration': False,
              'peak_radius': 0.130,
              'bkg_inner_radius': 0.14,
              'bkg_outer_radius': 0.15,
              'integrate_if_edge_peak': True,
              'ellipse_region_radius': 0.20,
              'ellipse_size_specified': True,
              'rebin_step': -0.004,
              'preserve_events': True,
              'use_ikeda_carpenter': False,
              'n_bad_edge_pixels': 0,
              'cylinder_radius': 0.05,
              'cylinder_length': 0.30,
              'exp_name': '',
              'reduce_one_run_script': 'ReduceSCD_OneRun_xz_offset.py',
              'run_nums': '',
              'slurm_queue_name': 'None',
              'max_processes': 8,
                }

    cell_type = ['Triclinic',
                 'Monoclinic',
                 'Orthorhombic',
                 'Tetragonal',
                 'Rhombohedral',
                 'Hexagonal',
                 'Cubic']

    centering_mode = {'P': cell_type.copy(),
                      'I': ['Tetragonal', 'Monoclinic', 'Cubic'],
                      'A': ['Monoclinic', 'Orthorhombic'],
                      'B': ['Monoclinic', 'Orthorhombic'],
                      'C': ['Monoclinic', 'Orthorhombic'],
                      'F': ['Orthorhombic', 'Cubic'],
                      'Robv': ['Rhombohedral'],
                      'Rrev': ['Rhombohedral'],
                      }

    cell_type_dict = {}
    o_config_dict = None

    def __init__(self, working_dir='', config_dict_loaded={}):
        self.working_dir = working_dir
        self.config_dict_loaded = config_dict_loaded

        self.o_config_dict = ConfigDict(config_dict=config_dict_loaded)

        self.init_css()
        self.__create_cell_type_centering_dict()

    def init_css(self):
        display(HTML("""
            <style>
            .mylabel_key {
               font-style: bold;
               color: black;
               font-size: 18px;
            }
            </style>
            """))

    def __create_cell_type_centering_dict(self):
        self.cell_type_dict = defaultdict()
        for _key in self.centering_mode.keys():
            _list = self.centering_mode[_key]
            for _item in _list:
                self.cell_type_dict.setdefault(_item, []).append(_key)

    def __get_dict_parameter_value(self, parameter):
        if self.config_dict[parameter]:
            return self.config_dict[parameter]
        else:
            return self.config[parameter]

    def define_config_file_name(self):

        _default_config = self.o_config_dict.get_parameter_value('config_name')

        display(HTML("<h2>Define Config File Name</h2>"))
        config_file_ui = widgets.HBox([widgets.Label("Config File Name:",
                                                     layout=widgets.Layout(width='20%')),
                                       widgets.Text(_default_config,
                                                    layout=widgets.Layout(width='75%')),
                                       widgets.Label(".cfg",
                                                     layout=widgets.Layout(width='5%'))])
        self.config_file_ui = config_file_ui.children[1]
        display(config_file_ui)

    def select_input_data_folder(self):

        # ****** Select Input Data Folder ********

        display(HTML("<h2 id='input_directory'>Select Input Data Folder</h2>"))

        _input_data_folder = self.o_config_dict.get_parameter_value('data_directory')

        select_input_data_folder_ui = None
        def select_input_data_folder(selection):
            select_input_data_folder_ui.children[1].value = selection

        select_input_data_folder_ui = widgets.HBox([widgets.Label("Input Data Folder Selected:",
                                                                  layout=widgets.Layout(width='25%')),
                                                    widgets.Label(_input_data_folder,
                                                                  layout=widgets.Layout(width='70%'))])

        select_input_data_folder_ui.children[0].add_class("mylabel_key")
        self.input_data_folder_ui = select_input_data_folder_ui.children[1]
        display(select_input_data_folder_ui)

        if not (_input_data_folder == 'N/A') and os.path.exists(_input_data_folder):
            start_dir = _input_data_folder
        else:
            start_dir = os.path.join(self.working_dir, 'data')

        input_folder_ui = MyFileSelectorPanel(instruction='',
                                              start_dir=start_dir,
                                              next=select_input_data_folder,
                                              type='directory')
        input_folder_ui.show()


    def select_output_folder(self):

        # ****** Select or Create Output Folder ********

        display(HTML("<h2 id='output_directory'>Select or Create Output Folder</h2>"))
        _output_data_folder = self.o_config_dict.get_parameter_value('output_directory')

        select_output_data_folder_ui = None

        def select_output_data_folder(selection):
            select_output_data_folder_ui.children[1].value = selection

        if not (_output_data_folder == 'N/A') and os.path.exists(_output_data_folder):
            start_dir = _output_data_folder
        else:
            start_dir = os.path.join(self.working_dir, 'shared')

        select_output_data_folder_ui = widgets.HBox([widgets.Label("Output Data Folder Selected:",
                                                                   layout=widgets.Layout(width='25%')),
                                                     widgets.Label(start_dir,
                                                                   layout=widgets.Layout(width='70%'))])

        select_output_data_folder_ui.children[0].add_class("mylabel_key")
        self.output_data_folder_ui = select_output_data_folder_ui.children[1]
        display(select_output_data_folder_ui)

        output_folder_ui = MyFileSelectorPanel(instruction='Location of Output Folder',
                                               start_dir=start_dir,
                                               type='directory',
                                               next=select_output_data_folder,
                                               newdir_toolbar_button=True)
        output_folder_ui.show()

    def parameters_1(self):
        # def cell_type_changed(value):
        #     centering_ui.children[1].options = self.cell_type_dict[value['new']]
        #     centering_ui.children[1].value = self.cell_type_dict[value['new']][0]
        #
        # def centering_changed(value):
        #     pass

        # calibration files
        working_dir = self.working_dir

        calib_folder = os.path.dirname(working_dir)
        list_of_calibration_file = glob.glob(os.path.join(calib_folder, 'shared/calibrations') + '/2017C/*.DetCal')
        list_of_calibration_file.append('None')
        _calibration_file = self.o_config_dict.get_parameter_value('calibration_file_1')
        if not (_calibration_file is None) and os.path.exists(_calibration_file):
            list_of_calibration_file = [_calibration_file] + list_of_calibration_file

        # ****** Specify calibration file(s) ********

        display(HTML("<h2 id='calibration_file'>Specify calibration file(s)</h2><br>SNAP requires two calibration files, one for each bank. \
                     If the default detector position is to be used, specify <strong>None</strong> as the calibration file name."))

        calibration1_ui = widgets.HBox([widgets.Label("Calibration File:",
                                                      layout=widgets.Layout(width='15%')),
                                        widgets.Dropdown(options=list_of_calibration_file,
                                                         layout=widgets.Layout(width='85%'))])
        self.calibration_file_ui = calibration1_ui.children[1]
        display(calibration1_ui)

        # ****** Goniometer z Offset correction ********

        display(HTML("<h2>Goniometer z Offset Correction</h2><br>Test correction for Goniometer z offset"))

        _z_offset = self.o_config_dict.get_parameter_value('z_offset')
        _x_offset = self.o_config_dict.get_parameter_value('x_offset')

        offset_min_value = -10.0
        offset_max_value = +10.0

        if not (offset_min_value <= _x_offset <= offset_max_value):
            _x_offset = 0.0

        if not (offset_min_value <= _z_offset <= offset_max_value):
            _z_offset = 0.0

        zoffset_ui = widgets.HBox([widgets.Label("z_offset:",
                                                 layout=widgets.Layout(width='5%')),
                                   widgets.FloatSlider(value=_z_offset,
                                                       min=offset_min_value,
                                                       max=offset_max_value,
                                                       readout_format='.2f',
                                                       continuous_update=False,
                                                       layout=widgets.Layout(width='30%'))])

        xoffset_ui = widgets.HBox([widgets.Label("x_offset:",
                                                 layout=widgets.Layout(width='5%')),
                                   widgets.FloatSlider(value=_x_offset,
                                                       min=offset_min_value,
                                                       max=offset_max_value,
                                                       readout_format='.2f',
                                                       continuous_update=False,
                                                       layout=widgets.Layout(width='30%'))])

        self.zoffset_ui = zoffset_ui.children[1]
        self.xoffset_ui = xoffset_ui.children[1]
        offset_ui = widgets.VBox([zoffset_ui, xoffset_ui])
        display(offset_ui)

        # ****** Use Monitor Counts ?********

        display(HTML("<h2>Use Monitor Counts ?</h2><br> If use_monitor_counts is True, then the integrated beam monitor \
            counts will be used for scaling. <br>If use_monitor_counts is False, \
            then the integrated proton charge will be used for scaling. <br><br>These \
            values will be listed under MONCNT in the integrate file."))

        _monitor_flag = self.o_config_dict.get_parameter_value('use_monitor_counts')
        monitor_counts_flag_ui = widgets.Checkbox(value=_monitor_flag,
                                                  description='Use Monitor Counts')
        self.monitor_counts_flag_ui = monitor_counts_flag_ui
        display(monitor_counts_flag_ui)

        # ****** TOF and Monitor ********

        display(HTML("<h2>TOF and Monitor</h2><br>Min & max tof determine the range of events loaded.<br> Min & max monitor tof \
                    determine the range of tofs integrated in the monitor data to get the \
                    total monitor counts. <br>You need these even if Use Monitor Counts is False."))


        tof_ui = widgets.HBox([widgets.Label("TOF Range",
                                             layout=widgets.Layout(width=self.left_column_width)),
                               widgets.IntRangeSlider(value=[1000, 16600],
                                                      min=500,
                                                      max=16600,
                                                      step=1,
                                                      continuous_update=False,
                                                      readout_format='d',
                                                      layout=widgets.Layout(width='50%')),
                               widgets.Label("\u00B5s",
                                             layout=widgets.Layout(width='20%'))])
        self.tof_ui = tof_ui.children[1]

        monitor_index_ui = widgets.HBox([widgets.Label("Monitor Index",
                                                       layout=widgets.Layout(width=self.left_column_width)),
                                         widgets.Dropdown(options=['0', '1'],
                                                          value='0',
                                                          layout=widgets.Layout(width='10%'))])
        self.monitor_index_ui = monitor_index_ui.children[1]

        monitor_ui = widgets.HBox([widgets.Label("Monitor TOF Range",
                                                 layout=widgets.Layout(width=self.left_column_width)),
                                   widgets.IntRangeSlider(value=[800, 12500],
                                                          min=500,
                                                          max=16600,
                                                          step=1,
                                                          continuous_update=False,
                                                          readout_format='d',
                                                          layout=widgets.Layout(width='50%')),
                                   widgets.Label("\u00B5s",
                                                 layout=widgets.Layout(width='20%'))])
        self.monitor_tof_ui = monitor_ui.children[1]

        tof_ui = widgets.VBox([tof_ui, monitor_index_ui, monitor_ui])

        display(tof_ui)

        # ****** UB ********

        display(HTML("<h2 id='ub_filename'>UB</h2><br>Read the UB matrix from file. This option will be applied to each run and used for \
            combined file. This option is especially helpful for 2nd frame TOPAZ data."))

        ub_flag_ui = widgets.Checkbox(value=False,
                                      description='Read UB')

        ub_file_selected_ui = widgets.HBox([widgets.Label("UB File Selected:",
                                                          layout=widgets.Layout(width='20%')),
                                            widgets.Label("N/A",
                                                          layout=widgets.Layout(width='80%'))])
        ub_file_selected_ui.children[0].add_class("mylabel_key")
        self.ub_file_selected_ui = ub_file_selected_ui

        def ub_flag_changed(value):
            display_file_selection_flag = value['new']
            self.ub_ui.activate_status(not display_file_selection_flag)
            if display_file_selection_flag:
                ub_file_selected_ui.layout.visibility = 'visible'
            else:
                ub_file_selected_ui.layout.visibility = 'hidden'

        self.ub_flag_ui = ub_flag_ui
        ub_flag_ui.observe(ub_flag_changed, names='value')
        display(ub_flag_ui)

        def select_ub_file(selection):
            ub_file_selected_ui.children[1].value = selection

        display(ub_file_selected_ui)
        self.ub_ui = MyFileSelectorPanel(instruction='Select UB File (*.mat)',
                                         start_dir=os.path.join(working_dir, 'shared'),
                                         next=select_ub_file)

        # init display
        self.ub_ui.show()
        ub_flag_changed({'new': self.ub_flag_ui.value})


    def parameters_2(self):

        def cell_type_changed(value):
            centering_ui.children[1].options = self.cell_type_dict[value['new']]
            centering_ui.children[1].value = self.cell_type_dict[value['new']][0]

        # ****** Cell ********

        display(HTML("<h2>Cell</h2><br>Specifiy a conventional cell type and centering.<br>If these are None, only \
            one .mat and .integrate file will be written for this run, and they will \
            be in terms of the Niggli reduced cell.  If these specifiy a valid \
            cell type and centering, an additional .mat and .integrate file will be \
            written for the specified cell_type and centering.<br><br><strong>NOTE:</strong> If run in \
            parallel, the driving script will only read the Niggli version of the \
            .integrate file, and will combine, re-index and convert to a conventional \
            cell, so these can usually be left as None.<br><br> \
            Cell transformation is not applied to cylindrical profiles, \
            i.e. use None if cylindrical integration is used!  "))

        cell_type_ui = widgets.HBox([widgets.Label("Cell Type:",
                                                   layout=widgets.Layout(width=self.left_column_width)),
                                     widgets.Dropdown(options=self.cell_type,
                                                      value='Monoclinic',
                                                      layout=widgets.Layout(width='20%'))])
        cell_type_ui.children[1].observe(cell_type_changed, names='value')
        self.cell_type_ui = cell_type_ui.children[1]

        centering_ui = widgets.HBox([widgets.Label("Centering:",
                                                   layout=widgets.Layout(width=self.left_column_width)),
                                     widgets.Dropdown(options=self.cell_type_dict['Monoclinic'],
                                                      value='P',
                                                      layout=widgets.Layout(width='20%'))])
        self.centering_ui = centering_ui.children[1]
        # centering_ui.children[1].observe(centering_changed, names='value')

        cell_ui = widgets.VBox([cell_type_ui, centering_ui])

        display(cell_ui)

        # ****** Number of Peaks ********

        display(HTML("<h2>Number of Peaks</h2><br> Number of peaks to find, per run, both for getting the UB matrix, \
        AND to determine how many peaks are integrated, if peak positions are \
        NOT predicted. <br><br> <strong>NOTE:</strong> This number must be choosen carefully. <ul><li> If too \
        many peaks are requested, find peaks will take a very long time and \
        the returned peaks will probably not even index, since most of them \
        will be 'noise' peaks.</li><li> If too few are requested, then there will be \
        few peaks to be integrated, and the UB matrix may not be as accurate \
        as it should be for predicting peaks to integrate.</li></ul>"))

        peak_ui = widgets.HBox([widgets.Label("Number of Peaks:",
                                              layout=widgets.Layout(width=self.left_column_width)),
                                widgets.IntSlider(value=300,
                                                  min=100,
                                                  max=3000,
                                                  layout=widgets.Layout(width='30%'))])
        self.number_peak_ui = peak_ui.children[1]
        display(peak_ui)

        # ****** min_d, max_d and Tolerance ********

        display(HTML("<h2>min_d, max_d and Tolerance</h2><br>min_d, max_d and tolerance control indexing peaks.<br><br>max_d is also \
            used to specify a threshold for the separation between peaks \
            returned by FindPeaksMD, so it should be specified somewhat larger \
            than the largest cell edge in the Niggli reduced cell for the sample."))

        d_ui = widgets.HBox([widgets.Label("d",
                                           layout=widgets.Layout(width='1%')),
                             widgets.IntRangeSlider(value=[5, 25],
                                                    min=3,
                                                    max=90,
                                                    step=1,
                                                    layout=widgets.Layout(width='30%')),
                             widgets.Label("\u00c5")])
        self.d_ui = d_ui.children[1]

        tolerance_ui = widgets.HBox([widgets.Label("Tolerance",
                                                   layout=widgets.Layout(width='10%')),
                                     widgets.FloatSlider(value=0.12,
                                                         min=0.06,
                                                         max=0.51,
                                                         step=0.01,
                                                         layout=widgets.Layout(width='30%'))])
        self.tolerance_ui = tolerance_ui.children[1]

        d_tolerance_ui = widgets.VBox([d_ui, tolerance_ui])

        display(d_tolerance_ui)

        # ****** Predicted Peak ********

        display(HTML("<h2>Predicted Peak</h2><br> If predicted peak positions are to be integrated, \
            then the integrate_predicted_peaks flag should be set to True and the range \
            of wavelengths and d-spacings must be specified"))

        pred_flag_ui = widgets.HBox([widgets.Label("Integrate Predicted Peaks?",
                                                   layout=widgets.Layout(width='20%')),
                                     widgets.Checkbox(value=False,
                                                      layout=widgets.Layout(width='20%'))])
        self.pred_flag_ui = pred_flag_ui.children[1]

        pred_ui = widgets.HBox([widgets.Label("Predicted Wavelengths",
                                              layout=widgets.Layout(width='20%')),
                                widgets.FloatRangeSlider(value=[0.5, 3.4],
                                                         min=.25,
                                                         max=3.6,
                                                         layout=widgets.Layout(width='35%')),
                                widgets.Label("\u00c5")])
        self.pred_ui = pred_ui.children[1]

        pred_dspacing_ui = widgets.HBox([widgets.Label("Predicted dspacing",
                                                       layout=widgets.Layout(width='20%')),
                                         widgets.FloatRangeSlider(value=[0.5, 11.0],
                                                                  min=.25,
                                                                  max=12,
                                                                  layout=widgets.Layout(width='35%')),
                                         widgets.Label("\u00c5")])
        self.pred_dspacing_ui = pred_dspacing_ui.children[1]

        predicted_ui = widgets.VBox([pred_flag_ui, pred_ui, pred_dspacing_ui])
        display(predicted_ui)

        # ****** Integration Method ********

        display(HTML("<h2>Integration Method</h2><br> Select one of the following integration method."))

        inte_ui = widgets.HBox([widgets.Label("Integration Method",
                                              layout=widgets.Layout(width='15%')),
                                widgets.Dropdown(options=['Sphere', 'Ellipse', 'Cylindrical', 'Fit Peaks'],
                                                 value='Ellipse',
                                                 layout=widgets.Layout(width='20%'))])
        self.inte_ui = inte_ui.children[1]
        display(inte_ui)

        _answer_ikeda = False

        # display(HTML("<h2>Integration Control Parameters</h2>"))

        peak_ui = widgets.HBox([widgets.Label("Peak Radius",
                                              layout=widgets.Layout(width='25%')),
                                widgets.FloatSlider(value=0.13,
                                                    min=0.05,
                                                    max=0.25,
                                                    step=0.001,
                                                    readout_format='.3f',
                                                    layout=widgets.Layout(width='30%')),
                                widgets.Label("\u00c5")])
        self.peak_ui = peak_ui.children[1]

        bkg_ui = widgets.HBox([widgets.Label("Background Inner and Outer Radius",
                                             layout=widgets.Layout(width='25%')),
                               widgets.FloatRangeSlider(value=[0.14, 0.15],
                                                        min=peak_ui.children[1].value,
                                                        max=0.2,
                                                        step=0.001,
                                                        readout_format='.3f',
                                                        layout=widgets.Layout(width='30%')),
                               widgets.Label("\u00c5")])
        self.bkg_ui = bkg_ui.children[1]


        def on_peak_changed(change):
            new_range = [change['new'], change['new'] * 1.2]
            bkg_ui.children[1].min = change['new']
            bkg_ui.children[1].max = change['new'] * 1.2

        peak_ui.children[1].observe(on_peak_changed, names='value')

        vertical_layout = [peak_ui, bkg_ui]

        ## will be display only if Sphere has been selected
        inte_flag_ui = widgets.HBox([widgets.Label("Integrate if Edge Peak?",
                                                   layout=widgets.Layout(width='15%')),
                                     widgets.Checkbox(value=True)])
        self.inte_flag_ui = inte_flag_ui.children[1]
        vertical_layout.append(inte_flag_ui)
        ### end

        ellipse_region_ui = widgets.HBox([widgets.Label("Ellipse Region Radius",
                                                        layout=widgets.Layout(width='25%')),
                                          widgets.FloatSlider(value=0.20,
                                                              min=bkg_ui.children[1].value[1],
                                                              max=0.30,
                                                              step=0.001,
                                                              readout_format='.3f',
                                                              layout=widgets.Layout(width='30%')),
                                          widgets.Label("\u00c5")])
        self.ellipse_region_radius_ui = ellipse_region_ui.children[1]
        vertical_layout.append(ellipse_region_ui)

        ellipse_size_ui = widgets.HBox([widgets.Label("Ellipse Size Specified",
                                                      layout=widgets.Layout(width='25%')),
                                        widgets.Checkbox(value=True,
                                                         layout=widgets.Layout(width='20%'))])

        self.ellipse_size_ui = ellipse_size_ui
        self.ellipse_size_ui_checkbox = ellipse_size_ui.children[1]
        vertical_layout.append(ellipse_size_ui)
        integration_ui = widgets.VBox(vertical_layout)
        display(integration_ui)

        def on_back_outer_changed(change):
            ellipse_region_ui.children[1].min = change['new'][1]

        bkg_ui.children[1].observe(on_back_outer_changed, names='value')

        def inte_method_changed(value):


            _visibility_inte_flag = 'hidden'
            _cylindrical_flag = 'hidden'
            _fit_peaks_flag = 'hidden'
            if value['new'] in ['Sphere', 'Ellipse']:
                _visibility = 'visible'
                if value['new'] == 'Sphere':
                    _visibility_inte_flag = 'visible'
                _answer_ikeda = False
            else:

                if value['new'] == 'Cylindrical':
                    _cylindrical_flag = 'visible'

                else:
                    _fit_peaks_flag = 'visible'

                _visibility = 'hidden'
                _answer_ikeda = True

            if self.fit_peaks_vertical_layout:
                self.fit_peaks_vertical_layout.layout.visibility = _fit_peaks_flag

            if self.ikeda_flag_ui:
                self.ikeda_flag_ui.value = str(_answer_ikeda)

            peak_ui.layout.visibility = _visibility
            bkg_ui.layout.visibility = _visibility
            integration_ui.layout.visibility = _visibility
            ellipse_region_ui.layout.visibility = _visibility
            inte_flag_ui.layout.visibility = _visibility_inte_flag

            if self.v_box:
                self.v_box.layout.visibility = _cylindrical_flag

        inte_method_changed({'new': 'Ellipse'})
        inte_ui.children[1].observe(inte_method_changed, names='value')
        # self.inte_flag_ui = inte_flag_ui

        #_answer_ikeda = str(inte_flag_ui.children[1].value)

        # display(HTML("<h2>Cylindrical Integration Control Parameters</h2>"))

        self.radius_ui = widgets.HBox([widgets.Label("Cylinder Radius",
                                                layout=widgets.Layout(width='15%')),
                                  widgets.FloatSlider(value=0.05,
                                                      min=0.02,
                                                      max=0.1,
                                                      step=0.001,
                                                      readout_format="0.3f",
                                                      layout=widgets.Layout(width='30%')),
                                  widgets.Label("\u00c5")])
        self.cylinder_radius_ui = self.radius_ui.children[1]
        self.length_ui = widgets.HBox([widgets.Label("Cylinder Length",
                                                layout=widgets.Layout(width='15%')),
                                  widgets.FloatSlider(value=0.3,
                                                      min=0.1,
                                                      max=0.5,
                                                      step=0.01,
                                                      readout_format="0.3f",
                                                      layout=widgets.Layout(width='30%')),
                                  widgets.Label("\u00c5")])
        self.cylinder_length_ui = self.length_ui.children[1]

        self.v_box = widgets.VBox([self.radius_ui, self.length_ui])
        display(self.v_box)
        self.v_box.layout.visibility = 'hidden'

        # display(HTML("<h2>Fit Peaks Integration Control Parameters</h2>"))

        line_1 = widgets.Label("Rebin")
        line_1.add_class("mylabel_key")
        line_2 = widgets.VBox([widgets.Label("--> Logarithmic",
                                             layout=widgets.Layout(width='25%',
                                                                   left='20px')),
                               widgets.Label("--> 0.006",
                                             layout=widgets.Layout(width='25%',
                                                                   left='20px'))])

        line_3 = widgets.HBox([widgets.Label("Preserve Events:",
                                             layout=widgets.Layout(width='25%')),
                               widgets.Label("True")])
        line_3.children[0].add_class("mylabel_key")
        line_4 = widgets.HBox([widgets.Label("Use Ikeda Carpenter:",
                                             layout=widgets.Layout(width='25%')),
                               widgets.Label(str(_answer_ikeda))])
        line_4.children[0].add_class("mylabel_key")
        self.ikeda_flag_ui = line_4.children[1]

        self.fit_peaks_vertical_layout = widgets.VBox([line_1, line_2, line_3, line_4])
        display(self.fit_peaks_vertical_layout)
        self.fit_peaks_vertical_layout.layout.visibility = 'hidden'

        # ****** Bad Edge Pixels ********

        display(HTML("<h2>Bad Edge Pixels</h2>"))

        bad_pixels_ui = widgets.HBox([widgets.Label("Nbr bad edge pixels:",
                                                    layout=widgets.Layout(width='15%')),
                                      widgets.IntSlider(value=0,
                                                        min=0,
                                                        max=50,
                                                        layout=widgets.Layout(width='30%'))])

        self.bad_pixels_ui = bad_pixels_ui.children[1]
        display(bad_pixels_ui)

        # ****** Experiment Name ********

        display(HTML("<h2>Experiment Name</h2>"))

        exp_name_ui = widgets.Text("",
                                   layout=widgets.Layout(width="50%"))
        self.exp_name_ui = exp_name_ui
        display(exp_name_ui)

        # ****** Run Numbers to Reduce ********

        display(HTML("<h2 id='run_nums'>Run Numbers to Reduce</h2><br>Specify the run numbers that should be reduced."))

        run_ui = widgets.HBox([widgets.Label("Run Numbers:", layout=widgets.Layout(width='10%')),
                               widgets.Text(value="",
                                            layout=widgets.Layout(width='40%'),
                                            placeholder='1,4:5,10,20,30:40')])
        self.run_ui = run_ui.children[1]
        display(run_ui)

        import multiprocessing
        nbr_processor = multiprocessing.cpu_count()

        # ****** Number of Processes ********

        display(HTML("<h2>Number of Processes</h2><br>This controls the maximum number of processes that will be run \
            simultaneously locally, or that will be simultaneously submitted to slurm. \
            The value of max_processes should be choosen carefully with the size of the \
            system in mind, to avoid overloading the system.  Since the lower level \
            calculations are all multi-threaded, this should be substantially lower than \
            the total number of cores available (" + str(nbr_processor) + " on this computer). \
            All runs will be processed eventually.  If there are more runs than then \
            max_processes, as some processes finish, new ones will be started, until \
            all runs have been processed."))

        process_ui = widgets.HBox([widgets.Label("Nbr Processes:", layout=widgets.Layout(width='10%')),
                                   widgets.IntSlider(value=nbr_processor - 1,
                                                     min=1,
                                                     max=nbr_processor,
                                                     layout=widgets.Layout(width='20%'))])
        self.process_ui = process_ui.children[1]
        display(process_ui)


    def advanced_options(self):

        display(HTML("<br><br>"))
        pass_layout_ui = widgets.HBox([widgets.Label("Advanced Options Password: ",
                                                     layout=widgets.Layout(width='25%')),
                                       widgets.Text(value="",
                                                    placeholder='password',
                                                    layout=widgets.Layout(width='10%'))])

        MASTER_PASSWORD = 'topaz'
        self.password_found = False

        password = []
        str_password = ''

        self.select_advanced_data_folder_ui = None
        self.advanced_ui = None

        def on_pass_changed(change):

            # global password_found
            # global reduce_ui
            # global reduce_label_ui

            new_len_pass = len(change['new'])
            old_len_pass = len(password)
            if new_len_pass > old_len_pass:
                # added a character
                last_character = change['new'][-1]
                if last_character == '*':
                    return
                password.append(last_character)
            elif new_len_pass < old_len_pass:
                if password != []:
                    password.pop()

            new_string = '*' * new_len_pass
            pass_ui.value = new_string

            # recompose passowrd
            str_password = ''.join(password)

            label_ui = None
            def select_advanced_file(selection):
                label_ui.value = selection
                self.reduce_one_run_script = selection

            if str_password == MASTER_PASSWORD:

                if self.password_found == False:  # to only display widgets once

                    self.select_advanced_data_folder_ui = widgets.HBox([widgets.Label("Reduce One Run Script:",
                                                                              layout=widgets.Layout(width='25%')),
                                                                widgets.Label(self.reduce_one_run_script,
                                                                              layout=widgets.Layout(width='70%'))])
                    label_ui = self.select_advanced_data_folder_ui.children[1]
                    display(self.select_advanced_data_folder_ui)

                    self.advanced_ui = MyFileSelectorPanel(instruction='Select Reduce Python Script ',
                                                         start_dir=os.path.join(self.working_dir,'shared/'),
                                                         next=select_advanced_file)

                    self.advanced_ui.show()
                    self.password_found = True

                else:
                    self.password_found = False

            else:
                if self.select_advanced_data_folder_ui:
                    self.select_advanced_data_folder_ui.close()
                if self.advanced_ui:
                    self.advanced_ui.remove()

        pass_ui = pass_layout_ui.children[1]
        pass_ui.observe(on_pass_changed, names='value')

        display(pass_layout_ui)

    def create_config(self):

        config = self.config

        # calibration file
        config['calibration_file_1'] = os.path.abspath(self.calibration_file_ui.value)

        # goniometer z offset correction
        config['z_offset'] = self.zoffset_ui.value
        config['x_offset'] = self.xoffset_ui.value

        # input data folder
        _data_directory = self.input_data_folder_ui.value
        if not _data_directory == 'N/A':
            _data_directory = os.path.abspath(self.input_data_folder_ui.value)
        config['data_directory'] = _data_directory

        # output folder
        _output_folder = self.output_data_folder_ui.value
        if not _output_folder == 'N/A':
            _output_folder = os.path.abspath(_output_folder)
        config['output_directory'] = _output_folder

        # monitor counts
        config['use_monitor_counts'] = self.monitor_counts_flag_ui.value

        # tof and monitor
        [min_tof, max_tof] = self.tof_ui.value
        config['min_tof'] = min_tof
        config['max_tof'] = max_tof

        config['monitor_index'] = self.monitor_index_ui.value

        [min_monitor_tof, max_monitor_tof] = self.monitor_tof_ui.value
        config['min_monitor_tof'] = min_monitor_tof
        config['max_monitor_tof'] = max_monitor_tof

        # UB
        config['read_UB'] = self.ub_flag_ui.value
        ub_filename = self.ub_file_selected_ui.children[1].value
        if not ub_filename == 'N/A':
            ub_filename = os.path.abspath(ub_filename)
        config['UB_filename'] = ub_filename

        # cell
        config['cell_type'] = self.cell_type_ui.value
        config['centering'] = self.centering_ui.value

        # number of peaks
        config['num_peaks_to_find'] = self.number_peak_ui.value

        # min_d, max_d and tolerance
        [min_d, max_d] = self.d_ui.value
        config['min_d'] = min_d
        config['max_d'] = max_d
        config['tolerance'] = self.tolerance_ui.value

        # predicted peak
        config['integrate_predicted_peaks'] = self.pred_flag_ui.value
        [min_pred_wl, max_pred_wl] = self.pred_ui.value
        config['min_pred_wl'] = min_pred_wl
        config['max_pred_wl'] = max_pred_wl
        [min_pred_dspacing, max_pred_dspacing] = self.pred_dspacing_ui.value
        config['min_pred_dspacing'] = min_pred_dspacing
        config['max_pred_dspacing'] = max_pred_dspacing

        # integration method
        inte_method = self.inte_ui.value
        use_ikeda_carpenter = False
        if inte_method == 'Ellipse':
            config['use_ellipse_integration'] = True
        elif inte_method == 'Sphere':
            config['use_sphere_integration'] = True
        elif inte_method == 'Cylindrical':
            config['use_cylindrical_integration'] = True
        elif inte_method == 'Fit Peaks':
            use_ikeda_carpenter = True
            config['use_fit_peaks_integration'] = True

        config['peak_radius'] = self.peak_ui.value
        [bkg_inner_radius, bkg_outer_radius] = self.bkg_ui.value
        config['bkg_inner_radius'] = bkg_inner_radius
        config['bkg_outer_radius'] = bkg_outer_radius

        config['integrate_if_edge_peak'] = self.inte_flag_ui.value

        config['ellipse_region_radius'] = self.ellipse_region_radius_ui.value
        config['ellipse_size_specified'] = self.ellipse_size_ui_checkbox.value
        config['use_ikeda_carpenter'] = use_ikeda_carpenter

        # bad edge pixels
        config['n_bad_edge_pixels'] = self.bad_pixels_ui.value

        # cylinder radius and length
        config['cylinder_radius'] = self.cylinder_radius_ui.value
        config['cylinder_length'] = self.cylinder_length_ui.value

        # exp name
        config['exp_name'] = self.exp_name_ui.value

        # run number to reduce
        config['run_nums'] = self.run_ui.value.replace(" ", "")

        # max processes
        config['max_processes'] = self.process_ui.value

        # # for debugging
        # for _key in config:
        #     print("{} -> {}".format(_key, config[_key]))

        # checking that we have the minimum info to create config
        config_status_dict = self.check_config_can_be_created(config)

        if config_status_dict['status']:

            config_text = ""
            for _key in config:
                config_text += "{} {}\n".format(_key, config[_key])

            output_folder = config['output_directory']

            # make sure folder exist
            if not os.path.exists(output_folder):
                display(HTML('<h2><span style="color:red">Folder does not exist! Please create folder first</span></h2>'))
                display(HTML("<h2>Name of folder: </h2>" + output_folder))

            # check we have write permission to this file
            config_file_name = self.config_file_ui.value + '.cfg'

            full_config = os.path.abspath(os.path.join(output_folder, config_file_name))
            try:
                make_ascii_file_from_string(text=config_text, filename=full_config)
                display(HTML("<h2>Config file created: </h2>" + full_config))
            except OSError:
                display(HTML('<h2><span style="color:red">You do not have write permission to this file!</span></h2>'))
                display(HTML("<h2>Name of folder: </h2>" + output_folder))

        else:

            list_missing_parameters = config_status_dict['missing_parameters']
            list_tags = config_status_dict['list_tags']

            tags_para = zip(list_tags, list_missing_parameters)

            display(HTML('<h2><span style="color:red">Missing Parameters to Create Config File!</span></h2>'))
#            display(HTML('<a href="#input_data_folder">input data folder</a>'))
            for _tags, _missing_item in tags_para:
                display(HTML('-> <a href="#' + _tags + '">' + _missing_item + '</a>'))

    def check_config_can_be_created(self, config):

        list_missing_parameters = []
        list_tags = []
        _status = True

        if config['calibration_file_1'] == 'N/A':
            _status = False
            list_missing_parameters.append('Calibration File 1 Name')
            list_tags.append('calibration_file')

        if config['data_directory'] == 'N/A':
            _status = False
            list_missing_parameters.append('Input Data Folder Name')
            list_tags.append('input_directory')

        if config['output_directory'] == 'N/A':
            _status = False
            list_missing_parameters.append('Output Folder Name')
            list_tags.append('output_directory')

        if config['read_UB']:
            if config['UB_filename'] == 'N/A':
                _status = False
                list_missing_parameters.append('UB File Name')
                list_tags.append('ub_filename')

        if config['run_nums'] == '':
            _status = False
            list_missing_parameters.append('Run Numbers')
            list_tags.append('run_nums')

        config_status_dict = {'status': _status,
                              'missing_parameters': list_missing_parameters,
                              'list_tags': list_tags}

        return config_status_dict

