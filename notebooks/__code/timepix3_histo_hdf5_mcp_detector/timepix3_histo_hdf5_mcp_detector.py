import logging
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from ipywidgets import interactive
import ipywidgets as widgets
from IPython.core.display import display, HTML
from qtpy import QtGui

from __code.roi_selection_ui import Interface

from neutronbraggedge.experiment_handler import *
from neutronbraggedge.braggedge import BraggEdge as BraggEdgeLibrary

from __code._utilities.file import get_full_home_file_name
from __code._utilities import LAMBDA, MICRO, ANGSTROMS
from __code._utilities.color import Color
from __code.ipywe import fileselector


LOG_FILE_NAME = ".timepix3_histo_hdf5_mcp_detector.log"


class Timepix3HistoHdf5McpDetector:

    # histogram data
    histo_data = None

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
            self.time_spectra = np.array(f['entry']['histo']['tof_ns'])

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

            _rect = patches.Rectangle((y0, x0),
                                      y1-y0,
                                      x1-x0,
                                      linewidth=1,
                                      edgecolor=list_matplotlib_colors[_roi_index],
                                      facecolor='none')
            rect_array.append(_rect)

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

        def plot_profiles(x_axis, dSD_m, offset_micros, element):

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

            if x_axis == 'TOF':
                tof_array = self.time_spectra
                x_axis_array = tof_array
                xlabel = "TOF offset (" + MICRO + "s)"
            else:
                _exp = Experiment(tof=self.time_spectra * 1e-6,  # to convert to seconds
                                  distance_source_detector_m=dSD_m,
                                  detector_offset_micros=offset_micros)
                lambda_array = _exp.lambda_array[:] * 1e10  # to be in Angstroms
                x_axis_array = lambda_array
                xlabel = LAMBDA + "(" + ANGSTROMS + ")"

            ax2.cla()
            for _profile_key in profile_dict.keys():
                ax2.plot(x_axis_array[:-1], profile_dict[_profile_key],
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

        v = interactive(plot_profiles,
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
                        element=widgets.RadioButtons(options=['Ni', 'Ta'],
                                                     value='Ni'),
                        )
        display(v)