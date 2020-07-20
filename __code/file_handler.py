import os
from pathlib import Path
import pandas as pd
from astropy.io import fits
import numpy as np
import pickle
import shutil
from PIL import Image
import glob
from collections import Counter, namedtuple, OrderedDict
import re
import datetime

from ipywidgets import widgets
from IPython.core.display import display, HTML

from __code.metadata_handler import MetadataHandler


def force_file_extension(filename, ext='.txt'):
    """this method check the name of the file and makes sure the extension is the one we are requesting"""
    [base, extension] = os.path.splitext(filename)

    # name of file does not have any extension
    if extension == "":
        return filename + ext

    # name of file has the right extension
    if extension == ext:
        return filename

    # name of file has the wrong extension
    else:
        return base + ext


def test_image(file_name, threshold=5000):
    # check size of image and return False if size is below threshold 
    statinfo = os.stat(file_name)
    if statinfo.st_size < threshold:
        return False
    return True


def load_data(filenames='', folder='', showing_progress=False):
    '''
    load the various file_name format
    '''
    if folder:
        list_files = glob.glob(folder + '/*.*')
        stack = []

        if showing_progress:
            w = widgets.IntProgress()
            w.max = len(list_files)
            display(w)


        for _index, _file in enumerate(list_files):
            _data = load_data(filenames=_file)
            stack.append(_data)

            if showing_progress:
                w.value = _index+1

        return stack

    elif isinstance(filenames, str):
        data_type = get_data_type(filenames)
        if data_type == '.fits':
            hdulist = fits.open(filenames, ignore_missing_end=True)
            hdu = hdulist[0]
            _image = np.asarray(hdu.data)
            hdulist.close()
            return _image
        elif (data_type == '.tiff') or (data_type == '.tif'):
            _image = Image.open(filenames)
            return np.array(_image)
        else:
            return []
        
    else: # list of filenames
        
        list_files = filenames
    
        stack = []

        if showing_progress:
            w = widgets.IntProgress()
            w.max = len(list_files)
            display(w)


        for _index, _file in enumerate(list_files):
            _data = load_data(filenames=_file)
            stack.append(_data)

            if showing_progress:
                w.value = _index+1

        return stack

    
def save_data(data=[], filename=''):
    data_type = get_data_type(filename)
    if data_type == '.fits':
        make_fits(data=data, filename=filename)
    elif (data_type == '.tiff') or (data_type == '.tif'):
        make_tiff(data=data, filename=filename)


def get_file_extension(filename):
    '''retrieve the file extension of the filename and make sure
    we only keep the extension value and not the "dot" before it'''
    full_extension = get_data_type(filename)
    return full_extension[1:]


def get_data_type(file_name):
    '''
    using the file name extension, will return the type of the data
    
    Arguments:
        full file name
        
    Returns:
        file extension    ex:.tif, .fits
    '''
    filename, file_extension = os.path.splitext(file_name)
    return file_extension.strip()


def save_file(folder='', base_file_name='', suffix='', dictionary={}):
    if folder == '':
        return
    
    output_file = folder + base_file_name + '_time_dictionary.dat'
    pickle.dump(dictionary, open(output_file, "wb"))
    
    return output_file


def make_tiff(data=[], filename=''):
    new_image = Image.fromarray(data)
    new_image.save(filename)


def make_fits(data=[], filename=''):
    fits.writeto(filename, data, clobber=True)


def make_folder(folder_name):
    if not (os.path.exists(folder_name)):
        os.makedirs(folder_name)


def make_or_reset_folder(folder_name):
    if os.path.exists(folder_name):
         shutil.rmtree(folder_name)
    os.makedirs(folder_name)         


def copy_files_to_folder(list_files=[], output_folder=""):
    for _file in list_files:
        shutil.copy(_file, output_folder)


def copy_and_rename_files_to_folder(list_files=[], new_list_files_names=[], output_folder=''):
    for _index_file, _original_file in enumerate(list_files):
        _new_file = os.path.join(output_folder, new_list_files_names[_index_file])
        shutil.copy(_original_file, _new_file)


def remove_SummedImg_from_list(list_files):
    base_name_and_extension = os.path.basename(list_files[0])
    dir_name = os.path.dirname(list_files[0])
    [base_name, _] = os.path.splitext(base_name_and_extension)
    base_base_name_array = base_name.split('_')
    name = '_'.join(base_base_name_array[0:-1])
    index = base_base_name_array[-1]
    file_to_remove = os.path.join(dir_name, name + '_SummedImg.fits')
    list_files_cleaned = []
    for _file in list_files:
        if _file == file_to_remove:
            continue
        list_files_cleaned.append(_file)
    return list_files_cleaned


