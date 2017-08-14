import os

def format_directory(function):
    '''
    This decorator will make sure the directory format is correct for the right
    os system. On Mac, pyqt does not like seing the '\' replacing the white spaces.
    '''
    
    def new_function(dir=None, **kwargs):

        if dir is None:
            dir = './'
        elif dir == "":
            dir = './'
        else:
            if os.sys.platform == 'darwin':
                dir = dir.replace('\\','')
        return function(dir=dir, **kwargs)
                
    return new_function
        