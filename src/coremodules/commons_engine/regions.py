from . import database_operations
from core.modules import Modules
from framework.page import Component

__author__ = 'justusadam'


class RegionHandler:

    modules = Modules()

    operations = database_operations.RegionOperations()

    def __init__(self, region_name):
        self.name = region_name
        self.commons = self.get_all_commons()

    def get_all_commons(self):
        common_names = self.operations.get_commons(self.name)

        acc = []

        for item in common_names:
            acc.append(self.get_item(item))

        return acc

    def get_item(self, item_name):
        (handler_module, item_type) = self.operations.get_item_info(item_name)
        handler = self.modules[handler_module].common_handler(item_type, item_name)
        return Common(item_name, handler, item_type)

    def compile(self):
        region = Component(self.name)
        compiled = [item.compile() for item in self.commons]
        for item in compiled:
            region += item

        return region


class Common:

    def __init__(self, name, handler, item_type):
        self.name = name
        self.handler = handler
        self.item_type = item_type