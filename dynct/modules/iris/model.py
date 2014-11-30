from dynct.util.time import utcnow
from dynct.backend.orm import *
from dynct.core.model import ContentHandler, Module, ContentTypes
from dynct.modules.users.model import User


__author__ = 'justusadam'



class Page(BaseModel):
    content_type = ForeignKeyField(ContentTypes)
    page_title = CharField()
    creator = ForeignKeyField(User)
    published = BooleanField(default=False)
    date_created = DateField(default=utcnow())


def field(name):
    class GenericField(BaseModel):
        class Meta:
            db_table = name + '_data'

        page = ForeignKeyField(Page)
        content = TextField()
        path_prefix = CharField()
    return GenericField


class FieldConfig(BaseModel):
    machine_name = CharField(unique=True)
    display_name = CharField()
    content_type = ForeignKeyField(ContentHandler)
    handler_module = ForeignKeyField(Module)
    weight = IntegerField(default=0)
    description = TextField(null=True)