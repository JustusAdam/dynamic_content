from . import database_operations
from core.modules import Modules
from framework.page import Component

__author__ = 'justusadam'


class RegionHandler:

    modules = Modules()

    def __init__(self, region_name, theme):
        self.operations = database_operations.RegionOperations()
        self.name = region_name
        self.theme = theme
        self.commons = self.get_all_commons(region_name, theme)

    def get_all_commons(self, name, theme):
        common_names = self.operations.get_commons(name, theme)

        acc = []

        if common_names:
            info = {a[0]: (a[1], a[2]) for a in self.get_items_info(common_names)}

            for item in common_names:
                acc.append(self.get_item(item, *info[item]))

        return acc

    def get_item(self, item_name, handler_module, item_type):
        handler = self.modules[handler_module].common_handler(item_type, item_name)
        return Common(item_name, handler, item_type)

    def get_items_info(self, items):
        return self.operations.get_all_items_info(items)

    @property
    def compiled(self):
        r = Component(self.name)
        cont = []
        if self.commons:
            c = [item.handler.compiled for item in self.commons]
            for comp_item in c:
                r.integrate(comp_item)
                cont.append(comp_item.content)
        r.content = cont

        return r


class Common:

    def __init__(self, name, handler, item_type):
        self.name = name
        self.handler = handler
        self.item_type = item_type