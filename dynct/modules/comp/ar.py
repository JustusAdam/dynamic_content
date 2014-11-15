from dynct.backend.ar.base import ARObject

__author__ = 'justusadam'


class Common(ARObject):
    _table = 'regions'

    def __init__(self, item_name, region, weight, theme, show_title, render_args, rid=-1):
        super().__init__()
        self.rid = rid
        self.item_name = item_name
        self.region = region
        self.weight = weight
        self.theme = theme
        self.show_title = show_title
        self.render_args = render_args


class CommonsAccess(ARObject):
    _table = 'commons_custom_access'