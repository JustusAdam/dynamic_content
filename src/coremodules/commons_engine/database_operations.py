from core.database_operations import Operations, escape

__author__ = 'justusadam'


class MenuOperations(Operations):

    _queries = {
        'mysql': {
            'get_items': 'select item_name, item_path, parent_item, weight from menu_items where enabled=true and menu={menu_name};',
            'get_menu_info': 'select menu_name from menus where machine_name={machine_name};',
            'add_menu_item': 'insert into menu_items (item_name, display_name, item_path, menu, enabled, tooltip, parent_item, weight) values ({item_name}, {display_name}, {item_path}, {menu}, {enabled}, {tooltip}, {parent_item}, {weight});',
            'toggle_enabled': 'update menu_items set enabled={enabled} where item_name={item_name} and menu={menu};',
            'add_menu': 'insert into menus (machine_name, menu_name, enabled) values ({machine_name}, {menu_name}, {enabled});'
        }
    }

    _tables = {'menu_items', 'menus'}

    def get_items(self, name):
        self.execute('get_items', menu_name=escape(name))
        return self.cursor.fetchall()

    def get_menu_info(self, name):
        self.execute('get_menu_info',machine_name=escape(name))
        return self.cursor.fetchone()[0]

    def toggle_enabled(self, item, menu, state):
        self.execute('toggle_enabled', enabled=escape(state), item_name=escape(item), menu=escape(menu))

    def enable_item(self, item, menu):
        self.toggle_enabled(item, menu, True)

    def disable_item(self, item, menu):
        self.toggle_enabled(item, menu, False)

    def add_menu_item(self, item_name, display_name, item_path, menu, enabled, parent_item, weight, tooltip=''):
        if not tooltip:
            tooltip = item_path
        self.execute('add_menu_item', item_name=escape(item_name), display_name=escape(display_name), item_path=escape(item_path), menu=escape(menu), enabled=escape(enabled), tooltip=escape(tooltip), parent_item=escape(parent_item), weight=escape(weight))

    def add_menu(self, machine_name, menu_name, enabled):
        self.execute('add_menu', machine_name=escape(machine_name), menu_name=escape(menu_name), enabled=escape(enabled))

class CommonsOperations(Operations):

    _queries = {
        'mysql': {

        }
    }

