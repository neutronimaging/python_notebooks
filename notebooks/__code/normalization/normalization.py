import os
import logging as notebook_logging

import numpy as np
from IPython.display import HTML, display
from ipywidgets import Layout, widgets
from NeuNorm.normalization import Normalization as NeuNormNormalization
from NeuNorm.roi import ROI

from __code.roi_selection_ui import Interface
from __code.ipywe.fileselector import FileSelectorPanel as MyFileSelectorPanel
from __code import file_handler
from __code._utilities.file import make_or_increment_folder_name
from __code.config import gamma_filtering_coefficient
from __code.ipywe import fileselector


LOG_PATH = "/SNS/VENUS/shared/log/"
file_name, ext = os.path.splitext(os.path.basename(__file__))
user_name = os.getlogin()  # add user name to the log file name
log_file_name = os.path.join(LOG_PATH, f"{user_name}_{file_name}.log")
notebook_logging.basicConfig(
    filename=log_file_name,
    filemode="w",
    format="[%(levelname)s] - %(asctime)s - %(message)s",
    level=notebook_logging.INFO,
)
notebook_logging.info(f"*** Starting {file_name} ***")


class ListFiles:
    sample = []
    ob = []
    df = []


class Normalization:
    sample_runs = []
    ob_runs = []
    dc_runs = []

    data_array = None

    def __init__(self, working_dir="."):
        self.working_dir = working_dir

        notebook_logging.info(
            f"Normalization object created with working directory: {self.working_dir}"
        )

    def select_sample_runs(self):
        self.select_data(
            instruction="Select Sample Runs",
            next_function=self.sample_next_function,
            start_dir=self.working_dir,
            multiple=True,
            newdir_toolbar_button=False,
        )

    def sample_next_function(self, b):
        notebook_logging.info(f"Sample files selected: {b}")
        self.sample_runs = b
        display(
            HTML(
                f"<span style='font-size:16px; color:blue'>{len(b)} Sample files selected</span>"
            )
        )
        print(f"{len(b)} sample files selected")

    def select_ob_runs(self):
        self.select_data(
            instruction="Select Open Beam (OB) Runs",
            next_function=self.ob_next_function,
            start_dir=self.working_dir,
            multiple=True,
            newdir_toolbar_button=False,
        )

    def ob_next_function(self, b):
        notebook_logging.info(f"OB files selected: {b}")
        self.ob_runs = b
        display(
            HTML(
                f"<span style='font-size:16px; color:blue'>{len(b)} OB files selected</span>"
            )
        )
        print(f"{len(b)} OB files selected")

    def select_dc_runs(self):
        self.select_data(
            instruction="Select Dark Current (DC) Runs (if any)",
            next_function=self.dc_next_function,
            start_dir=self.working_dir,
            multiple=True,
            newdir_toolbar_button=False,
        )

    def dc_next_function(self, b):
        notebook_logging.info(f"DC files selected: {b}")
        self.dc_runs = b
        display(
            HTML(
                f"<span style='font-size:16px; color:blue'>{len(b)} DC files selected</span>"
            )
        )
        print(f"{len(b)} DC files selected")

    def select_data(
        self,
        instruction="Select data runs",
        next_function=None,
        start_dir=None,
        multiple=True,
        newdir_toolbar_button=False,
    ):
        self.list_input_folders_ui = MyFileSelectorPanel(
            instruction=instruction,
            start_dir=start_dir,
            type="file",
            newdir_toolbar_button=newdir_toolbar_button,
            multiple=multiple,
            sort_in_reverse=True,
            # sort_increasing=False,
            next=next_function,
        )
        self.list_input_folders_ui.show()

    def load_data(self, data_type="sample"):
        if data_type == "sample":
            list_files = self.sample_runs
        elif data_type == "ob":
            list_files = self.ob_runs
        else:
            list_files = self.dc_runs

        o_norm = NeuNormNormalization()
        o_norm.load(file=list_files, data_type=data_type, notebook=True)
        self.o_norm = o_norm
        return o_norm.data[data_type]["data"]

    def select_background_region(self):
        # load sample images selected
        self.data_array = self.load_data(data_type="sample")
        # get integrated image and use it in the Interface
        self.o_roi_selection_ui = Interface(array2d=np.mean(self.data_array, axis=0))
        self.o_roi_selection_ui.show()

    def normalization_settings(self):
        if self.data_array is None:
            self.data_array = self.load_data(data_type="sample")

        list_files = ListFiles()
        list_files.sample = self.sample_runs
        list_files.ob = self.ob_runs
        list_files.df = self.dc_runs

        self.o_norm_handler = NormalizationHandler(
            list_files=list_files,
            working_dir=self.working_dir,
            sample_data=self.data_array,
        )
        self.o_norm_handler.load_data()
        self.o_norm_handler.settings()

    def select_output_folder(self):
        self.list_input_folders_ui = MyFileSelectorPanel(
            instruction="Select output folder",
            start_dir=self.working_dir,
            type="directory",
            newdir_toolbar_button=True,
            multiple=False,
            sort_in_reverse=True,
            # sort_increasing=False,
            next=self.normalized_and_export,
        )
        self.list_input_folders_ui.show()

    def normalized_and_export(self, output_folder):
        notebook_logging.info(f"Output folder selected: {output_folder}")
        display(
            HTML(
                f"<span style='font-size:16px; color:blue'>Output folder selected: {output_folder}</span>"
            )
        )
        self.output_folder = output_folder

    def export_normalized_data(self):
        output_folder = self.output_folder

        dict_roi = None
        if hasattr(self, "o_roi_selection_ui"):
            dict_roi = self.o_roi_selection_ui.list_roi
            if dict_roi == {}:
                dict_roi = None

        self.o_norm_handler.run_normalization(dict_roi=dict_roi)
        self.o_norm_handler.export(output_folder=output_folder)
        notebook_logging.info("*** End of the program ***")

    @classmethod
    def legend(cls) -> None:
        display(HTML("<hr style='height:2px'/>"))
        display(HTML("<h2>Legend</h2>"))
        display(
            HTML(
                "<ul>"
                "<li><b><font color='red'>Mandatory steps</font></b> must be performed to ensure proper data processing.</li>"
                "<li><b><font color='orange'>Optional but recommended steps</font></b> are not mandatory but should be performed to ensure proper data processing.</li>"
                "<li><b><font color='purple'>Optional steps</font></b> are not mandatory but highly recommended to improve the quality of your data processing.</li>"
                "</ul>"
            )
        )
        display(HTML("<hr style='height:2px'/>"))


