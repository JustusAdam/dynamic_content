from . import database_operations
from core import Modules
from framework.html_elements import ContainerElement
from framework.page import Component

__author__ = 'justusadam'


class CommonsHandler:

    # used to identify items with internationalization
    com_type = 'commons'

    source_table = 'commons_config'

    dn_ops = None

    # temporary
    language = 'english'

    def __init__(self, machine_name, show_title):
        self.name = machine_name
        self.show_title = show_title

    def get_display_name(self, item, language='english'):
        if not self.dn_ops:
            self.dn_ops = Modules()['internationalization'].Operations()
        return self.dn_ops.get_display_name(item, self.source_table, language)

    def wrap_content(self, content):
        if self.show_title:
            title = ContainerElement(self.get_display_name(self.name), html_type='h3')
        else:
            title = ''
        return ContainerElement(title, content, classes={self.name.replace('_', '-'), 'common'})

    @property
    def compiled(self):
        return None


class TextCommonsHandler(CommonsHandler):

    com_type = 'text'

    def __init__(self, machine_name, show_title):
        self.co = database_operations.CommonsOperations()
        super().__init__(machine_name, show_title)

    def get_content(self, name):
        return self.co.get_content(name, self.com_type)

    @property
    def compiled(self):
        obj = Component(self.name, self.wrap_content(self.get_content(self.name)))
        return obj


