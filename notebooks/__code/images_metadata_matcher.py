try:
    from ipywidgets import widgets
except:
    pass


class ImagesMetadataMatcher:

    def __init__(self, working_dir='./'):
        self.working_dir = working_dir