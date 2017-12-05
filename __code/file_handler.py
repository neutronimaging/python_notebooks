import os
from astropy.io import fits
import numpy as np
import pickle
import shutil
from PIL import Image
import glob
from collections import Counter
import re

from ipywidgets.widgets import interact
from ipywidgets import widgets
from IPython.core.display import display, HTML

import NeuNorm
from NeuNorm.normalization import Normalization


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
    
def make_ascii_file(metadata=[], data=[], output_file_name='', dim='2d'):
    f = open(output_file_name, 'w')
    for _meta in metadata:
        _line = _meta + "\n"
        f.write(_line)
        
    for _data in data:
        if dim == '2d':
            _str_data = [str(_value) for _value in _data]
            _line = ",".join(_str_data) + "\n"
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

def retrieve_list_of_most_dominand_extension_from_folder(folder=''):
    '''
    This will return the list of files from the most dominand file extension found in the folder
    as well as the most dominand extension used
    '''
    
    list_of_input_files = glob.glob(os.path.join(folder, '*'))
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

    list_of_input_files = glob.glob(os.path.join(folder, '*' + dominand_extension))

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






   