class NormalizationHandler:
    data = None
    integrated_sample = []
    working_dir = ""
    o_norm = None

    normalized_data_array = []

    def __init__(
        self,
        list_files: ListFiles = None,
        working_dir: str = "",
        gamma_threshold: float = 0.9,
        sample_data: list = None,
    ):
        self.files = list_files
        self.working_dir = working_dir
        self.data = Data()
        if sample_data is not None:
            self.data.sample = sample_data

        self.gamma_threshold = gamma_threshold

    def load_data(self):
        self.o_norm = NeuNormNormalization()

        # sample

        list_sample = self.files.sample
        # self.o_norm.load(file=list_sample, notebook=True, auto_gamma_filter=False,
        #                  manual_gamma_filter=True, manual_gamma_threshold=self.gamma_threshold)
        self.o_norm.load(file=list_sample, notebook=True)
        self.data.sample = self.o_norm.data["sample"]["data"]
        self.list_file_names = list_sample

        # ob
        list_ob = self.files.ob
        # self.o_norm.load(file=list_ob, data_type='ob', notebook=True, auto_gamma_filter=False,
        #                  manual_gamma_filter=True, manual_gamma_threshold=self.gamma_threshold)
        self.o_norm.load(file=list_ob, data_type="ob", notebook=True)
        self.data.ob = self.o_norm.data["ob"]["data"]

        # df
        list_df = self.files.df
        if list_df:
            # self.o_norm.load(file=list_df, data_type='df', notebook=True, auto_gamma_filter=False,
            #                  manual_gamma_filter=True, manual_gamma_threshold=self.gamma_threshold)
            self.o_norm.load(file=list_df, data_type="df", notebook=True)
            self.data.df = self.o_norm.data["df"]["data"]

    def get_data(self, data_type="sample"):
        if data_type == "sample":
            return self.data.sample
        elif data_type == "ob":
            return self.data.ob
        else:
            return self.data.df

    # def plot_images(self, data_type='sample'):
    #
    #     sample_array = self.get_data(data_type=data_type)
    #
    #     def _plot_images(index):
    #         _ = plt.figure(num=data_type, figsize=(5, 5))
    #         ax_img = plt.subplot(111)
    #         my_imshow= ax_img.imshow(sample_array[index], cmap='viridis')
    #         plt.colorbar(my_imshow)
    #
    #     _ = widgets.interact(_plot_images,
    #                  index=widgets.IntSlider(min=0,
    #                                          max=len(self.get_data(data_type=data_type)) - 1,
    #                                          step=1,
    #                                          value=0,
    #                                          description='{} Index'.format(data_type),
    #                                          continuous_update=False))

    def calculate_integrated_sample(self):
        if len(self.data.sample) > 1:
            integrated_array = np.array([_array for _array in self.data.sample])
            self.integrated_sample = integrated_array.mean(axis=0)
        else:
            self.integrated_sample = np.squeeze(self.data.sample)

    # def with_or_without_roi(self):
    #     label1 = widgets.Label("Do you want to select a region of interest (ROI) that will make sure that the " +
    #                           "sample background matches the OB background")
    #     label2 = widgets.Label("-> Make sure your selection do not overlap your sample!")
    #     box = widgets.HBox([widgets.Label("With or Without ROI?"),
    #                         widgets.RadioButtons(options=['yes','no'],
    #                                             value='yes',
    #                                             layout=widgets.Layout(width='50%'))])
    #     self.with_or_without_radio_button = box.children[1]
    #     vertical = widgets.VBox([label1, label2, box])
    #     display(vertical)

    # def select_sample_roi(self):
    #
    #     if self.with_or_without_radio_button.value == 'no':
    #         label2 = widgets.Label("-> You chose not to select any ROI! Next step: Normalization")
    #         display(label2)
    #         return
    #
    #     label2 = widgets.Label("-> Make sure your selection do not overlap your sample!")
    #     display(label2)
    #
    #     if self.integrated_sample == []:
    #         self.calculate_integrated_sample()
    #
    #     _integrated_sample = self.integrated_sample
    #     [height, width] = np.shape(_integrated_sample)
    #
    #     def plot_roi(x_left, y_top, width, height):
    #         _ = plt.figure(figsize=(5, 5))
    #         ax_img = plt.subplot(111)
    #         ax_img.imshow(_integrated_sample,
    #                       cmap='viridis',
    #                       interpolation=None)
    #
    #         _rectangle = patches.Rectangle((x_left, y_top),
    #                                        width,
    #                                        height,
    #                                        edgecolor='white',
    #                                        linewidth=2,
    #                                        fill=False)
    #         ax_img.add_patch(_rectangle)
    #
    #         return [x_left, y_top, width, height]
    #
    #     self.roi_selection = widgets.interact(plot_roi,
    #                                   x_left=widgets.IntSlider(min=0,
    #                                                            max=width,
    #                                                            step=1,
    #                                                            value=0,
    #                                                            description='X Left',
    #                                                            continuous_update=False),
    #                                   y_top=widgets.IntSlider(min=0,
    #                                                           max=height,
    #                                                           value=0,
    #                                                           step=1,
    #                                                           description='Y Top',
    #                                                           continuous_update=False),
    #                                   width=widgets.IntSlider(min=0,
    #                                                           max=width - 1,
    #                                                           step=1,
    #                                                           value=60,
    #                                                           description="Width",
    #                                                           continuous_update=False),
    #                                   height=widgets.IntSlider(min=0,
    #                                                            max=height - 1,
    #                                                            step=1,
    #                                                            value=100,
    #                                                            description='Height',
    #                                                            continuous_update=False))

    def settings(self):
        o_norm = self.o_norm
        nbr_sample = len(self.data.sample)
        nbr_ob = len(self.data.ob)
        if self.data.df:
            nbr_df = len(self.data.df)
        else:
            nbr_df = 0

        table_title = "Summary Table"
        how_to_combine_title = "How do you want to combine the OBs?"
        force_combine_title = "Do you want to combine the OBs?"

        def force_combining_changed(value):
            widgets_changed()

        def how_to_combine_changed(value):
            widgets_changed()

        def widgets_changed():
            if self.force_ui.value == "no":
                accordion_children = [self.force_ui, table]
                accordion_title = [force_combine_title, table_title]
                self.how_to_ui.disabled = True
            elif nbr_sample != nbr_ob:
                accordion_children = [self.how_to_ui, table]
                accordion_title = [how_to_combine_title, table_title]
                self.how_to_ui.disabled = False
            else:
                accordion_children = [self.force_ui, self.how_to_ui, table]
                accordion_title = [
                    force_combine_title,
                    how_to_combine_title,
                    table_title,
                ]
                self.how_to_ui.disabled = False
            table.value = get_html_table()
            accordion.children = accordion_children
            for _index, _title in enumerate(accordion_title):
                accordion.set_title(_index, _title)
            accordion.selected_index = len(accordion_title) - 1

        def get_html_table():
            force_combine = self.force_ui.value
            how_to_combine = self.how_to_ui.value

            if force_combine == "yes":
                description = (
                    f"OBs <b>will be combined</b> using <b>{how_to_combine}</b>"
                )
            else:
                description = (
                    "OBs <b>won't be combined</b>! Each sample will use <b>1 OB</b>"
                )

            html_table = (
                f"<table style='width:800px'>"
                "<tr>"
                "<th style='background-color: grey'>Nbr of Samples</th>"
                "<th style='background-color: grey'>Nbr of OBs</th>"
                "<th style='background-color: grey'>Nbr of DCs</th>"
                "<th style='background-color: grey; width:60%'>Description of Process</th>"
                "</tr>"
                "<tr>"
                f"<td>{nbr_sample}</td>"
                f"<td>{nbr_ob}</td>"
                f"<td>{nbr_df}</td>"
                f"<td>{description}</td>"
                "</tr>"
                "</table>"
            )
            return html_table

        accordion_children = []
        accordion_title = list()

        self.force_ui = widgets.RadioButtons(
            options=["yes", "no"],
            value="yes",
            disabled=False,
            layout=widgets.Layout(width="200px"),
        )
        accordion_children.append(self.force_ui)
        self.force_ui.observe(force_combining_changed, names="value")

        self.how_to_ui = widgets.RadioButtons(
            options=["median", "mean"],
            value="median",
            layout=widgets.Layout(width="200px"),
        )
        accordion_children.append(self.how_to_ui)
        self.how_to_ui.observe(how_to_combine_changed, names="value")

        html_table = ""
        table = widgets.HTML(value=html_table)
        accordion_children.append(table)

        if nbr_sample != nbr_ob:
            self.force_ui.value = "yes"
            accordion_children = [self.how_to_ui, table]
            how_to_combine_title = "How to combine?"
            accordion_title = [how_to_combine_title, table_title]
        else:
            accordion_title.append(force_combine_title)
            accordion_title.append(how_to_combine_title)
            accordion_title.append(table_title)

        table.value = get_html_table()

        accordion = widgets.Accordion(
            children=accordion_children, title=accordion_title
        )

        for _index, _title in enumerate(accordion_title):
            accordion.set_title(_index, _title)

        accordion.selected_index = len(accordion_title) - 1
        display(accordion)

    def run_normalization(self, dict_roi=None):
        force_mean_ob = False
        force_median_ob = False

        force_combine = self.force_ui.value
        if force_combine == "yes":
            how_to_combine = self.how_to_ui.value
            if how_to_combine == "mean":
                force_mean_ob = True
            elif how_to_combine == "median":
                force_median_ob = True
            else:
                raise NotImplementedError(
                    f"How to combine OB algorithm ({how_to_combine}) not implemented!"
                )

        if dict_roi is None:
            # try:
            self.o_norm.df_correction()
            self.o_norm.normalization(
                notebook=True,
                force_median_ob=force_median_ob,
                force_mean_ob=force_mean_ob,
                force=True,
            )
            self.normalized_data_array = self.o_norm.get_normalized_data()
            self.normalized_metadata_array = self.o_norm.data["sample"]["metadata"]

            # except ValueError:
            #     display(
            #         HTML(
            #             '<span style="font-size: 20px; color:red">Data Size of Sample, OB and DF (if any) '
            #             + "do not Match!</span>"
            #         )
            #     )
            #     return

        else:
            _list_roi = []
            for _key in dict_roi.keys():
                _roi = dict_roi[_key]
                x0 = _roi["x0"]
                y0 = _roi["y0"]
                x1 = _roi["x1"]
                y1 = _roi["y1"]

                x_left = np.min([x0, x1])
                y_top = np.min([y0, y1])

                width_roi = np.abs(x0 - x1)
                height_roi = np.abs(y0 - y1)

                _roi = ROI(x0=x_left, y0=y_top, width=width_roi, height=height_roi)
                _list_roi.append(_roi)

            self.debugging_roi = _list_roi

            self.o_norm.df_correction()
            if _list_roi:
                # try:
                self.o_norm.normalization(
                    roi=_list_roi[0],
                    notebook=True,
                    force_median_ob=force_median_ob,
                    force_mean_ob=force_mean_ob,
                    force=True,
                )
                # except ValueError:
                #     display(
                #         HTML(
                #             '<span style="font-size: 20px; color:red">Data Size of Sample, OB and DF (if any) '
                #             + "do not Match!</span>"
                #         )
                #     )
                #     return

            else:
                self.o_norm.normalization(notebook=True)

            self.normalized_data_array = self.o_norm.get_normalized_data()
            self.normalized_metadata_array = self.o_norm.data["sample"]["metadata"]

    def select_export_folder(self, ipts_folder="./"):
        def display_file_selector_from_shared(ev):
            start_dir = os.path.join(ipts_folder, "shared")
            self.output_folder_ui.remove()
            self.display_file_selector(start_dir=start_dir)

        def display_file_selector_from_home(ev):
            import getpass

            _user = getpass.getuser()
            start_dir = os.path.join("/SNS/users", _user)
            self.output_folder_ui.remove()
            self.display_file_selector(start_dir=start_dir)

        ipts = os.path.basename(self.working_dir)

        button_layout = widgets.Layout(width="30%", border="1px solid gray")

        hbox = widgets.HBox(
            [
                widgets.Button(
                    description=f"Jump to {ipts} Shared Folder",
                    button_style="success",
                    layout=button_layout,
                ),
                widgets.Button(
                    description="Jump to My Home Folder",
                    button_style="success",
                    layout=button_layout,
                ),
            ]
        )
        go_to_shared_button_ui = hbox.children[0]
        go_to_home_button_ui = hbox.children[1]

        go_to_shared_button_ui.on_click(display_file_selector_from_shared)
        go_to_home_button_ui.on_click(display_file_selector_from_home)

        display(hbox)

        self.display_file_selector()

    def display_file_selector(self, start_dir=""):
        self.output_folder_ui = fileselector.FileSelectorPanel(
            instruction="Select Output Folder",
            start_dir=start_dir,
            multiple=False,
            type="directory",
        )
        self.output_folder_ui.show()

    def export(self, output_folder):
        base_folder = (
            os.path.basename(os.path.dirname(self.list_file_names[0])) + "_normalized"
        )
        output_folder = os.path.join(output_folder, base_folder)
        output_folder = make_or_increment_folder_name(output_folder)

        w = widgets.IntProgress(description="Exporting: ", value=0)
        w.max = len(self.files.sample)
        display(w)

        for _index, _file in enumerate(self.list_file_names):
            basename = os.path.basename(_file)
            _base, _ext = os.path.splitext(basename)
            output_file_name = os.path.join(output_folder, _base + ".tiff")
            file_handler.make_tiff(
                filename=output_file_name,
                data=self.normalized_data_array[_index],
                metadata=self.normalized_metadata_array[_index],
            )

            w.value = _index + 1

        display(
            HTML(
                '<span style="font-size: 20px; color:blue">The normalized images have been '
                + "created in "
                + output_folder
                + "</span>"
            )
        )


