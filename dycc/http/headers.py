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
    def from_dict(cls, d:dict):
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

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.key == other.key and self.value == other.value
        elif isinstance(other, str):
            return self == self.from_str(other)
        elif isinstance(other, (tuple, list)):
            return self == self.from_tuple(other)
        else:
            raise TypeError(
                'Equality check expected type {}, {}, {} or {},'
                'found {}'.format(self.__class__, str, tuple, list, type(other))
            )

    def __str__(self):
        return str(self.key) + ': ' + str(self.value)