from .entity import EditEntityHandler, EntityPageHandler

__author__ = 'justusadam'


name = 'iris'

role = 'page_handler'


def page_handler_factory(page_id, url_tail, get_query):
    if url_tail[0] == 'edit':
        return EditEntityHandler(page_id, get_query)
    else:
        return EntityPageHandler(page_id,get_query)