from dyc.util import time, decorators
from dyc.backend import orm
from dyc.core import model as coremodel
from dyc.modules.users import model as usersmodel
from dyc.modules.commons import model as commonsmodel


__author__ = 'Justus Adam'


class Page(orm.BaseModel):
    content_type = orm.ForeignKeyField(coremodel.ContentTypes)
    page_title = orm.CharField()
    creator = orm.ForeignKeyField(usersmodel.User)
    published = orm.BooleanField(default=False)
    date_created = orm.DateField(default=time.utcnow())
    menu_item = orm.ForeignKeyField(commonsmodel.MenuItem, null=True)


@decorators.multicache
def field(name):
    class FieldData(orm.BaseModel):
        class Meta:
            db_table = name + '_data'

        page_type = orm.CharField()
        page_id = orm.IntegerField()
        content = orm.TextField()

    return FieldData


class FieldType(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    handler = orm.CharField(null=False)


class FieldConfig(orm.BaseModel):
    field_type = orm.ForeignKeyField(FieldType)
    content_type = orm.ForeignKeyField(coremodel.ContentHandler)
    weight = orm.IntegerField(default=0)
    description = orm.TextField(null=True)
