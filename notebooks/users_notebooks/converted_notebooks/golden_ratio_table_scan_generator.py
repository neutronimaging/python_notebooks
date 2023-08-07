# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Example of the output file format 

# CG1D:Det:Q1:TIFF1:FilePath,CG1D:Det:Q1:TIFF1:FileName,CG1D:Det:Q1:AcquireTime,CG1D:Mot:SmallRot2,CG1D:Scan:IncrementRunNo.PROC,CG1D:Scan:RunNoRestore.PROC,Camera,Camera
# /data/IPTS-25781/raw/ct_scans/2022_11_07_DAS,das_test_1,2.4,1.0,1,1,QHY 90,QHY 90
# /data/IPTS-25781/raw/ct_scans/2022_11_07_DAS,das_test_2,2.4,2.0,1,1,QHY 90,QHY 90
# /data/IPTS-25781/raw/ct_scans/2022_11_07_DAS,das_test_3,2.4,3.0,1,1,QHY 90,QHY 90
# /data/IPTS-25781/raw/ct_scans/2022_11_07_DAS,das_test_4,2.4,4.,1,1,QHY 90,QHY 90
# /data/IPTS-25781/raw/ct_scans/2022_11_07_DAS,das_test_5,2.4,5.0,1,1,QHY 90,QHY 90

# +
import numpy as np

def make_ascii_file(data=[], output_file_name=''):
    f = open(output_file_name, 'w')
    for _data in data:
        _line = str(_data) + '\n'
        f.write(_line)

    f.close()


# -

# # User input 

# +
file_path = "/data/IPTS-25265/raw/ct_scans/2022_11_08_1image_30s_1000angles/"
acquisition_time_s = 30
nbr_projections_per_angle = 1
name_of_rotation_stage = "CG1D:Mot:SmallRot2"
name_of_camera = "QHY 90"

name_of_the_table_scan_file = "/Users/j35/Desktop/table_scan_1image_30s_1000angles.csv"
# -

# # golden ratio file (created by neuit.sns.gov)

# +
with open("Data.csv") as stream:
    lines = stream.readlines()
    
angle_values = ["%.2f"%(float(l)) for l in lines[1:]]
angle_values.insert(1, "90.00")

import pprint
# pprint.pprint(angle_values)

# +
file_name = []
csv_file = [f"CG1D:Det:Q1:TIFF1:FilePath,CG1D:Det:Q1:TIFF1:FileName,CG1D:Det:Q1:AcquireTime,{name_of_rotation_stage},CG1D:Scan:IncrementRunNo.PROC,CG1D:Scan:RunNoRestore.PROC,Camera,Camera"]

for angle in angle_values:
    angle_value_as_list = angle.split(".")
    angle_values_as_list_padded = [f"{int(_value):03d}" for _value in angle_value_as_list]
    angle_value = "_".join(angle_values_as_list_padded)
    for pro in np.arange(nbr_projections_per_angle):
        file_name = f"image_{angle_value}"
        _entry = f"{file_path},{file_name},{acquisition_time_s},{angle},1,1,{name_of_camera},{name_of_camera}"
        csv_file.append(_entry)
    
make_ascii_file(data=csv_file, output_file_name=name_of_the_table_scan_file)

# +
e_name = []
# for angle in angle_values:
#     angle_value_as_list = angle.split(".")
#     angle_values_as_list_padded = [f"{int(_value):03d}" for _value in angle_value_as_list]
#     angle_value = "_".join(angle_values_as_list_padded)
#     file_name.append(f"image_{angle_value}")
    
# csv_file = [f"CG1D:Det:Q1:TIFF1:FilePath,CG1D:Det:Q1:TIFF1:FileName,CG1D:Det:Q1:AcquireTime,{name_of_rotation_stage},CG1D:Scan:IncrementRunNo.PROC,CG1D:Scan:RunNoRestore.PROC,Camera,Camera"]
# for row_index in np.arange(len(angle_values)):
#     _entry = f"{file_path},{file_name[row_index]},{acquisition_time_s},{angle_values[row_index]},1,1,{name_of_camera},{name_of_camera}"
#     csv_file.append(_entry)
    
# make_ascii_file(data=csv_file, output_file_name=name_of_the_table_scan_file)# fil
# -