class GammaCoefficient:
    def select_gamma_coefficient(self):
        self.gamma_coeff_ui = widgets.HBox(
            [
                widgets.Label("Gamma Coefficient:", layout=widgets.Layout(width="20%")),
                widgets.FloatSlider(
                    value=gamma_filtering_coefficient,
                    min=0,
                    max=1,
                    layout=widgets.Layout(width="50%"),
                ),
            ]
        )
        display(self.gamma_coeff_ui)

    def get_coefficient(self):
        return self.gamma_coeff_ui.children[1].value


def close(w):
    "recursively close a widget"
    if hasattr(w, "children"):
        for c in w.children:
            close(c)
            continue
    w.close()
    return


class myFileSelectorPanel(fileselector.FileSelectorPanel):
    def __init__(
        self,
        instruction,
        start_dir=".",
        type="file",
        next=None,
        multiple=False,
        newdir_toolbar_button=False,
        current_ui=None,
    ):
        super(myFileSelectorPanel, self).__init__(
            instruction,
            start_dir=start_dir,
            type=type,
            next=next,
            multiple=multiple,
            newdir_toolbar_button=newdir_toolbar_button,
        )
        self.current_ui = current_ui

    def validate(self, s):
        super(myFileSelectorPanel, self).validate(s)
        try:
            if self.current_ui.state == "sample":
                self.current_ui.files.sample = self.selected
            elif self.current_ui.state == "ob":
                self.current_ui.files.ob = self.selected
            else:
                self.current_ui.files.df = self.selected

            parent_folder = os.path.dirname(os.path.dirname(self.selected[0]))
            self.current_ui.working_dir = parent_folder
            self.current_ui.label.value = f"{len(self.selected)} files selected"
            self.current_ui.next_button_ui.disabled = False
            self.current_ui.next_button_ui.button_style = "success"
        except AttributeError:
            pass


