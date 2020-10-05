import os

class UiBuilder(object):

    pyuic = ''
    
    def __init__(self, ui_name=''):
        self.define_pyuic_to_run()
        self.ui_name = os.path.abspath('ui/' + ui_name)
        [base, ext] = os.path.splitext(ui_name)
        py_name = base + '.py'
        self.py_name = os.path.abspath('__code/' + py_name)

        # run command
        print(self.pyuic + ' ' + self.ui_name + ' -o ' + self.py_name)
        os.system(self.pyuic + ' ' + self.ui_name + ' -o ' + self.py_name)
        
    def define_pyuic_to_run(self):
        try:
            from PyQt4 import QtGui
            self.pyuic = 'pyuic4'
        except:
            from PyQt5 import QtGui
            self.pyuic = 'pyuic5'
