from core.database import DatabaseError, Database, escape

__author__ = 'justusadam'

import unittest


# class MyTestCase(unittest.TestCase):
#     def test_something(self):
#         self.assertEqual(True, False)

class AutoIncrTest(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        try:
            self.db.select('id', 'testtable')
        except DatabaseError:
            self.db.create_table('testtable', ['id int unsigned not null auto_increment primary key', 'title varchar(50) unique'])
        try:
            self.db.remove('testtable', 'title=' + escape('testtitle'))
        except DatabaseError:
            pass


    def test(self):
        id_value = self.db.retr_auto_incr_val('testtable')
        self.db.insert('testtable', 'title', 'testtitle')
        db_result = self.db.select('id', 'testtable', 'where title=' + escape('testtitle')).fetchone()[0]
        self.assertEqual(id_value, db_result)

    def tearDown(self):
        del self.db


if __name__ == '__main__':
    unittest.main()
