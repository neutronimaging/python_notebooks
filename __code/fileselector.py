import ipywidgets as ipyw
import os
import time
from IPython.core.display import HTML


class MyFileSelectorPanel:
    """Files and directories selector"""

    # If ipywidgets version 5.3 or higher is used, the "width="
    # statement should change the width of the file selector. "width="
    # doesn't appear to work in earlier versions.
    select_layout = ipyw.Layout(width="750px", height="260px")
    select_multiple_layout = ipyw.Layout(
        width="750px", height="260px", display="flex", flex_flow="column")
    button_layout = ipyw.Layout(margin="5px 40px")
    toolbar_button_layout = ipyw.Layout(margin="5px 10px", width="100px")
    toolbar_box_layout = ipyw.Layout(border='1px solid lightgrey', padding='3px', margin='5px 50px 5px 5px')
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
            custom_layout=None
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
        self.multiple = multiple
        self.newdir_toolbar_button = newdir_toolbar_button
        self.createPanel(os.path.abspath(start_dir))
        self.next = next
        return

    def activate_status(self, is_disabled=True):
        self.button_layout.disabled = is_disabled
        self.ok.disabled = is_disabled
        self.jumpto_input.disabled = is_disabled
        self.enterdir.disabled = is_disabled
        self.jumpto_button.disabled = is_disabled
        self.select.disabled = is_disabled

    def createPanel(self, curdir):
        self.header = ipyw.Label(self.instruction, layout=self.label_layout)
        self.footer = ipyw.HTML("")
        self.body = self.createBody(curdir)
        self.panel = ipyw.VBox(children=[self.header, self.body, self.footer])
        return

    def createBody(self, curdir):
        self.curdir = curdir
        self.footer.value = "Please wait..."
        # toolbar
        # "jump to"
        self.jumpto_input = jumpto_input = ipyw.Text(
            value=curdir, placeholder="", description="Location: ", layout=ipyw.Layout(width='500px')
        )
        jumpto_button = ipyw.Button(description="Jump", layout=self.toolbar_button_layout)
        jumpto_button.on_click(self.handle_jumpto)
        jumpto = ipyw.HBox(children=[jumpto_input, jumpto_button], layout=self.toolbar_box_layout)
        self.jumpto_button = jumpto
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
        # enter directory button
        self.enterdir = ipyw.Button(description='Enter directory', layout=self.button_layout)
        self.enterdir.on_click(self.handle_enterdir)
        # select button
        self.ok = ipyw.Button(description='Select', layout=self.button_layout)
        self.ok.on_click(self.validate)
        buttons = ipyw.HBox(children=[self.enterdir, self.ok])
        lower_panel = ipyw.VBox(children=[self.select, buttons],
                                layout=ipyw.Layout(border='1px solid lightgrey', margin='5px', padding='10px'))
        body = ipyw.VBox(children=[toolbar, lower_panel], layout=self.layout)
        self.footer.value = ""
        return body

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

    def handle_enterdir(self, s):
        v = self.select.value
        v = del_ftime(v)
        if self.multiple:
            if len(v) != 1:
                self.js_alert("Please select a directory")
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
                    self.js_alert("Please select file(s)")
                    return
        else:
            assert self.type == 'directory'
            for p in paths:
                if not os.path.isdir(p):
                    self.js_alert("Please select directory(s)")
                    return
        # set output
        if self.multiple:
            self.selected = paths
        else:
            self.selected = paths[0]
        # clean up
        # self.remove()  ## fileselector stays alive
        # next step
        if self.next:
            self.next(self.selected)
        return

    def show(self):
        display(self.panel)
        return

    def remove(self):
        close(self.panel)



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