def make_ascii_file(metadata=[], data=[], output_file_name='', dim='2d', sep=','):
    f = open(output_file_name, 'w')
    for _meta in metadata:
        _line = _meta + "\n"
        f.write(_line)
        
    for _data in data:
        if dim == '2d':
            _str_data = [str(_value) for _value in _data]
            _line = sep.join(_str_data) + "\n"
        else:
            _line = str(_data) + '\n'
        f.write(_line)
       
    f.close()


def make_ascii_file_from_string(text="", filename=''):
    with open(filename, 'w') as f:
        f.write(text)


def read_ascii(filename=''):
    '''return contain of an ascii file'''
    f = open(filename, 'r')
    text = f.read()
    f.close()
    return text


def retrieve_metadata_from_dsc_file(filename=''):
    text = read_ascii(filename=filename)
    splitted_text = text.split('\n')
    metadata = {}
    metadata['acquisition_time'] = splitted_text[9]
    metadata['user_format'] = splitted_text[-3]
    metadata['os_format'] = splitted_text[-7]

    return metadata


def retrieve_metadata_from_dsc_list_files(list_files=[]):
    w = widgets.IntProgress()
    w.max = len(list_files)
    display(w)

    metadata = {}
    for _index, _file in enumerate(list_files):
        metadata[os.path.basename(_file)] = retrieve_metadata_from_dsc_file(filename=_file)
        w.value = _index+1

    return metadata


def retrieve_list_of_most_dominand_extension_from_folder(folder='', files=[]):
    '''
    This will return the list of files from the most dominand file extension found in the folder
    as well as the most dominand extension used
    '''

    if folder:
        list_of_input_files = glob.glob(os.path.join(folder, '*'))
    else:
        list_of_input_files = files

    list_of_input_files.sort()
    list_of_base_name = [os.path.basename(_file) for _file in list_of_input_files]

    # work with the largest common file extension from the folder selected

    counter_extension = Counter()
    for _file in list_of_base_name:
        [_base, _ext] = os.path.splitext(_file)
        counter_extension[_ext] += 1

    dominand_extension = ''
    dominand_number = 0
    for _key in counter_extension.keys():
        if counter_extension[_key] > dominand_number:
            dominand_extension = _key
            dominand_number = counter_extension[_key]

    list_of_input_files = glob.glob(os.path.join(folder, '*' + dominand_extension))
    list_of_input_files.sort()

    list_of_input_files = [os.path.abspath(_file) for _file in list_of_input_files]

    return [list_of_input_files, dominand_extension]


def remove_file_from_list(list_files=[], regular_expression=''):
    '''
    This method will look through the list of files provided and will try
    to find, using regular expresision, the name of the file that does match
    the 're' argument passed. If found, the list is returned without that file

    Parameters:
    ===========
    list_files: list
    re: string (regular expression)
      example: re = '*_SummedImg.fits'

    Returns:
    ========
    list
    '''
    if regular_expression == '':
        return list_files

    p = re.compile(regular_expression)
    for _index, _file in enumerate(list_files):
        if p.match(_file):
            list_files.pop(_index)

    return list_files


def convert_to_human_readable_format(timestamp):
    """Convert the unix time stamp into a human readable time format

    Format return will look like  "2018-01-29 10:30:25"
    """
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def _convert_epics_timestamp_to_rfc3339_timestamp(epics_timestamp):
    # TIFF files from CG1D have EPICS timestamps.  From the Controls
    # Wiki:
    #
    # > EPICS timestamp. The timestamp is made when the image is read
    # > out from the camera. Format is seconds.nanoseconds since Jan 1st
    # > 00:00 1990.

    # Convert seconds since "EPICS epoch" to seconds since the "UNIX
    # epoch" so that Python can understand it.  I got the offset by
    # calculating the number of seconds between the two epochs at
    # https://www.epochconverter.com/
    #EPOCH_OFFSET = 631152000
    EPOCH_OFFSET = 0
    unix_epoch_timestamp = EPOCH_OFFSET + epics_timestamp
    return unix_epoch_timestamp


