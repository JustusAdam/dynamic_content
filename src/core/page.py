__author__ = 'justusadam'


class Component:

    def __init__(self, content='', stylesheets=set(), metatags=set(), scripts=set()):
        self.content = content
        self.stylesheets = stylesheets
        self.metatags = metatags
        self.scripts = scripts


class Page(Component):
    def __init__(self, url, content='', stylesheets=set(), metatags=set(), scripts=set()):
        super().__init__(content, stylesheets, metatags, scripts)
        self._url = url