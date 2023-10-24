import os
import h5py


class Hdf5Handler:

    def __init__(self, parent=None):
        self.parent = parent

    def load(self, filename=None):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"{filename} does not exist!")

        self.filename = filename
        self.import_hdf5()

    def import_hdf5(self):
        f = h5py.File(self.filename, 'r')
        entry = f['entry']

        # integrated image
        self.parent.integrated_normalized_radiographs = entry['integrated normalized radiographs']['2D array'][:]

        # metadata
        self.parent.metadata = {}
        list_key = ['detector_offset', 'distance_source_detector', 'hkl_value', 'material_name']
        for _key in list_key:
            self.parent.metadata[_key] = entry['metadata'][_key][()].decode('utf-8')
        self.parent.metadata['d0'] = entry['metadata']['d0'][()]

        # strain mapping
        self.parent.strain_mapping = {}
        for _key in entry['strain mapping'].keys():
            self.parent.strain_mapping[_key] = {'val': entry['strain mapping'][_key]['val'][()],
                                                'err': entry['strain mapping'][_key]['err'][()],
                                                }

        # bin
        self.parent.bin = {}
        list_row = []
        list_column = []
        for _key in entry['strain mapping'].keys():
            key_entry = entry['strain mapping'][_key]
            _key_dict = {'x0': key_entry['bin coordinates']['x0'][()],
                         'x1': key_entry['bin coordinates']['x1'][()],
                         'y0': key_entry['bin coordinates']['y0'][()],
                         'y1': key_entry['bin coordinates']['y1'][()],
                         'row_index': entry['fitting']['kropff'][_key]['fitted']['row_index'][()],
                         'column_index': entry['fitting']['kropff'][_key]['fitted']['column_index'][()],
                         }

            list_row.append(entry['fitting']['kropff'][_key]['fitted']['row_index'][()])
            list_column.append(entry['fitting']['kropff'][_key]['fitted']['column_index'][()])
            self.parent.bin[_key] = _key_dict

        set_list_row = set(list(list_row))
        set_list_column = set(list(list_column))

        self.parent.nbr_row = len(set_list_row)
        self.parent.nbr_column = len(set_list_column)

        self.parent.d = {}
        kropff_entry = entry['fitting']['kropff']
        for _key in kropff_entry.keys():
            self.parent.d[_key] = kropff_entry[_key]['fitted']['d']['val'][()]

        self.parent.lambda_hkl = {}
        for _key in kropff_entry.keys():
            self.parent.lambda_hkl[_key] = kropff_entry[_key]['fitted']['lambda_hkl']['val'][()]
