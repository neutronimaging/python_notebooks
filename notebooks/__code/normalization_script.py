import argparse
import numpy as np

from NeuNorm.normalization import Normalization
from NeuNorm.roi import ROI

parser = argparse.ArgumentParser(description='Neutron Imaging Normalization')
parser.add_argument('-o', '--output', help='output folder', type=str)
parser.add_argument('-sf', '--sample_files', help='comma separated list of samples', type=str)
parser.add_argument('-of', '--ob_files', help='comma separated list of open beams', type=str)
parser.add_argument('-df', '--df_files', help='comma separated list of dark fields', type=str)
parser.add_argument('-rois', help='colon string of each roi: x0,y0,x1,y1')

def normalization():

    def remove_back_slash(list_files):
        if list_files:
            list_files_cleaned = []
            for _file in list_files:
                new_file = _file.replace("\\", "")
                list_files_cleaned.append(new_file)
            return list_files_cleaned
        return list_files

    args = parser.parse_args()
    # print("output: {}".format(args.output))  # to retrieve output value
    # print("sf: {}".format(args.sample_files))
    # print("ob: {}".format(args.ob_files))
    #
    # print("x0: {}".format(args.roi_x0))
    # print("y0: {}".format(args.roi_y0))
    # print("x1: {}".format(args.roi_x1))
    # print("y1: {}".format(args.roi_y1))

    o_norm = Normalization()
    list_samples = args.sample_files.split(',')
    list_obs = args.ob_files.split(',')

    list_samples = remove_back_slash(list_samples)
    list_obs = remove_back_slash(list_obs)

    # loading
    o_norm.load(file=list_samples)
    o_norm.load(file=list_obs, data_type='ob')
    if args.df_files:
        list_dfs = args.df_files.split(',')
        list_dfs = remove_back_slash(list_dfs)
        o_norm.load(file=list_dfs, data_type='df')
        o_norm.df_correction()

    if args.rois:
        list_rois = args.rois.split(':')
        array_roi_object = []
        for _rois in list_rois:
            [x0,y0,x1,y1] = _rois.split(',')  #x0,y0,x1,y1
            _roi = ROI(x0=np.int(x0), y0=np.int(y0), x1=np.int(x1), y1=np.int(y1))
            array_roi_object.append(_roi)

        o_norm.normalization(roi=array_roi_object)

    else:
        o_norm.normalization()

    output_folder = args.output
    output_folder = output_folder.replace("\\", "")
    o_norm.export(folder=output_folder)

if __name__ == "__main__":
   normalization()







