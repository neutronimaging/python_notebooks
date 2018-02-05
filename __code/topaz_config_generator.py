import glob
from ipywidgets import widgets
import ipywe.fileselector
import os

from IPython.core.display import HTML
from IPython.display import display


class TopazConfigGenerator(object):

    ikeda_flag_ui = None
    v_box = None
    fit_peaks_vertical_layout = None
    reduce_ui = None
    reduce_label_ui = None

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
              'use_ellipse_integration': True,
              'use_fit_peaks_integration': False,
              'use_cylindrical_integration': False,
              'peak_radius': 0.130,
              'bkg_inner_radius': 0.14,
              'bkg_outer_radius': 0.15,
              'integrate_if_edge_peak': True,
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


    def __init__(self, working_dir=''):
        self.working_dir = working_dir
        self.__define_css_format()
        self.__run()

    def __run(self):

        # calibration files
        working_dir = self.working_dir

        calib_folder = os.path.dirname(working_dir)
        list_of_calibration_file = glob.glob(os.path.join(calib_folder, 'shared/calibrations') + '/2017C/*.DetCal')
        list_of_calibration_file.append('None')

        display(HTML("<h2>Specify calibration file(s)</h2><br>SNAP requires two calibration files, one for each bank. \
                     If the default detector position is to be used, specify <strong>None</strong> as the calibration file name."))

        calibration1_ui = widgets.HBox([widgets.Label("Calibration File #1:",
                                                      layout=widgets.Layout(width='15%')),
                                        widgets.Dropdown(options=list_of_calibration_file,
                                                         layout=widgets.Layout(width='60%'))])

        display(calibration1_ui)

        # Test correction for Goniometer z offset

        display(HTML("<h2>Goniometer z Offset Correction</h2><br>Test correction for Goniometer z offset"))

        offset_min_value = -10.0
        offset_max_value = +10.0

        zoffset_ui = widgets.HBox([widgets.Label("z_offset:",
                                                 layout=widgets.Layout(width='5%')),
                                   widgets.FloatSlider(value=0.0,
                                                       min=offset_min_value,
                                                       max=offset_max_value,
                                                       readout_format='.2f',
                                                       continuous_update=False,
                                                       layout=widgets.Layout(width='30%'))])

        xoffset_ui = widgets.HBox([widgets.Label("x_offset:",
                                                 layout=widgets.Layout(width='5%')),
                                   widgets.FloatSlider(value=0.0,
                                                       min=offset_min_value,
                                                       max=offset_max_value,
                                                       readout_format='.2f',
                                                       continuous_update=False,
                                                       layout=widgets.Layout(width='30%'))])

        offset_ui = widgets.VBox([zoffset_ui, xoffset_ui])
        display(offset_ui)

        display(HTML("<h2>Select Input Data Folder</h2>"))

        input_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='',
                                                               start_dir=os.path.join(working_dir, 'data'),
                                                               type='directory')
        input_folder_ui.show()

        display(HTML("<h2>Select or Create Output Folder</h2>"))
        output_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Location of Output Folder',
                                                                start_dir=os.path.join(working_dir, 'shared'),
                                                                type='directory',
                                                                newdir_toolbar_button=True)
        output_folder_ui.show()

        display(HTML("<h2>Use Monitor Counts ?</h2><br> If use_monitor_counts is True, then the integrated beam monitor \
            counts will be used for scaling. <br>If use_monitor_counts is False, \
            then the integrated proton charge will be used for scaling. <br><br>These \
            values will be listed under MONCNT in the integrate file."))

        monitor_counts_flag_ui = widgets.Checkbox(value=False,
                                                  description='Use Monitor Counts')
        display(monitor_counts_flag_ui)

        display(HTML("<h2>TOF and Monitor</h2><br>Min & max tof determine the range of events loaded.<br> Min & max monitor tof \
                    determine the range of tofs integrated in the monitor data to get the \
                    total monitor counts. <br>You need these even if Use Monitor Counts is False."))

        left_column_width = '15%'

        tof_ui = widgets.HBox([widgets.Label("TOF Range",
                                             layout=widgets.Layout(width=left_column_width)),
                               widgets.IntRangeSlider(value=[1000, 16600],
                                                      min=500,
                                                      max=16600,
                                                      step=1,
                                                      continuous_update=False,
                                                      readout_format='d',
                                                      layout=widgets.Layout(width='50%')),
                               widgets.Label("\u00B5s",
                                             layout=widgets.Layout(width='20%'))])

        monitor_index_ui = widgets.HBox([widgets.Label("Monitor Index",
                                                       layout=widgets.Layout(width=left_column_width)),
                                         widgets.Dropdown(options=['0', '1'],
                                                          value='0',
                                                          layout=widgets.Layout(width='10%'))])

        monitor_ui = widgets.HBox([widgets.Label("Monitor TOF Range",
                                                 layout=widgets.Layout(width=left_column_width)),
                                   widgets.IntRangeSlider(value=[800, 12500],
                                                          min=500,
                                                          max=16600,
                                                          step=1,
                                                          continuous_update=False,
                                                          readout_format='d',
                                                          layout=widgets.Layout(width='50%')),
                                   widgets.Label("\u00B5s",
                                                 layout=widgets.Layout(width='20%'))])

        tof_ui = widgets.VBox([tof_ui, monitor_index_ui, monitor_ui])

        display(tof_ui)

        display(HTML("<h2>UB</h2><br>Read the UB matrix from file. This option will be applied to each run and used for \
            combined file. This option is especially helpful for 2nd frame TOPAZ data."))

        ub_flag_ui = widgets.Checkbox(value=False,
                                      description='Read UB')

        display(ub_flag_ui)

        if ub_flag_ui.value:
            ub_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select UB File (*.mat)',
                                                         start_dir=os.path.join(working_dir, 'shared'))

            ub_ui.show()

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
                                                   layout=widgets.Layout(width=left_column_width)),
                                     widgets.Dropdown(options=['Monoclinic', 'Triclinic', 'other'],
                                                      value='Monoclinic',
                                                      layout=widgets.Layout(width='20%'))])

        centering_ui = widgets.HBox([widgets.Label("Centering:",
                                                   layout=widgets.Layout(width=left_column_width)),
                                     widgets.Dropdown(options=['I', 'F', 'A', 'B', 'C', 'P', 'None'],
                                                      value='P',
                                                      layout=widgets.Layout(width='20%'))])

        cell_ui = widgets.VBox([cell_type_ui, centering_ui])

        display(cell_ui)

        display(HTML("<h2>Number of Peaks</h2><br> Number of peaks to find, per run, both for getting the UB matrix, \
        AND to determine how many peaks are integrated, if peak positions are \
        NOT predicted. <br><br> <strong>NOTE:</strong> This number must be choosen carefully. <ul><li> If too \
        many peaks are requested, find peaks will take a very long time and \
        the returned peaks will probably not even index, since most of them \
        will be 'noise' peaks.</li><li> If too few are requested, then there will be \
        few peaks to be integrated, and the UB matrix may not be as accurate \
        as it should be for predicting peaks to integrate.</li></ul>"))

        peak_ui = widgets.HBox([widgets.Label("Number of Peaks:",
                                              layout=widgets.Layout(width=left_column_width)),
                                widgets.IntSlider(value=300,
                                                  min=100,
                                                  max=3000,
                                                  layout=widgets.Layout(width='30%'))])
        display(peak_ui)

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

        tolerance_ui = widgets.HBox([widgets.Label("Tolerance",
                                                   layout=widgets.Layout(width='10%')),
                                     widgets.FloatSlider(value=0.12,
                                                         min=0.06,
                                                         max=0.51,
                                                         step=0.01,
                                                         layout=widgets.Layout(width='30%'))])

        d_tolerance_ui = widgets.VBox([d_ui, tolerance_ui])

        display(d_tolerance_ui)

        display(HTML("<h2>Predicted Peak</h2><br> If predicted peak positions are to be integrated, \
            then the integrate_predicted_peaks flag should be set to True and the range \
            of wavelengths and d-spacings must be specified"))

        pred_flag_ui = widgets.HBox([widgets.Label("Integrate Predicted Peaks?",
                                                   layout=widgets.Layout(width='20%')),
                                     widgets.Checkbox(value=False,
                                                      layout=widgets.Layout(width='20%'))])

        pred_ui = widgets.HBox([widgets.Label("Predicted Wavelengths",
                                              layout=widgets.Layout(width='20%')),
                                widgets.FloatRangeSlider(value=[0.5, 3.4],
                                                         min=.25,
                                                         max=3.6,
                                                         layout=widgets.Layout(width='35%')),
                                widgets.Label("\u00c5")])

        pred_dspacing_ui = widgets.HBox([widgets.Label("Predicted dspacing",
                                                       layout=widgets.Layout(width='20%')),
                                         widgets.FloatRangeSlider(value=[0.5, 11.0],
                                                                  min=.25,
                                                                  max=12,
                                                                  layout=widgets.Layout(width='35%')),
                                         widgets.Label("\u00c5")])

        predicted_ui = widgets.VBox([pred_flag_ui, pred_ui, pred_dspacing_ui])
        display(predicted_ui)

        display(HTML("<h2>Integration Method</h2><br> Select one of the following integration method."))

        inte_ui = widgets.HBox([widgets.Label("Integration Method",
                                              layout=widgets.Layout(width='15%')),
                                widgets.Dropdown(options=['Sphere', 'Ellipse', 'Cylindrical', 'Fit Peaks'],
                                                 value='Ellipse',
                                                 layout=widgets.Layout(width='20%'))])
        display(inte_ui)

        _answer_ikeda = False

        #         display(HTML("<h2>Integration Control Parameters</h2>"))

        peak_ui = widgets.HBox([widgets.Label("Peak Radius",
                                              layout=widgets.Layout(width='25%')),
                                widgets.FloatSlider(value=0.13,
                                                    min=0.05,
                                                    max=0.25,
                                                    step=0.001,
                                                    readout_format='.3f',
                                                    layout=widgets.Layout(width='30%')),
                                widgets.Label("\u00c5")])

        bkg_ui = widgets.HBox([widgets.Label("Background Inner and Outer Radius",
                                             layout=widgets.Layout(width='25%')),
                               widgets.FloatRangeSlider(value=[0.14, 0.15],
                                                        min=peak_ui.children[1].value,
                                                        max=0.2,
                                                        step=0.001,
                                                        readout_format='.3f',
                                                        layout=widgets.Layout(width='30%')),
                               widgets.Label("\u00c5")])

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
        vertical_layout.append(ellipse_region_ui)

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
        self.inte_flag_ui = inte_flag_ui

        inte_flag_ui = self.inte_flag_ui
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

        self.length_ui = widgets.HBox([widgets.Label("Cylinder Length",
                                                layout=widgets.Layout(width='15%')),
                                  widgets.FloatSlider(value=0.3,
                                                      min=0.1,
                                                      max=0.5,
                                                      step=0.01,
                                                      readout_format="0.3f",
                                                      layout=widgets.Layout(width='30%')),
                                  widgets.Label("\u00c5")])

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

        display(HTML("<h2>Bad Edge Pixels</h2>"))

        bad_pixels_ui = widgets.HBox([widgets.Label("Nbr bad edge pixels:",
                                                    layout=widgets.Layout(width='15%')),
                                      widgets.IntSlider(value=0,
                                                        min=0,
                                                        max=50,
                                                        layout=widgets.Layout(width='30%'))])

        display(bad_pixels_ui)

        display(HTML("<h2>Experiment Name</h2>"))

        exp_name_ui = widgets.Text("",
                                   layout=widgets.Layout(width="50%"))
        display(exp_name_ui)

        display(HTML("<h2>Run Numbers to Reduce</h2><br>Specify the run numbers that should be reduced."))

        run_ui = widgets.HBox([widgets.Label("Run Numbers:", layout=widgets.Layout(width='10%')),
                               widgets.Text(value="",
                                            layout=widgets.Layout(width='40%'),
                                            placeholder='1,4:5,10,20,30:40')])
        display(run_ui)

        import multiprocessing
        nbr_processor = multiprocessing.cpu_count()

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
        display(process_ui)


    def advanced_options(self):

        display(HTML("<br><br>"))
        pass_layout_ui = widgets.HBox([widgets.Label(" >>> Advanced Options Password <<<",
                                                     layout=widgets.Layout(width='25%')),
                                       widgets.Text("",
                                                    layout=widgets.Layout(width='10%'))])

        MASTER_PASSWORD = 'topaz'
        self.password_found = False

        password = []
        str_password = ''

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

            if str_password == MASTER_PASSWORD:

                if self.password_found == False:  # to only display widgets once
                    self.reduce_label_ui = widgets.Label("Reduce One Run Script",
                                                    layout=widgets.Layout(width='15%'))
                    display(self.reduce_label_ui)

                    self.reduce_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Reduce Python Script ',
                                                                     start_dir=os.path.join(
                                                                         self.working_dir,
                                                                         'shared/reduce/'))

                    self.reduce_ui.show()
                    self.password_found = True

                else:
                    self.password_found = False

            else:
                try:
                    self.reduce_label_ui.close()
                    self.reduce_ui.remove()
                except:
                    pass

        pass_ui = pass_layout_ui.children[1]
        pass_ui.observe(on_pass_changed, names='value')

        display(pass_layout_ui)

