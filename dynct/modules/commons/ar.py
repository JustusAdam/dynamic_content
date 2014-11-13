from dynct.backend.ar import ARObject

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

    def __init__(self, display_name, item_path, menu, enabled, parent_item, weight, tooltip='', item_id=-1):
        super().__init__()
        self.display_name = display_name
        self.item_id = item_id
        self.item_path = item_path
        self.parent_item = parent_item
        self.weight = weight
        self.menu = menu
        self.enabled = enabled
        self.tooltip = tooltip


class CommonsConfig(ARObject):
    _table = 'commons_config'

    def __init__(self, element_name, element_type, handler_module, show_title, access_type, cid=-1):
        super().__init__()
        self.cid = cid
        self.element_name = element_name
        self.element_type = element_type
        self.handler_module = handler_module
        self.show_title = show_title
        self.access_type = access_type