def retrieve_time_stamp(list_images):
    [_, ext] = os.path.splitext(list_images[0])
    if ext.lower() in ['.tiff', '.tif']:
        ext = 'tif'
    elif ext.lower() == '.fits':
        ext = 'fits'
    else:
        raise ValueError

    box = widgets.HBox([widgets.Label("Retrieving Time Stamp",
                                      layout=widgets.Layout(width='20%')),
                        widgets.IntProgress(min=0,
                                            max=len(list_images),
                                            value=0,
                                            layout=widgets.Layout(width='50%'))
                        ])
    progress_bar = box.children[1]
    display(box)

    list_time_stamp = []
    list_time_stamp_user_format = []
    for _index, _file in enumerate(list_images):
        _time_stamp = MetadataHandler.get_time_stamp(file_name=_file, ext=ext)
        _time_stamp = _convert_epics_timestamp_to_rfc3339_timestamp(_time_stamp)
        list_time_stamp.append(_time_stamp)

        _user_format = convert_to_human_readable_format(_time_stamp)
        list_time_stamp_user_format.append(_user_format)
        progress_bar.value = _index + 1

    box.close()

    return {'list_images': list_images,
            'list_time_stamp': list_time_stamp,
            'list_time_stamp_user_format': list_time_stamp_user_format}


def get_list_of_files(folder="", extension='tiff'):
    list_files = glob.glob(os.path.join(folder, "*.{}".format(extension)))
    list_files.sort()
    return list_files


def get_list_of_all_files_in_subfolders(folder="", extensions=['tiff','tif']):
    absolute_path_folder = os.path.abspath(folder)
    list_files = []
    for path, _, files in os.walk(absolute_path_folder):
        for name in files:
            if get_file_extension(name) in extensions:
                list_files.append(os.path.join(path, name))
    return list_files


def read_bragg_edge_fitting_ascii_format(full_file_name):
    if not Path(full_file_name).exists():
        raise FileNotFoundError

    metadata = {'detector_offset': '',
                'distance_detector_sample': '',
                }
    metadata_column = OrderedDict()
    line_number = 1
    col_label = ['index', 'tof', 'lambda']
    with open(full_file_name, 'r') as f:
        for line in f:
            if "#base folder: " in line:
                metadata['base_folder'] = line.split("#base folder: ")[1].strip()
                line_number += 1
                continue
            if "#fitting peak range in file index:" in line:
                regular = r"^#fitting peak range in file index: \[(?P<left_index>\d+), (?P<right_index>\d+)\]$"
                m = re.search(regular, line.strip())
                if m:
                    metadata['bragg_edge_range'] = [np.int(m.group('left_index')),
                                                    np.int(m.group('right_index'))]
                else:
                    metadata['bragg_edge_range'] = [None, None]
                line_number += 1
                continue
            if "#distance detector-sample: " in line:
                metadata['distance_detector_sample'] = line.split("#distance detector-sample: ")[1].strip()
                line_number += 1
                continue
            if "#detector offset: " in line:
                metadata['detector_offset'] = line.split("#detector offset: ")[1].strip()
                line_number += 1
                continue
            if "#fitting procedure started: " in line:
                result = True if line.split("#fitting procedure started: ")[1].strip() == 'True' else False
                metadata['fitting_procedure_started'] = result
                line_number += 1
                continue
            if "#kropff " in line:
                regular = r"^#kropff (?P<type>\w+) selection range: \[(?P<left_index>\d+), " \
                          r"(?P<right_index>\d+)\]$"
                m = re.search(regular, line.strip())
                if m:
                    metadata['kropff_{}'.format(m.group('type'))] = [np.int(m.group('left_index')),
                                                                     np.int(m.group('right_index'))]
                line_number += 1
                continue
            if "#fitting algorithm selected: " in line:
                metadata['fitting_algorithm_selected'] = line.split('#fitting algorithm selected: ')[1].strip()
                line_number += 1
                continue
            if "#column " in line:
                regular = r"^#column (?P<column_index>\d+) -> x0:(?P<x0>\d+), y0:(?P<y0>\d+), width:(?P<width>\d+), " \
                          r"height:(?P<height>\d+), kropff: a0:(?P<a0>-{0,1}\d+.\d+|None), b0:(?P<b0>-{0,1}\d+.\d+|None), a0_error:(" \
                          r"?P<a0_error>\d+.\d+|None), b0_error:(?P<b0_error>\d+.\d+|None), ahkl:(?P<ahkl>-{0,1}\d+.\d+|None), bhkl:(?P<bhkl>-{0,1}\d+.\d+|None), " \
                          r"ahkl_error:(?P<ahkl_error>\d+.\d+|None), bhkl_error:(?P<bhkl_error>\d+.\d+|None), lambdahkl:(" \
                          r"?P<lambdahkl>-{0,1}\d+.\d+|None), tau:(?P<tau>-{0,1}\d+.\d+|None), sigma:(?P<sigma>-{0,1}\d+.\d+|None), lambdahkl_error:(" \
                          r"?P<lambdahkl_error>\d+.\d+|None), tau_error:(?P<tau_error>\d+.\d+|None), sigma_error:(?P<sigma_error>\d+.\d+|None)$"

                m = re.search(regular, line.strip())
                if m:
                    metadata_column[m.group('column_index').strip()] = {'x0': m.group('x0'),
                                                                        'y0': m.group('y0'),
                                                                        'width': m.group('width'),
                                                                        'height': m.group('height'),
                                                                        'a0': m.group('a0'),
                                                                        'b0': m.group('b0'),
                                                                        'a0_error': m.group('a0_error'),
                                                                        'b0_error': m.group('b0_error'),
                                                                        'ahkl': m.group('ahkl'),
                                                                        'bhkl': m.group('bhkl'),
                                                                        'ahkl_error': m.group('ahkl_error'),
                                                                        'bhkl_error': m.group('bhkl_error'),
                                                                        'lambdahkl': m.group('lambdahkl'),
                                                                        'tau': m.group('tau'),
                                                                        'sigma': m.group('sigma'),
                                                                        'lambdahkl_error': m.group('lambdahkl_error'),
                                                                        'tau_error': m.group('tau_error'),
                                                                        'sigma_error': m.group('sigma_error')}
                    col_label.append(m.group("column_index"))
                line_number += 1
                continue
        metadata['columns'] = metadata_column

    pd_data = pd.read_csv(full_file_name, skiprows=line_number, header=0, names=col_label)
    return {'data': pd_data, 'metadata': metadata}

