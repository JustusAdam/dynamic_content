from dyc.backend import orm
from dycm import theming


__author__ = 'Justus Adam'

access_types = ['default_granted', 'override']


class Menu(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    enabled = orm.BooleanField(default=False)


class CommonData(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    content = orm.TextField()


class CommonsConfig(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    element_type = orm.CharField()
    access_type = orm.IntegerField()


class MenuItem(orm.BaseModel):
    path = orm.CharField(null=True)
    enabled = orm.BooleanField(default=False)
    parent = orm.ForeignKeyField('self', related_name='children', null=True)
    weight = orm.IntegerField(default=0)
    menu = orm.ForeignKeyField(Menu)
    tooltip = orm.TextField(null=True)
    display_name = orm.CharField()


class Common(orm.BaseModel):
    machine_name = orm.CharField()
    region = orm.CharField()
    weight = orm.IntegerField(default=0)
    theme = orm.ForeignKeyField(theming.model.Theme)
    show_title = orm.BooleanField()
    render_args = orm.CharField(null=True)
