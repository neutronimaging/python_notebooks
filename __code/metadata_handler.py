from PIL import Image
import os


class MetadataHandler(object):

    @staticmethod
    def get_time_stamp(file_name='', ext='tif'):

        if ext == 'tif':
            o_image = Image.open(file_name)
            o_dict = dict(o_image.tag_v2)
            time_stamp = o_dict[65000][0]

        elif ext == 'fits':
            time_stamp = os.path.getmtime(file_name)

        else:
            raise NotImplemented

        return time_stamp

