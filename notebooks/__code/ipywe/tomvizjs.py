# Allows Python 3-style division in Python 2.7

import ipywidgets as ipyw
from traitlets import Unicode

from . import base


@ipyw.register("ipywe.TomvizJs")
class TomvizJs(base.DOMWidget):
    _view_name = Unicode("TomvizJsView").tag(sync=True)
    _model_name = Unicode("TomvizJsModel").tag(sync=True)

    url = Unicode("").tag(sync=True)

    def __init__(self, url=None):
        super(TomvizJs, self).__init__()
        self.url = url
