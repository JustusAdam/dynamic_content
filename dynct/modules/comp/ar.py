from dynct.backend.ar.base import ARObject

__author__ = 'justusadam'


class CommonsConfig(ARObject):
    _table = 'commons_config'

    def __init__(self, element_name, element_type, handler_module, show_title, access_type):
        super().__init__()
        self.element_name = element_name
        self.element_type = element_type
        self.handler_module = handler_module
        self.show_title = show_title
        self.access_type = access_type


class Common(ARObject):
    _table = 'regions'

    def __init__(self, item_name, region, weight, theme):
        super().__init__()
        self.item_name = item_name
        self.region = region
        self.weight = weight
        self.theme = theme


class CommonsAccess(ARObject):
    _table = 'commons_custom_access'