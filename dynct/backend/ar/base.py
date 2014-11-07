from dynct.backend.database import Database
import inspect
from dynct.errors import DatabaseError


class ARObject(object):
    """
    _saved is a value designed to prevent debuggers automatic execution of @property code
    from accidentally saving the object multiple times, especially if it doesn't have
    any unique values and thus creates new rows all the time.
    """
    _table = ''
    database = Database()

    def __init__(self):
        self._saved = False

    @classmethod
    def get(cls, **descriptor):
        """
        Retrieve a single Object from the database.
        :param descriptor: Should be one ore more table keys.
        :return:
        """
        data = cls._get(descriptor).fetchone()
        if data:
            return cls(*data)
        else:
            return None

    @classmethod
    def get_many(cls, range_, sort_by=None, **descriptors):
        """
        Retrieves many objects and returns a list of them.
        :param range_:
        :param descriptors:
        :return:
        """

        return [cls()]

    @classmethod
    def get_all(cls, sort_by='', **descriptors):
        """
        Retrieves all objects described by descriptors.
        :param sort_by:
        :param descriptors:
        :return:
        """
        if sort_by:
            tail = 'order by ' + sort_by
        else:
            tail = ''
        data = cls._get(descriptors, tail).fetchall()
        if data:
            return [cls(*a) for a in data]
        else:
            return None

    @classmethod
    def _get(cls, descriptors, _tail:str=''):
        return cls.database.select(cls._values(), cls._table, ' and '.join([a + '=%(' + a + ')s' for a in descriptors]) + _tail, descriptors)

    def save(self, **descriptors):
        print(self.primary_key())
        if not descriptors and getattr(self, self.primary_key()) == inspect.signature(self.__init__).parameters[self.primary_key()].default:
            self.insert()
        else:
            try:
                self.update(**descriptors)
            except DatabaseError:
                self.insert()

    def update(self, **descriptors):
        if descriptors:
            d = descriptors
        else:
            d = {self.primary_key(): getattr(self, self.primary_key())}
        condition = ' and '.join([a + '=%(' + a + ')s' for a in d])
        pairing = {a:getattr(self, a) for a in self._values()}
        self.database.update(self._table, pairing, condition, d)

    def insert(self):
        values = self._values()[:]
        if not hasattr(self, self.primary_key()) or getattr(self, self.primary_key()) == inspect.signature(self.__init__).parameters[self.primary_key()].default:
            values.remove(self.primary_key())
        self.database.insert(self._table, {a:getattr(self, a) for a in values})

    @classmethod
    def primary_key(cls):
        if not hasattr(cls, '_primary_key'):
            def c(l):
                for i in l:
                    if i[3] == 'PRI':
                        return i[0]
                return None
            cls._primary_key = c(cls.database.show_columns(cls._table))
        return cls._primary_key

    @classmethod
    def _values(cls) -> list:
        if not hasattr(cls, '_values_'):
            cls._values_ = inspect.getargspec(cls.__init__)[0][1:]
        return cls._values_

    def _get_one_special_value(self, name, q_tail):
        values = self._values()[:]
        values.remove(name)
        descriptors = {a:getattr(self, a) for a in values}
        return self.database.select(name, self._table, ' and '.join([a + '=%(' + a + ')s' for a in descriptors]) + ' ' + q_tail, descriptors).fetchone()[0]


class PartiallyLazyARObject(ARObject):
    _lazy_values = list()

    def __getattribute__(self, item):
        a = super().__getattribute__(item)
        if not a:
            if item in self._lazy_values:
                existing = {f:getattr(self, f) for f in self._values()}
                a = self.database.select(item, self._table, ' and '.join([b + '=%(' + b + ')s' for b in existing]), existing)
                # execute query to get value
                self.__setattr__(item, a)
        return a

    @classmethod
    def _values(cls):
        if not hasattr(cls, '_values_'):
            # TODO test this
            cls._values_ = filter(lambda a: a not in cls._lazy_values, inspect.getargspec(cls.__init__)[0][1:] - cls._lazy_values)
        return cls._values_