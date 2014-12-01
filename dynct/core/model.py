from dynct.backend.orm import *

__author__ = 'justusadam'


class Theme(BaseModel):
    machine_name = CharField()
    enabled = BooleanField(default=False)


class Module(BaseModel):
    machine_name = CharField(unique=True)
    path = TextField()
    enabled = BooleanField(default=False)


class ContentHandler(BaseModel):
    module = ForeignKeyField(Module)
    machine_name = CharField(unique=True)
    path_prefix = CharField(unique=True)


class ContentTypes(BaseModel):
    machine_name = CharField(unique=True)
    content_handler = ForeignKeyField(ContentHandler)
    display_name = CharField(null=True)
    theme = ForeignKeyField(Theme)
    description = TextField(null=True)


class Alias(BaseModel):
    source_url = CharField()
    alias = CharField(unique=True)