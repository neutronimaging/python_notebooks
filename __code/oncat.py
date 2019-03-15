import getpass
import pyoncat

ID = '35b12436-99cc-4ee1-9faf-b2608ea3e6e6'


class Oncat:

    oncat = None

    def __init__(self):

        token_store = InMemoryTokenStore()

        self.oncat = pyoncat.ONCat(
                    'https://oncat.ornl.gov',
                    client_id=ID,
                    # scopes=['api:read',
                    client_secret=None,
                    token_getter=token_store.get_token,
                    token_setter=token_store.set_token,
                    flow=pyoncat.RESOURCE_OWNER_CREDENTIALS_FLOW,
                )

        self.username = getpass.getuser()

    def authentication(self):

        try:
            self.oncat.login(self.username,
                             getpass.getpass("Enter Password for {}:".format(self.username)))
        except:
            self.oncat = None
            return False

        return True



# Create token store
class InMemoryTokenStore(object):
    def __init__(self):
        self._token = None

    def set_token(self, token):
        self._token = token

    def get_token(self):
        return self._token