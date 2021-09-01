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

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
# #from __code.filename_metadata_match import FilenameMetadataMatch

# from __code import system
# system.System.select_working_dir()
# from __code.__all import custom_style
# custom_style.style()

# + run_control={"frozen": false, "read_only": false}
import ipywe.fileselector
from IPython.core.display import HTML
from __code.time_utility import RetrieveTimeStamp
import os

class FilenameMetadataMatch(object):

    data_folder = ''
    metadata_file = ''
    
    list_data_time_stamp = None
    
    def __init__(self, working_dir='./'):
        self.working_dir = working_dir

    def select_input_folder(self):
        _instruction = "Select Input Folder ..."
        self.input_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction=_instruction,
                                                                    start_dir=self.working_dir,
                                                                    next=self.select_input_folder_done,
                                                                    type='directory',
                                                                   )
        self.input_folder_ui.show()
        
    def select_input_folder_done(self, folder):
        self.data_folder = folder
        display(HTML('Folder Selected: <span style="font-size: 20px; color:green">' + folder))

    def select_metadata_file(self):
        _instruction = "Select Metadata File ..."
        self.metadata_ui = ipywe.fileselector.FileSelectorPanel(instruction=_instruction,
                                                                start_dir=self.working_dir,
                                                                next=self.select_metadata_file_done,
                                                               )
        self.metadata_ui.show()
        
    def select_metadata_file_done(self, metadata_file):
        self.metadata_file = metadata_file
        display(HTML('Metadata File Selected: <span style="font-size: 20px; color:green">' + metadata_file))
        
    def retrieve_time_stamp(self):
        o_retriever = RetrieveTimeStamp(folder=self.data_folder)
        o_retriever._run()
        self.list_data_time_stamp = o_retriever
    
    def load_metadata(self):
        metadata_file = self.metadata_file
    


# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Input Folder 
# -

# This is where we select the folder of images that we will need to match with the metadat 

# + run_control={"frozen": false, "read_only": false}
#o_match = FilenameMetadataMatch(working_dir=system.System.get_working_dir())
o_match = FilenameMetadataMatch(working_dir='/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-20444-Regina/')
o_match.select_input_folder()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Metadata File 
# -

# We need to select here the metadata file (*.mpt)

# + run_control={"frozen": false, "read_only": false}
o_match.select_metadata_file()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Retrieve Time Stamp

# + run_control={"frozen": false, "read_only": false}
o_match.retrieve_time_stamp()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Load Metadata File

# + [markdown] run_control={"frozen": false, "read_only": false}
# # DEBUGGING STARTS HERE

# + run_control={"frozen": false, "read_only": false}
import pandas as pd
import codecs
from __code.file_handler import get_file_extension
from ipywidgets import widgets
import os
import pprint

#metadata_file = o_match.metadata_file
import glob
import platform

if platform.node() == 'mac95470':
    git_dir = os.path.abspath(os.path.expanduser('~/git/'))
else:
    git_dir = '/Volumes/my_book_thunderbolt_duo/git/'
    
metadata_list_files = glob.glob(git_dir + '/standards/ASCII/*.mpt')

index_file = 2

metadata_file = metadata_list_files[index_file]
print("Loading file: {}".format(metadata_file))

assert os.path.exists(metadata_file)

# + [markdown] run_control={"frozen": false, "read_only": false}
# **Allow users to define:**
#
#  * reference_line_showing_end_of_metadata
#  * start_of_data_after_how_many_lines_from_reference_line
#  * index or label of time info column in big table
# -

from __code.metadata_ascii_parser import *

# + run_control={"frozen": false, "read_only": false}
o_meta = MetadataFileParser(filename=metadata_file, 
                            meta_type='mpt',
                            time_label='time/s',
                            reference_line_showing_end_of_metadata='Number of loops',
                            end_of_metadata_after_how_many_lines_from_reference_line=1)
o_meta.parse()

# + run_control={"frozen": false, "read_only": false}
o_meta.select_data_to_keep()
# -

o_meta.keep_only_columns_of_data_of_interest()
o_meta.select_output_location()

# +
# data = o_meta.get_data()

# +
# metadata_to_keep = np.array(o_meta.box.children[1].value)

# +
# new_data = data[metadata_to_keep]

# +
# data = new_data.reset_index()
# data.rename(index=str, columns={"index": "TimeStamp"})
# -


