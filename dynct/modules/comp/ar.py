from dynct.backend.ar.base import ARObject

__author__ = 'justusadam'


class Common(ARObject):
    _table = 'regions'

    def __init__(self, item_name, region, weight, theme, rid=-1):
        super().__init__()
        self.rid = rid
        self.item_name = item_name
        self.region = region
        self.weight = weight
        self.theme = theme


class CommonsAccess(ARObject):
    _table = 'commons_custom_access'