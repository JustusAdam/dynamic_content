from dynct.backend import orm
from dynct.core import model as coremodel

__author__ = 'justusadam'


class Category(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    display_name = orm.CharField()
    description = orm.TextField(null=True)
    weight = orm.IntegerField(default=0)


class Subcategory(Category):
    category = orm.ForeignKeyField(Category)


class AdminPage(Category):
    handler_module = orm.ForeignKeyField(coremodel.Module)
    subcategory = orm.ForeignKeyField(Subcategory)

    @property
    def category(self):
        return self.subcategory