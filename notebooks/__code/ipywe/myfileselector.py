import ipywidgets as ipyw
import glob
import os
import time
from IPython.core.display import HTML
from IPython.display import display
from __code.ipywe import fileselector

from NeuNorm.normalization import Normalization
from ipywidgets import widgets


class MyFileSelectorPanel:
    """Files and directories selector"""

    # If ipywidgets version 5.3 or higher is used, the "width="
    # statement should change the width of the file selector. "width="
    # doesn't appear to work in earlier versions.
    select_layout = ipyw.Layout(width="99%", height="260px")
    select_multiple_layout = ipyw.Layout(
        width="99%", height="260px", display="flex", flex_flow="column")
    button_layout = ipyw.Layout(margin="5px 40px", border='1px solid gray')
    toolbar_button_layout = ipyw.Layout(margin="5px 10px", width="100px", border='1px solid gray')
    toolbar_box_layout = ipyw.Layout(border='1px solid lightgrey', padding='3px', margin='5px 50px 5px 5px',
                                     width='100%')
    label_layout = ipyw.Layout(width="250px")
    layout = ipyw.Layout()

    def js_alert(self, m):
        js = "<script>alert('%s');</script>" % m
        display(HTML(js))
        return

    def __init__(
            self,
            instruction,
            start_dir=".", type='file', next=None,
            multiple=False, newdir_toolbar_button=False,
            custom_layout=None,
            filters=dict(), default_filter=None,
            stay_alive=False,
    ):
        """
        Create FileSelectorPanel instance
        Parameters
        ----------
        instruction : str
            instruction to users for file/dir selection
        start_dir : str
            starting directory path
        type : str
            type of selection. "file" or "directory"
        multiple: bool
            if True, multiple files/dirs can be selected
        next : function
            callback function to execute after the selection is selected
        newdir_toolbar_button : bool
            If true, a button to create new directory is added to the toolbar
        filters: dictionary
            each key will be the search message for the user, such as "Ascii", "notebooks"
            the value will be the search engine, such as "*.txt" or "*.ipynb"
        stay_alive: bool (False by default)
            if True, the fileselector won't disapear after selection of a file/directory
        """
        if type not in ['file', 'directory']:
            raise ValueError("type must be either file or directory")
        if custom_layout:
            for k, v in custom_layout.items():
                name = '%s_layout' % k
                assert name in dir(self), "Invalid layout item: %s" % name
                setattr(self, name, v)
                continue
        self.instruction = instruction
        self.type = type
        self.filters = filters
        self.default_filter = default_filter
        self.cur_filter = None
        self.multiple = multiple
        self.newdir_toolbar_button = newdir_toolbar_button
        self.createPanel(os.path.abspath(start_dir))
        self.next = next
        self.stay_alive = stay_alive

    def createPanel(self, curdir):
        self.header = ipyw.Label(self.instruction, layout=self.label_layout)
        self.footer = ipyw.HTML("")
        self.body = self.createBody(curdir)
        self.panel = ipyw.VBox(children=[self.header, self.body, self.footer])

    def createBody(self, curdir):
        self.curdir = curdir
        self.footer.value = "Please wait..."
        # toolbar on the top
        # "jump to"
        self.jumpto_input = jumpto_input = ipyw.Text(
            value=curdir, placeholder="", description="Location: ", layout=ipyw.Layout(width='100%'))
        jumpto_button = ipyw.Button(description="Jump", layout=self.toolbar_button_layout)
        jumpto_button.on_click(self.handle_jumpto)
        jumpto = ipyw.HBox(children=[jumpto_input, jumpto_button], layout=self.toolbar_box_layout)
        self.jumpto_button = jumpto_button
        if self.newdir_toolbar_button:
            # "new dir"
            self.newdir_input = newdir_input = ipyw.Text(
                value="", placeholder="new dir name", description="New subdir: ",
                layout=ipyw.Layout(width='180px'))
            newdir_button = ipyw.Button(description="Create", layout=self.toolbar_button_layout)
            newdir_button.on_click(self.handle_newdir)
            newdir = ipyw.HBox(children=[newdir_input, newdir_button], layout=self.toolbar_box_layout)
            toolbar = ipyw.HBox(children=[jumpto, newdir])
        else:
            toolbar = ipyw.HBox(children=[jumpto])
        # entries in this starting dir

        if self.filters:
            self.createFilterWidget()
            entries_files = sorted(self.getFilteredEntries())
        else:
            entries_files = sorted(os.listdir(curdir))

        entries_paths = [os.path.join(curdir, e) for e in entries_files]
        entries_ftime = create_file_times(entries_paths)
        entries = create_nametime_labels(entries_files, entries_ftime)
        self._entries = entries = [' .', ' ..', ] + entries
        if self.multiple:
            value = []
            self.select = ipyw.SelectMultiple(
                value=value, options=entries,
                description="Select",
                layout=self.select_multiple_layout)
        else:
            value = entries[0]
            self.select = ipyw.Select(
                value=value, options=entries,
                description="Select",
                layout=self.select_layout)
        """When ipywidgets 7.0 is released, the old way that the select or select multiple 
           widget was set up (see below) should work so long as self.select_layout is changed
           to include the display="flex" and flex_flow="column" statements. In ipywidgets 6.0,
           this doesn't work because the styles of the select and select multiple widgets are
           not the same.

        self.select = widget(
            value=value, options=entries,
            description="Select",
            layout=self.select_layout) """

        # ------------------------------------------------------------
        # |  (filter)                                                |
        # |  Entries _______________________         | Change Dir |  |
        # |          _______________________                         |
        # |          _______________________                         |
        # |          _______________________                         |
        # |          _______________________             | Select |  |
        # ------------------------------------------------------------
        # left
        left_widgets = []
        if self.filters: left_widgets.append(self.filter_widget)
        left_widgets.append(self.select)
        left_vbox = ipyw.VBox(left_widgets, layout=ipyw.Layout(width="80%"))
        # right
        # change directory button
        self.changedir = ipyw.Button(description='Change directory', layout=self.button_layout)
        self.changedir.on_click(self.handle_changedir)
        # select button
        import copy
        ok_layout = cloneLayout(self.button_layout)
        ok_layout.margin = 'auto 40px 5px';
        ok_layout.border = "1px solid blue"
        self.ok = ipyw.Button(description='Select', layout=ok_layout)
        self.ok.on_click(self.validate)
        right_vbox = ipyw.VBox(children=[self.changedir, self.ok])
        select_panel = ipyw.HBox(
            children=[left_vbox, right_vbox],
            layout=ipyw.Layout(border='1px solid lightgrey', margin='5px', padding='10px')
        )
        body = ipyw.VBox(children=[toolbar, select_panel], layout=self.layout)
        self.footer.value = ""
        return body

    def createFilterWidget(self):
        if 'All' not in self.filters: self.filters.update(All=['*.*'])
        self.cur_filter = self.cur_filter or self.filters[self.default_filter or 'All']
        self.filter_widget = ipyw.Dropdown(
            options=self.filters,
            value=self.cur_filter,
            layout=ipyw.Layout(align_self='flex-end', width='15%'))
        self.filter_widget.observe(self.handle_filter_changed, names='value')
        return

    def getFilteredEntries(self):
        curdir = self.curdir
        cur_filter = self.filter_widget.value

        if type(cur_filter) is list:
            cur_filter = cur_filter[0]

        list_files = glob.glob(os.path.join(curdir, cur_filter))
        # filter out dirs, they will be added below
        list_files = filter(lambda o: not os.path.isdir(o), list_files)
        list_files = list(map(os.path.basename, list_files))
        list_dirs = [o for o in os.listdir(curdir) if os.path.isdir(os.path.join(curdir, o))]
        self.footer.value += '<p>' + ' '.join(list_dirs) + '</p>'
        entries = list_dirs + list_files
        return entries

    def handle_filter_changed(self, value):
        self.cur_filter = value['new']
        self.changeDir(self.curdir)

    def disable(self):
        disable(self.panel)
        return

    def enable(self):
        enable(self.panel)
        return

    def changeDir(self, path):
        close(self.body)
        self.body = self.createBody(path)
        self.panel.children = [self.header, self.body, self.footer]
        return

    def handle_jumpto(self, s):
        v = self.jumpto_input.value
        if not os.path.isdir(v): return
        self.changeDir(v)
        return

    def handle_newdir(self, s):
        v = self.newdir_input.value
        path = os.path.join(self.curdir, v)
        try:
            os.makedirs(path)
        except:
            return
        self.changeDir(path)
        return

    def handle_changedir(self, s):
        v = self.select.value
        v = del_ftime(v)
        if self.multiple:
            if len(v) != 1:
                js_alert("Please select a directory")
                return
            v = v[0]
        p = os.path.abspath(os.path.join(self.curdir, v))
        if os.path.isdir(p):
            self.changeDir(p)
        return

    def validate(self, s):
        v = self.select.value
        v = del_ftime(v)
        # build paths
        if self.multiple:
            vs = v
            paths = [os.path.join(self.curdir, v) for v in vs]
        else:
            path = os.path.join(self.curdir, v)
            paths = [path]
        # check type
        if self.type == 'file':
            for p in paths:
                if not os.path.isfile(p):
                    js_alert("Please select file(s)")
                    return
        else:
            assert self.type == 'directory'
            for p in paths:
                if not os.path.isdir(p):
                    js_alert("Please select directory(s)")
                    return
        # set output
        if self.multiple:
            self.selected = paths
        else:
            self.selected = paths[0]

        # clean up unless user choose not to
        if not self.stay_alive: self.remove()

        # next step
        if self.next:
            self.next(self.selected)
        return

    def show(self):
        display(self.panel)
        return

    def remove(self):
        close(self.panel)


