import unittest

from pymysql.connections import Connection

from dynct.backend.ar.data import Column
from dynct.backend.database import Database, escape
from dynct.backend.ar import base


__author__ = 'justusadam'


class ARTest(unittest.TestCase):
    def setUp(self):
        self.ar_db = base.VirtualDatabase(Database())

    def test_ar_database(self):
        test_table = 'cms_users'
        self.assertIsInstance(self.ar_db, base.VirtualDatabase)
        self.assertIsInstance(self.ar_db.database._connection, Connection)
        self.assertTrue(len(self.ar_db.database.show_columns(test_table)) > 0)

    def test_ar_table(self):
        test_table_name = 'access_group_permissions'
        test_table = self.ar_db.table(test_table_name)
        self.assertIsInstance(test_table, base.VirtualDBTable)

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
        self.assertEqual(testrow1.exists, True)
        self.assertEqual(testrow1['page_id'], 0)
        self.assertEqual(testrow1['content'], 'oergierngiernvienunerlwefnjewnjewnf')

    def testInsertion(self):
        table_name = 'body_data'
        table = self.ar_db.table(table_name)
        testrow1 = table.row()

        self.assertEqual(testrow1.exists, False)
        self.assertEqual(testrow1['content'], None)
        content = 'unittest test content'
        # date = datetime.datetime.utcnow()
        # testrow1['date_changed'] = date

        testrow1['content'] = content
        testrow1['page_id'] = 3

        self.assertRaises(ValueError, testrow1.save)
        path_prefix = 'unittest'
        testrow1['path_prefix'] = path_prefix
        testrow1.save()
        testrow2 = table.row(page_id=3, content=content)
        self.assertEqual(testrow2['content'], content)
        self.assertEqual(testrow2.exists, True)

        self.assertRaises(KeyError, testrow1.__setitem__, 'this fails', 'content')

        self.ar_db.database.remove(table_name, 'path_prefix=' + escape(path_prefix))

    def test_compound_table(self):
        test_table_names = ['cms_users', 'cms_user_auth', 'form_tokens']
        table = base.CompoundVirtualDBTable(self.ar_db, *test_table_names)
        result = table.keys()
        self.assertSetEqual(result, {'uid', 'id', 'username', 'email_address', 'token', 'salt', 'password'})


if __name__ == '__main__':
    unittest.main()