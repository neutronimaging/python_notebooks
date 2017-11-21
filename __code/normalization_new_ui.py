from ipywidgets import widgets, Layout
from IPython.core.display import display
import ipywe.fileselector

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
                 next=None, multiple=False,
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
        if self.current_ui.state == 'sample':
            self.current_ui.files.sample = self.selected
        elif self.current_ui.state == 'ob':
            self.current_ui.files.ob = self.selected
        else:
            self.current_ui.files.df = self.selected

        self.current_ui.label.value = "{} files selected".format(len(self.selected))


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

    def __init__(self, prev_button=False, next_button=True, state='sample', working_dir=''):

        self.prev_button = prev_button
        self.next_button = next_button
        self.state = state
        self.working_dir = working_dir

    def init_ui(self, files=None):

        self.files = files

        self.__top_panel()
        self.__bottom_panel()
        self.__file_selector()
        self.__init_widgets()

    def __init_widgets(self):
        self.title.value = "Select list of {} files ".format(self.state)

        _list = self.files.sample
        if self.state == 'ob':
            _list = self.files.ob
        elif self.state == 'df':
            _list = self.files.df
        self.label.value = "{} files selected".format(len(_list))

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
                                                 button_style='info',
                                                 layout=widgets.Layout(width='20%'))
            self.prev_button_ui.on_click(self.prev_button_clicked)
            list_ui.append(self.prev_button_ui)

        self.current_state_label_ui = widgets.Label("         ",
                                                    layout=widgets.Layout(width='70%'))
        list_ui.append(self.current_state_label_ui)

        if self.next_button:
            self.next_button_ui = widgets.Button(description="Next Step>>",
                                                 tooltip='Click to move to next step',
                                                 button_style='info',
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
        display(widgets.Label("Selection of All Input Files",
                              layout=self.label_layout))

        self.sample_panel = sample_panel
        self.sample_panel.show()
        return


class SampleSelectionPanel(Panel):
    files = None

    def __init__(self, prev_button=False, next_button=True, working_dir=''):
        super(SampleSelectionPanel, self).__init__(prev_button=prev_button,
                                                   next_button=next_button,
                                                   working_dir=working_dir)

    def next_button_clicked(self, event):
        self.remove()
        _panel = OBSelectionPanel()
        _panel.init_ui(files=self.files)
        _panel.show()


class OBSelectionPanel(Panel):
    def __init__(self, working_dir=''):
        super(OBSelectionPanel, self).__init__(prev_button=True, state='ob', working_dir=working_dir)

    def next_button_clicked(self, event):
        self.remove()
        _panel = DFSelectionPanel()
        _panel.init_ui(files=self.files)
        _panel.show()

    def prev_button_clicked(self, event):
        self.remove()
        _panel = SampleSelectionPanel()
        _panel.init_ui(files=self.files)
        _panel.show()


class DFSelectionPanel(Panel):
    def __init__(self, working_dir=''):
        super(DFSelectionPanel, self).__init__(prev_button=True,
                                               next_button=False,
                                               state='df',
                                               working_dir=working_dir)

    def prev_button_clicked(self, event):
        self.remove()
        _panel = OBSelectionPanel()
        _panel.init_ui(files=self.files)
        _panel.show()
