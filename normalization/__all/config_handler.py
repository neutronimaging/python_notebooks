try:
    from PyQt4.QtCore import QSettings
except ImportError:
    from PyQt5.QtCore import QSettings
    
def init_config():
    settings = QSettings('settings.ini', QSettings.IniFormat)
    
def save_config(key='', value='', group=''):
    settings = QSettings('settings.ini')
    if not (group == ''):
        settings.beginGroup(group)

    if value == '':
        value = None
    settings.setValue(key, value)
    
    if not (group == ''):
        settings.endGroup()
    
def load_config(key='', default_value='', group=''):
    settings = QSettings('settings.ini')
    if not (group == ''):
        settings.beginGroup(group)

    value = settings.value(key)
    settings.endGroup()
    if (value is None) or (value == 'None'):
        return default_value
    else:
        return value

    