__author__ = 'justusadam'

import unittest

from core.database import Database


class generalIrisTesting(unittest.TestCase):
    def setUp(self):
        db = Database()
        db.insert('iris', ('id', 'content_type', 'page_title', 'published', 'creator'), ('1', 'test_type', 'helloo', '1', '1'))
        #db.insert('content_handlers', ('handler_module', 'path_prefix'), ('iris', 'iris'))
        db.insert('page_fields', ('field_name', 'content_type', 'handler_module', 'weight'), ('body', 'test_type', 'iris', '1'))
        #db.drop_tables('body')
        # field_table = {
        #     'table_name': 'body',
        #     'columns': [
        #         'id int unsigned not null auto_increment unique primary key',
        #         'page_id int unsigned not null unique',
        #         'content text'
        #     ]
        # }
        #db.create_table(**field_table)
        db.insert('body', ('page_id', 'content'), ('1', 'Testcontent, lorem ipsum bla bla bla'))

    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
