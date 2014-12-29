from dynct.modules import i18n
from dynct.util import html
from dynct.modules.comp import page
from . import model

__author__ = 'justusadam'

ACCESS_DEFAULT_GRANTED = 0


class Commons:
    # used to identify items with i18n
    com_type = 'commons'

    source_table = 'commons_config'

    dn_ops = None

    # temporary
    language = 'english'

    def __init__(self, conf:model.CommonsConfig, render_args, show_title, client):
        self.show_title = show_title
        self.client = client
        self.conf = conf
        self.name = self.conf.machine_name
        self.render_args = render_args

    @property
    def title(self):
        return i18n.translate(self.name, self.language)

    def wrap_content(self, content):
        if self.show_title:
            title = html.ContainerElement(self.title, html_type='h3')
        else:
            title = ''
        if isinstance(content, (list, tuple, set)):
            return html.ContainerElement(title, *content, classes={self.name.replace('_', '-'), 'common'})
        else:
            return html.ContainerElement(title, content, classes={self.name.replace('_', '-'), 'common'})

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
            obj = page.Component(self.wrap_content(self.get_content(self.name)))
            return obj
        else:
            return None