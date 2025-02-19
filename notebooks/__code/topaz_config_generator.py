import glob
from ipywidgets import widgets
import os
import re
import shutil
from collections import defaultdict
from IPython.core.display import HTML
from IPython.display import display
import pandas as pd
import subprocess

from __code.file_handler import make_ascii_file_from_string
from __code.file_handler import read_ascii
from __code.ipywe.myfileselector import MyFileSelectorPanel
from __code.utilities import ListRunsParser
from __code.topaz_config import topaz_python_script, topaz_reduction_path


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
                                                  start_dir=self.working_dir,
                                                  filters={'config': ['*.config']},
                                                  default_filter='config',
                                                  stay_alive=True)
        self.config_file_ui.show()

    def load_config(self, config_file_name):
        self.config_selected_label.value = config_file_name
        #try:
        #pd_config = pd.read_csv(config_file_name, sep=' ', comment='#')

        full_config = read_ascii(config_file_name)
        config_array = full_config.split('\n')

        config_dict = dict()
        for _line in config_array:
            if (not (_line.startswith('#'))) and (not (_line == '')):
                _new_line = re.sub('\s+', ',', _line)
                my_split = _new_line.split(',')
                _key = my_split[0]
                _value = my_split[1]
                config_dict[_key] = _value

        [config_dict['config_name'], _] = os.path.splitext(os.path.basename(config_file_name))
        self.config_dict = config_dict

        # except:
        #     display(HTML("Error loading config file {}!".format(config_file_name)))
        #     return

        display(HTML("Configuration file has been loaded with success!"))

        # list_para_name = pd_config['instrument_name']
        # list_para_value = pd_config['TOPAZ']

        # config_dict = dict(zip(list_para_name, list_para_value))
        # adding config_name tag that contains the name of the loaded config name