class Data:
    sample = []
    ob = []
    df = []


class Files:
    sample = []
    ob = []
    df = []


class Panel:
    layout = Layout(border="1px lightgray solid", margin="5px", padding="15px")
    button_layout = Layout(margin="10px 5px 5px 5px")
    label_layout = Layout(height="32px", padding="2px", width="300px")

    current_state_label_ui = None
    prev_button_ui = None
    next_button_ui = None
    o_norm_handler = None

    df_panel = None

    def __init__(
        self,
        prev_button=False,
        next_button=False,
        state="sample",
        working_dir="",
        top_object=None,
        gamma_coefficient=0.9,
    ):
        self.prev_button = prev_button
        self.next_button = next_button
        self.state = state
        self.working_dir = working_dir
        self.ipts_dir = working_dir
        self.top_object = top_object
        self.gamma_threshold = gamma_coefficient

    def init_ui(self, files=None):
        self.files = files

        self.__top_panel()
        self.__bottom_panel()
        self.__file_selector()
        self.__init_widgets()

    def __init_widgets(self):
        _list = self.files.sample
        _label = "Sample"
        _option = "(mandatory)"
        if self.state == "ob":
            _list = self.files.ob
            _label = "Open Beam"
        elif self.state == "df":
            _list = self.files.df
            _label = "Dark Field"
            _option = "(optional)"
        self.label.value = f"{len(_list)} files selected"
        self.title.value = f"Select list of {_label} files {_option} "

        if len(_list) > 0:
            self.next_button_ui.disabled = False
            self.next_button_ui.button_style = "success"

        if self.state == "df":
            self.next_button_ui.disabled = False
            self.next_button_ui.button_style = "success"

    def __top_panel(self):
        title_ui = widgets.HBox(
            [
                widgets.Label("Instructions:", layout=widgets.Layout(width="20%")),
                widgets.Label(
                    "Select Samples Images and click NEXT",
                    layout=widgets.Layout(width="50%"),
                ),
            ]
        )

        # label_ui = widgets.HBox(
        #     [
        #         widgets.Label("Sample selected:", layout=widgets.Layout(width="20%")),
        #         widgets.Label("None", layout=widgets.Layout(width="50%")),
        #     ]
        # )
        self.title = title_ui.children[
            1
        ]  # "Select [Samples/OB/DF] Images [and click NEXT]
        # self.label = label_ui.children[1]  # number of samples selected

        # self.top_panel = widgets.VBox(children=[title_ui, label_ui], layout=self.layout)
        self.top_panel = widgets.VBox(children=[title_ui], layout=self.layout)

    def prev_button_clicked(self, event):
        raise NotImplementedError

    def next_button_clicked(self, event):
        raise NotImplementedError

    def __bottom_panel(self):
        list_ui = []
        if self.prev_button:
            self.prev_button_ui = widgets.Button(
                description="<< Previous Step",
                tooltip="Click to move to previous step",
                button_style="success",
                disabled=False,
                layout=widgets.Layout(width="20%"),
            )
            self.prev_button_ui.on_click(self.prev_button_clicked)
            list_ui.append(self.prev_button_ui)

        self.current_state_label_ui = widgets.Label(
            "         ", layout=widgets.Layout(width="70%")
        )
        list_ui.append(self.current_state_label_ui)

        if self.next_button:
            self.next_button_ui = widgets.Button(
                description="Next Step>>",
                tooltip="Click to move to next step",
                button_style="warning",
                disabled=True,
                layout=widgets.Layout(width="20%"),
            )
            list_ui.append(self.next_button_ui)
            self.next_button_ui.on_click(self.next_button_clicked)

        self.bottom_panel = widgets.HBox(list_ui)

    def __file_selector(self):
        self.file_selector = myFileSelectorPanel(
            instruction="", start_dir=self.working_dir, multiple=True, current_ui=self
        )

    def show(self):
        display(self.top_panel)
        display(self.bottom_panel)
        self.file_selector.show()

    def remove(self):
        return
        close(self.top_panel)
        close(self.bottom_panel)
        self.file_selector.remove()

    def nextStep(self):
        raise NotImplementedError


