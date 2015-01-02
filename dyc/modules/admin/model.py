from dyc.backend import orm
from dyc.core import model as coremodel

__author__ = 'justusadam'


class Category(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    display_name = orm.CharField()
    description = orm.TextField(null=True)
    weight = orm.IntegerField(default=0)


class Subcategory(orm.BaseModel):
    display_name = orm.CharField()
    description = orm.TextField(null=True)
    weight = orm.IntegerField(default=0)
    category = orm.ForeignKeyField(Category)
    machine_name = orm.CharField(unique=False)


class AdminPage(orm.BaseModel):
    machine_name = orm.CharField(unique=False)
    display_name = orm.CharField()
    description = orm.TextField(null=True)
    weight = orm.IntegerField(default=0)
    handler_module = orm.ForeignKeyField(coremodel.Module)
    subcategory = orm.ForeignKeyField(Subcategory)