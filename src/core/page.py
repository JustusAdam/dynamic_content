__author__ = 'justusadam'


class Component:

    def __init__(self, content='', stylesheets=set(), metatags=set(), scripts=set()):
        self.content = content
        self.stylesheets = stylesheets
        self.metatags = metatags
        self.scripts = scripts


class Page(Component):
    def __init__(self, url, title='', content='', stylesheets=set(), metatags=set(), scripts=set(), show_title=True):
        super().__init__(content, stylesheets, metatags, scripts)
        self._url = url
        self.title = title
        self.show_title = show_title
        self.used_theme = 'active'