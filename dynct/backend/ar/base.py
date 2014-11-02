from itertools import chain

from .data import Column
from ..database import escape, DatabaseError, Database
from .data import Table


__author__ = 'justusadam'


class VirtualStorage(object):
    @property
    def db(self):
        return self.database

    def __init__(self, database):
        self.database = database

    def __del__(self):
        self.save()

    def save(self):
        pass


class VirtualDatabase(VirtualStorage):
    def __init__(self, database=None):
        if database is None:
            database = Database()
        super().__init__(database)

    def table(self, name):
        return SimpleVirtualDBTable(self, name)


class ARRow(dict, VirtualStorage):
    updated = []
    exists = False

    def __init__(self, table, autoretrieve : bool = True, **identifiers):

        super().__init__(**identifiers)
        VirtualStorage.__init__(self, table.database)
        self._has_keys = None
        self.ar_table = table
        self.table = table.table
        self.table_name = table.name

        if autoretrieve and self.has_key:
            self._get_data()

    @property
    def has_key(self):
        if self._has_keys is None:
            for column in self.table.values():
                if column.key:
                    if column.name in self:
                        self._has_keys = True
                        return True
            self._has_keys = False
            return False
        else:
            return self._has_keys

    def _get_data(self):
        items = self.items
        try:
            result = self.ar_table.get_one(items, self._key_values)
            if result:
                self.update(dict(zip(items, result)))
                self.exists = True
        except (DatabaseError, Exception):
            self.exists = False

    @property
    def _key_values(self):
        return {a:self[a] for a in self._db_keys}

    @property
    def columns(self):
        return self.table

    @property
    def _db_keys(self):
        columns = {a.name: a for a in self.columns}
        return list(filter(lambda a: bool(columns[a].key), self))

    def __setitem__(self, key, value):
        if key in self or key in self.ar_table.columns:
            dict.__setitem__(self, key, value)
            if key not in self.updated:
                self.updated.append(key)
        else:
            raise KeyError

    def save(self):
        if self.updated:
            if self.exists:
                self._update()
            else:
                self._insert()
                self.exists = True
            self.updated = []

    def _update(self):
        self.ar_table.update(dict([[a, self[a]] for a in self.updated]), self._key_values)

    def _insert(self):
        missing_keys = []
        for key in filter(lambda a: self.table[a].default is None and 'auto_increment' not in self.table[a].extra,
                          self.table):
            if not self[key]:
                missing_keys.append(key)
        if missing_keys:
            print('missing columns with no default argument: ' + ' '.join(missing_keys))
            raise ValueError
        self.ar_table.insert(self, self._key_values)
        self._get_data()


class VirtualDBTable(VirtualStorage):
    name = None
    table = None
    casted_row = ARRow
    _columns = Table()

    def __init__(self, ar_database):
        assert isinstance(ar_database, VirtualDatabase)
        super().__init__(ar_database.database)
        self.ar_database = ar_database

    @property
    def columns(self):
        return self._columns

    def keys(self):
        pass

    def row(self, **identifiers):
        pass

    def insert(self, pairing, identifiers):
        pass

    def update(self, pairing, identifier):
        pass

    def get_one(self, cols, identifiers):
        pass

    def get_many(self, cols, identifiers):
        pass

    def join_condition(self, identifiers):
        return ' and '.join(list(a + '=' + escape(identifiers[a]) for a in identifiers))


class SimpleVirtualDBTable(VirtualDBTable):
    @property
    def table(self):
        return self.columns

    def __init__(self, ar_database, name):
        super().__init__(ar_database)
        self.name = name
        self._columns = Table(*self._get_cols(name))

    def keys(self):
        return self.table.db_keys()

    def _get_cols(self, table):
        data = self.db.show_columns(table=table)
        return list(Column(*b) for b in data)

    def row(self, **identifiers):
        return self.casted_row(self, **identifiers)

    def rows(self,  **identifiers):
        cols = list(self.table.keys())
        for row in self.get_many(cols, identifiers):
            r = self.casted_row(self, False, **dict(zip(cols, row)))
            r.exists = True
            yield r

    def insert(self, pairing, identifiers):
        self.db.insert(self.name, pairing, 'where ' + self.join_condition(identifiers))

    def update(self, pairing, identifier):
        self.db.update(self.name, pairing, 'where ' + self.join_condition(identifier))

    def _get_cursor(self, cols, identifiers):
        where = {
            True: 'where ' + self.join_condition(identifiers),
            False: ''
        }
        return self.db.select(', '.join(cols), self.name, where[bool(identifiers)] + ';')

    def get_one(self, cols, identifiers):
        return self._get_cursor(cols, identifiers).fetchone()

    def get_many(self, cols, identifiers, count=-1):
        if count < 0:
            return self._get_cursor(cols, identifiers).fetchall()
        else:
            return self._get_cursor(cols, identifiers).fetchmany(count)



class CompoundVirtualDBTable(VirtualDBTable):
    tables = {}

    def __init__(self, ar_database, *names):
        super().__init__(ar_database)
        for name in names:
            self.tables[name] = SimpleVirtualDBTable(ar_database, name)

    def row(self, **identifiers):
        return self.casted_row(self, **identifiers)

    def keys(self):
        return set(chain(*(a.keys() for a in self.tables.values())))

    @property
    def table(self):
        return {a.table for a in self.tables}