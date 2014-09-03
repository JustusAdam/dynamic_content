__author__ = 'justusadam'


class Page:

    def __init__(self, url):
        self.content = None
        self.stylesheets = None
        self.metatags = None
        self.scripts = None
        self.url = url