from dynct.backend.database import Database
import inspect



class ARObject:
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
        return cls.database.select(cls.values(), cls._table, ' and '.join([a + '=%(' + a + ')s' for a in descriptors]) + _tail, descriptors)

    def save(self):
        self.database.update(self._table, {a:getattr(self, a) for a in self.values()})

    @classmethod
    def values(cls) -> list:
        if not hasattr(cls, '_values'):
            cls._values = inspect.getargspec(cls.__init__)[0][1:]
        return cls._values