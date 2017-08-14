# coding: utf-8

import ipywidgets as ipyw
from IPython.display import display, HTML, clear_output

def js_alert(m):
    js = "<script>alert('%s');</script>" % m
    display(HTML(js))
    return

