from dynct.backend.database import Database
import inspect
from dynct.errors import DatabaseError



class ARObject(object):
    _table = ''
    database = Database()
    _protected_values = ['exists']

    def __init__(self, exists=False):
        self._exists = exists

    @classmethod
    def get(cls, **descriptor):
        """
        Retrieve a single Object from the database.
        :param descriptor: Should be one ore more table keys.
        :return:
        """
        data = cls._get(descriptor).fetchone()
        if data:
            return cls(*data, exists=True)
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

        return [cls(exists=True)]

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
            return [cls(*a, exists=True) for a in data]
        else:
            return None

    @classmethod
    def _get(cls, descriptors, _tail:str=''):
        return cls.database.select(cls._values(), cls._table, ' and '.join([a + '=%(' + a + ')s' for a in descriptors]) + _tail, descriptors)

    def save(self):
        if self._exists:
            self._update()
        else:
            self._insert()

    def _update(self):
        pass

    def _insert(self):
        pass


    @classmethod
    def _values(cls) -> list:
        if not hasattr(cls, '_values_'):
            cls._values_ = list(filter(lambda a: a not in cls._protected_values, inspect.getargspec(cls.__init__)[0][1:]))
        return cls._values_

    def _get_one_special_value(self, name, q_tail):
        descriptors = {a:getattr(self, a) for a in self._values()}
        return self.database.select(name, self._table, ' and '.join([a + '=%(' + a + ')s' for a in descriptors] + q_tail), descriptors)


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
            cls._values_ = filter(lambda a: a not in cls._protected_values and a not in cls._lazy_values, inspect.getargspec(cls.__init__)[0][1:] - cls._lazy_values)
        return cls._values_