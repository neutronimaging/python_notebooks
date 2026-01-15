import dxchange
import numpy as np
from tqdm import tqdm
from skimage.io import imread
import multiprocessing as mp


def _init_arr_from_stack(list_files, ext=".tiff", slc=None):
    """
    Initialize numpy array from files in a folder.
    """
    number_of_files = len(list_files)
    first_file = list_files[0]
    if ext == ".fits":
        _arr = dxchange.read_fits(first_file)
        f_type = "fits"
    elif ext in [".tiff", ".tif"]:
        _arr = dxchange.read_tiff(first_file)
        f_type = "tif"
    else:
        raise ValueError(f"'{first_file}', only '.tif/.tiff' and '.fits' are supported.")
    size = (number_of_files, _arr.shape[0], _arr.shape[1])
    return np.empty(size, dtype=_arr.dtype), f_type


def read_img_stack(list_files: list, ext=".tiff", fliplr=False, flipud=False):
    arr, f_type = _init_arr_from_stack(list_files, ext=ext)
    if f_type == "tif":
        for m, name in tqdm(enumerate(list_files)):
            _arr = dxchange.read_tiff(name)
            if fliplr:
                _arr = np.fliplr(_arr)
            if flipud:
                _arr = np.flipud(_arr)
            arr[m] = _arr
    elif f_type == "fits":
        for m, name in tqdm(enumerate(list_files)):
            _arr = dxchange.read_fits(name)
            if fliplr:
                _arr = np.fliplr(_arr)
            if flipud:
                _arr = np.flipud(_arr)
            arr[m] = _arr
    return arr


def _worker(fl):
    return (imread(fl).astype(np.float32)).swapaxes(0, 1)


def load_data_using_multithreading(list_tif: list = None, combine_tof: bool = False) -> np.ndarray:
    """load data using multithreading"""
    with mp.Pool(processes=40) as pool:
        data = pool.map(_worker, list_tif)

    if combine_tof:
        return np.array(data).sum(axis=0)
    else:
        return np.array(data, dtype=np.float32)