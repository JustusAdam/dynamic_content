from .content_handler import FieldBasedPageContentHandler, EditFieldBasedContentHandler, AddFieldBasedContentHandler
from .field_handler import BaseFieldHandler, EditBaseFieldHandler, AddBaseFieldHandler
from . import database_operations as dbo

from core.database_operations import ContentHandlers, ContentTypes

from core import InitMod

__author__ = 'justusadam'


name = 'iris'

role = 'page_handler'

path_prefix = 'iris'


def content_handler(url, parent_handler):
    handlers = {
        'edit': EditFieldBasedContentHandler,
        'show': FieldBasedPageContentHandler,
        'add': AddFieldBasedContentHandler
    }
    return handlers[url.page_modifier](url, parent_handler)


def field_handler(field_name, prefix, page_id, modifier):
    handlers = {
        'show': BaseFieldHandler,
        'add': AddBaseFieldHandler,
        'edit': EditBaseFieldHandler
    }
    return handlers[modifier](prefix, page_id, field_name)


class InitIris(InitMod):
    operations = {
        'ct': dbo.Pages,
        'field': dbo.Fields
    }

    def fill_tables(self, ops):
        conf = ops['ct'].config
        ContentHandlers().add_new('iris', name, path_prefix)
        ContentTypes().add('article', 'Simple Article', 'iris', 'active')
        ops['field'].add_field_type('body', 'Body', 'article', 'iris')
        page_id = ops['ct'].add_page(**{k:conf['startpage'][k] for k in ['content_type', 'creator', 'page_title', 'published', 'page_type']})
        ops['field'].add_field(table='body', page_id=page_id, path_prefix=conf['startpage']['page_type'], content=conf['startpage']['body'])

        page_id = ops['ct'].add_page('iris', 'article', 'Wuhuuu', 1, True)
        ops['field'].add_field('body', 'iris', page_id, '<p>More content is good</p><iframe src="http://www.xkcd.com" height="840px" width="600px" seamless></iframe>')


init_class = InitIris