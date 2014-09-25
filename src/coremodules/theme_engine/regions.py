from . import database_operations
from core.modules import Modules
from framework.base_handlers import CommonsHandler
from framework.html_elements import ContainerElement
from framework.page import Component

__author__ = 'justusadam'


class RegionHandler:

    modules = Modules()

    def __init__(self, region_name, region_config, theme, user, access_group):
        self.user_info = (user, access_group)
        self.operations = database_operations.RegionOperations()
        self.name = region_name
        self.theme = theme
        self.commons = self.get_all_commons(region_name, theme)
        self.config = region_config

    def get_all_commons(self, name, theme):
        region_info = self.operations.get_commons(name, theme)

        acc = []

        if region_info:
            info = {a[0]: a[1:] for a in self.get_items_info(region_info)}

            for item in region_info:
                acc.append(self.get_item(item, *self.user_info + info[item]))

        return acc

    def get_item(self, item_name, user, access_group, handler_module, item_type, show_title):
        show_title = show_title == 1
        handler = self.modules[handler_module].common_handler(item_type, item_name, show_title, user, access_group)
        assert isinstance(handler, CommonsHandler)
        return Common(item_name, handler, item_type)

    def get_items_info(self, items):
        return self.operations.get_all_items_info(items)

    def wrap(self, value):
        classes = ['region', 'region-' + self.name.replace('_', '-')]
        if 'classes' in self.config:
            if isinstance(self.config['classes'], str):
                classes.append(self.config['classes'])
            else:
                classes += self.config['classes']
        return ContainerElement(ContainerElement(*value, classes={'region-wrapper', 'wrapper'}), classes=set(classes))

    @property
    def compiled(self):
        stylesheets = []
        meta = []
        scripts = []
        cont_acc = []
        if self.commons:
            c = [item.handler.compiled for item in self.commons]
            for comp_item in c:
                stylesheets += comp_item.stylesheets
                meta += comp_item.metatags
                scripts += comp_item.metatags
                cont_acc.append(comp_item.content)
            content = self.wrap(cont_acc)
        else:
            content = ''

        return Component(self.name, content, stylesheets=stylesheets, metatags=meta, scripts=scripts)


class Common:

    def __init__(self, name, handler, item_type):
        self.name = name
        self.handler = handler
        self.item_type = item_type