class ListMostDominantExtension(object):
    Result = namedtuple('Result', ('list_files', 'ext', 'uniqueness'))

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def get_list_of_files(self):
        list_of_input_files = glob.glob(os.path.join(self.working_dir, '*'))
        list_of_input_files.sort()
        self.list_of_base_name = [os.path.basename(_file) for _file in list_of_input_files]

    def get_counter_of_extension(self):
        counter_extension = Counter()
        for _file in self.list_of_base_name:
            [_base, _ext] = os.path.splitext(_file)
            counter_extension[_ext] += 1
        self.counter_extension = counter_extension

    def get_dominant_extension(self):
        dominant_extension = ''
        dominant_number = 0
        list_of_number_of_ext = []
        for _key in self.counter_extension.keys():
            list_of_number_of_ext.append(self.counter_extension[_key])
            if self.counter_extension[_key] > dominant_number:
                dominant_extension = _key
                dominant_number = self.counter_extension[_key]

        self.dominant_number = dominant_number
        self.dominant_extension = dominant_extension
        self.list_of_number_of_ext = list_of_number_of_ext

    def check_uniqueness_of_dominand_extension(self):
        # check if there are several ext with the same max number
        indices = [i for i, x in enumerate(self.list_of_number_of_ext) if x == self.dominant_number]
        if len(indices) > 1:  # found several majority ext
            self.uniqueness = False
        else:
            self.uniqueness = True

    def calculate(self):
        self.get_list_of_files()
        self.get_counter_of_extension()
        self.get_dominant_extension()
        self.check_uniqueness_of_dominand_extension()
        self.retrieve_parameters()

    def retrieve_parameters(self):
        if self.uniqueness:
            list_of_input_files = glob.glob(os.path.join(self.working_dir, '*' + self.dominant_extension))
            list_of_input_files.sort()

            self.result = self.Result(list_files=list_of_input_files,
                                      ext=self.dominant_extension,
                                      uniqueness=True)

        else:

            list_of_maj_ext = [_ext for _ext in self.counter_extension.keys() if
                               self.counter_extension[_ext] == self.dominant_number]

            box = widgets.HBox([widgets.Label("Select Extension to work with",
                                              layout=widgets.Layout(width='20%')),
                                widgets.Dropdown(options=list_of_maj_ext,
                                                 layout=widgets.Layout(width='20%'),
                                                 value=list_of_maj_ext[0])])
            display(box)
            self.dropdown_ui = box.children[1]

    def get_files_of_selected_ext(self):
        if self.uniqueness:
            return self.result

        else:
            _ext_selected = self.dropdown_ui.value
            list_of_input_files = glob.glob(os.path.join(self.working_dir, '*' + _ext_selected))
            list_of_input_files.sort()

            return self.Result(list_files=list_of_input_files,
                               ext=self.dominant_extension,
                               uniqueness=True)
