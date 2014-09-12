"""
Defines structures used to hold data that is being transmitted between modules and handlers.
"""

__author__ = 'justusadam'


class Component:

    def __init__(self, title, content='', stylesheets=set(), metatags=set(), scripts=set()):
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
        if isinstance(val, (list, tuple, str)):
            self._stylesheets = set(val)
        else:
            self._stylesheets = val

    @property
    def metatags(self):
        return self._metatags

    @metatags.setter
    def metatags(self, val):
        self._metatags = val

    @property
    def scripts(self):
        return self._scripts

    @scripts.setter
    def scripts(self, val):
        self._scripts = val

class Page(Component):
    def __init__(self, url, title='', content='', stylesheets=set(), metatags=set(), scripts=set(), show_title=True):
        super().__init__(title, content, stylesheets, metatags, scripts)
        self._url = url
        self.show_title = show_title
        self.used_theme = 'active'