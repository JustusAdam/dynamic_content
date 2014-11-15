from dynct.backend.ar import ARObject

__author__ = 'justusadam'


class ContentTypes(ARObject):
    _table = 'content_types'

    def __init__(self, content_type_name, display_name, content_handler, theme, description='', id=-1):
        self.content_handler = content_handler
        self.content_type_name = content_type_name
        self.display_name = display_name
        self.theme = theme
        self.description = description
        self.id = id


class Alias(ARObject):
    _table = 'alias'

    def __init__(self, source_url, alias, id=-1):
        self.source_url = source_url
        self.alias = alias
        self.id = id


class ContentHandler(ARObject):
    _table = 'content_handlers'

    def __init__(self, handler_module, handler_name, path_prefix, id=-1):
        self.handler_module = handler_module
        self.handler_name = handler_name
        self.path_prefix = path_prefix
        self.id = id


