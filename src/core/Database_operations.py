from core import database

__author__ = 'justusadam'


charset = 'utf-8'


def escape_item(item, c=charset):
    return database.escape_item(item, c)


class Operations:
    def __init__(self):
        self.db = database.Database()
        self.charset = 'utf-8'
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.commit()


class ContentHandlers(Operations):

    queries = {
        'add_new': 'replace into content_handlers (handler_module, handler_name, path_prefix) values ({handler_module}, {handler_name}, {path_prefix});',
        'get_by_prefix': 'select handler_module from content_handlers where path_prefix={path_prefix};'
    }

    def add_new(self, handler_name, handler_module, path_prefix):
        query = self.queries['add_new'].format(handler_module=escape_item(handler_module), handler_name=escape_item(handler_name), path_prefix=escape_item(path_prefix))
        self.cursor.execute(query)
        self.db.commit()

    def get_by_prefix(self, prefix):
        query = self.queries['get_by_prefix'].format(path_prefix=escape_item(prefix))
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]


class Modules(Operations):

    queries = {
        'get_id': 'select id from modules where module_name={module_name};'
    }

    def get_id(self, module_name):
        query = self.queries['get_id'].format(module_name=escape_item(module_name))
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]

    def create_multiple_tables(self, *tables):
        for table in tables:
            try:
                self.db.create_table(**table)
            except database.DatabaseError as error:
                print('Error in Database Module Operations (create_table)')
                print(error)

    def drop_tables(self, names):
        self.db.drop_tables(names)

    def insert_into_tables(self, values):
        if not isinstance(values, (tuple, list)):
            values = (values,)
        for value in values:
            self.db.insert(**value)

    def get_path(self, module):
        return self.db.select('module_path', 'modules', 'where module_name = ' + escape_item(module)).fetchone()[0]

    def set_active(self, module):
        self.db.update('modules', {'enabled': '1'}, 'module_name = ' + escape_item(module))

    def add_module(self, module_name, module_path, module_role):
        self.db.insert('modules', ('module_name', 'module_path', 'module_role'), (module_name, module_path, module_role))

    def update_path(self, module_name, path):
        self.db.update('modules', {'module_path': path}, 'module_name = ' + escape_item(module_name))

    def ask_active(self, module):
        return self.db.select('enabled', 'modules', 'where module_name = ' + escape_item(module)).fetchone()[0]

    def get_enabled(self):
        results =  self.db.select(('module_name', 'module_path'), 'modules', 'where enabled=' + escape_item(1)).fetchall()
        acc = []
        for module in results:
            acc.append({'name':module[0], 'path': module[1]})
        return acc


class Alias(Operations):

    def get_by_alias(self, alias):
        return self.db.select('source_url', 'alias', 'where alias = ' + escape_item(alias)).fetchone()[0]

    def get_by_source(self, source):
        return self.db.select('alias', 'alias', 'where source_url = ' + escape_item(source)).fetchone()[0]