class WizardPanel:
    label_layout = Layout(
        border="1px lighgray solide", height="35px", padding="8px", width="300px"
    )
    sample_panel = None

    def __init__(self, sample_panel=None):
        display(widgets.Label("Selection of All Input Files", layout=self.label_layout))

        self.sample_panel = sample_panel
        self.sample_panel.show()
        return


# class SampleSelectionPanel(Panel):
#     files = None
#     o_norm = None

#     def __init__(self, prev_button=False, next_button=True, working_dir="", top_object=None):
#         super(SampleSelectionPanel, self).__init__(
#             prev_button=prev_button, next_button=next_button, working_dir=working_dir, top_object=top_object
#         )

#     # def __init__(self, prev_button=False, next_button=True, working_dir='', top_object=None, gamma_coefficient=None):
#     #     super(SampleSelectionPanel, self).__init__(prev_button=prev_button,
#     #                                                next_button=next_button,
#     #                                                working_dir=working_dir,
#     #                                                top_object=top_object,
#     #                                                gamma_coefficient=gamma_coefficient)

#     # def next_button_clicked(self, event):
#     #     self.remove()
#     #     _panel = OBSelectionPanel(working_dir=self.working_dir, top_object=self)
#     #     _panel.init_ui(files=self.files)
#     #     _panel.show()


