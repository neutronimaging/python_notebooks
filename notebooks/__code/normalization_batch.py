import os
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from IPython.core.display import HTML

from ipywidgets import widgets, Layout
from IPython.core.display import display
import ipywe.fileselector

from NeuNorm.normalization import Normalization
from NeuNorm.roi import ROI

from __code import utilities, file_handler


def close(w):
    "recursively close a widget"
    if hasattr(w, 'children'):
        for c in w.children:
            close(c)
            continue
    w.close()
    return


class myFileSelectorPanel(ipywe.fileselector.FileSelectorPanel):
    def __init__(self, instruction, start_dir=".", type='file',
                 next=None,
                 multiple=False,
                 newdir_toolbar_button=False,
                 current_ui=None):
        super(myFileSelectorPanel, self).__init__(instruction,
                                                  start_dir=start_dir,
                                                  type=type,
                                                  next=next,
                                                  multiple=multiple,
                                                  newdir_toolbar_button=newdir_toolbar_button)
        self.current_ui = current_ui

    def validate(self, s):
        super(myFileSelectorPanel, self).validate(s)
        try:
            if self.current_ui.state == 'sample':
                self.current_ui.files.sample = self.selected
            elif self.current_ui.state == 'ob':
                self.current_ui.files.ob = self.selected
            else:
                self.current_ui.files.df = self.selected

            parent_folder = os.path.dirname(os.path.dirname(self.selected[0]))
            self.current_ui.working_dir = parent_folder
            self.current_ui.label.value = "{} files selected".format(len(self.selected))
            self.current_ui.next_button_ui.disabled = False
            self.current_ui.next_button_ui.button_style = 'success'
        except AttributeError:
            pass


class Data:
    sample = []
    ob = []
    df = []


class Files:
    sample = []
    ob = []
    df = []


class Panel:
    layout = Layout(border='1px lightgray solid', margin='5px', padding='15px')
    button_layout = Layout(margin='10px 5px 5px 5px')
    label_layout = Layout(height='32px', padding='2px', width='300px')

    current_state_label_ui = None
    prev_button_ui = None
    next_button_ui = None
    o_norm_handler = None

    df_panel = None
    top_object = None
    
    def __init__(self, prev_button=False, next_button=True, state='sample', working_dir='',
                top_object=None):

        self.prev_button = prev_button
        self.next_button = next_button
        self.state = state
        self.working_dir = working_dir
        self.top_object = top_object

    def init_ui(self, files=None):

        self.files = files

        self.__top_panel()
        self.__bottom_panel()
        self.__file_selector()
        self.__init_widgets()

    def __init_widgets(self):
        
        _list = self.files.sample
        _label = "Sample"
        _option = '(mandatory)'
        if self.state == 'ob':
            _list = self.files.ob
            _label = 'Open Beam'
        elif self.state == 'df':
            _list = self.files.df
            _label = 'Dark Field'
            _option = '(optional)'
        self.label.value = "{} files selected".format(len(_list))
        self.title.value = "Select list of {} files {} ".format(_label, _option)
        
        if len(_list) > 0:
            self.next_button_ui.disabled = False
            self.next_button_ui.button_style = 'success'
            
        if self.state == 'df':
            self.next_button_ui.disabled = False
            self.next_button_ui.button_style = 'success'

    def __top_panel(self):
        title_ui = widgets.HBox([widgets.Label("Instructions:",
                                               layout=widgets.Layout(width='20%')),
                                 widgets.Label("Select Samples Images and click NEXT",
                                               layout=widgets.Layout(width='50%')),
                                 ])

        label_ui = widgets.HBox([widgets.Label("Sample selected:",
                                               layout=widgets.Layout(width='20%')),
                                 widgets.Label("None",
                                               layout=widgets.Layout(width='50%')),
                                 ])
        self.title = title_ui.children[1]  # "Select [Samples/OB/DF] Images [and click NEXT]
        self.label = label_ui.children[1]  # number of samples selected

        self.top_panel = widgets.VBox(children=[title_ui, label_ui],
                                      layout=self.layout)

    def prev_button_clicked(self, event):
        raise NotImplementedError

    def next_button_clicked(self, event):
        raise NotImplementedError

    def __bottom_panel(self):
        list_ui = []
        if self.prev_button:
            self.prev_button_ui = widgets.Button(description="<< Previous Step",
                                                 tooltip='Click to move to previous step',
                                                 button_style='success',
                                                 disabled=False,
                                                 layout=widgets.Layout(width='20%'))
            self.prev_button_ui.on_click(self.prev_button_clicked)
            list_ui.append(self.prev_button_ui)

        self.current_state_label_ui = widgets.Label("         ",
                                                    layout=widgets.Layout(width='70%'))
        list_ui.append(self.current_state_label_ui)

        if self.next_button:
            self.next_button_ui = widgets.Button(description="Next Step>>",
                                                 tooltip='Click to move to next step',
                                                 button_style='warning',
                                                 disabled=True,
                                                 layout=widgets.Layout(width='20%'))
            list_ui.append(self.next_button_ui)
            self.next_button_ui.on_click(self.next_button_clicked)

        self.bottom_panel = widgets.HBox(list_ui)

    def __file_selector(self):
        self.file_selector = myFileSelectorPanel(instruction='',
                                                 start_dir=self.working_dir,
                                                 multiple=True,
                                                 current_ui=self)

    def show(self):
        display(self.top_panel)
        display(self.bottom_panel)
        self.file_selector.show()

    def remove(self):
        close(self.top_panel)
        close(self.bottom_panel)
        self.file_selector.remove()

    def nextStep(self):
        raise NotImplementedError


