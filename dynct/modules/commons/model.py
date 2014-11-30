from dynct.backend.orm import *
from dynct.core.model import Module

__author__ = 'justusadam'


access_types = ['default_granted', 'override']


class Menu(BaseModel):
    machine_name = CharField(unique=True)
    enabled = BooleanField(default=False)


class Common(BaseModel):
    machine_name = CharField(unique=True)
    content = TextField()


class CommonsConfig(BaseModel):
    machine_name = CharField(unique=True)
    element_type = CharField()
    handler_module = ForeignKeyField(Module)
    access_type = IntegerField()


class MenuItem(BaseModel):
    path = CharField(null=True)
    enabled = BooleanField(default=False)
    parent = ForeignKeyField('self', related_name='children', null=True)
    weight = IntegerField(default=0)
    menu = ForeignKeyField(Menu)
    tooltip = TextField(null=True)
    display_name = CharField()