# class OBSelectionPanel(Panel):
#     def __init__(self, working_dir="", top_object=None):
#         super(OBSelectionPanel, self).__init__(
#             prev_button=True, state="ob", working_dir=working_dir, top_object=top_object
#         )

#     def next_button_clicked(self, event):
#         self.remove()
#         _panel = DFSelectionPanel(working_dir=self.working_dir, top_object=self.top_object)
#         _panel.init_ui(files=self.files)
#         _panel.show()

#     def prev_button_clicked(self, event):
#         self.remove()
#         _panel = SampleSelectionPanel(working_dir=self.working_dir, top_object=self.top_object)
#         _panel.init_ui(files=self.files)
#         _panel.show()


# class DFSelectionPanel(Panel):
#     def __init__(self, working_dir="", top_object=None):
#         self.working_dir = working_dir
#         super(DFSelectionPanel, self).__init__(
#             prev_button=True, next_button=True, state="df", working_dir=working_dir, top_object=top_object
#         )

#     def prev_button_clicked(self, event):
#         self.remove()
#         _panel = OBSelectionPanel(working_dir=self.working_dir, top_object=self.top_object)
#         _panel.init_ui(files=self.files)
#         _panel.show()

#     def next_button_clicked(self, event):
#         self.remove()
#         o_norm_handler = NormalizationHandler(
#             files=self.files, working_dir=self.working_dir, gamma_threshold=self.gamma_threshold
#         )
#         o_norm_handler.load_data()
#         self.top_object.o_norm_handler = o_norm_handler
#         self.top_object.o_norm = o_norm_handler.o_norm
