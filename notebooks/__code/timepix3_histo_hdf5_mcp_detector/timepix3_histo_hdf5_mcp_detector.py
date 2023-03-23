import logging
import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from ipywidgets import interactive
import ipywidgets as widgets
from IPython.core.display import display, HTML
import json

from __code.advanced_roi_selection_ui.advanced_roi_selection_ui import Interface

from neutronbraggedge.experiment_handler import *
from neutronbraggedge.braggedge import BraggEdge as BraggEdgeLibrary

from __code._utilities.file import get_full_home_file_name
from __code._utilities import LAMBDA, MICRO, ANGSTROMS
from __code._utilities.color import Color
from __code._utilities.time import get_current_time_in_special_file_name_format
from __code.ipywe import fileselector
from __code.timepix3_histo_hdf5_mcp_detector.fit_regions import FitRegions
from __code._utilities.array import find_nearest_index
from __code.timepix3_histo_hdf5_mcp_detector import FittingRegions
from __code.timepix3_histo_hdf5_mcp_detector import DefaultFittingParameters
from __code.timepix3_histo_hdf5_mcp_detector import JSONKeys
from __code.file_folder_browser import FileFolderBrowser

LOG_FILE_NAME = ".timepix3_histo_hdf5_mcp_detector.log"
MAX_TIME_PER_PULSE = 1.667e4


