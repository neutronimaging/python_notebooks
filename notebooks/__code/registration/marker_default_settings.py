import numpy as np
import pyqtgraph as pg


class MarkerDefaultSettings:
    x = 0
    y = 0

    width = 50
    height = 50

    color = {'white' : pg.mkPen('w', width=2),
             'yellow': pg.mkPen('y', width=2),
             'green' : pg.mkPen('g', width=2),
             'red'   : pg.mkPen('r', width=2),
             'blue'  : pg.mkPen('b', width=2),
             'cyan'  : pg.mkPen('c', width=2),
             'black' : pg.mkPen('k', width=2),
             }

    color_html = {'white' : 'ffffff',
                  'yellow': 'ffff00',
                  'green' : '00ff00',
                  'red'   : 'ff0000',
                  'blue'  : '0000ff',
                  'cyan'  : '00ffff',
                  'black' : '000000',
                  }

    def __init__(self, image_reference=None):
        if not (image_reference is None):
            [height, width] = np.shape(image_reference)
            self.x = int(width / 2)
            self.y = int(height / 2)

