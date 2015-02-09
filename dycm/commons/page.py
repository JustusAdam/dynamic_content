__author__ = 'Justus Adam'
__version__ = '0.1'


class Component:
    def __init__(self, content, title='', stylesheets=set(), metatags=set(), scripts=set()):
        self.content = content
        self._stylesheets = stylesheets
        self._metatags = metatags
        self._scripts = scripts
        self.title = title

    @property
    def stylesheets(self):
        return self._stylesheets

    @stylesheets.setter
    def stylesheets(self, val):
        if isinstance(val, set):
            self._stylesheets = val
        elif isinstance(val, (list, tuple)):
            self._stylesheets = set(val)
        elif isinstance(val, str):
            self._stylesheets = {val}

    @property
    def metatags(self):
        return self._metatags

    @metatags.setter
    def metatags(self, val):
        if isinstance(val, set):
            self._metatags = val
        elif isinstance(val, (list, tuple)):
            self._metatags = set(val)
        elif isinstance(val, str):
            self._metatags = {val}

    @property
    def scripts(self):
        return self._scripts

    @scripts.setter
    def scripts(self, val):
        if isinstance(val, set):
            self._scripts = val
        elif isinstance(val, (list, tuple)):
            self._scripts = set(val)
        elif isinstance(val, str):
            self._scripts = {val}

    def __str__(self):
        return str(self.content)