# XXX css for big select area XXX
display(HTML("""
<style type="text/css">
.jupyter-widgets select option {font-family: "Lucida Console", Monaco, monospace;}
div.output_subarea {padding: 0px;}
div.output_subarea > div {margin: 0.4em;}
</style>
"""))


def js_alert(m):
    js = "<script>alert('%s');</script>" % m
    display(HTML(js))
    return

def cloneLayout(l):
    c = ipyw.Layout()
    for k,v in l.get_state().items():
        if k.startswith('_'): continue
        setattr(c, k, v)
    return c

def close(w):
    "recursively close a widget"
    recursive_op(w, lambda x: x.close())
    return

def disable(w):
    "recursively disable a widget"
    def _(w):
        w.disabled = True
    recursive_op(w, _)
    return

def enable(w):
    "recursively enable a widget"
    def _(w):
        w.disabled = False
    recursive_op(w, _)
    return

def recursive_op(w, single_op):
    if hasattr(w, 'children'):
        for c in w.children:
            recursive_op(c, single_op)
            continue
    single_op(w)
    return

def close(w):
    "recursively close a widget"
    if hasattr(w, 'children'):
        for c in w.children:
            close(c)
            continue
    w.close()
    return

def create_file_times(paths):
    """returns a list of file modify time"""
    ftimes = []
    for f in paths:
        try:
            if os.path.isdir(f):
                ftimes.append("Directory")
            else:
                ftime_sec = os.path.getmtime(f)
                ftime_tuple = time.localtime(ftime_sec)
                ftime = time.asctime(ftime_tuple)
                ftimes.append(ftime)
        except OSError:
            ftimes.append("Unknown or Permission Denied")
    return ftimes


