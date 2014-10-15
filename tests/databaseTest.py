from backend.database.mysql import Database as MySql

__author__ = 'justusadam'

import unittest


# class MyTestCase(unittest.TestCase):
# def test_something(self):
# self.assertEqual(True, False)
#
# class AutoIncrTest(unittest.TestCase):
#   def setUp(self):
#     self.db = Database()
#     try:
#       self.db.select('id', 'testtable')
#     except DatabaseError:
#       self.db.create_table('testtable',
#                            ['id int unsigned not null auto_increment primary key', 'title varchar(50) unique'])
#     try:
#       self.db.remove('testtable', 'title=' + escape('testtitle', 'utf-8'))
#     except DatabaseError:
#       pass
#
#   def tearDown(self):
#     del self.db

class ConnectionTest(unittest.TestCase):
  def setUp(self):
    self.db = Database()

  def testActiveConnection(self):
    self.assertIsInstance(self.db, type(MySql(None)))
    self.assertEqual(self.db.connected, True)

  def testDeadConnection(self):
    self.db.close()
    self.assertEqual(self.db.connected, False)


if __name__ == '__main__':
  unittest.main()