class WizardPanel:
    label_layout = Layout(border='1px lighgray solide', height='35px', padding='8px', width='300px')
    sample_panel = None

    def __init__(self, sample_panel=None):
        # display(widgets.Label("Selection of All Input Files",
        #                       layout=self.label_layout))
        #
        self.sample_panel = sample_panel
        self.sample_panel.show()
        return


class SampleSelectionPanel(Panel):

    files = None
    o_norm = None
    
    def __init__(self, prev_button=False, next_button=True, working_dir='', top_object=None):
        super(SampleSelectionPanel, self).__init__(prev_button=prev_button,
                                                   next_button=next_button,
                                                   working_dir=working_dir,
                                                   top_object=top_object)

    def next_button_clicked(self, event):
        self.remove()
        _panel = OBSelectionPanel(working_dir=self.working_dir, top_object=self)
        _panel.init_ui(files=self.files)
        _panel.show()


class OBSelectionPanel(Panel):
    def __init__(self, working_dir='', top_object=None):
        super(OBSelectionPanel, self).__init__(prev_button=True, state='ob', 
                                               working_dir=working_dir,
                                               top_object=top_object)

    def next_button_clicked(self, event):
        self.remove()
        _panel = DFSelectionPanel(working_dir=self.working_dir,
                                 top_object=self.top_object)
        _panel.init_ui(files=self.files)
        _panel.show()

    def prev_button_clicked(self, event):
        self.remove()
        _panel = SampleSelectionPanel(working_dir=self.working_dir,
                                     top_object=self.top_object)
        _panel.init_ui(files=self.files)
        _panel.show()

class DFSelectionPanel(Panel):
    def __init__(self, working_dir='', top_object=None):
        self.working_dir = working_dir
        super(DFSelectionPanel, self).__init__(prev_button=True,
                                               next_button=True,
                                               state='df',
                                               working_dir=working_dir,
                                              top_object=top_object)

    def prev_button_clicked(self, event):
        self.remove()
        _panel = OBSelectionPanel(working_dir=self.working_dir, top_object=self.top_object)
        _panel.init_ui(files=self.files)
        _panel.show()

    def next_button_clicked(self, event):
        self.remove()
        o_norm_handler = NormalizationHandler(files=self.files,
                                              working_dir=self.working_dir)
        o_norm_handler.load_data()
        self.top_object.o_norm_handler = o_norm_handler
        self.top_object.o_norm = o_norm_handler.o_norm

