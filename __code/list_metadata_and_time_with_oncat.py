from __code import oncat
from IPython.core.display import display, HTML
from ipywidgets import widgets


class ListMetadata:

    def __init__(self, system=None, file=''):
        self.instrument = system.System.get_instrument_selected()
        self.facility = system.System.get_facility_selected()
        self.file = file

        _oncat = oncat.Oncat()
        self.oncat_session = _oncat.authentication()

    def select_metadata(self):
        list_metadata = self.retrieve_list_metadata()

        box = widgets.HBox([widgets.Label("Select Metadata To Retrieve",
                                          layout=widgets.Layout(width='20%')),
                            widgets.SelectMultiple(options=list_metadata,
                                                   layout=widgets.Layout(width='30%',
                                                                         height='80%'))],
                           layout=widgets.Layout(height='400px'))
        select_box = box.children[1]
        display(box)

    def retrieve_list_metadata(self):
        _data = oncat.GetEverything(instrument=self.instrument,
                                         facility=self.facility,
                                         run=self.file,
                                         oncat=self.oncat_session)

        self.data = _data.datafiles
        dict_metadata = self.data.to_dict()
        return dict_metadata.keys()