def create_nametime_labels(entries, ftimes):
    if not entries:
        return []
    max_len = max(len(e) for e in entries)
    n_spaces = 5
    fmt_str = ' %-' + str(max_len + n_spaces) + "s|" + ' ' * n_spaces + '%s'
    label_list = [fmt_str % (e, f) for e, f in zip(entries, ftimes)]
    return label_list


def del_ftime(file_label):
    """file_label is either a str or a tuple of strings"""
    if isinstance(file_label, tuple):
        return tuple(del_ftime(s) for s in file_label)
    else:
        file_label_new = file_label.strip()
        if file_label_new != "." and file_label_new != "..":
            file_label_new = file_label_new.split("|")[0].rstrip()
    return (file_label_new)


class FileSelection(object):

    next = None

    def __init__(self,
                 working_dir='./',
                 filter='',
                 default_filter=None,
                 next=None,
                 instructions=None,
                 multiple=True):
        self.working_dir = working_dir
        self.instuctions = instructions
        self.filter = filter
        self.default_filter = default_filter
        self.next = next
        self.multiple = multiple

        self.progress_bar_output = ipyw.Output()  # reserve space for progress bar

    def select_file_help(self, value):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/file_selector/#select_profile")

    def load_files(self, files):
        o_norm = Normalization()
        files.sort()
        with self.progress_bar_output:
            self.progress_bar_output.clear_output()
            o_norm.load(file=files, notebook=False)
        self.progress_bar_output.clear_output()
        self.data_dict = o_norm.data

    def load_files_without_checking_shape(self, files):
        o_norm = Normalization()
        files.sort()
        with self.progress_bar_output:
            self.progress_bar_output.clear_output()
            o_norm.load(file=files, notebook=True, check_shape=False)
        self.data_dict = o_norm.data

    def select_data(self, check_shape=True):
        help_ui = widgets.Button(description="HELP",
                                 button_style='info')
        help_ui.on_click(self.select_file_help)
        status_bar = ipyw.VBox([help_ui, self.progress_bar_output])
        display(status_bar)

        instructions = self.instuctions if self.instuctions else "Select Images ..."

        if check_shape:

            next = self.next if self.next else self.load_files
            if self.filter:
                self.files_ui = fileselector.FileSelectorPanel(instruction=instructions,
                                                               start_dir=self.working_dir,
                                                               next=next,
                                                               filters=self.filter,
                                                               default_filter=self.default_filter,
                                                               multiple=self.multiple)
            else:
                 self.files_ui = fileselector.FileSelectorPanel(instruction=instructions,
                                                                start_dir=self.working_dir,
                                                                next=next,
                                                                multiple=self.multiple)

        else:

            next = self.next if self.next else self.load_files_without_checking_shape
            if self.filter:
                self.files_ui = fileselector.FileSelectorPanel(instruction=instructions,
                                                               start_dir=self.working_dir,
                                                               next=next,
                                                               filters=self.filter,
                                                               default_filter=self.default_filter,
                                                               multiple=self.multiple)
            else:
                self.files_ui = fileselector.FileSelectorPanel(instruction=instructions,
                                                               start_dir=self.working_dir,
                                                               next=next,
                                                               multiple=self.multiple)

        self.files_ui.show()


