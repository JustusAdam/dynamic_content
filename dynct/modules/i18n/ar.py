from dynct.backend.ar.base import ARObject

__author__ = 'justusadam'


class DisplayName(ARObject):
    _table = 'display_names'

    def __init__(self, machine_name, source_table, translations:dict):
        assert isinstance(translations, dict)
        super().__init__()
        self.machine_name = machine_name
        self.source_table = source_table
        for tr in translations:
            setattr(self, tr, translations[tr])

    def __getattr__(self, item):
        if item in self._values():
            return None
        raise AttributeError

    @classmethod
    def _values(cls):
        if not hasattr(cls, '_values_'):
            cls._values_ = [a[0] for a in cls.database.show_columns(cls._table)][1:]
        return cls._values_

    @classmethod
    def get(cls, **descriptor):
        data = cls._get(descriptor).fetchone()
        if data:
            return cls(*data[:2], translations=dict(zip(cls._values()[2:], data[2:])))
        else:
            return None

    @classmethod
    def get_all(cls, sort_by='', **descriptors):
        if sort_by:
            tail = 'order by ' + sort_by
        else:
            tail = ''
        data = cls._get(descriptors, tail).fetchall()
        if data:
            return [cls(*a[:2], translations=dict(zip(cls._values()[2:], a[2:]))) for a in data]
        else:
            return None