from src.coremodules.iris.iris import EditIrisHandler, IrisPageHandler

__author__ = 'justusadam'


name = 'iris'

role = 'page_handler'


def page_handler_factory(page_id, url_tail, get_query):
    if url_tail[0] == 'edit':
        return EditIrisHandler(page_id, get_query)
    else:
        return IrisPageHandler(page_id,get_query)