from IPython.core.display import display, HTML
from ipywidgets import widgets
from collections import OrderedDict
import os

from __code import oncat
from __code.file_handler import make_ascii_file


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
        list_files = self.list_of_files
        projection = self.create_projection()
        output_ascii_file_name = ListMetadata.create_output_ascii_name(list_files, output_folder)

        o_metadata_selected = oncat.GetProjection(instrument=self.instrument,
                                                  facility=self.facility,
                                                  list_files=list_files,
                                                  oncat=self.oncat_session,
                                                  projection=projection)
        metadata_selected = o_metadata_selected.datafiles

        name_metadata = self.create_metadata_name_row()
        value_metadata = self.create_metadata_value_rows(list_files, metadata_selected)
        make_ascii_file(metadata=name_metadata,
                        data=value_metadata,
                        output_file_name=output_ascii_file_name,
                        dim='1d')
        display(HTML('<span style="font-size: 20px; color:Green">File ' + output_ascii_file_name +
                     ' has been created with success!</span>'))

    def create_metadata_value_rows(self, list_files, metadata_selected):
        value_metadata = []
        for _file in list_files:
            time_stamp = self.unify_timestamp_format(metadata_selected[_file]['ingested'])
            _metadata = []
            for _metadata_name in self.get_list_metadata_selected():
                _metadata.append(str(metadata_selected[_file]['metadata'][_metadata_name]))
            row_string = "{}, {}, {}".format(_file,
                                             time_stamp,
                                             ", ".join(_metadata))
            value_metadata.append(row_string)
        return value_metadata

    def unify_timestamp_format(self, old_timestamp):
        o_time = TimestampFormatter(timesdtamp=old_timestamp)
        new_timestamp = o_time.format_oncat_timestamp()
        return new_timestamp

    def create_metadata_name_row(self):
        name_metadata = ["#filename, timestamp_user_format, " + ", ".join(self.get_list_metadata_selected())]
        return name_metadata

    @staticmethod
    def create_output_ascii_name(list_files, output_folder):
        output_ascii_file_name = os.path.abspath(os.path.basename(os.path.dirname(list_files[0]))) + \
                                 '_metadata_report.txt'
        return os.path.join(output_folder, output_ascii_file_name)

    def create_projection(self):
        list_metadata_selected = self.get_list_metadata_selected()
        projection = []
        for _metadata_selected in list_metadata_selected:
            projection.append('metadata.{}'.format(_metadata_selected.strip()))
        return projection

    def get_list_metadata_selected(self):
        list_metadata_selected = []
        for metadata_selected in self.select_box.value:
            metadata_name = metadata_selected.split("\t -->")
            list_metadata_selected.append(metadata_name[0].strip())
        return list_metadata_selected



