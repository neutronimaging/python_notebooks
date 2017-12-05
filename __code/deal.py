import shutil
import os
import ipywe.fileselector
import glob

from ipywidgets import widgets
from IPython.core.display import display, HTML

class Deal(object):

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_input_folder(self):
        self.input_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Folder with All Images to Deal ...',
                                                                    start_dir=self.working_dir,
                                                                    multiple=False,
                                                                    type='directory')

        self.input_folder_ui.show()

    def select_output_folder(self):
        self.output_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Output Folder ...',
                                                                    start_dir=self.working_dir,
                                                                    multiple=False,
                                                                    type='directory')

        self.output_folder_ui.show()

    def deal(self):

        self.input_folder = self.input_folder_ui.selected
        self.list_input_images = glob.glob(os.path.join(self.input_folder, '*.*'))

        self.output_folder = self.output_folder_ui.selected

        result_dict = self.__split(list_images=self.list_input_images)

        display(HTML('<span>Number of images per folder: ' + str(result_dict['nbr_images_per_folder']) + '<br>' + \
                     'Number of folders: ' + str(result_dict['nbr_folders']) + '</span>'))

        self.__deal(nbr_images_per_folder=result_dict['nbr_images_per_folder'],
                    nbr_folders=result_dict['nbr_folders'],
                    output_folder=self.output_folder,
                    output_folder_dict=result_dict['output_folder_dict'])

    def __split(self, list_images=[]):
        # splitting name using hypothesis that name is defined as /path/image###_####.fits
        list_folder = set([os.path.basename(_file).split('_')[0] for _file in list_images])
        output_folder_dict = {}
        for _folder in list_folder:
            output_folder_dict[_folder] = []

        #putting each input image into its own dictionary array
        for _image in list_images:
            _key = os.path.basename(_image).split('_')[0]
            output_folder_dict[_key].append(_image)

        nbr_images_per_folder = len(output_folder_dict[list(output_folder_dict.keys())[0]])
        nbr_folders = len(list(output_folder_dict.keys()))

        return {'output_folder_dict': output_folder_dict,
                'nbr_images_per_folder': nbr_images_per_folder,
                'nbr_folders': nbr_folders}

    def __deal(self, prefix_name='image', nbr_images_per_folder=0, nbr_folders=0,
        output_folder='', output_folder_dict={}):
        '''
        copy the images into their corresponding new output folder

        Parameters:
        ===========
        prefix_name: default is 'image'. Will be used to define the new name of the images
        nbr_images_per_folder: int
        nbr_folders: int
        output_fodler: string
        output_folder_dict: {}. {'image001': [ list of images],
                                'image002': [list of images]}

        '''
        box1 = widgets.HBox([widgets.Label("images progress:",
                                          layout=widgets.Layout(width='30%')),
                            widgets.IntProgress(max=nbr_images_per_folder-1)])
        display(box1)
        w1 = box1.children[1]

        box2 = widgets.HBox([widgets.Label("folder progress:",
                                          layout=widgets.Layout(width='30%')),
                            widgets.IntProgress(max=nbr_folders-1)])
        display(box2)
        w2 = box2.children[1]

        _index1 = 0
        for _folder in output_folder_dict.keys():
            # make folder
            _new_folder = os.path.join(output_folder, _folder)
            os.mkdir(_new_folder)
            _input_list_images = output_folder_dict[_folder]

            _index2 = 0
            for _input_image in _input_list_images:
                _basename_image = os.path.basename(_input_image)
                [part1, part2] = _basename_image.split('_')
                new_name = os.path.join(output_folder, _folder, prefix_name + '_' + part2)
                shutil.copyfile(_input_image, new_name)
                _index2 += 1
                w1.value = _index2

            w1.value = 0

            _index1 += 1
            w2.value = _index1

        w1.value = nbr_images_per_folder

        box1.close()
        box2.close()
