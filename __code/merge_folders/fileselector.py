
# coding: utf-8

import os, glob, time
import ipywidgets as ipyw
from IPython.display import display, HTML, clear_output
# This try-except should not be necessary anymore.
# The testing is now done in ../tests.
try:
    from ._utils import js_alert
except Exception:
    # only used if testing in this directory without installing
    from _utils import js_alert

class FileSelectorPanel:

    """Files and directories selector
    """
    
    #If ipywidgets version 5.3 or higher is used, the "width="
    #statement should change the width of the file selector. "width="
    #doesn't appear to work in earlier versions.
    select_layout = ipyw.Layout(width="750px")
    select_multiple_layout = ipyw.Layout(width="750px", display="flex", flex_flow="column")
    button_layout = ipyw.Layout(margin="5px 40px")
    label_layout = ipyw.Layout(width="250px")
    layout = ipyw.Layout()
    
    def __init__(self, instruction, start_dir=".", type='file', next=None, multiple=False):
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
        """
        if not type in ['file', 'directory']:
            raise ValueError("type must be either file or directory")
        self.instruction = instruction
        self.type = type
        self.multiple = multiple
        self.createPanel(os.path.abspath(start_dir))
        self.next = next
        return

    def createPanel(self, curdir):
        self.curdir = curdir
        explanation = ipyw.Label(self.instruction,layout=self.label_layout)
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
        self.widgets = [explanation, self.select, buttons]
        self.panel = ipyw.VBox(children=self.widgets, layout=self.layout)
        return	
    
    def handle_enterdir(self, s):
        v = self.select.value
        v = del_ftime(v)
        if self.multiple:
            if len(v)!=1:
                js_alert("Please select a directory")
                return
            v = v[0]
        p = os.path.abspath(os.path.join(self.curdir, v))
        if os.path.isdir(p):
            self.remove()
            self.createPanel(p)
            self.show()
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
        # clean up
        self.remove()
        # next step
        if self.next:
            self.next(self.selected)

        _result = self.widgets[1].value
        _name_folder = [_folder.split('|')[0].strip() for _folder in _result]

        _str_name_of_folder = ", ".join(_name_folder)

        display(HTML('<span style="font-size: 20px; color:blue">You have selected ' + \
            str(len(_name_folder)) + ' folders [' + _str_name_of_folder + '] </span>')) 

        return

    def show(self):
        display(HTML("""
        <style type="text/css">
        .jupyter-widgets select option {
            font-family: "Lucida Console", Monaco, monospace;
        }
        </style>
        """))
        display(self.panel)

    def result(self):
        _result = self.widgets[1].value
        _name_folder = [_folder.split('|')[0].strip() for _folder in _result]
        return _name_folder

    def remove(self):
        for w in self.widgets: w.close()
        self.panel.close()


def create_file_times(paths):
    "returns a list of file modify time"
    ftimes = []
    for f in paths:
        if os.path.isdir(f):
            ftimes.append("Directory")
        else:
            ftime_sec = os.path.getmtime(f)
            ftime_tuple = time.localtime(ftime_sec)
            ftime = time.asctime(ftime_tuple)
            ftimes.append(ftime)
    return ftimes

def create_nametime_labels(entries, ftimes):
    if not entries: return []
    max_len = max(len(e) for e in entries)
    n_spaces = 5
    fmt_str = ' %-' + str(max_len+n_spaces) + "s|" + ' '*n_spaces + '%s'
    label_list = [fmt_str % (e, f) for e, f in zip(entries, ftimes)]
    return label_list

def del_ftime(file_label):
    "file_label is either a str or a tuple of strings"
    if isinstance(file_label, tuple):
        return tuple(del_ftime(s) for s in file_label)
    else:    
        file_label_new = file_label.strip()
        if file_label_new != "." and file_label_new != "..":
            file_label_new = file_label_new.split("|")[0].rstrip()
    return(file_label_new)

def test1():
    panel = FileSelectorPanel("instruction", start_dir=".")
    print('\n'.join(panel._entries))
    panel.handle_enterdir(".")
    return

def test2():
    s = " __init__.py          |     Tue Jun 13 23:24:05 2017"
    assert del_ftime(s) == '__init__.py'
    s = ' . '
    assert del_ftime(s) == '.'
    s = (" __init__.py          |     Tue Jan 13 23:24:05 2017",
         " _utils.py            |     Mon Feb 11 12:00:00 2017")
    dels = del_ftime(s)
    expected = ("__init__.py", "_utils.py")
    for e, r in zip(dels, expected):
        assert e == r
    return


def main():
    #test1()
    test2()
    return

if __name__ == '__main__': main()



