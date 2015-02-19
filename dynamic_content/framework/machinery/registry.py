"""
Store miscellaneous persistent but changeable
python data structures in the database
"""

import pickle
from framework.backend import orm

__author__ = 'Justus Adam'
__version__ = '0.1'


class _Registry(orm.BaseModel):
    key = orm.CharField(unique=True)
    value = orm.BlobField()


class Registry:
    """
    A sort of dictionary imitating object that stores
    miscellaneous information in then database
    """
    __slots__ = ()

    def __getitem__(self, item):
        return pickle.loads(
            _Registry.get(key=item).value
        )

    def __setitem__(self, key, value):
        assert isinstance(key, str)
        assert len(key) <= 255
        value = pickle.dumps(value)
        assert isinstance(value, (bytes, bytearray))
        try:
            entry = _Registry.get(key=key)
            entry.value = value
            entry.save()
        except orm.DoesNotExist:
            _Registry.create(key=key, value=value)

    def __contains__(self, item):
        try:
            _Registry.get(key=item)
            return True
        except orm.DoesNotExist:
            return False