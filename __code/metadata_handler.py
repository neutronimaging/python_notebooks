from PIL import Image
import os


class MetadataHandler(object):

    @staticmethod
    def get_time_stamp(file_name='', ext='tif'):

        if ext == 'tif':
            try:
                o_image = Image.open(file_name)
                o_dict = dict(o_image.tag_v2)
                time_stamp = o_dict[650000][0]
                # time_stamp_s = str(o_dict[65002][0])
                # time_stamp_ns = str(o_dict[65003][0])
                # time_stamp_string = "{}.{}".format(time_stamp_s, time_stamp_ns)
                # time_stamp = float(time_stamp_string)
            except:
                time_stamp = os.path.getmtime(file_name)
        elif ext == 'fits':
            time_stamp = os.path.getmtime(file_name)

        else:
            raise NotImplemented

        return time_stamp

