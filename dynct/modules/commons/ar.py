from dynct.backend.ar.base import ARObject

__author__ = 'justusadam'


def com(name):
    class Common(ARObject):
        _table = 'com_' + name

        def __init__(self, machine_name, content, id=-1):
            super().__init__()
            self.id = id
            self.machine_name = machine_name
            self.content = content
    return Common


class Menu(ARObject):
    _table = 'menus'

    def __init__(self, machine_name, enabled, id=-1):
        super().__init__()
        self.id = id
        self.machine_name = machine_name
        self.enabled = enabled


class MenuItem(ARObject):
    _table = 'menu_items'

    def __init__(self, item_name, item_path, menu, enabled, parent_item, weight, tooltip='', id=-1):
        super().__init__()
        self.id = id
        self.item_name = item_name
        self.item_path = item_path
        self.parent_item = parent_item
        self.weight = weight
        self.menu = menu
        self.enabled = enabled
        self.tooltip = tooltip