class FileSelectorPanelWithJumpFolders:

    def __init__(
            self,
            instruction="Select Output Folder",
            start_dir=".",
            type='file',
            next=None,
            multiple=False,
            newdir_toolbar_button=False,
            custom_layout=None,
            filters=dict(), default_filter=None,
            stay_alive=False,
            ipts_folder='./',
            show_jump_to_share=True,
            show_jump_to_home=True,
    ):
        self.type = type
        self.next = next

        def display_file_selector_from_shared(ev):
            start_dir = os.path.join(ipts_folder, 'shared')
            self.output_folder_ui.remove()
            self.display_file_selector(instruction=instruction,
                                       start_dir=start_dir,
                                       type=type,
                                       next=next,
                                       multiple=multiple,
                                       newdir_toolbar_button=newdir_toolbar_button,
                                       custom_layout=custom_layout,
                                       filters=filters,
                                       stay_alive=stay_alive,
                                       )

        def display_file_selector_from_home(ev):
            start_dir = os.path.expanduser("~")
            self.output_folder_ui.remove()
            self.display_file_selector(instruction=instruction,
                                       start_dir=start_dir,
                                       type=type,
                                       next=next,
                                       multiple=multiple,
                                       newdir_toolbar_button=newdir_toolbar_button,
                                       custom_layout=custom_layout,
                                       filters=filters,
                                       stay_alive=stay_alive,
                                       )

        ipts = os.path.basename(ipts_folder)

        button_layout = widgets.Layout(width='30%',
                                       border='1px solid gray')

        list_buttons = []
        if show_jump_to_share:
            share_button = widgets.Button(description="Jump to {} Shared Folder".format(ipts),
                                          button_style='success',
                                          layout=button_layout)
            share_button.on_click(display_file_selector_from_shared)
            list_buttons.append(share_button)

        if show_jump_to_home:
            home_button = widgets.Button(description="Jump to My Home Folder",
                                         button_style='success',
                                         layout=button_layout)
            home_button.on_click(display_file_selector_from_home)
            list_buttons.append(home_button)

        hbox = widgets.HBox(list_buttons)

        # if show_jump_to_home and show_jump_to_share:
        #
        #     hbox = widgets.HBox([widgets.Button(description="Jump to {} Shared Folder".format(ipts),
        #                                         button_style='success',
        #                                         layout=button_layout),
        #                          widgets.Button(description="Jump to My Home Folder",
        #                                         button_style='success',
        #                                         layout=button_layout)])
        #     go_to_shared_button_ui = hbox.children[0]
        #     go_to_home_button_ui = hbox.children[1]
        #
        #     go_to_shared_button_ui.on_click(display_file_selector_from_shared)
        #     go_to_home_button_ui.on_click(display_file_selector_from_home)

        display(hbox)
        self.shortcut_buttons = hbox # use this reference to hide those buttons

        self.display_file_selector(instruction=instruction,
                                   start_dir=start_dir,
                                   type=self.type,
                                   next=next,
                                   multiple=multiple,
                                   newdir_toolbar_button=newdir_toolbar_button,
                                   custom_layout=custom_layout,
                                   filters=filters,
                                   default_filter=default_filter,
                                   stay_alive=stay_alive)

    def display_file_selector(self, instruction="",
                                    start_dir="./",
                                    multiple=False,
                                    default_filter=None,
                                    next=None,
                                    newdir_toolbar_button=False,
                                    type='file',
                                    custom_layout=None,
                                    filters=None,
                                    stay_alive=False):

        self.output_folder_ui = fileselector.FileSelectorPanel(instruction=instruction,
                                                                     start_dir=start_dir,
                                                                     multiple=multiple,
                                                                     next=next,
                                                                     newdir_toolbar_button=newdir_toolbar_button,
                                                                     type=type,
                                                                     custom_layout=custom_layout,
                                                                     default_filter=default_filter,
                                                                     filters=filters,
                                                                     stay_alive=stay_alive)

        self.output_folder_ui.show()
