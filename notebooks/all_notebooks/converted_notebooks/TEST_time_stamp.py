# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.5.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + run_control={"frozen": false, "read_only": false}
# MacPro
list_files = ["/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-19799/Day1/20180129_BanderaGrey_Dolomite_Dry_0040_0182.tiff",
             "/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-19921-Charles/02/im0000.tif"]

# unix
#list_files = ['/HFIR/CG1DImaging/IPTS-19799/raw/radiographs/Day1/20180129_BanderaGrey_Dolomite_Dry_0040_0182.tif',]

expected_time_stamp = [886107840.0457269,
                       1517259840.5604978,]

expected_user_time_stamp = ["2018-01-29 16:04:00",
                            "2018-03-21 12:14:31",]

# +
from PIL import Image
import os
import datetime
import pytz

class MetadataHandler(object):

    @staticmethod
    def get_time_stamp(file_name='', ext='tif'):

        if ext == 'tif':
            try:
                o_image = Image.open(file_name)
                o_dict = dict(o_image.tag_v2)
                try:
                    time_stamp_s = str(o_dict[65002])
                    time_stamp_ns = str(o_dict[65003])
                    time_stamp_string = "{}.{}".format(time_stamp_s, time_stamp_ns)
                    time_stamp = float(time_stamp_string)
                except:
                    time_stamp = o_dict[65000]

                time_stamp = MetadataHandler._convert_epics_timestamp_to_rfc3339_timestamp(time_stamp)
            except:
                time_stamp = os.path.getctime(file_name)
        elif ext == 'fits':
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

#         # Use pytz magic to get an ORNL-localized version of a Python
#     # datetime object.
#         ornl_datetime = pytz.timezone('America/New_York').localize(
#         datetime.datetime.fromtimestamp(unix_epoch_timestamp)
#         )

#         return str(ornl_datetime.isoformat())


# -

for _index,_file in enumerate(list_files):
    _time_stamp = MetadataHandler.get_time_stamp(file_name=_file, ext='tif')
    assert MetadataHandler.convert_to_human_readable_format(_time_stamp) == expected_user_time_stamp[_index]

# Testing the type of the metadata

o_image = Image.open(list_files[0])
o_dict = dict(o_image.tag_v2)
type(o_dict[65002])

import platform

platform.system()


