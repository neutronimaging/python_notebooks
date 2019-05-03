import getpass
import pyoncat
import re

from ipywidgets import widgets
from IPython.core.display import display

CLIENT_ID = '35b12436-99cc-4ee1-9faf-b2608ea3e6e6'


class Oncat:

    oncat = None

    def __init__(self):

        token_store = InMemoryTokenStore()

        self.oncat = pyoncat.ONCat(
                        'https://oncat.ornl.gov',
                        client_id=CLIENT_ID,
                        client_secret=None,
                        token_getter=token_store.get_token,
                        token_setter=token_store.set_token,
                        flow=pyoncat.RESOURCE_OWNER_CREDENTIALS_FLOW,
                        )
        self.username = getpass.getuser()

    def authentication(self):
        try:
            self.oncat.login(self.username,
                             str(getpass.getpass("Enter Password for {}:".format(self.username))))
        except:
            self.oncat = None

        return self.oncat


class GetEverything:

    def __init__(self,
                 instrument='CG1D',
                 facility='HFIR',
                 run='',
                 oncat=None):

        run = self.__remove_leading_backslash(run)

        self.datafiles = oncat.Datafile.retrieve(
            run,
            facility=facility,
            instrument=instrument)

    def __remove_leading_backslash(self, run):
        return run[1:]


class GetProjection:

    def __init__(self,
                 instrument='CG1D',
                 facility='HFIR',
                 list_files=[],
                 oncat=None,
                 projection=[],
                 with_progressbar=False):

        projection.append('ingested')

        if with_progressbar:
            box1 = widgets.HBox([widgets.Label("Retrieving Metadata ...",
                                               layout=widgets.Layout(width='30%')),
                                 widgets.IntProgress(max=len(list_files),
                                                     layout=widgets.Layout(width='70%'))])
            display(box1)
            slider = box1.children[1]

        self.datafiles = {}
        for _index, _file in enumerate(list_files):
            self.datafiles[_file] = oncat.Datafile.retrieve(_file,
                                                            facility=facility,
                                                            instrument=instrument,
                                                            projection=projection)

            if with_progressbar:
                slider.value = _index

        if with_progressbar:
            box1.close()


# Create token store
class InMemoryTokenStore(object):
    def __init__(self):
        self._token = None

    def set_token(self, token):
        self._token = token

    def get_token(self):
        return self._token
