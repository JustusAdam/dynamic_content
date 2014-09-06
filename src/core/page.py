__author__ = 'justusadam'


class Component:

    def __init__(self):
        self.content = ''
        self.stylesheets = set()
        self.metatags = set()
        self.scripts = set()


class Page(Component):
    def __init__(self, url):
        super().__init__()
        self._url = url