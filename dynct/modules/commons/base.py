from dynct.modules import i18n
from dynct.modules.comp.html_elements import ContainerElement
from dynct.modules.comp.page import Component
from .ar import CommonsConfig

__author__ = 'justusadam'

ACCESS_DEFAULT_GRANTED = 0


class Commons:
    # used to identify items with i18n
    com_type = 'commons'

    source_table = 'commons_config'

    dn_ops = None

    # temporary
    language = 'english'

    def __init__(self, conf:CommonsConfig, render_args, show_title, client):
        self.show_title = show_title
        self.client = client
        self.conf = conf
        self.name = self.conf.element_name
        self.render_args = render_args

    @property
    def title(self):
        return i18n.get_display_name(self.name, self.source_table, self.language)

    def wrap_content(self, content):
        if self.show_title:
            title = ContainerElement(self.title, html_type='h3')
        else:
            title = ''
        if isinstance(content, (list, tuple, set)):
            return ContainerElement(title, *content, classes={self.name.replace('_', '-'), 'common'})
        else:
            return ContainerElement(title, content, classes={self.name.replace('_', '-'), 'common'})

    def get_content(self, name):
        return ''

    def check_permission(self, permission):
        if self.conf.access_type == ACCESS_DEFAULT_GRANTED:
            return True
        return self.client.check_permission(permission)

    def check_access(self):
        return self.check_permission('access common ' + self.name)

    def compile(self):
        if self.check_access():
            obj = Component(self.wrap_content(self.get_content(self.name)))
            return obj
        else:
            return None