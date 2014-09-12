from core.database_operations import Operations
from core.database import escape

__author__ = 'justusadam'


class ContentTypes(Operations):

    _queries = {
        'mysql': {
            'get_page_information': 'select content_type, page_title from {page_type} where id={page_id};',
            'get_theme': 'select theme from content_types where content_type_name={content_type}:',
            'get_fields': 'select field_name, weight, machine_name, handler_module from page_fields where content_type={content_type};',
            'edit_page': 'update {page_type} set page_title={page_title}, published={published};',
            'add_page': 'insert into {page_type} (id, content_type, page_title, creator, published) values ({page_id}, {content_type}, {page_title}, {creator}, {published});'
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

    def add_page(self, page_type, page_id, content_type, page_title, creator, published):
        self.execute('add_page', page_type=page_type, page_id=escape(page_id), content_type=escape(content_type), page_title=escape(page_title), creator=escape(creator), published=escape(published))


class Fields(Operations):

    pass