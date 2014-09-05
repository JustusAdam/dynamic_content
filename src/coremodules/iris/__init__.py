from src.coremodules.iris.iris import EditIrisHandler, IrisContentHandler

__author__ = 'justusadam'


name = 'iris'

role = 'page_handler'


def content_handler_factory(url):
    if url.page_modifier == 'edit':
        return EditIrisHandler(url)
    else:
        return IrisContentHandler(url)