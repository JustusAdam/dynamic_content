from dynct.backend.ar.base import ARObject

__author__ = 'justusadam'


class Category(ARObject):
    _table = 'admin_categories'

    def __init__(self, machine_name, display_name):
        self.machine_name = machine_name
        self.display_name = display_name
        super().__init__()


class Subcategory(ARObject):
    _table = 'admin_subcategories'

    def __init__(self, machine_name, display_name, category):
        self.machine_name = machine_name
        self.display_name = display_name
        self.category = category
        super().__init__()


class AdminPage(ARObject):
    _table = 'admin_pages'

    def __init__(self, machine_name, display_name, subcategory, handler_module):
        self.machine_name = machine_name
        self.display_name = display_name
        self.subcategory = subcategory
        self.handler_module = handler_module
        super().__init__()

    @property
    def category(self):
        return self.subcategory