from core.database_operations import Operations, escape

__author__ = 'justusadam'


class MenuOperations(Operations):

    _queries = {
        'mysql': {
            'get_items': 'select (display_name, item_path) from menu_items where enabled=true and menu={menu_name};'
        }
    }

    def get_items(self, name):
        self.execute('get_items', menu_name=escape(name))
        return self.cursor.fetchall()