class NormalizationHandler(object):
    """This class will load a subset of the sample, just enough to be able to
    select ROI"""

    data = None
    integrated_sample = []
    working_dir = ''
    o_norm = None

    normalized_data_array = []

    def __init__(self, files=None, working_dir=''):
        self.files = files
        self.working_dir = working_dir
        self.data = Data()

    def load_data(self):
        self.o_norm = Normalization()
        
        # sample
        full_list_sample = self.files.sample
        nbr_full_list_sampled = len(full_list_sample)

        if nbr_full_list_sampled > 3:
            new_list_sample = [full_list_sample[0],
                               full_list_sample[np.int(nbr_full_list_sampled/2)],
                               full_list_sample[-1]]
            list_sample = new_list_sample

        self.o_norm.load(file=list_sample, notebook=True)
        self.data.sample = self.o_norm.data['sample']['data']
        self.list_file_names = list_sample

    def select_export_folder(self):

        def display_file_selector_from_shared(ev):
            start_dir = os.path.join(self.working_dir, 'shared')
            if not os.path.exists(start_dir):
                start_dir = self.working_dir

            self.output_folder_ui.remove()
            self.display_file_selector(start_dir=start_dir)

        def display_file_selector_from_home(ev):
            import getpass
            _user = getpass.getuser()
            start_dir = os.path.join('/SNS/users', _user)
            if not os.path.exists(start_dir):
                start_dir = self.working_dir

            self.output_folder_ui.remove()
            self.display_file_selector(start_dir=start_dir)

        ipts = os.path.basename(self.working_dir)

        button_layout = widgets.Layout(width='30%',
                                       border='1px solid gray')

        self.hbox = widgets.HBox([widgets.Button(description="Jump to {} Shared Folder".format(ipts),
                                            button_style='success',
                                            layout=button_layout),
                             widgets.Button(description="Jump to My Home Folder",
                                            button_style='success',
                                            layout=button_layout)])
        go_to_shared_button_ui = self.hbox.children[0]
        go_to_home_button_ui = self.hbox.children[1]

        go_to_shared_button_ui.on_click(display_file_selector_from_shared)
        go_to_home_button_ui.on_click(display_file_selector_from_home)

        display(self.hbox)
        self.display_file_selector()

    def display_file_selector(self, start_dir=''):

        def remove_buttons(ev):
            self.hbox.close()

        self.output_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Output Folder',
                                                                     start_dir=start_dir,
                                                                     multiple=False,
                                                                     next=remove_buttons,
                                                                     type='directory')
        self.output_folder_ui.show()

    def export(self, rois={}):
        base_folder = os.path.basename(os.path.dirname(self.list_file_names[0])) + '_normalized'
        output_folder = os.path.abspath(os.path.join(self.output_folder_ui.selected, base_folder))
        utilities.make_dir(dir=output_folder)
        self.normalized(rois=rois, output_folder=output_folder)

        display(HTML('<span style="font-size: 20px; color:blue">The normalized images are currently being ' +
                     'created in </span><span style="font-size: 20px; color:green">' + output_folder + \
                     '<br><br></span><span style="font-size: 20px; color:blue">Feel free to start another reduction now!</span>'))

    def prepare_file_names_for_command_line(self, list_files):
        if list_files:
            list_files_new_format = []
            for _file in list_files:
                new_file = _file.replace(" ", "\\ ")
                list_files_new_format.append(new_file)

            str_files = ",".join(list_files_new_format)
            return str_files
        return list_files

    def normalized(self, rois={}, output_folder=''):

        py_script = os.path.abspath("./__code/normalization_script.py")
        command_line = 'python {}'.format(py_script)

        # sample files
        str_sample_files = self.prepare_file_names_for_command_line(self.files.sample)
        command_line += " -sf={}".format(str_sample_files)

        # ob files
        str_ob_files = self.prepare_file_names_for_command_line(self.files.ob)
        command_line += ' -of={}'.format(str_ob_files)

        # df files
        if self.files.df:
            str_df_files = self.prepare_file_names_for_command_line(self.files.df)
            command_line += ' -df={}'.format(str_df_files)

        # roi
        if not rois == {}:
            _list_roi = []
            for _key in rois.keys():
                _roi = rois[_key]
                x0 = _roi['x0']
                y0 = _roi['y0']
                x1 = _roi['x1']
                y1 = _roi['y1']
                _list_roi.append("{},{},{},{}".format(x0, y0, x1, y1))
            str_list_roi = ":".join(_list_roi)
            command_line += ' -rois={}'.format(str_list_roi)

        # output
        output_folder = output_folder.replace(" ", "\\ ")
        command_line += ' --output={} &'.format(output_folder)

        # print("command line > {}".format(command_line))
        os.system(command_line)







