from core.database_operations import Operations
from core.database import escape

__author__ = 'justusadam'


class ContentTypes(Operations):

    _queries = {
        'mysql': {
            'get_page_information': 'select content_type, page_title from {page_type} where id={page_id};',
            'get_theme': 'select theme from content_types where content_type_name={content_type};',
            'get_fields': 'select field_name, weight, machine_name, handler_module from page_fields where content_type={content_type};',
            'edit_page': 'update {page_type} set page_title={page_title}, published={published};',
            'add_page': 'insert into {page_type} (content_type, page_title, creator, published) values ({content_type}, {page_title}, {creator}, {published}); ',
            'get_new_id': 'select id from {page_type} where content_type={content_type} and page_title={page_title} and creator={creator} and published={published} order by id desc limit 1;',
            'largest_id': 'select id from {table} order by id desc limit 1;'
        }
    }

    def get_page_information(self, page_type, page_id):
        self.execute('get_page_information', page_type=page_type, page_id=escape(page_id))
        return self.cursor.fetchone()

    def get_theme(self, content_type):
        self.execute('get_theme', content_type=escape(content_type))
        return self.cursor.fetchone()[0]

    def get_fields(self, content_type):
        self.execute('get_fields', content_type=escape(content_type))
        return self.cursor.fetchall()

    def edit_page(self, page_type, page_title, published):
        self.execute('edit_page', page_type=page_type, page_title=escape(page_title), published=escape(published))

    def add_page(self, page_type, content_type, page_title, creator, published):
        values = dict(page_type=page_type, content_type=escape(content_type), page_title=escape(page_title), creator=escape(creator), published=escape(published))
        self.execute('add_page', **values)
        self.execute('get_new_id', **values)
        return self.cursor.fetchone()[0]

    def get_largest_id(self, table):
        self.execute('largest_id', table=table)
        return self.cursor.fetchone()[0]


class Fields(Operations):

    _queries = {
        'mysql': {
            'get_content': 'select content from {table} where page_id={page_id} and path_prefix={path_prefix};',
            'alter_content': 'update {table} set content={content} where page_id={page_id} and path_prefix={path_prefix};',
            'add_field': 'insert into {table} (page_id, content, path_prefix) values ({page_id}, {content}, {path_prefix});'
        }
    }

    def get_content(self, table, path_prefix, page_id):
        self.execute('get_content', table=table, page_id=escape(page_id), path_prefix=escape(path_prefix))
        return self.cursor.fetchone()[0]

    def alter_content(self, table, path_prefix, page_id, content):
        self.execute('alter_content', table=table, page_id=escape(page_id), content=escape(content), path_prefix=escape(path_prefix))

    def add_field(self, table, path_prefix, page_id, content):
        self.execute('add_field', table=table, page_id=escape(page_id), content=escape(content), path_prefix=escape(path_prefix))
