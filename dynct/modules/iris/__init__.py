from pathlib import Path
from .content_handler import IrisController
from . import field, ar
from dynct.util.config import read_config

__author__ = 'justusadam'

name = 'iris'

role = 'page_handler'

path_prefix = 'iris'


def admin_handler(h_name):
    return None


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
    from dynct.core.ar import ContentTypes, ContentHandler

    conf = read_config(Path(__file__).parent / 'config.json')
    ContentHandler('iris', name, path_prefix).save()
    ContentTypes('article', 'Simple Article', 'iris', 'active').save()
    ar.FieldConfig('body', 'Body', 'article', 'iris', 1, '')

    # add admin pages

    # add some initial pages


    p = ar.page(conf['startpage']['page_type'])(
        **{k: conf['startpage'][k] for k in ['content_type', 'page_title', 'creator', 'published']})
    p.save()
    page_id = p.get_id()
    ar.field('body')(page_id=page_id, path_prefix=conf['startpage']['page_type'],
                content=conf['startpage']['body']).save()

    p = ar.page('iris')('article', 'Wuhuuu', 1, True)
    p.save()
    page_id = p.get_id()
    ar.field('body')(page_id,
                '<p>More content is good</p><iframe src="http://www.xkcd.com" height="840px" width="600px" seamless></iframe>', 'iris').save()

