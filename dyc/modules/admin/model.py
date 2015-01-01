from dyc.backend import orm
from dyc.core import model as coremodel

__author__ = 'justusadam'


class Category(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    display_name = orm.CharField()
    description = orm.TextField(null=True)
    weight = orm.IntegerField(default=0)


class Subcategory(Category):
    category = orm.ForeignKeyField(Category)
    machine_name = orm.CharField(unique=False)

    class Meta(object):
        primary_key = orm.CompositeKey('category', 'machine_name')


class AdminPage(Category):
    machine_name = orm.CharField(unique=False)
    handler_module = orm.ForeignKeyField(coremodel.Module)
    subcategory = orm.ForeignKeyField(Subcategory)

    class Meta(object):
        primary_key = orm.CompositeKey('subcategory', 'machine_name')