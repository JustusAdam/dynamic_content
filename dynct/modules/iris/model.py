from dynct.util import time, decorators
from dynct.backend import orm
from dynct.core import model as coremodel
from dynct.modules.users import model as usersmodel


__author__ = 'justusadam'



class Page(orm.BaseModel):
    content_type = orm.ForeignKeyField(coremodel.ContentTypes)
    page_title = orm.CharField()
    creator = orm.ForeignKeyField(usersmodel.User)
    published = orm.BooleanField(default=False)
    date_created = orm.DateField(default=time.utcnow())


class BodyField(orm.BaseModel):
    class Meta:
        db_table = 'body' + '_data'

    page = orm.ForeignKeyField(Page)
    content = orm.TextField()


@decorators.multicache
def field(name):
    if name == 'body':
        return BodyField
    class GenericField(orm.BaseModel):
        class Meta:
            db_table = name + '_data'

        page_type = orm.CharField()
        page_id = orm.IntegerField()
        content = orm.TextField()

    return GenericField


class FieldConfig(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    display_name = orm.CharField()
    content_type = orm.ForeignKeyField(coremodel.ContentHandler)
    handler_module = orm.ForeignKeyField(coremodel.Module)
    weight = orm.IntegerField(default=0)
    description = orm.TextField(null=True)