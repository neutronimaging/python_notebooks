import numpy as np
import os
import re
import shutil
from configparser import RawConfigParser
#import glob
import itertools
from shutil import copyfile

#from ipywidgets.widgets import interact
from ipywidgets import widgets
from IPython.core.display import display, HTML


def calculate_file_temperature(left_T=-1, right_T=-1, left_time=-1, right_time=-1, file_time = -1):
    coeff = (float(right_T) - float(left_T)) / (float(right_time) - float(left_time))
    part1 = coeff * (float(file_time) - float(left_time))
    return part1 + float(left_T)

def get_first_temperature_and_index_value(index=-1, data_array=[], direction='left'):
    if direction == 'left':
        coeff = -1
    else:
        coeff = 1

    while (np.isnan(data_array[index])):
        index += coeff
    return [data_array[index], index]

def extract_temperature(index=-1, temperature_array=[], time_stamp_array=[]):
    
    [left_T, left_index] = get_first_temperature_and_index_value(index=index, data_array=temperature_array, direction='left')
    [right_T, right_index] = get_first_temperature_and_index_value(index=index, data_array=temperature_array, direction='right')
    
    left_time = time_stamp_array[left_index]
    right_time = time_stamp_array[right_index]
    
    file_time = time_stamp_array[index]

    file_temperature = calculate_file_temperature(left_T = left_T, right_T = right_T, 
                                                 left_time = left_time, right_time = right_time,
                                                 file_time = file_time)

    return file_temperature

def retrieve_T_from_file_vs_temperature_array(file_name='', file_array=[], temperature_array=[]):
    index = file_array.index(file_name)
    return temperature_array[index]

def make_output_file_name(bin_number=-1, index=-1, algorithm='mean'):
    '''
    takes the bin number and the algorithm name to create the output file name 
    
    Paramters:
        * bin_number: index of bin
        * index: index of file in folder
        * algorithm: (optional) default value 'mean'. Name of algorithm used to bin data
            will be used in the new output file name
            
    Return:
        * string file name of the output file
        
    Example:
        bin_number = 3
        index = 2
        algorithm = "mean"
        
        will return  'bin#3_0002_mean.fits
    
    '''
    
    ext = '.fits'
    list_output_file_name = []
    _output_file_name = "bin#{:03d}_{:04d}_{}.fits".format(bin_number, index, algorithm)
    return _output_file_name

def keep_folder_name(image):
    image_array = image.split('_')
    return image_array[0]

def is_extension(filename='', ext='.fits'):
    _ext = os.path.splitext(filename)[1]
    if _ext == ext:
        return True
    else:
        return False
    
def index_first_boolean(result, boolean=True):
    for _index, _value in enumerate(result):
        if _value == boolean:
            return _index
        
def index_last_boolean(result, boolean=True):
    for _index, _value in reversed(list(enumerate(result))):
        if _value == boolean:
            return _index
        
def find_index_of_value_in_array(array=[], value=-1, index_type='le'):
    '''
    index_type is either 'le' or 'ge'
    '''
    if index_type == 'le':
        result = x_axis < value
        return index_first_boolean(result, False)
    else:
        result = x_axis > value
        return index_last_boolean(result, False)
    
def make_user_friendly_list_of_bins(full_list_of_bins):
    return [os.path.basename(_file) for _file in full_list_of_bins]
        
    
def get_ipts():
    current_folder = os.getcwd()
    parent_folder = os.path.basename(current_folder)

    result = re.search('IPTS_(\d+)', parent_folder)
    if result:
        ipts = result.group(1)
    else:
        ipts = ''
        
    return ipts
    
def get_working_dir(ipts='', debugging=False):
    '''
    if there is an ipts argument passed in, the working dir will be '/HFIR/CG1DImaging/IPTS-{}'.format(ipts)
    if ipts is empty: program will look if there is a 'working_dir' argument in the 'main_session' of the config file
    '~/.notebooks_config.cfg', otherwise will return the current folder location
    '''
    if ipts:
        if debugging:
            _path = '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS_{}'.format(ipts)
        else:
            _path = '/HFIR/CG1DImaging/IPTS-{}/'.format(ipts)
            print(_path)
        if os.path.exists(_path):
            return _path

    config_path = os.path.join(os.path.expanduser('~/'), '.notebooks_config.cfg')
    if os.path.exists(config_path):
        parser = RawConfigParser()
        parser.read(config_path)
        try:
            working_dir = parser.get('main_session', 'working_dir')
        except:
            working_dir = './'
    else:
        working_dir = './'

    return working_dir

def make_dir(dir='', overwrite=True):
    if dir== '':
        return
    
    if overwrite:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.mkdir(dir)
    else:
        if not (os.path.exists(dir)):
            os.mkdir(dir)

def format_file_index(filename='', number_of_digits=4):
    '''
    This function take a file name that may look like this /Users/my_user/folder/description_1.tif
    and will format it to make sure the prefix has a fix number of digit. If number of digit is 4,
    the file name will be now /Users/my_user/folder/description_0001.tif

    Parameters:
    ===========
    filename: string. name of file
    number_of_digits: default is 4. int. number of digit to add to number at the end

    Returns:
    ========
    new file name formatted
    '''
    _basename = os.path.basename(filename)
    [_base, _ext] = os.path.splitext(_basename)
    _base_slitted = _base.split('_')
    _number = np.int(_base_slitted[-1])

    return ''

