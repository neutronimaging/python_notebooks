import matplotlib.image as mpimg
import logging
import numpy as np

from NeuNorm.normalization import Normalization

from __code._utilities.file import get_file_extension


def load_file(file=None):
    ext = get_file_extension(filename=file)

    if ext.lower() in ['jpg', 'jpeg']:
        _data = mpimg.imread(file)
        # with Image.open(file) as im:   # BUG that crashes the UI
        #    _data = np.asarray(im.convert('L'))/255.

    else:
        o_norm = Normalization()
        o_norm.load(file=file, notebook=False)
        _data = o_norm.data['sample']['data'][0]

    logging.info(f"np.shape(_data): {np.shape(_data)}")
    return _data
