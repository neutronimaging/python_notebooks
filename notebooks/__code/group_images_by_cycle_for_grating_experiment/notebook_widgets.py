from ipywidgets import widgets
from IPython.core.display import display, HTML

from __code._utilities.metadata_handler import MetadataHandler
from __code.group_images_by_cycle_for_grating_experiment.get import Get


class NotebookWidgets:

    def __init__(self, parent=None):
        self.parent = parent

    def select_metadata_to_use_for_sorting(self):
        # retrieving list of metadata
        list_metadata = MetadataHandler.get_list_of_metadata(self.parent.list_images[0])
        self.parent.list_metadata = list_metadata

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
        self.parent.search_outer_field.observe(self.parent.search_metadata_outer_edited, names='value')
        search_outer.children[2].on_click(self.parent.reset_search_metadata_outer)

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
        self.parent.list_metadata_outer.observe(self.parent.metadata_outer_selection_changed, names='value')

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
        self.parent.search_inner_field.observe(self.parent.search_metadata_inner_edited, names='value')
        search_inner.children[2].on_click(self.parent.reset_search_metadata_inner)

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
        self.parent.list_metadata_inner.observe(self.parent.metadata_inner_selection_changed, names='value')

        metadata = widgets.HBox([metadata_outer, widgets.Label(" "), metadata_inner])
        display(metadata)

        self.parent.save_key_metadata()
