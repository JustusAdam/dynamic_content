from dycc.backend import orm

__author__ = 'Justus Adam'
__version__ = '0.1'


class Theme(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    enabled = orm.BooleanField(default=False)
    path = orm.CharField()