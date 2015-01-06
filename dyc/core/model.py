from dyc.backend import orm


__author__ = 'Justus Adam'
__version__ = '0.1'


class Theme(orm.BaseModel):
    machine_name = orm.CharField()
    enabled = orm.BooleanField(default=False)


class Module(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    path = orm.TextField()
    enabled = orm.BooleanField(default=False)


class ContentHandler(orm.BaseModel):
    module = orm.ForeignKeyField(Module)
    machine_name = orm.CharField(unique=True)
    path_prefix = orm.CharField(unique=True)


class ContentTypes(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    content_handler = orm.ForeignKeyField(ContentHandler)
    display_name = orm.CharField(null=True)
    theme = orm.ForeignKeyField(Theme)
    description = orm.TextField(null=True)
