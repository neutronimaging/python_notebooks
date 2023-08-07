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

# +
import os, shutil, numpy as np, glob, time, pickle as pkl, imars3d
from imars3d.jnbui import ct_wizard, imageslider
from imars3d.ImageFile import ImageFile

# Be patient, this may take a little while too
# # %matplotlib notebook
# %matplotlib inline
from matplotlib import pyplot as plt
# -

# # Input Settings

data_folder = '/Volumes/G-DRIVE/IPTS/IPTS-25519-iMars3D-command-line/raw/ct_scans/2021_07_21_1in/'
ob_folder = '/Volumes/G-DRIVE/IPTS/IPTS-25519-iMars3D-command-line/raw/ob/2021_07_21_1in/'
df_folder = '/Volumes/G-DRIVE/IPTS/IPTS-25519-iMars3D-command-line/raw/df/2021_07_19/'

ct_sig = "treated_1inch"
ct_scan_root = "/Volumes/G-DRIVE/IPTS/IPTS-25519-iMars3D-command-line/raw/ct_scans/"
ct_dir = "/Volumes/G-DRIVE/IPTS/IPTS-25519-iMars3D-command-line/raw/ct_scans/2021_07_21_1in/"
iptsdir = "/Volumes/G-DRIVE/IPTS/IPTS-25519-iMars3D-command-line/"
outdir = "/Volumes/G-DRIVE/IPTS/IPTS-25519-iMars3D-command-line/shared/processed_data/2021_07_21_1in"
instrument = "CG1D"
ob_dir = "/Volumes/G-DRIVE/IPTS/IPTS-25519-iMars3D-command-line/raw/ob/"
data_dir = "/Volumes/G-DRIVE/IPTS/IPTS-25519-iMars3D-command-line/raw/"
workdir = "/Volumes/G-DRIVE/IPTS/sandbox/work.imars3d/2021_07_21_1in"
df_files = glob.glob(os.path.join(df_folder, "*.tiff"))
scan = "2021_07_21_1in"
ipts = 25519
ob_files = glob.glob(os.path.join(ob_folder, "*.tiff"))
ct_subdir = "2021_07_21_1in"
df_dir = "/Volumes/G-DRIVE/IPTS/IPTS-25519-iMars3D-command-line/raw/df/"
facility = "HFIR"
ct_scans_subdir = glob.glob(os.path.dirname(data_folder) + "/*")

# # Create CT data object

from imars3d.CT import CT

ct = CT(data_dir,
       CT_subdir=ct_dir,
       CT_identifier=ct_sig,
       workdir=workdir,
       outdir=outdir,
       ob_files=ob_files,
       df_files=df_files)

# # preprocess 

# %%time
ppd = ct.preprocess()

xmin = 500
ymin = 0
xmax = 1600
ymax = 2047

# %%time
ct.recon(crop_window=(xmin, ymin, xmax, ymax))