def get_n_random_element(input_list=[], n=1):
    '''
    will return a list of n element taken from the input array called input_list
    '''
    n_random = np.random.randint(0, len(input_list)-1, n)
    new_list = [input_list[_index] for _index in n_random]
    return new_list

def rename_files(dict_old_new_names={}, new_output_folder=''):
    make_dir(dir=new_output_folder)

    nbr_files = len(dict_old_new_names.keys())
    w1 = widgets.IntProgress()
    w1.max = nbr_files
    display(w1)

    # create new images
    for _index, _old_name in enumerate(dict_old_new_names.keys()):
        _new_name = os.path.join(new_output_folder, dict_old_new_names[_old_name])
        os.rename(_old_name, _new_name)
        w1.value = _index + 1

def copy_files(dict_old_new_names={}, new_output_folder=''):
    make_dir(dir=new_output_folder)

    nbr_files = len(dict_old_new_names.keys())
    w1 = widgets.IntProgress()
    w1.max = nbr_files
    display(w1)

    # create new images
    for _index, _old_name in enumerate(dict_old_new_names.keys()):
        _new_name = os.path.join(new_output_folder, dict_old_new_names[_old_name])
        copyfile(_old_name, _new_name)
        w1.value = _index + 1


class ListRunsParser(object):
    """
    will clean up the current_list_of_runs with the new added runs
    ex: [1,2,3,4,7] -> 1:4,7
    if a new run is already in the list of runs, it will then be removed from the list
    ex: [1,2,3,4] with new run [1] -> 2:4
    """

    list_current_runs = []  # ['1','10','2','30','4']
    int_list_current_runs = []  # [1, 2, 4, 10, 30]

    def __init__(self, current_runs=''):
        if current_runs:
            self.make_discrete_list_of_runs(str_current_runs=current_runs)

    def make_discrete_list_of_runs(self, str_current_runs=''):
        spans = (el.partition(':')[::2] for el in str_current_runs.split(','))
        ranges = (np.arange(int(s), int(e) + 1 if e else int(s) + 1)
                  for s, e in spans)
        try:
            all_nums = itertools.chain.from_iterable(ranges)
            _all_nums = set(all_nums)
        except ValueError:
            raise ValueError("Check format of input")
        self.list_current_runs = [str(_run) for _run in _all_nums]

    def new_runs(self, list_runs=[]):
        """add new runs, remove already existing ones"""

        # find list of runs to remove
        list_runs = set(list_runs)
        _list_runs_to_remove = set(list_runs.intersection(self.list_current_runs))

        # remove the runs from list_runs and list_current_runs
        clean_list_runs = list(list_runs - _list_runs_to_remove)
        clean_list_current_runs = list(set(self.list_current_runs) - _list_runs_to_remove)

        new_list_current_runs = clean_list_runs + clean_list_current_runs
        self.list_current_runs = new_list_current_runs

        # go from string to int
        int_new_list_current_runs = [np.int(_run) for _run in new_list_current_runs]

        # sort them to prepare them for output format
        int_new_list_current_runs.sort()
        self.int_list_current_runs = int_new_list_current_runs

        if int_new_list_current_runs == []:
            self.str_list_current_runs = ""
            return

        # create output string format

        # only 1 run
        if len(int_new_list_current_runs) == 1:
            self.str_list_current_runs = str(int_new_list_current_runs[0])
            return

        # more than 1 run

        # create full matching list
        def match_list(reference_list=[], our_list=[]):
            _index = 0
            _ref_list_and_our_list = zip(our_list, reference_list)
            for _ref_run, _our_run in _ref_list_and_our_list:
                if _ref_run == _our_run:
                    _index += 1
                    continue
                break

            return _index

        _index = 0
        _groups = []
        _our_list = self.int_list_current_runs[_index: ]
        _list_full_reference = np.arange(_our_list[0], _our_list[-1]+1)

        # print("new list: {}".format(_our_list))

        while _our_list:

            _ref_index = match_list(reference_list=_list_full_reference,
                                    our_list=_our_list)

            _group = [_our_list[0], _our_list[_ref_index-1]]
            # print("_group: {}".format(_group))
            _groups.append(_group)

            _our_list = _our_list[_ref_index:]
            if len(_our_list) == 1:
                _groups.append(_our_list)
                break

            if len(_our_list) == 0:
                break

            _list_full_reference = np.arange(_our_list[0], _our_list[-1]+1)

        # print("_groups: {}".format(_groups))

        list_runs = []
        for _group in _groups:

            if len(_group) == 2:
                [_left_value, _right_value] = _group

                if _left_value == _right_value:
                    list_runs.append(str(_left_value))
                elif _right_value == (_left_value + 1):
                    list_runs.append(str(_left_value))
                    list_runs.append(str(_right_value))
                else:
                    list_runs.append("{}:{}".format(_left_value, _right_value))

            else:
                list_runs.append(str(_group[0]))

        str_runs = ",".join(list_runs)
        # print(str_runs)
        return str_runs


















