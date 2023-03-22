import logging
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from ipywidgets import interactive
import ipywidgets as widgets
from IPython.core.display import display, HTML
from lmfit import Model, Parameter

from __code.roi_selection_ui import Interface

from neutronbraggedge.experiment_handler import *
from neutronbraggedge.braggedge import BraggEdge as BraggEdgeLibrary

from __code._utilities.file import get_full_home_file_name
from __code._utilities import LAMBDA, MICRO, ANGSTROMS
from __code._utilities.color import Color
from __code.ipywe import fileselector
from __code.timepix3_histo_hdf5_mcp_detector.fit_regions import FitRegions
from __code._utilities.array import find_nearest_index

LOG_FILE_NAME = ".timepix3_histo_hdf5_mcp_detector.log"
MAX_TIME_PER_PULSE = 1.667e4


class Timepix3HistoHdf5McpDetector:

    # histogram data
    histo_data = None

    # list of profiles
    profile_dict = None

    def __init__(self, working_dir=None):
        self.working_dir = working_dir

        self.log_file_name = get_full_home_file_name(LOG_FILE_NAME)
        logging.basicConfig(filename=self.log_file_name,
                            filemode='w',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)
        logging.info("*** Starting a new session ***")

    def select_nexus(self):
        self.nexus_ui = fileselector.FileSelectorPanel(instruction='Select Histo HDF5 file ...',
                                                       start_dir=self.working_dir,
                                                       next=self.load_nexus,
                                                       filters={'NeXus': ".h5"},
                                                       multiple=False)
        self.nexus_ui.show()

    def load_nexus(self, nexus_file_name=None):
        logging.info(f"Loading HDF5: {nexus_file_name}")
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
                          display_info_message=False)

        o_gui.show()
        # QtGui.QGuiApplication.processEvents()

    def returning_from_roi_selection(self, roi_selected):
        logging.info(f"User selected: {roi_selected}")
        self.roi_selected = roi_selected

    def calculate_and_display_profiles(self):
        roi_selected = self.roi_selected

        list_matplotlib_colors = Color.list_matplotlib

        profile_dict = {}
        rect_array = []
        for _roi_index in roi_selected.keys():
            x0 = roi_selected[_roi_index]['x0']
            y0 = roi_selected[_roi_index]['y0']
            x1 = roi_selected[_roi_index]['x1']
            y1 = roi_selected[_roi_index]['y1']

            profile_dict[_roi_index] = []

            for _index_image, _image in enumerate(self.stack):
                mean_counts = np.nanmean(_image[y0:y1+1, x0:x1+1])
                profile_dict[_roi_index].append(mean_counts)

            _rect = patches.Rectangle((x0, y0),
                                      x1-x0,
                                      y1-y0,
                                      linewidth=1,
                                      edgecolor=list_matplotlib_colors[_roi_index],
                                      facecolor='none')
            rect_array.append(_rect)

        self.profile_dict = profile_dict

        max_counts = []
        for _profile_key in profile_dict.keys():
            max_counts.append(np.max(profile_dict[_profile_key]))
        total_max_counts = np.max(max_counts)

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

        def plot_profiles(x_axis, dSD_m, offset_micros, time_shift, element):

            if element == 'Ni':
                _handler = BraggEdgeLibrary(material=[element],
                                            number_of_bragg_edges=5)
            else:  # Ta
                _handler = BraggEdgeLibrary(new_material=[{'name': 'Ta',
                                                           'lattice': 3.3058,
                                                           'crystal_structure': 'BCC'}],
                                            number_of_bragg_edges=5)

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
            for _profile_key in profile_dict.keys():

                _profile = np.array(profile_dict[_profile_key])
                _profile_shifted = np.hstack((_profile[~condition], _profile[condition]))

                ax2.plot(x_axis_array, _profile_shifted,
                         label=f"ROI #{_profile_key}",
                         color=list_matplotlib_colors[_profile_key])
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

                    ax2.text(_x, (total_max_counts - total_max_counts / 7),
                             _hkl,
                             ha="center",
                             rotation=45,
                             size=15,
                             )

        self.v = interactive(plot_profiles,
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

        lambda_x_axis, profiles_shifted_dict = self.prepare_data()
        self.lambda_x_axis = lambda_x_axis
        self.profiles_shifted_dict = profiles_shifted_dict

        list_matplotlib_colors = Color.list_matplotlib
        fig3, ax3 = plt.subplots(figsize=(8, 8),
                                 nrows=1,
                                 ncols=1)

        def plot_peaks(left_range, right_range, left_edge, right_edge):

            ax3.cla()

            for _profile_key in profiles_shifted_dict.keys():

                _profile = np.array(profiles_shifted_dict[_profile_key])

                ax3.plot(lambda_x_axis, _profile,
                         label=f"ROI #{_profile_key}",
                         color=list_matplotlib_colors[_profile_key])
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
                                                                      # value=np.min(lambda_x_axis),
                                                                      value=0.8,  # FIXME for debugging only
                                                                      readout_format=".3f"),
                                       right_range=widgets.FloatSlider(min=np.min(lambda_x_axis),
                                                                       max=np.max(lambda_x_axis),
                                                                       # value=np.max(lambda_x_axis),
                                                                       value=1.9,  # FIXME for debugging only
                                                                       readout_format=".3f"),
                                       left_edge=widgets.FloatSlider(min=np.min(lambda_x_axis),
                                                                     max=np.max(lambda_x_axis),
                                                                     value=1.2,  # FIXME for debugging only
                                                                     readout_format=".3f"),
                                       right_edge=widgets.FloatSlider(min=np.min(lambda_x_axis),
                                                                      max=np.max(lambda_x_axis),
                                                                      value=1.4,   # FIXME for debugging only
                                                                      readout_format=".3f"))
        display(self.peak_to_fit)

    def prepare_data(self):
        """
        this is where the y-axis to fit and x_axis (lambda scale) are calculated using the instrument
        settings and the time shift define in the previous cells.
        """

        profiles_dict = self.profile_dict
        profiles_shifted_dict = {}

        dSD_m = self.v.children[1].value
        offset_micros = self.v.children[2].value
        time_shift = self.v.children[3].value
        # element = self.v.children[4].value

        # left_range = self.peak_to_fit.children[0].value
        # right_range = self.peak_to_fit.children[1].value

        tof_array = self.time_spectra[:-1]
        condition = np.array(tof_array) < time_shift

        _exp = Experiment(tof=tof_array * 1e-6,  # to convert to seconds
                          distance_source_detector_m=dSD_m,
                          detector_offset_micros=offset_micros)
        lambda_array = _exp.lambda_array[:] * 1e10  # to be in Angstroms

        for _profile_key in profiles_dict.keys():
            _profile = np.array(profiles_dict[_profile_key])
            _profile_shifted = np.hstack((_profile[~condition], _profile[condition]))
            # _profile_shifted = _profile_shifted[left_range: right_range]
            profiles_shifted_dict[_profile_key] = _profile_shifted

        # self.x_axis_to_fit = lambda_array[left_range: right_range]
        self.x_axis_to_fit = lambda_array
        self.list_of_y_axis_to_fit = profiles_shifted_dict

        return lambda_array, profiles_shifted_dict

    def setup_fitting_parameters(self):

        display(HTML('<span style="font-size: 20px; color:blue">Init parameters</span>'))

        text_width = '80px'   # px
        display(HTML('<span style="font-size: 15px; color:green">High lambda</span>'))
        self.a0_layout = widgets.HBox([widgets.Label(u"a\u2080"),
                                  widgets.IntText(1,
                                                  layout=widgets.Layout(width=text_width))])
        self.b0_layout = widgets.HBox([widgets.Label(u"b\u2080"),
                                  widgets.IntText(1,
                                                  layout=widgets.Layout(width=text_width))])
        high_layout = widgets.VBox([self.a0_layout,
                                    self.b0_layout])
        display(high_layout)

        display(HTML(''))

        display(HTML('<span style="font-size: 15px; color:green">Low lambda</span>'))
        self.ahkl_layout = widgets.HBox([widgets.Label(u"a\u2095\u2096\u2097"),
                                  widgets.IntText(1,
                                                  layout=widgets.Layout(width=text_width))])
        self.bhkl_layout = widgets.HBox([widgets.Label(u"b\u2095\u2096\u2097"),
                                  widgets.IntText(1,
                                                  layout=widgets.Layout(width=text_width))])
        low_layout = widgets.VBox([self.ahkl_layout,
                                   self.bhkl_layout])
        display(low_layout)

        display(HTML(''))

        display(HTML('<span style="font-size: 15px; color:green">Bragg peak</span>'))
        self.lambdahkl_layout = widgets.HBox([widgets.Label(u"\u03bb\u2095\u2096\u2097"),
                                  widgets.FloatText(5e-8,
                                                    layout=widgets.Layout(width=text_width))])
        self.tau_layout = widgets.HBox([widgets.Label(u"\u03C4"),
                                  widgets.FloatText(1,
                                                    layout=widgets.Layout(width=text_width))])
        self.sigma_layout = widgets.HBox([widgets.Label(u"\u03C3"),
                                   widgets.FloatText(1e-3,
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
        profiles_shifted_dict = self.profiles_shifted_dict

        left_lambda_range = self.peak_to_fit.children[0].value
        right_lambda_range = self.peak_to_fit.children[1].value

        left_range = find_nearest_index(lambda_x_axis, left_lambda_range)
        right_range = find_nearest_index(lambda_x_axis, right_lambda_range)

        logging.info(f"Prepare data to fit:")
        logging.info(f"\tleft_range: {left_lambda_range}" + u"\u212b " + f"-> index: {left_range}")
        logging.info(f"\tright_range: {right_lambda_range}" + u"\u212b " + f"-> index: {right_range}")
        logging.info(f"\tlambda_x_axis: {lambda_x_axis}")
        logging.info(f"\tnumber of profiles: {len(profiles_shifted_dict.keys())}")

        for _profile_key in profiles_shifted_dict.keys():
            logging.info(f"\t{_profile_key}: size is {len(profiles_shifted_dict[_profile_key])}")
            _profile = np.array(profiles_shifted_dict[_profile_key])
            _profile_to_fit = _profile[left_range: right_range+1]

        self.x_axis_to_fit = lambda_x_axis[left_range: right_range]

        self.x_axis_to_fit = lambda_x_axis
        self.list_of_y_axis_to_fit = profiles_shifted_dict

    def fit_peak(self):

        self.prepare_data_to_fit()

        x_axis_to_fit = self.x_axis_to_fit
        list_of_y_axis_to_fit = self.list_of_y_axis_to_fit

        a0 = self.a0_layout.children[1].value
        b0 = self.b0_layout.children[1].value

        ahkl = self.ahkl_layout.children[1].value
        bhkl = self.bhkl_layout.children[1].value

        lambdahkl = self.lambdahkl_layout.children[1].value
        tau = self.tau_layout.children[1].value
        sigma = self.sigma_layout.children[1].value

        for _y_axis_to_fit in list_of_y_axis_to_fit:

            o_fit_regions = FitRegions(a0=a0,
                                       b0=b0,
                                       ahkl=ahkl,
                                       bhkl=bhkl,
                                       lambdahkl=lambdahkl,
                                       sigma=sigma,
                                       tau=tau,
                                       x_axis_to_fit=x_axis_to_fit,
                                       y_axis_to_fit=_y_axis_to_fit)
