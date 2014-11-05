from dynct.core.modules import Modules
from .html_elements import ContainerElement
from .page import Component
from . import database_operations
from . import ar

__author__ = 'justusadam'


class RegionHandler:
    modules = Modules()

    def __init__(self, region_name, region_config, theme, client):
        self.client = client
        # self.operations = database_operations.RegionOperations()
        self.name = region_name
        self.theme = theme
        self.commons = self.get_all_commons(region_name, theme)
        self.config = region_config

    def get_all_commons(self, name, theme):
        region_info = ar.Common.get_all(region=name, theme=theme)
        acc = [self.get_item(a) for a in self.get_items_info(region_info)]
        return acc

    def get_item(self, item:ar.CommonsConfig):
        show_title = item.show_title == 1
        handler = self.modules[item.handler_module].common_handler(item.element_type)(item.element_name, show_title, item.access_type,
                                                                         self.client)
        return Common(item.element_name, handler, item.element_type)

    def get_items_info(self, items):
        return [ar.CommonsConfig.get(element_name=a.item_name) for a in items]

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
                if comp_item:
                    stylesheets += comp_item.stylesheets
                    meta += comp_item.metatags
                    scripts += comp_item.metatags
                    cont_acc.append(comp_item.content)
            content = self.wrap(cont_acc)
        else:
            content = ''

        return Component(content, stylesheets=stylesheets, metatags=meta, scripts=scripts)


class Common:
    def __init__(self, name, handler, item_type):
        self.name = name
        self.handler = handler
        self.item_type = item_type