class Timepix3HistoHdf5McpDetector:

    # histogram data
    histo_data = None

    # profile of all ROIs, without and with shifting
    profile = None
    profile_shifted = None

    # list of rois selected
    # {{0: {'x0': 0, 'x1': 10, 'y0': 20, 'y1': 50},
    #  {1: ...},
    # }
    rois_selected = None

    # dict of fitting result
    # {'a0': {'value': None, 'error': None},
    #  'b0': {'value': None, 'error': None},
    #  'ahkl': {'value': None, 'error': None},
    #  'bhkl': {'value': None, 'error': None},
    #  'lambdahkl': {'value': None, 'error': None},
    #  'tau': {'value': None, 'error': None},
    #  'sigma': {'value': None, 'error': None},
    #  FittingRegions.bragg_peak: {'xaxis': None,
    #                              'yaxis': None,
    #                             },
    #  }
    fit_dict = {}

    def __init__(self, working_dir=None):
        self.working_dir = working_dir

        self.log_file_name = get_full_home_file_name(LOG_FILE_NAME)
        logging.basicConfig(filename=self.log_file_name,
                            filemode='w',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)
        logging.info("*** Starting a new session ***")

    def hdf5_or_config_file_input(self):
        self.toggle_button = widgets.ToggleButtons(
            options=['HDF5 MCP', 'Config File'],
            description="",
            button_style='',
            tooltips=['Select HDF5 MCP Histo File', 'Select Config File'],
        )
        display(self.toggle_button)

        validate_button = widgets.Button(description="SELECT",
                                         icon="folder-open",
                                         layout=widgets.Layout(width="310px"))
        display(validate_button)

        validate_button.on_click(self.input_selection_made)

    def input_selection_made(self, _):
        if self.toggle_button.value == "HDF5 MCP":
            self.select_nexus()
        else:
            self.select_config()

    def select_nexus(self):
        self.nexus_ui = fileselector.FileSelectorPanel(instruction='Select Histo HDF5 file ...',
                                                       start_dir=self.working_dir,
                                                       next=self.load_nexus,
                                                       filters={'NeXus': ".h5"},
                                                       multiple=False)
        self.nexus_ui.show()

    def select_config(self):
        self.config_ui = fileselector.FileSelectorPanel(instruction='Select Config file ...',
                                                       start_dir=self.working_dir,
                                                       next=self.load_config,
                                                       filters={'Config': ".json"},
                                                       multiple=False)
        self.config_ui.show()

    def load_config(self, config_file_name):
        with open(config_file_name) as f:
            config = json.load(f)
        self.json_dict = config

        input_nexus_filename = config[JSONKeys.input_nexus_filename]
        self.load_nexus(nexus_file_name=input_nexus_filename)

        dSD_ = config[JSONKeys.dSD_m]
        rois_selected = config[JSONKeys.rois_selected]
        offset_micros = config[JSONKeys.offset_micros]
        time_shift = config[JSONKeys.time_shift]
        element = config[JSONKeys.element]

        left_range = config[JSONKeys.left_range]
        right_range = config[JSONKeys.right_range]
        left_edge = config[JSONKeys.left_edge]
        right_edge = config[JSONKeys.right_edge]

        #FIXME



    def load_nexus(self, nexus_file_name=None):
        logging.info(f"Loading HDF5: {nexus_file_name}")
        self.input_nexus_filename = nexus_file_name

        # updating the working folder
        self.working_dir = os.path.dirname(nexus_file_name)

        with h5py.File(nexus_file_name, 'r') as f:
            self.stack = np.array(f['entry']['histo']['stack'])
            self.time_spectra = np.array(f['entry']['histo']['tof_ns']) / 1000  # to convert to micros

    def preview_integrated_stack(self):
        self.integrated_stack = self.stack.sum(axis=0)
        fig, ax = plt.subplots(figsize=(7, 7),
                               nrows=1, ncols=1)
        image = ax.imshow(self.integrated_stack)
        self.cb = plt.colorbar(image, ax=ax)
        plt.show()

        max_counts = np.max(self.integrated_stack)

        def plot_integrated(vmin, vmax):
            self.cb.remove()
            plt.title("Integrated slices (sum)")
            image = ax.imshow(self.integrated_stack, vmin=vmin, vmax=vmax)
            self.cb = plt.colorbar(image, ax=ax)
            plt.show()

        v = interactive(plot_integrated,
                        vmin=widgets.IntSlider(min=0,
                                               max=max_counts,
                                               value=0),
                        vmax=widgets.IntSlider(min=0,
                                               max=max_counts,
                                               value=max_counts),
                        )
        display(v)

    def select_roi(self):
        # use the integrated image and ROI tool to select
        # ROIs
        o_gui = Interface(array2d=self.integrated_stack,
                          callback=self.returning_from_roi_selection,
                          display_info_message=False,
                          mandatory_regions=True,
                          list_roi={0: {'x0': 467, 'y0': 99, 'x1': 975, 'y1': 429}})
        o_gui.show()
        # QtGui.QGuiApplication.processEvents()

    def returning_from_roi_selection(self, rois_selected):
        logging.info(f"User selected: {rois_selected}")
        self.rois_selected = rois_selected

    def calculate_and_display_profile(self):
        rois_selected = self.rois_selected

        list_matplotlib_colors = Color.list_matplotlib

        # calculate the number of pixels in all ROIs
        # this will be needed to calculate mean counts per image
        # also record rectangle of ROIs for display only
        total_pixels_in_rois = 0
        rect_array = []
        for _roi_index in rois_selected.keys():
            x0 = rois_selected[_roi_index]['x0']
            y0 = rois_selected[_roi_index]['y0']
            x1 = rois_selected[_roi_index]['x1']
            y1 = rois_selected[_roi_index]['y1']

            width = np.abs(x1-x0)
            height = np.abs(y1-y0)
            total_pixels_in_rois += width * height

            _rect = patches.Rectangle((x0, y0),
                                      x1-x0,
                                      y1-y0,
                                      linewidth=1,
                                      edgecolor=list_matplotlib_colors[_roi_index],
                                      facecolor='none')
            rect_array.append(_rect)

        profile = []
        for _index_image, _image in enumerate(self.stack):

            total_counts_for_this_image = 0
            for _roi_index in rois_selected.keys():
                x0 = rois_selected[_roi_index]['x0']
                y0 = rois_selected[_roi_index]['y0']
                x1 = rois_selected[_roi_index]['x1']
                y1 = rois_selected[_roi_index]['y1']

                total_counts_for_this_image += np.nansum(_image[y0:y1+1, x0:x1+1])

            profile.append(total_counts_for_this_image / total_pixels_in_rois)

        self.profile =  profile
        max_counts = np.max(profile)

        fig1, ax1 = plt.subplots(figsize=(8, 8),
                                 nrows=1,
                                 ncols=1)

        preview = ax1.imshow(self.integrated_stack)
        cb = plt.colorbar(preview, ax=ax1)
        plt.show()

        for _patch in rect_array:
            ax1.add_patch(_patch)

        fig2, ax2 = plt.subplots(figsize=(8, 8),
                                 nrows=1,
                                 ncols=1)

        def plot_profile(x_axis, dSD_m, offset_micros, time_shift, element):

            if element == 'Ni':
                _handler = BraggEdgeLibrary(material=[element],
                                            number_of_bragg_edges=6)
            else:  # Ta
                _handler = BraggEdgeLibrary(new_material=[{'name': 'Ta',
                                                           'lattice': 3.3058,
                                                           'crystal_structure': 'BCC'}],
                                            number_of_bragg_edges=6)

            self.bragg_edges = _handler.bragg_edges
            self.hkl = _handler.hkl
            self.handler = _handler

            # applying the shift to the tof axis
            tof_array = self.time_spectra[:-1]
            condition = np.array(tof_array) < time_shift

            if x_axis == 'TOF':
                x_axis_array = tof_array
                xlabel = "TOF offset (" + MICRO + "s)"
            else:
                _exp = Experiment(tof=tof_array * 1e-6,  # to convert to seconds
                                  distance_source_detector_m=dSD_m,
                                  detector_offset_micros=offset_micros)
                lambda_array = _exp.lambda_array[:] * 1e10  # to be in Angstroms
                x_axis_array = lambda_array
                xlabel = LAMBDA + "(" + ANGSTROMS + ")"

            ax2.cla()
            _profile = np.array(profile)
            _profile_shifted = np.hstack((_profile[~condition], _profile[condition]))

            ax2.plot(x_axis_array, _profile_shifted,
                     color=list_matplotlib_colors[0])
            ax2.set_ylabel("Mean counts of ROI")
            ax2.set_xlabel(xlabel)

            if x_axis == 'lambda':

                logging.info(f"for Ni: {self.hkl[element] =}")
                for _index, _x in enumerate(self.bragg_edges[element]):
                    _hkl_array = self.hkl[element][_index]
                    _str_hkl_array = [str(value) for value in _hkl_array]
                    _hkl = ",".join(_str_hkl_array)

                    # to display _x in the right axis
                    ax2.axvline(x=_x, color='r', linestyle='--')

                    ax2.text(_x, (max_counts - max_counts / 7),
                             _hkl,
                             ha="center",
                             rotation=45,
                             size=15,
                             )

        self.v = interactive(plot_profile,
                        x_axis=widgets.RadioButtons(options=['TOF', 'lambda'],
                                                    value='lambda',
                                                    ),
                        dSD_m=widgets.FloatSlider(value=19.855,
                                                  min=15,
                                                  max=25,
                                                  step=0.001,
                                                  continuous_update=False,
                                                  readout_format=".3f"),
                        offset_micros=widgets.IntSlider(value=0,
                                                        min=0,
                                                        max=15000,
                                                        continuous_update=False),
                        time_shift=widgets.IntSlider(value=0,
                                                     min=0,
                                                     max=MAX_TIME_PER_PULSE,
                                                     step=1,
                                                     continuous_update=False),
                        element=widgets.RadioButtons(options=['Ni', 'Ta'],
                                                     value='Ni'),
                        )
        display(self.v)

    def select_peak_to_fit(self):

        display(HTML('<span style="font-size: 20px; color:green">Full range of peak to fit (left_range, right_range)</span>'))
        display(HTML('<span style="font-size: 20px; color:red">Peak threshold (left_peak, right_peak)</span>'))

        lambda_x_axis, profile_shifted = self.prepare_data()
        self.lambda_x_axis = lambda_x_axis
        self.profile_shifted = profile_shifted

        list_matplotlib_colors = Color.list_matplotlib
        fig3, ax3 = plt.subplots(figsize=(8, 8),
                                 nrows=1,
                                 ncols=1)

        def plot_peaks(left_range, right_range, left_edge, right_edge):

            ax3.cla()

            _profile = np.array(self.profile)

            ax3.plot(lambda_x_axis, _profile,
                     color=list_matplotlib_colors[0])
            ax3.set_ylabel("Mean counts of ROI")
            ax3.set_xlabel(LAMBDA + "(" + ANGSTROMS + ")")

            # display range
            ax3.axvline(x=left_range, color='g')
            ax3.axvline(x=right_range, color='g')

            # display range of edge
            ax3.axvline(x=left_edge, color='r')
            ax3.axvline(x=right_edge, color='r')

        self.peak_to_fit = interactive(plot_peaks,
                                       left_range=widgets.FloatSlider(min=np.min(lambda_x_axis),
                                                                      max=np.max(lambda_x_axis),
                                                                      step=0.001,
                                                                      # value=np.min(lambda_x_axis),
                                                                      value=0.8,  # FIXME for debugging only
                                                                      readout_format=".3f"),
                                       right_range=widgets.FloatSlider(min=np.min(lambda_x_axis),
                                                                       max=np.max(lambda_x_axis),
                                                                       step=0.001,
                                                                       # value=np.max(lambda_x_axis),
                                                                       value=1.9,  # FIXME for debugging only
                                                                       readout_format=".3f"),
                                       left_edge=widgets.FloatSlider(min=np.min(lambda_x_axis),
                                                                     max=np.max(lambda_x_axis),
                                                                     step=0.001,
                                                                     value=1.2,  # FIXME for debugging only
                                                                     readout_format=".3f"),
                                       right_edge=widgets.FloatSlider(min=np.min(lambda_x_axis),
                                                                      max=np.max(lambda_x_axis),
                                                                      step=0.001,
                                                                      value=1.4,   # FIXME for debugging only
                                                                      readout_format=".3f"))
        display(self.peak_to_fit)

    def prepare_data(self):
        """
        this is where the y-axis to fit and x_axis (lambda scale) are calculated using the instrument
        settings and the time shift define in the previous cells.
        """

        profile = self.profile

        dSD_m = self.v.children[1].value
        offset_micros = self.v.children[2].value
        time_shift = self.v.children[3].value
        # element = self.v.children[4].value

        tof_array = self.time_spectra[:-1]
        condition = np.array(tof_array) < time_shift

        _exp = Experiment(tof=tof_array * 1e-6,  # to convert to seconds
                          distance_source_detector_m=dSD_m,
                          detector_offset_micros=offset_micros)
        lambda_array = _exp.lambda_array[:] * 1e10  # to be in Angstroms

        profile = np.array(profile)
        profile_shifted = np.hstack((profile[~condition], profile[condition]))

        self.x_axis_to_fit = lambda_array
        self.y_axis_to_fit = profile_shifted

        return lambda_array, profile_shifted

    def setup_fitting_parameters(self):

        display(HTML('<span style="font-size: 20px; color:blue">Init parameters</span>'))

        text_width = '80px'   # px
        display(HTML('<span style="font-size: 15px; color:green">High lambda</span>'))
        self.a0_layout = widgets.HBox([widgets.Label(u"a\u2080"),
                                  widgets.IntText(DefaultFittingParameters.a0,
                                                  layout=widgets.Layout(width=text_width))])
        self.b0_layout = widgets.HBox([widgets.Label(u"b\u2080"),
                                  widgets.IntText(DefaultFittingParameters.b0,
                                                  layout=widgets.Layout(width=text_width))])
        high_layout = widgets.VBox([self.a0_layout,
                                    self.b0_layout])
        display(high_layout)

        display(HTML(''))

        display(HTML('<span style="font-size: 15px; color:green">Low lambda</span>'))
        self.ahkl_layout = widgets.HBox([widgets.Label(u"a\u2095\u2096\u2097"),
                                  widgets.IntText(DefaultFittingParameters.ahkl,
                                                  layout=widgets.Layout(width=text_width))])
        self.bhkl_layout = widgets.HBox([widgets.Label(u"b\u2095\u2096\u2097"),
                                  widgets.IntText(DefaultFittingParameters.bhkl,
                                                  layout=widgets.Layout(width=text_width))])
        low_layout = widgets.VBox([self.ahkl_layout,
                                   self.bhkl_layout])
        display(low_layout)

        display(HTML(''))

        display(HTML('<span style="font-size: 15px; color:green">Bragg peak</span>'))
        self.lambdahkl_layout = widgets.HBox([widgets.Label(u"\u03bb\u2095\u2096\u2097"),
                                  widgets.FloatText(DefaultFittingParameters.lambdahkl,
                                                    layout=widgets.Layout(width=text_width))])
        self.tau_layout = widgets.HBox([widgets.Label(u"\u03C4"),
                                  widgets.FloatText(DefaultFittingParameters.tau,
                                                    layout=widgets.Layout(width=text_width))])
        self.sigma_layout = widgets.HBox([widgets.Label(u"\u03C3"),
                                   widgets.FloatText(DefaultFittingParameters.sigma,
                                                     layout=widgets.Layout(width=text_width))])
        bragg_peak_layout = widgets.VBox([self.lambdahkl_layout,
                                          self.tau_layout,
                                          self.sigma_layout])
        display(bragg_peak_layout)

    def prepare_data_to_fit(self):
        """
        this is where the y-axis to fit and x_axis (lambda scale) are calculated using the instrument
        settings and the time shift define in the previous cells.
        """
        lambda_x_axis = self.lambda_x_axis
        profile_shifted = self.profile_shifted

        # threshold of peak to fit
        left_lambda_range = self.peak_to_fit.children[0].value
        right_lambda_range = self.peak_to_fit.children[1].value
        left_peak = find_nearest_index(lambda_x_axis, left_lambda_range)
        right_peak = find_nearest_index(lambda_x_axis, right_lambda_range)
        self.left_peak_index = left_peak
        self.right_peak_index = right_peak

        # edge of peak to fit
        left_lambda_edge = self.peak_to_fit.children[2].value
        right_lambda_edge = self.peak_to_fit.children[3].value
        left_edge = find_nearest_index(lambda_x_axis, left_lambda_edge)
        right_edge = find_nearest_index(lambda_x_axis, right_lambda_edge)
        self.left_edge_index = left_edge
        self.right_edge_index = right_edge

        logging.info(f"Prepare data to fit:")
        logging.info(f"\tpeak left_range: {left_lambda_range}" + u"\u212b " + f"-> index: {left_peak}")
        logging.info(f"\tpeak right_range: {right_lambda_range}" + u"\u212b " + f"-> index: {right_peak}")
        logging.info(f"\tedge left_range: {left_lambda_edge}" + u"\u212b " + f"-> index: {left_edge}")
        logging.info(f"\tedge right_range: {right_lambda_edge}" + u"\u212b " + f"-> index: {right_edge}")
        logging.info(f"\tlambda_x_axis: {lambda_x_axis}")

        logging.info(f"\tsize of profile: {len(profile_shifted)}")

        # self.x_axis_to_fit = lambda_x_axis[left_range: right_range]
        self.x_axis_to_fit = lambda_x_axis
        self.y_axis_to_fit = profile_shifted

    def fit_peak(self):

        self.prepare_data_to_fit()

        x_axis_to_fit = self.x_axis_to_fit
        y_axis_to_fit = self.y_axis_to_fit

        a0 = self.a0_layout.children[1].value
        b0 = self.b0_layout.children[1].value

        ahkl = self.ahkl_layout.children[1].value
        bhkl = self.bhkl_layout.children[1].value

        lambdahkl = self.lambdahkl_layout.children[1].value
        tau = self.tau_layout.children[1].value
        sigma = self.sigma_layout.children[1].value

        # full_x_axis = self.x_axis_to_fit
        # full_y_axis = self.y_axis_to_fit

        fig4, ax4 = plt.subplots(figsize=(8, 8),
                                 nrows=1,
                                 ncols=1)

        # display full spectrum
        list_matplotlib_colors = Color.list_matplotlib
        ax4.plot(x_axis_to_fit, -np.log(y_axis_to_fit), '*',
                 color=list_matplotlib_colors[0])

        max_counts = 0
        dict_of_fit_dict = {}

        o_fit_regions = FitRegions(a0=a0,
                                   b0=b0,
                                   ahkl=ahkl,
                                   bhkl=bhkl,
                                   lambdahkl=lambdahkl,
                                   sigma=sigma,
                                   tau=tau,
                                   x_axis_to_fit=x_axis_to_fit,
                                   y_axis_to_fit=y_axis_to_fit,
                                   left_peak_index=self.left_peak_index,
                                   right_peak_index=self.right_peak_index,
                                   left_edge_index=self.left_edge_index,
                                   right_edge_index=self.right_edge_index)
        o_fit_regions.all_regions()

        self.fit_dict = o_fit_regions.fit_dict

        # display fitting
        # high lambda
        x_axis_fitted_high_lambda = o_fit_regions.fit_dict[FittingRegions.high_lambda]['xaxis']
        y_axis_fitted_high_lambda = o_fit_regions.fit_dict[FittingRegions.high_lambda]['yaxis']
        ax4.plot(x_axis_fitted_high_lambda, y_axis_fitted_high_lambda, 'r-')

        # low lambda
        x_axis_fitted_low_lambda = o_fit_regions.fit_dict[FittingRegions.low_lambda]['xaxis']
        y_axis_fitted_low_lambda = o_fit_regions.fit_dict[FittingRegions.low_lambda]['yaxis']
        ax4.plot(x_axis_fitted_low_lambda, y_axis_fitted_low_lambda, 'y-')

        # bragg peak
        x_axis_fitted = o_fit_regions.fit_dict[FittingRegions.bragg_peak]['xaxis']
        y_axis_fitted = o_fit_regions.fit_dict[FittingRegions.bragg_peak]['yaxis']
        ax4.plot(x_axis_fitted, y_axis_fitted, 'w-')

        ax4.set_ylabel("Cross Section (a.u.)")

        lambdahkl = o_fit_regions.fit_dict['lambdahkl']['value']
        print(f"lambda_hkl: {lambdahkl:.3f}" + u"\u212b")
        ax4.axvline(lambdahkl,
                    color='r', linestyle='--')
        _local_max_counts = np.max(-np.log(y_axis_to_fit))
        max_counts = _local_max_counts if _local_max_counts > max_counts else max_counts
        ax4.text(lambdahkl,
                 (max_counts-max_counts/2),
                 f"{lambdahkl:.3f}",
                 ha="center",
                 rotation=45,
                 size=15,
                 )

        element = self.v.children[4].value
        if element == 'Ni':
            _handler = BraggEdgeLibrary(material=[element],
                                        number_of_bragg_edges=6)
        else:  # Ta
            _handler = BraggEdgeLibrary(new_material=[{'name': 'Ta',
                                                       'lattice': 3.3058,
                                                       'crystal_structure': 'BCC'}],
                                        number_of_bragg_edges=6)

        self.bragg_edges = _handler.bragg_edges
        self.hkl = _handler.hkl
        self.handler = _handler

        for _index, _lambda in enumerate(self.bragg_edges[element]):
            # to display _x in the right axis
            ax4.axvline(x=_lambda, color='r', linestyle='--')

            ax4.text(_lambda, (max_counts - max_counts/7),
                     f"{element}\n{_lambda:.3f}",
                     ha="center",
                     rotation=45,
                     size=15,
                     )

    def saving_session(self):
        # select output location
        o_output_folder = FileFolderBrowser(working_dir=self.working_dir,
                                            next_function=self.export_session)
        o_output_folder.select_output_folder(instruction="Select output folder ...")

    def export_session(self, output_folder=None):

        logging.info(f"Export session")

        # create output file name based on input nexus loaded
        input_nexus_filename = self.input_nexus_filename
        base, _ = os.path.splitext(os.path.basename(input_nexus_filename))
        current_time = get_current_time_in_special_file_name_format()

        output_file_name = os.path.join(output_folder, f"config_{base}_{current_time}.json")

        # record all parameters
        rois_selected = self.rois_selected
        dSD_m = self.v.children[1].value
        offset_micros = self.v.children[2].value
        time_shift = self.v.children[3].value
        element = self.v.children[4].value

        left_range = self.peak_to_fit.children[0].value
        right_range = self.peak_to_fit.children[1].value
        left_edge = self.peak_to_fit.children[2].value
        right_edge = self.peak_to_fit.children[3].value

        # make json compatible rois_selected
        json_friendly_rois_selected = {}
        for _key in rois_selected.keys():
            json_friendly_rois_selected[str(_key)] = {JSONKeys.x0: str(rois_selected[_key][JSONKeys.x0]),
                                                      JSONKeys.y0: str(rois_selected[_key][JSONKeys.y0]),
                                                      JSONKeys.x1: str(rois_selected[_key][JSONKeys.x1]),
                                                      JSONKeys.y1: str(rois_selected[_key][JSONKeys.y1]),
                                                      }

        json_dict = {JSONKeys.infos: f"config file created on {current_time}",
                     JSONKeys.input_nexus_filename: input_nexus_filename,
                     JSONKeys.dSD_m: f"{dSD_m:.4f}",
                     JSONKeys.offset_micros: f"{offset_micros:.4f}",
                     JSONKeys.time_shift: f"{time_shift:.4f}",
                     JSONKeys.element: element,
                     JSONKeys.left_range: f"{left_range:.4f}",
                     JSONKeys.right_range: f"{right_range:.4f}",
                     JSONKeys.left_edge: f"{left_edge:.4f}",
                     JSONKeys.right_edge: f"{right_edge:.4f}",
                     JSONKeys.rois_selected: json_friendly_rois_selected}

        logging.info(json_dict)

        with open(output_file_name, 'w') as json_file:
            json.dump(json_dict, json_file)

        display(HTML('<span>Created config file: </span><span style="font-size: 20px; color:blue">' +
                     output_file_name + '</span>'))
