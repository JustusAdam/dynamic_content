from application.config import ModuleConfig
from application.fragments import AppFragment
from .content_handler import FieldBasedPageContent, EditFieldBasedContent, AddFieldBasedContentHandler
from .field import *
from . import database_operations as dbo

__author__ = 'justusadam'


class IrisApp(AppFragment):
    content_handlers = {
        'edit': EditFieldBasedContent,
        'show': FieldBasedPageContent,
        'access': FieldBasedPageContent,
        'add': AddFieldBasedContentHandler
    }
    field_handlers = {
        'access': BaseFieldHandler,
        'add': AddBaseFieldHandler,
        'edit': EditBaseFieldHandler
    }

    def __init__(self, config):
        super().__init__(config)

    def content_handler(self, url):
        return self.content_handlers[url.page_modifier]

    def field_handler(self, field_name, prefix, page_id, modifier):
        return self.field_handlers[modifier](prefix, page_id, field_name)

    def setup_fragment(self):
        from core.database_operations import ContentHandlers, ContentTypes

        name = 'iris'
        path_prefix = 'iris'

        ct = dbo.Pages()
        ct.init_tables()
        f = dbo.Fields()
        f.init_tables()
        conf = ct.config

        # add basic content handlers etc
        ContentHandlers().add_new('iris', name, path_prefix)
        ContentTypes().add('article', 'Simple Article', 'iris', 'active')
        f.add_field_type('body', 'Body', 'article', 'iris')

        # add admin pages

        # add some initial pages

        page_id = ct.add_page(
            **{k: conf['startpage'][k] for k in ['content_type', 'creator', 'page_title', 'published', 'page_type']})
        f.add_field(table='body', page_id=page_id, path_prefix=conf['startpage']['page_type'],
                    content=conf['startpage']['body'])

        page_id = ct.add_page('iris', 'article', 'Wuhuuu', 1, True)
        f.add_field('body', 'iris', page_id,
                    '<p>More content is good</p><iframe src="http://www.xkcd.com" height="840px" width="600px" seamless></iframe>')


class IrisConf(ModuleConfig):
    pass