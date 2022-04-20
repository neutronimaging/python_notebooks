from ipywidgets import widgets
from IPython.core.display import display
import numpy as np

from __code._utilities.metadata_handler import MetadataHandler
from __code.group_images_by_cycle_for_grating_experiment.get import Get
from __code.group_images_by_cycle_for_grating_experiment.event_handler import EventHandler


class NotebookWidgets:

    def __init__(self, parent=None):
        self.parent = parent

    def select_metadata_to_use_for_sorting(self):
        # retrieving list of metadata
        list_metadata = MetadataHandler.get_list_of_metadata(self.parent.list_images[0])
        self.parent.list_metadata = list_metadata
        o_event = EventHandler(parent=self.parent)

        o_get = Get(parent=self.parent)
        metadata_inner_value, metadata_outer_value = o_get.default_metadata_selected()

        select_width = "550px"
        select_height = "300px"

        # metadata_outer
        search_outer = widgets.HBox([widgets.Label("Search:"),
                                     widgets.Text("",
                                                  layout=widgets.Layout(width="150px")),
                                     widgets.Button(description="X",
                                                    button_style='',
                                                    layout=widgets.Layout(width="10px"))
                                     ])
        self.parent.search_outer_field = search_outer.children[1]
        self.parent.search_outer_field.observe(o_event.search_metadata_outer_edited, names='value')
        search_outer.children[2].on_click(o_event.reset_search_metadata_outer)

        result2 = widgets.HBox([widgets.HTML("<u>Metadata Selected</u>:",
                                             layout=widgets.Layout(width="200px")),
                                widgets.Label(metadata_outer_value,
                                              layout=widgets.Layout(width="100%"))])
        self.parent.metadata_outer_selected_label = result2.children[1]

        metadata_outer = widgets.VBox([widgets.HTML("<b>Outer Loop Metadata</b>"),
                                       search_outer,
                                       widgets.Select(options=list_metadata,
                                                      value=metadata_outer_value,
                                                      layout=widgets.Layout(width=select_width,
                                                                            height=select_height)),
                                       result2])
        self.parent.list_metadata_outer = metadata_outer.children[2]
        self.parent.list_metadata_outer.observe(o_event.metadata_outer_selection_changed, names='value')

        # metadata_inner
        search_inner = widgets.HBox([widgets.Label("Search:",
                                                   ),
                                     widgets.Text("",
                                                  layout=widgets.Layout(width="150px")),
                                     widgets.Button(description="X",
                                                    button_style='',
                                                    layout=widgets.Layout(width="10px")
                                                    )])
        self.parent.search_inner_field = search_inner.children[1]
        self.parent.search_inner_field.observe(o_event.search_metadata_inner_edited, names='value')
        search_inner.children[2].on_click(o_event.reset_search_metadata_inner)

        result1 = widgets.HBox([widgets.HTML("<u>Metadata Selected</u>:",
                                             layout=widgets.Layout(width="200px")),
                                widgets.Label(metadata_inner_value,
                                              layout=widgets.Layout(width="100%"))])
        self.parent.metadata_inner_selected_label = result1.children[1]

        metadata_inner = widgets.VBox([widgets.HTML("<b>Inner Loop Metadata</b>"),
                                       search_inner,
                                       widgets.Select(options=list_metadata,
                                                      value=metadata_inner_value,
                                                      layout=widgets.Layout(width=select_width,
                                                                            height=select_height)),
                                       result1])
        self.parent.list_metadata_inner = metadata_inner.children[2]
        self.parent.list_metadata_inner.observe(o_event.metadata_inner_selection_changed, names='value')

        metadata = widgets.HBox([metadata_outer, widgets.Label(" "), metadata_inner])
        display(metadata)

        self.parent.save_key_metadata()

    def display_groups(self):
        o_get = Get(parent=self.parent)
        o_event = EventHandler(parent=self.parent)

        self.parent.group_images()
        nbr_groups = len(self.parent.dictionary_of_groups_sorted.keys())

        # column 1
        group_label = ["Group # {}".format(_index) for _index in np.arange(nbr_groups)]
        self.parent.list_group_label = group_label
        vbox_left = widgets.VBox([widgets.HTML("<b>Select Group</b>:"),
                                  widgets.Select(options=group_label,
                                                 layout=widgets.Layout(width="150px",
                                                                       height="300px"))])
        select_group_ui = vbox_left.children[1]
        select_group_ui.observe(o_event.group_index_changed, 'value')

        # column 2
        vbox_center = widgets.VBox([widgets.HTML("<b>Original file names</b>:"),
                                    widgets.Select(options=o_get.list_of_files_basename_only(0),
                                                   layout=widgets.Layout(width="450px",
                                                                         height="300px"))])

        list_of_files_ui = vbox_center.children[1]
        list_of_files_ui.observe(o_event.list_of_files_changed, 'value')
        self.parent.list_of_files_ui = list_of_files_ui

        # column 3
        vbox_3 = widgets.VBox([widgets.HTML("<b>New Name</b>"),
                               widgets.Select(options=o_get.list_of_new_files_basename_only(0),
                                              layout=widgets.Layout(width="450px",
                                                                    height="300px"))])
        list_of_new_files_ui = vbox_3.children[1]
        list_of_new_files_ui.observe(o_event.list_of_new_files_changed, 'value')
        self.parent.list_of_new_files_ui = list_of_new_files_ui

        # column 4
        vbox_right = widgets.VBox([widgets.Label("Metadata:"),
                                   widgets.Textarea(value="",
                                                    layout=widgets.Layout(width="200px",
                                                                          height="300px"))])
        self.parent.metadata_ui = vbox_right.children[1]

        o_event.list_of_files_changed(value={'new': o_get.list_of_files_basename_only(0)[0]})

        hbox = widgets.HBox([vbox_left, vbox_center, vbox_3, vbox_right])
        display(hbox)

        message = widgets.HTML("<b><font color='blue'>INFO</font></b>: <i>if more than 1 image are in the same "
                               "<b>original file names</b> row, they will be combined using <b>median</b></i>.")
        display(message)

        bottom_hbox = widgets.HBox([widgets.HTML("<b>Images are in</b>:",
                                                 layout=widgets.Layout(width="150px")),
                                    widgets.Label(self.parent.data_path,
                                                  layout=widgets.Layout(width="90%"))])
        self.parent.path_ui = bottom_hbox.children[1]
        display(bottom_hbox)

    def generate_angel_configuration_file(self):

        o_event = EventHandler(parent=self.parent)

        load_previous_excel_ui = widgets.Button(
                description="Use previously created EXCEL File",
                icon="edit",
                layout=widgets.Layout(width="50%",
                                      border="2px solid green")
        )
        load_previous_excel_ui.on_click(o_event.use_excel_file_clicked)

        create_new_excel_ui = widgets.Button(
                description="Create New Excel",
                layout=widgets.Layout(width="50%",
                                      border="2px solid green"),
                icon="file-excel-o"
        )
        create_new_excel_ui.on_click(o_event.create_new_excel_clicked)

        hori_layout = widgets.Layout()
        hori_box = widgets.HBox([load_previous_excel_ui, create_new_excel_ui],
                                layout=hori_layout)
        display(hori_box)

        self.parent.excel_info_widget = widgets.HTML("")
        display(self.parent.excel_info_widget)
