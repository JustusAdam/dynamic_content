from dynct.backend.orm import *
from dynct.core.model import Module

__author__ = 'justusadam'


class Category(BaseModel):
    machine_name = CharField(unique=True)
    display_name = CharField()
    description = TextField(null=True)
    weight = IntegerField(default=0)


class Subcategory(Category):
    category = ForeignKeyField(Category)


class AdminPage(Category):
    handler_module = ForeignKeyField(Module)
    subcategory = ForeignKeyField(Subcategory)

    @property
    def category(self):
        return self.subcategory