__author__ = 'Justus Adam'
__version__ = '0.1'


class Header:
    def __init__(self, key, value=None):
        self.key = key
        self.value = value

    @classmethod
    def from_str(cls, string:str):
        k, v = string.split(': ', 1)
        return cls(k, v)

    @classmethod
    def many_from_str(cls, string:str):
        l = string.split('\n')
        for i in l:
            yield cls.from_str(i)

    @classmethod
    def any_from_str(cls, string:str):
        l = string.split('\n')
        if len(l) == 1:
            return cls.from_str(l[0])
        else:
            return cls.many_from_str(string)

    @classmethod
    def many_from_dict(cls, d:dict):
        for k, v in d.items():
            yield cls(k, v)

    @classmethod
    def from_tuple(cls, t):
        if len(t) == 2:
            return cls(*t)
        else:
            raise TypeError(
                'tuple for header construction must have length 2, '
                'had length {}'.format(len(t))
            )

    from_list = from_tuple

    @classmethod
    def many_from_tuple(cls, t):
        for i in t:
            yield cls.auto_construct(i)

    many_from_list = many_from_tuple

    @classmethod
    def any_from_tuple(cls, t):
        if len(t) == 2 and isinstance(t[0], str):
            return cls.from_tuple(t)
        else:
            return cls.many_from_tuple(t)

    @classmethod
    def auto_construct(cls, raw):
        """
        Constructs a new Header instance with the appropriate classmethod
         determined by the type of the input
        :param raw: raw input data
        :return:
        """
        if isinstance(raw, cls):
            return raw
        elif isinstance(raw, dict):
            return cls.many_from_dict(raw)
        elif isinstance(raw, str):
            return cls.any_from_str(raw)
        elif isinstance(raw, (list, tuple)):
            return cls.any_from_tuple(raw)
        else:
            raise TypeError(
                'The type {} is not supported for auto construction'.format(type(raw))
            )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.key == other.key and self.value == other.value
        else:
            return self == self.auto_construct(other)

    def __str__(self):
        return str(self.key) + ': ' + str(self.value)