from core.database_operations import Operations, escape

__author__ = 'justusadam'


class MenuOperations(Operations):

    _queries = {
        'mysql': {
            'get_items': 'select display_name, item_path from menu_items where enabled=true and menu={menu_name};'
        }
    }

    def get_items(self, name):
        self.execute('get_items', menu_name=escape(name))
        return self.cursor.fetchall()


class RegionOperations(Operations):

    _queries = {
        'mysql': {
            'get_commons': 'select item_name from regions where region={region} order by weight;',
            'get_item_info': 'select handler_module, item_type from common_elements where item_name={item_name};'
        }
    }

    def get_commons(self, region_name):
        self.execute('get_commons', region=region_name)
        return self.cursor.fetchall()

    def get_item_info(self, item_name):
        self.execute('get_item_info', item_name=item_name)
        return self.cursor.fetchone()