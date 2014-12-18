from dynct.backend import orm
from dynct.core import model as coremodel

__author__ = 'justusadam'


access_types = ['default_granted', 'override']


class Menu(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    enabled = orm.BooleanField(default=False)


class CommonData(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    content = orm.TextField()


class CommonsConfig(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    element_type = orm.CharField()
    handler_module = orm.ForeignKeyField(coremodel.Module)
    access_type = orm.IntegerField()


class MenuItem(orm.BaseModel):
    path = orm.CharField(null=True)
    enabled = orm.BooleanField(default=False)
    parent = orm.ForeignKeyField('self', related_name='children', null=True)
    weight = orm.IntegerField(default=0)
    menu = orm.ForeignKeyField(Menu)
    tooltip = orm.TextField(null=True)
    display_name = orm.CharField()