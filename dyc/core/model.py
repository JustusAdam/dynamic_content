from dyc.backend import orm


__author__ = 'Justus Adam'
__version__ = '0.1'


class Module(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    path = orm.TextField()
    enabled = orm.BooleanField(default=False)