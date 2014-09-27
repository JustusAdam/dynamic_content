from core.database_operations import Operations, escape

__author__ = 'justusadam'


class MenuOperations(Operations):

    _queries = {
        'mysql': {
            'get_items': 'select item_name, item_path, parent_item, weight from menu_items where enabled=true and menu={menu_name};',
            'add_menu_item': 'insert into menu_items (item_name, item_path, menu, enabled, tooltip, parent_item, weight) values ({item_name}, {item_path}, {menu}, {enabled}, {tooltip}, {parent_item}, {weight});',
            'toggle_enabled': 'update menu_items set enabled={enabled} where item_name={item_name} and menu={menu};',
            'add_menu': 'insert into menus (machine_name, enabled) values ({machine_name}, {enabled});'
        }
    }

    _tables = {'menu_items', 'menus'}

    def get_items(self, name):
        self.execute('get_items', menu_name=escape(name))
        return self.cursor.fetchall()

    def toggle_enabled(self, item, menu, state):
        self.execute('toggle_enabled', enabled=escape(state), item_name=escape(item), menu=escape(menu))

    def enable_item(self, item, menu):
        self.toggle_enabled(item, menu, True)

    def disable_item(self, item, menu):
        self.toggle_enabled(item, menu, False)

    def add_menu_item(self, item_name, item_path, menu, enabled, parent_item, weight, tooltip=''):
        if not tooltip:
            tooltip = item_path
        self.execute('add_menu_item', item_name=escape(item_name), item_path=escape(item_path), menu=escape(menu), enabled=escape(enabled), tooltip=escape(tooltip), parent_item=escape(parent_item), weight=escape(weight))

    def add_menu(self, machine_name, enabled):
        self.execute('add_menu', machine_name=escape(machine_name), enabled=escape(enabled))


class CommonsOperations(Operations):

    _queries = {
        'mysql': {
            'add_content': 'insert into com_{com_type} (machine_name, content) values ({machine_name}, {content});',
            'add_com_table': 'create table com_{com_type} (id int unsigned not null unique auto_increment primary key, machine_name varchar(200) not null unique, content {spec});',
            'get_content': 'select content from com_{com_type} where machine_name={machine_name};'
        }
    }

    _tables = ['com_text']

    def add_content(self, com_type, element_name, content):
        self.execute('add_content', com_type=com_type, machine_name=escape(element_name), content=escape(content))

    def add_com_table(self, com_type, spec):
        self.execute('add_com_table', com_type=com_type, spec=spec)

    def get_content(self, machine_name, com_type):
        self.execute('get_content', machine_name=escape(machine_name), com_type=com_type)
        return self.cursor.fetchone()[0]