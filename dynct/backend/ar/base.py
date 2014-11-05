from dynct.backend.database import Database
import inspect



class ARObject(object):
    _table = ''
    database = Database()

    def __init__(self):
        self._is_real = False

    @classmethod
    def get(cls, **descriptor):
        """
        Retrieve a single Object from the database.
        :param descriptor: Should be one ore more table keys.
        :return:
        """
        cursor = cls._get(descriptor)
        return cls(*cursor.fetchone())

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
        tail = {
            True: 'order by ' + sort_by,
            False: ''
        }[bool(sort_by)]
        cursor = cls._get(descriptors, tail)
        return [cls(*a) for a in cursor.fetchall()]

    @classmethod
    def _get(cls, descriptors, _tail:str=''):
        return cls.database.select(cls._values(), cls._table, ' and '.join([a + '=%(' + a + ')s' for a in descriptors]) + _tail, descriptors)

    def save(self):
        self.database.update(self._table, {a:getattr(self, a) for a in self._values()})

    @classmethod
    def _values(cls) -> list:
        if not hasattr(cls, '_values_'):
            cls._values_ = inspect.getargspec(cls.__init__)[0][1:]
        return cls._values_


class PartiallyLazyARObject(ARObject):
    _lazy_values = set()

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
            cls._values_ = inspect.getargspec(cls.__init__)[0][1:] - cls._lazy_values
        return cls._values_