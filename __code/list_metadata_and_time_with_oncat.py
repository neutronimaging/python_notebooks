from __code import oncat
from IPython.core.display import display, HTML
from ipywidgets import widgets
from collections import OrderedDict


class ListMetadata:

    instrument = 'CG1D'
    facility = 'HFIR'
    first_file = ''
    list_of_files = []
    list_metadata = []

    def __init__(self):
        _oncat = oncat.Oncat()
        self.oncat_session = _oncat.authentication()

        if self.oncat_session is None:
            display(HTML('<span style="font-size: 20px; color:red">Wrong Password!</span>'))
        else:
            display(HTML('<span style="font-size: 20px; color:green">Valid Password!</span>'))

    def select_metadata(self, system=None, list_of_files=[]):
        if not list_of_files:
            display(HTML('<span style="font-size: 20px; color:red">You need to select at least one file!</span>'))
            return

        if not system:
            return

        self.instrument = system.System.get_instrument_selected()
        self.facility = system.System.get_facility_selected()
        self.list_of_files = list_of_files
        self.first_file = list_of_files[0]
        self.list_metadata_with_examples = self.retrieve_list_metadata_with_examples()

        display(HTML('<span style="font-size: 20px; color:blue">CTRL + Click to select multiple rows!</span>'))
        box1 = widgets.HBox([widgets.Label("Select Metadata To Retrieve",
                                          layout=widgets.Layout(width='20%')),
                            widgets.SelectMultiple(options=self.list_metadata_with_examples,
                                                   layout=widgets.Layout(width='80%',
                                                                         height='100%'))],
                           layout=widgets.Layout(height='500px'))
        self.select_box = box1.children[1]
        display(box1)

    def retrieve_list_metadata_with_examples(self):
        list_metadata = self.retrieve_list_metadata()
        raw_data = self.raw_oncat_metadata
        list_metadata_with_examples = ListMetadata.format_list_metadata_with_examples(list_metadata, raw_data)
        return list_metadata_with_examples

    @staticmethod
    def format_list_metadata_with_examples(list_metadata, raw_data):
        list_metadata_with_examples = []
        for _key in list_metadata:
            _key_with_value = "{:>40} \t --> \texample: {}".format(_key,
                                                                   raw_data[_key])
            list_metadata_with_examples.append(_key_with_value)
        return list_metadata_with_examples

    def retrieve_list_metadata(self):
        _data = oncat.GetEverything(instrument=self.instrument,
                                         facility=self.facility,
                                         run=self.first_file,
                                         oncat=self.oncat_session)

        self.raw_oncat_data = _data.datafiles
        sorted_dict_metadata = self.create_sorted_dict_metadata(_data)
        return sorted_dict_metadata.keys()

    def create_sorted_dict_metadata(self, _data):
        _data = _data.datafiles['metadata']
        dict_metadata = _data.to_dict()
        keys_sorted = sorted(dict_metadata.keys())
        sorted_dict_metadata = OrderedDict()
        for _key in keys_sorted:
            sorted_dict_metadata[_key] = dict_metadata[_key]
        self.raw_oncat_metadata = sorted_dict_metadata
        return sorted_dict_metadata

    def export_ascii(self, output_folder):
        list_metadata_selected = self.get_list_metadata_selected()
        list_files = self.list_of_files

        




    def get_list_metadata_selected(self):
        list_metadata_selected = []
        for metadata_selected in self.select_box.value:
            metadata_name = metadata_selected.split("\t -->")
            list_metadata_selected.append(metadata_name[0])

        return list_metadata_selected



