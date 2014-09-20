from core.database_operations import Operations, escape

__author__ = 'justusadam'


class RegionOperations(Operations):

    _queries = {
        'mysql': {
            'get_commons': 'select item_name from regions where region={region} and theme={theme} order by weight desc;',
            'get_all_items_info': 'select element_name, handler_module, element_type from commons_config where {pred}',
            'add_item_config': 'insert into commons_config (element_name, element_type, handler_module) values ({element_name}, {element_type}, {handler_module});',
            'add_item': 'insert into regions (item_name, region, weight, theme) values ({item_name}, {region}, {weight}, {theme});'
        }
    }

    _tables = {'commons_config', 'regions'}

    def get_commons(self, region_name, theme):
        self.execute('get_commons', region=escape(region_name), theme=escape(theme))
        return tuple(a[0] for a in self.cursor.fetchall())

    def get_all_items_info(self, item_names):
        pred = ' or '.join(['element_name=' + escape(a) for a in item_names])
        self.execute('get_all_items_info', pred=pred)
        return self.cursor.fetchall()

    def add_item_conf(self, element_name, element_type, handler_module):
        self.execute('add_item_config', element_name=escape(element_name), element_type=escape(element_type), handler_module=escape(handler_module))

    def add_item(self, item_name, region, weight, theme):
        self.execute('add_item', region=escape(region), item_name=escape(item_name), weight=escape(weight), theme=escape(theme))

    def move_item(self):
        pass