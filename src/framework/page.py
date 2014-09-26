"""
Defines structures used to hold data that is being transmitted between modules and handlers.
"""

__author__ = 'justusadam'


class Component:

    def __init__(self,content, stylesheets=set(), metatags=set(), scripts=set()):
        self.content = content
        self._stylesheets = stylesheets
        self._metatags = metatags
        self._scripts = scripts

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


class Page(Component):
    def __init__(self, url, content='', stylesheets=set(), metatags=set(), scripts=set(), show_title=True):
        super().__init__(content, stylesheets, metatags, scripts)
        self._url = url
        self.show_title = show_title