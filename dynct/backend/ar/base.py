from dynct.backend.database import Database
import inspect


class ARObject(object):
    _table = ''
    database = Database

    @classmethod
    def get(cls, **descriptor):
        """
        Retrieve a single Object from the database.
        :param descriptor: Should be one ore more table keys.
        :return:
        """
        data = cls._get(descriptor, 'limit 1').fetchone()
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
        if sort_by:
            order = 'order by ' + sort_by
        else:
            order = ''
        if range_:
            limit = 'limit ' + range_
        else:
            limit = ''
        tail = ' '.join([order, limit])
        data = cls._get(descriptors, tail).fetchall()
        if data:
            return [cls(*a) for a in data]
        else:
            return None

    @classmethod
    def get_all(cls, sort_by=None, **descriptors):
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
        return cls.database.select(cls._keys(), cls._table,
                                   ' and '.join([a + '=%(' + a + ')s' for a in descriptors]),  _tail, descriptors)

    def save(self, **descriptors):
        """
        If no descriptors are provided saves the current ARObject in the database.

        If no primary key value was given, aka the default value was used, the object will be saved without specifying
        the primary key (to allow for auto_increment etc.)

        If descriptors are provided updates all rows that match the descriptors.
        :param descriptors:
        :return:
        """
        print(self.primary_key())
        if not descriptors and (not self.primary_key() or (getattr(self, self.primary_key()) == inspect.signature(self.__init__).parameters[self.primary_key()].default)):
            self.insert()
        else:
            try:
                self.update(**descriptors)
            except IOError:
                self.insert()

    def update(self, **descriptors):
        if descriptors:
            d = descriptors
        else:
            d = {self.primary_key(): getattr(self, self.primary_key())}
        condition = ' and '.join([a + '=%(' + a + ')s' for a in d])
        self.database.update(self._table, self._values(), condition, d)

    def insert(self):
        keys = self._keys()[:]
        if self.primary_key():
            if not hasattr(self, self.primary_key()) or getattr(self, self.primary_key()) == inspect.signature(self.__init__).parameters[self.primary_key()].default:
                keys.remove(self.primary_key())
        self.database.insert(self._table, self._values(keys))

    def _values(self, keys:list=None, exceptions:list=None):
        if not keys:
            keys = self._keys()
        params = inspect.signature(self.__init__).parameters
        return {a:getattr(self, a) for a in keys if getattr(self, a) != params[a] or (exceptions and a in exceptions)}

    @classmethod
    def primary_key(cls):
        if not hasattr(cls, '_primary_key'):
            cls._primary_key = [x[0] for x in cls.database.show_columns(cls._table) if x[3] == 'PRI'][0]
        return cls._primary_key

    @classmethod
    def _keys(cls) -> list:
        if not hasattr(cls, '_values_'):
            cls._values_ = inspect.getargspec(cls.__init__)[0][1:]
        return cls._values_

    def _descriptors(self):
        if self._primary_key:
            return {self.primary_key(): getattr(self, self.primary_key())}
        else:
            return {a:getattr(self, a) for a in self._keys()}

    def _get_one_special_value(self, name, q_tail):
        values = self._keys()[:]
        values.remove(name)
        descriptors = {a:getattr(self, a) for a in values}
        return self.database.select(name, self._table,
                                    ' and '.join([a + '=%(' + a + ')s' for a in descriptors]), q_tail,
                                    descriptors).fetchone()[0]

    def delete(self, **descriptors):
        """
        Deletes rows that fit the values in 'descriptors'.
        If descriptors isn't specified it deletes the row
        that matches all of its own values.
        :param descriptors:
        :return:
        """
        if not descriptors:
            descriptors = self._descriptors()
        self.database.remove(self._table, ' and '.join([a + '=%(' + a + ')s' for a in descriptors]), descriptors)


class PartiallyLazyARObject(ARObject):
    _lazy_values = list()

    def __getattribute__(self, item):
        a = super().__getattribute__(item)
        if not a:
            if item in self._lazy_values:
                existing = {f:getattr(self, f) for f in self._keys()}
                a = self.database.select(item, self._table, ' and '.join([b + '=%(' + b + ')s' for b in existing]),
                                         params=existing)
                # execute query to get value
                self.__setattr__(item, a)
        return a

    @classmethod
    def _keys(cls):
        if not hasattr(cls, '_values_'):
            # TODO test this
            cls._values_ = [x for x in inspect.getargspec(cls.__init__)[0][1:] if x not in cls._lazy_values]
        return cls._values_