from .content_handler import FieldBasedPageContent, EditFieldBasedContent, AddFieldBasedContentHandler
from . import field
from . import database_operations as dbo

__author__ = 'justusadam'

name = 'iris'

role = 'page_handler'

path_prefix = 'iris'


def content_handler(url):
  handlers = {
    'edit': EditFieldBasedContent,
    'show': FieldBasedPageContent,
    'add': AddFieldBasedContentHandler
  }
  return handlers[url.page_modifier]


def field_handler(field_name, prefix, page_id, modifier):
  handlers = {
    'access': field.BaseFieldHandler,
    'add': field.AddBaseFieldHandler,
    'edit': field.EditBaseFieldHandler
  }
  return handlers[modifier](prefix, page_id, field_name)


def post_handler(url):
  handlers = {
    'add': None,
    'edit': None
  }
  return handlers[url.page_modifier]


def prepare():
  from core.database_operations import ContentHandlers, ContentTypes
  ct = dbo.Pages()
  ct.init_tables()
  f = dbo.Fields()
  f.init_tables()
  conf = ct.config

  # add basic content handlers etc
  ContentHandlers().add_new('iris', name, path_prefix)
  ContentTypes().add('article', 'Simple Article', 'iris', 'active')
  f.add_field_type('body', 'Body', 'article', 'iris')


  page_id = ct.add_page(
    **{k: conf['startpage'][k] for k in ['content_type', 'creator', 'page_title', 'published', 'page_type']})
  f.add_field(table='body', page_id=page_id, path_prefix=conf['startpage']['page_type'],
              content=conf['startpage']['body'])

  page_id = ct.add_page('iris', 'article', 'Wuhuuu', 1, True)
  f.add_field('body', 'iris', page_id,
              '<p>More content is good</p><iframe src="http://www.xkcd.com" height="840px" width="600px" seamless></iframe>')
