# Allows Python 3-style division in Python 2.7

import ipywidgets as ipyw
from traitlets import Unicode

from . import base


@ipyw.register("ipywe.VtkJs")
class VtkJs(base.DOMWidget):
    _view_name = Unicode("VtkJsView").tag(sync=True)
    _model_name = Unicode("VtkJsModel").tag(sync=True)

    url = Unicode("").tag(sync=True)

    def __init__(self, url=None):
        super().__init__()
        self.url = url