class ConfigParser(object):


    def __init__(self, config_file=''):
        if config_file:
            self.parse_config(config_file = config_file)

    def parse_config(self, config_file=''):
        pass


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
              'reduce_one_run_script': '/SNS/TOPAZ/shared/calibrations/Reduction/ReduceSCD_OneRun_xz_offset.py',
              'run_nums': '',
              'slurm_queue_name': 'None',
              'max_processes': 8,
              'config_name': 'tmp.config',
              }

    def __init__(self, config_dict={}):
        self.config_dict = config_dict

    def get_parameter_value(self, parameter):

        para_type = type(self.config[parameter])
        if self.config_dict == {}:
            return self.config[parameter]

        if not (parameter in self.config_dict.keys()):
            return self.config[parameter]

        if self.config_dict[parameter]:
            config_para = self.config_dict[parameter]
            if isinstance(self.config[parameter], bool):
                if self.config_dict[parameter] in ["True", "true"]:
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
              'reduce_one_run_script': '/SNS/TOPAZ/shared/calibrations/Reduction/ReduceSCD_OneRun_xz_offset.py',
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
                 'Cubic',
                 'None']

    centering_mode = {'P': cell_type[:-1],
                      'I': ['Tetragonal', 'Monoclinic', 'Cubic'],
                      'A': ['Monoclinic', 'Orthorhombic'],
                      'B': ['Monoclinic', 'Orthorhombic'],
                      'C': ['Monoclinic', 'Orthorhombic'],
                      'F': ['Orthorhombic', 'Cubic'],
                      'Robv': ['Rhombohedral'],
                      'Rrev': ['Rhombohedral'],
                      'None': ['None']
                      }

    cell_type_dict = {}
    o_config_dict = None
    display_config_to_super_user = False

    def __init__(self, working_dir='', config_dict_loaded={}):
        self.working_dir = working_dir
        self.config_dict_loaded = config_dict_loaded

        self.o_config_dict = ConfigDict(config_dict=config_dict_loaded)

        self.init_css()
        self.__create_cell_type_centering_dict()
        self.run_all()

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

    def run_all(self):
        self.define_config_file_name()
        self.select_input_data_folder()
        self.select_output_folder()
        self.parameters_1()
        self.parameters_2()
        self.advanced_options()

    def define_config_file_name(self):

        _default_config = self.o_config_dict.get_parameter_value('config_name')
        [_name_config, _] = os.path.splitext(_default_config)

        display(HTML("<h2>Define Config File Name</h2>"))
        config_file_ui = widgets.HBox([widgets.Label("Config File Name:",
                                                     layout=widgets.Layout(width='20%')),
                                       widgets.Text(_name_config,
                                                    layout=widgets.Layout(width='75%')),
                                       widgets.Label(".config",
                                                     layout=widgets.Layout(width='5%'))])
        self.config_file_ui = config_file_ui.children[1]
        display(config_file_ui)



    def select_input_data_folder(self):

        def update_list_of_runs(list_of_runs):
            self.full_list_of_runs_ui.options = list_of_runs
            if list_of_runs == []:
                self.run_numbers_error_ui.value = ">> Format Error! <<"
                self.full_run_numbers_layout.layout.visibility = 'hidden'
            else:
                self.run_numbers_error_ui.value = ""
                self.full_run_numbers_layout.layout.visibility = 'visible'

        # ****** Select Input Data Folder ********

        display(HTML("<h2 id='input_directory'>Select Input Data Folder</h2>"))

        _input_data_folder = self.o_config_dict.get_parameter_value('data_directory')

        select_input_data_folder_ui = None
        def _select_input_data_folder(selection):
            select_input_data_folder_ui.children[1].value = selection

            # update the list of runs display at the bottom of the page if user select new input data folder
            _path_to_look_for = os.path.abspath(os.path.join(self.input_data_folder_ui.value, 'TOPAZ_*_event.nxs'))
            list_of_event_nxs = glob.glob(_path_to_look_for)

            list_of_runs = []
            if list_of_event_nxs:
                re_string = r"^TOPAZ_(?P<run>\d+)_event.nxs$"
                for _nexus in list_of_event_nxs:
                    _short_nexus = os.path.basename(_nexus)
                    m = re.match(re_string, _short_nexus)
                    if m:
                        _run = m.group('run')
                        list_of_runs.append(_run)

            list_of_runs.sort()
            update_list_of_runs(list_of_runs)
            self.list_of_runs = list_of_runs

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
            if not os.path.exists(start_dir):
                start_dir = self.working_dir
                if not os.path.exists(start_dir):
                    start_dir = '/'

        input_folder_ui = MyFileSelectorPanel(instruction='',
                                              start_dir=start_dir,
                                              next=_select_input_data_folder,
                                              type='directory',
                                              stay_alive=True)
        input_folder_ui.show()
        display(widgets.Label(""))


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
            if not os.path.exists(start_dir):
                start_dir = self.working_dir
                if not os.path.exists(start_dir):
                    start_dir = '/'

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
                                               newdir_toolbar_button=True,
                                               stay_alive=True)
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

        _min_tof = self.o_config_dict.get_parameter_value('min_tof')
        _max_tof = self.o_config_dict.get_parameter_value('max_tof')
        tof_ui = widgets.HBox([widgets.Label("TOF Range",
                                             layout=widgets.Layout(width=self.left_column_width)),
                               widgets.IntRangeSlider(value=[_min_tof, _max_tof],
                                                      min=500,
                                                      max=16600,
                                                      step=1,
                                                      continuous_update=False,
                                                      readout_format='d',
                                                      layout=widgets.Layout(width='50%')),
                               widgets.Label("\u00B5s",
                                             layout=widgets.Layout(width='20%'))])
        self.tof_ui = tof_ui.children[1]

        _monitor_index = self.o_config_dict.get_parameter_value('monitor_index')
        monitor_index_ui = widgets.HBox([widgets.Label("Monitor Index",
                                                       layout=widgets.Layout(width=self.left_column_width)),
                                         widgets.Dropdown(options=['0', '1'],
                                                          value=str(_monitor_index),
                                                          layout=widgets.Layout(width='10%'))])
        self.monitor_index_ui = monitor_index_ui.children[1]

        _min_monitor_tof = self.o_config_dict.get_parameter_value('min_monitor_tof')
        _max_monitor_tof = self.o_config_dict.get_parameter_value('max_monitor_tof')
        monitor_ui = widgets.HBox([widgets.Label("Monitor TOF Range",
                                                 layout=widgets.Layout(width=self.left_column_width)),
                                   widgets.IntRangeSlider(value=[_min_monitor_tof, _max_monitor_tof],
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

        _ub_flag = self.o_config_dict.get_parameter_value('read_UB')
        ub_flag_ui = widgets.Checkbox(value=_ub_flag,
                                      description='Read UB')

        _ub_file = self.o_config_dict.get_parameter_value('UB_filename')
        if _ub_file == '':
            _ub_file = 'N/A'
        ub_file_selected_ui = widgets.HBox([widgets.Label("UB File Selected:",
                                                          layout=widgets.Layout(width='20%')),
                                            widgets.Label(_ub_file,
                                                          layout=widgets.Layout(width='80%'))])
        ub_file_selected_ui.children[0].add_class("mylabel_key")
        self.ub_file_selected_ui = ub_file_selected_ui

        def ub_flag_changed(value):
            display_file_selection_flag = value['new']
            if display_file_selection_flag:
                self.ub_ui.enable()
            else:
                self.ub_ui.disable()
            # self.ub_ui.activate_status(not display_file_selection_flag)
            if display_file_selection_flag:
                ub_file_selected_ui.layout.visibility = 'visible'
            else:
                ub_file_selected_ui.layout.visibility = 'hidden'

        self.ub_flag_ui = ub_flag_ui
        ub_flag_ui.observe(ub_flag_changed, names='value')
        display(ub_flag_ui)

        def select_ub_file(selection):
            ub_file_selected_ui.children[1].value = selection

        _ub_file = self.o_config_dict.get_parameter_value('UB_filename')
        if _ub_file == '':
            _ub_path = os.path.join(self.working_dir, 'shared')
        else:
            _ub_path = os.path.dirname(_ub_file)
        display(ub_file_selected_ui)
        self.ub_ui = MyFileSelectorPanel(instruction='Select UB File (*.mat)',
                                         start_dir=_ub_path,
                                         next=select_ub_file,
                                         stay_alive=True,
                                         filters={'UB files': ['*.mat']})

        # init display
        self.ub_ui.show()
        ub_flag_changed({'new': self.ub_flag_ui.value})

    def parameters_2(self):

        def cell_type_changed(value):
            ## clear first
            # centering_ui.children[1].options = []
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

        _cell_type = self.o_config_dict.get_parameter_value('cell_type')
        cell_type_ui = widgets.HBox([widgets.Label("Cell Type:",
                                                   layout=widgets.Layout(width=self.left_column_width)),
                                     widgets.Dropdown(options=self.cell_type,
                                                      value=_cell_type,
                                                      layout=widgets.Layout(width='20%'))])
        cell_type_ui.children[1].observe(cell_type_changed, names='value')
        self.cell_type_ui = cell_type_ui.children[1]

        _centering = self.o_config_dict.get_parameter_value('centering')

        centering_ui = widgets.HBox([widgets.Label("Centering:",
                                                   layout=widgets.Layout(width=self.left_column_width)),
                                     widgets.Dropdown(options=self.cell_type_dict[_cell_type],
                                                      value=_centering,
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

        _number_peaks = self.o_config_dict.get_parameter_value('num_peaks_to_find')
        peak_ui = widgets.HBox([widgets.Label("Number of Peaks:",
                                              layout=widgets.Layout(width=self.left_column_width)),
                                widgets.IntSlider(value=_number_peaks,
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

        _min_d = self.o_config_dict.get_parameter_value('min_d')
        _max_d = self.o_config_dict.get_parameter_value('max_d')
        d_ui = widgets.HBox([widgets.Label("d",
                                           layout=widgets.Layout(width='1%')),
                             widgets.IntRangeSlider(value=[_min_d, _max_d],
                                                    min=3,
                                                    max=90,
                                                    step=1,
                                                    layout=widgets.Layout(width='30%')),
                             widgets.Label("\u00c5")])
        self.d_ui = d_ui.children[1]

        _tolerance = self.o_config_dict.get_parameter_value('tolerance')
        tolerance_ui = widgets.HBox([widgets.Label("Tolerance",
                                                   layout=widgets.Layout(width='10%')),
                                     widgets.FloatSlider(value=_tolerance,
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

        _pred_flag = self.o_config_dict.get_parameter_value('integrate_predicted_peaks')
        pred_flag_ui = widgets.HBox([widgets.Label("Integrate Predicted Peaks?",
                                                   layout=widgets.Layout(width='20%')),
                                     widgets.Checkbox(value=_pred_flag,
                                                      layout=widgets.Layout(width='20%'))])
        self.pred_flag_ui = pred_flag_ui.children[1]

        _min_pred = self.o_config_dict.get_parameter_value('min_pred_wl')
        _max_pred = self.o_config_dict.get_parameter_value('max_pred_wl')
        pred_ui = widgets.HBox([widgets.Label("Predicted Wavelengths",
                                              layout=widgets.Layout(width='20%')),
                                widgets.FloatRangeSlider(value=[_min_pred, _max_pred],
                                                         min=.25,
                                                         max=3.6,
                                                         layout=widgets.Layout(width='35%')),
                                widgets.Label("\u00c5")])
        self.pred_ui = pred_ui.children[1]

        _min_spacing = self.o_config_dict.get_parameter_value('min_pred_dspacing')
        _max_spacing = self.o_config_dict.get_parameter_value('max_pred_dspacing')
        pred_dspacing_ui = widgets.HBox([widgets.Label("Predicted dspacing",
                                                       layout=widgets.Layout(width='20%')),
                                         widgets.FloatRangeSlider(value=[_min_spacing, _max_spacing],
                                                                  min=.25,
                                                                  max=12,
                                                                  layout=widgets.Layout(width='35%')),
                                         widgets.Label("\u00c5")])
        self.pred_dspacing_ui = pred_dspacing_ui.children[1]

        predicted_ui = widgets.VBox([pred_flag_ui, pred_ui, pred_dspacing_ui])
        display(predicted_ui)

        # ****** Integration Method ********

        display(HTML("<h2>Integration Method</h2><br> Select one of the following integration method."))

        _use_sphere = self.o_config_dict.get_parameter_value('use_sphere_integration')
        _use_ellipse = self.o_config_dict.get_parameter_value('use_ellipse_integration')
        _use_fit_peaks = self.o_config_dict.get_parameter_value('use_fit_peaks_integration')
        # _use_cylindrical = self.o_config_dict.get_parameter_value('use_cylindrical_integration')
        _loaded_value = {}

        # print("_use_sphere: {}".format(_use_sphere))
        # print("_use_ellipse: {}".format(_use_ellipse))
        # print("use_fit_peaks: {}".format(_use_fit_peaks))
        #

        if _use_sphere:
            _loaded_value['new'] = 'Sphere'
            _value = 'Sphere'
        elif _use_ellipse:
            _loaded_value['new'] = 'Ellipse'
            _value = 'Ellipse'
        elif _use_fit_peaks:
            _loaded_value['new'] = 'Fit Peaks'
            _value = 'Fit Peaks'
        else:
            _loaded_value['new'] = 'Cylindrical'
            _value = 'Cylindrical'

        inte_ui = widgets.HBox([widgets.Label("Integration Method",
                                              layout=widgets.Layout(width='15%')),
                                widgets.Dropdown(options=['Sphere', 'Ellipse', 'Cylindrical', 'Fit Peaks'],
                                                 value=_value,
                                                 layout=widgets.Layout(width='20%'))])
        self.inte_ui = inte_ui.children[1]
        display(inte_ui)

        _answer_ikeda = False

        # display(HTML("<h2>Integration Control Parameters</h2>"))

        _peak_radius = self.o_config_dict.get_parameter_value('peak_radius')
        peak_ui = widgets.HBox([widgets.Label("Peak Radius",
                                              layout=widgets.Layout(width='25%')),
                                widgets.FloatSlider(value=_peak_radius,
                                                    min=0.05,
                                                    max=0.25,
                                                    step=0.001,
                                                    readout_format='.3f',
                                                    layout=widgets.Layout(width='30%')),
                                widgets.Label("\u00c5")])
        self.peak_ui = peak_ui.children[1]

        _bkg_inner = self.o_config_dict.get_parameter_value('bkg_inner_radius')
        _bkg_outer = self.o_config_dict.get_parameter_value('bkg_outer_radius')
        bkg_ui = widgets.HBox([widgets.Label("Background Inner and Outer Radius",
                                             layout=widgets.Layout(width='25%')),
                               widgets.FloatRangeSlider(value=[_bkg_inner, _bkg_outer],
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
        _inte_flag = self.o_config_dict.get_parameter_value('integrate_if_edge_peak')
        inte_flag_ui = widgets.HBox([widgets.Label("Integrate if Edge Peak?",
                                                   layout=widgets.Layout(width='15%')),
                                     widgets.Checkbox(value=_inte_flag)])
        self.inte_flag_ui = inte_flag_ui.children[1]
        vertical_layout.append(inte_flag_ui)
        ### end

        _ellipse_radius = self.o_config_dict.get_parameter_value('ellipse_region_radius')
        ellipse_region_ui = widgets.HBox([widgets.Label("Ellipse Region Radius",
                                                        layout=widgets.Layout(width='25%')),
                                          widgets.FloatSlider(value=_ellipse_radius,
                                                              min=bkg_ui.children[1].value[1],
                                                              max=0.30,
                                                              step=0.001,
                                                              readout_format='.3f',
                                                              layout=widgets.Layout(width='30%')),
                                          widgets.Label("\u00c5")])
        self.ellipse_region_radius_ui = ellipse_region_ui.children[1]
        vertical_layout.append(ellipse_region_ui)

        _ellipse_flag = self.o_config_dict.get_parameter_value('ellipse_size_specified')
        ellipse_size_ui = widgets.HBox([widgets.Label("Ellipse Size Specified",
                                                      layout=widgets.Layout(width='25%')),
                                        widgets.Checkbox(value=_ellipse_flag,
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

        _cylinder_radius = self.o_config_dict.get_parameter_value('cylinder_radius')
        self.radius_ui = widgets.HBox([widgets.Label("Cylinder Radius",
                                                layout=widgets.Layout(width='15%')),
                                  widgets.FloatSlider(value=_cylinder_radius,
                                                      min=0.02,
                                                      max=0.1,
                                                      step=0.001,
                                                      readout_format="0.3f",
                                                      layout=widgets.Layout(width='30%')),
                                  widgets.Label("\u00c5")])
        self.cylinder_radius_ui = self.radius_ui.children[1]

        _cylinder_length = self.o_config_dict.get_parameter_value('cylinder_length')
        self.length_ui = widgets.HBox([widgets.Label("Cylinder Length",
                                                layout=widgets.Layout(width='15%')),
                                  widgets.FloatSlider(value=_cylinder_length,
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

        # run method that disable or not widgets
        inte_method_changed(_loaded_value)

        # ****** Bad Edge Pixels ********

        display(HTML("<h2>Bad Edge Pixels</h2>"))

        _bad_pixels = self.o_config_dict.get_parameter_value('n_bad_edge_pixels')
        bad_pixels_ui = widgets.HBox([widgets.Label("Nbr bad edge pixels:",
                                                    layout=widgets.Layout(width='15%')),
                                      widgets.IntSlider(value=_bad_pixels,
                                                        min=0,
                                                        max=50,
                                                        layout=widgets.Layout(width='30%'))])

        self.bad_pixels_ui = bad_pixels_ui.children[1]
        display(bad_pixels_ui)

        # ****** Experiment Name ********

        display(HTML("<h2 id='exp_name'>Experiment Name</h2>"))

        _exp = self.o_config_dict.get_parameter_value('exp_name')
        exp_name_ui = widgets.Text(_exp,
                                   layout=widgets.Layout(width="50%"))
        self.exp_name_ui = exp_name_ui
        display(exp_name_ui)

        # ****** Run Numbers to Reduce ********

        display(HTML("<h2 id='run_nums'>Run Numbers to Reduce</h2><br>Specify the run numbers that should be reduced."))

        self.full_list_of_runs_selected = []
        self.list_of_runs_already_selected = []

        o_parser = ListRunsParser(current_runs="")

        def run_numbers_text_changed(value):
            new_text = value['new']
            _error_label_visibility = 'hidden'
            list_current_runs = []
            try:
                o_parser = ListRunsParser(current_runs=new_text)
                list_current_runs = o_parser.list_current_runs
            except ValueError:
                _error_label_visibility = 'visible'

            self.run_numbers_error_ui.value = ">> Format Error! <<"
            self.run_numbers_error_ui.layout.visibility = _error_label_visibility

            # check runs that do not exist in full_list_of_runs
            list_runs_do_not_exist = []
            list_runs_do_exist = []
            for _run in list_current_runs:
                if _run in self.list_of_runs:
                    list_runs_do_exist.append(_run)
                else:
                    list_runs_do_not_exist.append(_run)

            if list_runs_do_not_exist:
                self.last_row_ui.layout.visibility = 'visible'
                self.last_row_ui.children[1].value = ",".join(list_runs_do_not_exist)
            else:
                self.last_row_ui.layout.visibility = 'hidden'

            # only display in the middle widget, the runs that do exist
            list_runs_do_exist.sort()
            self.selected_runs_ui.options = list_runs_do_exist

        def full_list_of_runs_changed(value):
            self.full_list_of_runs_selected = value['new']

        def selected_runs_ui_changed(value):
            pass

        def add_button_clicked(value):
            for _run in self.full_list_of_runs_selected:
                self.list_of_runs_already_selected.append(_run)

            self.list_of_runs_already_selected = list(set(self.list_of_runs_already_selected))
            self.list_of_runs_already_selected.sort()

            self.selected_runs_ui.options = self.list_of_runs_already_selected

            o_parser = ListRunsParser()
            new_str_runs = o_parser.new_runs(self.list_of_runs_already_selected)

            self.run_numbers_text_ui.value = new_str_runs

        def remove_button_clicked(value):
            list_of_runs_to_remove = set(self.selected_runs_ui.value)
            list_of_runs_already_selected = set(self.list_of_runs_already_selected)

            new_list_of_runs_already_selected = list_of_runs_already_selected - list_of_runs_to_remove
            new_list_of_runs_already_selected = list(new_list_of_runs_already_selected)
            new_list_of_runs_already_selected.sort()
            new_list_of_runs_already_selected = set(new_list_of_runs_already_selected)
            self.selected_runs_ui.options = new_list_of_runs_already_selected
            list_of_runs_already_selected = list(new_list_of_runs_already_selected)

            str_list_of_runs_already_selected = ",".join(list_of_runs_already_selected)

            if len(list_of_runs_already_selected) > 1:
                o_parser = ListRunsParser(current_runs=str_list_of_runs_already_selected)
                new_str_runs = o_parser.new_runs()
            elif len(list_of_runs_already_selected) == 1:
                new_str_runs = str(list_of_runs_already_selected[0])
            else:
                new_str_runs = ''

            self.run_numbers_text_ui.value = new_str_runs
            self.list_of_runs_already_selected = list_of_runs_already_selected

        ## initialize
        _path_to_look_for = os.path.abspath(os.path.join(self.input_data_folder_ui.value, 'TOPAZ_*_event.nxs'))
        list_of_event_nxs = glob.glob(_path_to_look_for)

        list_of_runs = []
        if list_of_event_nxs:
            re_string = r"^TOPAZ_(?P<run>\d+)_event.nxs$"
            for _nexus in list_of_event_nxs:
                _short_nexus = os.path.basename(_nexus)
                m = re.match(re_string, _short_nexus)
                if m:
                    _run = m.group('run')
                    list_of_runs.append(_run)
        self.list_of_runs = list_of_runs

        # listen to selection to autopopulate the list of runs when user click runs
        if list_of_runs == []:
            _visibility = 'hidden'
            _message = '>> No event NeXus found in the input folder! <<'
        else:
            _visibility = 'visible'
            _message = ''

        self._run_nums = self.o_config_dict.get_parameter_value('run_nums')
        o_parser = ListRunsParser(current_runs=self._run_nums)
        self.list_runs = o_parser.list_current_runs

        ## build UI

        first_row_ui = widgets.HBox([widgets.Label("Run numbers:",
                                                   layout=widgets.Layout(width='10%')),
                                     widgets.Text(self._run_nums,
                                                  placeholder='',
                                                  layout=widgets.Layout(width='40%')),
                                     widgets.Label(_message,
                                                   layout=widgets.Layout(visibility='visible',
                                                                         color='red'))])
        first_row_ui.children[1].observe(run_numbers_text_changed, 'value')
        self.run_numbers_text_ui = first_row_ui.children[1]
        self.run_numbers_error_ui = first_row_ui.children[2]

        col_1_ui = widgets.VBox([widgets.Label("Full list of runs"),
                                 widgets.SelectMultiple(options=self.list_of_runs,
                                                        layout=widgets.Layout(height='150px',
                                                                              width='100px'))],
                                layout=widgets.Layout(width='120px'))
        col_1_ui.children[1].observe(full_list_of_runs_changed, 'value')

        col_2_ui = widgets.VBox([widgets.Button(description="Add ->",
                                                layout=widgets.Layout(border='1px solid blue',
                                                                      width='120px'))],
                                layout=widgets.Layout(width='160px',
                                                      align_self='center'))
        col_2_ui.children[0].on_click(add_button_clicked)

        col_3_ui = widgets.VBox([widgets.Label("Selected runs"),
                                 widgets.SelectMultiple(options=self.list_runs,
                                                        layout=widgets.Layout(height='150px',
                                                                              width='100px'))],
                                layout=widgets.Layout(width='120px'))
        col_3_ui.children[1].observe(selected_runs_ui_changed, 'value')
        self.full_list_of_runs_ui = col_1_ui.children[1]
        self.selected_runs_ui = col_3_ui.children[1]

        col_4_ui = widgets.Button(description="Remove",
                                  layout=widgets.Layout(width='120px',
                                                        border='1px solid red',
                                                        align_self='flex-end'))
        col_4_ui.on_click(remove_button_clicked)

        second_row_ui = widgets.HBox([col_1_ui, col_2_ui, col_3_ui, col_4_ui],
                                     layout=widgets.Layout(border='1px solid lightgrey',
                                                           padding='3px',
                                                           margin='5px 5px 5px 5px',
                                                           visibility=_visibility,
                                                           width='50%'))

        self.last_row_ui = widgets.HBox([widgets.Label("Invalid run(s):",
                                                  layout=widgets.Layout(width='8%')),
                                    widgets.Label("",
                                                  layout=widgets.Layout(width='80%'))],
                                   layout=widgets.Layout(visibility='hidden'))

        layout_ui = widgets.VBox([first_row_ui, second_row_ui, self.last_row_ui])
        self.full_run_numbers_layout = second_row_ui

        display(layout_ui)

        # ****** Number of Processes ********

        import multiprocessing
        nbr_processor = multiprocessing.cpu_count()
        if nbr_processor > 6:
            nbr_processor = 6

        display(HTML("<h2>Number of Processes</h2><br>This controls the maximum number of processes that will be run \
            simultaneously locally, or that will be simultaneously submitted to slurm. \
            The value of max_processes should be choosen carefully with the size of the \
            system in mind, to avoid overloading the system.  Since the lower level \
            calculations are all multi-threaded, this should be substantially lower than \
            the total number of cores available (" + str(nbr_processor) + " on this computer). \
            All runs will be processed eventually.  If there are more runs than then \
            max_processes, as some processes finish, new ones will be started, until \
            all runs have been processed."))

        _max_processes = self.o_config_dict.get_parameter_value('max_processes')

        # make sure we do not use more processes that max allowed
        if _max_processes > nbr_processor:
            _max_processes = nbr_processor
        process_ui = widgets.HBox([widgets.Label("Nbr Processes:", layout=widgets.Layout(width='10%')),
                                   widgets.IntSlider(value=_max_processes,
                                                     min=1,
                                                     max=nbr_processor,
                                                     layout=widgets.Layout(width='20%'))])
        self.process_ui = process_ui.children[1]
        display(process_ui)

    def advanced_options(self):

        display(HTML("<br><br>"))
        display(HTML("<h2>Advanced Options</h2>"))

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

        self.reduce_one_run_script = self.o_config_dict.get_parameter_value('reduce_one_run_script')
        def on_pass_changed(change):

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

                self.display_config_to_super_user = True
                if self.password_found == False:  # to only display widgets once

                    self.select_advanced_data_folder_ui = widgets.HBox([widgets.Label("Reduce One Run Script:",
                                                                              layout=widgets.Layout(width='25%')),
                                                                widgets.Label(self.reduce_one_run_script,
                                                                              layout=widgets.Layout(width='70%'))])
                    label_ui = self.select_advanced_data_folder_ui.children[1]
                    display(self.select_advanced_data_folder_ui)

                    advanced_folder = topaz_reduction_path
                    if not os.path.exists(advanced_folder):
                        advanced_folder = self.working_dir


                    self.advanced_ui = MyFileSelectorPanel(instruction='Select Reduce Python Script ',
                                                           start_dir=advanced_folder,
                                                           next=select_advanced_file,
                                                           stay_alive=True)

                    self.advanced_ui.show()
                    self.password_found = True

                else:
                    self.password_found = False

            else:

                self.display_config_to_super_user = False

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
        self.output_folder = _output_folder

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
        config['run_nums'] = self.run_numbers_text_ui.value.replace(" ", "")

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
            config_file_name = self.config_file_ui.value + '.config'

            full_config = os.path.abspath(os.path.join(output_folder, config_file_name))
            self.full_config = full_config
            try:
                make_ascii_file_from_string(text=config_text, filename=full_config)
                display(HTML("<h2>Config file created: </h2>" + full_config))

                # display content of config file if user is super user
                if self.display_config_to_super_user:
                    list_hori_layout = []
                    _key_width = "20%"
                    _value_width = "80%"
                    for _key in config:

                        _hori_layout = widgets.HBox([widgets.Label("{}:".format(_key),
                                                                   layout=widgets.Layout(width=_key_width)),
                                                     widgets.Label("{}".format(config[_key]),
                                                                   layout=widgets.Layout(width=_value_width))])
                        list_hori_layout.append(_hori_layout)

                    verti_layout = widgets.VBox(list_hori_layout,
                                                layout=widgets.Layout(border="1px solid grey"))
                    display(verti_layout)


            except OSError:
                display(HTML('<h2><span style="color:red">You do not have write permission to this file!</span></h2>'))
                display(HTML("<h2>Name of folder: </h2>" + output_folder))
                display(HTML('-> <a href="#output_directory"> Jump to output folder selection</a>'))

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

        if config['exp_name'] == '':
            _status = False
            list_missing_parameters.append("Experiment Name")
            list_tags.append('exp_name')

        if config['run_nums'] == '':
            _status = False
            list_missing_parameters.append('Run Numbers')
            list_tags.append('run_nums')

        config_status_dict = {'status': _status,
                              'missing_parameters': list_missing_parameters,
                              'list_tags': list_tags}

        self.reduction_status = _status
        return config_status_dict

    def run_reduction(self):

        if self.reduction_status:

            _output_folder = self.output_folder

            # # copy all the python files used by the main python script
            # for _file in python_files_to_copy :
            #     shutil.copyfile(_file, _output_folder)
            #
            # # copy the python script to run
            # shutil.copyfile(topaz_python_script, _output_folder)

            # get topaz shell script full path
            #current_dir = os.getcwd()
            #shell_script = os.path.join(current_dir, '__code/TOPAZ_run_reduction.sh')


            # move to output folder
            #os.chdir(_output_folder)

            _script_to_run = "python {} {}".format(topaz_python_script, self.full_config)
            display(HTML("Copy/Paste the following command in a terminal session and hit ENTER " +
                         "<br><br><span style='font-size: 20px; color:green'> " + _script_to_run + "</span>"))

            # p = subprocess.Popen(_script_to_run,
            #                      shell=True,
            #                      stdout=subprocess.PIPE,
            #                      stderr=subprocess.STDOUT)
            #
            # for line in p.stdout.readlines():
            #     print(line)
            #
            # retval = p.wait()

        else:
            display(HTML('<span style="font-size: 20px; color:red">Please check the missing ' + \
                         'information to create the config file (needed to run the reduction)!</span>'))

