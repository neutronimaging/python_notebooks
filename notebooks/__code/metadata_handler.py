from PIL import Image
import datetime
import os
from collections import OrderedDict
from ipywidgets import widgets
from IPython.core.display import display

class MetadataHandler(object):

    @staticmethod
    def get_time_stamp(file_name='', ext='tif'):

        if ext == 'tif':
            try:
                o_image = Image.open(file_name)
                o_dict = dict(o_image.tag_v2)
                try:
                    time_stamp_s = o_dict[65002]
                    time_stamp_ns = o_dict[65003]
                    time_stamp = time_stamp_s + time_stamp_ns * 1e-9
                except:
                    time_stamp = o_dict[65000]

                time_stamp = MetadataHandler._convert_epics_timestamp_to_rfc3339_timestamp(time_stamp)

            except:
                time_stamp = os.path.getctime(file_name)
        elif ext == 'fits':
            time_stamp = os.path.getctime(file_name)
        elif ext == 'jpg':
            time_stamp = os.path.getctime(file_name)

        else:
            raise NotImplemented

        return time_stamp

    @staticmethod
    def convert_to_human_readable_format(timestamp):
        """Convert the unix time stamp into a human readable time format

        Format return will look like  "2018-01-29 10:30:25"
        """
        return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
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
        EPOCH_OFFSET = 631152000
        unix_epoch_timestamp = EPOCH_OFFSET + epics_timestamp

        return unix_epoch_timestamp

    @staticmethod
    def get_metata(filename='', list_metadata=[]):
        if filename == "":
            return {}

        image = Image.open(filename)
        metadata = image.tag_v2
        result = {}
        for _meta in list_metadata:
            result[_meta] = metadata.get(_meta)

        image.close()
        return result

    @staticmethod
    def get_metadata(filename='', list_metadata=[], using_enum_object=False):
        if filename == "":
            return {}

        image = Image.open(filename)
        metadata = image.tag_v2
        result = {}
        if list_metadata == []:
            for _key in metadata.keys():
                result[_key] = metadata.get(_key)
            return result

        for _meta in list_metadata:
            result[_meta] = metadata.get(_meta.value)

        image.close()
        return result

    @staticmethod
    def retrieve_metadata(list_files=[], list_metadata=[], using_enum_object=False):
        if list_files == []:
            return {}

        _dict = OrderedDict()
        for _file in list_files:
            _meta = MetadataHandler.get_metadata(filename=_file,
                                                 list_metadata=list_metadata,
                                                 using_enum_object=using_enum_object)
            _dict[_file] = _meta

        return _dict

    @staticmethod
    def get_value_of_metadata_key(filename='', list_key=None):
        if filename == "":
            return {}

        image = Image.open(filename)
        metadata = image.tag_v2
        result = {}
        if list_key == []:
            for _key in metadata.keys():
                result[_key] = metadata.get(_key)
            return result

        for _meta in list_key:
            result[_meta] = metadata.get(_meta)

        image.close()
        return result

    @staticmethod
    def retrieve_value_of_metadata_key(list_files=[], list_key=[], is_from_notebook=False):
        if list_files == []:
            return {}

        if is_from_notebook:
            progress_bar = widgets.IntProgress(min=0,
                                               max=len(list_files)-1,
                                               value=0)
            display(progress_bar)

        _dict = OrderedDict()
        for _index, _file in enumerate(list_files):
            _meta = MetadataHandler.get_value_of_metadata_key(filename=_file,
                                                              list_key=list_key)
            _dict[_file] = _meta
            if is_from_notebook:
                progress_bar.value = _index

        if is_from_notebook:
            progress_bar.close()

        return _dict
