import unittest
from framework.shell.ar import base
from framework.shell.ar.data import Column
from framework.shell.database import Database
from pymysql.connections import Connection
import datetime

__author__ = 'justusadam'


class ARTest(unittest.TestCase):

  def setUp(self):
    self.ar_db = base.ARDatabase(Database())

  def test_ar_database(self):
    test_table = 'cms_users'
    self.assertIsInstance(self.ar_db, base.ARDatabase)
    self.assertIsInstance(self.ar_db.database._connection, Connection)
    self.assertTrue(len(self.ar_db.database.show_columns(test_table)) > 0)

  def test_ar_table(self):
    test_table_name = 'access_group_permissions'
    test_table = self.ar_db.table(test_table_name)
    self.assertIsInstance(test_table, base.ARTable)

  def test_table(self):
    test_table_name = 'cms_users'
    test_table = self.ar_db.table(test_table_name).columns
    keys = []
    for element in test_table:
      a = test_table[element]
      self.assertIsInstance(a, Column)
      if a.key:
        keys.append(element)
    real = test_table.db_keys()
    for key in keys:
      self.assertIn(key, real, msg=real)

  def testRetrieval(self):
    table = self.ar_db.table('body_data')
    testrow1 = table.row(id=6)
    self.assertEqual(testrow1['page_id'], 0)
    self.assertEqual(testrow1['content'], 'oergierngiernvienunerlwefnjewnjewnf')

  def testInsertion(self):
    table = self.ar_db.table('body_data')
    testrow1 = table.row()
    self.assertEqual(testrow1.exists, False)
    self.assertEqual(testrow1['content'], None)
    content = 'unittest test content'
    # date = datetime.datetime.utcnow()
    # testrow1['date_changed'] = date
    testrow1['content'] = content
    testrow1['page_id'] = 3
    self.assertRaises(ValueError, testrow1.save)
    testrow1['path_prefix'] = 'unittest'
    testrow1.save()
    testrow2 = table.row(page_id=3, content=content)
    self.assertEqual(testrow2['content'], content)
    self.assertEqual(testrow2.exists, True)


if __name__ == '__main__':
    unittest.main()